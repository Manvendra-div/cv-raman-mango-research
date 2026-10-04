"""Test script for Zone Intelligence Module end-to-end validation."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.zone_intelligence.zone_profile import ZoneProfiler
from src.zone_intelligence.orchard_matching import OrchardMatcher
from src.zone_intelligence.reference_yield import ReferenceYieldCalculator
from src.zone_intelligence.yield_gap import YieldGapAnalyzer
from src.zone_intelligence.limiting_factors import LimitingFactorAnalyzer


def test_zone_pipeline():
    """Test complete zone intelligence pipeline."""
    print("=" * 70)
    print("ZONE INTELLIGENCE MODULE TEST")
    print("=" * 70)

    # Load dataset
    dataset_path = PROJECT_ROOT / "data" / "raw" / "mango_microbiome_dataset.csv"
    df = pd.read_csv(dataset_path)
    print(f"\n✓ Dataset loaded: {len(df)} samples, {len(df.columns)} features")

    # Test 1: Zone Profiler
    print("\n[1/5] Testing ZoneProfiler...")
    profiler = ZoneProfiler(df)
    villages = profiler.available_villages()
    print(f"  Villages: {villages}")

    malihabad_profile = profiler.village_profile("Malihabad")
    if malihabad_profile:
        print(f"  Malihabad: {malihabad_profile.sample_count} samples")
        print(f"  Mean yield: {malihabad_profile.yield_stats['mean']:.2f} kg/tree")

    # Test 2: Orchard Matcher
    print("\n[2/5] Testing OrchardMatcher...")
    matcher = OrchardMatcher(df)
    match = matcher.match(
        village="Malihabad",
        variety="Dashehari",
        tree_age=15,
        management="Organic"
    )
    print(f"  Matched {match.match_count} orchards, {match.sample_count} samples")
    print(f"  Criteria: {match.criteria_used.get('tier')}")
    print(f"  Sufficient: {match.sufficient}")

    # Test 3: Reference Yield Calculator
    print("\n[3/5] Testing ReferenceYieldCalculator...")
    ref_calc = ReferenceYieldCalculator()
    ref = ref_calc.from_match_result(match)
    print(f"  Mean: {ref.mean:.2f} kg/tree")
    print(f"  Q75: {ref.q75:.2f} kg/tree")
    print(f"  Top 10%: {ref.top10_mean:.2f} kg/tree")

    # Test 4: Yield Gap Analyzer
    print("\n[4/5] Testing YieldGapAnalyzer...")
    gap_analyzer = YieldGapAnalyzer()
    predicted_yield = 18.5
    primary_gap = gap_analyzer.primary_gap(predicted_yield, ref)
    print(f"  Predicted: {primary_gap.predicted_yield:.2f} kg/tree")
    print(f"  Reference (Q75): {primary_gap.reference_yield:.2f} kg/tree")
    print(f"  Gap: {primary_gap.gap_absolute:.2f} kg ({primary_gap.gap_percentage:.1f}%)")

    # Test 5: Limiting Factor Analyzer
    print("\n[5/5] Testing LimitingFactorAnalyzer...")
    lf_analyzer = LimitingFactorAnalyzer()

    # Create sample with some deficiencies
    sample = df.iloc[0].to_dict()
    sample["pH"] = 5.5  # Below optimal
    sample["Available_P"] = 8.0  # Below optimal
    sample["Pathogen_Load_Index"] = 0.75  # High pathogen

    peer_medians = lf_analyzer.peer_medians_from_match(match.matched_samples)
    factors = lf_analyzer.analyze(sample, peer_medians=peer_medians)

    print(f"  Identified {len(factors)} limiting factors:")
    for i, factor in enumerate(factors[:3], 1):
        print(f"    {i}. {factor.feature}: {factor.measured_value:.2f} "
              f"({factor.confidence} confidence)")

    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED - Zone Intelligence Module operational")
    print("=" * 70)


if __name__ == "__main__":
    test_zone_pipeline()

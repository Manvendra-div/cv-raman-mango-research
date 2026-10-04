"""Zone intelligence service for the DSS.

Wraps the zone intelligence modules into a single cached service that
the API and dashboard layers can call.  Loaded lazily alongside the
main DSSService so that zone analysis is available at every prediction.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.zone_intelligence.zone_profile import ZoneProfiler
from src.zone_intelligence.orchard_matching import OrchardMatcher
from src.zone_intelligence.reference_yield import ReferenceYieldCalculator
from src.zone_intelligence.yield_gap import YieldGapAnalyzer
from src.zone_intelligence.limiting_factors import LimitingFactorAnalyzer

RAW_DATASET = PROJECT_ROOT / "data" / "raw" / "mango_microbiome_dataset.csv"


class ZoneService:
    """Facade over the five zone-intelligence modules."""

    def __init__(self) -> None:
        if not RAW_DATASET.exists():
            raise FileNotFoundError(
                f"Zone intelligence requires the raw dataset at {RAW_DATASET}"
            )
        self._df = pd.read_csv(RAW_DATASET)
        self._profiler = ZoneProfiler(self._df)
        self._matcher = OrchardMatcher(self._df)
        self._ref_calc = ReferenceYieldCalculator()
        self._gap_analyzer = YieldGapAnalyzer()
        self._lf_analyzer = LimitingFactorAnalyzer()

    # ------------------------------------------------------------------
    # High-level convenience: full zone analysis for one prediction
    # ------------------------------------------------------------------

    def zone_analysis(
        self,
        predicted_yield: float,
        village: str,
        variety: str,
        tree_age: int,
        management: Optional[str] = None,
        sample_values: Optional[Dict[str, float]] = None,
        shap_contributions: Optional[Dict[str, float]] = None,
        *,
        exclude_orchard: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run the complete zone intelligence pipeline for a single sample."""

        # 1. Comparable orchard matching
        match = self._matcher.match(
            village=village,
            variety=variety,
            tree_age=tree_age,
            management=management,
            exclude_orchard=exclude_orchard,
        )

        # 2. Reference yield
        ref = self._ref_calc.from_match_result(match)

        # 3. Yield gap
        all_gaps = self._gap_analyzer.analyze(predicted_yield, ref)
        primary_gap = self._gap_analyzer.primary_gap(predicted_yield, ref)

        # 4. Limiting factors
        limiting_factors: List[Dict[str, Any]] = []
        if sample_values:
            peer_medians = self._lf_analyzer.peer_medians_from_match(
                match.matched_samples
            )
            factors = self._lf_analyzer.analyze(
                sample_values,
                shap_contributions=shap_contributions,
                peer_medians=peer_medians,
            )
            limiting_factors = [
                LimitingFactorAnalyzer.to_dict(f) for f in factors
            ]

        # 5. Village profile (for context)
        village_profile = self._profiler.village_profile(village)
        village_dict = (
            ZoneProfiler.profile_to_dict(village_profile)
            if village_profile
            else None
        )

        return {
            "comparable_orchards": {
                "criteria": match.criteria_used,
                "orchard_count": match.match_count,
                "sample_count": match.sample_count,
                "sufficient": match.sufficient,
                "orchard_ids": match.matched_orchard_ids[:20],
                "warnings": match.warnings,
            },
            "reference_yield": ReferenceYieldCalculator.to_dict(ref),
            "yield_gap": {
                "primary": YieldGapAnalyzer.to_dict(primary_gap),
                "all_benchmarks": {
                    k: YieldGapAnalyzer.to_dict(v) for k, v in all_gaps.items()
                },
            },
            "limiting_factors": limiting_factors,
            "village_profile": village_dict,
        }

    # ------------------------------------------------------------------
    # Individual module access (for fine-grained API endpoints)
    # ------------------------------------------------------------------

    def village_profiles(self) -> Dict[str, Any]:
        profiles = self._profiler.all_village_profiles()
        return {
            village: ZoneProfiler.profile_to_dict(p)
            for village, p in profiles.items()
        }

    def available_zones(self) -> Dict[str, Any]:
        return {
            "villages": self._profiler.available_villages(),
            "varieties": self._profiler.available_varieties(),
            "management_types": self._profiler.available_management_types(),
        }


@lru_cache(maxsize=1)
def get_zone_service() -> ZoneService:
    return ZoneService()

#!/usr/bin/env python3
"""
Deep Data Quality Audit - Mango Soil Microbiome Dataset
Performs comprehensive checks on dataset integrity, biological validity,
compositional constraints, and orchard structure.
"""

import pandas as pd
import numpy as np
import json
import os

# ── Paths ──
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_V2 = os.path.join(BASE, "data", "raw", "mango_microbiome_dataset.csv")
DATA_V1 = os.path.join(BASE, "data", "raw", "mango_microbiome_dataset_v1_original.csv")
OUT_JSON = os.path.join(BASE, "outputs", "data_quality_audit_results.json")

# ── Taxonomic columns ──
TAXA_COLS = [
    "Proteobacteria", "Actinobacteria", "Acidobacteria", "Firmicutes",
    "Bacteroidetes", "Ascomycota", "Basidiomycota", "Glomeromycota",
    "Mortierellomycota", "Zygomycota", "Thaumarchaeota", "Euryarchaeota"
]

# ── Biological ranges ──
BIO_RANGES = {
    "pH":                    (4.0, 9.5),
    "EC":                    (0.0, 4.0),
    "Organic_Carbon":        (0.0, 5.0),
    "Soil_Moisture":         (0.0, 100.0),
    "Pathogen_Load_Index":   (0.0, 1.0),
    "Shannon_Index":         (0.0, 6.0),
    "Simpson_Index":         (0.0, 1.0),
    "Pielou_Evenness":       (0.0, 1.0),
}
for t in TAXA_COLS:
    BIO_RANGES[t] = (0.0, 100.0)


def safe(v):
    """Make a value JSON-serializable."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, pd.Series):
        return v.to_dict()
    if isinstance(v, pd.DataFrame):
        return v.to_dict()
    if isinstance(v, dict):
        return {str(k): safe(vv) for k, vv in v.items()}
    return v


def deep_safe(obj):
    """Recursively make an object JSON-serializable."""
    if isinstance(obj, dict):
        return {str(k): deep_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [deep_safe(v) for v in obj]
    return safe(obj)


def audit_dataset(df, label="v2"):
    """Run all audit checks on a dataframe. Returns dict of findings."""
    report = {}

    # ─── 1. Basic Integrity ───
    print(f"\n{'='*60}")
    print(f"  1. BASIC INTEGRITY ({label})")
    print(f"{'='*60}")

    integrity = {
        "shape": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
        "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
        "missing_values_per_column": {},
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    if len(missing_cols) > 0:
        integrity["missing_values_per_column"] = {col: int(v) for col, v in missing_cols.items()}
    else:
        integrity["missing_values_per_column"] = "NONE - zero missing values"

    # Duplicate Sample_IDs
    if "Sample_ID" in df.columns:
        dup_ids = df["Sample_ID"].duplicated().sum()
        integrity["duplicate_sample_ids"] = int(dup_ids)
    else:
        integrity["duplicate_sample_ids"] = "Sample_ID column not found"

    report["1_basic_integrity"] = integrity
    print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"  Total missing: {integrity['total_missing']}")
    print(f"  Duplicate rows: {integrity['duplicate_rows']}")
    if "Sample_ID" in df.columns:
        print(f"  Duplicate Sample_IDs: {dup_ids}")

    # ─── 2. Negative Value Investigation ───
    print(f"\n{'='*60}")
    print(f"  2. NEGATIVE VALUE INVESTIGATION ({label})")
    print(f"{'='*60}")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    neg_report = {}
    neg_found = False
    for col in numeric_cols:
        neg_count = int((df[col] < 0).sum())
        min_val = float(df[col].min())
        if neg_count > 0:
            neg_found = True
            neg_report[col] = {
                "negative_count": neg_count,
                "negative_pct": round(neg_count / len(df) * 100, 2),
                "min_value": round(min_val, 6),
            }
            is_taxa = " [TAXONOMIC]" if col in TAXA_COLS else ""
            print(f"  ** {col}{is_taxa}: {neg_count} negatives ({neg_report[col]['negative_pct']}%), min={min_val:.6f}")
        else:
            neg_report[col] = {"negative_count": 0, "min_value": round(min_val, 6)}

    if not neg_found:
        print("  No negative values found in any numeric column.")

    report["2_negative_values"] = neg_report

    # ─── 3. Microbiome Compositional Check ───
    print(f"\n{'='*60}")
    print(f"  3. MICROBIOME COMPOSITIONAL CHECK ({label})")
    print(f"{'='*60}")

    present_taxa = [c for c in TAXA_COLS if c in df.columns]
    missing_taxa = [c for c in TAXA_COLS if c not in df.columns]

    comp = {"taxa_columns_present": present_taxa, "taxa_columns_missing": missing_taxa}

    if len(present_taxa) > 0:
        row_sums = df[present_taxa].sum(axis=1)
        comp["row_sum_stats"] = {
            "mean": round(float(row_sums.mean()), 4),
            "std": round(float(row_sums.std()), 4),
            "min": round(float(row_sums.min()), 4),
            "max": round(float(row_sums.max()), 4),
            "median": round(float(row_sums.median()), 4),
        }
        comp["sums_to_100pct"] = bool(np.allclose(row_sums, 100.0, atol=0.01))
        comp["rows_below_95"] = int((row_sums < 95).sum())
        comp["rows_above_105"] = int((row_sums > 105).sum())
        comp["rows_outside_95_105"] = int(((row_sums < 95) | (row_sums > 105)).sum())

        # Percentile breakdown
        comp["row_sum_percentiles"] = {
            f"p{p}": round(float(np.percentile(row_sums, p)), 4)
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        }

        print(f"  Taxa columns found: {len(present_taxa)}/{len(TAXA_COLS)}")
        print(f"  Row-sum mean: {comp['row_sum_stats']['mean']:.4f}")
        print(f"  Row-sum std:  {comp['row_sum_stats']['std']:.4f}")
        print(f"  Row-sum range: [{comp['row_sum_stats']['min']:.4f}, {comp['row_sum_stats']['max']:.4f}]")
        print(f"  Sums to ~100%: {comp['sums_to_100pct']}")
        print(f"  Rows < 95%: {comp['rows_below_95']}")
        print(f"  Rows > 105%: {comp['rows_above_105']}")

    report["3_compositional_check"] = comp

    # ─── 4. Biological Range Validation ───
    print(f"\n{'='*60}")
    print(f"  4. BIOLOGICAL RANGE VALIDATION ({label})")
    print(f"{'='*60}")

    range_report = {}
    for col in numeric_cols:
        stats = {
            "min": round(float(df[col].min()), 6),
            "max": round(float(df[col].max()), 6),
            "mean": round(float(df[col].mean()), 6),
            "std": round(float(df[col].std()), 6),
        }
        if col in BIO_RANGES:
            lo, hi = BIO_RANGES[col]
            below = int((df[col] < lo).sum())
            above = int((df[col] > hi).sum())
            stats["bio_range"] = [lo, hi]
            stats["below_range_count"] = below
            stats["above_range_count"] = above
            stats["out_of_range_total"] = below + above
            if below + above > 0:
                print(f"  ** {col}: {below + above} out of range [{lo}, {hi}] "
                      f"(below={below}, above={above}, min={stats['min']}, max={stats['max']})")
        range_report[col] = stats

    # Check if nothing flagged
    any_flagged = any(
        v.get("out_of_range_total", 0) > 0 for v in range_report.values()
    )
    if not any_flagged:
        print("  All values within expected biological ranges.")

    report["4_biological_ranges"] = range_report

    # ─── 5. Target Distribution ───
    print(f"\n{'='*60}")
    print(f"  5. TARGET DISTRIBUTION ({label})")
    print(f"{'='*60}")

    targets = {}

    # Mango_Yield
    if "Mango_Yield" in df.columns:
        y = df["Mango_Yield"]
        skew_val = float(y.skew())
        targets["Mango_Yield"] = {
            "count": int(y.count()),
            "mean": round(float(y.mean()), 4),
            "std": round(float(y.std()), 4),
            "min": round(float(y.min()), 4),
            "max": round(float(y.max()), 4),
            "median": round(float(y.median()), 4),
            "skewness": round(skew_val, 4),
            "kurtosis": round(float(y.kurtosis()), 4),
            "percentiles": {
                f"p{p}": round(float(np.percentile(y, p)), 4) for p in [1, 5, 25, 50, 75, 95, 99]
            },
            "floor_effect_pct_at_min": round(float((y == y.min()).mean() * 100), 2),
            "ceiling_effect_pct_at_max": round(float((y == y.max()).mean() * 100), 2),
        }
        print(f"  Mango_Yield: mean={targets['Mango_Yield']['mean']}, "
              f"std={targets['Mango_Yield']['std']}, skew={skew_val:.4f}")
        print(f"    range: [{targets['Mango_Yield']['min']}, {targets['Mango_Yield']['max']}]")

    # Disease_Risk
    if "Disease_Risk" in df.columns:
        vc = df["Disease_Risk"].value_counts()
        total = len(df)
        targets["Disease_Risk"] = {
            "class_counts": {str(k): int(v) for k, v in vc.items()},
            "class_percentages": {str(k): round(v / total * 100, 2) for k, v in vc.items()},
            "n_classes": int(vc.shape[0]),
        }
        print(f"  Disease_Risk classes: {dict(vc)}")

    # Nutrient_Availability
    if "Nutrient_Availability" in df.columns:
        vc = df["Nutrient_Availability"].value_counts()
        total = len(df)
        targets["Nutrient_Availability"] = {
            "class_counts": {str(k): int(v) for k, v in vc.items()},
            "class_percentages": {str(k): round(v / total * 100, 2) for k, v in vc.items()},
            "n_classes": int(vc.shape[0]),
            "deficient_exists": bool("Deficient" in vc.index),
        }
        print(f"  Nutrient_Availability classes: {dict(vc)}")
        print(f"    Deficient class exists: {targets['Nutrient_Availability']['deficient_exists']}")

    report["5_target_distribution"] = targets

    # ─── 6. Orchard Structure Analysis ───
    print(f"\n{'='*60}")
    print(f"  6. ORCHARD STRUCTURE ANALYSIS ({label})")
    print(f"{'='*60}")

    structure = {}

    if "Orchard_ID" in df.columns:
        orch_counts = df["Orchard_ID"].value_counts()
        structure["samples_per_orchard"] = {
            "n_orchards": int(orch_counts.shape[0]),
            "min": int(orch_counts.min()),
            "max": int(orch_counts.max()),
            "mean": round(float(orch_counts.mean()), 2),
            "std": round(float(orch_counts.std()), 4),
            "all_equal": bool(orch_counts.nunique() == 1),
            "all_equal_value": int(orch_counts.iloc[0]) if orch_counts.nunique() == 1 else None,
        }
        # Exact count distribution
        count_dist = orch_counts.value_counts().sort_index()
        structure["samples_per_orchard"]["count_distribution"] = {
            int(k): int(v) for k, v in count_dist.items()
        }

        is_pseudo = structure["samples_per_orchard"]["all_equal"]
        eq_val = structure["samples_per_orchard"]["all_equal_value"]
        print(f"  Orchards: {structure['samples_per_orchard']['n_orchards']}")
        print(f"  Samples/orchard: min={orch_counts.min()}, max={orch_counts.max()}, "
              f"mean={orch_counts.mean():.1f}, std={orch_counts.std():.4f}")
        if is_pseudo:
            print(f"  *** PSEUDO-REPLICATION ALERT: ALL orchards have exactly {eq_val} samples ***")

    if "Village" in df.columns:
        vill_counts = df["Village"].value_counts()
        structure["samples_per_village"] = {
            str(k): int(v) for k, v in vill_counts.items()
        }
        structure["n_villages"] = int(vill_counts.shape[0])
        print(f"  Villages: {structure['n_villages']}")
        print(f"  Samples/village: {dict(vill_counts)}")

    if "Village" in df.columns and "Orchard_ID" in df.columns:
        orch_per_vill = df.groupby("Village")["Orchard_ID"].nunique()
        structure["orchards_per_village"] = {str(k): int(v) for k, v in orch_per_vill.items()}
        print(f"  Orchards/village: {dict(orch_per_vill)}")

    if "Village" in df.columns and "Mango_Variety" in df.columns:
        cross = pd.crosstab(df["Village"], df["Mango_Variety"])
        structure["village_variety_crosstab"] = {
            str(v): {str(c): int(cross.loc[v, c]) for c in cross.columns}
            for v in cross.index
        }
        print(f"  Village x Variety cross-tab shape: {cross.shape}")
        print(cross.to_string())

    report["6_orchard_structure"] = structure

    # ─── 7. Feature-Target Correlation ───
    print(f"\n{'='*60}")
    print(f"  7. FEATURE-TARGET CORRELATION ({label})")
    print(f"{'='*60}")

    corr_report = {}
    if "Mango_Yield" in df.columns:
        numeric_df = df.select_dtypes(include=[np.number])
        if "Mango_Yield" in numeric_df.columns:
            corrs = numeric_df.corr()["Mango_Yield"].drop("Mango_Yield", errors="ignore")
            corrs_abs = corrs.abs().sort_values(ascending=False)
            top10 = corrs_abs.head(10)
            corr_report["top_10_corr_with_yield"] = {
                col: round(float(corrs[col]), 4) for col in top10.index
            }
            print("  Top 10 correlations with Mango_Yield:")
            for col in top10.index:
                print(f"    {col}: r={corrs[col]:.4f}")

            # Target leakage check
            leakage = corrs_abs[corrs_abs > 0.95]
            if len(leakage) > 0:
                corr_report["potential_leakage_yield"] = {
                    col: round(float(corrs[col]), 4) for col in leakage.index
                }
                print(f"\n  *** POTENTIAL LEAKAGE: {list(leakage.index)} have |r|>0.95 with Mango_Yield ***")
            else:
                corr_report["potential_leakage_yield"] = "NONE"
                print("  No features with |r|>0.95 to Mango_Yield (no leakage detected).")

    # Check leakage for Disease_Risk and Nutrient_Availability (if encoded)
    for target in ["Disease_Risk", "Nutrient_Availability"]:
        if target in df.columns and df[target].dtype in [np.float64, np.int64, np.float32, np.int32]:
            numeric_df = df.select_dtypes(include=[np.number])
            if target in numeric_df.columns:
                corrs_t = numeric_df.corr()[target].drop(target, errors="ignore").abs()
                leakage_t = corrs_t[corrs_t > 0.95]
                if len(leakage_t) > 0:
                    corr_report[f"potential_leakage_{target}"] = {
                        col: round(float(corrs_t[col]), 4) for col in leakage_t.index
                    }

    report["7_feature_target_correlation"] = corr_report

    return report


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

print("=" * 60)
print("  MANGO SOIL MICROBIOME - DEEP DATA QUALITY AUDIT")
print("=" * 60)

# Load v2
print(f"\nLoading v2 dataset: {DATA_V2}")
df_v2 = pd.read_csv(DATA_V2)
print(f"  Loaded: {df_v2.shape}")

report = {}
report["audit_metadata"] = {
    "dataset_path": DATA_V2,
    "audit_date": "2026-10-04",
    "pandas_version": pd.__version__,
    "numpy_version": np.__version__,
}

# Run full audit on v2
v2_report = audit_dataset(df_v2, label="v2")
report.update(v2_report)

# ─── 8. V1 vs V2 Comparison ───
print(f"\n{'='*60}")
print("  8. V1 vs V2 COMPARISON")
print(f"{'='*60}")

v1_comparison = {}
if os.path.exists(DATA_V1):
    print(f"  V1 file found: {DATA_V1}")
    df_v1 = pd.read_csv(DATA_V1)

    v1_comparison["v1_exists"] = True
    v1_comparison["v1_shape"] = {"rows": int(df_v1.shape[0]), "cols": int(df_v1.shape[1])}
    v1_comparison["v2_shape"] = {"rows": int(df_v2.shape[0]), "cols": int(df_v2.shape[1])}
    v1_comparison["shape_match"] = (df_v1.shape == df_v2.shape)

    # Column comparison
    v1_cols = set(df_v1.columns)
    v2_cols = set(df_v2.columns)
    v1_comparison["columns_only_in_v1"] = sorted(list(v1_cols - v2_cols))
    v1_comparison["columns_only_in_v2"] = sorted(list(v2_cols - v1_cols))
    v1_comparison["common_columns"] = sorted(list(v1_cols & v2_cols))

    print(f"  V1 shape: {df_v1.shape}, V2 shape: {df_v2.shape}")
    print(f"  Columns only in V1: {v1_comparison['columns_only_in_v1']}")
    print(f"  Columns only in V2: {v1_comparison['columns_only_in_v2']}")

    # Negative values comparison for key taxa
    neg_comparison = {}
    for col in ["Zygomycota", "Bacteroidetes"] + TAXA_COLS:
        if col in df_v1.columns and col in df_v2.columns:
            v1_neg = int((df_v1[col] < 0).sum())
            v2_neg = int((df_v2[col] < 0).sum())
            v1_min = round(float(df_v1[col].min()), 6)
            v2_min = round(float(df_v2[col].min()), 6)
            neg_comparison[col] = {
                "v1_negative_count": v1_neg,
                "v2_negative_count": v2_neg,
                "v1_min": v1_min,
                "v2_min": v2_min,
                "negatives_fixed": v1_neg > 0 and v2_neg == 0,
            }
            if v1_neg > 0 or v2_neg > 0:
                fixed_str = " [FIXED in v2]" if v1_neg > 0 and v2_neg == 0 else ""
                print(f"  {col}: v1 negatives={v1_neg} (min={v1_min}), "
                      f"v2 negatives={v2_neg} (min={v2_min}){fixed_str}")

    v1_comparison["negative_value_comparison"] = neg_comparison

    # Target distribution comparison
    target_comp = {}
    for target in ["Mango_Yield", "Disease_Risk", "Nutrient_Availability"]:
        if target in df_v1.columns and target in df_v2.columns:
            tc = {}
            if df_v1[target].dtype in [np.float64, np.int64, np.float32, np.int32]:
                tc["v1_mean"] = round(float(df_v1[target].mean()), 4)
                tc["v2_mean"] = round(float(df_v2[target].mean()), 4)
                tc["v1_std"] = round(float(df_v1[target].std()), 4)
                tc["v2_std"] = round(float(df_v2[target].std()), 4)
            else:
                v1_vc = df_v1[target].value_counts()
                v2_vc = df_v2[target].value_counts()
                tc["v1_classes"] = {str(k): int(v) for k, v in v1_vc.items()}
                tc["v2_classes"] = {str(k): int(v) for k, v in v2_vc.items()}
            target_comp[target] = tc

    v1_comparison["target_distribution_comparison"] = target_comp

    # V1 compositional check (brief)
    present_taxa_v1 = [c for c in TAXA_COLS if c in df_v1.columns]
    if present_taxa_v1:
        v1_sums = df_v1[present_taxa_v1].sum(axis=1)
        v1_comparison["v1_compositional_sum_stats"] = {
            "mean": round(float(v1_sums.mean()), 4),
            "std": round(float(v1_sums.std()), 4),
            "min": round(float(v1_sums.min()), 4),
            "max": round(float(v1_sums.max()), 4),
        }
        print(f"\n  V1 compositional sums: mean={v1_sums.mean():.4f}, "
              f"range=[{v1_sums.min():.4f}, {v1_sums.max():.4f}]")

else:
    v1_comparison["v1_exists"] = False
    print("  V1 file not found. Skipping comparison.")

report["8_v1_v2_comparison"] = v1_comparison


# ══════════════════════════════════════════════════════════════
#  SAVE REPORT
# ══════════════════════════════════════════════════════════════

os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

report_safe = deep_safe(report)
with open(OUT_JSON, "w") as f:
    json.dump(report_safe, f, indent=2, default=str)

print(f"\n{'='*60}")
print(f"  REPORT SAVED: {OUT_JSON}")
print(f"{'='*60}")


# ══════════════════════════════════════════════════════════════
#  EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════

print(f"\n{'#'*60}")
print(f"  EXECUTIVE SUMMARY")
print(f"{'#'*60}")

issues = []
info = []

# Missing values
if report["1_basic_integrity"]["total_missing"] == 0:
    info.append("ZERO missing values across all columns")
else:
    issues.append(f"Missing values detected: {report['1_basic_integrity']['total_missing']} total")

# Duplicates
if report["1_basic_integrity"]["duplicate_rows"] > 0:
    issues.append(f"Duplicate rows: {report['1_basic_integrity']['duplicate_rows']}")

# Negative values
neg_cols = [k for k, v in report["2_negative_values"].items() if v.get("negative_count", 0) > 0]
if neg_cols:
    issues.append(f"NEGATIVE VALUES in {len(neg_cols)} column(s): {neg_cols}")
else:
    info.append("No negative values in any numeric column")

# Compositional check
comp = report["3_compositional_check"]
if "sums_to_100pct" in comp:
    if comp["sums_to_100pct"]:
        info.append("Taxonomic abundances sum to ~100% (compositional constraint satisfied)")
    else:
        issues.append(f"Taxonomic sums DO NOT sum to 100%: mean={comp['row_sum_stats']['mean']:.2f}, "
                      f"range=[{comp['row_sum_stats']['min']:.2f}, {comp['row_sum_stats']['max']:.2f}]")
        issues.append(f"  Rows outside 95-105%: {comp['rows_outside_95_105']}")

# Biological ranges
for col, stats in report["4_biological_ranges"].items():
    oor = stats.get("out_of_range_total", 0)
    if oor > 0:
        issues.append(f"Out-of-range values in {col}: {oor} rows (range: {stats['bio_range']})")

# Pseudo-replication
orch = report.get("6_orchard_structure", {}).get("samples_per_orchard", {})
if orch.get("all_equal"):
    eq_val = orch.get("all_equal_value")
    issues.append(f"PSEUDO-REPLICATION: All {orch['n_orchards']} orchards have exactly {eq_val} samples each "
                  f"- samples within orchards are NOT independent")

# Target distribution
tgt = report.get("5_target_distribution", {})
if "Nutrient_Availability" in tgt:
    na = tgt["Nutrient_Availability"]
    if na.get("deficient_exists"):
        info.append(f"Deficient class CONFIRMED in Nutrient_Availability "
                    f"({na['class_percentages'].get('Deficient', '?')}% of samples)")

# Leakage
corr = report.get("7_feature_target_correlation", {})
if corr.get("potential_leakage_yield") != "NONE" and corr.get("potential_leakage_yield"):
    if isinstance(corr["potential_leakage_yield"], dict):
        issues.append(f"POTENTIAL TARGET LEAKAGE: {list(corr['potential_leakage_yield'].keys())}")

# V1 comparison
v1c = report.get("8_v1_v2_comparison", {})
if v1c.get("v1_exists"):
    neg_comp = v1c.get("negative_value_comparison", {})
    fixed_cols = [col for col, vals in neg_comp.items() if vals.get("negatives_fixed")]
    if fixed_cols:
        info.append(f"V1->V2: Negative values FIXED in: {fixed_cols}")
    new_cols = v1c.get("columns_only_in_v2", [])
    if new_cols:
        info.append(f"V1->V2: New columns added in V2: {new_cols}")

print("\n  ISSUES FOUND:")
if issues:
    for i, iss in enumerate(issues, 1):
        print(f"    {i}. {iss}")
else:
    print("    None!")

print("\n  KEY FINDINGS (OK):")
for i, inf in enumerate(info, 1):
    print(f"    {i}. {inf}")

print(f"\n  Total issues: {len(issues)}")
print(f"  Audit complete.")

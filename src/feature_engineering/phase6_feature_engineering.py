"""Phase 6 feature engineering and feature-selection pipeline.

This script builds engineered agronomic and microbiome features from the
Phase 5 clean master dataset, evaluates redundancy and multicollinearity, and
exports a biologically meaningful feature list for Phase 7 modeling.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_MASTER = PROJECT_ROOT / "data" / "processed" / "clean_master_dataset.csv"
SPLIT_MEMBERSHIP = PROJECT_ROOT / "data" / "splits" / "split_membership.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "phase6_feature_engineering"
FEATURE_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "feature_engineering"

ENGINEERED_FEATURE_TABLE = PROCESSED_DIR / "engineered_feature_table.csv"
FEATURE_TABLE = PROCESSED_DIR / "feature_table.csv"
FEATURE_DOCUMENTATION = PROCESSED_DIR / "feature_documentation.csv"
SELECTED_FEATURES_JSON = PROCESSED_DIR / "selected_features.json"

REDUNDANCY_REPORT = FEATURE_OUTPUT_DIR / "redundancy_pairs.csv"
VIF_REPORT = FEATURE_OUTPUT_DIR / "multicollinearity_vif.csv"
TARGET_ASSOCIATION_REPORT = FEATURE_OUTPUT_DIR / "feature_target_associations.csv"
FEATURE_SUMMARY_JSON = FEATURE_OUTPUT_DIR / "phase6_feature_summary.json"
FEATURE_SELECTION_REPORT = REPORT_DIR / "feature_selection_report.md"

TARGET_COLUMNS = ["Mango_Yield", "Disease_Risk", "Nutrient_Availability"]
ID_COLUMNS = ["Sample_ID", "Orchard_ID"]
CATEGORICAL_FEATURES = ["Village", "Mango_Variety", "Soil_Depth", "Sampling_Season", "Management"]

BACTERIAL_TAXA = [
    "Proteobacteria",
    "Actinobacteria",
    "Acidobacteria",
    "Firmicutes",
    "Bacteroidetes",
]
FUNGAL_TAXA = [
    "Ascomycota",
    "Basidiomycota",
    "Glomeromycota",
    "Mortierellomycota",
    "Zygomycota",
]
ARCHAEAL_TAXA = ["Thaumarchaeota", "Euryarchaeota"]

BENEFICIAL_MICROBES = [
    "Nitrogen_Fixers",
    "Phosphate_Solubilizers_PSB",
    "Potassium_Solubilizers",
    "Mycorrhizae_AMF",
    "Trichoderma",
    "Pseudomonas_PGPR",
]
NUTRIENT_CYCLING_MICROBES = [
    "Nitrogen_Fixers",
    "Phosphate_Solubilizers_PSB",
    "Potassium_Solubilizers",
    "Mycorrhizae_AMF",
]
BIOCONTROL_MICROBES = ["Trichoderma", "Pseudomonas_PGPR"]

PHASE6_FEATURES = [
    "Diversity_Score_Phase6",
    "Richness_Evenness_Balance_Phase6",
    "Bacterial_Dominance_Index_Phase6",
    "Fungal_Dominance_Index_Phase6",
    "Archaeal_Dominance_Index_Phase6",
    "Beneficial_Microbial_Index_Phase6",
    "Nutrient_Cycling_Index_Phase6",
    "Biocontrol_Index_Phase6",
    "Pathogen_Load_Index_Phase6",
    "Pathogen_Beneficial_Ratio_Phase6",
    "Beneficial_to_Pathogen_Log_Ratio_Phase6",
    "NPK_Balance_Score_Phase6",
    "Micronutrient_Balance_Score_Phase6",
    "Texture_Balance_Score_Phase6",
    "Soil_Physical_Condition_Score_Phase6",
    "Soil_Chemical_Fertility_Score_Phase6",
    "Climate_Comfort_Score_Phase6",
    "Soil_Health_Index_Phase6",
]

BIOLOGICAL_PRIORITY = {
    "Soil_Health_Index_Phase6": 1,
    "Pathogen_Load_Index_Phase6": 1,
    "NPK_Balance_Score_Phase6": 1,
    "Beneficial_Microbial_Index_Phase6": 1,
    "Diversity_Score_Phase6": 1,
    "Nutrient_Cycling_Index_Phase6": 2,
    "Biocontrol_Index_Phase6": 2,
    "Pathogen_Beneficial_Ratio_Phase6": 2,
    "Soil_Chemical_Fertility_Score_Phase6": 2,
    "Soil_Physical_Condition_Score_Phase6": 2,
    "Micronutrient_Balance_Score_Phase6": 3,
    "Climate_Comfort_Score_Phase6": 3,
    "Tree_Age": 3,
    "pH": 3,
    "EC": 3,
    "Organic_Carbon": 3,
    "Available_P": 3,
    "Available_K": 3,
    "Total_Nitrogen": 3,
    "Fusarium": 3,
    "Trichoderma": 3,
    "Pseudomonas_PGPR": 3,
}


@dataclass(frozen=True)
class FeatureDoc:
    feature: str
    feature_group: str
    source_columns: str
    formula_summary: str
    interpretation: str
    modeling_note: str


def ensure_dirs() -> None:
    for path in [PROCESSED_DIR, REPORT_DIR, FEATURE_OUTPUT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def minmax(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    minimum = values.min()
    maximum = values.max()
    if pd.isna(minimum) or pd.isna(maximum) or np.isclose(maximum, minimum):
        return pd.Series(0.5, index=series.index)
    return (values - minimum) / (maximum - minimum)


def suitability_score(series: pd.Series, optimum: float, tolerance: float) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    score = 1.0 - (values - optimum).abs() / tolerance
    return score.clip(lower=0.0, upper=1.0).fillna(0.0)


def log_minmax(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    logged = np.log10(df[columns].clip(lower=0) + 1.0)
    return logged.apply(minmax)


def row_balance_score(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    scaled = df[columns].apply(minmax)
    mean = scaled.mean(axis=1)
    std = scaled.std(axis=1).fillna(0.0)
    balance = mean * (1.0 - std.clip(upper=1.0))
    return balance.clip(lower=0.0, upper=1.0)


def calculate_phase6_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    otu_score = minmax(out["OTU_Count"])
    chao_score = minmax(out["Chao1_Richness"])
    shannon_score = minmax(out["Shannon_Index"])
    simpson_score = minmax(out["Simpson_Index"])
    pielou_score = minmax(out["Pielou_Evenness"])
    out["Diversity_Score_Phase6"] = (
        0.25 * otu_score
        + 0.25 * chao_score
        + 0.25 * shannon_score
        + 0.15 * simpson_score
        + 0.10 * pielou_score
    ) * 100.0
    out["Richness_Evenness_Balance_Phase6"] = (
        (0.35 * otu_score + 0.35 * chao_score + 0.30 * pielou_score) * 100.0
    )

    out["Bacterial_Dominance_Index_Phase6"] = out[BACTERIAL_TAXA].max(axis=1)
    out["Fungal_Dominance_Index_Phase6"] = out[FUNGAL_TAXA].max(axis=1)
    out["Archaeal_Dominance_Index_Phase6"] = out[ARCHAEAL_TAXA].max(axis=1)

    beneficial_scaled = log_minmax(out, BENEFICIAL_MICROBES)
    nutrient_microbe_scaled = log_minmax(out, NUTRIENT_CYCLING_MICROBES)
    biocontrol_scaled = log_minmax(out, BIOCONTROL_MICROBES)
    out["Beneficial_Microbial_Index_Phase6"] = beneficial_scaled.mean(axis=1) * 100.0
    out["Nutrient_Cycling_Index_Phase6"] = nutrient_microbe_scaled.mean(axis=1) * 100.0
    out["Biocontrol_Index_Phase6"] = biocontrol_scaled.mean(axis=1) * 100.0

    out["Pathogen_Load_Index_Phase6"] = minmax(out["Fusarium"]) * 100.0
    beneficial_sum = out[BENEFICIAL_MICROBES].clip(lower=0).sum(axis=1)
    out["Pathogen_Beneficial_Ratio_Phase6"] = out["Fusarium"].clip(lower=0) / (beneficial_sum + 1.0)
    out["Beneficial_to_Pathogen_Log_Ratio_Phase6"] = np.log10((beneficial_sum + 1.0) / (out["Fusarium"].clip(lower=0) + 1.0))

    out["NPK_Balance_Score_Phase6"] = row_balance_score(out, ["Total_Nitrogen", "Available_P", "Available_K"]) * 100.0
    out["Micronutrient_Balance_Score_Phase6"] = row_balance_score(out, ["Zn", "Fe", "Mn", "Cu"]) * 100.0

    loam_sand = suitability_score(out["Sand"], optimum=40.0, tolerance=40.0)
    loam_silt = suitability_score(out["Silt"], optimum=40.0, tolerance=40.0)
    loam_clay = suitability_score(out["Clay"], optimum=20.0, tolerance=35.0)
    out["Texture_Balance_Score_Phase6"] = (loam_sand + loam_silt + loam_clay) / 3.0 * 100.0

    pH_score = suitability_score(out["pH"], optimum=7.2, tolerance=1.5)
    ec_score = 1.0 - minmax(out["EC"])
    moisture_score = suitability_score(out["Soil_Moisture"], optimum=22.0, tolerance=18.0)
    temp_score = suitability_score(out["Soil_Temperature"], optimum=28.0, tolerance=14.0)
    bulk_score = suitability_score(out["Bulk_Density"], optimum=1.35, tolerance=0.35)
    cec_score = minmax(out["CEC"])
    out["Soil_Physical_Condition_Score_Phase6"] = (
        0.25 * moisture_score + 0.20 * temp_score + 0.25 * bulk_score + 0.30 * out["Texture_Balance_Score_Phase6"] / 100.0
    ) * 100.0
    out["Soil_Chemical_Fertility_Score_Phase6"] = (
        0.20 * pH_score
        + 0.10 * ec_score
        + 0.20 * minmax(out["Organic_Carbon"])
        + 0.25 * out["NPK_Balance_Score_Phase6"] / 100.0
        + 0.15 * out["Micronutrient_Balance_Score_Phase6"] / 100.0
        + 0.10 * cec_score
    ) * 100.0

    air_temp_score = suitability_score(out["Air_Temp_Avg"], optimum=28.0, tolerance=16.0)
    humidity_score = suitability_score(out["Humidity"], optimum=65.0, tolerance=35.0)
    rainfall_score = suitability_score(out["Rainfall"], optimum=150.0, tolerance=150.0)
    radiation_score = suitability_score(out["Solar_Radiation"], optimum=20.0, tolerance=8.0)
    out["Climate_Comfort_Score_Phase6"] = (
        0.30 * air_temp_score + 0.25 * humidity_score + 0.25 * rainfall_score + 0.20 * radiation_score
    ) * 100.0

    pathogen_penalty = out["Pathogen_Load_Index_Phase6"] / 100.0
    out["Soil_Health_Index_Phase6"] = (
        0.30 * out["Soil_Chemical_Fertility_Score_Phase6"] / 100.0
        + 0.20 * out["Soil_Physical_Condition_Score_Phase6"] / 100.0
        + 0.20 * out["Diversity_Score_Phase6"] / 100.0
        + 0.20 * out["Beneficial_Microbial_Index_Phase6"] / 100.0
        + 0.10 * out["Climate_Comfort_Score_Phase6"] / 100.0
        - 0.15 * pathogen_penalty
    ).clip(lower=0.0, upper=1.0) * 100.0

    return out


def build_feature_documentation() -> pd.DataFrame:
    docs = [
        FeatureDoc(
            "Diversity_Score_Phase6",
            "microbiome_diversity",
            "OTU_Count; Chao1_Richness; Shannon_Index; Simpson_Index; Pielou_Evenness",
            "Weighted min-max normalized alpha-diversity composite.",
            "Higher values indicate richer and more even microbial communities.",
            "Useful for yield, soil-health, and resilience modeling.",
        ),
        FeatureDoc(
            "Richness_Evenness_Balance_Phase6",
            "microbiome_diversity",
            "OTU_Count; Chao1_Richness; Pielou_Evenness",
            "Weighted richness-evenness composite.",
            "Captures whether richness is accompanied by even community structure.",
            "Interpret alongside full diversity score.",
        ),
        FeatureDoc(
            "Beneficial_Microbial_Index_Phase6",
            "functional_microbes",
            "; ".join(BENEFICIAL_MICROBES),
            "Mean of log-scaled min-max normalized beneficial microbial groups.",
            "Higher values indicate stronger beneficial microbial support.",
            "Use with pathogen metrics to avoid one-sided interpretation.",
        ),
        FeatureDoc(
            "Nutrient_Cycling_Index_Phase6",
            "functional_microbes",
            "; ".join(NUTRIENT_CYCLING_MICROBES),
            "Mean of log-scaled nutrient-cycling microbial groups.",
            "Higher values suggest stronger biological nutrient-cycling potential.",
            "Complements chemical NPK balance.",
        ),
        FeatureDoc(
            "Biocontrol_Index_Phase6",
            "functional_microbes",
            "; ".join(BIOCONTROL_MICROBES),
            "Mean of log-scaled Trichoderma and Pseudomonas PGPR.",
            "Higher values suggest stronger beneficial biocontrol presence.",
            "Interpret as proxy, not confirmed disease suppression.",
        ),
        FeatureDoc(
            "Pathogen_Load_Index_Phase6",
            "pathogen_pressure",
            "Fusarium",
            "Min-max normalized Fusarium load.",
            "Higher values indicate higher pathogen pressure.",
            "Strong disease-risk candidate; does not diagnose all mango diseases.",
        ),
        FeatureDoc(
            "Pathogen_Beneficial_Ratio_Phase6",
            "pathogen_pressure",
            "Fusarium; beneficial microbial groups",
            "Fusarium divided by total beneficial microbial abundance plus one.",
            "Higher values indicate pathogen pressure relative to beneficial microbes.",
            "Useful for disease-risk interpretation.",
        ),
        FeatureDoc(
            "Beneficial_to_Pathogen_Log_Ratio_Phase6",
            "pathogen_pressure",
            "Fusarium; beneficial microbial groups",
            "Log10 ratio of beneficial microbes to Fusarium.",
            "Higher values indicate beneficial dominance over pathogen load.",
            "Use alongside pathogen load index.",
        ),
        FeatureDoc(
            "NPK_Balance_Score_Phase6",
            "nutrient_balance",
            "Total_Nitrogen; Available_P; Available_K",
            "Mean of min-max scaled NPK values penalized by imbalance.",
            "Higher values indicate stronger and more balanced primary nutrients.",
            "Supports yield and nutrient-availability modeling.",
        ),
        FeatureDoc(
            "Micronutrient_Balance_Score_Phase6",
            "nutrient_balance",
            "Zn; Fe; Mn; Cu",
            "Mean of min-max scaled micronutrients penalized by imbalance.",
            "Higher values indicate more balanced micronutrient status.",
            "Useful secondary soil-health feature.",
        ),
        FeatureDoc(
            "Texture_Balance_Score_Phase6",
            "soil_physical",
            "Sand; Silt; Clay",
            "Suitability score around loam-like sand, silt, and clay proportions.",
            "Higher values indicate texture closer to balanced loam conditions.",
            "Synthetic proxy; use measured local soil classes for real data.",
        ),
        FeatureDoc(
            "Soil_Physical_Condition_Score_Phase6",
            "soil_physical",
            "Soil_Moisture; Soil_Temperature; Bulk_Density; Texture_Balance_Score_Phase6",
            "Weighted physical-condition score.",
            "Higher values indicate favorable physical soil condition.",
            "Complements chemical and microbial health scores.",
        ),
        FeatureDoc(
            "Soil_Chemical_Fertility_Score_Phase6",
            "soil_chemical",
            "pH; EC; Organic_Carbon; NPK_Balance_Score_Phase6; Micronutrient_Balance_Score_Phase6; CEC",
            "Weighted chemical fertility score with salinity penalty.",
            "Higher values indicate favorable soil chemical status.",
            "Important yield-prediction feature.",
        ),
        FeatureDoc(
            "Climate_Comfort_Score_Phase6",
            "climate",
            "Air_Temp_Avg; Humidity; Rainfall; Solar_Radiation",
            "Suitability score around moderate mango orchard climate conditions.",
            "Higher values indicate less stressful climate context.",
            "Use as contextual feature rather than direct soil property.",
        ),
        FeatureDoc(
            "Soil_Health_Index_Phase6",
            "integrated_soil_health",
            "Chemical, physical, diversity, beneficial microbe, climate, and pathogen-pressure scores",
            "Weighted integrated index with pathogen penalty.",
            "Higher values indicate better overall soil-health profile.",
            "High-level summary feature; keep raw components for XAI.",
        ),
        FeatureDoc(
            "Bacterial_Dominance_Index_Phase6",
            "taxonomic_structure",
            "; ".join(BACTERIAL_TAXA),
            "Maximum bacterial phylum relative abundance.",
            "Higher values indicate stronger bacterial dominance by one phylum.",
            "Potential redundancy with individual bacterial phyla.",
        ),
        FeatureDoc(
            "Fungal_Dominance_Index_Phase6",
            "taxonomic_structure",
            "; ".join(FUNGAL_TAXA),
            "Maximum fungal phylum relative abundance.",
            "Higher values indicate stronger fungal dominance by one phylum.",
            "Potential redundancy with individual fungal phyla.",
        ),
        FeatureDoc(
            "Archaeal_Dominance_Index_Phase6",
            "taxonomic_structure",
            "; ".join(ARCHAEAL_TAXA),
            "Maximum archaeal group relative abundance.",
            "Higher values indicate stronger archaeal dominance by one group.",
            "Potential redundancy because only two archaeal groups are present.",
        ),
    ]
    return pd.DataFrame([doc.__dict__ for doc in docs])


def numeric_candidate_columns(df: pd.DataFrame) -> list[str]:
    excluded = set(ID_COLUMNS + TARGET_COLUMNS + CATEGORICAL_FEATURES)
    excluded.update(["Preprocessing_Status", "Compositional_Normalization"])
    return [
        c
        for c in df.columns
        if c not in excluded and pd.api.types.is_numeric_dtype(df[c])
    ]


def add_split_membership(df: pd.DataFrame) -> pd.DataFrame:
    membership = pd.read_csv(SPLIT_MEMBERSHIP)
    return df.merge(membership, on="Sample_ID", how="left", validate="one_to_one")


def compute_target_associations(train: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    disease = train["Disease_Risk"].map({"Low": 0, "Medium": 1, "High": 2})
    nutrient = train["Nutrient_Availability"].map({"Deficient": 0, "Optimal": 1, "High": 2})
    rows = []
    for feature in feature_cols:
        series = train[feature]
        rows.append(
            {
                "Feature": feature,
                "Correlation_With_Mango_Yield": series.corr(train["Mango_Yield"]),
                "Correlation_With_Disease_Risk_Ordinal": series.corr(disease),
                "Correlation_With_Nutrient_Availability_Ordinal": series.corr(nutrient),
            }
        )
    assoc = pd.DataFrame(rows).fillna(0.0)
    assoc["Max_Abs_Target_Association"] = assoc[
        [
            "Correlation_With_Mango_Yield",
            "Correlation_With_Disease_Risk_Ordinal",
            "Correlation_With_Nutrient_Availability_Ordinal",
        ]
    ].abs().max(axis=1)
    assoc["Biological_Priority"] = assoc["Feature"].map(BIOLOGICAL_PRIORITY).fillna(5).astype(int)
    return assoc.sort_values(
        ["Biological_Priority", "Max_Abs_Target_Association", "Feature"],
        ascending=[True, False, True],
    )


def compute_redundancy_pairs(train: pd.DataFrame, feature_cols: list[str], threshold: float = 0.90) -> pd.DataFrame:
    corr = train[feature_cols].corr().abs()
    rows = []
    columns = corr.columns.tolist()
    for i, left in enumerate(columns):
        for right in columns[i + 1 :]:
            value = corr.loc[left, right]
            if pd.notna(value) and value >= threshold:
                rows.append({"Feature_A": left, "Feature_B": right, "Abs_Correlation": float(value)})
    return pd.DataFrame(rows).sort_values("Abs_Correlation", ascending=False)


def compute_vif(train: pd.DataFrame, feature_cols: list[str], max_rows: int = 5000) -> pd.DataFrame:
    # VIF is estimated on a deterministic sample for speed and to keep reports stable.
    sample = train[feature_cols].dropna()
    if len(sample) > max_rows:
        sample = sample.sample(n=max_rows, random_state=42)

    variances = sample.var(numeric_only=True)
    usable_cols = variances[variances > 1e-12].index.tolist()
    x = sample[usable_cols].to_numpy(dtype=float)
    x = (x - x.mean(axis=0)) / x.std(axis=0)

    rows = []
    for idx, feature in enumerate(usable_cols):
        y = x[:, idx]
        others = np.delete(x, idx, axis=1)
        if others.shape[1] == 0:
            vif = 1.0
            r2 = 0.0
        else:
            coef, *_ = np.linalg.lstsq(others, y, rcond=None)
            pred = others @ coef
            ss_res = float(np.sum((y - pred) ** 2))
            ss_tot = float(np.sum((y - y.mean()) ** 2))
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
            vif = float("inf") if r2 >= 0.999999 else 1.0 / max(1e-12, 1.0 - r2)
        rows.append({"Feature": feature, "VIF": vif, "R2_From_Other_Features": r2})
    return pd.DataFrame(rows).sort_values("VIF", ascending=False)


def select_features(
    train: pd.DataFrame,
    assoc: pd.DataFrame,
    feature_cols: list[str],
    max_features: int = 34,
    redundancy_threshold: float = 0.95,
) -> tuple[list[str], pd.DataFrame]:
    corr = train[feature_cols].corr().abs()
    selected: list[str] = []
    rows = []

    ordered = assoc["Feature"].tolist()
    for feature in ordered:
        if len(selected) >= max_features:
            rows.append({"Feature": feature, "Decision": "Dropped", "Reason": "Feature limit reached"})
            continue

        redundant_with = ""
        for existing in selected:
            value = corr.loc[feature, existing]
            if pd.notna(value) and value >= redundancy_threshold:
                redundant_with = existing
                break

        if redundant_with:
            rows.append(
                {
                    "Feature": feature,
                    "Decision": "Dropped",
                    "Reason": f"Redundant with {redundant_with} at abs correlation >= {redundancy_threshold}",
                }
            )
        else:
            selected.append(feature)
            rows.append({"Feature": feature, "Decision": "Selected", "Reason": "Biologically meaningful and non-redundant"})

    return selected, pd.DataFrame(rows)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    text_df = df.copy()
    for column in text_df.columns:
        if pd.api.types.is_numeric_dtype(text_df[column]):
            text_df[column] = text_df[column].map(lambda value: f"{value:.6g}" if pd.notna(value) else "")
        else:
            text_df[column] = text_df[column].astype(str)

    headers = text_df.columns.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in text_df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(lines)


def write_feature_selection_report(
    engineered: pd.DataFrame,
    assoc: pd.DataFrame,
    selected_features: list[str],
    selection_decisions: pd.DataFrame,
    redundancy: pd.DataFrame,
    vif: pd.DataFrame,
) -> None:
    top_assoc = assoc.head(15)
    high_vif = vif[vif["VIF"] >= 10].head(15)
    dropped_redundant = selection_decisions[selection_decisions["Decision"] == "Dropped"].head(15)

    lines = [
        "# Phase 6 Feature-Selection Report",
        "",
        "Generated by `src/feature_engineering/phase6_feature_engineering.py`.",
        "",
        "## Input",
        "",
        "- Input dataset: `data/processed/clean_master_dataset.csv`",
        f"- Rows processed: {len(engineered)}",
        f"- Phase 6 engineered features created: {len(PHASE6_FEATURES)}",
        "",
        "## Engineered Feature Groups",
        "",
        "- Microbial diversity score and richness-evenness balance.",
        "- Pathogen-load and pathogen-beneficial ratio metrics.",
        "- Nutrient-balance and micronutrient-balance scores.",
        "- Soil physical, chemical, climate, and integrated soil-health indices.",
        "- Beneficial microbial, nutrient-cycling, and biocontrol summaries.",
        "",
        "## Top Train-Split Target Associations",
        "",
        dataframe_to_markdown(top_assoc),
        "",
        "## Selected Feature Set",
        "",
    ]
    for feature in selected_features:
        lines.append(f"- `{feature}`")

    lines.extend(
        [
            "",
            "## Redundancy and Multicollinearity",
            "",
            f"- Redundancy pairs at abs correlation >= 0.90: {len(redundancy)}",
            f"- Features with VIF >= 10: {len(vif[vif['VIF'] >= 10])}",
            "",
            "### Highest VIF Features",
            "",
            dataframe_to_markdown(high_vif) if not high_vif.empty else "No VIF values >= 10.",
            "",
            "### Example Dropped Features",
            "",
            dataframe_to_markdown(dropped_redundant) if not dropped_redundant.empty else "No features dropped before the feature limit.",
            "",
            "## Outputs",
            "",
            "- Engineered feature table: `data/processed/engineered_feature_table.csv`",
            "- Feature table: `data/processed/feature_table.csv`",
            "- Feature documentation: `data/processed/feature_documentation.csv`",
            "- Selected features: `data/processed/selected_features.json`",
            "- Redundancy report: `outputs/feature_engineering/redundancy_pairs.csv`",
            "- VIF report: `outputs/feature_engineering/multicollinearity_vif.csv`",
            "- Target association report: `outputs/feature_engineering/feature_target_associations.csv`",
            "",
            "## Caveats",
            "",
            "- The current feature engineering is based on the synthetic prototype dataset.",
            "- Feature selection uses training rows only, but selected features still require Phase 7 model validation.",
            "- VIF is expected to flag compositional groups such as texture and taxa because they contain sum constraints.",
            "- Phase 6 features are interpretable proxies, not proof of causal agronomic mechanisms.",
        ]
    )
    FEATURE_SELECTION_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(engineered: pd.DataFrame) -> dict[str, object]:
    with_splits = add_split_membership(engineered)
    train = with_splits[with_splits["Split"] == "train"].copy()
    feature_cols = numeric_candidate_columns(engineered)

    assoc = compute_target_associations(train, feature_cols)
    redundancy = compute_redundancy_pairs(train, feature_cols)
    vif = compute_vif(train, feature_cols)
    selected_features, selection_decisions = select_features(train, assoc, feature_cols)

    engineered_cols = ID_COLUMNS + ["Village", "Split"] + TARGET_COLUMNS
    engineered_cols += [c for c in ["Microbial_Richness_Score", "Nutrient_Balance_Ratio", "Pathogen_Load_Index", "Soil_Health_Index"] if c in with_splits.columns]
    engineered_cols += PHASE6_FEATURES
    with_splits[engineered_cols].to_csv(ENGINEERED_FEATURE_TABLE, index=False)
    with_splits.to_csv(FEATURE_TABLE, index=False)

    docs = build_feature_documentation()
    docs.to_csv(FEATURE_DOCUMENTATION, index=False)

    assoc.to_csv(TARGET_ASSOCIATION_REPORT, index=False)
    redundancy.to_csv(REDUNDANCY_REPORT, index=False)
    vif.to_csv(VIF_REPORT, index=False)
    selection_decisions.to_csv(FEATURE_OUTPUT_DIR / "feature_selection_decisions.csv", index=False)

    payload = {
        "selected_numeric_features": selected_features,
        "categorical_features_for_encoding": CATEGORICAL_FEATURES,
        "target_columns": TARGET_COLUMNS,
        "selection_split": "train",
        "max_features": 34,
        "redundancy_threshold": 0.95,
        "phase6_engineered_features": PHASE6_FEATURES,
        "notes": [
            "Selected features are biologically meaningful and filtered for redundancy on the training split.",
            "Categorical features should be encoded by the Phase 5 preprocessing approach.",
        ],
    }
    SELECTED_FEATURES_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary = {
        "rows": int(len(engineered)),
        "phase6_feature_count": len(PHASE6_FEATURES),
        "candidate_numeric_feature_count": len(feature_cols),
        "selected_numeric_feature_count": len(selected_features),
        "redundancy_pairs_abs_corr_ge_0_90": int(len(redundancy)),
        "vif_ge_10_count": int(len(vif[vif["VIF"] >= 10])),
        "selected_features": selected_features,
        "outputs": {
            "engineered_feature_table": str(ENGINEERED_FEATURE_TABLE.relative_to(PROJECT_ROOT)),
            "feature_table": str(FEATURE_TABLE.relative_to(PROJECT_ROOT)),
            "feature_documentation": str(FEATURE_DOCUMENTATION.relative_to(PROJECT_ROOT)),
            "selected_features": str(SELECTED_FEATURES_JSON.relative_to(PROJECT_ROOT)),
            "feature_selection_report": str(FEATURE_SELECTION_REPORT.relative_to(PROJECT_ROOT)),
        },
    }
    FEATURE_SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_feature_selection_report(engineered, assoc, selected_features, selection_decisions, redundancy, vif)
    return summary


def main() -> None:
    ensure_dirs()
    if not CLEAN_MASTER.exists():
        raise FileNotFoundError("Phase 5 clean master dataset is missing. Run Phase 5 preprocessing first.")
    if not SPLIT_MEMBERSHIP.exists():
        raise FileNotFoundError("Phase 5 split membership file is missing. Run Phase 5 preprocessing first.")

    df = pd.read_csv(CLEAN_MASTER)
    engineered = calculate_phase6_features(df)
    summary = write_outputs(engineered)
    print("Phase 6 feature engineering complete.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

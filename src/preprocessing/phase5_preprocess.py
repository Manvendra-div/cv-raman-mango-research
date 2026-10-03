"""Phase 5 data integration and preprocessing pipeline.

This script builds reproducible Phase 5 outputs from the current synthetic
mango microbiome CSV. It also defines the same merge keys, cleaning rules, and
output schemas expected when real Phase 3/4 field and lab tables become
available.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = PROJECT_ROOT / "data" / "raw" / "mango_microbiome_dataset.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "phase5_preprocessing"

CLEAN_MASTER = PROCESSED_DIR / "clean_master_dataset.csv"
DATA_DICTIONARY = PROCESSED_DIR / "data_dictionary.csv"
MODEL_READY_ALL = PROCESSED_DIR / "model_ready_all_features.csv"
MODEL_READY_TARGETS = PROCESSED_DIR / "model_ready_all_targets.csv"
FEATURE_COLUMNS_JSON = PROCESSED_DIR / "preprocessing_feature_columns.json"
REPORT_MD = REPORT_DIR / "preprocessing_report.md"
SUMMARY_JSON = REPORT_DIR / "preprocessing_summary.json"

RANDOM_STATE = 42
GEOGRAPHIC_HOLDOUT_VILLAGE = "Rahimabad"

ID_COLUMNS = ["Sample_ID", "Orchard_ID"]
TARGET_COLUMNS = ["Mango_Yield", "Disease_Risk", "Nutrient_Availability"]

CATEGORICAL_FEATURES = [
    "Village",
    "Mango_Variety",
    "Soil_Depth",
    "Sampling_Season",
    "Management",
]

EXCLUDED_FROM_MODEL_FEATURES = set(ID_COLUMNS + TARGET_COLUMNS + ["Orchard_ID"])

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
TAXA_COLUMNS = BACTERIAL_TAXA + FUNGAL_TAXA + ARCHAEAL_TAXA


@dataclass(frozen=True)
class DataDictionaryEntry:
    column: str
    group: str
    role: str
    unit: str
    description: str
    preprocessing_note: str


def ensure_dirs() -> None:
    for path in [PROCESSED_DIR, SPLITS_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_raw_dataset() -> pd.DataFrame:
    if not RAW_DATA.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_DATA}")
    return pd.read_csv(RAW_DATA)


def normalize_depth_label(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip()
    numbers = re.findall(r"\d+", text)
    if len(numbers) >= 2:
        return f"{numbers[0]}-{numbers[1]}"
    return text.replace("_", "-")


def standardize_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column in CATEGORICAL_FEATURES + ["Orchard_ID", "Sample_ID"]:
        if column in out.columns:
            out[column] = out[column].astype("string").str.strip()

    if "Soil_Depth" in out.columns:
        out["Soil_Depth"] = out["Soil_Depth"].map(normalize_depth_label)

    if "Mango_Variety" in out.columns:
        variety_map = {
            "Dasheri": "Dashehari",
            "Dusseheri": "Dashehari",
            "Dusheri": "Dashehari",
        }
        out["Mango_Variety"] = out["Mango_Variety"].replace(variety_map)

    return out


def fill_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int], dict[str, int]]:
    out = df.copy()
    missing_before = out.isna().sum().astype(int).to_dict()

    feature_columns = [c for c in out.columns if c not in TARGET_COLUMNS]
    numeric_features = out[feature_columns].select_dtypes(include=["number"]).columns.tolist()
    categorical_features = [
        c
        for c in feature_columns
        if c not in numeric_features and c in out.columns
    ]

    for column in numeric_features:
        if out[column].isna().any():
            out[column] = out[column].fillna(out[column].median())

    for column in categorical_features:
        if out[column].isna().any():
            out[column] = out[column].fillna("Unknown")

    missing_after = out.isna().sum().astype(int).to_dict()
    return out, missing_before, missing_after


def normalize_taxa_group(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    cols = [c for c in columns if c in out.columns]
    if not cols:
        return out

    out[cols] = out[cols].clip(lower=0)
    sums = out[cols].sum(axis=1)
    nonzero = sums > 0
    out.loc[nonzero, cols] = out.loc[nonzero, cols].div(sums[nonzero], axis=0) * 100.0
    out.loc[~nonzero, cols] = 0.0
    return out


def clean_and_standardize(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    report: dict[str, object] = {}
    out = df.copy()

    report["raw_rows"] = int(len(out))
    report["raw_columns"] = int(out.shape[1])
    report["duplicate_rows_before"] = int(out.duplicated().sum())

    out = standardize_categoricals(out)
    out, missing_before, missing_after = fill_missing_values(out)
    report["missing_values_before"] = {k: v for k, v in missing_before.items() if v}
    report["missing_values_after"] = {k: v for k, v in missing_after.items() if v}

    negative_taxa_counts = {
        column: int((out[column] < 0).sum())
        for column in TAXA_COLUMNS
        if column in out.columns
    }
    report["negative_taxa_values_before"] = {
        k: v for k, v in negative_taxa_counts.items() if v
    }

    out = normalize_taxa_group(out, BACTERIAL_TAXA)
    out = normalize_taxa_group(out, FUNGAL_TAXA)
    out = normalize_taxa_group(out, ARCHAEAL_TAXA)

    negative_taxa_after = {
        column: int((out[column] < 0).sum())
        for column in TAXA_COLUMNS
        if column in out.columns
    }
    report["negative_taxa_values_after"] = {
        k: v for k, v in negative_taxa_after.items() if v
    }

    if "Sample_ID" in out.columns:
        report["unique_sample_ids"] = int(out["Sample_ID"].nunique())
    if "Orchard_ID" in out.columns:
        report["unique_orchard_ids"] = int(out["Orchard_ID"].nunique())

    out["Preprocessing_Status"] = "Cleaned"
    out["Compositional_Normalization"] = "Taxa normalized within bacterial, fungal, and archaeal groups"

    report["clean_rows"] = int(len(out))
    report["clean_columns"] = int(out.shape[1])
    return out, report


def build_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    metadata_cols = {
        "Sample_ID",
        "Orchard_ID",
        "Village",
        "Latitude",
        "Longitude",
        "Mango_Variety",
        "Tree_Age",
        "Soil_Depth",
        "Sampling_Season",
        "Management",
    }
    soil_cols = {
        "pH",
        "EC",
        "Organic_Carbon",
        "Total_Nitrogen",
        "Available_P",
        "Available_K",
        "Soil_Moisture",
        "Soil_Temperature",
        "Bulk_Density",
        "CEC",
        "Sand",
        "Silt",
        "Clay",
        "Zn",
        "Fe",
        "Mn",
        "Cu",
        "C_N_Ratio",
    }
    climate_cols = {"Air_Temp_Avg", "Rainfall", "Humidity", "Solar_Radiation"}
    diversity_cols = {"OTU_Count", "Shannon_Index", "Simpson_Index", "Chao1_Richness", "Pielou_Evenness"}
    functional_cols = {
        "Nitrogen_Fixers",
        "Phosphate_Solubilizers_PSB",
        "Potassium_Solubilizers",
        "Mycorrhizae_AMF",
        "Trichoderma",
        "Pseudomonas_PGPR",
        "Fusarium",
        "Pathogen_Load_Index",
    }
    engineered_cols = {"Microbial_Richness_Score", "Nutrient_Balance_Ratio", "Soil_Health_Index"}

    units = {
        "Latitude": "degrees_north",
        "Longitude": "degrees_east",
        "Tree_Age": "years",
        "EC": "dS_per_m",
        "Organic_Carbon": "percent",
        "Total_Nitrogen": "kg_per_ha",
        "Available_P": "kg_per_ha",
        "Available_K": "kg_per_ha",
        "Soil_Moisture": "percent",
        "Soil_Temperature": "deg_C",
        "Bulk_Density": "g_per_cm3",
        "CEC": "cmol_per_kg",
        "Sand": "percent",
        "Silt": "percent",
        "Clay": "percent",
        "Zn": "ppm",
        "Fe": "ppm",
        "Mn": "ppm",
        "Cu": "ppm",
        "Air_Temp_Avg": "deg_C",
        "Rainfall": "mm",
        "Humidity": "percent",
        "Solar_Radiation": "MJ_per_m2_day",
        "Mango_Yield": "kg_per_tree",
    }
    for col in TAXA_COLUMNS:
        units[col] = "percent_relative_abundance"

    descriptions = {
        "Sample_ID": "Unique sample identifier.",
        "Orchard_ID": "Synthetic or field orchard identifier.",
        "Village": "Village or study-site label.",
        "Mango_Yield": "Mango yield target for regression.",
        "Disease_Risk": "Disease-risk class target.",
        "Nutrient_Availability": "Nutrient-availability class target.",
        "Preprocessing_Status": "Row-level preprocessing status.",
        "Compositional_Normalization": "Taxonomic normalization note.",
    }

    rows: list[DataDictionaryEntry] = []
    for column in df.columns:
        if column in metadata_cols:
            group = "sample_site_metadata"
        elif column in soil_cols:
            group = "soil_physicochemical"
        elif column in climate_cols:
            group = "climate_weather"
        elif column in diversity_cols:
            group = "microbiome_diversity"
        elif column in TAXA_COLUMNS:
            group = "taxonomic_relative_abundance"
        elif column in functional_cols:
            group = "functional_microbes_pathogen"
        elif column in engineered_cols:
            group = "engineered_existing"
        elif column in TARGET_COLUMNS:
            group = "target"
        elif column in {"Preprocessing_Status", "Compositional_Normalization"}:
            group = "preprocessing_metadata"
        else:
            group = "other"

        if column in TARGET_COLUMNS:
            role = "target"
        elif column in ID_COLUMNS or column in {"Preprocessing_Status", "Compositional_Normalization"}:
            role = "identifier_or_metadata"
        elif column == "Orchard_ID":
            role = "metadata_not_default_model_feature"
        else:
            role = "feature"

        note = ""
        if column == "Soil_Depth":
            note = "Standardized to ASCII labels such as 0-15 and 15-30."
        elif column in TAXA_COLUMNS:
            note = "Negative values clipped to zero, then normalized within domain group."
        elif column in CATEGORICAL_FEATURES:
            note = "Categorical values stripped and encoded in model-ready outputs."
        elif pd.api.types.is_numeric_dtype(df[column]) and column not in TARGET_COLUMNS:
            note = "Numeric feature scaled in model-ready outputs."

        rows.append(
            DataDictionaryEntry(
                column=column,
                group=group,
                role=role,
                unit=units.get(column, "not_applicable"),
                description=descriptions.get(column, f"{column} variable from integrated dataset."),
                preprocessing_note=note,
            )
        )

    return pd.DataFrame([entry.__dict__ for entry in rows])


def make_splits(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if "Village" not in df.columns:
        raise ValueError("Village column is required for geographic hold-out split.")

    holdout = df[df["Village"] == GEOGRAPHIC_HOLDOUT_VILLAGE].copy()
    remaining = df[df["Village"] != GEOGRAPHIC_HOLDOUT_VILLAGE].copy()

    if remaining.empty:
        raise ValueError("No rows remain after geographic hold-out split.")

    stratify = remaining["Disease_Risk"] if "Disease_Risk" in remaining.columns else None
    train, temp = train_test_split(
        remaining,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    temp_stratify = temp["Disease_Risk"] if "Disease_Risk" in temp.columns else None
    validation, test = train_test_split(
        temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp_stratify,
    )

    return {
        "train": train.copy(),
        "validation": validation.copy(),
        "test": test.copy(),
        "holdout_rahimabad": holdout.copy(),
    }


def write_split_files(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    membership_parts = []
    for split_name, split_df in splits.items():
        path = SPLITS_DIR / f"{split_name}.csv"
        split_df.to_csv(path, index=False)
        membership_parts.append(
            split_df[["Sample_ID"]].assign(Split=split_name)
        )
    membership = pd.concat(membership_parts, ignore_index=True)
    membership.to_csv(SPLITS_DIR / "split_membership.csv", index=False)
    return membership


def get_model_feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    candidate_cols = [c for c in df.columns if c not in EXCLUDED_FROM_MODEL_FEATURES]
    candidate_cols = [
        c
        for c in candidate_cols
        if c not in {"Preprocessing_Status", "Compositional_Normalization"}
    ]
    numeric_features = [
        c
        for c in candidate_cols
        if pd.api.types.is_numeric_dtype(df[c])
    ]
    categorical_features = [
        c
        for c in CATEGORICAL_FEATURES
        if c in candidate_cols
    ]
    return numeric_features, categorical_features


def build_model_ready_outputs(
    splits: dict[str, pd.DataFrame],
    numeric_features: list[str],
    categorical_features: list[str],
) -> dict[str, object]:
    transformer = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric_features),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    train = splits["train"]
    transformer.fit(train[numeric_features + categorical_features])
    feature_names = transformer.get_feature_names_out().tolist()

    all_feature_parts = []
    all_target_parts = []
    split_shapes: dict[str, dict[str, int]] = {}

    for split_name, split_df in splits.items():
        matrix = transformer.transform(split_df[numeric_features + categorical_features])
        feature_df = pd.DataFrame(matrix, columns=feature_names, index=split_df.index)
        feature_df.insert(0, "Sample_ID", split_df["Sample_ID"].to_numpy())
        feature_df.insert(1, "Split", split_name)
        feature_path = PROCESSED_DIR / f"model_ready_{split_name}_features.csv"
        feature_df.to_csv(feature_path, index=False)
        all_feature_parts.append(feature_df)

        target_df = split_df[["Sample_ID"] + TARGET_COLUMNS].copy()
        target_df.insert(1, "Split", split_name)
        target_path = PROCESSED_DIR / f"model_ready_{split_name}_targets.csv"
        target_df.to_csv(target_path, index=False)
        all_target_parts.append(target_df)

        split_shapes[split_name] = {
            "rows": int(len(split_df)),
            "encoded_feature_columns": int(len(feature_names)),
        }

    pd.concat(all_feature_parts, ignore_index=True).to_csv(MODEL_READY_ALL, index=False)
    pd.concat(all_target_parts, ignore_index=True).to_csv(MODEL_READY_TARGETS, index=False)

    feature_payload = {
        "numeric_features_scaled": numeric_features,
        "categorical_features_encoded": categorical_features,
        "encoded_feature_names": feature_names,
        "excluded_from_default_model_features": sorted(EXCLUDED_FROM_MODEL_FEATURES),
        "fit_split": "train",
        "geographic_holdout_village": GEOGRAPHIC_HOLDOUT_VILLAGE,
        "random_state": RANDOM_STATE,
    }
    FEATURE_COLUMNS_JSON.write_text(json.dumps(feature_payload, indent=2), encoding="utf-8")

    return {
        "split_shapes": split_shapes,
        "encoded_feature_count": len(feature_names),
        "numeric_feature_count": len(numeric_features),
        "categorical_feature_count": len(categorical_features),
    }


def write_report(summary: dict[str, object]) -> None:
    split_counts = summary["split_counts"]
    negative_before = summary["cleaning_report"].get("negative_taxa_values_before", {})
    negative_after = summary["cleaning_report"].get("negative_taxa_values_after", {})
    disease_counts = summary.get("disease_risk_counts", {})
    nutrient_counts = summary.get("nutrient_availability_counts", {})

    lines = [
        "# Phase 5 Preprocessing Report",
        "",
        "Generated by `src/preprocessing/phase5_preprocess.py`.",
        "",
        "## Input",
        "",
        f"- Raw dataset: `{RAW_DATA.relative_to(PROJECT_ROOT)}`",
        f"- Raw rows: {summary['cleaning_report']['raw_rows']}",
        f"- Raw columns: {summary['cleaning_report']['raw_columns']}",
        "",
        "## Cleaning Actions",
        "",
        "- Standardized categorical text values.",
        "- Fixed soil-depth labels to ASCII values such as `0-15` and `15-30`.",
        "- Imputed missing numeric feature values with the median where needed.",
        "- Imputed missing categorical feature values as `Unknown` where needed.",
        "- Clipped negative taxonomic relative abundances to zero.",
        "- Normalized bacterial, fungal, and archaeal relative-abundance groups separately.",
        "",
        f"- Negative taxa values before cleaning: `{negative_before}`",
        f"- Negative taxa values after cleaning: `{negative_after}`",
        "",
        "## Outputs",
        "",
        f"- Clean master dataset: `{CLEAN_MASTER.relative_to(PROJECT_ROOT)}`",
        f"- Data dictionary: `{DATA_DICTIONARY.relative_to(PROJECT_ROOT)}`",
        f"- Model-ready feature matrix: `{MODEL_READY_ALL.relative_to(PROJECT_ROOT)}`",
        f"- Model-ready targets: `{MODEL_READY_TARGETS.relative_to(PROJECT_ROOT)}`",
        f"- Split membership: `data/splits/split_membership.csv`",
        "",
        "## Split Counts",
        "",
    ]
    for split_name, count in split_counts.items():
        lines.append(f"- {split_name}: {count}")

    lines.extend(
        [
            "",
            "## Target Class Counts",
            "",
            f"- Disease risk: `{disease_counts}`",
            f"- Nutrient availability: `{nutrient_counts}`",
            "",
            "## Known Caveats",
            "",
            "- The current dataset is synthetic, not a real field dataset.",
            "- `Nutrient_Availability` currently lacks the `Deficient` class.",
            "- `Orchard_ID` is preserved in the clean master dataset but excluded from the default model-ready feature matrix to reduce identifier leakage risk.",
            "- Encoders and scalers are fit on the training split only, then applied to validation, test, and Rahimabad hold-out splits.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw = read_raw_dataset()
    clean, cleaning_report = clean_and_standardize(raw)

    clean.to_csv(CLEAN_MASTER, index=False)
    data_dictionary = build_data_dictionary(clean)
    data_dictionary.to_csv(DATA_DICTIONARY, index=False)

    splits = make_splits(clean)
    membership = write_split_files(splits)
    numeric_features, categorical_features = get_model_feature_columns(clean)
    model_ready_summary = build_model_ready_outputs(splits, numeric_features, categorical_features)

    split_counts = {name: int(len(frame)) for name, frame in splits.items()}
    summary = {
        "cleaning_report": cleaning_report,
        "split_counts": split_counts,
        "split_membership_rows": int(len(membership)),
        "disease_risk_counts": clean["Disease_Risk"].value_counts().astype(int).to_dict(),
        "nutrient_availability_counts": clean["Nutrient_Availability"].value_counts().astype(int).to_dict(),
        "model_ready_summary": model_ready_summary,
        "outputs": {
            "clean_master_dataset": str(CLEAN_MASTER.relative_to(PROJECT_ROOT)),
            "data_dictionary": str(DATA_DICTIONARY.relative_to(PROJECT_ROOT)),
            "model_ready_all_features": str(MODEL_READY_ALL.relative_to(PROJECT_ROOT)),
            "model_ready_all_targets": str(MODEL_READY_TARGETS.relative_to(PROJECT_ROOT)),
            "split_membership": "data/splits/split_membership.csv",
        },
    }
    write_report(summary)

    print("Phase 5 preprocessing complete.")
    print(json.dumps({"split_counts": split_counts, "outputs": summary["outputs"]}, indent=2))


if __name__ == "__main__":
    main()

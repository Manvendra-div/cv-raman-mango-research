"""Phase 8 Explainable AI for verified Phase 7 champion models.

Generates SHAP and LIME explanations, dependence diagnostics, local
waterfall-style plots, and agronomic recommendation rules for the current
champion regression and classification models.
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from lime.lime_tabular import LimeTabularExplainer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_TABLE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"
SELECTED_FEATURES_JSON = PROJECT_ROOT / "data" / "processed" / "selected_features.json"

REGRESSION_CHAMPION_MODEL = PROJECT_ROOT / "outputs" / "models" / "regression" / "champion_regression_model.joblib"
DISEASE_CHAMPION_MODEL = PROJECT_ROOT / "outputs" / "models" / "classification" / "champion_disease_risk_model.joblib"
NUTRIENT_CHAMPION_MODEL = PROJECT_ROOT / "outputs" / "models" / "classification" / "champion_nutrient_availability_model.joblib"

BASE_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "explainability" / "phase8_xai"
FIGURE_DIR = BASE_OUTPUT_DIR / "figures"
TABLE_DIR = BASE_OUTPUT_DIR / "tables"
LOCAL_DIR = BASE_OUTPUT_DIR / "local_explanations"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "phase8_explainable_ai"

GLOBAL_IMPORTANCE_CSV = TABLE_DIR / "phase8_global_feature_importance.csv"
TRANSFORMED_SHAP_CSV = TABLE_DIR / "phase8_shap_transformed_feature_importance.csv"
DEPENDENCE_CSV = TABLE_DIR / "phase8_shap_dependence_thresholds.csv"
LOCAL_SHAP_CSV = TABLE_DIR / "phase8_local_shap_explanations.csv"
LIME_CSV = TABLE_DIR / "phase8_lime_local_explanations.csv"
LOCAL_SAMPLE_CSV = TABLE_DIR / "phase8_local_sample_summary.csv"
RECOMMENDATION_RULES_CSV = TABLE_DIR / "phase8_recommendation_rules.csv"
INSTANCE_RECOMMENDATIONS_CSV = TABLE_DIR / "phase8_instance_recommendations.csv"
FEATURE_AUDIT_CSV = TABLE_DIR / "phase8_expected_feature_audit.csv"
SUMMARY_JSON = TABLE_DIR / "phase8_xai_summary.json"
REPORT_MD = REPORT_DIR / "phase8_explainable_ai_report.md"

RANDOM_STATE = 42
BACKGROUND_SIZE = 120
EXPLAIN_SIZE = 220
MAX_DISPLAY = 20
LOCAL_EXPLANATIONS_PER_TARGET = 3


@dataclass(frozen=True)
class TargetConfig:
    key: str
    target_column: str
    model_path: Path
    task: str
    output_label: str
    class_of_interest: str | None = None


TARGET_CONFIGS = [
    TargetConfig(
        key="mango_yield",
        target_column="Mango_Yield",
        model_path=REGRESSION_CHAMPION_MODEL,
        task="regression",
        output_label="Predicted Mango_Yield",
    ),
    TargetConfig(
        key="disease_risk",
        target_column="Disease_Risk",
        model_path=DISEASE_CHAMPION_MODEL,
        task="classification",
        output_label="Probability of High Disease_Risk",
        class_of_interest="High",
    ),
    TargetConfig(
        key="nutrient_availability",
        target_column="Nutrient_Availability",
        model_path=NUTRIENT_CHAMPION_MODEL,
        task="classification",
        output_label="Probability of High Nutrient_Availability",
        class_of_interest="High",
    ),
]

DEPENDENCE_FEATURES = {
    "mango_yield": [
        "Soil_Health_Index",
        "Soil_Health_Index_Phase6",
        "NPK_Balance_Score_Phase6",
        "Microbial_Richness_Score",
    ],
    "disease_risk": [
        "Pathogen_Load_Index",
        "Pathogen_Load_Index_Phase6",
        "Beneficial_Microbial_Index_Phase6",
        "Pathogen_Beneficial_Ratio_Phase6",
    ],
    "nutrient_availability": [
        "NPK_Balance_Score_Phase6",
        "Available_P",
        "Available_K",
        "Total_Nitrogen",
    ],
}

EXPECTED_EXPLANATION_FEATURES = [
    "Pathogen_Load_Index",
    "Pathogen_Load_Index_Phase6",
    "Soil_Health_Index",
    "Soil_Health_Index_Phase6",
    "NPK_Balance_Score_Phase6",
    "Microbial_Richness_Score",
    "Fusarium",
    "Beneficial_Microbial_Index_Phase6",
]


def ensure_dirs() -> None:
    for path in [FIGURE_DIR, TABLE_DIR, LOCAL_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_selected_features() -> tuple[list[str], list[str]]:
    payload = json.loads(SELECTED_FEATURES_JSON.read_text(encoding="utf-8"))
    return payload["selected_numeric_features"], payload["categorical_features_for_encoding"]


def load_feature_table() -> pd.DataFrame:
    if not FEATURE_TABLE.exists():
        raise FileNotFoundError("Missing Phase 6 feature table. Run Phases 5 and 6 before Phase 8.")
    df = pd.read_csv(FEATURE_TABLE)
    if "Split" not in df.columns:
        raise ValueError("Feature table must contain the Phase 5 Split column.")
    return df


def build_feature_matrix(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    missing = [col for col in numeric + categorical if col not in df.columns]
    if missing:
        raise ValueError(f"Missing selected feature columns: {missing}")
    return df[numeric + categorical].copy()


def transformed_feature_names(pipeline: Any) -> list[str]:
    return [str(name) for name in pipeline.named_steps["preprocess"].get_feature_names_out()]


def transform_features(pipeline: Any, raw_x: pd.DataFrame, feature_names: list[str]) -> pd.DataFrame:
    transformed = pipeline.named_steps["preprocess"].transform(raw_x)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    return pd.DataFrame(transformed, columns=feature_names, index=raw_x.index)


def original_feature_name(feature_name: str, numeric: list[str], categorical: list[str]) -> str:
    if feature_name in numeric:
        return feature_name
    for column in categorical:
        if feature_name == column or feature_name.startswith(f"{column}_"):
            return column
    return feature_name


def make_output_function(config: TargetConfig, model: Any, feature_names: list[str]) -> tuple[Callable[[Any], np.ndarray], int | None]:
    estimator = model.named_steps["model"]
    if config.task == "regression":
        return lambda values: estimator.predict(np.asarray(values)), None

    classes = [str(value) for value in estimator.classes_]
    if config.class_of_interest not in classes:
        raise ValueError(f"Class {config.class_of_interest} not available for {config.target_column}: {classes}")
    class_index = classes.index(str(config.class_of_interest))

    def predict_class_probability(values: Any) -> np.ndarray:
        array = np.asarray(values)
        return estimator.predict_proba(array)[:, class_index]

    return predict_class_probability, class_index


def output_values_for_raw(config: TargetConfig, pipeline: Any, raw_x: pd.DataFrame) -> np.ndarray:
    if config.task == "regression":
        return pipeline.predict(raw_x)
    classes = [str(value) for value in pipeline.named_steps["model"].classes_]
    class_index = classes.index(str(config.class_of_interest))
    return pipeline.predict_proba(raw_x)[:, class_index]


def select_local_indices(config: TargetConfig, df: pd.DataFrame, raw_features: pd.DataFrame, pipeline: Any) -> list[int]:
    validation = df[df["Split"] == "validation"].copy()
    holdout = df[df["Split"] == "holdout_rahimabad"].copy()

    selected: list[int] = []
    validation_output = pd.Series(
        output_values_for_raw(config, pipeline, raw_features.loc[validation.index]),
        index=validation.index,
    )
    holdout_output = pd.Series(
        output_values_for_raw(config, pipeline, raw_features.loc[holdout.index]),
        index=holdout.index,
    )

    if config.task == "regression":
        selected.extend(
            [
                int(validation_output.idxmax()),
                int(validation_output.idxmin()),
                int(holdout_output.idxmax()),
            ]
        )
    else:
        selected.extend(
            [
                int(validation_output.idxmax()),
                int((validation_output - 0.5).abs().idxmin()),
                int(holdout_output.idxmax()),
            ]
        )

    unique: list[int] = []
    for index in selected:
        if index not in unique:
            unique.append(index)
    return unique[:LOCAL_EXPLANATIONS_PER_TARGET]


def select_explain_indices(
    config: TargetConfig,
    df: pd.DataFrame,
    raw_features: pd.DataFrame,
    pipeline: Any,
) -> tuple[list[int], list[int]]:
    validation = df[df["Split"] == "validation"]
    sample_size = min(EXPLAIN_SIZE, len(validation))
    sampled = validation.sample(n=sample_size, random_state=RANDOM_STATE).index.tolist()
    local_indices = select_local_indices(config, df, raw_features, pipeline)
    combined = list(dict.fromkeys(sampled + local_indices))
    return combined, local_indices


def compute_permutation_shap(
    output_function: Callable[[Any], np.ndarray],
    background: pd.DataFrame,
    explain: pd.DataFrame,
) -> shap.Explanation:
    masker = shap.maskers.Independent(background, max_samples=min(BACKGROUND_SIZE, len(background)))
    explainer = shap.Explainer(
        output_function,
        masker,
        algorithm="permutation",
        feature_names=explain.columns.tolist(),
    )
    return explainer(
        explain,
        max_evals=(2 * explain.shape[1]) + 1,
        batch_size=64,
        silent=True,
    )


def native_importance_rows(
    config: TargetConfig,
    estimator: Any,
    feature_names: list[str],
    numeric: list[str],
    categorical: list[str],
) -> list[dict[str, Any]]:
    values: np.ndarray | None = None
    source = ""
    if hasattr(estimator, "coef_"):
        coef = np.asarray(estimator.coef_)
        values = np.abs(coef).ravel()
        source = "Absolute_Coefficient"
    elif hasattr(estimator, "feature_importances_"):
        values = np.asarray(estimator.feature_importances_)
        source = "Model_Feature_Importance"

    if values is None:
        return []

    rows = []
    for feature, value in zip(feature_names, values, strict=False):
        rows.append(
            {
                "Target": config.target_column,
                "Output_Explained": config.output_label,
                "Importance_Type": source,
                "Feature": feature,
                "Original_Feature": original_feature_name(feature, numeric, categorical),
                "Importance": float(value),
            }
        )
    return rows


def summarize_shap_importance(
    config: TargetConfig,
    explanation: shap.Explanation,
    transformed_x: pd.DataFrame,
    raw_x: pd.DataFrame,
    numeric: list[str],
    categorical: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    shap_values = np.asarray(explanation.values, dtype=float)
    rows = []
    for column_index, feature in enumerate(transformed_x.columns):
        original = original_feature_name(feature, numeric, categorical)
        feature_values = transformed_x[feature]
        shap_feature = shap_values[:, column_index]
        spearman = pd.Series(feature_values).corr(pd.Series(shap_feature), method="spearman")
        rows.append(
            {
                "Target": config.target_column,
                "Output_Explained": config.output_label,
                "Feature": feature,
                "Original_Feature": original,
                "Mean_Abs_SHAP": float(np.mean(np.abs(shap_feature))),
                "Mean_SHAP": float(np.mean(shap_feature)),
                "Spearman_Feature_SHAP": float(spearman) if pd.notna(spearman) else np.nan,
            }
        )
    transformed = pd.DataFrame(rows).sort_values(["Target", "Mean_Abs_SHAP"], ascending=[True, False])
    transformed["Transformed_Feature_Rank"] = transformed.groupby("Target")["Mean_Abs_SHAP"].rank(
        ascending=False,
        method="first",
    ).astype(int)

    original = (
        transformed.groupby(["Target", "Output_Explained", "Original_Feature"], as_index=False)
        .agg(
            Importance=("Mean_Abs_SHAP", "sum"),
            Mean_SHAP=("Mean_SHAP", "sum"),
            Top_Transformed_Feature=("Feature", "first"),
        )
        .sort_values(["Target", "Importance"], ascending=[True, False])
    )
    original["Importance_Type"] = "SHAP_Mean_Abs_Aggregated"
    original["Rank"] = original.groupby("Target")["Importance"].rank(ascending=False, method="first").astype(int)
    return transformed, original


def plot_shap_summaries(config: TargetConfig, explanation: shap.Explanation, transformed_x: pd.DataFrame) -> list[str]:
    paths: list[str] = []
    bar_path = FIGURE_DIR / f"shap_summary_bar_{config.key}.png"
    beeswarm_path = FIGURE_DIR / f"shap_summary_beeswarm_{config.key}.png"

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        plt.figure()
        shap.summary_plot(
            explanation.values,
            transformed_x,
            plot_type="bar",
            max_display=MAX_DISPLAY,
            show=False,
        )
    plt.title(f"{config.target_column}: SHAP summary")
    plt.tight_layout()
    plt.savefig(bar_path, dpi=180, bbox_inches="tight")
    plt.close()
    paths.append(str(bar_path.relative_to(PROJECT_ROOT)))

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        plt.figure()
        shap.summary_plot(
            explanation.values,
            transformed_x,
            max_display=MAX_DISPLAY,
            show=False,
        )
    plt.title(f"{config.target_column}: SHAP distribution")
    plt.tight_layout()
    plt.savefig(beeswarm_path, dpi=180, bbox_inches="tight")
    plt.close()
    paths.append(str(beeswarm_path.relative_to(PROJECT_ROOT)))
    return paths


def plot_aggregated_importance(config: TargetConfig, global_importance: pd.DataFrame) -> str:
    subset = global_importance[
        (global_importance["Target"] == config.target_column)
        & (global_importance["Importance_Type"] == "SHAP_Mean_Abs_Aggregated")
    ].sort_values("Importance", ascending=False).head(15)
    path = FIGURE_DIR / f"shap_original_feature_importance_{config.key}.png"
    plt.figure(figsize=(8, 5))
    plt.barh(subset["Original_Feature"][::-1], subset["Importance"][::-1], color="#2f6f73")
    plt.xlabel("Mean absolute SHAP contribution")
    plt.ylabel("Original feature")
    plt.title(f"{config.target_column}: aggregated SHAP importance")
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    return str(path.relative_to(PROJECT_ROOT))


def plot_dependence(
    config: TargetConfig,
    feature: str,
    raw_x: pd.DataFrame,
    transformed_x: pd.DataFrame,
    shap_values: np.ndarray,
) -> tuple[str | None, dict[str, Any] | None]:
    if feature not in raw_x.columns or feature not in transformed_x.columns:
        return None, None

    feature_index = transformed_x.columns.get_loc(feature)
    x_values = raw_x[feature].astype(float)
    y_values = shap_values[:, feature_index]
    q25 = float(x_values.quantile(0.25))
    q50 = float(x_values.quantile(0.50))
    q75 = float(x_values.quantile(0.75))
    spearman = x_values.corr(pd.Series(y_values, index=x_values.index), method="spearman")
    low_mean = float(pd.Series(y_values, index=x_values.index)[x_values <= q25].mean())
    high_mean = float(pd.Series(y_values, index=x_values.index)[x_values >= q75].mean())

    path = FIGURE_DIR / f"shap_dependence_{config.key}_{feature.lower()}.png"
    plt.figure(figsize=(7, 4.5))
    plt.scatter(x_values, y_values, s=15, alpha=0.7, color="#445e93")
    plt.axvline(q25, color="#9f6a38", linestyle="--", linewidth=1, label="Q25")
    plt.axvline(q50, color="#444444", linestyle=":", linewidth=1, label="Median")
    plt.axvline(q75, color="#28774f", linestyle="--", linewidth=1, label="Q75")
    plt.axhline(0, color="#222222", linewidth=0.8)
    plt.xlabel(feature)
    plt.ylabel("SHAP contribution")
    plt.title(f"{config.target_column}: {feature}")
    plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()

    row = {
        "Target": config.target_column,
        "Output_Explained": config.output_label,
        "Feature": feature,
        "Q25": q25,
        "Median": q50,
        "Q75": q75,
        "Spearman_Feature_SHAP": float(spearman) if pd.notna(spearman) else np.nan,
        "Low_Quartile_Mean_SHAP": low_mean,
        "High_Quartile_Mean_SHAP": high_mean,
        "High_Minus_Low_SHAP": high_mean - low_mean,
        "Figure": str(path.relative_to(PROJECT_ROOT)),
    }
    return str(path.relative_to(PROJECT_ROOT)), row


def prediction_metadata(config: TargetConfig, pipeline: Any, row: pd.Series, raw_x: pd.DataFrame) -> dict[str, Any]:
    x_row = raw_x.loc[[row.name]]
    predicted = pipeline.predict(x_row)[0]
    output_value = float(output_values_for_raw(config, pipeline, x_row)[0])
    metadata = {
        "Target": config.target_column,
        "Output_Explained": config.output_label,
        "Sample_ID": row["Sample_ID"],
        "Split": row["Split"],
        "Village": row["Village"],
        "Actual_Value": row[config.target_column],
        "Predicted_Value": predicted,
        "Explained_Output_Value": output_value,
    }
    if config.task == "classification":
        metadata["Class_Of_Interest"] = config.class_of_interest
    return metadata


def write_local_shap_outputs(
    config: TargetConfig,
    pipeline: Any,
    df: pd.DataFrame,
    raw_features: pd.DataFrame,
    transformed_x: pd.DataFrame,
    explanation: shap.Explanation,
    local_indices: list[int],
    numeric: list[str],
    categorical: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    shap_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    figure_paths: list[str] = []
    position_by_index = {index: position for position, index in enumerate(transformed_x.index.tolist())}

    for raw_index in local_indices:
        if raw_index not in position_by_index:
            continue
        position = position_by_index[raw_index]
        row = df.loc[raw_index]
        sample_metadata = prediction_metadata(config, pipeline, row, raw_features)
        sample_rows.append(sample_metadata)

        sample_id = str(row["Sample_ID"])
        shap_values = np.asarray(explanation.values[position], dtype=float)
        order = np.argsort(np.abs(shap_values))[::-1][:12]
        for rank, feature_index in enumerate(order, start=1):
            feature = transformed_x.columns[feature_index]
            shap_rows.append(
                {
                    **sample_metadata,
                    "Rank": rank,
                    "Feature": feature,
                    "Original_Feature": original_feature_name(feature, numeric, categorical),
                    "Feature_Value": float(transformed_x.iloc[position, feature_index]),
                    "SHAP_Value": float(shap_values[feature_index]),
                    "Abs_SHAP_Value": float(abs(shap_values[feature_index])),
                }
            )

        waterfall_path = LOCAL_DIR / f"shap_waterfall_{config.key}_{sample_id}.png"
        plt.figure(figsize=(8, 5))
        shap.plots.waterfall(explanation[position], max_display=12, show=False)
        plt.title(f"{config.target_column}: {sample_id}")
        plt.tight_layout()
        plt.savefig(waterfall_path, dpi=180, bbox_inches="tight")
        plt.close()
        figure_paths.append(str(waterfall_path.relative_to(PROJECT_ROOT)))

    return shap_rows, sample_rows, figure_paths


def write_lime_outputs(
    config: TargetConfig,
    output_function: Callable[[Any], np.ndarray],
    background: pd.DataFrame,
    transformed_x: pd.DataFrame,
    df: pd.DataFrame,
    raw_features: pd.DataFrame,
    local_indices: list[int],
) -> tuple[list[dict[str, Any]], list[str]]:
    explainer = LimeTabularExplainer(
        training_data=background.to_numpy(),
        feature_names=background.columns.tolist(),
        mode="regression",
        discretize_continuous=True,
        random_state=RANDOM_STATE,
    )
    lime_rows: list[dict[str, Any]] = []
    paths: list[str] = []

    for raw_index in local_indices:
        if raw_index not in transformed_x.index:
            continue
        row = df.loc[raw_index]
        sample_id = str(row["Sample_ID"])
        sample_metadata = prediction_metadata(config, joblib.load(config.model_path), row, raw_features)
        transformed_row = transformed_x.loc[raw_index].to_numpy()
        explanation = explainer.explain_instance(
            transformed_row,
            lambda values: output_function(values),
            num_features=12,
        )
        for rank, (feature_condition, contribution) in enumerate(explanation.as_list(), start=1):
            lime_rows.append(
                {
                    **sample_metadata,
                    "Rank": rank,
                    "Feature_Condition": feature_condition,
                    "LIME_Contribution": float(contribution),
                    "Abs_LIME_Contribution": float(abs(contribution)),
                }
            )

        figure = explanation.as_pyplot_figure()
        figure.suptitle(f"{config.target_column}: LIME {sample_id}")
        lime_png = LOCAL_DIR / f"lime_{config.key}_{sample_id}.png"
        figure.tight_layout()
        figure.savefig(lime_png, dpi=180, bbox_inches="tight")
        plt.close(figure)
        paths.append(str(lime_png.relative_to(PROJECT_ROOT)))

        lime_html = LOCAL_DIR / f"lime_{config.key}_{sample_id}.html"
        explanation.save_to_file(str(lime_html))
        paths.append(str(lime_html.relative_to(PROJECT_ROOT)))

    return lime_rows, paths


def feature_audit(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    selected = set(numeric + categorical)
    rows = []
    for feature in EXPECTED_EXPLANATION_FEATURES:
        rows.append(
            {
                "Feature": feature,
                "Present_In_Dataset": feature in df.columns,
                "Used_By_Champion_Feature_Set": feature in selected,
                "Notes": (
                    "Direct model input"
                    if feature in selected
                    else "Available as raw context but not directly used by champion feature set"
                    if feature in df.columns
                    else "Not available in current dataset"
                ),
            }
        )
    return pd.DataFrame(rows)


def build_recommendation_rules(
    df: pd.DataFrame,
    train_df: pd.DataFrame,
    global_importance: pd.DataFrame,
    numeric: list[str],
) -> pd.DataFrame:
    def q(feature: str, value: float) -> float:
        return float(train_df[feature].quantile(value))

    def support(feature: str, target: str) -> str:
        subset = global_importance[
            (global_importance["Target"] == target)
            & (global_importance["Original_Feature"] == feature)
            & (global_importance["Importance_Type"] == "SHAP_Mean_Abs_Aggregated")
        ]
        if subset.empty:
            return "Not in selected champion feature set; use as contextual agronomic check."
        row = subset.sort_values("Rank").iloc[0]
        return f"SHAP rank {int(row['Rank'])} for {target}; mean absolute contribution {row['Importance']:.5g}."

    rule_specs = [
        {
            "Rule_ID": "R1_low_soil_health",
            "Target": "Mango_Yield",
            "Feature": "Soil_Health_Index_Phase6",
            "Comparator": "<=",
            "Threshold": q("Soil_Health_Index_Phase6", 0.25),
            "Recommendation": "Improve organic carbon, reduce compaction, maintain biological amendments, and retest soil health before major input changes.",
        },
        {
            "Rule_ID": "R2_low_npk_balance",
            "Target": "Mango_Yield",
            "Feature": "NPK_Balance_Score_Phase6",
            "Comparator": "<=",
            "Threshold": q("NPK_Balance_Score_Phase6", 0.25),
            "Recommendation": "Balance nitrogen, phosphorus, and potassium using soil-test-guided fertilization rather than increasing only one nutrient.",
        },
        {
            "Rule_ID": "R3_high_pathogen_load",
            "Target": "Disease_Risk",
            "Feature": "Pathogen_Load_Index_Phase6",
            "Comparator": ">=",
            "Threshold": q("Pathogen_Load_Index_Phase6", 0.75),
            "Recommendation": "Inspect roots and canopy for disease symptoms, improve sanitation, and consider targeted biological or integrated disease management.",
        },
        {
            "Rule_ID": "R4_high_fusarium_context",
            "Target": "Disease_Risk",
            "Feature": "Fusarium",
            "Comparator": ">=",
            "Threshold": q("Fusarium", 0.75),
            "Recommendation": "Treat high Fusarium as a disease-context warning; verify with field symptoms and pathogen-specific assays before intervention.",
        },
        {
            "Rule_ID": "R5_low_beneficial_microbes",
            "Target": "Disease_Risk",
            "Feature": "Beneficial_Microbial_Index_Phase6",
            "Comparator": "<=",
            "Threshold": q("Beneficial_Microbial_Index_Phase6", 0.25),
            "Recommendation": "Support beneficial microbes through organic amendments, reduced unnecessary chemical stress, and verified bioinoculant strategies.",
        },
        {
            "Rule_ID": "R6_low_microbial_richness",
            "Target": "Mango_Yield",
            "Feature": "Microbial_Richness_Score",
            "Comparator": "<=",
            "Threshold": q("Microbial_Richness_Score", 0.25),
            "Recommendation": "Increase soil biological resilience with organic matter inputs, mulch, cover vegetation where suitable, and reduced disturbance.",
        },
        {
            "Rule_ID": "R7_high_nutrient_status",
            "Target": "Nutrient_Availability",
            "Feature": "NPK_Balance_Score_Phase6",
            "Comparator": ">=",
            "Threshold": q("NPK_Balance_Score_Phase6", 0.75),
            "Recommendation": "Maintain nutrient balance and avoid excessive fertilizer additions that may increase salinity or antagonistic nutrient effects.",
        },
    ]

    rows = []
    for spec in rule_specs:
        feature = spec["Feature"]
        rows.append(
            {
                **spec,
                "Threshold_Source": "train split quartile",
                "Feature_In_Dataset": feature in df.columns,
                "Feature_Used_By_Champion": feature in numeric,
                "XAI_Support": support(feature, spec["Target"]),
            }
        )
    return pd.DataFrame(rows)


def rule_triggered(value: float, comparator: str, threshold: float) -> bool:
    if comparator == "<=":
        return value <= threshold
    if comparator == ">=":
        return value >= threshold
    raise ValueError(f"Unsupported comparator: {comparator}")


def build_instance_recommendations(
    df: pd.DataFrame,
    local_sample_rows: pd.DataFrame,
    rules: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    if local_sample_rows.empty:
        return pd.DataFrame()

    sample_ids = local_sample_rows["Sample_ID"].drop_duplicates().tolist()
    indexed = df.set_index("Sample_ID")
    for sample_id in sample_ids:
        row = indexed.loc[sample_id]
        for _, rule in rules.iterrows():
            feature = rule["Feature"]
            if feature not in df.columns:
                continue
            value = float(row[feature])
            if rule_triggered(value, rule["Comparator"], float(rule["Threshold"])):
                rows.append(
                    {
                        "Sample_ID": sample_id,
                        "Split": row["Split"],
                        "Village": row["Village"],
                        "Rule_ID": rule["Rule_ID"],
                        "Target": rule["Target"],
                        "Feature": feature,
                        "Feature_Value": value,
                        "Comparator": rule["Comparator"],
                        "Threshold": float(rule["Threshold"]),
                        "Recommendation": rule["Recommendation"],
                    }
                )
    return pd.DataFrame(rows)


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "No rows."
    text_df = df.copy()
    for column in text_df.columns:
        if pd.api.types.is_numeric_dtype(text_df[column]):
            text_df[column] = text_df[column].map(lambda value: f"{value:.6g}" if pd.notna(value) else "")
        else:
            text_df[column] = text_df[column].fillna("").astype(str)
    headers = text_df.columns.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in text_df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(lines)


def write_report(
    global_importance: pd.DataFrame,
    transformed_importance: pd.DataFrame,
    dependence: pd.DataFrame,
    local_samples: pd.DataFrame,
    rules: pd.DataFrame,
    feature_audit_df: pd.DataFrame,
    generated_figures: list[str],
) -> None:
    lines = [
        "# Phase 8 Explainable AI Report",
        "",
        "Generated by `src/explainability/phase8_explainable_ai.py`.",
        "",
        "## Purpose",
        "",
        "Phase 8 explains the verified Phase 7 champion models using SHAP, LIME, dependence diagnostics, local waterfall plots, and agronomic recommendation rules.",
        "",
        "## Explained Champion Models",
        "",
        "| Target | Champion model | Explained output |",
        "|---|---|---|",
        "| `Mango_Yield` | `Linear_Regression` | predicted yield |",
        "| `Disease_Risk` | `Gradient_Boosting` | probability of `High` disease risk |",
        "| `Nutrient_Availability` | `Random_Forest` | probability of `High` nutrient availability |",
        "",
        "## Top SHAP Features",
        "",
    ]
    shap_global = global_importance[global_importance["Importance_Type"] == "SHAP_Mean_Abs_Aggregated"]
    for target in shap_global["Target"].drop_duplicates():
        lines.extend(
            [
                f"### {target}",
                "",
                dataframe_to_markdown(
                    shap_global[shap_global["Target"] == target][
                        ["Rank", "Original_Feature", "Importance", "Mean_SHAP", "Top_Transformed_Feature"]
                    ].head(10)
                ),
                "",
            ]
        )

    lines.extend(
        [
            "## Dependence and Threshold Diagnostics",
            "",
            dataframe_to_markdown(
                dependence[
                    [
                        "Target",
                        "Feature",
                        "Q25",
                        "Median",
                        "Q75",
                        "Spearman_Feature_SHAP",
                        "High_Minus_Low_SHAP",
                        "Figure",
                    ]
                ]
            ),
            "",
            "## Local Samples Explained",
            "",
            dataframe_to_markdown(
                local_samples[
                    [
                        "Target",
                        "Sample_ID",
                        "Split",
                        "Village",
                        "Actual_Value",
                        "Predicted_Value",
                        "Explained_Output_Value",
                    ]
                ]
            ),
            "",
            "## Expected Explanation Feature Audit",
            "",
            dataframe_to_markdown(feature_audit_df),
            "",
            "## Recommendation Rules",
            "",
            dataframe_to_markdown(
                rules[
                    [
                        "Rule_ID",
                        "Target",
                        "Feature",
                        "Comparator",
                        "Threshold",
                        "Recommendation",
                        "XAI_Support",
                    ]
                ]
            ),
            "",
            "## Generated Figures",
            "",
        ]
    )
    for figure in generated_figures:
        lines.append(f"- `{figure}`")

    lines.extend(
        [
            "",
            "## Output Tables",
            "",
            f"- Global feature importance: `{GLOBAL_IMPORTANCE_CSV.relative_to(PROJECT_ROOT)}`",
            f"- Transformed SHAP importance: `{TRANSFORMED_SHAP_CSV.relative_to(PROJECT_ROOT)}`",
            f"- Dependence thresholds: `{DEPENDENCE_CSV.relative_to(PROJECT_ROOT)}`",
            f"- Local SHAP explanations: `{LOCAL_SHAP_CSV.relative_to(PROJECT_ROOT)}`",
            f"- LIME explanations: `{LIME_CSV.relative_to(PROJECT_ROOT)}`",
            f"- Recommendation rules: `{RECOMMENDATION_RULES_CSV.relative_to(PROJECT_ROOT)}`",
            f"- Instance recommendations: `{INSTANCE_RECOMMENDATIONS_CSV.relative_to(PROJECT_ROOT)}`",
            "",
            "## Caveats",
            "",
            "- The current data are synthetic prototype data.",
            "- SHAP and LIME explanations are generated in the fitted transformed feature space and aggregated back to original feature names for agronomic readability.",
            "- `Fusarium` is available in the dataset but is not directly used by the current champion feature set; pathogen composite features carry that model signal.",
            "- Recommendations are decision-support rules, not field prescriptions; they should be validated with soil tests, pathogen assays, and orchard observations.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", message="An input array is constant*")
    ensure_dirs()

    numeric_features, categorical_features = read_selected_features()
    df = load_feature_table()
    train_df = df[df["Split"] == "train"].copy()
    raw_features = build_feature_matrix(df, numeric_features, categorical_features)

    global_parts: list[pd.DataFrame] = []
    transformed_parts: list[pd.DataFrame] = []
    dependence_rows: list[dict[str, Any]] = []
    local_shap_rows: list[dict[str, Any]] = []
    local_sample_rows: list[dict[str, Any]] = []
    lime_rows: list[dict[str, Any]] = []
    generated_figures: list[str] = []

    for config in TARGET_CONFIGS:
        pipeline = joblib.load(config.model_path)
        feature_names = transformed_feature_names(pipeline)
        output_function, _ = make_output_function(config, pipeline, feature_names)

        train_raw = build_feature_matrix(train_df, numeric_features, categorical_features)
        background_raw = train_raw.sample(n=min(BACKGROUND_SIZE, len(train_raw)), random_state=RANDOM_STATE)
        background = transform_features(pipeline, background_raw, feature_names)

        explain_indices, local_indices = select_explain_indices(config, df, raw_features, pipeline)
        explain_raw = raw_features.loc[explain_indices]
        explain_transformed = transform_features(pipeline, explain_raw, feature_names)

        explanation = compute_permutation_shap(output_function, background, explain_transformed)
        transformed_importance, shap_global = summarize_shap_importance(
            config,
            explanation,
            explain_transformed,
            explain_raw,
            numeric_features,
            categorical_features,
        )
        transformed_parts.append(transformed_importance)
        global_parts.append(shap_global)

        native_rows = native_importance_rows(
            config,
            pipeline.named_steps["model"],
            feature_names,
            numeric_features,
            categorical_features,
        )
        if native_rows:
            native_df = pd.DataFrame(native_rows)
            native_global = (
                native_df.groupby(["Target", "Output_Explained", "Importance_Type", "Original_Feature"], as_index=False)
                .agg(Importance=("Importance", "sum"), Top_Transformed_Feature=("Feature", "first"))
                .sort_values(["Target", "Importance"], ascending=[True, False])
            )
            native_global["Rank"] = native_global.groupby(["Target", "Importance_Type"])["Importance"].rank(
                ascending=False,
                method="first",
            ).astype(int)
            native_global["Mean_SHAP"] = np.nan
            global_parts.append(native_global)

        generated_figures.extend(plot_shap_summaries(config, explanation, explain_transformed))

        current_global = pd.concat(global_parts, ignore_index=True)
        generated_figures.append(plot_aggregated_importance(config, current_global))

        shap_values = np.asarray(explanation.values, dtype=float)
        for feature in DEPENDENCE_FEATURES[config.key]:
            figure, row = plot_dependence(config, feature, explain_raw, explain_transformed, shap_values)
            if figure:
                generated_figures.append(figure)
            if row:
                dependence_rows.append(row)

        shap_local, sample_local, waterfall_paths = write_local_shap_outputs(
            config,
            pipeline,
            df,
            raw_features,
            explain_transformed,
            explanation,
            local_indices,
            numeric_features,
            categorical_features,
        )
        local_shap_rows.extend(shap_local)
        local_sample_rows.extend(sample_local)
        generated_figures.extend(waterfall_paths)

        lime_local, lime_paths = write_lime_outputs(
            config,
            output_function,
            background,
            explain_transformed,
            df,
            raw_features,
            local_indices,
        )
        lime_rows.extend(lime_local)
        generated_figures.extend(lime_paths)

    transformed_importance_df = pd.concat(transformed_parts, ignore_index=True)
    global_importance_df = pd.concat(global_parts, ignore_index=True)
    dependence_df = pd.DataFrame(dependence_rows)
    local_shap_df = pd.DataFrame(local_shap_rows)
    local_samples_df = pd.DataFrame(local_sample_rows)
    lime_df = pd.DataFrame(lime_rows)
    feature_audit_df = feature_audit(df, numeric_features, categorical_features)

    rules_df = build_recommendation_rules(df, train_df, global_importance_df, numeric_features)
    instance_recommendations = build_instance_recommendations(df, local_samples_df, rules_df)

    global_importance_df.to_csv(GLOBAL_IMPORTANCE_CSV, index=False)
    transformed_importance_df.to_csv(TRANSFORMED_SHAP_CSV, index=False)
    dependence_df.to_csv(DEPENDENCE_CSV, index=False)
    local_shap_df.to_csv(LOCAL_SHAP_CSV, index=False)
    lime_df.to_csv(LIME_CSV, index=False)
    local_samples_df.to_csv(LOCAL_SAMPLE_CSV, index=False)
    rules_df.to_csv(RECOMMENDATION_RULES_CSV, index=False)
    instance_recommendations.to_csv(INSTANCE_RECOMMENDATIONS_CSV, index=False)
    feature_audit_df.to_csv(FEATURE_AUDIT_CSV, index=False)

    write_report(
        global_importance_df,
        transformed_importance_df,
        dependence_df,
        local_samples_df,
        rules_df,
        feature_audit_df,
        generated_figures,
    )

    summary = {
        "phase": "8",
        "status": "complete",
        "targets_explained": [config.target_column for config in TARGET_CONFIGS],
        "shap_background_rows": BACKGROUND_SIZE,
        "shap_explain_rows_per_target_requested": EXPLAIN_SIZE,
        "local_explanations_per_target": LOCAL_EXPLANATIONS_PER_TARGET,
        "global_importance_rows": int(len(global_importance_df)),
        "transformed_shap_rows": int(len(transformed_importance_df)),
        "dependence_rows": int(len(dependence_df)),
        "local_shap_rows": int(len(local_shap_df)),
        "lime_rows": int(len(lime_df)),
        "recommendation_rules": int(len(rules_df)),
        "instance_recommendations": int(len(instance_recommendations)),
        "figures_generated": int(len(generated_figures)),
        "report": str(REPORT_MD.relative_to(PROJECT_ROOT)),
        "tables": {
            "global_feature_importance": str(GLOBAL_IMPORTANCE_CSV.relative_to(PROJECT_ROOT)),
            "transformed_shap_importance": str(TRANSFORMED_SHAP_CSV.relative_to(PROJECT_ROOT)),
            "dependence_thresholds": str(DEPENDENCE_CSV.relative_to(PROJECT_ROOT)),
            "local_shap": str(LOCAL_SHAP_CSV.relative_to(PROJECT_ROOT)),
            "lime": str(LIME_CSV.relative_to(PROJECT_ROOT)),
            "recommendation_rules": str(RECOMMENDATION_RULES_CSV.relative_to(PROJECT_ROOT)),
            "instance_recommendations": str(INSTANCE_RECOMMENDATIONS_CSV.relative_to(PROJECT_ROOT)),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Phase 8 explainable AI complete.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

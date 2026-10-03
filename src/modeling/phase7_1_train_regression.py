"""Phase 7.1 regression modeling for Mango_Yield.

Trains and evaluates regression models using the Phase 6 selected feature set.
The script writes model artifacts, metrics, predictions, residual summaries,
village-wise errors, season-wise errors, and a champion-model report.
"""

from __future__ import annotations

import json
import math
import shutil
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVR


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_TABLE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"
SELECTED_FEATURES_JSON = PROJECT_ROOT / "data" / "processed" / "selected_features.json"

MODEL_DIR = PROJECT_ROOT / "outputs" / "models" / "regression"
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics" / "regression"
PREDICTIONS_DIR = PROJECT_ROOT / "outputs" / "predictions" / "regression"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "phase7_regression"

METRICS_CSV = METRICS_DIR / "regression_model_metrics.csv"
RESIDUAL_SUMMARY_CSV = METRICS_DIR / "regression_residual_summary.csv"
VILLAGE_ERROR_CSV = METRICS_DIR / "regression_village_wise_error.csv"
SEASON_ERROR_CSV = METRICS_DIR / "regression_season_wise_error.csv"
FEATURE_IMPORTANCE_CSV = METRICS_DIR / "regression_tree_feature_importance.csv"
PREDICTIONS_CSV = PREDICTIONS_DIR / "regression_predictions_all_models.csv"
CHAMPION_PREDICTIONS_CSV = PREDICTIONS_DIR / "regression_champion_predictions.csv"
SUMMARY_JSON = METRICS_DIR / "regression_model_summary.json"
REPORT_MD = REPORT_DIR / "regression_model_development_report.md"
CHAMPION_POINTER = MODEL_DIR / "champion_regression_model.json"

TARGET = "Mango_Yield"
SPLIT_ORDER = ["train", "validation", "test", "holdout_rahimabad"]
RANDOM_STATE = 42


@dataclass(frozen=True)
class ModelSpec:
    name: str
    estimator: Any
    description: str


def ensure_dirs() -> None:
    for path in [MODEL_DIR, METRICS_DIR, PREDICTIONS_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_selected_features() -> tuple[list[str], list[str]]:
    payload = json.loads(SELECTED_FEATURES_JSON.read_text(encoding="utf-8"))
    return payload["selected_numeric_features"], payload["categorical_features_for_encoding"]


def load_feature_table() -> pd.DataFrame:
    if not FEATURE_TABLE.exists():
        raise FileNotFoundError("Missing Phase 6 feature table. Run Phase 6 before Phase 7.1.")
    df = pd.read_csv(FEATURE_TABLE)
    if "Split" not in df.columns:
        raise ValueError("Feature table must contain the Phase 5 Split column.")
    return df


def make_preprocessor(numeric_features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric_features),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def get_model_specs() -> list[ModelSpec]:
    specs = [
        ModelSpec(
            "Mean_Baseline",
            DummyRegressor(strategy="mean"),
            "Mean-value dummy baseline.",
        ),
        ModelSpec(
            "Linear_Regression",
            LinearRegression(),
            "Ordinary least-squares linear regression baseline.",
        ),
        ModelSpec(
            "Elastic_Net",
            ElasticNet(alpha=0.001, l1_ratio=0.25, max_iter=20000, random_state=RANDOM_STATE),
            "Regularized linear model with L1/L2 penalty.",
        ),
        ModelSpec(
            "Linear_SVR",
            LinearSVR(C=1.0, epsilon=0.05, max_iter=20000, random_state=RANDOM_STATE),
            "Scalable linear support vector regression.",
        ),
        ModelSpec(
            "Random_Forest",
            RandomForestRegressor(
                n_estimators=250,
                max_depth=None,
                min_samples_leaf=2,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "Random Forest regressor for nonlinear tabular interactions.",
        ),
        ModelSpec(
            "Gradient_Boosting",
            GradientBoostingRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=3,
                random_state=RANDOM_STATE,
            ),
            "Gradient Boosting regressor for nonlinear threshold effects.",
        ),
        ModelSpec(
            "MLP_Regressor",
            MLPRegressor(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                solver="adam",
                alpha=0.0005,
                learning_rate_init=0.001,
                max_iter=300,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=20,
                random_state=RANDOM_STATE,
            ),
            "Neural network baseline for structured tabular data.",
        ),
    ]

    try:
        from xgboost import XGBRegressor
    except ImportError:
        pass
    else:
        specs.append(
            ModelSpec(
                "XGBoost",
                XGBRegressor(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=3,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    objective="reg:squarederror",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
                "Optional XGBoost regressor, included when xgboost is installed.",
            )
        )

    try:
        from lightgbm import LGBMRegressor
    except ImportError:
        pass
    else:
        specs.append(
            ModelSpec(
                "LightGBM",
                LGBMRegressor(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=-1,
                    num_leaves=31,
                    objective="regression",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                    verbose=-1,
                ),
                "Optional LightGBM regressor, included when lightgbm is installed.",
            )
        )

    return specs


def safe_model_name(name: str) -> str:
    return name.lower().replace(" ", "_")


def rmse(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> float:
    return math.sqrt(mean_squared_error(y_true, y_pred))


def metrics_for(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "RMSE": rmse(y_true, y_pred),
        "MAE": mean_absolute_error(y_true, y_pred),
        "R2": r2_score(y_true, y_pred) if len(y_true) > 1 else float("nan"),
        "Mean_Residual": float(np.mean(y_true.to_numpy() - y_pred)),
        "Median_Abs_Error": float(np.median(np.abs(y_true.to_numpy() - y_pred))),
    }


def build_feature_matrix(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    missing = [col for col in numeric + categorical if col not in df.columns]
    if missing:
        raise ValueError(f"Missing selected feature columns: {missing}")
    return df[numeric + categorical].copy()


def make_predictions_frame(model_name: str, split_name: str, split_df: pd.DataFrame, y_pred: np.ndarray) -> pd.DataFrame:
    y_true = split_df[TARGET].to_numpy()
    residual = y_true - y_pred
    columns = [
        "Sample_ID",
        "Orchard_ID",
        "Village",
        "Sampling_Season",
        "Soil_Depth",
        "Mango_Variety",
        "Management",
    ]
    out = split_df[columns].copy()
    out.insert(0, "Model", model_name)
    out.insert(1, "Split", split_name)
    out["Actual_Mango_Yield"] = y_true
    out["Predicted_Mango_Yield"] = y_pred
    out["Residual"] = residual
    out["Abs_Error"] = np.abs(residual)
    out["Squared_Error"] = residual**2
    return out


def evaluate_predictions(predictions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    residual_rows = []
    village_rows = []
    season_rows = []

    for (model, split), group in predictions.groupby(["Model", "Split"], sort=False):
        y_true = group["Actual_Mango_Yield"]
        y_pred = group["Predicted_Mango_Yield"].to_numpy()
        row = {"Model": model, "Split": split, "Rows": int(len(group))}
        row.update(metrics_for(y_true, y_pred))
        metric_rows.append(row)

        residual_rows.append(
            {
                "Model": model,
                "Split": split,
                "Rows": int(len(group)),
                "Residual_Mean": float(group["Residual"].mean()),
                "Residual_Std": float(group["Residual"].std()),
                "Residual_Q05": float(group["Residual"].quantile(0.05)),
                "Residual_Q50": float(group["Residual"].quantile(0.50)),
                "Residual_Q95": float(group["Residual"].quantile(0.95)),
                "Abs_Error_Q50": float(group["Abs_Error"].quantile(0.50)),
                "Abs_Error_Q95": float(group["Abs_Error"].quantile(0.95)),
            }
        )

    for (model, split, village), group in predictions.groupby(["Model", "Split", "Village"], sort=False):
        y_true = group["Actual_Mango_Yield"]
        y_pred = group["Predicted_Mango_Yield"].to_numpy()
        row = {"Model": model, "Split": split, "Village": village, "Rows": int(len(group))}
        row.update(metrics_for(y_true, y_pred))
        village_rows.append(row)

    for (model, split, season), group in predictions.groupby(["Model", "Split", "Sampling_Season"], sort=False):
        y_true = group["Actual_Mango_Yield"]
        y_pred = group["Predicted_Mango_Yield"].to_numpy()
        row = {"Model": model, "Split": split, "Sampling_Season": season, "Rows": int(len(group))}
        row.update(metrics_for(y_true, y_pred))
        season_rows.append(row)

    return (
        pd.DataFrame(metric_rows),
        pd.DataFrame(residual_rows),
        pd.DataFrame(village_rows),
        pd.DataFrame(season_rows),
    )


def hybrid_rule_adjustment(df: pd.DataFrame) -> np.ndarray:
    adjustment = np.zeros(len(df), dtype=float)

    adjustment += 0.004 * (df["Soil_Health_Index_Phase6"].to_numpy() - 50.0)
    adjustment += 0.003 * (df["NPK_Balance_Score_Phase6"].to_numpy() - 50.0)
    adjustment += 0.002 * (df["Beneficial_Microbial_Index_Phase6"].to_numpy() - 50.0)
    adjustment -= 0.0035 * (df["Pathogen_Load_Index_Phase6"].to_numpy() - 50.0)

    return np.clip(adjustment, -0.75, 0.75)


def train_hybrid_model(
    train_df: pd.DataFrame,
    split_dfs: dict[str, pd.DataFrame],
    numeric_features: list[str],
    categorical_features: list[str],
) -> tuple[Pipeline, list[pd.DataFrame]]:
    base = Pipeline(
        steps=[
            ("preprocess", make_preprocessor(numeric_features, categorical_features)),
            (
                "model",
                GradientBoostingRegressor(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    base.fit(build_feature_matrix(train_df, numeric_features, categorical_features), train_df[TARGET])

    prediction_frames = []
    for split_name in SPLIT_ORDER:
        split_df = split_dfs[split_name]
        x = build_feature_matrix(split_df, numeric_features, categorical_features)
        base_pred = base.predict(x)
        y_pred = base_pred + hybrid_rule_adjustment(split_df)
        prediction_frames.append(make_predictions_frame("Hybrid_Rule_Guided_GB", split_name, split_df, y_pred))

    return base, prediction_frames


def extract_tree_feature_importance(model_name: str, pipeline: Pipeline) -> pd.DataFrame:
    estimator = pipeline.named_steps["model"]
    if not hasattr(estimator, "feature_importances_"):
        return pd.DataFrame()
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    return pd.DataFrame(
        {
            "Model": model_name,
            "Feature": names,
            "Importance": estimator.feature_importances_,
        }
    ).sort_values(["Model", "Importance"], ascending=[True, False])


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "No rows."

    text_df = df.copy()
    for column in text_df.columns:
        if pd.api.types.is_numeric_dtype(text_df[column]):
            text_df[column] = text_df[column].map(lambda value: f"{value:.5g}" if pd.notna(value) else "")
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


def write_report(
    metrics: pd.DataFrame,
    champion_model: str,
    selected_features: list[str],
    categorical_features: list[str],
    model_descriptions: dict[str, str],
) -> None:
    validation = metrics[metrics["Split"] == "validation"].sort_values("RMSE")
    test = metrics[metrics["Split"] == "test"].sort_values("RMSE")
    holdout = metrics[metrics["Split"] == "holdout_rahimabad"].sort_values("RMSE")

    lines = [
        "# Phase 7.1 Mango Yield Regression Report",
        "",
        "Generated by `src/modeling/phase7_1_train_regression.py`.",
        "",
        "## Target",
        "",
        "- `Mango_Yield` in kg/tree.",
        "",
        "## Feature Set",
        "",
        f"- Selected numeric features: {len(selected_features)}",
        f"- Categorical features encoded: {', '.join(categorical_features)}",
        "- Preprocessing is fit on the train split only inside each model pipeline.",
        "",
        "## Models Trained",
        "",
    ]
    for model, description in model_descriptions.items():
        lines.append(f"- `{model}`: {description}")

    lines.extend(
        [
            "",
            "## Champion Selection",
            "",
            f"Champion model selected by lowest validation RMSE: `{champion_model}`.",
            "",
            "## Validation Metrics",
            "",
            dataframe_to_markdown(validation[["Model", "Rows", "RMSE", "MAE", "R2", "Mean_Residual"]]),
            "",
            "## Test Metrics",
            "",
            dataframe_to_markdown(test[["Model", "Rows", "RMSE", "MAE", "R2", "Mean_Residual"]]),
            "",
            "## Rahimabad Geographic Hold-Out Metrics",
            "",
            dataframe_to_markdown(holdout[["Model", "Rows", "RMSE", "MAE", "R2", "Mean_Residual"]]),
            "",
            "## Outputs",
            "",
            "- Model metrics: `outputs/metrics/regression/regression_model_metrics.csv`",
            "- Residual summary: `outputs/metrics/regression/regression_residual_summary.csv`",
            "- Village-wise error: `outputs/metrics/regression/regression_village_wise_error.csv`",
            "- Season-wise error: `outputs/metrics/regression/regression_season_wise_error.csv`",
            "- Predictions: `outputs/predictions/regression/regression_predictions_all_models.csv`",
            "- Champion predictions: `outputs/predictions/regression/regression_champion_predictions.csv`",
            "- Saved models: `outputs/models/regression/`",
            "",
            "## Caveats",
            "",
            "- The current data are synthetic prototype data.",
            "- The hybrid model uses transparent agronomic rule adjustments on top of Gradient Boosting predictions.",
            "- Phase 8 XAI should explain the champion model and verify whether important features are agronomically meaningful.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    ensure_dirs()

    numeric_features, categorical_features = read_selected_features()
    df = load_feature_table()
    split_dfs = {split: df[df["Split"] == split].copy() for split in SPLIT_ORDER}
    if any(frame.empty for frame in split_dfs.values()):
        empty = [name for name, frame in split_dfs.items() if frame.empty]
        raise ValueError(f"Missing split rows for: {empty}")

    train_df = split_dfs["train"]
    model_specs = get_model_specs()
    model_descriptions = {spec.name: spec.description for spec in model_specs}
    model_descriptions["Hybrid_Rule_Guided_GB"] = "Gradient Boosting plus transparent agronomic rule adjustment."

    all_predictions = []
    feature_importance_parts = []

    for spec in model_specs:
        model_name = spec.name
        pipeline = Pipeline(
            steps=[
                ("preprocess", make_preprocessor(numeric_features, categorical_features)),
                ("model", clone(spec.estimator)),
            ]
        )
        pipeline.fit(build_feature_matrix(train_df, numeric_features, categorical_features), train_df[TARGET])

        model_path = MODEL_DIR / f"{safe_model_name(model_name)}.joblib"
        joblib.dump(pipeline, model_path)

        importance = extract_tree_feature_importance(model_name, pipeline)
        if not importance.empty:
            feature_importance_parts.append(importance)

        for split_name in SPLIT_ORDER:
            split_df = split_dfs[split_name]
            x = build_feature_matrix(split_df, numeric_features, categorical_features)
            y_pred = pipeline.predict(x)
            all_predictions.append(make_predictions_frame(model_name, split_name, split_df, y_pred))

    hybrid_base, hybrid_predictions = train_hybrid_model(train_df, split_dfs, numeric_features, categorical_features)
    joblib.dump(hybrid_base, MODEL_DIR / "hybrid_rule_guided_gb_base_pipeline.joblib")
    (MODEL_DIR / "hybrid_rule_guided_gb_rule_config.json").write_text(
        json.dumps(
            {
                "base_model": "GradientBoostingRegressor",
                "adjustment_formula": "clip(0.004*(Soil_Health_Index_Phase6-50) + 0.003*(NPK_Balance_Score_Phase6-50) + 0.002*(Beneficial_Microbial_Index_Phase6-50) - 0.0035*(Pathogen_Load_Index_Phase6-50), -0.75, 0.75)",
                "units": "kg_per_tree adjustment",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    all_predictions.extend(hybrid_predictions)

    predictions = pd.concat(all_predictions, ignore_index=True)
    metrics, residual_summary, village_error, season_error = evaluate_predictions(predictions)

    metrics.to_csv(METRICS_CSV, index=False)
    residual_summary.to_csv(RESIDUAL_SUMMARY_CSV, index=False)
    village_error.to_csv(VILLAGE_ERROR_CSV, index=False)
    season_error.to_csv(SEASON_ERROR_CSV, index=False)
    predictions.to_csv(PREDICTIONS_CSV, index=False)

    if feature_importance_parts:
        pd.concat(feature_importance_parts, ignore_index=True).to_csv(FEATURE_IMPORTANCE_CSV, index=False)
    else:
        pd.DataFrame(columns=["Model", "Feature", "Importance"]).to_csv(FEATURE_IMPORTANCE_CSV, index=False)

    champion_row = metrics[metrics["Split"] == "validation"].sort_values("RMSE").iloc[0]
    champion_model = str(champion_row["Model"])
    champion_predictions = predictions[predictions["Model"] == champion_model].copy()
    champion_predictions.to_csv(CHAMPION_PREDICTIONS_CSV, index=False)

    champion_file = MODEL_DIR / f"{safe_model_name(champion_model)}.joblib"
    champion_artifact: dict[str, Any] = {
        "champion_model": champion_model,
        "selection_metric": "validation_RMSE",
        "validation_RMSE": float(champion_row["RMSE"]),
        "selected_numeric_features": numeric_features,
        "categorical_features": categorical_features,
    }
    if champion_file.exists():
        shutil.copyfile(champion_file, MODEL_DIR / "champion_regression_model.joblib")
        champion_artifact["model_artifact"] = "outputs/models/regression/champion_regression_model.joblib"
    elif champion_model == "Hybrid_Rule_Guided_GB":
        champion_artifact["base_model_artifact"] = "outputs/models/regression/hybrid_rule_guided_gb_base_pipeline.joblib"
        champion_artifact["rule_config"] = "outputs/models/regression/hybrid_rule_guided_gb_rule_config.json"
    CHAMPION_POINTER.write_text(json.dumps(champion_artifact, indent=2), encoding="utf-8")

    summary = {
        "target": TARGET,
        "rows": int(len(df)),
        "models": sorted(predictions["Model"].unique().tolist()),
        "champion_model": champion_model,
        "champion_validation_RMSE": float(champion_row["RMSE"]),
        "metrics_file": str(METRICS_CSV.relative_to(PROJECT_ROOT)),
        "predictions_file": str(PREDICTIONS_CSV.relative_to(PROJECT_ROOT)),
        "champion_pointer": str(CHAMPION_POINTER.relative_to(PROJECT_ROOT)),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(metrics, champion_model, numeric_features, categorical_features, model_descriptions)

    print("Phase 7.1 regression modeling complete.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

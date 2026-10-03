"""Phase 10 validation workflow.

Implements internal cross-validation, Rahimabad geographic hold-out validation,
real-sample validation scaffolding, and field-intervention validation
scaffolding for the current research prototype.
"""

from __future__ import annotations

import json
import math
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import ElasticNet, LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC, LinearSVR


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_TABLE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"
SELECTED_FEATURES_JSON = PROJECT_ROOT / "data" / "processed" / "selected_features.json"

PHASE7_REGRESSION_METRICS = PROJECT_ROOT / "outputs" / "metrics" / "regression" / "regression_model_metrics.csv"
PHASE7_CLASSIFICATION_METRICS = PROJECT_ROOT / "outputs" / "metrics" / "classification" / "classification_model_metrics.csv"

REGRESSION_CHAMPION_MODEL = PROJECT_ROOT / "outputs" / "models" / "regression" / "champion_regression_model.joblib"
DISEASE_CHAMPION_MODEL = PROJECT_ROOT / "outputs" / "models" / "classification" / "champion_disease_risk_model.joblib"
NUTRIENT_CHAMPION_MODEL = PROJECT_ROOT / "outputs" / "models" / "classification" / "champion_nutrient_availability_model.joblib"

VALIDATION_DATA_DIR = PROJECT_ROOT / "data" / "validation"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "validation" / "phase10"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "phase10_validation"

INTERNAL_CV_REGRESSION_CSV = OUTPUT_DIR / "phase10_internal_cv_regression_metrics.csv"
INTERNAL_CV_CLASSIFICATION_CSV = OUTPUT_DIR / "phase10_internal_cv_classification_metrics.csv"
INTERNAL_CV_SUMMARY_CSV = OUTPUT_DIR / "phase10_internal_cv_summary.csv"
TRAIN_TEST_COMPARISON_CSV = OUTPUT_DIR / "phase10_train_test_split_comparison.csv"
GEO_REGRESSION_CSV = OUTPUT_DIR / "phase10_geographic_holdout_regression_metrics.csv"
GEO_CLASSIFICATION_CSV = OUTPUT_DIR / "phase10_geographic_holdout_classification_metrics.csv"
INTERNAL_VS_GEO_CSV = OUTPUT_DIR / "phase10_internal_vs_geographic_summary.csv"
REAL_SAMPLE_STATUS_CSV = OUTPUT_DIR / "phase10_real_sample_validation_status.csv"
REAL_SAMPLE_PREDICTIONS_CSV = OUTPUT_DIR / "phase10_real_sample_predictions.csv"
FIELD_STATUS_CSV = OUTPUT_DIR / "phase10_field_intervention_status.csv"
FIELD_SUMMARY_CSV = OUTPUT_DIR / "phase10_field_intervention_summary.csv"
VALIDATION_MANIFEST_CSV = OUTPUT_DIR / "phase10_validation_manifest.csv"
SUMMARY_JSON = OUTPUT_DIR / "phase10_validation_summary.json"
REPORT_MD = REPORT_DIR / "phase10_validation_report.md"

REAL_SAMPLE_TEMPLATE = VALIDATION_DATA_DIR / "real_sample_validation_template.csv"
REAL_SAMPLE_INPUT = VALIDATION_DATA_DIR / "real_sample_validation_input.csv"
FIELD_TEMPLATE = VALIDATION_DATA_DIR / "field_intervention_validation_template.csv"
FIELD_INPUT = VALIDATION_DATA_DIR / "field_intervention_validation_input.csv"

TARGET_REGRESSION = "Mango_Yield"
TARGETS_CLASSIFICATION = ["Disease_Risk", "Nutrient_Availability"]
PREFERRED_CLASS_ORDER = {
    "Disease_Risk": ["Low", "Medium", "High"],
    "Nutrient_Availability": ["Deficient", "Optimal", "High"],
}
RANDOM_STATE = 42
N_SPLITS = 5


@dataclass(frozen=True)
class ModelSpec:
    name: str
    estimator: Any
    family: str


def log(message: str) -> None:
    print(f"[Phase 10] {message}", flush=True)


def ensure_dirs() -> None:
    for path in [VALIDATION_DATA_DIR, OUTPUT_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_selected_features() -> tuple[list[str], list[str]]:
    payload = json.loads(SELECTED_FEATURES_JSON.read_text(encoding="utf-8"))
    return payload["selected_numeric_features"], payload["categorical_features_for_encoding"]


def load_feature_table() -> pd.DataFrame:
    if not FEATURE_TABLE.exists():
        raise FileNotFoundError("Missing feature table. Run Phase 6 before Phase 10.")
    df = pd.read_csv(FEATURE_TABLE)
    required = ["Split", "Village", TARGET_REGRESSION, *TARGETS_CLASSIFICATION]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Feature table missing required columns: {missing}")
    return df


def make_preprocessor(numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_feature_matrix(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    missing = [col for col in numeric + categorical if col not in df.columns]
    if missing:
        raise ValueError(f"Missing selected feature columns: {missing}")
    return df[numeric + categorical].copy()


def regression_specs() -> list[ModelSpec]:
    return [
        ModelSpec("Mean_Baseline", DummyRegressor(strategy="mean"), "baseline"),
        ModelSpec("Linear_Regression", LinearRegression(), "linear"),
        ModelSpec("Elastic_Net", ElasticNet(alpha=0.001, l1_ratio=0.25, max_iter=10000, random_state=RANDOM_STATE), "linear"),
        ModelSpec("Linear_SVR", LinearSVR(C=1.0, epsilon=0.05, max_iter=10000, random_state=RANDOM_STATE), "svm"),
        ModelSpec(
            "Random_Forest",
            RandomForestRegressor(n_estimators=60, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1),
            "tree_ensemble",
        ),
        ModelSpec(
            "Gradient_Boosting",
            GradientBoostingRegressor(n_estimators=80, learning_rate=0.06, max_depth=3, random_state=RANDOM_STATE),
            "boosting",
        ),
    ]


def classification_specs() -> list[ModelSpec]:
    return [
        ModelSpec("Majority_Baseline", DummyClassifier(strategy="most_frequent"), "baseline"),
        ModelSpec(
            "Logistic_Regression",
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
            "linear",
        ),
        ModelSpec(
            "Linear_SVM",
            CalibratedClassifierCV(
                estimator=LinearSVC(C=1.0, class_weight="balanced", dual=False, max_iter=10000, random_state=RANDOM_STATE),
                method="sigmoid",
                cv=3,
            ),
            "svm",
        ),
        ModelSpec(
            "Random_Forest",
            RandomForestClassifier(
                n_estimators=60,
                min_samples_leaf=2,
                class_weight="balanced_subsample",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "tree_ensemble",
        ),
        ModelSpec(
            "Gradient_Boosting",
            GradientBoostingClassifier(n_estimators=80, learning_rate=0.06, max_depth=3, random_state=RANDOM_STATE),
            "boosting",
        ),
    ]


def observed_class_order(target: str, df: pd.DataFrame) -> list[str]:
    observed = set(df[target].dropna().astype(str).unique().tolist())
    preferred = [label for label in PREFERRED_CLASS_ORDER[target] if label in observed]
    remaining = sorted(label for label in observed if label not in preferred)
    return preferred + remaining


def regression_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "RMSE": math.sqrt(mean_squared_error(y_true, y_pred)),
        "MAE": mean_absolute_error(y_true, y_pred),
        "R2": r2_score(y_true, y_pred) if len(y_true) > 1 else np.nan,
    }


def predict_proba_aligned(model: Pipeline, x: pd.DataFrame, classes: list[str]) -> np.ndarray:
    raw = model.predict_proba(x)
    model_classes = [str(value) for value in model.named_steps["model"].classes_]
    aligned = np.zeros((len(x), len(classes)), dtype=float)
    for out_index, label in enumerate(classes):
        if label in model_classes:
            aligned[:, out_index] = raw[:, model_classes.index(label)]
    row_sums = aligned.sum(axis=1)
    missing = row_sums == 0
    if missing.any():
        aligned[missing, :] = 1.0 / len(classes)
        row_sums = aligned.sum(axis=1)
    return aligned / row_sums[:, None]


def roc_auc_for(y_true: pd.Series, proba: np.ndarray, classes: list[str]) -> float:
    scores = []
    y_text = y_true.astype(str)
    for index, label in enumerate(classes):
        y_binary = (y_text == label).astype(int)
        if y_binary.nunique() < 2:
            continue
        try:
            scores.append(roc_auc_score(y_binary, proba[:, index]))
        except ValueError:
            continue
    return float(np.mean(scores)) if scores else np.nan


def classification_metrics(y_true: pd.Series, y_pred: np.ndarray, proba: np.ndarray, classes: list[str]) -> dict[str, float]:
    return {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Balanced_Accuracy": balanced_accuracy_score(y_true, y_pred),
        "Precision_Macro": precision_score(y_true, y_pred, labels=classes, average="macro", zero_division=0),
        "Recall_Macro": recall_score(y_true, y_pred, labels=classes, average="macro", zero_division=0),
        "Macro_F1": f1_score(y_true, y_pred, labels=classes, average="macro", zero_division=0),
        "ROC_AUC": roc_auc_for(y_true, proba, classes),
    }


def run_internal_cv_regression(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    rows = []
    x_all = build_feature_matrix(df, numeric, categorical)
    y_all = df[TARGET_REGRESSION]
    kfold = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    for spec in regression_specs():
        log(f"Internal regression CV: {spec.name}")
        for fold, (train_idx, valid_idx) in enumerate(kfold.split(x_all), start=1):
            log(f"Internal regression CV: {spec.name} fold {fold}/{N_SPLITS}")
            pipeline = Pipeline([("preprocess", make_preprocessor(numeric, categorical)), ("model", clone(spec.estimator))])
            pipeline.fit(x_all.iloc[train_idx], y_all.iloc[train_idx])
            pred = pipeline.predict(x_all.iloc[valid_idx])
            row = {
                "Target": TARGET_REGRESSION,
                "Model": spec.name,
                "Model_Family": spec.family,
                "Fold": fold,
                "Rows": int(len(valid_idx)),
            }
            row.update(regression_metrics(y_all.iloc[valid_idx], pred))
            rows.append(row)
    return pd.DataFrame(rows)


def run_internal_cv_classification(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    rows = []
    for target in TARGETS_CLASSIFICATION:
        classes = observed_class_order(target, df)
        x_all = build_feature_matrix(df, numeric, categorical)
        y_all = df[target].astype(str)
        kfold = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
        for spec in classification_specs():
            log(f"Internal classification CV: {target} {spec.name}")
            for fold, (train_idx, valid_idx) in enumerate(kfold.split(x_all, y_all), start=1):
                log(f"Internal classification CV: {target} {spec.name} fold {fold}/{N_SPLITS}")
                pipeline = Pipeline([("preprocess", make_preprocessor(numeric, categorical)), ("model", clone(spec.estimator))])
                pipeline.fit(x_all.iloc[train_idx], y_all.iloc[train_idx])
                pred = pipeline.predict(x_all.iloc[valid_idx]).astype(str)
                proba = predict_proba_aligned(pipeline, x_all.iloc[valid_idx], classes)
                row = {
                    "Target": target,
                    "Model": spec.name,
                    "Model_Family": spec.family,
                    "Fold": fold,
                    "Rows": int(len(valid_idx)),
                }
                row.update(classification_metrics(y_all.iloc[valid_idx], pred, proba, classes))
                rows.append(row)
    return pd.DataFrame(rows)


def summarize_internal_cv(regression_cv: pd.DataFrame, classification_cv: pd.DataFrame) -> pd.DataFrame:
    reg = (
        regression_cv.groupby(["Target", "Model", "Model_Family"], as_index=False)
        .agg(
            Folds=("Fold", "count"),
            Mean_RMSE=("RMSE", "mean"),
            Std_RMSE=("RMSE", "std"),
            Mean_MAE=("MAE", "mean"),
            Mean_R2=("R2", "mean"),
        )
        .sort_values(["Target", "Mean_RMSE"])
    )
    reg["Task"] = "Regression"
    reg["Primary_Metric"] = "RMSE"
    reg["Primary_Mean"] = reg["Mean_RMSE"]
    reg["Primary_Std"] = reg["Std_RMSE"]

    clf = (
        classification_cv.groupby(["Target", "Model", "Model_Family"], as_index=False)
        .agg(
            Folds=("Fold", "count"),
            Mean_Accuracy=("Accuracy", "mean"),
            Std_Accuracy=("Accuracy", "std"),
            Mean_Macro_F1=("Macro_F1", "mean"),
            Std_Macro_F1=("Macro_F1", "std"),
            Mean_ROC_AUC=("ROC_AUC", "mean"),
        )
        .sort_values(["Target", "Mean_Macro_F1"], ascending=[True, False])
    )
    clf["Task"] = "Classification"
    clf["Primary_Metric"] = "Macro_F1"
    clf["Primary_Mean"] = clf["Mean_Macro_F1"]
    clf["Primary_Std"] = clf["Std_Macro_F1"]

    return pd.concat([reg, clf], ignore_index=True, sort=False)


def build_train_test_comparison() -> pd.DataFrame:
    rows = []
    if PHASE7_REGRESSION_METRICS.exists():
        reg = pd.read_csv(PHASE7_REGRESSION_METRICS)
        for _, row in reg.iterrows():
            rows.append(
                {
                    "Task": "Regression",
                    "Target": TARGET_REGRESSION,
                    "Model": row["Model"],
                    "Split": row["Split"],
                    "Rows": row["Rows"],
                    "Primary_Metric": "RMSE",
                    "Primary_Value": row["RMSE"],
                    "Secondary_Metric": "MAE",
                    "Secondary_Value": row["MAE"],
                    "Additional_Metric": "R2",
                    "Additional_Value": row["R2"],
                }
            )
    if PHASE7_CLASSIFICATION_METRICS.exists():
        clf = pd.read_csv(PHASE7_CLASSIFICATION_METRICS)
        for _, row in clf.iterrows():
            rows.append(
                {
                    "Task": "Classification",
                    "Target": row["Target"],
                    "Model": row["Model"],
                    "Split": row["Split"],
                    "Rows": row["Rows"],
                    "Primary_Metric": "Macro_F1",
                    "Primary_Value": row["Macro_F1"],
                    "Secondary_Metric": "Accuracy",
                    "Secondary_Value": row["Accuracy"],
                    "Additional_Metric": "ROC_AUC",
                    "Additional_Value": row["ROC_AUC"],
                }
            )
    return pd.DataFrame(rows)


def run_geographic_holdout_regression(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    train = df[df["Village"] != "Rahimabad"].copy()
    holdout = df[df["Village"] == "Rahimabad"].copy()
    rows = []
    for spec in regression_specs():
        log(f"Rahimabad regression hold-out: {spec.name}")
        pipeline = Pipeline([("preprocess", make_preprocessor(numeric, categorical)), ("model", clone(spec.estimator))])
        pipeline.fit(build_feature_matrix(train, numeric, categorical), train[TARGET_REGRESSION])
        pred = pipeline.predict(build_feature_matrix(holdout, numeric, categorical))
        row = {
            "Target": TARGET_REGRESSION,
            "Model": spec.name,
            "Model_Family": spec.family,
            "Train_Rows": int(len(train)),
            "Holdout_Village": "Rahimabad",
            "Holdout_Rows": int(len(holdout)),
        }
        row.update(regression_metrics(holdout[TARGET_REGRESSION], pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("RMSE")


def run_geographic_holdout_classification(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    train = df[df["Village"] != "Rahimabad"].copy()
    holdout = df[df["Village"] == "Rahimabad"].copy()
    rows = []
    for target in TARGETS_CLASSIFICATION:
        classes = observed_class_order(target, df)
        for spec in classification_specs():
            log(f"Rahimabad classification hold-out: {target} {spec.name}")
            pipeline = Pipeline([("preprocess", make_preprocessor(numeric, categorical)), ("model", clone(spec.estimator))])
            pipeline.fit(build_feature_matrix(train, numeric, categorical), train[target].astype(str))
            x_holdout = build_feature_matrix(holdout, numeric, categorical)
            pred = pipeline.predict(x_holdout).astype(str)
            proba = predict_proba_aligned(pipeline, x_holdout, classes)
            row = {
                "Target": target,
                "Model": spec.name,
                "Model_Family": spec.family,
                "Train_Rows": int(len(train)),
                "Holdout_Village": "Rahimabad",
                "Holdout_Rows": int(len(holdout)),
            }
            row.update(classification_metrics(holdout[target].astype(str), pred, proba, classes))
            rows.append(row)
    return pd.DataFrame(rows).sort_values(["Target", "Macro_F1"], ascending=[True, False])


def build_internal_vs_geo_summary(internal_summary: pd.DataFrame, geo_reg: pd.DataFrame, geo_clf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, geo in geo_reg.iterrows():
        internal = internal_summary[
            (internal_summary["Task"] == "Regression")
            & (internal_summary["Target"] == TARGET_REGRESSION)
            & (internal_summary["Model"] == geo["Model"])
        ]
        if internal.empty:
            continue
        internal_row = internal.iloc[0]
        rows.append(
            {
                "Task": "Regression",
                "Target": TARGET_REGRESSION,
                "Model": geo["Model"],
                "Primary_Metric": "RMSE",
                "Internal_CV_Mean": internal_row["Primary_Mean"],
                "Geographic_Holdout": geo["RMSE"],
                "Holdout_Minus_Internal": float(geo["RMSE"]) - float(internal_row["Primary_Mean"]),
            }
        )
    for _, geo in geo_clf.iterrows():
        internal = internal_summary[
            (internal_summary["Task"] == "Classification")
            & (internal_summary["Target"] == geo["Target"])
            & (internal_summary["Model"] == geo["Model"])
        ]
        if internal.empty:
            continue
        internal_row = internal.iloc[0]
        rows.append(
            {
                "Task": "Classification",
                "Target": geo["Target"],
                "Model": geo["Model"],
                "Primary_Metric": "Macro_F1",
                "Internal_CV_Mean": internal_row["Primary_Mean"],
                "Geographic_Holdout": geo["Macro_F1"],
                "Holdout_Minus_Internal": float(geo["Macro_F1"]) - float(internal_row["Primary_Mean"]),
            }
        )
    return pd.DataFrame(rows)


def write_real_sample_template(numeric: list[str], categorical: list[str]) -> None:
    columns = [
        "Sample_ID",
        "Orchard_ID",
        *numeric,
        *categorical,
        "Fusarium",
        "Observed_Mango_Yield",
        "Observed_Disease_Risk",
        "Observed_Nutrient_Availability",
        "Observed_Disease_Notes",
        "Measurement_Date",
    ]
    pd.DataFrame(columns=columns).to_csv(REAL_SAMPLE_TEMPLATE, index=False)
    if not REAL_SAMPLE_INPUT.exists():
        pd.DataFrame(columns=columns).to_csv(REAL_SAMPLE_INPUT, index=False)


def predict_champions(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    x = build_feature_matrix(df, numeric, categorical)
    yield_model = joblib.load(REGRESSION_CHAMPION_MODEL)
    disease_model = joblib.load(DISEASE_CHAMPION_MODEL)
    nutrient_model = joblib.load(NUTRIENT_CHAMPION_MODEL)
    out = df[[col for col in ["Sample_ID", "Orchard_ID"] if col in df.columns]].copy()
    out["Predicted_Mango_Yield"] = yield_model.predict(x)
    out["Predicted_Disease_Risk"] = disease_model.predict(x).astype(str)
    out["Predicted_Nutrient_Availability"] = nutrient_model.predict(x).astype(str)
    return out


def run_real_sample_validation(numeric: list[str], categorical: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    write_real_sample_template(numeric, categorical)
    real = pd.read_csv(REAL_SAMPLE_INPUT)
    if real.empty:
        status = pd.DataFrame(
            [
                {
                    "Validation_Level": "Real-Sample Validation",
                    "Status": "Pending real orchard samples",
                    "Input_File": str(REAL_SAMPLE_INPUT.relative_to(PROJECT_ROOT)),
                    "Template_File": str(REAL_SAMPLE_TEMPLATE.relative_to(PROJECT_ROOT)),
                    "Rows": 0,
                    "Notes": "Populate the input file with measured real-sample features and observed targets, then rerun Phase 10.",
                }
            ]
        )
        pd.DataFrame(
            columns=[
                "Sample_ID",
                "Orchard_ID",
                "Predicted_Mango_Yield",
                "Predicted_Disease_Risk",
                "Predicted_Nutrient_Availability",
                "Observed_Mango_Yield",
                "Observed_Disease_Risk",
                "Observed_Nutrient_Availability",
            ]
        ).to_csv(REAL_SAMPLE_PREDICTIONS_CSV, index=False)
        return status, pd.DataFrame()

    predictions = predict_champions(real, numeric, categorical)
    for observed, predicted in [
        ("Observed_Mango_Yield", "Predicted_Mango_Yield"),
        ("Observed_Disease_Risk", "Predicted_Disease_Risk"),
        ("Observed_Nutrient_Availability", "Predicted_Nutrient_Availability"),
    ]:
        if observed in real.columns:
            predictions[observed] = real[observed]
            if observed == "Observed_Mango_Yield" and real[observed].notna().any():
                predictions["Mango_Yield_Error"] = real[observed] - predictions[predicted]
            elif real[observed].notna().any():
                predictions[f"{observed}_Correct"] = real[observed].astype(str) == predictions[predicted].astype(str)
    predictions.to_csv(REAL_SAMPLE_PREDICTIONS_CSV, index=False)
    status = pd.DataFrame(
        [
            {
                "Validation_Level": "Real-Sample Validation",
                "Status": "Executed",
                "Input_File": str(REAL_SAMPLE_INPUT.relative_to(PROJECT_ROOT)),
                "Template_File": str(REAL_SAMPLE_TEMPLATE.relative_to(PROJECT_ROOT)),
                "Rows": int(len(real)),
                "Notes": "Predictions written; compare observed targets where present.",
            }
        ]
    )
    return status, predictions


def write_field_template() -> None:
    columns = [
        "Intervention_ID",
        "Orchard_ID",
        "Village",
        "Treatment_Group",
        "Recommendation_Rule_ID",
        "Recommendation_Applied",
        "Baseline_Date",
        "Followup_Date",
        "Baseline_Soil_Health_Index",
        "Followup_Soil_Health_Index",
        "Baseline_Pathogen_Load_Index",
        "Followup_Pathogen_Load_Index",
        "Baseline_Mango_Yield",
        "Followup_Mango_Yield",
        "Baseline_Disease_Incidence_Percent",
        "Followup_Disease_Incidence_Percent",
        "Monitoring_Notes",
    ]
    pd.DataFrame(columns=columns).to_csv(FIELD_TEMPLATE, index=False)
    if not FIELD_INPUT.exists():
        pd.DataFrame(columns=columns).to_csv(FIELD_INPUT, index=False)


def run_field_intervention_validation() -> tuple[pd.DataFrame, pd.DataFrame]:
    write_field_template()
    field = pd.read_csv(FIELD_INPUT)
    if field.empty:
        status = pd.DataFrame(
            [
                {
                    "Validation_Level": "Field Intervention Validation",
                    "Status": "Pending field intervention data",
                    "Input_File": str(FIELD_INPUT.relative_to(PROJECT_ROOT)),
                    "Template_File": str(FIELD_TEMPLATE.relative_to(PROJECT_ROOT)),
                    "Rows": 0,
                    "Notes": "Populate treatment and control observations, then rerun Phase 10.",
                }
            ]
        )
        pd.DataFrame(
            columns=[
                "Treatment_Group",
                "Rows",
                "Mean_Soil_Health_Change",
                "Mean_Pathogen_Load_Change",
                "Mean_Yield_Change",
                "Mean_Disease_Incidence_Change",
            ]
        ).to_csv(FIELD_SUMMARY_CSV, index=False)
        return status, pd.DataFrame()

    field["Soil_Health_Change"] = field["Followup_Soil_Health_Index"] - field["Baseline_Soil_Health_Index"]
    field["Pathogen_Load_Change"] = field["Followup_Pathogen_Load_Index"] - field["Baseline_Pathogen_Load_Index"]
    field["Yield_Change"] = field["Followup_Mango_Yield"] - field["Baseline_Mango_Yield"]
    field["Disease_Incidence_Change"] = field["Followup_Disease_Incidence_Percent"] - field["Baseline_Disease_Incidence_Percent"]
    summary = (
        field.groupby("Treatment_Group", as_index=False)
        .agg(
            Rows=("Intervention_ID", "count"),
            Mean_Soil_Health_Change=("Soil_Health_Change", "mean"),
            Mean_Pathogen_Load_Change=("Pathogen_Load_Change", "mean"),
            Mean_Yield_Change=("Yield_Change", "mean"),
            Mean_Disease_Incidence_Change=("Disease_Incidence_Change", "mean"),
        )
        .sort_values("Treatment_Group")
    )
    summary.to_csv(FIELD_SUMMARY_CSV, index=False)
    status = pd.DataFrame(
        [
            {
                "Validation_Level": "Field Intervention Validation",
                "Status": "Executed",
                "Input_File": str(FIELD_INPUT.relative_to(PROJECT_ROOT)),
                "Template_File": str(FIELD_TEMPLATE.relative_to(PROJECT_ROOT)),
                "Rows": int(len(field)),
                "Notes": "Treatment/control summary written.",
            }
        ]
    )
    return status, summary


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "No rows."
    text = df.copy()
    for col in text.columns:
        if pd.api.types.is_numeric_dtype(text[col]):
            text[col] = text[col].map(lambda value: f"{value:.6g}" if pd.notna(value) else "")
        else:
            text[col] = text[col].fillna("").astype(str)
    headers = text.columns.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in text.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(lines)


def build_manifest() -> pd.DataFrame:
    paths = [
        INTERNAL_CV_REGRESSION_CSV,
        INTERNAL_CV_CLASSIFICATION_CSV,
        INTERNAL_CV_SUMMARY_CSV,
        TRAIN_TEST_COMPARISON_CSV,
        GEO_REGRESSION_CSV,
        GEO_CLASSIFICATION_CSV,
        INTERNAL_VS_GEO_CSV,
        REAL_SAMPLE_STATUS_CSV,
        REAL_SAMPLE_PREDICTIONS_CSV,
        FIELD_STATUS_CSV,
        FIELD_SUMMARY_CSV,
        REAL_SAMPLE_TEMPLATE,
        REAL_SAMPLE_INPUT,
        FIELD_TEMPLATE,
        FIELD_INPUT,
        SUMMARY_JSON,
        REPORT_MD,
    ]
    rows = []
    for path in paths:
        if path.exists():
            rows.append(
                {
                    "Artifact": str(path.relative_to(PROJECT_ROOT)),
                    "Exists": True,
                    "Size_Bytes": int(path.stat().st_size),
                }
            )
        else:
            rows.append({"Artifact": str(path.relative_to(PROJECT_ROOT)), "Exists": False, "Size_Bytes": 0})
    return pd.DataFrame(rows)


def write_report(
    internal_summary: pd.DataFrame,
    geo_reg: pd.DataFrame,
    geo_clf: pd.DataFrame,
    internal_vs_geo: pd.DataFrame,
    real_status: pd.DataFrame,
    field_status: pd.DataFrame,
    manifest: pd.DataFrame,
) -> None:
    best_reg = internal_summary[internal_summary["Task"] == "Regression"].sort_values("Primary_Mean").head(5)
    best_clf = internal_summary[internal_summary["Task"] == "Classification"].sort_values(
        ["Target", "Primary_Mean"], ascending=[True, False]
    )
    lines = [
        "# Phase 10 Validation Report",
        "",
        "Generated by `src/validation/phase10_validation.py`.",
        "",
        "## Purpose",
        "",
        "Phase 10 validates the research prototype at four levels: internal validation, Rahimabad geographic hold-out validation, real-sample validation readiness, and field-intervention validation readiness.",
        "",
        "## 10.1 Internal Validation",
        "",
        f"- K-fold cross-validation folds: `{N_SPLITS}`",
        "- Regression uses KFold.",
        "- Classification uses StratifiedKFold.",
        "- Phase 7 train/test split metrics are consolidated for comparison.",
        "",
        "### Top Internal Regression Models",
        "",
        dataframe_to_markdown(best_reg[["Target", "Model", "Folds", "Mean_RMSE", "Std_RMSE", "Mean_MAE", "Mean_R2"]]),
        "",
        "### Top Internal Classification Models",
        "",
        dataframe_to_markdown(
            best_clf.groupby("Target", group_keys=False).head(5)[
                ["Target", "Model", "Folds", "Mean_Accuracy", "Mean_Macro_F1", "Mean_ROC_AUC"]
            ]
        ),
        "",
        "## 10.2 Rahimabad Geographic Hold-Out Validation",
        "",
        "Models are retrained on all non-Rahimabad rows and evaluated on Rahimabad only.",
        "",
        "### Regression Hold-Out Ranking",
        "",
        dataframe_to_markdown(geo_reg[["Model", "Train_Rows", "Holdout_Rows", "RMSE", "MAE", "R2"]]),
        "",
        "### Classification Hold-Out Ranking",
        "",
        dataframe_to_markdown(
            geo_clf[["Target", "Model", "Train_Rows", "Holdout_Rows", "Accuracy", "Macro_F1", "ROC_AUC"]]
        ),
        "",
        "### Internal vs Geographic Summary",
        "",
        dataframe_to_markdown(internal_vs_geo),
        "",
        "## 10.3 Real-Sample Validation",
        "",
        dataframe_to_markdown(real_status),
        "",
        "## 10.4 Field Intervention Validation",
        "",
        dataframe_to_markdown(field_status),
        "",
        "## Artifacts",
        "",
        dataframe_to_markdown(manifest),
        "",
        "## Caveats",
        "",
        "- Current executable validation uses the synthetic prototype dataset.",
        "- Real-sample validation and field-intervention validation are scaffolded with templates and will execute when real observations are added.",
        "- Compact validation model configurations are used for cross-validation to make repeated validation reproducible on a local machine.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    ensure_dirs()

    log("Loading selected features and Phase 6 feature table")
    numeric, categorical = read_selected_features()
    df = load_feature_table()

    log("Starting 10.1 internal regression validation")
    regression_cv = run_internal_cv_regression(df, numeric, categorical)
    log("Starting 10.1 stratified internal classification validation")
    classification_cv = run_internal_cv_classification(df, numeric, categorical)
    log("Summarizing internal validation and Phase 7 train/test comparison")
    internal_summary = summarize_internal_cv(regression_cv, classification_cv)
    train_test = build_train_test_comparison()
    log("Starting 10.2 Rahimabad geographic hold-out validation")
    geo_reg = run_geographic_holdout_regression(df, numeric, categorical)
    geo_clf = run_geographic_holdout_classification(df, numeric, categorical)
    internal_vs_geo = build_internal_vs_geo_summary(internal_summary, geo_reg, geo_clf)
    log("Preparing 10.3 real-sample validation artifacts")
    real_status, real_predictions = run_real_sample_validation(numeric, categorical)
    log("Preparing 10.4 field-intervention validation artifacts")
    field_status, field_summary = run_field_intervention_validation()

    log("Writing Phase 10 validation outputs")
    regression_cv.to_csv(INTERNAL_CV_REGRESSION_CSV, index=False)
    classification_cv.to_csv(INTERNAL_CV_CLASSIFICATION_CSV, index=False)
    internal_summary.to_csv(INTERNAL_CV_SUMMARY_CSV, index=False)
    train_test.to_csv(TRAIN_TEST_COMPARISON_CSV, index=False)
    geo_reg.to_csv(GEO_REGRESSION_CSV, index=False)
    geo_clf.to_csv(GEO_CLASSIFICATION_CSV, index=False)
    internal_vs_geo.to_csv(INTERNAL_VS_GEO_CSV, index=False)
    real_status.to_csv(REAL_SAMPLE_STATUS_CSV, index=False)
    field_status.to_csv(FIELD_STATUS_CSV, index=False)

    best_regression = internal_summary[internal_summary["Task"] == "Regression"].sort_values("Primary_Mean").iloc[0]
    best_classification = (
        internal_summary[internal_summary["Task"] == "Classification"]
        .sort_values(["Target", "Primary_Mean"], ascending=[True, False])
        .groupby("Target")
        .head(1)
    )
    summary = {
        "phase": "10",
        "status": "complete",
        "rows": int(len(df)),
        "kfold_splits": N_SPLITS,
        "rahimabad_rows": int((df["Village"] == "Rahimabad").sum()),
        "best_internal_regression_model": {
            "model": str(best_regression["Model"]),
            "mean_rmse": float(best_regression["Mean_RMSE"]),
        },
        "best_internal_classification_models": {
            row["Target"]: {"model": row["Model"], "mean_macro_f1": float(row["Mean_Macro_F1"])}
            for _, row in best_classification.iterrows()
        },
        "real_sample_validation_status": str(real_status.iloc[0]["Status"]),
        "field_intervention_validation_status": str(field_status.iloc[0]["Status"]),
        "outputs": {
            "internal_cv_regression": str(INTERNAL_CV_REGRESSION_CSV.relative_to(PROJECT_ROOT)),
            "internal_cv_classification": str(INTERNAL_CV_CLASSIFICATION_CSV.relative_to(PROJECT_ROOT)),
            "internal_cv_summary": str(INTERNAL_CV_SUMMARY_CSV.relative_to(PROJECT_ROOT)),
            "train_test_comparison": str(TRAIN_TEST_COMPARISON_CSV.relative_to(PROJECT_ROOT)),
            "geographic_regression": str(GEO_REGRESSION_CSV.relative_to(PROJECT_ROOT)),
            "geographic_classification": str(GEO_CLASSIFICATION_CSV.relative_to(PROJECT_ROOT)),
            "internal_vs_geographic": str(INTERNAL_VS_GEO_CSV.relative_to(PROJECT_ROOT)),
            "real_sample_template": str(REAL_SAMPLE_TEMPLATE.relative_to(PROJECT_ROOT)),
            "field_intervention_template": str(FIELD_TEMPLATE.relative_to(PROJECT_ROOT)),
            "report": str(REPORT_MD.relative_to(PROJECT_ROOT)),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    manifest = build_manifest()
    manifest.to_csv(VALIDATION_MANIFEST_CSV, index=False)
    write_report(internal_summary, geo_reg, geo_clf, internal_vs_geo, real_status, field_status, manifest)

    # Rebuild after report creation so the manifest records the report itself.
    manifest = build_manifest()
    manifest.to_csv(VALIDATION_MANIFEST_CSV, index=False)
    write_report(internal_summary, geo_reg, geo_clf, internal_vs_geo, real_status, field_status, manifest)

    print("Phase 10 validation complete.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

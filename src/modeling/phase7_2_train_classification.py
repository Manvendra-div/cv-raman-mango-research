"""Phase 7.2 classification modeling for disease and nutrient targets.

Trains and evaluates classification models using the Phase 6 selected feature
set. The script writes model artifacts, metrics, confusion matrices,
calibration curves, predictions, and per-target champion-model metadata.
"""

from __future__ import annotations

import json
import shutil
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
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_TABLE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"
SELECTED_FEATURES_JSON = PROJECT_ROOT / "data" / "processed" / "selected_features.json"

MODEL_DIR = PROJECT_ROOT / "outputs" / "models" / "classification"
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics" / "classification"
PREDICTIONS_DIR = PROJECT_ROOT / "outputs" / "predictions" / "classification"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "phase7_classification"

METRICS_CSV = METRICS_DIR / "classification_model_metrics.csv"
CLASS_METRICS_CSV = METRICS_DIR / "classification_class_metrics.csv"
CONFUSION_CSV = METRICS_DIR / "classification_confusion_matrix.csv"
CALIBRATION_CSV = METRICS_DIR / "classification_calibration_curve.csv"
FEATURE_IMPORTANCE_CSV = METRICS_DIR / "classification_tree_feature_importance.csv"
PREDICTIONS_CSV = PREDICTIONS_DIR / "classification_predictions_all_models.csv"
CHAMPION_PREDICTIONS_CSV = PREDICTIONS_DIR / "classification_champion_predictions.csv"
SUMMARY_JSON = METRICS_DIR / "classification_model_summary.json"
REPORT_MD = REPORT_DIR / "classification_model_development_report.md"
CHAMPION_POINTER = MODEL_DIR / "champion_classification_models.json"

TARGETS = ["Disease_Risk", "Nutrient_Availability"]
PREFERRED_CLASS_ORDER = {
    "Disease_Risk": ["Low", "Medium", "High"],
    "Nutrient_Availability": ["Deficient", "Optimal", "High"],
}
SPLIT_ORDER = ["train", "validation", "test", "holdout_rahimabad"]
RANDOM_STATE = 42
CALIBRATION_BINS = 10


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
        raise FileNotFoundError("Missing Phase 6 feature table. Run Phase 6 before Phase 7.2.")
    df = pd.read_csv(FEATURE_TABLE)
    if "Split" not in df.columns:
        raise ValueError("Feature table must contain the Phase 5 Split column.")
    missing_targets = [target for target in TARGETS if target not in df.columns]
    if missing_targets:
        raise ValueError(f"Feature table is missing classification targets: {missing_targets}")
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
    return [
        ModelSpec(
            "Majority_Baseline",
            DummyClassifier(strategy="most_frequent"),
            "Most-frequent-class control baseline.",
        ),
        ModelSpec(
            "Logistic_Regression",
            LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
                solver="lbfgs",
                random_state=RANDOM_STATE,
            ),
            "Balanced Logistic Regression baseline.",
        ),
        ModelSpec(
            "Linear_SVM",
            CalibratedClassifierCV(
                estimator=LinearSVC(
                    C=1.0,
                    class_weight="balanced",
                    dual=False,
                    max_iter=20000,
                    random_state=RANDOM_STATE,
                ),
                method="sigmoid",
                cv=3,
            ),
            "Calibrated linear Support Vector Machine classifier.",
        ),
        ModelSpec(
            "Random_Forest",
            RandomForestClassifier(
                n_estimators=250,
                max_depth=None,
                min_samples_leaf=2,
                class_weight="balanced_subsample",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "Random Forest classifier for nonlinear tabular interactions.",
        ),
        ModelSpec(
            "Gradient_Boosting",
            GradientBoostingClassifier(
                n_estimators=250,
                learning_rate=0.05,
                max_depth=3,
                random_state=RANDOM_STATE,
            ),
            "Gradient Boosting classifier for nonlinear threshold effects.",
        ),
        ModelSpec(
            "MLP_Classifier",
            MLPClassifier(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                solver="adam",
                alpha=0.0005,
                learning_rate_init=0.001,
                max_iter=250,
                early_stopping=False,
                n_iter_no_change=20,
                random_state=RANDOM_STATE,
            ),
            "Neural network classifier for structured tabular data.",
        ),
    ]


def safe_name(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "_" for char in value]
    return "_".join("".join(chars).split("_")).strip("_")


def observed_class_order(target: str, df: pd.DataFrame) -> list[str]:
    observed = set(df[target].dropna().astype(str).unique().tolist())
    preferred = [label for label in PREFERRED_CLASS_ORDER.get(target, []) if label in observed]
    remaining = sorted(label for label in observed if label not in preferred)
    return preferred + remaining


def build_feature_matrix(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    missing = [col for col in numeric + categorical if col not in df.columns]
    if missing:
        raise ValueError(f"Missing selected feature columns: {missing}")
    return df[numeric + categorical].copy()


def fitted_model_classes(pipeline: Pipeline) -> list[str]:
    estimator = pipeline.named_steps["model"]
    if not hasattr(estimator, "classes_"):
        raise ValueError(f"Estimator {type(estimator).__name__} does not expose classes_.")
    return [str(value) for value in estimator.classes_]


def predict_proba_aligned(pipeline: Pipeline, x: pd.DataFrame, classes: list[str]) -> np.ndarray:
    if not hasattr(pipeline, "predict_proba"):
        raise ValueError(f"Pipeline for {type(pipeline.named_steps['model']).__name__} lacks predict_proba.")

    raw_proba = pipeline.predict_proba(x)
    model_classes = fitted_model_classes(pipeline)
    aligned = np.zeros((len(x), len(classes)), dtype=float)

    for out_index, class_label in enumerate(classes):
        if class_label in model_classes:
            aligned[:, out_index] = raw_proba[:, model_classes.index(class_label)]

    row_sums = aligned.sum(axis=1)
    missing = row_sums == 0
    if missing.any():
        aligned[missing, :] = 1.0 / len(classes)
        row_sums = aligned.sum(axis=1)
    return aligned / row_sums[:, None]


def probability_columns(classes: list[str]) -> list[str]:
    return [f"Prob_{safe_name(class_label)}" for class_label in classes]


def make_predictions_frame(
    target: str,
    model_name: str,
    split_name: str,
    split_df: pd.DataFrame,
    y_pred: np.ndarray,
    proba: np.ndarray,
    classes: list[str],
) -> pd.DataFrame:
    y_true = split_df[target].astype(str).to_numpy()
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
    out.insert(0, "Target", target)
    out.insert(1, "Model", model_name)
    out.insert(2, "Split", split_name)
    out["Actual_Class"] = y_true
    out["Predicted_Class"] = y_pred.astype(str)
    out["Correct"] = out["Actual_Class"] == out["Predicted_Class"]

    class_to_index = {class_label: index for index, class_label in enumerate(classes)}
    predicted_probabilities = []
    actual_probabilities = []
    for row_index, predicted_label in enumerate(out["Predicted_Class"]):
        predicted_probabilities.append(proba[row_index, class_to_index.get(predicted_label, 0)])
    for row_index, actual_label in enumerate(out["Actual_Class"]):
        actual_probabilities.append(proba[row_index, class_to_index.get(actual_label, 0)])

    out["Predicted_Class_Probability"] = predicted_probabilities
    out["Actual_Class_Probability"] = actual_probabilities
    for class_index, class_label in enumerate(classes):
        out[f"Prob_{safe_name(class_label)}"] = proba[:, class_index]
    return out


def multiclass_brier_score(y_true: pd.Series, proba: np.ndarray, classes: list[str]) -> float:
    class_to_index = {class_label: index for index, class_label in enumerate(classes)}
    y_one_hot = np.zeros_like(proba, dtype=float)
    for row_index, label in enumerate(y_true.astype(str)):
        if label in class_to_index:
            y_one_hot[row_index, class_to_index[label]] = 1.0
    return float(np.mean(np.sum((proba - y_one_hot) ** 2, axis=1)))


def roc_auc_for(y_true: pd.Series, proba: np.ndarray, classes: list[str]) -> float:
    observed = set(y_true.astype(str).unique().tolist())
    if len(observed) < 2:
        return float("nan")
    scores = []
    for class_index, class_label in enumerate(classes):
        y_binary = (y_true.astype(str) == class_label).astype(int)
        if y_binary.nunique() < 2:
            continue
        try:
            scores.append(roc_auc_score(y_binary, proba[:, class_index]))
        except ValueError:
            continue
    if not scores:
        return float("nan")
    return float(np.mean(scores))


def metrics_for(y_true: pd.Series, y_pred: pd.Series, proba: np.ndarray, classes: list[str]) -> dict[str, float]:
    return {
        "Accuracy": float(accuracy_score(y_true, y_pred)),
        "Balanced_Accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "Precision_Macro": float(precision_score(y_true, y_pred, labels=classes, average="macro", zero_division=0)),
        "Recall_Macro": float(recall_score(y_true, y_pred, labels=classes, average="macro", zero_division=0)),
        "Macro_F1": float(f1_score(y_true, y_pred, labels=classes, average="macro", zero_division=0)),
        "ROC_AUC": roc_auc_for(y_true, proba, classes),
        "Multiclass_Brier": multiclass_brier_score(y_true, proba, classes),
        "Mean_Predicted_Class_Probability": float(np.mean(np.max(proba, axis=1))),
    }


def evaluate_predictions(
    predictions: pd.DataFrame,
    class_orders: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    class_metric_rows = []
    confusion_rows = []
    calibration_rows = []

    for (target, model, split), group in predictions.groupby(["Target", "Model", "Split"], sort=False):
        classes = class_orders[target]
        prob_cols = probability_columns(classes)
        proba = group[prob_cols].to_numpy(dtype=float)
        y_true = group["Actual_Class"].astype(str)
        y_pred = group["Predicted_Class"].astype(str)

        row = {"Target": target, "Model": model, "Split": split, "Rows": int(len(group))}
        row.update(metrics_for(y_true, y_pred, proba, classes))
        metric_rows.append(row)

        precision, recall, f1, support = precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=classes,
            zero_division=0,
        )
        for class_label, precision_value, recall_value, f1_value, support_value in zip(
            classes,
            precision,
            recall,
            f1,
            support,
            strict=True,
        ):
            class_metric_rows.append(
                {
                    "Target": target,
                    "Model": model,
                    "Split": split,
                    "Class": class_label,
                    "Precision": float(precision_value),
                    "Recall": float(recall_value),
                    "F1": float(f1_value),
                    "Support": int(support_value),
                }
            )

        matrix = confusion_matrix(y_true, y_pred, labels=classes)
        actual_totals = matrix.sum(axis=1)
        for actual_index, actual_label in enumerate(classes):
            for predicted_index, predicted_label in enumerate(classes):
                count = int(matrix[actual_index, predicted_index])
                total = int(actual_totals[actual_index])
                confusion_rows.append(
                    {
                        "Target": target,
                        "Model": model,
                        "Split": split,
                        "Actual_Class": actual_label,
                        "Predicted_Class": predicted_label,
                        "Count": count,
                        "Actual_Class_Total": total,
                        "Row_Percent": float(count / total) if total else 0.0,
                    }
                )

        for class_label, probability_column in zip(classes, prob_cols, strict=True):
            probabilities = group[probability_column].to_numpy(dtype=float)
            actual = (y_true == class_label).astype(int).to_numpy()
            bin_ids = np.minimum((probabilities * CALIBRATION_BINS).astype(int), CALIBRATION_BINS - 1)
            for bin_id in range(CALIBRATION_BINS):
                mask = bin_ids == bin_id
                if not mask.any():
                    continue
                calibration_rows.append(
                    {
                        "Target": target,
                        "Model": model,
                        "Split": split,
                        "Class": class_label,
                        "Bin": int(bin_id + 1),
                        "Bin_Lower": float(bin_id / CALIBRATION_BINS),
                        "Bin_Upper": float((bin_id + 1) / CALIBRATION_BINS),
                        "Count": int(mask.sum()),
                        "Mean_Predicted_Probability": float(probabilities[mask].mean()),
                        "Observed_Class_Rate": float(actual[mask].mean()),
                    }
                )

    return (
        pd.DataFrame(metric_rows),
        pd.DataFrame(class_metric_rows),
        pd.DataFrame(confusion_rows),
        pd.DataFrame(calibration_rows),
    )


def build_rule_config(target: str, train_df: pd.DataFrame) -> dict[str, Any]:
    if target == "Disease_Risk":
        terms = [
            ("Pathogen_Load_Index_Phase6", 1.0),
            ("Pathogen_Beneficial_Ratio_Phase6", 0.5),
            ("Beneficial_Microbial_Index_Phase6", -0.35),
            ("Soil_Health_Index_Phase6", -0.35),
        ]
        increase_class = "High"
        decrease_class = "Low"
        rationale = "Higher pathogen pressure increases High risk; beneficial microbes and soil health reduce risk."
    elif target == "Nutrient_Availability":
        terms = [
            ("NPK_Balance_Score_Phase6", 1.2),
            ("Soil_Chemical_Fertility_Score_Phase6", 0.55),
            ("Available_P", 0.35),
            ("Available_K", 0.35),
            ("Total_Nitrogen", 0.25),
        ]
        increase_class = "High"
        decrease_class = "Optimal"
        rationale = "Higher nutrient and fertility scores shift the current two-class target toward High."
    else:
        raise ValueError(f"No hybrid rule configuration defined for target: {target}")

    stats = {}
    for column, _ in terms:
        values = train_df[column].astype(float)
        scale = float(values.std())
        stats[column] = {
            "center": float(values.mean()),
            "scale": scale if scale > 0 else 1.0,
        }

    return {
        "target": target,
        "terms": [{"feature": column, "weight": weight} for column, weight in terms],
        "feature_standardization": stats,
        "increase_class": increase_class,
        "decrease_class": decrease_class,
        "probability_multiplier": 0.055,
        "probability_clip": 0.18,
        "rationale": rationale,
    }


def hybrid_rule_adjusted_proba(
    target: str,
    df: pd.DataFrame,
    base_proba: np.ndarray,
    classes: list[str],
    config: dict[str, Any],
) -> np.ndarray:
    signal = np.zeros(len(df), dtype=float)
    for term in config["terms"]:
        column = term["feature"]
        stats = config["feature_standardization"][column]
        standardized = (df[column].astype(float).to_numpy() - stats["center"]) / stats["scale"]
        signal += float(term["weight"]) * standardized

    delta = np.clip(
        signal * float(config["probability_multiplier"]),
        -float(config["probability_clip"]),
        float(config["probability_clip"]),
    )

    adjusted = base_proba.copy()
    increase_class = config["increase_class"]
    decrease_class = config["decrease_class"]
    if increase_class in classes and decrease_class in classes:
        increase_index = classes.index(increase_class)
        decrease_index = classes.index(decrease_class)
        adjusted[:, increase_index] += delta
        adjusted[:, decrease_index] -= delta
    elif target == "Nutrient_Availability" and {"Deficient", "High"}.issubset(set(classes)):
        high_index = classes.index("High")
        deficient_index = classes.index("Deficient")
        adjusted[:, high_index] += np.maximum(delta, 0.0)
        adjusted[:, deficient_index] += np.maximum(-delta, 0.0)

    adjusted = np.clip(adjusted, 1e-8, None)
    return adjusted / adjusted.sum(axis=1, keepdims=True)


def labels_from_proba(proba: np.ndarray, classes: list[str]) -> np.ndarray:
    indexes = np.argmax(proba, axis=1)
    return np.array([classes[index] for index in indexes])


def train_hybrid_model(
    target: str,
    train_df: pd.DataFrame,
    split_dfs: dict[str, pd.DataFrame],
    numeric_features: list[str],
    categorical_features: list[str],
    classes: list[str],
) -> tuple[Pipeline, dict[str, Any], list[pd.DataFrame]]:
    base = Pipeline(
        steps=[
            ("preprocess", make_preprocessor(numeric_features, categorical_features)),
            (
                "model",
                GradientBoostingClassifier(
                    n_estimators=250,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    base.fit(build_feature_matrix(train_df, numeric_features, categorical_features), train_df[target].astype(str))
    config = build_rule_config(target, train_df)

    prediction_frames = []
    for split_name in SPLIT_ORDER:
        split_df = split_dfs[split_name]
        x = build_feature_matrix(split_df, numeric_features, categorical_features)
        base_proba = predict_proba_aligned(base, x, classes)
        y_proba = hybrid_rule_adjusted_proba(target, split_df, base_proba, classes, config)
        y_pred = labels_from_proba(y_proba, classes)
        prediction_frames.append(
            make_predictions_frame(target, "Hybrid_Rule_Guided_GB", split_name, split_df, y_pred, y_proba, classes)
        )

    return base, config, prediction_frames


def extract_tree_feature_importance(target: str, model_name: str, pipeline: Pipeline) -> pd.DataFrame:
    estimator = pipeline.named_steps["model"]
    if not hasattr(estimator, "feature_importances_"):
        return pd.DataFrame()
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    return pd.DataFrame(
        {
            "Target": target,
            "Model": model_name,
            "Feature": names,
            "Importance": estimator.feature_importances_,
        }
    ).sort_values(["Target", "Model", "Importance"], ascending=[True, True, False])


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
    champion_models: dict[str, dict[str, Any]],
    selected_features: list[str],
    categorical_features: list[str],
    class_orders: dict[str, list[str]],
    model_descriptions: dict[str, str],
) -> None:
    lines = [
        "# Phase 7.2 Classification Model Development Report",
        "",
        "Generated by `src/modeling/phase7_2_train_classification.py`.",
        "",
        "## Targets",
        "",
    ]
    for target in TARGETS:
        lines.append(f"- `{target}` classes: {', '.join(class_orders[target])}")

    lines.extend(
        [
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
    )
    for model, description in model_descriptions.items():
        lines.append(f"- `{model}`: {description}")

    lines.extend(
        [
            "",
            "## Champion Selection",
            "",
            "- Champion model selected independently for each target by highest validation macro F1-score.",
            "- Accuracy and ROC-AUC are retained as secondary diagnostics.",
            "",
        ]
    )
    champion_table = pd.DataFrame(
        [
            {
                "Target": target,
                "Champion_Model": payload["champion_model"],
                "Validation_Macro_F1": payload["validation_macro_f1"],
                "Validation_Accuracy": payload["validation_accuracy"],
                "Validation_ROC_AUC": payload["validation_roc_auc"],
            }
            for target, payload in champion_models.items()
        ]
    )
    lines.append(dataframe_to_markdown(champion_table))

    for target in TARGETS:
        lines.extend(
            [
                "",
                f"## {target} Validation Metrics",
                "",
            ]
        )
        validation = metrics[(metrics["Target"] == target) & (metrics["Split"] == "validation")].sort_values(
            ["Macro_F1", "Accuracy"],
            ascending=[False, False],
        )
        lines.append(
            dataframe_to_markdown(
                validation[["Model", "Rows", "Accuracy", "Precision_Macro", "Recall_Macro", "Macro_F1", "ROC_AUC"]]
            )
        )

        lines.extend(["", f"## {target} Test Metrics", ""])
        test = metrics[(metrics["Target"] == target) & (metrics["Split"] == "test")].sort_values(
            ["Macro_F1", "Accuracy"],
            ascending=[False, False],
        )
        lines.append(
            dataframe_to_markdown(
                test[["Model", "Rows", "Accuracy", "Precision_Macro", "Recall_Macro", "Macro_F1", "ROC_AUC"]]
            )
        )

        lines.extend(["", f"## {target} Rahimabad Geographic Hold-Out Metrics", ""])
        holdout = metrics[(metrics["Target"] == target) & (metrics["Split"] == "holdout_rahimabad")].sort_values(
            ["Macro_F1", "Accuracy"],
            ascending=[False, False],
        )
        lines.append(
            dataframe_to_markdown(
                holdout[["Model", "Rows", "Accuracy", "Precision_Macro", "Recall_Macro", "Macro_F1", "ROC_AUC"]]
            )
        )

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- Model metrics: `outputs/metrics/classification/classification_model_metrics.csv`",
            "- Class-wise metrics: `outputs/metrics/classification/classification_class_metrics.csv`",
            "- Confusion matrices: `outputs/metrics/classification/classification_confusion_matrix.csv`",
            "- Calibration curves: `outputs/metrics/classification/classification_calibration_curve.csv`",
            "- Predictions: `outputs/predictions/classification/classification_predictions_all_models.csv`",
            "- Champion predictions: `outputs/predictions/classification/classification_champion_predictions.csv`",
            "- Saved models: `outputs/models/classification/`",
            "",
            "## Caveats",
            "",
            "- The current data are synthetic prototype data.",
            "- `Nutrient_Availability` currently contains `High` and `Optimal`; no `Deficient` rows are present.",
            "- The hybrid models use transparent rule adjustments on top of Gradient Boosting probabilities.",
            "- Phase 8 XAI should explain the champion classifiers and verify whether important features are agronomically meaningful.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    ensure_dirs()

    numeric_features, categorical_features = read_selected_features()
    df = load_feature_table()
    class_orders = {target: observed_class_order(target, df) for target in TARGETS}
    split_dfs = {split: df[df["Split"] == split].copy() for split in SPLIT_ORDER}
    if any(frame.empty for frame in split_dfs.values()):
        empty = [name for name, frame in split_dfs.items() if frame.empty]
        raise ValueError(f"Missing split rows for: {empty}")

    model_specs = get_model_specs()
    model_descriptions = {spec.name: spec.description for spec in model_specs}
    model_descriptions["Hybrid_Rule_Guided_GB"] = "Gradient Boosting plus transparent agronomic rule adjustment."

    all_predictions = []
    feature_importance_parts = []

    for target in TARGETS:
        classes = class_orders[target]
        target_split_dfs = {
            split: split_df[split_df[target].notna()].copy()
            for split, split_df in split_dfs.items()
        }
        train_df = target_split_dfs["train"]
        if train_df[target].nunique() < 2:
            raise ValueError(f"Target {target} has fewer than two classes in the train split.")

        for spec in model_specs:
            pipeline = Pipeline(
                steps=[
                    ("preprocess", make_preprocessor(numeric_features, categorical_features)),
                    ("model", clone(spec.estimator)),
                ]
            )
            pipeline.fit(build_feature_matrix(train_df, numeric_features, categorical_features), train_df[target].astype(str))

            model_path = MODEL_DIR / f"{safe_name(target)}__{safe_name(spec.name)}.joblib"
            joblib.dump(pipeline, model_path)

            importance = extract_tree_feature_importance(target, spec.name, pipeline)
            if not importance.empty:
                feature_importance_parts.append(importance)

            for split_name in SPLIT_ORDER:
                split_df = target_split_dfs[split_name]
                x = build_feature_matrix(split_df, numeric_features, categorical_features)
                proba = predict_proba_aligned(pipeline, x, classes)
                y_pred = labels_from_proba(proba, classes)
                all_predictions.append(make_predictions_frame(target, spec.name, split_name, split_df, y_pred, proba, classes))

        hybrid_base, hybrid_config, hybrid_predictions = train_hybrid_model(
            target,
            train_df,
            target_split_dfs,
            numeric_features,
            categorical_features,
            classes,
        )
        hybrid_base_path = MODEL_DIR / f"{safe_name(target)}__hybrid_rule_guided_gb_base_pipeline.joblib"
        hybrid_config_path = MODEL_DIR / f"{safe_name(target)}__hybrid_rule_guided_gb_rule_config.json"
        joblib.dump(hybrid_base, hybrid_base_path)
        hybrid_config_path.write_text(json.dumps(hybrid_config, indent=2), encoding="utf-8")
        hybrid_importance = extract_tree_feature_importance(target, "Hybrid_Rule_Guided_GB", hybrid_base)
        if not hybrid_importance.empty:
            feature_importance_parts.append(hybrid_importance)
        all_predictions.extend(hybrid_predictions)

    predictions = pd.concat(all_predictions, ignore_index=True)
    metrics, class_metrics, confusion, calibration = evaluate_predictions(predictions, class_orders)

    metrics.to_csv(METRICS_CSV, index=False)
    class_metrics.to_csv(CLASS_METRICS_CSV, index=False)
    confusion.to_csv(CONFUSION_CSV, index=False)
    calibration.to_csv(CALIBRATION_CSV, index=False)
    predictions.to_csv(PREDICTIONS_CSV, index=False)

    if feature_importance_parts:
        pd.concat(feature_importance_parts, ignore_index=True).to_csv(FEATURE_IMPORTANCE_CSV, index=False)
    else:
        pd.DataFrame(columns=["Target", "Model", "Feature", "Importance"]).to_csv(FEATURE_IMPORTANCE_CSV, index=False)

    champion_models: dict[str, dict[str, Any]] = {}
    champion_prediction_parts = []
    for target in TARGETS:
        validation = metrics[(metrics["Target"] == target) & (metrics["Split"] == "validation")].copy()
        validation["ROC_AUC_Sort"] = validation["ROC_AUC"].fillna(-np.inf)
        champion_row = validation.sort_values(
            ["Macro_F1", "Accuracy", "ROC_AUC_Sort"],
            ascending=[False, False, False],
        ).iloc[0]
        champion_model = str(champion_row["Model"])
        champion_prediction_parts.append(
            predictions[(predictions["Target"] == target) & (predictions["Model"] == champion_model)].copy()
        )

        model_file = MODEL_DIR / f"{safe_name(target)}__{safe_name(champion_model)}.joblib"
        champion_artifact: dict[str, Any] = {
            "target": target,
            "classes": class_orders[target],
            "champion_model": champion_model,
            "selection_metric": "validation_Macro_F1",
            "validation_macro_f1": float(champion_row["Macro_F1"]),
            "validation_accuracy": float(champion_row["Accuracy"]),
            "validation_roc_auc": float(champion_row["ROC_AUC"]) if pd.notna(champion_row["ROC_AUC"]) else None,
            "selected_numeric_features": numeric_features,
            "categorical_features": categorical_features,
        }
        champion_copy = MODEL_DIR / f"champion_{safe_name(target)}_model.joblib"
        if model_file.exists():
            shutil.copyfile(model_file, champion_copy)
            champion_artifact["model_artifact"] = str(champion_copy.relative_to(PROJECT_ROOT))
        elif champion_model == "Hybrid_Rule_Guided_GB":
            champion_artifact["base_model_artifact"] = str(
                (MODEL_DIR / f"{safe_name(target)}__hybrid_rule_guided_gb_base_pipeline.joblib").relative_to(PROJECT_ROOT)
            )
            champion_artifact["rule_config"] = str(
                (MODEL_DIR / f"{safe_name(target)}__hybrid_rule_guided_gb_rule_config.json").relative_to(PROJECT_ROOT)
            )
        champion_models[target] = champion_artifact

    pd.concat(champion_prediction_parts, ignore_index=True).to_csv(CHAMPION_PREDICTIONS_CSV, index=False)
    CHAMPION_POINTER.write_text(json.dumps(champion_models, indent=2), encoding="utf-8")

    summary = {
        "targets": TARGETS,
        "rows": int(len(df)),
        "class_orders": class_orders,
        "models": sorted(predictions["Model"].unique().tolist()),
        "champion_models": {
            target: {
                "model": payload["champion_model"],
                "validation_macro_f1": payload["validation_macro_f1"],
                "validation_accuracy": payload["validation_accuracy"],
                "validation_roc_auc": payload["validation_roc_auc"],
            }
            for target, payload in champion_models.items()
        },
        "metrics_file": str(METRICS_CSV.relative_to(PROJECT_ROOT)),
        "predictions_file": str(PREDICTIONS_CSV.relative_to(PROJECT_ROOT)),
        "champion_pointer": str(CHAMPION_POINTER.relative_to(PROJECT_ROOT)),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(metrics, champion_models, numeric_features, categorical_features, class_orders, model_descriptions)

    print("Phase 7.2 classification modeling complete.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

"""Phase 7.3 complete model-results reporting.

Compiles the verified Phase 7.1 regression and Phase 7.2 classification
outputs into final model-result tables, reconciles existing report claims
against reproduced metrics, and writes a reproducibility report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REGRESSION_METRICS = PROJECT_ROOT / "outputs" / "metrics" / "regression" / "regression_model_metrics.csv"
REGRESSION_CHAMPION = PROJECT_ROOT / "outputs" / "models" / "regression" / "champion_regression_model.json"
CLASSIFICATION_METRICS = PROJECT_ROOT / "outputs" / "metrics" / "classification" / "classification_model_metrics.csv"
CLASSIFICATION_CHAMPIONS = PROJECT_ROOT / "outputs" / "models" / "classification" / "champion_classification_models.json"
FEATURE_TABLE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"

OUTPUT_METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics" / "phase7_model_results"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "phase7_model_results"

CHAMPION_SUMMARY_CSV = OUTPUT_METRICS_DIR / "phase7_champion_summary.csv"
REPORTED_VS_REPRODUCED_CSV = OUTPUT_METRICS_DIR / "phase7_reported_vs_reproduced.csv"
RAHIMABAD_SUMMARY_CSV = OUTPUT_METRICS_DIR / "phase7_rahimabad_holdout_summary.csv"
ARTIFACT_MANIFEST_CSV = OUTPUT_METRICS_DIR / "phase7_model_artifact_manifest.csv"
SUMMARY_JSON = OUTPUT_METRICS_DIR / "phase7_model_results_summary.json"
REPORT_MD = OUTPUT_REPORT_DIR / "phase7_complete_model_results_report.md"

SPLITS = ["train", "validation", "test", "holdout_rahimabad"]
CLASSIFICATION_TARGETS = ["Disease_Risk", "Nutrient_Availability"]


def ensure_dirs() -> None:
    OUTPUT_METRICS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_files(paths: list[Path]) -> None:
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required Phase 7 input files: {missing}")


def metric_row(df: pd.DataFrame, **filters: str) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        mask &= df[column].astype(str).eq(value)
    rows = df[mask]
    if rows.empty:
        raise ValueError(f"No metric row found for filters: {filters}")
    return rows.iloc[0]


def float_or_none(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def percent(value: Any) -> float:
    return float(value) * 100.0


def format_float(value: Any, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.{digits}g}"


def numeric_assessment(metric: str, delta: float) -> str:
    abs_delta = abs(delta)
    if metric in {"RMSE"}:
        if abs_delta <= 0.01:
            return "matched"
        if abs_delta <= 0.10:
            return "near"
        return "different"
    if metric in {"Accuracy_Percent"}:
        if abs_delta <= 0.10:
            return "matched"
        if abs_delta <= 0.50:
            return "near"
        return "different"
    if metric in {"Macro_F1"}:
        if abs_delta <= 0.001:
            return "matched"
        if abs_delta <= 0.005:
            return "near"
        return "different"
    if metric in {"Sample_Count"}:
        return "matched" if abs_delta == 0 else "different"
    return "different"


def add_numeric_reconciliation(
    rows: list[dict[str, Any]],
    section: str,
    claim_item: str,
    reported_model: str,
    reproduced_model: str,
    metric: str,
    reported_value: float,
    reproduced_value: float,
    reproduced_split: str,
    notes: str,
) -> None:
    delta = reproduced_value - reported_value
    rows.append(
        {
            "Section": section,
            "Claim_Item": claim_item,
            "Reported_Model": reported_model,
            "Reproduced_Model": reproduced_model,
            "Metric": metric,
            "Reported_Value": reported_value,
            "Reproduced_Value": reproduced_value,
            "Reproduced_Split": reproduced_split,
            "Difference": delta,
            "Assessment": numeric_assessment(metric, delta),
            "Notes": notes,
        }
    )


def add_text_reconciliation(
    rows: list[dict[str, Any]],
    section: str,
    claim_item: str,
    reported_value: str,
    reproduced_value: str,
    reproduced_split: str,
    notes: str,
) -> None:
    reported_normalized = reported_value.lower().replace(" ", "_")
    reproduced_normalized = reproduced_value.lower().replace(" ", "_")
    rows.append(
        {
            "Section": section,
            "Claim_Item": claim_item,
            "Reported_Model": reported_value,
            "Reproduced_Model": reproduced_value,
            "Metric": "Champion_Model",
            "Reported_Value": reported_value,
            "Reproduced_Value": reproduced_value,
            "Reproduced_Split": reproduced_split,
            "Difference": "",
            "Assessment": "matched" if reported_normalized == reproduced_normalized else "different",
            "Notes": notes,
        }
    )


def build_champion_summary(
    regression: pd.DataFrame,
    regression_champion: dict[str, Any],
    classification: pd.DataFrame,
    classification_champions: dict[str, Any],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    regression_model = regression_champion["champion_model"]
    reg_row = {
        "Task": "Regression",
        "Target": "Mango_Yield",
        "Champion_Model": regression_model,
        "Selection_Metric": "minimum validation RMSE",
        "Validation_Primary": metric_row(regression, Model=regression_model, Split="validation")["RMSE"],
        "Validation_Secondary": metric_row(regression, Model=regression_model, Split="validation")["MAE"],
        "Validation_Tertiary": metric_row(regression, Model=regression_model, Split="validation")["R2"],
        "Test_Primary": metric_row(regression, Model=regression_model, Split="test")["RMSE"],
        "Holdout_Primary": metric_row(regression, Model=regression_model, Split="holdout_rahimabad")["RMSE"],
        "Primary_Metric_Name": "RMSE",
        "Secondary_Metric_Name": "MAE",
        "Tertiary_Metric_Name": "R2",
        "Validation_Tie_Models": "",
        "Model_Artifact": regression_champion.get("model_artifact", ""),
    }
    rows.append(reg_row)

    for target, payload in classification_champions.items():
        champion_model = payload["champion_model"]
        validation = classification[(classification["Target"] == target) & (classification["Split"] == "validation")].copy()
        champion_validation = metric_row(classification, Target=target, Model=champion_model, Split="validation")
        tied = validation[
            np.isclose(validation["Macro_F1"].astype(float), float(champion_validation["Macro_F1"]))
            & np.isclose(validation["Accuracy"].astype(float), float(champion_validation["Accuracy"]))
            & np.isclose(validation["ROC_AUC"].astype(float), float(champion_validation["ROC_AUC"]))
        ]["Model"].tolist()

        rows.append(
            {
                "Task": "Classification",
                "Target": target,
                "Champion_Model": champion_model,
                "Selection_Metric": "maximum validation macro F1",
                "Validation_Primary": champion_validation["Macro_F1"],
                "Validation_Secondary": champion_validation["Accuracy"],
                "Validation_Tertiary": champion_validation["ROC_AUC"],
                "Test_Primary": metric_row(classification, Target=target, Model=champion_model, Split="test")["Macro_F1"],
                "Holdout_Primary": metric_row(
                    classification,
                    Target=target,
                    Model=champion_model,
                    Split="holdout_rahimabad",
                )["Macro_F1"],
                "Primary_Metric_Name": "Macro_F1",
                "Secondary_Metric_Name": "Accuracy",
                "Tertiary_Metric_Name": "ROC_AUC",
                "Validation_Tie_Models": ", ".join(tied),
                "Model_Artifact": payload.get("model_artifact", ""),
            }
        )

    return pd.DataFrame(rows)


def build_rahimabad_summary(
    regression: pd.DataFrame,
    regression_champion: dict[str, Any],
    classification: pd.DataFrame,
    classification_champions: dict[str, Any],
    rahimabad_rows: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    champion_regression_model = regression_champion["champion_model"]
    reg_champion = metric_row(regression, Model=champion_regression_model, Split="holdout_rahimabad")
    reg_best = regression[regression["Split"] == "holdout_rahimabad"].sort_values("RMSE").iloc[0]
    rows.append(
        {
            "Task": "Regression",
            "Target": "Mango_Yield",
            "Model": champion_regression_model,
            "Model_Role": "validation champion",
            "Rahimabad_Rows": rahimabad_rows,
            "Primary_Metric": "RMSE",
            "Primary_Value": reg_champion["RMSE"],
            "Secondary_Metric": "MAE",
            "Secondary_Value": reg_champion["MAE"],
            "Additional_Metric": "R2",
            "Additional_Value": reg_champion["R2"],
        }
    )
    rows.append(
        {
            "Task": "Regression",
            "Target": "Mango_Yield",
            "Model": reg_best["Model"],
            "Model_Role": "best Rahimabad RMSE",
            "Rahimabad_Rows": rahimabad_rows,
            "Primary_Metric": "RMSE",
            "Primary_Value": reg_best["RMSE"],
            "Secondary_Metric": "MAE",
            "Secondary_Value": reg_best["MAE"],
            "Additional_Metric": "R2",
            "Additional_Value": reg_best["R2"],
        }
    )

    for target, payload in classification_champions.items():
        model = payload["champion_model"]
        row = metric_row(classification, Target=target, Model=model, Split="holdout_rahimabad")
        rows.append(
            {
                "Task": "Classification",
                "Target": target,
                "Model": model,
                "Model_Role": "validation champion",
                "Rahimabad_Rows": rahimabad_rows,
                "Primary_Metric": "Macro_F1",
                "Primary_Value": row["Macro_F1"],
                "Secondary_Metric": "Accuracy",
                "Secondary_Value": row["Accuracy"],
                "Additional_Metric": "ROC_AUC",
                "Additional_Value": row["ROC_AUC"],
            }
        )

    return pd.DataFrame(rows)


def build_reported_vs_reproduced(
    regression: pd.DataFrame,
    regression_champion: dict[str, Any],
    classification: pd.DataFrame,
    classification_champions: dict[str, Any],
    rahimabad_rows: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    yield_model_map = {
        "SVM": "Linear_SVR",
        "Random Forest": "Random_Forest",
        "Gradient Boosting": "Gradient_Boosting",
        "MLP": "MLP_Regressor",
    }
    yield_reported = {
        "SVM": 1.97,
        "Random Forest": 1.96,
        "Gradient Boosting": 1.94,
        "MLP": 3.05,
    }
    for reported_model, reported_rmse in yield_reported.items():
        reproduced_model = yield_model_map[reported_model]
        reproduced_rmse = float(metric_row(regression, Model=reproduced_model, Split="validation")["RMSE"])
        add_numeric_reconciliation(
            rows,
            "Yield prediction",
            f"{reported_model} RMSE",
            reported_model,
            reproduced_model,
            "RMSE",
            reported_rmse,
            reproduced_rmse,
            "validation",
            "Existing report did not specify a split; validation split is used for model-comparison reconciliation.",
        )

    add_text_reconciliation(
        rows,
        "Yield prediction",
        "Champion",
        "Gradient Boosting",
        regression_champion["champion_model"],
        "validation",
        "Verified champion is selected by minimum validation RMSE.",
    )

    disease_target = "Disease_Risk"
    disease_claims = [
        ("SVM accuracy", "SVM", "Linear_SVM", 95.8, "Accuracy_Percent"),
        (
            "MLP plus hybrid rules accuracy",
            "MLP plus hybrid rules",
            "Hybrid_Rule_Guided_GB",
            95.3,
            "Accuracy_Percent",
        ),
        ("Random Forest accuracy", "Random Forest", "Random_Forest", 98.4, "Accuracy_Percent"),
        ("Gradient Boosting accuracy", "Gradient Boosting", "Gradient_Boosting", 99.2, "Accuracy_Percent"),
    ]
    for claim_item, reported_model, reproduced_model, reported_value, metric in disease_claims:
        reproduced_value = percent(
            metric_row(classification, Target=disease_target, Model=reproduced_model, Split="validation")["Accuracy"]
        )
        note = "Existing report did not specify a split; validation split is used for model-comparison reconciliation."
        if reported_model == "MLP plus hybrid rules":
            note += " No exact MLP-plus-rules artifact exists; mapped to the implemented hybrid rule-guided model."
        add_numeric_reconciliation(
            rows,
            "Disease-risk classification",
            claim_item,
            reported_model,
            reproduced_model,
            metric,
            reported_value,
            reproduced_value,
            "validation",
            note,
        )

    add_text_reconciliation(
        rows,
        "Disease-risk classification",
        "Champion",
        "Gradient Boosting",
        classification_champions[disease_target]["champion_model"],
        "validation",
        "Verified champion is selected by maximum validation macro F1-score.",
    )

    add_numeric_reconciliation(
        rows,
        "Rahimabad geographic hold-out",
        "Rahimabad samples",
        "Rahimabad",
        "holdout_rahimabad",
        "Sample_Count",
        5059,
        rahimabad_rows,
        "holdout_rahimabad",
        "Row count from `data/processed/feature_table.csv`.",
    )

    regression_holdout = metric_row(
        regression,
        Model=regression_champion["champion_model"],
        Split="holdout_rahimabad",
    )
    add_numeric_reconciliation(
        rows,
        "Rahimabad geographic hold-out",
        "Yield RMSE",
        "reported hold-out model",
        regression_champion["champion_model"],
        "RMSE",
        1.93,
        float(regression_holdout["RMSE"]),
        "holdout_rahimabad",
        "Reproduced value uses the verified Phase 7.1 regression champion.",
    )

    disease_holdout = metric_row(
        classification,
        Target=disease_target,
        Model=classification_champions[disease_target]["champion_model"],
        Split="holdout_rahimabad",
    )
    add_numeric_reconciliation(
        rows,
        "Rahimabad geographic hold-out",
        "Disease risk accuracy",
        "reported hold-out model",
        classification_champions[disease_target]["champion_model"],
        "Accuracy_Percent",
        99.53,
        percent(disease_holdout["Accuracy"]),
        "holdout_rahimabad",
        "Reproduced value uses the verified Phase 7.2 Disease_Risk champion.",
    )
    add_numeric_reconciliation(
        rows,
        "Rahimabad geographic hold-out",
        "Disease risk macro F1",
        "reported hold-out model",
        classification_champions[disease_target]["champion_model"],
        "Macro_F1",
        0.9952,
        float(disease_holdout["Macro_F1"]),
        "holdout_rahimabad",
        "Reproduced value uses the verified Phase 7.2 Disease_Risk champion.",
    )

    return pd.DataFrame(rows)


def build_artifact_manifest() -> pd.DataFrame:
    groups = [
        ("script", PROJECT_ROOT / "src" / "modeling", "phase7_*.py"),
        ("model", PROJECT_ROOT / "outputs" / "models" / "regression", "*"),
        ("model", PROJECT_ROOT / "outputs" / "models" / "classification", "*"),
        ("metric", PROJECT_ROOT / "outputs" / "metrics" / "regression", "*"),
        ("metric", PROJECT_ROOT / "outputs" / "metrics" / "classification", "*"),
        ("metric", OUTPUT_METRICS_DIR, "*"),
        ("prediction", PROJECT_ROOT / "outputs" / "predictions" / "regression", "*"),
        ("prediction", PROJECT_ROOT / "outputs" / "predictions" / "classification", "*"),
        ("report", PROJECT_ROOT / "outputs" / "reports" / "phase7_regression", "*"),
        ("report", PROJECT_ROOT / "outputs" / "reports" / "phase7_classification", "*"),
        ("report", OUTPUT_REPORT_DIR, "*"),
    ]
    rows = []
    for artifact_type, directory, pattern in groups:
        if not directory.exists():
            continue
        for path in sorted(directory.glob(pattern)):
            if path.is_dir():
                continue
            rows.append(
                {
                    "Artifact_Type": artifact_type,
                    "Path": str(path.relative_to(PROJECT_ROOT)),
                    "File_Extension": path.suffix,
                    "Size_Bytes": int(path.stat().st_size),
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
    champion_summary: pd.DataFrame,
    reported_vs_reproduced: pd.DataFrame,
    rahimabad_summary: pd.DataFrame,
    artifact_manifest: pd.DataFrame,
    regression: pd.DataFrame,
    classification: pd.DataFrame,
) -> None:
    validation_regression = regression[regression["Split"] == "validation"].sort_values("RMSE")
    validation_classification = classification[classification["Split"] == "validation"].sort_values(
        ["Target", "Macro_F1", "Accuracy"],
        ascending=[True, False, False],
    )

    lines = [
        "# Phase 7.3 Complete Model Results and Reproducibility Report",
        "",
        "Generated by `src/modeling/phase7_3_compile_model_results.py`.",
        "",
        "## Purpose",
        "",
        "Phase 7.3 closes the model-development reporting gap identified in `Detailed_Research_Work_Outline.md`: the earlier narrative report listed model results but did not include the code, trained models, or evaluation outputs needed to verify them.",
        "",
        "This report uses the verified outputs from Phase 7.1 regression and Phase 7.2 classification.",
        "",
        "## Champion Summary",
        "",
        dataframe_to_markdown(champion_summary),
        "",
        "## Reported vs Reproduced Results",
        "",
        dataframe_to_markdown(reported_vs_reproduced),
        "",
        "Assessment meanings:",
        "",
        "- `matched`: reproduced value agrees within the configured tolerance.",
        "- `near`: reproduced value is close but not exact.",
        "- `different`: reproduced result materially differs or the reported champion differs.",
        "",
        "## Rahimabad Hold-Out Summary",
        "",
        dataframe_to_markdown(rahimabad_summary),
        "",
        "## Verified Regression Validation Ranking",
        "",
        dataframe_to_markdown(validation_regression[["Model", "Rows", "RMSE", "MAE", "R2"]]),
        "",
        "## Verified Classification Validation Ranking",
        "",
        dataframe_to_markdown(
            validation_classification[
                ["Target", "Model", "Rows", "Accuracy", "Precision_Macro", "Recall_Macro", "Macro_F1", "ROC_AUC"]
            ]
        ),
        "",
        "## Reproducibility Artifacts",
        "",
        f"- Artifact manifest: `{ARTIFACT_MANIFEST_CSV.relative_to(PROJECT_ROOT)}`",
        f"- Champion summary: `{CHAMPION_SUMMARY_CSV.relative_to(PROJECT_ROOT)}`",
        f"- Reported-vs-reproduced table: `{REPORTED_VS_REPRODUCED_CSV.relative_to(PROJECT_ROOT)}`",
        f"- Rahimabad hold-out summary: `{RAHIMABAD_SUMMARY_CSV.relative_to(PROJECT_ROOT)}`",
        f"- Machine-readable summary: `{SUMMARY_JSON.relative_to(PROJECT_ROOT)}`",
        "",
        "Artifact counts:",
        "",
        dataframe_to_markdown(artifact_manifest.groupby("Artifact_Type").size().reset_index(name="Count")),
        "",
        "## Caveats",
        "",
        "- The current dataset is synthetic prototype data.",
        "- `Nutrient_Availability` currently contains `Optimal` and `High`; no `Deficient` rows are present.",
        "- Existing-report claims did not always specify a split, so validation metrics are used for model-comparison reconciliation and Rahimabad metrics are used for the geographic hold-out claims.",
        "- Phase 8 should explain the verified champions using XAI and check whether dominant predictors are agronomically meaningful.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    require_files([REGRESSION_METRICS, REGRESSION_CHAMPION, CLASSIFICATION_METRICS, CLASSIFICATION_CHAMPIONS, FEATURE_TABLE])

    regression = pd.read_csv(REGRESSION_METRICS)
    classification = pd.read_csv(CLASSIFICATION_METRICS)
    regression_champion = load_json(REGRESSION_CHAMPION)
    classification_champions = load_json(CLASSIFICATION_CHAMPIONS)
    feature_table = pd.read_csv(FEATURE_TABLE, usecols=["Split"])
    rahimabad_rows = int((feature_table["Split"] == "holdout_rahimabad").sum())

    champion_summary = build_champion_summary(
        regression,
        regression_champion,
        classification,
        classification_champions,
    )
    rahimabad_summary = build_rahimabad_summary(
        regression,
        regression_champion,
        classification,
        classification_champions,
        rahimabad_rows,
    )
    reported_vs_reproduced = build_reported_vs_reproduced(
        regression,
        regression_champion,
        classification,
        classification_champions,
        rahimabad_rows,
    )

    champion_summary.to_csv(CHAMPION_SUMMARY_CSV, index=False)
    rahimabad_summary.to_csv(RAHIMABAD_SUMMARY_CSV, index=False)
    reported_vs_reproduced.to_csv(REPORTED_VS_REPRODUCED_CSV, index=False)

    summary = {
        "phase": "7.3",
        "status": "complete",
        "source_metrics": {
            "regression": str(REGRESSION_METRICS.relative_to(PROJECT_ROOT)),
            "classification": str(CLASSIFICATION_METRICS.relative_to(PROJECT_ROOT)),
        },
        "champions": {
            "Mango_Yield": regression_champion["champion_model"],
            **{target: payload["champion_model"] for target, payload in classification_champions.items()},
        },
        "rahimabad_rows": rahimabad_rows,
        "reported_claims_total": int(len(reported_vs_reproduced)),
        "reported_claims_matched": int((reported_vs_reproduced["Assessment"] == "matched").sum()),
        "reported_claims_near": int((reported_vs_reproduced["Assessment"] == "near").sum()),
        "reported_claims_different": int((reported_vs_reproduced["Assessment"] == "different").sum()),
        "outputs": {
            "champion_summary": str(CHAMPION_SUMMARY_CSV.relative_to(PROJECT_ROOT)),
            "reported_vs_reproduced": str(REPORTED_VS_REPRODUCED_CSV.relative_to(PROJECT_ROOT)),
            "rahimabad_summary": str(RAHIMABAD_SUMMARY_CSV.relative_to(PROJECT_ROOT)),
            "artifact_manifest": str(ARTIFACT_MANIFEST_CSV.relative_to(PROJECT_ROOT)),
            "report": str(REPORT_MD.relative_to(PROJECT_ROOT)),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    artifact_manifest = build_artifact_manifest()
    artifact_manifest.to_csv(ARTIFACT_MANIFEST_CSV, index=False)
    write_report(champion_summary, reported_vs_reproduced, rahimabad_summary, artifact_manifest, regression, classification)

    print("Phase 7.3 model-results reporting complete.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

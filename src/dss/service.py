"""Shared prediction, explanation, and recommendation service for Phase 9."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_TABLE = PROJECT_ROOT / "data" / "processed" / "feature_table.csv"
SELECTED_FEATURES_JSON = PROJECT_ROOT / "data" / "processed" / "selected_features.json"

YIELD_MODEL = PROJECT_ROOT / "outputs" / "models" / "regression" / "champion_regression_model.joblib"
DISEASE_MODEL = PROJECT_ROOT / "outputs" / "models" / "classification" / "champion_disease_risk_model.joblib"
NUTRIENT_MODEL = PROJECT_ROOT / "outputs" / "models" / "classification" / "champion_nutrient_availability_model.joblib"
PHASE7_SUMMARY = PROJECT_ROOT / "outputs" / "metrics" / "phase7_model_results" / "phase7_model_results_summary.json"

GLOBAL_IMPORTANCE = PROJECT_ROOT / "outputs" / "explainability" / "phase8_xai" / "tables" / "phase8_global_feature_importance.csv"
DEPENDENCE_THRESHOLDS = PROJECT_ROOT / "outputs" / "explainability" / "phase8_xai" / "tables" / "phase8_shap_dependence_thresholds.csv"
RECOMMENDATION_RULES = PROJECT_ROOT / "outputs" / "explainability" / "phase8_xai" / "tables" / "phase8_recommendation_rules.csv"
PHASE8_REPORT = PROJECT_ROOT / "outputs" / "reports" / "phase8_explainable_ai" / "phase8_explainable_ai_report.md"


class DSSInput(BaseModel):
    """Input schema for the local DSS prediction endpoint."""

    Sample_ID: str | None = Field(default=None, description="Optional orchard or sample identifier.")
    NPK_Balance_Score_Phase6: float
    Diversity_Score_Phase6: float
    Soil_Health_Index_Phase6: float
    Beneficial_Microbial_Index_Phase6: float
    Pathogen_Load_Index_Phase6: float
    Soil_Chemical_Fertility_Score_Phase6: float
    Biocontrol_Index_Phase6: float
    Nutrient_Cycling_Index_Phase6: float
    Soil_Physical_Condition_Score_Phase6: float
    Pathogen_Beneficial_Ratio_Phase6: float
    Available_P: float
    Available_K: float
    Total_Nitrogen: float
    Climate_Comfort_Score_Phase6: float
    EC: float
    pH: float
    Tree_Age: float
    Trichoderma: float
    Organic_Carbon: float
    Pseudomonas_PGPR: float
    Micronutrient_Balance_Score_Phase6: float
    Pathogen_Load_Index: float
    Nutrient_Balance_Ratio: float
    Soil_Health_Index: float
    Microbial_Richness_Score: float
    Shannon_Index: float
    Pielou_Evenness: float
    Simpson_Index: float
    Richness_Evenness_Balance_Phase6: float
    Rainfall: float
    Mycorrhizae_AMF: float
    Air_Temp_Avg: float
    Euryarchaeota: float
    Mn: float
    Village: str
    Mango_Variety: str
    Soil_Depth: str
    Sampling_Season: str
    Management: str
    Fusarium: float | None = Field(
        default=None,
        description="Optional contextual pathogen feature used by Phase 8 recommendation rules.",
    )

    class Config:
        extra = "forbid"


class DSSService:
    """Loads Phase 7/8 artifacts and serves predictions plus explanations."""

    def __init__(self) -> None:
        self.selected = json.loads(SELECTED_FEATURES_JSON.read_text(encoding="utf-8"))
        self.numeric_features: list[str] = self.selected["selected_numeric_features"]
        self.categorical_features: list[str] = self.selected["categorical_features_for_encoding"]
        self.model_features = self.numeric_features + self.categorical_features

        self.feature_table = pd.read_csv(FEATURE_TABLE)
        self.train_table = self.feature_table[self.feature_table["Split"] == "train"].copy()

        self.yield_model = joblib.load(YIELD_MODEL)
        self.disease_model = joblib.load(DISEASE_MODEL)
        self.nutrient_model = joblib.load(NUTRIENT_MODEL)

        self.global_importance = pd.read_csv(GLOBAL_IMPORTANCE)
        self.dependence = pd.read_csv(DEPENDENCE_THRESHOLDS)
        self.rules = pd.read_csv(RECOMMENDATION_RULES)
        self.phase7_summary = json.loads(PHASE7_SUMMARY.read_text(encoding="utf-8")) if PHASE7_SUMMARY.exists() else {}

        self.numeric_ranges = self._build_numeric_ranges()
        self.categorical_options = {
            col: sorted(self.feature_table[col].dropna().astype(str).unique().tolist())
            for col in self.categorical_features
        }
        self.default_input = self._build_default_input()

    def _build_numeric_ranges(self) -> dict[str, dict[str, float]]:
        ranges: dict[str, dict[str, float]] = {}
        for col in self.numeric_features:
            series = self.feature_table[col].astype(float)
            ranges[col] = {
                "min": float(series.min()),
                "q25": float(series.quantile(0.25)),
                "median": float(series.median()),
                "q75": float(series.quantile(0.75)),
                "max": float(series.max()),
            }
        if "Fusarium" in self.feature_table.columns:
            series = self.feature_table["Fusarium"].astype(float)
            ranges["Fusarium"] = {
                "min": float(series.min()),
                "q25": float(series.quantile(0.25)),
                "median": float(series.median()),
                "q75": float(series.quantile(0.75)),
                "max": float(series.max()),
            }
        return ranges

    def _build_default_input(self) -> dict[str, Any]:
        defaults: dict[str, Any] = {"Sample_ID": "DSS-example"}
        for feature in self.numeric_features:
            defaults[feature] = self.numeric_ranges[feature]["median"]
        for feature in self.categorical_features:
            defaults[feature] = self.feature_table[feature].mode().iloc[0]
        if "Fusarium" in self.numeric_ranges:
            defaults["Fusarium"] = self.numeric_ranges["Fusarium"]["median"]
        return defaults

    def input_to_payload(self, data: DSSInput | dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, DSSInput):
            if hasattr(data, "model_dump"):
                return data.model_dump()
            return data.dict()
        return dict(data)

    def input_to_frame(self, data: DSSInput | dict[str, Any]) -> pd.DataFrame:
        payload = self.input_to_payload(data)
        missing = [feature for feature in self.model_features if feature not in payload]
        if missing:
            raise ValueError(f"Missing DSS model input features: {missing}")
        return pd.DataFrame([{feature: payload[feature] for feature in self.model_features}])

    def _class_prediction(self, model: Any, x: pd.DataFrame) -> dict[str, Any]:
        predicted = str(model.predict(x)[0])
        classes = [str(label) for label in model.named_steps["model"].classes_]
        probabilities = model.predict_proba(x)[0]
        probability_map = {label: float(probabilities[index]) for index, label in enumerate(classes)}
        return {
            "class": predicted,
            "probabilities": probability_map,
            "confidence": float(max(probabilities)),
        }

    def predict(self, data: DSSInput | dict[str, Any]) -> dict[str, Any]:
        payload = self.input_to_payload(data)
        x = self.input_to_frame(payload)

        yield_prediction = float(self.yield_model.predict(x)[0])
        disease = self._class_prediction(self.disease_model, x)
        nutrient = self._class_prediction(self.nutrient_model, x)
        explanations = {
            "Mango_Yield": self.explain_target("Mango_Yield", payload),
            "Disease_Risk": self.explain_target("Disease_Risk", payload),
            "Nutrient_Availability": self.explain_target("Nutrient_Availability", payload),
        }
        recommendations = self.generate_recommendations(payload)

        return {
            "sample_id": payload.get("Sample_ID"),
            "predictions": {
                "Mango_Yield": {
                    "value": yield_prediction,
                    "unit": "kg_per_tree",
                    "model": "Linear_Regression",
                },
                "Disease_Risk": {
                    "model": "Gradient_Boosting",
                    **disease,
                },
                "Nutrient_Availability": {
                    "model": "Random_Forest",
                    **nutrient,
                },
            },
            "explanations": explanations,
            "recommendations": recommendations,
            "reference_artifacts": self.reference_artifacts(),
            "caveat": "Synthetic prototype model output. Validate with field observations before agronomic action.",
        }

    def explain_target(self, target: str, payload: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
        shap_rows = self.global_importance[
            (self.global_importance["Target"] == target)
            & (self.global_importance["Importance_Type"] == "SHAP_Mean_Abs_Aggregated")
        ].sort_values("Rank")
        out: list[dict[str, Any]] = []
        for _, row in shap_rows.head(limit).iterrows():
            feature = str(row["Original_Feature"])
            value = payload.get(feature)
            dependence = self.dependence[
                (self.dependence["Target"] == target) & (self.dependence["Feature"] == feature)
            ]
            signal = "contextual"
            threshold_text = ""
            if not dependence.empty:
                dep = dependence.iloc[0]
                threshold_text = f"Q25={dep['Q25']:.4g}, median={dep['Median']:.4g}, Q75={dep['Q75']:.4g}"
                delta = float(dep["High_Minus_Low_SHAP"])
                if delta > 0:
                    signal = "higher values increase the explained output in Phase 8 dependence diagnostics"
                elif delta < 0:
                    signal = "higher values decrease the explained output in Phase 8 dependence diagnostics"
                else:
                    signal = "flat or weak dependence in Phase 8 diagnostics"
            elif feature in self.numeric_ranges:
                threshold_text = f"median={self.numeric_ranges[feature]['median']:.4g}"
            out.append(
                {
                    "rank": int(row["Rank"]),
                    "feature": feature,
                    "input_value": None if value is None else value,
                    "importance": float(row["Importance"]),
                    "mean_shap": None if pd.isna(row.get("Mean_SHAP")) else float(row.get("Mean_SHAP")),
                    "diagnostic_thresholds": threshold_text,
                    "interpretation": signal,
                }
            )
        return out

    def generate_recommendations(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        for _, rule in self.rules.iterrows():
            feature = str(rule["Feature"])
            if feature not in payload or payload.get(feature) is None:
                continue
            value = float(payload[feature])
            threshold = float(rule["Threshold"])
            comparator = str(rule["Comparator"])
            triggered = value <= threshold if comparator == "<=" else value >= threshold
            if triggered:
                recommendations.append(
                    {
                        "rule_id": str(rule["Rule_ID"]),
                        "target": str(rule["Target"]),
                        "feature": feature,
                        "feature_value": value,
                        "condition": f"{feature} {comparator} {threshold:.4g}",
                        "recommendation": str(rule["Recommendation"]),
                        "xai_support": str(rule["XAI_Support"]),
                    }
                )
        if not recommendations:
            recommendations.append(
                {
                    "rule_id": "NO_RULE_TRIGGERED",
                    "target": "Overall",
                    "feature": "",
                    "feature_value": None,
                    "condition": "No Phase 8 rule threshold triggered",
                    "recommendation": "Maintain monitoring and validate predictions with current soil tests and orchard observations.",
                    "xai_support": "No high-priority threshold rule fired for this input.",
                }
            )
        return recommendations

    def metadata(self) -> dict[str, Any]:
        return {
            "project": "Hybrid AI with Explainable AI for Mango Crop Soil Microbiome DSS",
            "required_numeric_features": self.numeric_features,
            "required_categorical_features": self.categorical_features,
            "optional_context_features": ["Fusarium"],
            "numeric_ranges": self.numeric_ranges,
            "categorical_options": self.categorical_options,
            "default_input": self.default_input,
            "champions": self.phase7_summary.get("champions", {}),
            "artifacts": self.reference_artifacts(),
        }

    def reference_artifacts(self) -> dict[str, str]:
        return {
            "phase8_report": str(PHASE8_REPORT.relative_to(PROJECT_ROOT)),
            "global_importance": str(GLOBAL_IMPORTANCE.relative_to(PROJECT_ROOT)),
            "dependence_thresholds": str(DEPENDENCE_THRESHOLDS.relative_to(PROJECT_ROOT)),
            "recommendation_rules": str(RECOMMENDATION_RULES.relative_to(PROJECT_ROOT)),
        }

    def export_markdown_report(self, prediction: dict[str, Any]) -> str:
        preds = prediction["predictions"]
        lines = [
            "# Mango Orchard DSS Prediction Report",
            "",
            f"Sample ID: `{prediction.get('sample_id') or 'not provided'}`",
            "",
            "## Predictions",
            "",
            f"- Mango yield: `{preds['Mango_Yield']['value']:.3f}` kg/tree",
            f"- Disease risk: `{preds['Disease_Risk']['class']}` "
            f"(confidence `{preds['Disease_Risk']['confidence']:.3f}`)",
            f"- Nutrient availability: `{preds['Nutrient_Availability']['class']}` "
            f"(confidence `{preds['Nutrient_Availability']['confidence']:.3f}`)",
            "",
            "## Recommendations",
            "",
        ]
        for rec in prediction["recommendations"]:
            lines.append(f"- `{rec['rule_id']}`: {rec['recommendation']}")
        lines.extend(["", "## Caveat", "", prediction["caveat"]])
        return "\n".join(lines) + "\n"


@lru_cache(maxsize=1)
def get_service() -> DSSService:
    return DSSService()

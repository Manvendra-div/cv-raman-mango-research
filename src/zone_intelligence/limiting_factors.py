"""Limiting factor identification.

Ranks soil, microbiome, and management factors that may be limiting
yield for a given orchard by combining three independent evidence
sources:

1. **Measured deficiency** — value below a validated reference range.
2. **Model attribution** — negative SHAP contribution to predicted
   yield.
3. **Peer comparison** — value below the median of high-performing
   comparable orchards.

Each factor is labelled with its evidence level so the farmer and
agronomist can distinguish confirmed deficiencies from model-inferred
hypotheses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


class EvidenceLevel(str, Enum):
    MEASURED_DEFICIENCY = "measured_deficiency"
    MODEL_ASSOCIATED = "model_associated"
    PEER_COMPARISON = "peer_comparison"
    COMBINED = "combined"
    UNVERIFIED = "unverified"


# Agronomically validated reference ranges for mango soils.
# Sources: Indian Council of Agricultural Research (ICAR) general
# soil-fertility ratings adapted for subtropical perennial horticulture.
# These are approximate — local calibration is always preferred.
REFERENCE_RANGES: Dict[str, Dict[str, float]] = {
    "pH":               {"low": 6.0, "high": 7.5, "unit": "-"},
    "EC":               {"low": 0.0, "high": 0.8, "unit": "dS/m"},
    "Organic_Carbon":   {"low": 0.5, "high": 0.9, "unit": "%"},
    "Total_Nitrogen":   {"low": 250, "high": 400, "unit": "kg/ha"},
    "Available_P":      {"low": 12,  "high": 30,  "unit": "kg/ha"},
    "Available_K":      {"low": 150, "high": 350, "unit": "kg/ha"},
    "Zn":               {"low": 0.6, "high": 2.0, "unit": "mg/kg"},
    "Fe":               {"low": 5.0, "high": 20,  "unit": "mg/kg"},
    "Mn":               {"low": 2.0, "high": 10,  "unit": "mg/kg"},
    "Cu":               {"low": 0.5, "high": 3.0, "unit": "mg/kg"},
    "CEC":              {"low": 10,  "high": 25,  "unit": "cmol/kg"},
    "Soil_Moisture":    {"low": 12,  "high": 30,  "unit": "%"},
    "Pathogen_Load_Index": {"low": 0, "high": 0.5, "unit": "index 0–1"},
}


@dataclass
class LimitingFactor:
    """A single potentially limiting factor."""

    feature: str
    measured_value: float
    evidence_level: EvidenceLevel
    evidence_sources: List[str]
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    peer_median: Optional[float] = None
    shap_contribution: Optional[float] = None
    unit: str = ""
    recommendation: str = ""
    confidence: str = "low"

    def severity_score(self) -> float:
        score = 0.0
        if self.reference_low is not None and self.measured_value < self.reference_low:
            score += 2.0
        if self.peer_median is not None and self.measured_value < self.peer_median:
            score += 1.0
        if self.shap_contribution is not None and self.shap_contribution < 0:
            score += abs(self.shap_contribution)
        return score


class LimitingFactorAnalyzer:
    """Identify and rank factors potentially limiting orchard yield."""

    def analyze(
        self,
        sample: Dict[str, float],
        *,
        shap_contributions: Optional[Dict[str, float]] = None,
        peer_medians: Optional[Dict[str, float]] = None,
    ) -> List[LimitingFactor]:
        """Return limiting factors sorted by severity (worst first)."""
        factors: List[LimitingFactor] = []

        for feature, ref in REFERENCE_RANGES.items():
            if feature not in sample:
                continue

            value = sample[feature]
            sources: List[str] = []
            evidence = EvidenceLevel.UNVERIFIED
            confidence = "low"

            # Evidence 1: measured deficiency
            is_deficient = value < ref["low"]
            is_excess = feature == "Pathogen_Load_Index" and value > ref["high"]
            if is_deficient or is_excess:
                sources.append("measured_deficiency")

            # Evidence 2: model attribution
            shap_val: Optional[float] = None
            if shap_contributions and feature in shap_contributions:
                shap_val = shap_contributions[feature]
                if shap_val < 0:
                    sources.append("model_negative_contribution")

            # Evidence 3: peer comparison
            peer_med: Optional[float] = None
            if peer_medians and feature in peer_medians:
                peer_med = peer_medians[feature]
                if feature == "Pathogen_Load_Index":
                    if value > peer_med:
                        sources.append("above_peer_median")
                elif value < peer_med:
                    sources.append("below_peer_median")

            if not sources:
                continue

            if len(sources) >= 3:
                evidence = EvidenceLevel.COMBINED
                confidence = "high"
            elif len(sources) == 2:
                evidence = EvidenceLevel.COMBINED
                confidence = "moderate"
            elif "measured_deficiency" in sources:
                evidence = EvidenceLevel.MEASURED_DEFICIENCY
                confidence = "moderate"
            elif "model_negative_contribution" in sources:
                evidence = EvidenceLevel.MODEL_ASSOCIATED
                confidence = "low"
            else:
                evidence = EvidenceLevel.PEER_COMPARISON
                confidence = "low"

            factor = LimitingFactor(
                feature=feature,
                measured_value=round(value, 4),
                evidence_level=evidence,
                evidence_sources=sources,
                reference_low=ref["low"],
                reference_high=ref["high"],
                peer_median=round(peer_med, 4) if peer_med is not None else None,
                shap_contribution=round(shap_val, 6) if shap_val is not None else None,
                unit=ref.get("unit", ""),
                recommendation=self._recommend(feature, value, ref, sources),
                confidence=confidence,
            )
            factors.append(factor)

        factors.sort(key=lambda f: f.severity_score(), reverse=True)
        return factors

    def peer_medians_from_match(
        self, matched_samples: pd.DataFrame
    ) -> Dict[str, float]:
        """Compute median values from comparable orchards."""
        medians: Dict[str, float] = {}
        for feature in REFERENCE_RANGES:
            if feature in matched_samples.columns:
                medians[feature] = float(matched_samples[feature].median())
        return medians

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    @staticmethod
    def _recommend(
        feature: str, value: float, ref: Dict[str, float], sources: List[str]
    ) -> str:
        is_deficient = value < ref["low"]
        is_pathogen_excess = (
            feature == "Pathogen_Load_Index" and value > ref["high"]
        )

        n_sources = len(sources)
        qualifier = (
            "Multiple evidence sources suggest"
            if n_sources >= 2
            else "Preliminary evidence suggests"
        )

        if feature == "Pathogen_Load_Index" and is_pathogen_excess:
            return (
                f"{qualifier} elevated pathogen pressure "
                f"(measured {value:.2f}, reference threshold {ref['high']}). "
                "Inspect roots and canopy for disease symptoms and "
                "consult a local plant pathologist before intervention."
            )

        if is_deficient:
            return (
                f"{qualifier} potentially low {feature.replace('_', ' ')} "
                f"(measured {value:.2f} {ref.get('unit', '')}, "
                f"reference threshold {ref['low']} {ref.get('unit', '')}). "
                "Confirm with a soil test and consult a qualified local "
                "agronomist regarding appropriate management."
            )

        return (
            f"{qualifier} {feature.replace('_', ' ')} "
            f"({value:.2f} {ref.get('unit', '')}) may be contributing to "
            "reduced performance relative to comparable orchards. "
            "Verify with targeted measurement before intervention."
        )

    @staticmethod
    def to_dict(factor: LimitingFactor) -> Dict[str, Any]:
        return {
            "feature": factor.feature,
            "measured_value": factor.measured_value,
            "evidence_level": factor.evidence_level.value,
            "evidence_sources": factor.evidence_sources,
            "reference_low": factor.reference_low,
            "reference_high": factor.reference_high,
            "peer_median": factor.peer_median,
            "shap_contribution": factor.shap_contribution,
            "unit": factor.unit,
            "recommendation": factor.recommendation,
            "confidence": factor.confidence,
            "severity_score": round(factor.severity_score(), 4),
        }

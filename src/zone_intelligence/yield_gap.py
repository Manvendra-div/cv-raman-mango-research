"""Yield gap analysis.

Computes the difference between predicted yield and a reference yield
benchmark derived from comparable orchards, expressed both in absolute
(kg/tree) and percentage terms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.zone_intelligence.reference_yield import ReferenceYield


@dataclass
class YieldGapResult:
    """Yield gap between predicted yield and a reference benchmark."""

    predicted_yield: float
    reference_yield: float
    reference_type: str   # e.g. "q75", "top10_mean", "median"
    gap_absolute: float   # kg/tree
    gap_percentage: float  # %
    interpretation: str
    warnings: List[str] = field(default_factory=list)


class YieldGapAnalyzer:
    """Calculate yield gaps relative to zone-level benchmarks.

    The *primary* reference is the 75th-percentile yield of comparable
    orchards — a realistic attainable benchmark.  The *aspirational*
    reference is the top-10 % mean.  Both are returned so the user can
    see the spread.
    """

    def analyze(
        self,
        predicted_yield: float,
        reference: ReferenceYield,
    ) -> Dict[str, YieldGapResult]:
        """Return gap results keyed by reference type."""
        results: Dict[str, YieldGapResult] = {}

        benchmarks = {
            "median": reference.median,
            "mean": reference.mean,
            "q75": reference.q75,
            "top10_mean": reference.top10_mean,
        }

        for ref_type, ref_value in benchmarks.items():
            results[ref_type] = self._compute_gap(
                predicted_yield,
                ref_value,
                ref_type,
                reference,
            )

        return results

    def primary_gap(
        self,
        predicted_yield: float,
        reference: ReferenceYield,
    ) -> YieldGapResult:
        """Return the gap relative to Q75 (practical attainable benchmark)."""
        return self._compute_gap(
            predicted_yield, reference.q75, "q75", reference
        )

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _compute_gap(
        self,
        predicted: float,
        ref_value: float,
        ref_type: str,
        reference: ReferenceYield,
    ) -> YieldGapResult:
        warnings: List[str] = list(reference.warnings)

        if ref_value <= 0:
            return YieldGapResult(
                predicted_yield=round(predicted, 2),
                reference_yield=0.0,
                reference_type=ref_type,
                gap_absolute=0.0,
                gap_percentage=0.0,
                interpretation="Reference yield unavailable or zero.",
                warnings=warnings + ["Reference yield is zero or missing."],
            )

        gap_abs = ref_value - predicted
        gap_pct = (gap_abs / ref_value) * 100

        interpretation = self._interpret(predicted, ref_value, gap_pct, ref_type)

        return YieldGapResult(
            predicted_yield=round(predicted, 2),
            reference_yield=round(ref_value, 2),
            reference_type=ref_type,
            gap_absolute=round(gap_abs, 2),
            gap_percentage=round(gap_pct, 1),
            interpretation=interpretation,
            warnings=warnings,
        )

    @staticmethod
    def _interpret(
        predicted: float, reference: float, gap_pct: float, ref_type: str
    ) -> str:
        label = {
            "median": "the median of comparable orchards",
            "mean": "the mean of comparable orchards",
            "q75": "the 75th-percentile of comparable orchards",
            "top10_mean": "the top-10% mean of comparable orchards",
        }.get(ref_type, ref_type)

        if gap_pct > 20:
            severity = "substantial"
        elif gap_pct > 10:
            severity = "moderate"
        elif gap_pct > 0:
            severity = "small"
        else:
            return (
                f"Predicted yield ({predicted:.1f} kg/tree) meets or "
                f"exceeds {label} ({reference:.1f} kg/tree). "
                "No yield gap relative to this benchmark."
            )

        return (
            f"Predicted yield ({predicted:.1f} kg/tree) is "
            f"{abs(gap_pct):.1f}% below {label} ({reference:.1f} kg/tree), "
            f"indicating a {severity} yield gap of {abs(predicted - reference):.1f} kg/tree."
        )

    @staticmethod
    def to_dict(result: YieldGapResult) -> Dict[str, Any]:
        return {
            "predicted_yield_kg_per_tree": result.predicted_yield,
            "reference_yield_kg_per_tree": result.reference_yield,
            "reference_type": result.reference_type,
            "gap_absolute_kg": result.gap_absolute,
            "gap_percentage": result.gap_percentage,
            "interpretation": result.interpretation,
            "warnings": result.warnings,
        }

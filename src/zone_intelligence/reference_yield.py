"""Reference yield calculation from comparable orchards.

Computes zone-level reference statistics (mean, median, upper quartile,
top-10 % yield) from matched comparable orchards so that a query
orchard's predicted yield can be contextualised.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.zone_intelligence.orchard_matching import MatchResult


@dataclass
class ReferenceYield:
    """Reference yield statistics for a set of comparable orchards."""

    mean: float
    median: float
    q75: float
    q90: float
    top10_mean: float
    std: float
    min: float
    max: float
    sample_count: int
    orchard_count: int
    source_description: str
    warnings: List[str]

    @property
    def has_sufficient_data(self) -> bool:
        return self.orchard_count >= 3 and self.sample_count >= 10


class ReferenceYieldCalculator:
    """Derive reference yield benchmarks from comparable orchards."""

    YIELD_COL = "Mango_Yield"

    def from_match_result(
        self,
        match: MatchResult,
        *,
        description_override: Optional[str] = None,
    ) -> ReferenceYield:
        yields = match.matched_samples[self.YIELD_COL]
        return self._compute(
            yields,
            orchard_count=match.match_count,
            description=description_override or self._describe_match(match),
            base_warnings=list(match.warnings),
        )

    def from_series(
        self,
        yields: pd.Series,
        *,
        orchard_count: int = 0,
        description: str = "custom",
    ) -> ReferenceYield:
        return self._compute(
            yields,
            orchard_count=orchard_count,
            description=description,
            base_warnings=[],
        )

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _compute(
        self,
        yields: pd.Series,
        *,
        orchard_count: int,
        description: str,
        base_warnings: List[str],
    ) -> ReferenceYield:
        warnings = list(base_warnings)

        if len(yields) == 0:
            warnings.append("No yield observations available for reference.")
            return ReferenceYield(
                mean=0.0, median=0.0, q75=0.0, q90=0.0,
                top10_mean=0.0, std=0.0, min=0.0, max=0.0,
                sample_count=0, orchard_count=0,
                source_description=description, warnings=warnings,
            )

        q75 = float(yields.quantile(0.75))
        q90 = float(yields.quantile(0.90))

        top10_threshold = float(yields.quantile(0.90))
        top10 = yields[yields >= top10_threshold]
        top10_mean = float(top10.mean()) if len(top10) > 0 else q90

        if orchard_count < 3:
            warnings.append(
                f"Only {orchard_count} comparable orchards found. "
                "Reference statistics may not be robust."
            )

        if orchard_count < 10:
            warnings.append(
                "Top-10% reference based on fewer than 10 orchards — "
                "interpret with caution."
            )

        return ReferenceYield(
            mean=float(yields.mean()),
            median=float(yields.median()),
            q75=q75,
            q90=q90,
            top10_mean=top10_mean,
            std=float(yields.std()),
            min=float(yields.min()),
            max=float(yields.max()),
            sample_count=len(yields),
            orchard_count=orchard_count,
            source_description=description,
            warnings=warnings,
        )

    @staticmethod
    def _describe_match(match: MatchResult) -> str:
        parts = []
        c = match.criteria_used
        if "village" in c:
            parts.append(f"Village={c['village']}")
        if "variety" in c:
            parts.append(f"Variety={c['variety']}")
        if "age_range" in c:
            lo, hi = c["age_range"]
            parts.append(f"Age={lo}–{hi}y")
        if "management" in c:
            parts.append(f"Mgmt={c['management']}")
        parts.append(f"tier={c.get('tier', '?')}")
        return "; ".join(parts)

    @staticmethod
    def to_dict(ref: ReferenceYield) -> Dict[str, Any]:
        return {
            "mean": round(ref.mean, 2),
            "median": round(ref.median, 2),
            "q75": round(ref.q75, 2),
            "q90": round(ref.q90, 2),
            "top10_mean": round(ref.top10_mean, 2),
            "std": round(ref.std, 2),
            "min": round(ref.min, 2),
            "max": round(ref.max, 2),
            "sample_count": ref.sample_count,
            "orchard_count": ref.orchard_count,
            "source_description": ref.source_description,
            "has_sufficient_data": ref.has_sufficient_data,
            "warnings": ref.warnings,
        }

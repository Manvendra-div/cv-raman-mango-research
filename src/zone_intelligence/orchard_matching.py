"""Comparable orchard matching.

Selects orchards that are comparable to a query orchard based on
village, variety, tree-age band, management type, and optionally
soil characteristics.  Returns matched observations along with
a transparency record of the criteria used and the match count.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


MIN_COMPARABLE_ORCHARDS = 3
MIN_COMPARABLE_SAMPLES = 10
AGE_BAND_WIDTH = 10  # years


@dataclass
class MatchResult:
    """Result of a comparable-orchard search."""

    matched_samples: pd.DataFrame
    matched_orchard_ids: List[str]
    match_count: int
    sample_count: int
    criteria_used: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)

    @property
    def sufficient(self) -> bool:
        return (
            self.match_count >= MIN_COMPARABLE_ORCHARDS
            and self.sample_count >= MIN_COMPARABLE_SAMPLES
        )


class OrchardMatcher:
    """Find orchards comparable to a query sample."""

    def __init__(self, dataset: pd.DataFrame) -> None:
        self._df = dataset.copy()

    def match(
        self,
        village: str,
        variety: str,
        tree_age: int,
        management: Optional[str] = None,
        *,
        exclude_orchard: Optional[str] = None,
        age_band: int = AGE_BAND_WIDTH,
        relax_on_insufficient: bool = True,
    ) -> MatchResult:
        """Find comparable orchards, relaxing criteria if needed.

        Matching tiers (applied in order, relaxing progressively):
          1. Village + Variety + Age band + Management
          2. Village + Variety + Age band  (drop management)
          3. Village + Variety             (drop age band)
          4. Village only                  (drop variety)

        If *relax_on_insufficient* is True the matcher walks down the
        tiers until a sufficient match is found.  Otherwise it returns
        whatever tier-1 produces (possibly insufficient).
        """
        age_lo = tree_age - age_band // 2
        age_hi = tree_age + age_band // 2

        tiers: List[Tuple[str, Dict[str, Any]]] = [
            (
                "village+variety+age+management",
                {"village": village, "variety": variety,
                 "age_range": (age_lo, age_hi), "management": management},
            ),
            (
                "village+variety+age",
                {"village": village, "variety": variety,
                 "age_range": (age_lo, age_hi), "management": None},
            ),
            (
                "village+variety",
                {"village": village, "variety": variety,
                 "age_range": None, "management": None},
            ),
            (
                "village",
                {"village": village, "variety": None,
                 "age_range": None, "management": None},
            ),
        ]

        for tier_name, criteria in tiers:
            result = self._apply_criteria(
                criteria, exclude_orchard=exclude_orchard, tier_name=tier_name
            )
            if result.sufficient or not relax_on_insufficient:
                return result

        # Even the broadest tier was insufficient — return with warning
        result.warnings.append(
            f"Insufficient comparable orchards even at broadest tier "
            f"(village={village}). Only {result.match_count} orchards "
            f"with {result.sample_count} samples found."
        )
        return result

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _apply_criteria(
        self,
        criteria: Dict[str, Any],
        *,
        exclude_orchard: Optional[str],
        tier_name: str,
    ) -> MatchResult:
        mask = pd.Series(True, index=self._df.index)

        if criteria.get("village"):
            mask &= self._df["Village"] == criteria["village"]

        if criteria.get("variety"):
            mask &= self._df["Mango_Variety"] == criteria["variety"]

        age_range = criteria.get("age_range")
        if age_range is not None:
            lo, hi = age_range
            mask &= self._df["Tree_Age"].between(lo, hi)

        if criteria.get("management"):
            mask &= self._df["Management"] == criteria["management"]

        if exclude_orchard:
            mask &= self._df["Orchard_ID"] != exclude_orchard

        matched = self._df[mask]
        orchard_ids = sorted(matched["Orchard_ID"].unique().tolist())

        warnings: List[str] = []
        if tier_name != "village+variety+age+management":
            warnings.append(
                f"Relaxed matching criteria to '{tier_name}' to find "
                f"sufficient comparables."
            )

        used_criteria = {k: v for k, v in criteria.items() if v is not None}
        used_criteria["tier"] = tier_name

        return MatchResult(
            matched_samples=matched,
            matched_orchard_ids=orchard_ids,
            match_count=len(orchard_ids),
            sample_count=len(matched),
            criteria_used=used_criteria,
            warnings=warnings,
        )

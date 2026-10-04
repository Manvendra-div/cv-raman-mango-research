"""Village and variety-level zone profiling.

Computes summary statistics for soil, microbiome, yield, and disease
risk at the village, variety, and management level so that individual
orchards can be compared against their geographical context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


# Feature groups used for profiling
SOIL_FEATURES = [
    "pH", "EC", "Organic_Carbon", "Total_Nitrogen", "Available_P",
    "Available_K", "Soil_Moisture", "CEC", "Zn", "Fe", "Mn", "Cu",
]

MICROBIOME_FEATURES = [
    "Shannon_Index", "Simpson_Index", "Pielou_Evenness", "OTU_Count",
    "Chao1_Richness",
]

FUNCTIONAL_FEATURES = [
    "Nitrogen_Fixers", "Phosphate_Solubilizers_PSB",
    "Potassium_Solubilizers", "Mycorrhizae_AMF", "Trichoderma",
    "Pseudomonas_PGPR", "Fusarium", "Pathogen_Load_Index",
]

ENGINEERED_FEATURES = [
    "Microbial_Richness_Score", "Nutrient_Balance_Ratio",
    "Soil_Health_Index",
]

TARGET_YIELD = "Mango_Yield"
TARGET_DISEASE = "Disease_Risk"
TARGET_NUTRIENT = "Nutrient_Availability"


@dataclass
class ProfileSummary:
    """Statistical summary for a group of observations."""

    group_key: Dict[str, str]
    sample_count: int
    yield_stats: Dict[str, float]
    disease_distribution: Dict[str, int]
    nutrient_distribution: Dict[str, int]
    soil_stats: Dict[str, Dict[str, float]]
    microbiome_stats: Dict[str, Dict[str, float]]
    functional_stats: Dict[str, Dict[str, float]]
    engineered_stats: Dict[str, Dict[str, float]]


def _describe_numeric(series: pd.Series) -> Dict[str, float]:
    return {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "q25": float(series.quantile(0.25)),
        "q75": float(series.quantile(0.75)),
    }


def _safe_describe(df: pd.DataFrame, columns: List[str]) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}
    for col in columns:
        if col in df.columns and len(df) > 0:
            result[col] = _describe_numeric(df[col])
    return result


class ZoneProfiler:
    """Build statistical profiles at village, variety, and management level."""

    def __init__(self, dataset: pd.DataFrame) -> None:
        self._df = dataset.copy()

    # ------------------------------------------------------------------
    # Village-level profiles
    # ------------------------------------------------------------------

    def village_profile(self, village: str) -> Optional[ProfileSummary]:
        subset = self._df[self._df["Village"] == village]
        if subset.empty:
            return None
        return self._build_profile(subset, {"Village": village})

    def all_village_profiles(self) -> Dict[str, ProfileSummary]:
        profiles: Dict[str, ProfileSummary] = {}
        for village in sorted(self._df["Village"].unique()):
            p = self.village_profile(village)
            if p is not None:
                profiles[village] = p
        return profiles

    # ------------------------------------------------------------------
    # Variety-level profiles
    # ------------------------------------------------------------------

    def variety_profile(self, variety: str) -> Optional[ProfileSummary]:
        subset = self._df[self._df["Mango_Variety"] == variety]
        if subset.empty:
            return None
        return self._build_profile(subset, {"Mango_Variety": variety})

    def village_variety_profile(
        self, village: str, variety: str
    ) -> Optional[ProfileSummary]:
        subset = self._df[
            (self._df["Village"] == village)
            & (self._df["Mango_Variety"] == variety)
        ]
        if subset.empty:
            return None
        return self._build_profile(
            subset, {"Village": village, "Mango_Variety": variety}
        )

    # ------------------------------------------------------------------
    # Management-level profiles
    # ------------------------------------------------------------------

    def management_profile(self, management: str) -> Optional[ProfileSummary]:
        subset = self._df[self._df["Management"] == management]
        if subset.empty:
            return None
        return self._build_profile(subset, {"Management": management})

    # ------------------------------------------------------------------
    # Available dimensions
    # ------------------------------------------------------------------

    def available_villages(self) -> List[str]:
        return sorted(self._df["Village"].unique().tolist())

    def available_varieties(self) -> List[str]:
        return sorted(self._df["Mango_Variety"].unique().tolist())

    def available_management_types(self) -> List[str]:
        return sorted(self._df["Management"].unique().tolist())

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_profile(
        self, subset: pd.DataFrame, group_key: Dict[str, str]
    ) -> ProfileSummary:
        yield_stats: Dict[str, float] = {}
        if TARGET_YIELD in subset.columns:
            yield_stats = _describe_numeric(subset[TARGET_YIELD])

        disease_dist: Dict[str, int] = {}
        if TARGET_DISEASE in subset.columns:
            disease_dist = subset[TARGET_DISEASE].value_counts().to_dict()

        nutrient_dist: Dict[str, int] = {}
        if TARGET_NUTRIENT in subset.columns:
            nutrient_dist = subset[TARGET_NUTRIENT].value_counts().to_dict()

        return ProfileSummary(
            group_key=group_key,
            sample_count=len(subset),
            yield_stats=yield_stats,
            disease_distribution=disease_dist,
            nutrient_distribution=nutrient_dist,
            soil_stats=_safe_describe(subset, SOIL_FEATURES),
            microbiome_stats=_safe_describe(subset, MICROBIOME_FEATURES),
            functional_stats=_safe_describe(subset, FUNCTIONAL_FEATURES),
            engineered_stats=_safe_describe(subset, ENGINEERED_FEATURES),
        )

    # ------------------------------------------------------------------
    # Serialisation helpers (for API / dashboard)
    # ------------------------------------------------------------------

    @staticmethod
    def profile_to_dict(profile: ProfileSummary) -> Dict[str, Any]:
        return {
            "group_key": profile.group_key,
            "sample_count": profile.sample_count,
            "yield_stats": profile.yield_stats,
            "disease_distribution": profile.disease_distribution,
            "nutrient_distribution": profile.nutrient_distribution,
            "soil_stats": profile.soil_stats,
            "microbiome_stats": profile.microbiome_stats,
            "functional_stats": profile.functional_stats,
            "engineered_stats": profile.engineered_stats,
        }

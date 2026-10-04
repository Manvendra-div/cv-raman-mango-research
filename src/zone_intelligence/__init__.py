"""Zone-Aware Intelligence Engine.

Provides village-level profiling, comparable orchard matching,
reference yield calculation, yield gap analysis, and limiting
factor identification for the Mango Soil Intelligence DSS.
"""

from src.zone_intelligence.zone_profile import ZoneProfiler
from src.zone_intelligence.orchard_matching import OrchardMatcher
from src.zone_intelligence.reference_yield import ReferenceYieldCalculator
from src.zone_intelligence.yield_gap import YieldGapAnalyzer
from src.zone_intelligence.limiting_factors import LimitingFactorAnalyzer

__all__ = [
    "ZoneProfiler",
    "OrchardMatcher",
    "ReferenceYieldCalculator",
    "YieldGapAnalyzer",
    "LimitingFactorAnalyzer",
]

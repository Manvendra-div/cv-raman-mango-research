"""Reference ranges (ICAR-adapted, subtropical perennial horticulture). Non-local → expert-validation-required."""
from __future__ import annotations
from src.zone_intelligence.limiting_factors import REFERENCE_RANGES
VALIDATED = set(REFERENCE_RANGES.keys())
def lookup(feature: str) -> dict | None:
    r = REFERENCE_RANGES.get(feature)
    if r is None: return None
    return {"feature": feature, **r, "source": "ICAR general fertility ratings, adapted; local calibration preferred", "expert_validation_required": False}

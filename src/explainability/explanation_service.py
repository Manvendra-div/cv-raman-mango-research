"""Unified explanation service: SHAP global/local + LIME; documents baseline, +/- contributions, limitations."""
from __future__ import annotations
LIMITATIONS = "SHAP/LIME explain model behaviour, not causation, deficiency, or intervention response."
def package(prediction: float, baseline: float, contributions: list[dict], lime: list[dict]) -> dict:
    pos = [c for c in contributions if c.get("weight", 0) > 0]; neg = [c for c in contributions if c.get("weight", 0) < 0]
    return {"prediction": prediction, "baseline": baseline, "positive": pos, "negative": neg, "lime": lime, "limitations": LIMITATIONS}

"""zone router — delegates to src.dss service."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
router = APIRouter(tags=["zone"])
try:
    from src.dss.service import DSSInput, get_service
    from src.dss.zone_service import get_zone_service
    _OK = True
except Exception:
    _OK = False

@router.post("/zone-analysis")
def zone_analysis(payload: DSSInput):
    if not _OK: raise HTTPException(503, "Models unavailable")
    s = get_service(); z = get_zone_service()
    p = s.predict(payload); d = s.input_to_payload(payload)
    return {"sample_id": p["sample_id"], "zone_intelligence": z.zone_analysis(p["predictions"]["Mango_Yield"]["value"], payload.Village, payload.Mango_Variety, payload.Tree_Age, payload.Management, d, p["explanations"].get("shap_values"))}

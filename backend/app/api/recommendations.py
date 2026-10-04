"""recommendations router — delegates to src.dss service."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
router = APIRouter(tags=["recommendations"])
try:
    from src.dss.service import DSSInput, get_service
    from src.dss.zone_service import get_zone_service
    _OK = True
except Exception:
    _OK = False

@router.post("/recommendations")
def recommendations(payload: DSSInput):
    if not _OK: raise HTTPException(503, "Models unavailable")
    s = get_service(); d = s.input_to_payload(payload)
    return {"sample_id": d.get("Sample_ID"), "recommendations": s.generate_recommendations(d)}

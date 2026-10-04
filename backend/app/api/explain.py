"""explain router — delegates to src.dss service."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
router = APIRouter(tags=["explain"])
try:
    from src.dss.service import DSSInput, get_service
    from src.dss.zone_service import get_zone_service
    _OK = True
except Exception:
    _OK = False

@router.post("/explain")
def explain(payload: DSSInput):
    if not _OK: raise HTTPException(503, "Models unavailable")
    p = get_service().predict(payload)
    return {"sample_id": p["sample_id"], "explanations": p["explanations"]}

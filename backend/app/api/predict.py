"""predict router — delegates to src.dss service."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
router = APIRouter(tags=["predict"])
try:
    from src.dss.service import DSSInput, get_service
    from src.dss.zone_service import get_zone_service
    _OK = True
except Exception:
    _OK = False

@router.post("/predict")
def predict(payload: DSSInput):
    if not _OK: raise HTTPException(503, "Models unavailable")
    return get_service().predict(payload)

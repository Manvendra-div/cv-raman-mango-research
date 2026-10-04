"""metadata router — delegates to src.dss service."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
router = APIRouter(tags=["metadata"])
try:
    from src.dss.service import DSSInput, get_service
    from src.dss.zone_service import get_zone_service
    _OK = True
except Exception:
    _OK = False

@router.get("/metadata")
def metadata():
    if not _OK: raise HTTPException(503, "Service unavailable: artifacts missing")
    return get_service().metadata()

@router.get("/example-input")
def example_input():
    if not _OK: raise HTTPException(503, "Service unavailable")
    return get_service().default_input

@router.get("/zones")
def zones():
    if not _OK: raise HTTPException(503, "Service unavailable")
    return get_zone_service().available_zones()

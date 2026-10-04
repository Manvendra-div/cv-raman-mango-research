"""Backend entry — modular FastAPI, reuses src.dss service. No fake predictions: 503 if artifacts missing."""
from __future__ import annotations
from fastapi import FastAPI
from backend.app.api import predict, explain, recommendations, metadata, zone
app = FastAPI(title="Zone-Aware Mango Soil Intelligence and Yield Gap DSS", version="2.0.0",
    description="Yield/disease/nutrient + zone benchmarking + yield-gap + SHAP/LIME + agronomic rules.")
app.include_router(metadata.router); app.include_router(predict.router); app.include_router(explain.router)
app.include_router(recommendations.router); app.include_router(zone.router)
@app.get("/health")
def health(): return {"status": "ok", "system": "Zone-Aware Mango Soil Intelligence and Yield Gap DSS"}

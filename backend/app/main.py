"""Backend entry — modular FastAPI, reuses src.dss service. No fake predictions: 503 if artifacts missing."""
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from backend.app.api import predict, explain, recommendations, metadata, zone
app = FastAPI(title="Zone-Aware Mango Soil Intelligence and Yield Gap DSS", version="2.0.0",
    description="Yield/disease/nutrient + zone benchmarking + yield-gap + SHAP/LIME + agronomic rules.")
app.include_router(metadata.router); app.include_router(predict.router); app.include_router(explain.router)
app.include_router(recommendations.router); app.include_router(zone.router)

@app.get("/health")
def health(): return {"status": "ok", "system": "Zone-Aware Mango Soil Intelligence and Yield Gap DSS"}

@app.post("/report")
def report(payload: dict):
    """Full markdown report: predictions + SHAP + zone intelligence + Do/Don't explainer."""
    try:
        from src.dss.service import get_service
        from src.dss.zone_service import get_zone_service
    except Exception as e:
        raise HTTPException(503, f"Models unavailable: {e}")
    svc = get_service()
    result = svc.predict(payload)
    try:
        z = get_zone_service()
        zi = z.zone_analysis(
            predicted_yield=result["predictions"]["Mango_Yield"]["value"],
            village=payload.get("Village", ""),
            variety=payload.get("Mango_Variety", ""),
            tree_age=payload.get("Tree_Age", 10),
            management=payload.get("Management", ""),
            sample_values=payload,
            shap_contributions=result["explanations"].get("shap_values"),
        )
        result["zone_intelligence"] = zi
    except Exception:
        pass
    return {"sample_id": result["sample_id"], "markdown_report": svc.export_markdown_report(result)}

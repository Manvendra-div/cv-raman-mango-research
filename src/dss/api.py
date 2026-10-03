"""FastAPI backend for the Phase 9 decision support system."""

from __future__ import annotations

from fastapi import FastAPI

from src.dss.service import DSSInput, get_service


app = FastAPI(
    title="Malihabad Mango Soil Microbiome DSS",
    description="Local DSS for yield, disease-risk, nutrient-status, XAI, and recommendations.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    get_service()
    return {"status": "ok", "phase": "9"}


@app.get("/metadata")
def metadata() -> dict:
    return get_service().metadata()


@app.get("/example-input")
def example_input() -> dict:
    return get_service().default_input


@app.post("/predict")
def predict(payload: DSSInput) -> dict:
    return get_service().predict(payload)


@app.post("/explain")
def explain(payload: DSSInput) -> dict:
    service = get_service()
    prediction = service.predict(payload)
    return {
        "sample_id": prediction["sample_id"],
        "explanations": prediction["explanations"],
        "reference_artifacts": prediction["reference_artifacts"],
    }


@app.post("/recommendations")
def recommendations(payload: DSSInput) -> dict:
    service = get_service()
    data = service.input_to_payload(payload)
    return {
        "sample_id": data.get("Sample_ID"),
        "recommendations": service.generate_recommendations(data),
        "reference_artifacts": service.reference_artifacts(),
    }


@app.post("/report")
def report(payload: DSSInput) -> dict:
    service = get_service()
    prediction = service.predict(payload)
    return {
        "sample_id": prediction["sample_id"],
        "markdown_report": service.export_markdown_report(prediction),
        "prediction": prediction,
    }


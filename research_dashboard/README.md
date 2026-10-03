# Research Dashboard

Created on: 2026-06-27

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This dashboard brings the completed research workflow into one local Streamlit interface. It summarizes the processed dataset, feature engineering, model performance, explainable AI outputs, Phase 10 validation, and champion-model decision support.

## Dashboard Views

| View | Contents |
|---|---|
| Overview | Dataset size, split distribution, champion models, target distributions, phase coverage |
| Data Explorer | Village, split, variety, season, and management filters with yield and soil-health charts |
| Model Performance | Phase 7 regression/classification metrics, champion selection, Rahimabad hold-out summary |
| Explainability | Phase 8 SHAP feature importance, SHAP/LIME images, recommendation rules |
| Validation | Phase 10 internal CV, Rahimabad hold-out, real-sample status, field-intervention status |
| Decision Support | In-process champion-model prediction with explanations and recommendations |
| Artifacts | Browse and download key CSV, JSON, Markdown, image, and model artifacts |

## Run

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File research_dashboard\run_dashboard.ps1
```

Default URL:

```text
http://127.0.0.1:8502
```

## Main File

- `src/research_dashboard/dashboard.py`

## Notes

The dashboard uses local generated artifacts from Phases 5-10. The decision-support page loads the champion model pipelines directly through `src.dss.service`, so the FastAPI DSS server is not required for this dashboard.

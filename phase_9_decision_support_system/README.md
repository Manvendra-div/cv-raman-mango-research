# Phase 9: Decision Support System

Implemented on: 2026-06-27

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 9 from `Detailed_Research_Work_Outline.md`. Phase 9 turns the verified Phase 7 champion models and Phase 8 explainability outputs into a local decision support system.

## Implemented Components

| Requirement from Phase 9 | Implemented artifact |
|---|---|
| FastAPI prediction endpoint | `src/dss/api.py` |
| Input schema for selected features | `DSSInput` in `src/dss/service.py` |
| Preprocessing pipeline loader | `DSSService` loads fitted Phase 7 pipelines |
| Model loader | `DSSService` loads champion yield, disease-risk, and nutrient models |
| Prediction service | `DSSService.predict()` |
| Explanation service for SHAP/LIME output | `/explain` endpoint and Phase 8 artifact references |
| Recommendation generator | `DSSService.generate_recommendations()` |
| Streamlit input dashboard | `src/dss/dashboard.py` |
| Soil and microbiome input form | Dashboard tabs: Soil, Microbiome, Climate, Orchard |
| Yield prediction display | Dashboard metric card |
| Disease-risk display | Dashboard metric card |
| Nutrient status display | Dashboard metric card |
| SHAP or feature-contribution view | Dashboard contribution chart and table |
| Farmer-friendly recommendation panel | Dashboard recommendations table |
| Exportable report | `/report` endpoint and dashboard download buttons |

## Current Verified Models Served

| Target | Champion model | Source |
|---|---|---|
| `Mango_Yield` | `Linear_Regression` | `outputs/models/regression/champion_regression_model.joblib` |
| `Disease_Risk` | `Gradient_Boosting` | `outputs/models/classification/champion_disease_risk_model.joblib` |
| `Nutrient_Availability` | `Random_Forest` | `outputs/models/classification/champion_nutrient_availability_model.joblib` |

## Start Locally

Run from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File phase_9_decision_support_system\run_api.ps1
powershell -ExecutionPolicy Bypass -File phase_9_decision_support_system\run_dashboard.ps1
```

Default URLs:

- API: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8501`

## Reproduce Example Files

```powershell
python src\dss\generate_phase9_examples.py
```

## Caveat

This is a local research prototype using synthetic data and trained prototype models. Predictions and recommendations should be validated with field observations, soil tests, and pathogen assays before real agronomic use.


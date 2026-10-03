# Phase 8: Explainable AI

Implemented on: 2026-06-27

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 8 from `Detailed_Research_Work_Outline.md`. Phase 8 explains the verified Phase 7 champion models using SHAP, LIME, dependence diagnostics, local explanations, and agronomic recommendation rules.

## Explained Models

| Target | Verified champion | Explained output |
|---|---|---|
| `Mango_Yield` | `Linear_Regression` | predicted yield |
| `Disease_Risk` | `Gradient_Boosting` | probability of `High` disease risk |
| `Nutrient_Availability` | `Random_Forest` | probability of `High` nutrient availability |

## Methodology Coverage

| Phase 8 requirement | Implemented artifact |
|---|---|
| Global feature importance | `phase8_global_feature_importance.csv` |
| SHAP summary plots | `outputs/explainability/phase8_xai/figures/shap_summary_*` |
| SHAP dependence plots | `outputs/explainability/phase8_xai/figures/shap_dependence_*` |
| Local SHAP or waterfall explanations | `outputs/explainability/phase8_xai/local_explanations/shap_waterfall_*` |
| LIME local explanations | `outputs/explainability/phase8_xai/local_explanations/lime_*` |
| Agronomic recommendation rules | `phase8_recommendation_rules.csv` |
| Explanation report | `outputs/reports/phase8_explainable_ai/phase8_explainable_ai_report.md` |

## Current Output Summary

| Item | Count |
|---|---:|
| Targets explained | 3 |
| SHAP background rows per target | 120 |
| SHAP explanation rows requested per target | 220 |
| Local examples per target | 3 |
| Dependence diagnostics | 12 |
| Local SHAP contribution rows | 108 |
| LIME contribution rows | 108 |
| Recommendation rules | 7 |
| Instance-level recommendations | 17 |
| Generated figures and local HTML files | 48 |

## Reproduce

Run from the project root after Phase 7:

```powershell
python src\explainability\phase8_explainable_ai.py
```

## Main Implementation File

- `src/explainability/phase8_explainable_ai.py`

## Important Caveat

The current dataset is synthetic prototype data. Phase 8 explanations validate the XAI workflow and generate interpretable artifacts, but they should be validated with real orchard samples before being used as agronomic evidence.


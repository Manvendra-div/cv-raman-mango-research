# Recommendation Rule Notes

## Purpose

Recommendation rules translate Phase 8 XAI findings into decision-support flags. They are not field prescriptions.

## Rule Sources

Rules use:

- train-split quartile thresholds
- SHAP global importance support
- biologically meaningful features from the research outline
- contextual raw features where relevant

## Current Rule Families

| Rule family | Feature examples | Purpose |
|---|---|---|
| Soil health | `Soil_Health_Index_Phase6` | Flag low soil-health condition linked to yield risk |
| NPK balance | `NPK_Balance_Score_Phase6` | Flag nutrient imbalance and guide balanced fertilization |
| Pathogen pressure | `Pathogen_Load_Index_Phase6`, `Fusarium` | Flag disease-risk context |
| Beneficial microbes | `Beneficial_Microbial_Index_Phase6` | Flag low beneficial microbial support |
| Microbial richness | `Microbial_Richness_Score` | Flag reduced biological resilience |
| High nutrient status | `NPK_Balance_Score_Phase6` | Avoid unnecessary excess fertilizer when nutrient status is already high |

## Main Output

- `outputs/explainability/phase8_xai/tables/phase8_recommendation_rules.csv`

## Instance-Level Output

- `outputs/explainability/phase8_xai/tables/phase8_instance_recommendations.csv`

## Caveat

Rules should be validated with measured soil tests, pathogen assays, orchard observations, and local agronomic judgment before use in field recommendations.


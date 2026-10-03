# Explainable AI Workflow

## Objective

Explain the verified champion models from Phase 7 and translate model behavior into agronomically readable diagnostics.

## Inputs

| Input | Role |
|---|---|
| `data/processed/feature_table.csv` | Source rows and metadata for explanation |
| `data/processed/selected_features.json` | Selected numeric and categorical feature lists |
| `outputs/models/regression/champion_regression_model.joblib` | Yield model to explain |
| `outputs/models/classification/champion_disease_risk_model.joblib` | Disease-risk model to explain |
| `outputs/models/classification/champion_nutrient_availability_model.joblib` | Nutrient-availability model to explain |

## Explanation Steps

1. Load each champion model pipeline.
2. Use the fitted preprocessing step to transform selected features.
3. Compute model-agnostic permutation SHAP values in transformed model space.
4. Aggregate transformed SHAP values back to original feature names.
5. Generate SHAP summary bar and beeswarm plots.
6. Generate dependence plots for biologically meaningful features.
7. Select local validation and Rahimabad examples for each target.
8. Generate SHAP waterfall plots for local examples.
9. Generate LIME explanations for the same local examples.
10. Build recommendation rules from train-split thresholds and XAI support.
11. Write the Phase 8 explanation report.

## Explained Outputs

| Target | Explained output |
|---|---|
| `Mango_Yield` | predicted yield |
| `Disease_Risk` | probability of class `High` |
| `Nutrient_Availability` | probability of class `High` |

## Feature-Space Note

SHAP and LIME are computed in the fitted transformed model space. The script also maps transformed features back to original feature names so that the report can be interpreted agronomically.

## Expected Explanation Coverage

| Expected explanation from outline | Phase 8 handling |
|---|---|
| High pathogen load increases disease risk | `Pathogen_Load_Index` dependence plot and SHAP ranking |
| Higher soil health improves yield | `Soil_Health_Index` dependence plot and SHAP ranking |
| Balanced N, P, and K improves productivity | `NPK_Balance_Score_Phase6` and nutrient feature dependence plots |
| Low microbial richness may indicate reduced resilience | `Microbial_Richness_Score` dependence plot and recommendation rule |
| High Fusarium and low beneficial microbes indicate disease-prone orchards | `Fusarium` contextual rule plus `Beneficial_Microbial_Index_Phase6` dependence/recommendation rule |


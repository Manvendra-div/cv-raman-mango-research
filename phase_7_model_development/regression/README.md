# Phase 7.1: Mango Yield Regression

Implemented on: 2026-06-26

## Purpose

This folder implements the Phase 7.1 regression task from `Detailed_Research_Work_Outline.md`.

Target:

- `Mango_Yield`

## Methodology Coverage

| Outline requirement | Implemented artifact |
|---|---|
| Linear Regression or Elastic Net baseline | `linear_regression.joblib`, `elastic_net.joblib` |
| Support Vector Regression | `linear_svr.joblib` |
| Random Forest Regressor | `random_forest.joblib` |
| Gradient Boosting Regressor | `gradient_boosting.joblib` |
| XGBoost or LightGBM if allowed | Script auto-adds them if installed; neither package is installed in the current environment |
| MLP regressor | `mlp_regressor.joblib` |
| Hybrid rule-guided model | `hybrid_rule_guided_gb_base_pipeline.joblib`, `hybrid_rule_guided_gb_rule_config.json` |
| RMSE, MAE, R-squared | `outputs/metrics/regression/regression_model_metrics.csv` |
| Residual analysis | `outputs/metrics/regression/regression_residual_summary.csv` |
| Village-wise error | `outputs/metrics/regression/regression_village_wise_error.csv` |
| Season-wise error | `outputs/metrics/regression/regression_season_wise_error.csv` |
| Predictions | `outputs/predictions/regression/regression_predictions_all_models.csv` |
| Champion model report | `outputs/reports/phase7_regression/regression_model_development_report.md` |

## Current Champion

Champion selection rule:

- Lowest validation RMSE.

Selected champion:

- `Linear_Regression`

Validation performance:

- RMSE: `1.9931895836481133`
- MAE: `1.602414979235878`
- R2: `0.3029736965248554`

## Reproduce

Run from the project root:

```powershell
python src\modeling\phase7_1_train_regression.py
```

## Main Implementation File

- `src/modeling/phase7_1_train_regression.py`


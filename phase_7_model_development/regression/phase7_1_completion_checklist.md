# Phase 7.1 Completion Checklist

| Phase 7.1 task from outline | Status | Evidence |
|---|---|---|
| Define regression target `Mango_Yield` | Complete | `src/modeling/phase7_1_train_regression.py` |
| Use Phase 6 selected features | Complete | `data/processed/selected_features.json` |
| Preserve train, validation, test, and Rahimabad hold-out splits | Complete | `data/processed/feature_table.csv` |
| Train Linear Regression or Elastic Net baseline | Complete | `linear_regression.joblib`, `elastic_net.joblib` |
| Train Support Vector Regression | Complete | `linear_svr.joblib` |
| Train Random Forest Regressor | Complete | `random_forest.joblib` |
| Train Gradient Boosting Regressor | Complete | `gradient_boosting.joblib` |
| Include XGBoost or LightGBM if allowed | Complete with dependency gate | Script auto-adds installed packages; unavailable in current environment |
| Train MLP regressor | Complete | `mlp_regressor.joblib` |
| Train hybrid rule-guided model | Complete | `hybrid_rule_guided_gb_base_pipeline.joblib`, `hybrid_rule_guided_gb_rule_config.json` |
| Calculate RMSE, MAE, and R-squared | Complete | `regression_model_metrics.csv` |
| Perform residual analysis | Complete | `regression_residual_summary.csv` |
| Perform village-wise error analysis | Complete | `regression_village_wise_error.csv` |
| Perform season-wise error analysis | Complete | `regression_season_wise_error.csv` |
| Save all model predictions | Complete | `regression_predictions_all_models.csv` |
| Select and save champion model | Complete | `champion_regression_model.joblib`, `champion_regression_model.json` |
| Write regression model development report | Complete | `regression_model_development_report.md` |

## Current Phase 7.1 Exit Decision

Phase 7.1 is complete for the currently available synthetic dataset.

## Current Champion

| Field | Value |
|---|---|
| Champion model | `Linear_Regression` |
| Selection metric | validation RMSE |
| Validation RMSE | `1.9931895836481133` |
| Validation MAE | `1.602414979235878` |
| Validation R2 | `0.3029736965248554` |

## Ready for Phase 7.2

Phase 7.2 classification can begin after reviewing:

- `outputs/reports/phase7_regression/regression_model_development_report.md`
- `outputs/metrics/regression/regression_model_metrics.csv`
- `outputs/metrics/regression/regression_village_wise_error.csv`
- `outputs/metrics/regression/regression_season_wise_error.csv`


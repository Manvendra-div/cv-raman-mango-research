# Phase 7.2 Completion Checklist

| Phase 7.2 task from outline | Status | Evidence |
|---|---|---|
| Define classification targets `Disease_Risk` and `Nutrient_Availability` | Complete | `src/modeling/phase7_2_train_classification.py` |
| Use Phase 6 selected features | Complete | `data/processed/selected_features.json` |
| Preserve train, validation, test, and Rahimabad hold-out splits | Complete | `data/processed/feature_table.csv` |
| Train Logistic Regression baseline | Complete | `logistic_regression` artifacts per target |
| Train Support Vector Machine | Complete | `linear_svm` artifacts per target |
| Train Random Forest Classifier | Complete | `random_forest` artifacts per target |
| Train Gradient Boosting Classifier | Complete | `gradient_boosting` artifacts per target |
| Train MLP classifier | Complete | `mlp_classifier` artifacts per target |
| Train hybrid ML plus agronomic rules | Complete | hybrid base pipeline and rule-config artifacts per target |
| Calculate accuracy, precision, recall, and macro F1-score | Complete | `classification_model_metrics.csv` |
| Calculate confusion matrices | Complete | `classification_confusion_matrix.csv` |
| Calculate ROC-AUC where suitable | Complete | `classification_model_metrics.csv` |
| Calculate calibration curves | Complete | `classification_calibration_curve.csv` |
| Save all model predictions | Complete | `classification_predictions_all_models.csv` |
| Select and save champion models | Complete | `champion_classification_models.json` |
| Write classification model development report | Complete | `classification_model_development_report.md` |

## Current Phase 7.2 Exit Decision

Phase 7.2 is complete for the currently available synthetic dataset.

## Current Champions

| Target | Champion model | Selection metric | Validation macro F1 | Validation accuracy | Validation ROC-AUC |
|---|---|---|---:|---:|---:|
| `Disease_Risk` | `Gradient_Boosting` | validation macro F1 | 0.9901465246290658 | 0.9906291834002677 | 0.9996003834258405 |
| `Nutrient_Availability` | `Random_Forest` | validation macro F1 | 1.0 | 1.0 | 1.0 |

## Ready for Phase 8

Phase 8 XAI can begin after reviewing:

- `outputs/reports/phase7_classification/classification_model_development_report.md`
- `outputs/metrics/classification/classification_model_metrics.csv`
- `outputs/metrics/classification/classification_confusion_matrix.csv`
- `outputs/metrics/classification/classification_calibration_curve.csv`


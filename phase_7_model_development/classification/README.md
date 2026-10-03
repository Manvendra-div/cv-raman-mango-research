# Phase 7.2: Classification Tasks

Implemented on: 2026-06-26

## Purpose

This folder implements the Phase 7.2 classification task from `Detailed_Research_Work_Outline.md`.

Targets:

- `Disease_Risk`
- `Nutrient_Availability`

## Methodology Coverage

| Outline requirement | Implemented artifact |
|---|---|
| Logistic Regression baseline | `logistic_regression` model artifacts per target |
| Support Vector Machine | `linear_svm` calibrated model artifacts per target |
| Random Forest Classifier | `random_forest` model artifacts per target |
| Gradient Boosting Classifier | `gradient_boosting` model artifacts per target |
| MLP classifier | `mlp_classifier` model artifacts per target |
| Hybrid ML plus agronomic rules | `hybrid_rule_guided_gb_base_pipeline` and rule-config files per target |
| Accuracy, precision, recall, macro F1-score | `outputs/metrics/classification/classification_model_metrics.csv` |
| Confusion matrix | `outputs/metrics/classification/classification_confusion_matrix.csv` |
| ROC-AUC if suitable | `outputs/metrics/classification/classification_model_metrics.csv` |
| Calibration curve | `outputs/metrics/classification/classification_calibration_curve.csv` |
| Predictions | `outputs/predictions/classification/classification_predictions_all_models.csv` |
| Champion model report | `outputs/reports/phase7_classification/classification_model_development_report.md` |

## Current Champions

Champion selection rule:

- Highest validation macro F1-score per target.

| Target | Champion | Validation macro F1 | Validation accuracy | Validation ROC-AUC |
|---|---|---:|---:|---:|
| `Disease_Risk` | `Gradient_Boosting` | 0.9901465246290658 | 0.9906291834002677 | 0.9996003834258405 |
| `Nutrient_Availability` | `Random_Forest` | 1.0 | 1.0 | 1.0 |

## Reproduce

Run from the project root:

```powershell
python src\modeling\phase7_2_train_classification.py
```

## Main Implementation File

- `src/modeling/phase7_2_train_classification.py`

## Data Caveat

`Nutrient_Availability` currently contains `Optimal` and `High` classes only. The methodology mentions `Deficient`, but no `Deficient` rows are present in the current dataset.


# Phase 10 Validation Workflow

## Inputs

| Input | Purpose |
|---|---|
| `data/processed/feature_table.csv` | Phase 6 feature table with train, validation, test, and Rahimabad hold-out rows |
| `data/processed/selected_features.json` | Selected numeric and categorical model features |
| `outputs/metrics/regression/regression_model_metrics.csv` | Phase 7 train/test regression metrics |
| `outputs/metrics/classification/classification_model_metrics.csv` | Phase 7 train/test classification metrics |
| `outputs/models/*/champion_*.joblib` | Champion pipelines for real-sample prediction |

## Execution Stages

1. Load selected features and validate that all required targets are present.
2. Run 5-fold internal regression validation using KFold.
3. Run 5-fold internal classification validation using StratifiedKFold.
4. Consolidate Phase 7 train/test split metrics for comparison.
5. Retrain models on all non-Rahimabad villages and test on Rahimabad.
6. Create or read real-sample validation inputs.
7. Create or read field-intervention validation inputs.
8. Write CSV outputs, a JSON summary, a manifest, and a Markdown report.

## Validation Metrics

| Task | Primary metric | Supporting metrics |
|---|---|---|
| `Mango_Yield` regression | RMSE | MAE, R2 |
| `Disease_Risk` classification | Macro F1 | Accuracy, balanced accuracy, macro precision, macro recall, ROC AUC |
| `Nutrient_Availability` classification | Macro F1 | Accuracy, balanced accuracy, macro precision, macro recall, ROC AUC |

## Geographic Hold-Out Design

Rahimabad is held out completely during geographic validation. All non-Rahimabad rows are used for training, and all Rahimabad rows are used for testing. This checks whether internal validation performance transfers to an unseen village context.

## Rerun Command

```powershell
python src\validation\phase10_validation.py
```

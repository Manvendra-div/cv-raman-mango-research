# Phase 7: Model Development

Implemented on: 2026-06-26

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 7 from `Detailed_Research_Work_Outline.md`. Completed subphases currently include Phase 7.1 regression for `Mango_Yield`, Phase 7.2 classification for `Disease_Risk` and `Nutrient_Availability`, and Phase 7.3 complete model-results reporting.

## Implemented Subphases

| Subphase | Status | Entry point |
|---|---|---|
| 7.1 Regression task | Complete | `regression/README.md` |
| 7.2 Classification task | Complete | `classification/README.md` |
| 7.3 Model result reporting | Complete | `results_reporting/README.md` |

## Source Inputs Used

- `Detailed_Research_Work_Outline.md`
- `data/processed/feature_table.csv`
- `data/processed/selected_features.json`
- Phase 5 split assignments carried through the Phase 6 feature table

## Phase 7.1 Summary

Phase 7.1 trains regression models for `Mango_Yield`, evaluates them on train, validation, test, and Rahimabad geographic hold-out splits, and selects the champion model by lowest validation RMSE.

Current champion: `Linear_Regression`

Current validation RMSE: `1.9931895836481133`

## Phase 7.2 Summary

Phase 7.2 trains classification models for `Disease_Risk` and `Nutrient_Availability`, evaluates them on train, validation, test, and Rahimabad geographic hold-out splits, and selects one champion per target by highest validation macro F1-score.

Current `Disease_Risk` champion: `Gradient_Boosting`

Current `Disease_Risk` validation macro F1: `0.9901465246290658`

Current `Nutrient_Availability` champion: `Random_Forest`

Current `Nutrient_Availability` validation macro F1: `1.0`

## Phase 7.3 Summary

Phase 7.3 compiles the verified regression and classification outputs, reconciles the existing-report claims in the outline against reproduced metrics, summarizes Rahimabad hold-out results, and writes an artifact manifest for reproducibility.

Current verified champions:

- `Mango_Yield`: `Linear_Regression`
- `Disease_Risk`: `Gradient_Boosting`
- `Nutrient_Availability`: `Random_Forest`

Reported-claim reconciliation:

- matched: `2`
- near: `8`
- different: `4`

## Reproduce Phase 7

Run from the project root:

```powershell
python src\modeling\phase7_1_train_regression.py
python src\modeling\phase7_2_train_classification.py
python src\modeling\phase7_3_compile_model_results.py
```

# Phase 10: Validation

Implemented on: 2026-06-27

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 10 from `Detailed_Research_Work_Outline.md`. Phase 10 validates the research prototype at four levels: internal validation, Rahimabad geographic hold-out validation, real-sample validation readiness, and field-intervention validation readiness.

## Implemented Components

| Requirement from Phase 10 | Implemented artifact |
|---|---|
| K-fold cross-validation | `outputs/validation/phase10/phase10_internal_cv_regression_metrics.csv` |
| Stratified classification validation | `outputs/validation/phase10/phase10_internal_cv_classification_metrics.csv` |
| Train/test split comparison | `outputs/validation/phase10/phase10_train_test_split_comparison.csv` |
| Algorithm comparison | `outputs/validation/phase10/phase10_internal_cv_summary.csv` |
| Rahimabad geographic hold-out | `outputs/validation/phase10/phase10_geographic_holdout_*_metrics.csv` |
| Internal vs geographic comparison | `outputs/validation/phase10/phase10_internal_vs_geographic_summary.csv` |
| Real orchard sample validation | `data/validation/real_sample_validation_input.csv` and generated status outputs |
| Field intervention validation | `data/validation/field_intervention_validation_input.csv` and generated status outputs |
| Validation report | `outputs/reports/phase10_validation/phase10_validation_report.md` |

## Reproduce

Run from the project root:

```powershell
python src\validation\phase10_validation.py
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File phase_10_validation\run_phase10_validation.ps1
```

## Main Implementation File

- `src/validation/phase10_validation.py`

## Current Caveat

The internal and Rahimabad validations run against the current synthetic prototype dataset. Real-sample and field-intervention validation are implemented as executable workflows and will produce measured comparisons after real orchard observations are entered in `data/validation/`.

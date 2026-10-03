# Phase 6: Feature Engineering

Implemented on: 2026-06-26

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 6 from `Detailed_Research_Work_Outline.md`. Phase 6 creates biologically meaningful engineered features, documents them, evaluates redundancy and multicollinearity, and exports a selected feature set for Phase 7 model development.

## Source Inputs Used

- `Detailed_Research_Work_Outline.md`
- `data/processed/clean_master_dataset.csv`
- `data/splits/split_membership.csv`
- `phase_5_data_integration_preprocessing/preprocessing_workflow.md`

## Phase 6 Outputs

| Output required by methodology | Implemented artifact |
|---|---|
| Engineered feature table | `data/processed/engineered_feature_table.csv` |
| Feature documentation | `data/processed/feature_documentation.csv`, `feature_documentation.md` |
| Feature-selection report | `outputs/reports/phase6_feature_engineering/feature_selection_report.md` |
| Feature-engineering script | `src/feature_engineering/phase6_feature_engineering.py` |
| Full feature table | `data/processed/feature_table.csv` |
| Redundancy report | `outputs/feature_engineering/redundancy_pairs.csv` |
| Multicollinearity report | `outputs/feature_engineering/multicollinearity_vif.csv` |
| Target association report | `outputs/feature_engineering/feature_target_associations.csv` |
| Selected features | `data/processed/selected_features.json` |
| Completion evidence | `phase6_completion_checklist.md` |

## How to Reproduce

Run from the project root:

```powershell
python src\feature_engineering\phase6_feature_engineering.py
```

## Current Output Summary

| Item | Count |
|---|---:|
| Rows processed | 20,000 |
| New Phase 6 engineered features | 18 |
| Numeric candidate features audited | 71 |
| Selected numeric features | 34 |
| Redundancy pairs at abs correlation >= 0.90 | 5 |
| Features with VIF >= 10 | 38 |

## Ready for Phase 7

Phase 6 is ready for Phase 7 when:

- `data/processed/feature_table.csv` exists.
- `data/processed/engineered_feature_table.csv` exists.
- `data/processed/selected_features.json` exists.
- Feature-selection report is reviewed.
- Phase 7 models use the selected feature list or explicitly document any deviation.

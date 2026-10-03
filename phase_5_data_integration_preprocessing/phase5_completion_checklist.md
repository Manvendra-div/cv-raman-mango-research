# Phase 5 Completion Checklist

| Phase 5 task from outline | Status | Evidence |
|---|---|---|
| Merge site metadata, soil data, climate data, microbiome data, and yield/disease records | Complete for current synthetic dataset; real-data merge plan defined | `data/processed/clean_master_dataset.csv`; `data_integration_plan.md` |
| Standardize units and naming conventions | Complete | `src/preprocessing/phase5_preprocess.py`; `data/processed/data_dictionary.csv` |
| Handle missing values | Complete | `preprocessing_workflow.md`; `outputs/reports/phase5_preprocessing/preprocessing_report.md` |
| Encode categorical variables | Complete | `data/processed/model_ready_*_features.csv`; `data/processed/preprocessing_feature_columns.json` |
| Scale numerical variables where required | Complete | `src/preprocessing/phase5_preprocess.py`; model-ready feature files |
| Normalize compositional microbiome data appropriately | Complete | `preprocessing_workflow.md`; preprocessing report |
| Split data into training, validation, test, and geographic hold-out subsets | Complete | `data/splits/` |
| Produce clean master dataset | Complete | `data/processed/clean_master_dataset.csv` |
| Produce data dictionary | Complete | `data/processed/data_dictionary.csv` |
| Produce preprocessing script or notebook | Complete | `src/preprocessing/phase5_preprocess.py` |
| Produce train/test/hold-out split files | Complete | `data/splits/train.csv`; `data/splits/validation.csv`; `data/splits/test.csv`; `data/splits/holdout_rahimabad.csv` |

## Phase 5 Exit Decision

Phase 5 implementation is complete for the currently available synthetic dataset. The next implementation phase should be Phase 6: Feature Engineering.

## Locked Phase 5 Decisions

| Topic | Decision |
|---|---|
| Clean dataset path | `data/processed/clean_master_dataset.csv` |
| Data dictionary path | `data/processed/data_dictionary.csv` |
| Preprocessing script | `src/preprocessing/phase5_preprocess.py` |
| Geographic hold-out | Rahimabad |
| Internal split | 70 percent train, 15 percent validation, 15 percent test from non-holdout villages |
| Stratification target | `Disease_Risk` |
| Numeric scaling | `StandardScaler`, fit on train only |
| Categorical encoding | `OneHotEncoder`, fit on train only |
| Default leakage control | Exclude `Sample_ID`, targets, and `Orchard_ID` from model-ready features |
| Taxa normalization | Normalize bacterial, fungal, and archaeal groups separately |

## Current Output Summary

| Output | Rows |
|---|---:|
| Clean master dataset | 20,000 |
| Train split | 10,458 |
| Validation split | 2,241 |
| Test split | 2,242 |
| Rahimabad hold-out | 5,059 |

## Known Carry-Forward Caveats

- The dataset remains synthetic.
- `Nutrient_Availability` still has only `High` and `Optimal`; no `Deficient` class is present.
- Real Phase 3/4 data will need the same preprocessing logic after actual field/lab outputs exist.
- Phase 6 should audit engineered features for leakage and biological interpretability.

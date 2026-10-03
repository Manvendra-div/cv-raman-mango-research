# Phase 5: Data Integration and Preprocessing

Implemented on: 2026-06-26

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 5 from `Detailed_Research_Work_Outline.md`. Phase 5 converts the current raw synthetic CSV, and later real Phase 3/4 field and lab outputs, into clean, documented, split, and model-ready data files.

## Source Inputs Used

- `Detailed_Research_Work_Outline.md`
- `data/raw/mango_microbiome_dataset.csv`
- `phase_1_literature_review/final_technical_workflow.md`
- `phase_3_soil_microbiome_data_collection/initial_real_sample_dataset.md`
- `phase_4_laboratory_analysis/phase4_completion_checklist.md`

## Phase 5 Outputs

| Output required by methodology | Implemented artifact |
|---|---|
| Clean master dataset | `data/processed/clean_master_dataset.csv` |
| Data dictionary | `data/processed/data_dictionary.csv` |
| Preprocessing script | `src/preprocessing/phase5_preprocess.py` |
| Train/test/hold-out split files | `data/splits/train.csv`, `data/splits/validation.csv`, `data/splits/test.csv`, `data/splits/holdout_rahimabad.csv`, `data/splits/split_membership.csv` |
| Encoded/scaled model-ready data | `data/processed/model_ready_*_features.csv`, `data/processed/model_ready_*_targets.csv` |
| Preprocessing report | `outputs/reports/phase5_preprocessing/preprocessing_report.md` |
| Feature metadata | `data/processed/preprocessing_feature_columns.json` |

## Phase 5 Design Decision

The current implementation processes the available synthetic dataset. Real field/lab integration is also specified through the merge plan, but real merged outputs must wait until Phase 3 collection and Phase 4 lab analysis produce actual data.

## How to Reproduce

Run from the project root:

```powershell
python src\preprocessing\phase5_preprocess.py
```

## Current Generated Split Counts

| Split | Rows |
|---|---:|
| Train | 10,458 |
| Validation | 2,241 |
| Test | 2,242 |
| Rahimabad geographic hold-out | 5,059 |
| Total | 20,000 |

## Ready for Phase 6

Phase 5 is ready for Phase 6 when:

- Clean master dataset exists.
- Data dictionary exists.
- Split files exist.
- Encoded/scaled model-ready data exist.
- Preprocessing report has no blocking QC issues.

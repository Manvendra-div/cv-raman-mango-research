# Preprocessing Workflow

## 1. Objective

Prepare a reproducible dataset for Phase 6 feature engineering and Phase 7 model development.

## 2. Implemented Script

Main script:

```text
src/preprocessing/phase5_preprocess.py
```

Run command:

```powershell
python src\preprocessing\phase5_preprocess.py
```

## 3. Workflow Steps

1. Read `data/raw/mango_microbiome_dataset.csv`.
2. Standardize categorical text values.
3. Repair `Soil_Depth` encoding to ASCII labels.
4. Fill missing numeric feature values with training-independent median logic.
5. Fill missing categorical feature values as `Unknown`.
6. Clip negative taxonomic abundance values to zero.
7. Normalize bacterial, fungal, and archaeal taxonomic abundance groups separately.
8. Add preprocessing metadata columns.
9. Write `data/processed/clean_master_dataset.csv`.
10. Write `data/processed/data_dictionary.csv`.
11. Create Rahimabad geographic hold-out.
12. Split remaining villages into train, validation, and test sets.
13. Fit `StandardScaler` and `OneHotEncoder` on the train split only.
14. Transform train, validation, test, and hold-out splits.
15. Write model-ready feature and target files.
16. Write preprocessing report and feature metadata.

## 4. Missing-Value Policy

| Field type | Policy |
|---|---|
| Numeric feature | Median imputation |
| Categorical feature | `Unknown` |
| Target | Preserved; rows with missing targets should be reviewed before modeling |

The current synthetic dataset had no missing values.

## 5. Categorical Encoding

Encoded categorical features:

- `Village`
- `Mango_Variety`
- `Soil_Depth`
- `Sampling_Season`
- `Management`

`Orchard_ID` is preserved in the clean master dataset but excluded from the default model-ready feature matrix to reduce identifier leakage risk.

## 6. Scaling

Numeric feature columns are scaled using `StandardScaler`.

Important rule:

- The scaler is fitted only on the training split.
- Validation, test, and Rahimabad hold-out rows are transformed using the fitted training preprocessor.

## 7. Compositional Normalization

Taxonomic relative abundance is normalized by domain group:

- Bacterial phyla.
- Fungal phyla.
- Archaeal groups.

This prevents a synthetic negative or out-of-range value from entering model development.

## 8. Generated Model-Ready Files

Feature files:

- `data/processed/model_ready_train_features.csv`
- `data/processed/model_ready_validation_features.csv`
- `data/processed/model_ready_test_features.csv`
- `data/processed/model_ready_holdout_rahimabad_features.csv`
- `data/processed/model_ready_all_features.csv`

Target files:

- `data/processed/model_ready_train_targets.csv`
- `data/processed/model_ready_validation_targets.csv`
- `data/processed/model_ready_test_targets.csv`
- `data/processed/model_ready_holdout_rahimabad_targets.csv`
- `data/processed/model_ready_all_targets.csv`

Feature metadata:

- `data/processed/preprocessing_feature_columns.json`

# Feature Selection Method

## 1. Objective

Select a biologically meaningful and less redundant feature set for Phase 7 modeling.

## 2. Inputs

- `data/processed/feature_table.csv`
- `data/splits/split_membership.csv`
- Phase 6 engineered features
- Original cleaned numeric features

## 3. Selection Split

Feature associations and redundancy decisions are computed on the Phase 5 training split only.

This avoids using validation, test, or Rahimabad hold-out rows for feature-selection decisions.

## 4. Target Associations

The pipeline computes correlations with:

- `Mango_Yield`
- ordinal `Disease_Risk`
- ordinal `Nutrient_Availability`

Outputs:

- `outputs/feature_engineering/feature_target_associations.csv`

## 5. Redundancy Filtering

Candidate features are ranked using:

1. Biological priority.
2. Maximum absolute target association.
3. Feature name for deterministic ordering.

Features are dropped when they are redundant with an already selected feature at:

```text
absolute correlation >= 0.95
```

Output:

- `outputs/feature_engineering/feature_selection_decisions.csv`

## 6. Selected Feature Set

Final selected numeric features:

- Stored in `data/processed/selected_features.json`.
- Currently 34 numeric features.

Categorical features remain separate and should be encoded using the Phase 5 preprocessing approach.

## 7. Phase 7 Guidance

Phase 7 should compare at least:

- Raw feature baseline.
- Engineered feature set.
- Selected feature set.
- Combined raw plus selected engineered set.

This prevents the project from assuming that engineered features always improve performance.

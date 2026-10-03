# Classification Modeling Workflow

## Objective

Predict two classification targets from Phase 6 selected soil, microbiome, climate, orchard, and management features:

- `Disease_Risk`
- `Nutrient_Availability`

## Input Data

| Input | Role |
|---|---|
| `data/processed/feature_table.csv` | Model-ready table with Phase 6 engineered features and Phase 5 split labels |
| `data/processed/selected_features.json` | Selected numeric features and categorical features for encoding |

## Split Use

| Split | Role |
|---|---|
| `train` | Fit preprocessing and classifier parameters |
| `validation` | Select champion model per target |
| `test` | Estimate final in-distribution performance |
| `holdout_rahimabad` | Estimate geographic transfer performance |

Preprocessing is fit only inside each model pipeline on the train split.

## Modeling Steps

1. Load the Phase 6 feature table.
2. Read selected numeric and categorical features from `selected_features.json`.
3. Detect observed class order for each target:
   - `Disease_Risk`: Low, Medium, High
   - `Nutrient_Availability`: Optimal, High
4. Build a scikit-learn `ColumnTransformer`:
   - numeric features: `StandardScaler`
   - categorical features: `OneHotEncoder(handle_unknown="ignore")`
5. Train each classifier for each target on the train split.
6. Generate class predictions and class probabilities for train, validation, test, and Rahimabad hold-out splits.
7. Compute model-level, class-level, confusion-matrix, ROC-AUC, and calibration diagnostics.
8. Select one champion model per target by validation macro F1-score.
9. Save model artifacts, predictions, metrics, and report files.

## Candidate Models

| Model | Implementation |
|---|---|
| Majority baseline | `DummyClassifier(strategy="most_frequent")` |
| Logistic Regression baseline | `LogisticRegression(class_weight="balanced")` |
| Support Vector Machine | `CalibratedClassifierCV(LinearSVC)` |
| Random Forest | `RandomForestClassifier` |
| Gradient Boosting | `GradientBoostingClassifier` |
| MLP classifier | `MLPClassifier` |
| Hybrid ML plus agronomic rules | Gradient Boosting probabilities plus transparent rule adjustment |

## Hybrid Rule-Guided Models

`Disease_Risk` hybrid signal:

- increases `High` disease risk probability when pathogen pressure is higher
- decreases `High` disease risk probability when beneficial microbes and soil health are stronger

`Nutrient_Availability` hybrid signal:

- shifts probability toward `High` when nutrient and fertility indicators are higher
- shifts probability toward `Optimal` when the nutrient/fertility signal is lower

The rule settings are saved in:

- `outputs/models/classification/disease_risk__hybrid_rule_guided_gb_rule_config.json`
- `outputs/models/classification/nutrient_availability__hybrid_rule_guided_gb_rule_config.json`

## Output Decision

The validation split selects champions because it is not used for fitting. Test and Rahimabad hold-out splits remain diagnostic checks after champion selection.


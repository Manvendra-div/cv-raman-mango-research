# Regression Modeling Workflow

## Objective

Predict `Mango_Yield` from Phase 6 selected soil, microbiome, climate, orchard, and management features.

## Input Data

| Input | Role |
|---|---|
| `data/processed/feature_table.csv` | Model-ready table with Phase 6 engineered features and Phase 5 split labels |
| `data/processed/selected_features.json` | Selected numeric features and categorical features for encoding |

## Split Use

| Split | Role |
|---|---|
| `train` | Fit preprocessing and model parameters |
| `validation` | Select the champion model |
| `test` | Estimate final in-distribution performance |
| `holdout_rahimabad` | Estimate geographic transfer performance |

Preprocessing is fit only inside each pipeline on the train split.

## Modeling Steps

1. Load the Phase 6 feature table.
2. Read selected numeric and categorical features from `selected_features.json`.
3. Build a scikit-learn `ColumnTransformer`:
   - numeric features: `StandardScaler`
   - categorical features: `OneHotEncoder(handle_unknown="ignore")`
4. Train each regression candidate on the train split.
5. Generate predictions for train, validation, test, and Rahimabad hold-out splits.
6. Compute RMSE, MAE, R2, residual summaries, village-wise error, and season-wise error.
7. Select the champion by lowest validation RMSE.
8. Save model artifacts, predictions, metrics, and report files.

## Candidate Models

| Model | Implementation |
|---|---|
| Mean baseline | `DummyRegressor(strategy="mean")` |
| Linear Regression | `LinearRegression` |
| Elastic Net | `ElasticNet` |
| Support Vector Regression | `LinearSVR` |
| Random Forest | `RandomForestRegressor` |
| Gradient Boosting | `GradientBoostingRegressor` |
| MLP | `MLPRegressor` |
| Hybrid rule-guided model | Gradient Boosting plus transparent agronomic adjustment |
| XGBoost | Auto-included if `xgboost` is installed |
| LightGBM | Auto-included if `lightgbm` is installed |

## Hybrid Rule-Guided Adjustment

The hybrid model starts with Gradient Boosting predictions and applies a bounded agronomic adjustment:

```text
clip(
  0.004 * (Soil_Health_Index_Phase6 - 50)
  + 0.003 * (NPK_Balance_Score_Phase6 - 50)
  + 0.002 * (Beneficial_Microbial_Index_Phase6 - 50)
  - 0.0035 * (Pathogen_Load_Index_Phase6 - 50),
  -0.75,
  0.75
)
```

Adjustment unit:

- kg/tree

## Output Decision

The validation split selects the champion because it is not used for fitting. The test split and Rahimabad hold-out split remain diagnostic checks after champion selection.


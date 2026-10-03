# Regression Metrics Definition

## Primary Metrics

| Metric | Formula or meaning | Interpretation |
|---|---|---|
| RMSE | Square root of mean squared error | Penalizes larger errors more strongly |
| MAE | Mean absolute error | Typical absolute prediction error in kg/tree |
| R2 | Coefficient of determination | Fraction of target variance explained relative to mean prediction |

## Residual Diagnostics

Residual is calculated as:

```text
Actual_Mango_Yield - Predicted_Mango_Yield
```

Residual outputs include:

- mean residual
- residual standard deviation
- 5th, 50th, and 95th residual quantiles
- 50th and 95th absolute-error quantiles

These diagnostics are saved in:

- `outputs/metrics/regression/regression_residual_summary.csv`

## Group Error Diagnostics

Village-wise error:

- Tests whether a model performs unevenly across villages.
- Saved in `outputs/metrics/regression/regression_village_wise_error.csv`.

Season-wise error:

- Tests whether model error changes across sampling seasons.
- Saved in `outputs/metrics/regression/regression_season_wise_error.csv`.

## Champion Selection Metric

The champion model is selected by:

```text
minimum validation RMSE
```

Current champion:

- `Linear_Regression`

## Important Caveat

The current dataset is synthetic prototype data. Metrics are useful for pipeline validation and methodology completion, but they should not be interpreted as final agronomic field performance.


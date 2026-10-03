# Phase 7.3 Completion Checklist

| Phase 7.3 task | Status | Evidence |
|---|---|---|
| Read verified Phase 7.1 regression outputs | Complete | `regression_model_metrics.csv`, `champion_regression_model.json` |
| Read verified Phase 7.2 classification outputs | Complete | `classification_model_metrics.csv`, `champion_classification_models.json` |
| Reconcile existing-report model-result claims | Complete | `phase7_reported_vs_reproduced.csv` |
| Summarize verified champions | Complete | `phase7_champion_summary.csv` |
| Summarize Rahimabad hold-out performance | Complete | `phase7_rahimabad_holdout_summary.csv` |
| Create model artifact manifest | Complete | `phase7_model_artifact_manifest.csv` |
| Write complete Phase 7.3 report | Complete | `phase7_complete_model_results_report.md` |
| Write machine-readable summary | Complete | `phase7_model_results_summary.json` |
| Provide executable compiler script | Complete | `src/modeling/phase7_3_compile_model_results.py` |

## Current Phase 7.3 Exit Decision

Phase 7.3 is complete for the currently available synthetic dataset.

## Verified Champions

| Target | Champion | Selection rule |
|---|---|---|
| `Mango_Yield` | `Linear_Regression` | minimum validation RMSE |
| `Disease_Risk` | `Gradient_Boosting` | maximum validation macro F1 |
| `Nutrient_Availability` | `Random_Forest` | maximum validation macro F1 |

## Carry-Forward Notes for Phase 8

- Phase 8 should explain the verified champions, not the older unverified narrative-report champions.
- The `Mango_Yield` champion differs from the existing-report claim.
- `Nutrient_Availability` has no `Deficient` class in the current data.


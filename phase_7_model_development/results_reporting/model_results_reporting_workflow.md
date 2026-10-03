# Model Results Reporting Workflow

## Objective

Create a verified Phase 7 model-results package that is traceable to executable code, saved models, prediction files, and metric outputs.

## Workflow

1. Read Phase 7.1 regression metrics and champion metadata.
2. Read Phase 7.2 classification metrics and champion metadata.
3. Count Rahimabad hold-out samples from the processed feature table.
4. Build a champion summary across all modeled targets.
5. Compare existing-report claims from `Detailed_Research_Work_Outline.md` against reproduced metrics.
6. Build a Rahimabad hold-out summary for the verified champions.
7. Generate a Phase 7 artifact manifest covering scripts, models, metrics, predictions, and reports.
8. Write a complete markdown report and machine-readable JSON summary.

## Reconciliation Rules

When the existing report does not specify a split:

- validation metrics are used for model-comparison claims
- Rahimabad hold-out metrics are used for geographic hold-out claims

Assessment labels:

| Label | Meaning |
|---|---|
| `matched` | Reproduced result agrees within tolerance |
| `near` | Reproduced result is close but not exact |
| `different` | Reproduced result materially differs, or the champion differs |

## Important Decisions

| Topic | Decision |
|---|---|
| Regression champion rule | Lowest validation RMSE |
| Classification champion rule | Highest validation macro F1-score |
| Yield SVM mapping | Existing `SVM` claim maps to implemented `Linear_SVR` |
| Disease SVM mapping | Existing `SVM` claim maps to implemented `Linear_SVM` |
| MLP plus hybrid rules mapping | No exact artifact exists; comparison maps to implemented `Hybrid_Rule_Guided_GB` |
| Rahimabad split | `holdout_rahimabad` |


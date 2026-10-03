# Dashboard Scope

## Included

| Research component | Dashboard support |
|---|---|
| Processed research dataset | Summary cards, filters, distributions, aggregate tables |
| Feature engineering | Phase 6 summary and selected-feature views |
| Model development | Regression and classification metric tables and charts |
| Explainable AI | SHAP importance, SHAP summary images, dependence plots, local explanations |
| Recommendation rules | Phase 8 recommendation-rule table and triggered DSS recommendations |
| Validation | Phase 10 internal CV and Rahimabad hold-out comparison |
| Decision support | Live prediction using champion regression and classification pipelines |
| Artifact access | Local artifact inventory with downloads for text-based outputs |

## Data Sources

| Source | Path |
|---|---|
| Feature table | `data/processed/feature_table.csv` |
| Selected features | `data/processed/selected_features.json` |
| Phase 7 metrics | `outputs/metrics/` |
| Phase 8 XAI outputs | `outputs/explainability/phase8_xai/` |
| Phase 10 validation outputs | `outputs/validation/phase10/` |
| Champion models | `outputs/models/` |

## Runtime

The app is a local Streamlit dashboard. It is intended for research review and prototype decision support, not direct agronomic deployment without real-field validation.

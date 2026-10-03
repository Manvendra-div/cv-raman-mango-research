# DSS Workflow

## Objective

Provide a local tool for orchard-level prediction, explanation, and recommendation generation.

## Backend Flow

1. Receive selected soil, microbiome, climate, orchard, and management features.
2. Validate input with the `DSSInput` schema.
3. Build the model feature table in the same column order used during Phase 7.
4. Run the fitted Phase 7 preprocessing pipelines and champion models.
5. Return:
   - predicted mango yield
   - disease-risk class and probabilities
   - nutrient-availability class and probabilities
   - top SHAP-supported feature explanations from Phase 8
   - triggered recommendation rules
   - links to Phase 8 reference artifacts

## Frontend Flow

1. Load metadata from `/metadata`.
2. Create input controls from feature ranges and categorical options.
3. Submit input to `/predict`.
4. Display predictions as compact cards.
5. Display feature-contribution table and bar chart.
6. Display triggered recommendations.
7. Export Markdown or JSON reports.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Check API status |
| `/metadata` | GET | Return feature schema, ranges, options, and model metadata |
| `/example-input` | GET | Return default example input |
| `/predict` | POST | Return predictions, explanations, and recommendations |
| `/explain` | POST | Return explanation payload only |
| `/recommendations` | POST | Return triggered recommendations only |
| `/report` | POST | Return Markdown report plus prediction payload |

## Source Artifacts

| Artifact | Role |
|---|---|
| `data/processed/selected_features.json` | Feature contract |
| `data/processed/feature_table.csv` | Feature ranges and categorical options |
| `outputs/models/regression/champion_regression_model.joblib` | Yield prediction |
| `outputs/models/classification/champion_disease_risk_model.joblib` | Disease-risk prediction |
| `outputs/models/classification/champion_nutrient_availability_model.joblib` | Nutrient prediction |
| `outputs/explainability/phase8_xai/tables/phase8_global_feature_importance.csv` | Feature contribution context |
| `outputs/explainability/phase8_xai/tables/phase8_recommendation_rules.csv` | Recommendation rules |


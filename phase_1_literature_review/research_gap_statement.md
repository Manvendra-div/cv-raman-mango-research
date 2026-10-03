# Research Gap Statement

## 1. Final Problem Framing

Mango productivity in the Malihabad belt is influenced by soil fertility, microbial diversity, beneficial microbial functions, pathogen pressure, climate stress, orchard management, and tree-level agronomic context. These variables do not act independently. They interact through nonlinear soil-root-microbe processes that are difficult to interpret using conventional soil testing alone.

The central research problem is therefore:

How can soil microbiome composition, soil physicochemical properties, climate variables, orchard metadata, and mango crop-health outcomes be integrated into an interpretable AI framework that predicts yield, disease risk, and nutrient availability for mango orchards in the Malihabad region?

## 2. Evidence-Based Research Gaps

### Gap 1: Mango-specific microbiome prediction is underdeveloped

General plant and soil microbiome research shows that rhizosphere microbial communities influence nutrient cycling, disease suppression, and plant health. Mango-specific evidence also shows that orchard management can alter rhizosphere bacterial communities. However, there is no complete local framework in this workspace that links mango orchard microbiome features to predictive outcomes such as yield, disease risk, and nutrient availability.

Project response:

- Build a mango-specific prediction framework instead of borrowing a generic crop model.
- Use mango-relevant variables: variety, tree age, soil depth, season, management, soil fertility, diversity indices, beneficial groups, pathogen indicators, and village.

### Gap 2: Malihabad-focused AI-ready datasets are missing

The project has a synthetic dataset with 20,000 rows and 63 columns, but it does not yet have raw sequencing files, OTU/ASV tables, taxonomic assignment files, or real field metadata. The real-sample proposal currently defines only 12 composite datasets per year, which is useful for pilot validation but too small for robust ML model training or model refinement.

Project response:

- Treat the current CSV as a pipeline-prototyping dataset.
- Expand the real sampling plan in Phase 2 for real validation and future model refinement.
- Preserve village and orchard identity so that geographic hold-out validation is possible.

### Gap 3: Disease-risk modeling is too broad without disease-specific field labels

The synthetic `Disease_Risk` target is useful for initial classification, and Fusarium is an important mango disease indicator. However, mango disease ecology includes multiple disease pathways, including malformation, anthracnose, root-zone pathogens, post-harvest diseases, and management-related stress symptoms.

Project response:

- Keep `Disease_Risk` as a prototype target.
- In real sampling, add disease-scoring metadata and disease type where feasible.
- Add pathogen-specific features beyond Fusarium when laboratory design allows it.

### Gap 4: Agricultural AI often lacks explanation and actionability

Agricultural ML studies commonly report performance metrics but may not explain why a prediction was made or how it should influence agronomic action. For farmers and extension workers, a correct but opaque prediction is less useful than a prediction linked to soil-health interpretation and management choices.

Project response:

- Use SHAP for global and local feature attribution.
- Use LIME as a local, model-agnostic cross-check.
- Translate explanations into orchard-level recommendation rules with uncertainty labels.

### Gap 5: Existing project claims are not yet reproducible

`Final_Research_Report.md` reports strong model results and a DSS implementation, but the workspace does not contain model training scripts, preprocessing code, saved models, evaluation outputs, SHAP/LIME plots, API files, or dashboard files.

Project response:

- Separate Phase 1 concept finalization from unverified implementation claims.
- Require later phases to produce reproducible scripts, split files, model artifacts, explainability outputs, and DSS code.

### Gap 6: Synthetic data quality issues could bias model conclusions

The outline already identifies negative values in taxonomic abundance fields and a missing `Deficient` class in `Nutrient_Availability`. These issues could produce misleading models if not corrected before training.

Project response:

- Add data validation in Phase 5 before model development.
- Correct or regenerate invalid synthetic values before using the CSV for prototype modeling.
- Align target classes with the final research definitions.

## 3. Final Research Gap Statement

Despite growing evidence that soil microbiomes influence plant health and that machine learning can model complex agricultural systems, there is still a clear gap in mango-specific, Malihabad-focused, microbiome-aware, explainable AI research. Existing evidence supports the biological plausibility of linking soil microbiome and soil-health variables to crop outcomes, but there is no complete, reproducible, locally validated framework that integrates mango orchard metadata, soil chemistry, climate variables, microbial diversity, taxonomic abundance, functional microbial groups, yield records, disease-risk labels, nutrient availability classes, and XAI-based agronomic interpretation.

This research addresses that gap by developing a hybrid AI plus XAI framework for mango soil microbiome analysis and predictive modeling, with explicit separation between synthetic-data prototyping and future real-field validation.

## 4. Final Novelty Statement

The novelty of the work is not only the use of AI for agriculture. The specific novelty is:

1. Crop-specific: focused on mango, not generic crop yield prediction.
2. Place-specific: centered on Malihabad and nearby mango-growing villages.
3. Microbiome-aware: combines microbial diversity, taxonomic abundance, beneficial functional groups, pathogen indicators, soil chemistry, climate, and orchard metadata.
4. Multi-task: predicts yield, disease risk, and nutrient availability rather than a single target.
5. Explainable: uses SHAP and LIME to connect model behavior with agronomic interpretation.
6. Translational: aims to convert predictions into decision-support recommendations for soil health, disease risk, and nutrient management.

## 5. Contribution Boundaries

The project should make claims at three levels:

| Claim level | Allowed in current state? | Condition |
|---|---|---|
| Conceptual contribution | Yes | Supported by Phase 1 literature review and final workflow. |
| Synthetic prototype contribution | Yes, with caveats | Only if invalid values are corrected and scripts reproduce results. |
| Real-field scientific claim | Not yet | Requires field samples, laboratory analysis, real metadata, and validation. |
| Farmer-facing recommendation claim | Not yet | Requires validated model outputs and expert-reviewed recommendation rules. |

## 6. Research Gap Converted Into Implementation Requirements

- Build a data dictionary covering all variables and target definitions.
- Define real sampling strata across village, management, productivity history, variety, tree age, soil depth, and season.
- Use 16S rRNA for bacterial/archaeal profiling and ITS for fungal profiling.
- Generate OTU/ASV, taxonomy, diversity, and functional group outputs from real sequencing data.
- Implement reproducible preprocessing, split generation, feature engineering, training, evaluation, XAI, and reporting scripts.
- Validate internally, geographically, and eventually with real samples.
- Keep all DSS outputs traceable to model version, input data version, and explanation version.

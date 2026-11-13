# Research Paper Outline

## Proposed title

**A Zone-Aware and Explainable Decision Support Framework for Mango Soil–Microbiome Intelligence and Yield-Gap Assessment in Uttar Pradesh, India**

### Alternative title for a software/methods paper

**Design and Leakage-Aware Evaluation of a Soil–Microbiome Decision Support System for Mango Orchards**

---

## Accuracy statement for the manuscript

This outline is based on the current repository and its reproducible artifacts. The current executable dataset is a **synthetic prototype**, not a collection of measured field observations. Therefore:

- Synthetic results must be reported as **method-development or software-validation results**.
- They must not be presented as evidence of real orchard performance, biological causation, or guaranteed yield improvement.
- No claim of intervention effectiveness should be made until independent field measurements or a properly designed intervention study are available.
- The approximately 10,000-row dataset requested for a future study is **not currently present**. The repository currently uses the 20,000-row dataset described below.

The paper should not use the older `Final_Research_Report.md` as a source of numerical results without checking the underlying artifacts. Its claims about the yield champion, near-perfect performance, field viability, and causal interpretation are not consistent with the current verified outputs.

---

# 1. Abstract

Write the abstract only after the final analysis is frozen. Use the following structure:

### 1.1 Background

Mango productivity and disease risk may vary with soil chemistry, microbial indicators, climate, orchard characteristics, and management. A decision support system must combine these data while preserving interpretability and evaluating geographic generalization.

### 1.2 Objective

State that the study develops a prototype, zone-aware, explainable framework for:

1. Predicting mango yield.
2. Classifying disease risk.
3. Classifying nutrient availability.
4. Comparing observations with zone-specific reference benchmarks.
5. Presenting model explanations and cautious recommendations.

### 1.3 Methods

State the dataset size and provenance accurately:

- 20,000 rows in `data/raw/mango_microbiome_dataset.csv`.
- 63 original columns.
- 50 orchard identifiers.
- Four village labels: Malihabad, Rahimabad, Kakori, and Mall.
- Synthetic data generated with seed 42 for pipeline development.
- Model inputs selected from the training data and processed through the project pipeline.
- Geographic hold-out: Rahimabad.
- Orchard-aware validation: GroupKFold by `Orchard_ID`.

### 1.4 Results

Report only the final regenerated metrics. The current verified artifacts show:

- The selected regression champion in `phase7_champion_summary.csv` is **Linear Regression**, with validation RMSE 1.993, test RMSE 2.009, and geographic hold-out RMSE 1.984.
- The selected disease-risk champion is **Gradient Boosting**, with geographic hold-out macro-F1 0.990.
- The selected nutrient-availability champion is **Random Forest**, with geographic hold-out macro-F1 0.9998.
- These classification results are strongly affected by synthetic target-generation rules and must not be interpreted as field-level accuracy.

These values must be updated if the approximately 10,000-row subset is created and the models are retrained.

### 1.5 Conclusion

Conclude only that the repository demonstrates a reproducible prototype workflow. State that real orchard measurements are required before assessing agronomic validity or deployment performance.

---

# 2. Introduction

## 2.1 Agricultural and scientific context

Discuss:

- The importance of mango production in Uttar Pradesh.
- Variation in orchard productivity and disease pressure.
- The contribution of soil fertility, salinity, texture, moisture, microbial diversity, pathogen indicators, climate, variety, tree age, and management.
- The difficulty of interpreting high-dimensional soil and microbiome data.

Do not assign a measured effect size unless it is supported by a cited field study or the current dataset analysis.

## 2.2 Decision-support problem

Describe the practical need for a system that can:

- Estimate yield as a model output.
- Classify disease risk and nutrient availability.
- Explain which input variables contributed to a prediction.
- Compare an orchard with appropriate local reference observations.
- Separate measured deficiencies from model associations.
- Avoid prescribing fertilizer doses from feature importance alone.

## 2.3 Research gap

Present the gaps addressed by the framework:

1. Joint analysis of soil, microbiome, climate, and orchard variables.
2. Geographic hold-out evaluation rather than only random row-level splitting.
3. Orchard-grouped validation for correlated observations.
4. Explicit separation of prediction, explanation, benchmark comparison, and recommendation rules.
5. Farmer-facing reporting with uncertainty and synthetic-data warnings.

## 2.4 Study objectives

### Primary objective

To design and evaluate a reproducible, zone-aware, explainable decision support prototype for mango soil and yield-gap analysis.

### Secondary objectives

1. Prepare and validate a compatible soil–microbiome dataset.
2. Develop yield, disease-risk, and nutrient-availability models.
3. Evaluate generalization to a geographically held-out village.
4. Evaluate orchard-grouped performance.
5. Generate SHAP and LIME explanations with explicit limitations.
6. Translate measured-value rules into cautious recommendations.

## 2.5 Research questions

1. Can the pipeline produce reproducible predictions from the integrated soil–microbiome schema?
2. How do model results differ between random/internal, orchard-grouped, and geographic validation?
3. Which variables are important to the fitted models for each target?
4. Can model explanations be communicated without presenting association as causation?
5. Can a zone-aware DSS present useful diagnostic information while clearly stating the limitations of synthetic data?

---

# 3. Materials and Methods

## 3.1 Study setting

Describe the intended study geography:

- Malihabad, Uttar Pradesh
- Rahimabad, Uttar Pradesh
- Kakori, Uttar Pradesh
- Mall, Uttar Pradesh

Clarify that these labels are present in the synthetic prototype. Their presence does not establish that the rows are measured observations from those locations.

## 3.2 Dataset provenance and status

### Primary raw file

`data/raw/mango_microbiome_dataset.csv`

Verified profile:

| Property | Current value |
|---|---:|
| Rows | 20,000 |
| Columns | 63 |
| Missing cells | 0 in the current raw audit |
| Duplicate rows | 0 in the current raw audit |
| Orchard IDs | 50 |
| Villages | 4 |
| Rows per orchard in raw file | 400 |
| Data status | Synthetic prototype |
| Generator seed | 42 |

The raw file is treated as immutable. The processed file is:

`data/processed/clean_master_dataset.csv`

The model feature table is:

`data/processed/feature_table.csv`

It contains 20,000 rows and 84 columns after feature engineering and split metadata.

## 3.3 Dataset fields

Describe the six groups of variables:

1. Sample, orchard, location, variety, age, depth, season, and management metadata.
2. Soil physicochemical measurements.
3. Climate variables.
4. Diversity and microbiome variables.
5. Engineered soil, nutrient, pathogen, and microbial indicators.
6. Prediction targets.

The original targets are:

- `Mango_Yield` — regression target in kg/tree.
- `Disease_Risk` — Low, Medium, or High.
- `Nutrient_Availability` — Deficient, Optimal, or High.

## 3.4 Planned approximately 10,000-row study subset

If the paper is based on an approximately 10,000-row subset, describe it as a new analysis dataset, not as the current raw dataset.

The subset protocol must:

1. Preserve all required raw columns.
2. Preserve `Orchard_ID` and `Sample_ID`.
3. Use a documented random seed.
4. Sample by orchard rather than taking the first 10,000 rows.
5. Preserve village, variety, season, management, and target distributions as far as possible.
6. Keep the Rahimabad geographic hold-out intact.
7. Re-run cleaning, feature engineering, feature selection, model training, XAI, and validation.
8. Store the subset separately, for example under `data/interim/` or `data/processed/`.
9. Record the exact row-selection manifest.
10. Report the final row count, because “approximately 10,000” is not an exact sample size.

Do not claim that a 10,000-row analysis has been completed until the subset, manifest, models, and metrics exist.

## 3.5 Data quality assessment

Report:

- Missing values.
- Duplicate rows and duplicate identifiers.
- Numeric ranges.
- Categorical levels.
- Taxonomic abundance constraints.
- Yield distribution.
- Class distributions.
- Orchard-level row counts.
- Village-level row counts.

The current audit identifies two major limitations that must be discussed:

1. `Disease_Risk` is generated using thresholds of `Pathogen_Load_Index`.
2. `Nutrient_Availability` is generated using thresholds of `Nutrient_Balance_Ratio`.

These relationships create target leakage or near-deterministic target structure. Very high classification performance is therefore not evidence of real-world disease or nutrient prediction ability.

## 3.6 Preprocessing

Describe:

- Raw-to-processed cleaning.
- Numeric feature handling.
- Categorical encoding.
- Scaling where used by a model pipeline.
- Missing-value policy.
- Feature-name preservation.
- Artifact versioning.

State explicitly that preprocessing must be fitted on training data only for every validation split.

## 3.7 Feature engineering

Document the formulas and rationale for engineered variables, including:

- Diversity indicators.
- Richness/evenness balance.
- Beneficial microbial index.
- Nutrient cycling index.
- Biocontrol index.
- Pathogen load index.
- Pathogen-to-beneficial ratio.
- NPK balance score.
- Micronutrient balance score.
- Soil physical condition score.
- Soil chemical fertility score.
- Climate comfort score.
- Soil health index.

For every engineered variable, state whether it is measured, calculated from measured variables, or derived from a target-generating rule. Do not describe engineered features as independent biological observations.

## 3.8 Feature selection

The current metadata state that feature selection was performed using the training split, with a maximum of 34 selected numeric features and five categorical features used for encoding. The paper should report the exact feature-selection procedure used in the final run.

Feature selection must be performed inside the training portion of each validation fold. The geographic hold-out must not influence selection.

## 3.9 Prediction tasks

### 3.9.1 Yield regression

Target: `Mango_Yield`.

Report:

- RMSE.
- MAE.
- R².
- Mean baseline comparison.
- Internal validation.
- Orchard-grouped validation.
- Geographic hold-out validation.

### 3.9.2 Disease-risk classification

Target: `Disease_Risk`.

Report:

- Accuracy only as a supplementary metric.
- Balanced accuracy.
- Macro precision.
- Macro recall.
- Macro F1.
- Per-class metrics.
- Confusion matrix.

Emphasize that the synthetic disease labels are threshold-derived.

### 3.9.3 Nutrient-availability classification

Target: `Nutrient_Availability`.

Report the same classification metrics and class-specific results. Explicitly report class imbalance and threshold-derived labels.

## 3.10 Candidate models

Describe the candidate families actually run in the final experiment:

- Mean baseline.
- Linear regression or Elastic Net.
- Logistic regression for classification.
- Random Forest.
- Gradient Boosting.
- Linear SVM or SVR.
- Other models only if their artifacts and metrics are available.

Do not list a model as evaluated unless its final metrics can be reproduced from the repository.

## 3.11 Validation design

### Internal validation

Use the project’s training/validation/test design and report how all model choices were made.

### Orchard-grouped validation

Use `Orchard_ID` as the grouping variable. Observations from one orchard must not be split across training and validation folds when estimating orchard-level generalization.

### Geographic hold-out

The current design trains on:

- Malihabad
- Kakori
- Mall

and holds out:

- Rahimabad

The current geographic hold-out contains 5,059 rows after processing. This number is not the same as the 5,000 rows per village in the raw generated file because processing and split construction changed the row allocation.

No transformation, feature-selection decision, or threshold calibration may use Rahimabad observations.

## 3.12 Explainable AI

Use SHAP and LIME to explain the fitted models.

Each explanation should include:

- The prediction.
- The baseline or reference prediction.
- Positive contributions.
- Negative contributions.
- Input values.
- Feature definitions.
- Model-specific limitations.

State that SHAP and LIME explain the model’s behavior. They do not prove causation, deficiency, treatment response, or fertilizer dose.

## 3.13 Zone intelligence and yield-gap analysis

Describe the zone modules as a benchmark and comparison layer, not as a causal model.

The current system uses:

- Same-village and same-variety matching where possible.
- Tree-age and management context.
- Median, mean, Q75, and top-10-mean reference statistics.

Define Q75 as an observed attainable benchmark within the reference group, not as biological potential. Define the yield gap as a descriptive difference from that benchmark.

## 3.14 Recommendation rules

Recommendations must be triggered by measured values compared with documented reference ranges. The paper must distinguish:

1. Measured deficiency.
2. Negative model contribution.
3. Difference from peers.
4. Potential action to discuss.
5. Proven causal limitation.

The current DSS does not establish the fifth category. Recommendations must not prescribe fertilizer doses from SHAP rankings.

## 3.15 Software implementation

Describe:

- Python data and modeling pipeline.
- FastAPI backend.
- Streamlit dashboard.
- `/predict`, `/zone-analysis`, `/explain`, `/recommendations`, and `/report` services.
- Markdown and JSON report export.
- Test suite and smoke tests.

Include the repository commit or release identifier in the final paper.

---

# 4. Results

This section must be populated from the final frozen run. Do not copy values from older reports if they disagree with current artifacts.

## 4.1 Dataset description

Recommended table:

| Item | Value |
|---|---:|
| Raw rows | 20,000 currently; replace if 10,000-row subset is finalized |
| Original columns | 63 |
| Processed feature-table columns | 84 |
| Orchards | 50 |
| Villages | 4 |
| Missing cells | 0 in current raw audit |
| Duplicate rows | 0 in current raw audit |
| Data provenance | Synthetic prototype |

## 4.2 Target distributions

Report the final counts and percentages for:

- Mango yield summary statistics.
- Disease-risk classes.
- Nutrient-availability classes.

Include a warning that class balance and target distributions are properties of the synthetic generator.

## 4.3 Model performance

Use separate tables for regression and classification.

### Current verified reference values

These values describe the present 20,000-row artifacts and must be replaced after any 10,000-row retraining:

| Task | Selected model | Validation primary | Test primary | Geographic hold-out primary |
|---|---|---:|---:|---:|
| Mango yield | Linear Regression | RMSE 1.993 | RMSE 2.009 | RMSE 1.984 |
| Disease risk | Gradient Boosting | Macro-F1 0.990 | Macro-F1 0.993 | Macro-F1 0.990 |
| Nutrient availability | Random Forest | Macro-F1 1.000 | Macro-F1 1.000 | Macro-F1 0.9998 |

The current geographic regression result for the selected linear model is:

- MAE: 1.594 kg/tree.
- R²: 0.273.
- Hold-out village: Rahimabad.
- Training rows: 14,941.
- Hold-out rows: 5,059.

These are synthetic-prototype evaluation results. They do not demonstrate real-world accuracy.

## 4.4 Internal versus geographic performance

Report the difference between internal and geographic performance. Discuss whether the difference is small, large, or model-dependent. Do not call stable synthetic hold-out performance “field validation.”

## 4.5 Explainability results

Show:

- Global importance plots.
- Local explanation examples.
- Baseline-to-prediction contribution plots.
- Agreement and disagreement between SHAP and LIME.

Use wording such as “the model assigned a contribution” rather than “the feature caused.”

## 4.6 DSS outputs

Demonstrate:

- Prediction response.
- Zone-analysis response.
- Recommendation response.
- Full Markdown report.
- Bilingual farmer explainer.

Do not present a counterfactual yield bar as an observed or guaranteed yield increase.

---

# 5. Discussion

## 5.1 Main findings

Discuss the final results in relation to the research questions. Separate:

- What the prototype demonstrates technically.
- What the synthetic data permit the model to learn.
- What remains unknown about real orchards.

## 5.2 Interpretation of yield performance

The current verified yield model explains only a limited proportion of hold-out variance, with geographic R² of approximately 0.273. Discuss this conservatively. Do not describe the model as highly accurate or as a reliable production predictor.

## 5.3 Interpretation of classification performance

The very high disease-risk and nutrient-availability scores are expected to be influenced by deterministic or near-deterministic synthetic label rules. They should be treated as evidence that the software can reproduce the synthetic labeling structure, not as evidence of field diagnostic performance.

## 5.4 Geographic generalization

Discuss Rahimabad as a simulated geographic hold-out. It is not an independent real-world external validation site unless real observations are collected and documented.

## 5.5 Orchard correlation and pseudo-replication

Explain that the raw dataset contains 400 rows per orchard and that rows from the same orchard may not be independent. Report grouped validation and acknowledge that row-level results can be optimistic.

## 5.6 Explainability and agronomic interpretation

Discuss how SHAP and LIME improve transparency while emphasizing that explanation does not equal causation. Explain why model ranking cannot be converted directly into fertilizer dosage or treatment prescriptions.

## 5.7 Practical value of the DSS

The system may support:

- Data review.
- Soil-test interpretation.
- Field inspection prioritization.
- Zone-aware comparison.
- Research data collection.

It should not be described as replacing laboratory diagnosis, an agronomist, or field experimentation.

## 5.8 Comparison with previous studies

Use published literature for comparison. Compare:

- Sampling design.
- Soil and microbiome methods.
- Target definitions.
- Validation design.
- Geographic scale.
- Model metrics.

Do not compare synthetic-prototype accuracy directly with field-study accuracy without explaining the difference in data provenance.

---

# 6. Limitations

This subsection is required and should include at least the following:

1. The current dataset is synthetic.
2. There are no completed real-sample validation rows in the repository.
3. There are no completed field-intervention observations.
4. Disease-risk labels are threshold-derived from pathogen-load information.
5. Nutrient-availability labels are threshold-derived from nutrient-balance information.
6. Orchard observations are correlated and may represent pseudo-replication.
7. The current yield model has modest geographic R².
8. Local agronomic thresholds require field and laboratory calibration.
9. SHAP and LIME do not establish causal mechanisms.
10. What-if yield estimates are model counterfactuals, not measured treatment responses.
11. Q75 and top-10-mean are observed reference benchmarks, not biological potential.
12. Results from the current 20,000-row dataset cannot automatically be transferred to a future 10,000-row subset.

---

# 7. Future Work

## 7.1 Real field dataset

Collect paired observations of:

- Soil chemistry.
- 16S and ITS microbiome measurements.
- Orchard metadata.
- Disease observations.
- Measured yield in kg/tree.
- Management and intervention records.

## 7.2 Improved sampling design

Prioritize independent orchards over repeated rows from a small number of orchards. Stratify by village, variety, age, management, and season.

## 7.3 External validation

Evaluate the frozen model on a separate set of orchards and seasons that were not used for model selection.

## 7.4 Intervention evaluation

Use a suitable controlled or quasi-experimental design before claiming that a recommended action increases yield.

## 7.5 Dataset revision

If the approximately 10,000-row dataset becomes the main analysis set, regenerate:

- Processed data.
- Splits.
- Selected features.
- Models.
- Metrics.
- SHAP and LIME artifacts.
- DSS metadata.
- Reports.

---

# 8. Conclusion

The paper should conclude that the project provides a reproducible prototype for integrating soil, microbiome, climate, orchard, and zone information into an explainable mango decision support workflow. It should not conclude that the system has been field validated, that the identified features are causal, or that the suggested actions will produce a guaranteed yield increase. Those claims require measured field data and intervention evaluation.

---

# 9. Declarations

## 9.1 Data availability

State that the current repository contains a synthetic prototype dataset and that real field-validation inputs are currently pending. If real data are later collected, describe access restrictions and anonymization.

## 9.2 Code availability

List the repository, commit identifier, environment file, data-validation scripts, modeling scripts, API, dashboard, and test command.

## 9.3 Funding

Insert verified funding information only. Do not invent a funding source.

## 9.4 Conflict of interest

Insert an accurate declaration from the authors.

## 9.5 Ethics and permissions

For future field data, document orchard-owner permission, sample handling, geographic privacy, and laboratory approvals where applicable.

## 9.6 Author contributions

Complete using the journal’s required taxonomy.

---

# 10. Tables to prepare

1. Dataset variables and definitions.
2. Dataset-quality audit.
3. Village, orchard, variety, season, and management distribution.
4. Target distributions.
5. Candidate-model performance.
6. Internal, orchard-grouped, and geographic validation comparison.
7. Feature-engineering definitions.
8. Global explanation results.
9. Recommendation-rule definitions and evidence levels.
10. Real-data validation status.

# 11. Figures to prepare

1. Study workflow diagram.
2. Dataset and software architecture.
3. Village and orchard distribution map, only if geographic data are appropriate to publish.
4. Soil and microbiome exploratory distributions.
5. Target distributions.
6. Model-performance comparison.
7. Geographic hold-out workflow.
8. SHAP global summary.
9. Local explanation example.
10. Zone benchmark and yield-gap visualization.
11. DSS interface screenshot.
12. Farmer-facing bilingual explanation screenshot.

# 12. Reproducibility checklist

- [ ] Raw dataset identified and preserved as immutable.
- [ ] Data provenance labelled synthetic or measured.
- [ ] Dataset row and column counts verified.
- [ ] Approximately 10,000-row subset manifest created, if used.
- [ ] Random seeds recorded.
- [ ] Preprocessing fitted inside training data only.
- [ ] Feature selection performed inside training data only.
- [ ] Orchard groups kept separate during grouped validation.
- [ ] Rahimabad hold-out kept untouched until final evaluation.
- [ ] Model versions and package versions recorded.
- [ ] All final metrics regenerated from the final dataset.
- [ ] Target leakage tested and reported.
- [ ] SHAP and LIME limitations stated.
- [ ] No causal claims made from observational or synthetic associations.
- [ ] No fertilizer doses derived from SHAP rankings.
- [ ] Real-world validation status reported honestly.
- [ ] Code, reports, and artifact paths recorded.

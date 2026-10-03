# Final Objectives and Research Questions

## 1. Final Aim

To design, implement, evaluate, and explain a hybrid AI framework that integrates soil physicochemical properties, soil microbiome indicators, climate variables, orchard metadata, and agronomic outcomes to predict mango yield, disease risk, and nutrient availability for mango orchards in the Malihabad region of Uttar Pradesh.

## 2. Final Scientific Objectives

1. Characterize the soil-health and microbiome indicators most relevant to mango orchard productivity and disease risk.
2. Integrate mango orchard metadata, soil physicochemical parameters, climate variables, microbial diversity indices, taxonomic abundance, functional microbial groups, and target variables into a unified research dataset.
3. Identify soil, microbial, climate, and management predictors that are most strongly associated with mango yield, disease risk, and nutrient availability.
4. Evaluate whether microbiome-aware and engineered soil-health features improve predictive performance over soil-only baselines.
5. Interpret model behavior using explainable AI and translate key predictors into agronomically meaningful insights.

## 3. Final Technical Objectives

1. Create a reproducible data architecture for raw, interim, processed, and modeling-ready data.
2. Validate and clean the current synthetic dataset before prototype modeling.
3. Build feature engineering routines for `Microbial_Richness_Score`, `Nutrient_Balance_Ratio`, `Pathogen_Load_Index`, and `Soil_Health_Index`.
4. Train and compare regression models for `Mango_Yield`.
5. Train and compare classification models for `Disease_Risk` and `Nutrient_Availability`.
6. Evaluate internal test performance and geographic hold-out performance.
7. Generate SHAP and LIME explanations at global and local levels.
8. Produce recommendation rules linked to model outputs, explanation patterns, and agronomic thresholds.
9. Build a decision-support prototype only after the prediction and explanation pipeline is reproducible.

## 4. Final Practical Objectives

1. Support orchard-level soil-health interpretation for mango growers and agronomists.
2. Identify early risk indicators for disease-prone or low-yield orchards.
3. Help prioritize soil amendments, microbial interventions, nutrient management, and sampling follow-up.
4. Reduce unnecessary chemical input by supporting targeted and explainable recommendations.
5. Provide a research foundation for a future farmer-facing decision support system.

## 5. Final Research Questions

### RQ1: Soil and yield

Which soil physicochemical parameters are most associated with mango yield in the Malihabad mango orchard dataset?

Expected analysis:

- Correlation and mutual-information screening.
- Model-based feature importance.
- SHAP dependence analysis for pH, EC, organic carbon, N, P, K, CEC, soil moisture, and micronutrients.

### RQ2: Microbiome and soil health

Which microbial diversity indices, taxonomic groups, and functional microbial groups are most predictive of soil health and mango productivity?

Expected analysis:

- Feature-group comparison between soil-only, microbiome-only, and combined models.
- Diversity-index analysis using OTU/ASV-derived metrics when real data are available.
- SHAP summary plots for diversity and functional group features.

### RQ3: Disease risk

How strongly do pathogen indicators, especially Fusarium and the `Pathogen_Load_Index`, influence mango disease-risk classification?

Expected analysis:

- Class-wise feature importance.
- Confusion matrix by disease-risk category.
- SHAP analysis of High-risk predictions.
- Real-field disease scoring in later validation.

### RQ4: Feature engineering

Do engineered features such as `Soil_Health_Index`, `Microbial_Richness_Score`, `Nutrient_Balance_Ratio`, and `Pathogen_Load_Index` improve prediction performance and interpretability?

Expected analysis:

- Model comparison with and without engineered features.
- Leakage check to ensure engineered features are not directly derived from target labels.
- Stability analysis across train/test and geographic hold-out splits.

### RQ5: Model family comparison

Do tree-based ensemble models outperform linear baselines, SVM/SVR, and neural baselines on structured mango soil-microbiome data?

Expected analysis:

- Regression metrics: RMSE, MAE, R-squared.
- Classification metrics: accuracy, macro F1, precision, recall, confusion matrix.
- Calibration analysis for classification probabilities.

### RQ6: Explainability

Can SHAP and LIME translate model predictions into explanations that are meaningful to agronomists and usable in decision support?

Expected analysis:

- Global feature rankings.
- Local explanation reports for selected orchards.
- Consistency check between SHAP, LIME, and agronomic expectations.
- Expert review before farmer-facing use.

### RQ7: Geographic generalization

Does a model trained on multiple mango-growing villages generalize to a held-out village such as Rahimabad?

Expected analysis:

- Train on all villages except the held-out village.
- Test on the held-out village.
- Compare error and classification metrics against internal validation.
- Report village-wise residual and misclassification patterns.

### RQ8: Real-world validation

What real-world sampling design is required to validate and refine the synthetic-data prototype?

Expected analysis:

- Minimum sample-size plan by village, management type, season, soil depth, tree age, and yield history.
- Pilot validation using real soil and microbiome samples.
- Multi-season expansion for model refinement.

## 6. Final Working Hypotheses

1. Higher soil health and balanced nutrient availability are positively associated with mango yield.
2. Higher pathogen load is positively associated with higher disease-risk classification.
3. Microbial richness and beneficial microbial functional groups improve prediction when combined with soil physicochemical parameters.
4. Tree-based ensemble models will perform strongly on the structured tabular prototype dataset.
5. Geographic hold-out validation will be more realistic than random-only test splitting.
6. SHAP and LIME can identify agronomically interpretable predictors, but explanation outputs must be treated as model explanations rather than causal proof.
7. Real-field validation will reveal differences between synthetic assumptions and actual orchard behavior.

## 7. Target Definitions for Later Phases

| Target | Task type | Final definition requirement |
|---|---|---|
| `Mango_Yield` | Regression | kg/tree or equivalent standardized yield measure with date/season context. |
| `Disease_Risk` | Classification | Low, Medium, High based on a documented disease-scoring protocol or validated pathogen/disease indicators. |
| `Nutrient_Availability` | Classification | Deficient, Optimal, High based on soil-test thresholds and agronomic interpretation. |

## 8. Evaluation Commitments

The project should not report final model claims without:

- A fixed data split strategy.
- A geographic hold-out evaluation.
- Baseline model comparison.
- Saved preprocessing pipeline.
- Saved model artifacts.
- Versioned metric outputs.
- SHAP/LIME explanation outputs.
- Clear separation of synthetic prototype results and real-sample validation results.

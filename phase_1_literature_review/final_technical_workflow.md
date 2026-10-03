# Final Technical Workflow

This workflow is the Phase 1 technical blueprint for the full research project. It translates the finalized literature review, gap statement, objectives, and research questions into a reproducible implementation path.

## 1. Workflow Principle

Every reported result must be traceable to:

1. A data source.
2. A preprocessing version.
3. A feature set.
4. A split strategy.
5. A model version.
6. A metric output.
7. An explanation output.
8. A recommendation rule or report version, if used in the DSS.

## 2. End-to-End Pipeline

```text
Phase 1 concept finalization
  -> Phase 2 sampling design
  -> Phase 3 soil and microbiome data collection
  -> Phase 4 laboratory and bioinformatics analysis
  -> Phase 5 data integration and preprocessing
  -> Phase 6 feature engineering
  -> Phase 7 predictive modeling
  -> Phase 8 explainable AI
  -> Phase 9 decision support prototype
  -> Phase 10 validation and refinement
```

## 3. Data Architecture

Recommended project data layout:

```text
data/
  raw/
    mango_microbiome_dataset.csv
    field_metadata/
    lab_soil_tests/
    sequencing_reads/
  interim/
    cleaned_metadata/
    soil_qc/
    microbiome_qc/
    otu_or_asv_tables/
    taxonomy_tables/
  processed/
    master_dataset.csv
    data_dictionary.csv
    feature_table.csv
  splits/
    train.csv
    validation.csv
    test.csv
    holdout_rahimabad.csv
outputs/
  eda/
  models/
  metrics/
  explainability/
  recommendations/
  reports/
src/
  data_validation/
  preprocessing/
  feature_engineering/
  modeling/
  explainability/
  recommendation_rules/
  dss/
```

Current workspace status:

- `data/raw/mango_microbiome_dataset.csv` exists.
- Real field metadata, lab soil tests, sequencing reads, OTU/ASV tables, taxonomy tables, scripts, saved models, and explanation outputs do not yet exist.

## 4. Study Design Inputs for Phase 2

Phase 2 should preserve the following variables from the current conceptual design:

| Design axis | Required levels or fields |
|---|---|
| Village/geography | Malihabad, Rahimabad, Kakori, Mall, and any added local village labels |
| Orchard identity | Stable `Orchard_ID`, GPS coordinates, orchard size, owner/manager code if consented |
| Variety | Dashehari/Dusseheri spelling standardized, Langra, Chausa, Safeda, and any local variety |
| Tree context | Tree age, canopy condition, productivity history |
| Soil depth | 0-15 cm and 15-30 cm where feasible |
| Season | Pre-monsoon, monsoon/post-monsoon, winter, and phenological stage |
| Management | Organic, conventional, integrated; fertilizer, pesticide, irrigation history |
| Disease status | Disease score, observed symptoms, disease type if identifiable |
| Yield status | kg/tree, kg/orchard, or standardized productivity class with measurement date |

## 5. Laboratory and Bioinformatics Workflow

For real microbiome data, the final workflow should use:

1. 16S rRNA sequencing for bacteria and archaea.
2. ITS sequencing for fungi.
3. Quality control and denoising, preferably with QIIME 2 and DADA2 or a documented equivalent.
4. Taxonomic assignment using SILVA or an equivalent for 16S rRNA data.
5. Taxonomic assignment using UNITE or an equivalent for ITS data.
6. Alpha-diversity metrics such as observed ASVs/OTUs, Shannon index, Simpson index, Chao1 richness, and Pielou evenness.
7. Beta-diversity and ordination for exploratory analysis, not as a substitute for predictive validation.
8. Functional group mapping for agronomically relevant taxa where supported by literature or expert rules.

## 6. Data Validation Gates

Before any model is trained, apply these checks:

| Check | Rule |
|---|---|
| Missing values | Report by column and decide imputation by feature type. |
| Duplicate rows | Remove or justify duplicates. |
| ID uniqueness | `Sample_ID` must be unique. |
| Numeric ranges | Validate pH, EC, organic carbon, NPK, moisture, texture, micronutrients, diversity indices, and taxonomic abundance. |
| Compositional values | Taxonomic relative abundance must not be negative. Domain-level relative abundance should follow documented normalization rules. |
| Categorical classes | Target classes must match final definitions. |
| Leakage check | Engineered features must not encode target labels directly. |
| Encoding quality | Fix text-encoding issues such as mojibake in soil-depth labels before analysis. |

Known current synthetic-data issues to fix before modeling:

- Negative values in `Zygomycota`.
- Negative values in `Bacteroidetes`.
- Missing `Deficient` class in `Nutrient_Availability`.
- Text-encoding issue in soil-depth values, where dash characters appear incorrectly in the CSV preview.

## 7. Feature Groups

Use feature-group experiments to answer whether microbiome-aware modeling adds value.

| Feature group | Example columns |
|---|---|
| Metadata | Village, orchard, latitude, longitude, variety, tree age, soil depth, season, management |
| Soil physicochemical | pH, EC, organic carbon, N, P, K, moisture, temperature, bulk density, CEC, texture, micronutrients, C:N ratio |
| Climate | air temperature, rainfall, humidity, solar radiation |
| Diversity | OTU/ASV count, Shannon, Simpson, Chao1, Pielou |
| Taxonomy | Proteobacteria, Actinobacteria, Acidobacteria, Firmicutes, Bacteroidetes, Ascomycota, Basidiomycota, Glomeromycota, Mortierellomycota, Zygomycota, Thaumarchaeota, Euryarchaeota |
| Functional microbes | nitrogen fixers, phosphate solubilizers, potassium solubilizers, AMF, Trichoderma, Pseudomonas PGPR, Fusarium |
| Engineered features | microbial richness score, nutrient balance ratio, pathogen-load index, soil-health index |

## 8. Model Development Workflow

### 8.1 Regression: Mango Yield

Target:

- `Mango_Yield`

Candidate models:

- Mean/median baseline.
- Linear Regression or Elastic Net.
- Support Vector Regression.
- Random Forest Regressor.
- Gradient Boosting Regressor.
- XGBoost or LightGBM if project policy and package availability allow.
- MLP Regressor as a neural baseline.
- Hybrid rule-guided model only after baseline ML results are established.

Metrics:

- RMSE.
- MAE.
- R-squared.
- Residual distribution.
- Village-wise error.
- Season-wise error.
- Management-wise error.

### 8.2 Classification: Disease Risk

Target:

- `Disease_Risk`

Candidate models:

- Majority-class baseline.
- Logistic Regression.
- Support Vector Machine.
- Random Forest Classifier.
- Gradient Boosting Classifier.
- XGBoost or LightGBM if allowed.
- MLP Classifier as a neural baseline.
- Hybrid ML plus agronomic rules.

Metrics:

- Accuracy.
- Macro F1.
- Precision and recall by class.
- Confusion matrix.
- ROC-AUC or one-vs-rest AUC if class probabilities are calibrated and suitable.
- Calibration curve.

### 8.3 Classification: Nutrient Availability

Target:

- `Nutrient_Availability`

Important condition:

- Do not report a final three-class nutrient model until `Deficient`, `Optimal`, and `High` are all represented or a justified two-class target is explicitly defined.

Metrics:

- Accuracy.
- Macro F1.
- Class-wise precision and recall.
- Confusion matrix.
- Calibration curve.

## 9. Split Strategy

Use three split types:

1. Random stratified split for initial benchmarking.
2. Cross-validation for internal robustness.
3. Geographic hold-out split for external-style validation.

Recommended hold-out:

- Hold out Rahimabad for geographic validation because the current dataset has a large Rahimabad subset.

Split rules:

- For classification, stratify by target class when feasible.
- Keep all rows from a held-out village out of training.
- Consider orchard-level grouping to avoid leakage when repeated samples from the same orchard exist.
- Store split membership files in `data/splits/`.

## 10. Explainable AI Workflow

### 10.1 Global Explanations

Use:

- Tree-based feature importance as a quick diagnostic.
- SHAP summary plots for final champion models.
- SHAP dependence plots for important variables such as `Soil_Health_Index`, `Pathogen_Load_Index`, pH, EC, available P, available K, total nitrogen, microbial richness, `Fusarium`, `Trichoderma`, and `Pseudomonas_PGPR`.

Output:

- `outputs/explainability/shap_summary_yield.png`
- `outputs/explainability/shap_summary_disease.png`
- `outputs/explainability/shap_dependence_*.png`
- `outputs/explainability/global_explanation_report.md`

### 10.2 Local Explanations

Use:

- SHAP waterfall plots for selected orchard predictions.
- LIME local explanations as a model-agnostic cross-check.

Output:

- `outputs/explainability/local_case_<Sample_ID>.md`
- `outputs/explainability/local_case_<Sample_ID>_shap.png`
- `outputs/explainability/local_case_<Sample_ID>_lime.html`

### 10.3 Explanation Interpretation Rules

Explanations must be labelled as:

- Model behavior, not direct causal proof.
- Agronomic signals requiring expert interpretation.
- Actionable only when linked to validated thresholds and field context.

## 11. Recommendation Rule Layer

Recommendation rules should be separate from ML models.

Example rule categories:

| Signal | Possible recommendation direction |
|---|---|
| Low organic carbon and low soil-health index | Increase organic matter inputs, compost, mulch, or cover-crop strategy after agronomist review. |
| High pathogen-load index and high Fusarium | Recommend disease scouting, sanitation review, and pathogen-specific lab confirmation. |
| Low microbial richness and low beneficial functional groups | Recommend soil biological restoration strategy and management review. |
| Nutrient imbalance | Recommend soil-test-based nutrient correction rather than blanket fertilizer use. |
| High EC | Flag possible salinity stress and irrigation/drainage assessment. |

Each recommendation should include:

- Triggering features.
- Threshold or model explanation evidence.
- Confidence level.
- Required follow-up measurement.
- Expert review status.

## 12. Decision Support System Boundary

The DSS should not be built as a final deliverable until the following exist:

- Clean master dataset.
- Data dictionary.
- Preprocessing script.
- Feature-engineering script.
- Trained model artifacts.
- Evaluation metrics.
- SHAP/LIME explanation outputs.
- Recommendation rule file.
- Example input and output cases.

When ready, the DSS can include:

- FastAPI backend for prediction, explanation, and recommendation endpoints.
- Streamlit frontend for input, prediction display, explanation display, and report export.
- Version display for data, model, and recommendation rules.

## 13. Reproducibility Outputs Required Before Final Reporting

| Output | Required location |
|---|---|
| Data dictionary | `data/processed/data_dictionary.csv` and/or `docs/data_dictionary.md` |
| Data validation report | `outputs/reports/data_validation_report.md` |
| Split files | `data/splits/` |
| Feature documentation | `outputs/reports/feature_engineering_report.md` |
| Model metrics | `outputs/metrics/` |
| Saved models | `outputs/models/` |
| SHAP and LIME outputs | `outputs/explainability/` |
| Recommendation rules | `outputs/recommendations/` or `src/recommendation_rules/` |
| Final reproducibility README | `README.md` or `docs/reproducibility.md` |

## 14. Phase 1 Locked Decisions

| Decision | Final Phase 1 position |
|---|---|
| Research identity | Hybrid AI plus XAI for mango soil microbiome analysis in Malihabad. |
| Core novelty | Mango-specific, Malihabad-focused, microbiome-aware, explainable, multi-task framework. |
| Synthetic CSV role | Prototype dataset, not final field evidence. |
| Sequencing targets | 16S rRNA for bacteria/archaea; ITS for fungi. |
| Main targets | Mango yield, disease risk, nutrient availability. |
| Core validation | Internal validation plus geographic hold-out; later real-sample validation. |
| XAI methods | SHAP as primary explanation layer; LIME as local cross-check. |
| DSS timing | After reproducible modeling and explanation pipeline. |

## 15. Immediate Next Implementation Step

After Phase 1, the next practical implementation should be:

1. Create a complete data dictionary for the 63 current columns.
2. Add data-validation code for the synthetic CSV.
3. Correct or regenerate invalid synthetic taxonomic values.
4. Expand the real-sampling design for Phase 2.

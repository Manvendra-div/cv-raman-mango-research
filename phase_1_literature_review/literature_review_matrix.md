# Literature Review Matrix

This matrix implements the Phase 1 literature review for the project. It is organized around the research decisions needed before field design and model development.

## 1. Local Crop Context and Study Justification

| Theme | Reference | Evidence reviewed | Relevance to this project | Remaining gap |
|---|---|---|---|---|
| Mango as a high-value Indian crop | R1 | APEDA identifies mango as an important Indian export commodity and lists Uttar Pradesh as the leading state in 2023-24 production share. | Supports the practical importance of a mango-focused soil-health and AI study. | Production importance alone does not provide orchard-level microbiome or soil-health data. |
| Malihabad and Dashehari specificity | R2 | The GI record for Mango Malihabadi Dusseheri anchors the crop identity to the Malihabad region. | Supports a place-specific research design instead of a generic mango model. | GI identity does not define soil microbiome profiles, disease pressure, or AI-ready data variables. |
| Local orchard variability | Local proposal files | Existing project documents identify Malihabad, Rahimabad, Kakori, and Mall as village labels and include variety, tree age, management, depth, season, and orchard IDs. | Confirms that the project already has the correct metadata categories for stratified sampling and geographic validation. | The current CSV is synthetic, so real spatial and management effects remain unvalidated. |

## 2. Mango Soil Health, Microbiome, and Orchard Management

| Theme | Reference | Evidence reviewed | Relevance to this project | Remaining gap |
|---|---|---|---|---|
| Mango rhizosphere microbiome responds to management | R3 | Long-term organic and conventional mango orchard treatments altered bacterial community structure and soil biological activity in Dashehari mango orchards. | Direct evidence that mango orchard management can shape rhizosphere bacterial structure, supporting the use of `Management`, microbial features, and soil biological metrics. | The study supports microbiome sensitivity but does not provide a Malihabad-wide predictive AI framework for yield and disease risk. |
| Soil-health indicators must be multidimensional | R10 | Soil health is best assessed through combined physical, chemical, and biological indicators rather than a single measurement. | Supports using pH, EC, organic carbon, NPK, texture, CEC, moisture, microbial richness, diversity, and functional groups together. | Indicator weighting for mango-specific soil-health scoring remains project-specific and must be validated. |
| Rhizosphere microbiome is linked to plant health | R6 | Plant health is influenced by complex interactions between roots, soil microbes, pathogens, and beneficial taxa. | Supports the central assumption that mango yield and disease risk can be modeled from soil and microbiome variables. | General plant-health theory must be translated carefully into mango-specific, region-specific variables. |
| Disease-suppressive soils can have microbial signatures | R7 | Disease suppression can be associated with specific rhizosphere microbial communities and beneficial bacterial groups. | Supports including beneficial groups such as `Pseudomonas_PGPR`, `Trichoderma`, nitrogen fixers, phosphate solubilizers, and pathogen indicators. | Disease suppression is crop-, pathogen-, and soil-specific; synthetic proxy variables must later be replaced or calibrated using real samples. |
| Soil microbiome complexity requires careful interpretation | R9 | Soil microbiomes are highly diverse, context-sensitive, and difficult to reduce to simple causal explanations. | Justifies the project's use of XAI and cautious interpretation of feature importance. | Feature importance is not proof of biological causality; field trials and experimental validation remain necessary. |

## 3. Mango Disease Ecology

| Theme | Reference | Evidence reviewed | Relevance to this project | Remaining gap |
|---|---|---|---|---|
| Fusarium relevance in mango disease | R4 | Fusarium species are associated with mango malformation disease, with species-level diversity and regional differences. | Supports using `Fusarium` and `Pathogen_Load_Index` as disease-risk indicators. | Fusarium is only one disease pathway; field diagnosis should distinguish malformation, wilt, root rot, anthracnose, and other conditions. |
| Anthracnose as a major mango disease | R5 | Mango anthracnose is strongly linked with Colletotrichum species and remains an important post-harvest and field disease concern. | Broadens disease ecology beyond Fusarium and shows that the future real dataset may need disease-specific labels. | The current synthetic dataset does not include Colletotrichum or separate disease types. |
| Disease-risk target design | R4, R5, local CSV | The current `Disease_Risk` target is Low, Medium, High and is strongly driven by `Pathogen_Load_Index` in the synthetic dataset. | Useful as a first classification target for prototype modeling. | Real disease-risk labels should be based on field scoring, pathogen assays, or disease-specific diagnostic categories. |

## 4. AI and Machine Learning in Agriculture

| Theme | Reference | Evidence reviewed | Relevance to this project | Remaining gap |
|---|---|---|---|---|
| ML is widely used in agricultural prediction | R11 | Machine learning has been applied to yield prediction, disease detection, soil management, water management, and crop classification. | Supports the technical feasibility of using regression and classification models for mango outcomes. | General agricultural ML evidence does not remove the need for crop- and site-specific validation. |
| Updated agricultural ML landscape | R12 | Recent agriculture ML literature emphasizes data quality, feature selection, model choice, and careful validation. | Supports comparing baseline models, ensembles, and neural baselines instead of relying on a single model family. | Many agricultural ML studies suffer from limited reproducibility and insufficient external validation. |
| Crop yield prediction requires systematic model comparison | R13 | Crop-yield ML studies use a range of algorithms, data types, and validation methods, with no universally best method. | Supports the project plan to compare linear baselines, SVR, Random Forest, Gradient Boosting, optional XGBoost/LightGBM, and MLP. | The champion model must be selected from reproducible splits, not narrative claims. |
| AI can support soil microbiome and soil-health prediction | R14 | AI methods can help extract predictive structure from high-dimensional soil microbiome and soil-health datasets. | Directly supports a soil microbiome plus AI research framework. | Review-level evidence still requires local experimental design and real-data validation. |
| Supervised ML can link microbiome to soil-health measures | R15 | Microbiome profiles can be used with supervised learning to predict soil-health indicators. | Supports using microbiome-derived predictors for soil health and yield modeling. | Soil-health models may not generalize across crops, locations, sequencing protocols, and management systems without calibration. |

## 5. Microbiome-Based Yield and Disease Prediction Design

| Design question | Literature support | Project decision | Rationale | Risk control |
|---|---|---|---|---|
| Should microbiome variables be integrated with soil chemistry? | R6, R8, R10, R14, R15 | Yes. Use microbiome, soil physicochemical, climate, orchard metadata, and management variables together. | Mango productivity is influenced by biological, chemical, environmental, and management factors. | Report feature-group ablation: soil-only, microbiome-only, combined, and engineered features. |
| Should the project predict yield, disease risk, and nutrient availability? | R11, R12, R13, local proposal | Yes, but with separate task types: yield as regression; disease and nutrient status as classification. | The current dataset already contains these targets and the objectives need both productivity and soil-health decision support. | Ensure target definitions are measurable in real samples and avoid leakage from engineered features derived from targets. |
| Should tree ensembles be prioritized? | R11, R12, R13 | Yes, as strong tabular-data candidates, alongside transparent baselines. | Random Forest and Gradient Boosting are robust on structured mixed-feature datasets and produce usable importance signals. | Keep linear/logistic models as baselines and evaluate MLP only if sample size and feature quality justify it. |
| Should deep learning be central? | R9, R12, R14 | Not initially. Use deep learning as a secondary benchmark, not as the core claim. | The present data are tabular and synthetic; deep learning may overfit or add complexity without interpretability. | Consider graph or neural models later only if real OTU/ASV networks and sufficient sample size are available. |
| Should geography be used as a hold-out? | Local outline, R12, R13 | Yes. Use one village, such as Rahimabad, as a geographic hold-out. | A Malihabad-area model must generalize across village-level soil and management differences. | Also report village-wise and season-wise error on internal test data. |

## 6. Explainable AI and Decision Support

| Theme | Reference | Evidence reviewed | Relevance to this project | Remaining gap |
|---|---|---|---|---|
| SHAP for consistent feature attribution | R16 | SHAP provides a unified feature-attribution framework for explaining model predictions. | Supports global and local explanation of yield, disease-risk, and nutrient-status models. | SHAP values explain a fitted model, not necessarily causal biology. |
| LIME for local model-agnostic explanations | R17 | LIME approximates local model behavior to explain individual predictions. | Supports orchard-level explanation and cross-checking of local SHAP outputs. | LIME explanations can vary with perturbation settings and should be used as supporting evidence. |
| XAI in sustainable agriculture | R18 | Agricultural AI needs interpretability to support user trust, adoption, and responsible recommendations. | Supports making explanations a core research objective rather than an add-on. | Farmer-facing explanations must use agronomic language and avoid overclaiming certainty. |
| DSS requirements for Agriculture 4.0 | R19 | DSS design must consider usability, data integration, interoperability, scalability, and end-user trust. | Supports a future FastAPI/Streamlit DSS only after reproducible modeling and explanation pipelines exist. | A dashboard without validated models risks producing polished but unreliable recommendations. |

## 7. Microbiome Bioinformatics Method Support

| Method need | Reference | Project decision | Rationale |
|---|---|---|---|
| Reproducible microbiome analysis platform | R20 | Use QIIME 2 or an equivalent reproducible workflow for real microbiome processing. | Provides standard structure for demultiplexing, quality control, diversity metrics, taxonomy, and provenance. |
| ASV-level denoising | R21 | Prefer ASV generation through DADA2 where sequencing design allows it. | ASVs improve reproducibility and resolution compared with loosely clustered OTUs. |
| Bacterial/archaeal taxonomy | R22 | Use SILVA or a documented equivalent database for 16S rRNA taxonomy. | Aligns bacterial/archaeal taxonomic assignment with established reference resources. |
| Fungal taxonomy | R23 | Use UNITE or a documented equivalent database for ITS taxonomy. | Aligns fungal classification with a curated ITS reference resource. |

## 8. Literature-Derived Conceptual Model

The literature supports the following project concept:

1. Mango orchard productivity depends on interacting soil physical, chemical, biological, climate, and management variables.
2. Soil microbiome structure and functional groups are plausible predictors of soil health, nutrient cycling, disease suppression, and disease pressure.
3. Mango disease risk should not be treated as a single-pathogen problem. Fusarium is important for malformation-related risk, while anthracnose and other diseases may require additional pathogen or field-scoring variables.
4. ML is appropriate for nonlinear, multi-source agricultural prediction, but reproducibility and external validation are essential.
5. Tree-based ensembles are strong first candidates for tabular data, while deep learning should be justified by data volume and structure.
6. SHAP and LIME are suitable explanation methods, provided outputs are interpreted as model explanations rather than causal proof.
7. A decision support system should be built after the pipeline is reproducible and validated, not before.

## 9. Literature Review Conclusions for This Project

| Phase 1 conclusion | Decision locked for later phases |
|---|---|
| The project is scientifically justified because mango soil health, rhizosphere microbiomes, and disease ecology interact in ways that are hard to model manually. | Use integrated soil-microbiome-climate-orchard features. |
| The project is locally justified because Malihabad/Dusseheri mango has a specific geographical and agronomic identity. | Keep Malihabad focus and include nearby villages only as regional generalization strata. |
| The current synthetic dataset is useful but not sufficient for final scientific claims. | Treat synthetic modeling as prototype evidence until real samples are collected. |
| The final disease target should be clinically/agronomically defined. | Add field disease scoring and, where feasible, pathogen-specific measurements in real sampling. |
| SHAP and LIME fit the XAI objective but must be translated into agronomic recommendations carefully. | Build explanation-to-recommendation rules with thresholds and uncertainty flags. |
| The DSS is a later technical deliverable, not Phase 1 proof. | Build DSS only after reproducible preprocessing, training, evaluation, and XAI scripts are available. |

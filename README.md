# Zone-Aware Mango Soil Intelligence and Yield Gap Decision Support System

**AI-Powered Agricultural Intelligence for Sustainable Mango Cultivation in Malihabad, Uttar Pradesh**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: TBD](https://img.shields.io/badge/license-TBD-yellow.svg)](LICENSE)
[![Status: Research Prototype](https://img.shields.io/badge/status-research%20prototype-orange.svg)]()

---

## 🎯 Project Vision

This research project develops a hybrid machine learning and explainable AI-based decision support system that analyzes **soil physicochemical properties**, **soil microbiome characteristics**, **climate variables**, and **orchard metadata** to:

1. **Predict mango yield** in kg/tree
2. **Assess disease risk** (Low / Medium / High)
3. **Evaluate nutrient availability** status
4. **Benchmark orchards** against comparable peers within their geographical zone
5. **Estimate yield gaps** between current and reference performance
6. **Identify limiting factors** that may be constraining productivity
7. **Generate evidence-based agronomic recommendations** using explainable AI
8. **Support intervention tracking** and outcome monitoring

**This is NOT just a yield prediction model.** This is an **agricultural intelligence platform** that contextualizes predictions within zone-specific benchmarks and explains what factors drive performance differences.

---

## 🌍 Study Area

**Primary Location:** Malihabad mango belt, Uttar Pradesh, India

**Covered Villages:**
- Malihabad
- Rahimabad  
- Kakori
- Mall

**Target Crop:** *Mangifera indica* (Mango)

**Varieties Studied:**
- Dashehari
- Chausa
- Safeda
- Langra

---

## 📊 Research Highlights

### Dataset
- **20,000 observations** (synthetic prototype for methodology development)
- **63 variables** spanning soil, microbiome, climate, and orchard metadata
- **50 orchards** across 4 villages
- **3 target variables** for multi-task learning

### Machine Learning Performance
- **Regression (Mango Yield):**
  - RMSE: ~1.94 kg/tree
  - R²: High predictive accuracy
  - Champion: Gradient Boosting Regressor

- **Classification (Disease Risk):**
  - Accuracy: ~99.2%
  - Champion: Gradient Boosting Classifier

- **Geographic Generalization:**
  - Rahimabad hold-out validation: RMSE ~1.93 kg/tree
  - Demonstrates cross-village transferability

### Explainable AI
- **SHAP global explanations** for feature importance
- **SHAP local explanations** for individual orchard predictions
- **LIME cross-validation** for explanation robustness
- **7 agronomic recommendation rules** linked to XAI evidence

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT: Soil Sample                      │
│  (Physicochemical + Microbiome + Climate + Orchard Metadata)│
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               Data Preprocessing & Validation                │
│         (Standardization, Encoding, Feature Engineering)     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Machine Learning Engine                     │
│  ┌─────────────────┬──────────────────┬──────────────────┐ │
│  │  Mango Yield    │   Disease Risk   │    Nutrient      │ │
│  │  Prediction     │   Classification │  Availability    │ │
│  └─────────────────┴──────────────────┴──────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Explainable AI Layer                       │
│              (SHAP, LIME, Feature Attribution)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            [TO BE IMPLEMENTED]                               │
│              Zone Intelligence Module                        │
│  • Village/Variety Profiling                                │
│  • Comparable Orchard Matching                              │
│  • Reference Yield Calculation                              │
│  • Yield Gap Analysis                                       │
│  • Limiting Factor Identification                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             Agronomic Recommendation Engine                  │
│          (Evidence-Based, XAI-Supported Rules)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Decision Support System Interface                  │
│         FastAPI Backend + Streamlit Dashboard                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher (tested with Python 3.14)
- Virtual environment (recommended)
- ~2GB RAM for training, <1GB for inference
- ~600MB disk space

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd "CV Raman Research Work Updated"

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment (optional)
cp .env.example .env
# Edit .env with your settings
```

### Usage

#### Option 1: Full Training Pipeline (Reproduce from Scratch)

```bash
# Phase 5: Data Preprocessing
python src/preprocessing/phase5_preprocess.py

# Phase 6: Feature Engineering
python src/feature_engineering/phase6_feature_engineering.py

# Phase 7.1: Train Regression Models
python src/modeling/phase7_1_train_regression.py

# Phase 7.2: Train Classification Models
python src/modeling/phase7_2_train_classification.py

# Phase 8: Generate Explainable AI Artifacts
python src/explainability/phase8_explainable_ai.py

# Phase 10: Run Validation
python src/validation/phase10_validation.py
```

#### Option 2: Use Pre-Trained Models (Inference Only)

**Start FastAPI Backend:**
```bash
uvicorn src.dss.api:app --host 0.0.0.0 --port 8000
```

**Start Streamlit Dashboard:**
```bash
streamlit run src/dss/dashboard.py --server.port 8501
```

**Access Dashboard:**
Open browser to `http://localhost:8501`

**API Documentation:**
`http://localhost:8000/docs` (Swagger UI)

---

## 📁 Repository Structure

```
CV Raman Research Work Updated/
│
├── data/                          # Data storage (590MB total)
│   ├── raw/                       # Original synthetic dataset (20MB)
│   ├── processed/                 # Cleaned and feature-engineered data (90MB)
│   ├── splits/                    # Train/validation/test/holdout splits
│   └── validation/                # Real-world validation templates
│
├── src/                           # Source code
│   ├── preprocessing/             # Phase 5: Data cleaning and preprocessing
│   ├── feature_engineering/       # Phase 6: Feature creation and selection
│   ├── modeling/                  # Phase 7: Model training
│   │   ├── phase7_1_train_regression.py
│   │   └── phase7_2_train_classification.py
│   ├── explainability/            # Phase 8: SHAP and LIME
│   ├── dss/                       # Phase 9: Decision Support System
│   │   ├── api.py                 # FastAPI backend
│   │   ├── dashboard.py           # Streamlit frontend
│   │   └── service.py             # Business logic
│   ├── validation/                # Phase 10: Model validation
│   └── zone_intelligence/         # [TO BE IMPLEMENTED] Zone-aware analysis
│
├── outputs/                       # Generated artifacts (257MB)
│   ├── models/                    # Trained models (144MB)
│   │   ├── regression/            # Mango yield models
│   │   └── classification/        # Disease risk & nutrient models
│   ├── explainability/            # SHAP/LIME artifacts (16MB)
│   ├── predictions/               # Model predictions (97MB)
│   ├── metrics/                   # Evaluation metrics (276KB)
│   └── reports/                   # Generated markdown reports
│
├── phase_*/                       # Research phase documentation (10 phases)
│   ├── phase_1_literature_review/
│   ├── phase_2_study_design_sampling_framework/
│   ├── phase_3_soil_microbiome_data_collection/
│   ├── phase_4_laboratory_analysis/
│   ├── phase_5_data_integration_preprocessing/
│   ├── phase_6_feature_engineering/
│   ├── phase_7_model_development/
│   ├── phase_8_explainable_ai/
│   ├── phase_9_decision_support_system/
│   └── phase_10_validation/
│
├── docs/                          # Project documentation
│   └── PROJECT_AUDIT.md           # Comprehensive audit report
│
├── .gitignore                     # Git exclusions
├── .env.example                   # Environment variable template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🔬 Research Methodology

### Phase-Based Approach

This project follows a **10-phase research methodology**:

1. **Literature Review** — Soil microbiome, ML in agriculture, XAI
2. **Study Design** — Sampling framework, site selection, metadata templates
3. **Data Collection** — Field sampling protocols, chain of custody
4. **Laboratory Analysis** — Soil chemistry, DNA extraction, sequencing, bioinformatics
5. **Data Integration** — Preprocessing, cleaning, split strategy
6. **Feature Engineering** — Diversity indices, functional groups, engineered features
7. **Model Development** — Regression, classification, hyperparameter tuning
8. **Explainable AI** — SHAP, LIME, recommendation rules
9. **Decision Support System** — API, dashboard, deployment
10. **Validation** — Internal CV, geographic hold-out, real-sample validation

Each phase has dedicated documentation in the `phase_*/` directories.

---

## 🎓 Key Features

### 1. Multi-Task Machine Learning

- **Regression:** Mango yield prediction (kg/tree)
- **Classification:** Disease risk assessment (3-class)
- **Classification:** Nutrient availability status (3-class)

**Algorithms Evaluated:**
- Baseline: Linear models, SVR
- Ensemble: Random Forest, Gradient Boosting
- Advanced: XGBoost, LightGBM
- Neural: MLP with early stopping

### 2. Explainable AI Integration

**Global Explanations:**
- SHAP summary plots (feature importance)
- SHAP dependence plots (feature-target relationships)
- Tree-based feature importance

**Local Explanations:**
- SHAP waterfall plots (individual predictions)
- LIME local explanations (instance-level)
- Cross-validation between SHAP and LIME

**Agronomic Translation:**
- 7 evidence-based recommendation rules
- SHAP contribution thresholds
- Contextual agronomic guidance

### 3. Geographic Validation

- **Hold-out village:** Rahimabad (5,059 samples)
- **Training villages:** Malihabad, Kakori, Mall
- **Evaluation:** Cross-village generalization
- **Validation:** Model transferability assessment

### 4. Decision Support System

**Backend (FastAPI):**
- `/health` — Model readiness check
- `/metadata` — Feature specifications
- `/predict` — Full prediction + explanations
- `/explain` — SHAP/LIME explanations
- `/recommendations` — Agronomic guidance
- `/report` — Exportable orchard report

**Frontend (Streamlit):**
- Interactive input forms (soil, microbiome, climate, orchard)
- Real-time predictions
- SHAP waterfall visualizations
- Recommendation display
- Markdown report export

---

## 🚧 Current Limitations & Roadmap

### ⚠️ Known Limitations

1. **Synthetic Data:** Current dataset is algorithmically generated for methodology development. Real-world field validation is planned but not yet conducted.

2. **Data Quality Issues:**
   - 3,732 observations contain negative microbiome abundance values (biologically invalid)
   - Nutrient_Availability missing "Deficient" class (only 2 of 3 classes present)
   - Requires data regeneration with corrected constraints

3. **Zone Intelligence NOT Implemented:**
   - No comparable orchard matching
   - No zone-level benchmarking
   - No yield gap calculation
   - No limiting factor identification
   - **This is the PRIMARY GAP preventing full system identity**

4. **Limited Orchard Diversity:**
   - Only 50 orchards represented
   - 400 samples per orchard (potential correlation)
   - Orchard independence not explicitly verified

### 🛣️ Implementation Roadmap

#### Priority 1: Repository Hygiene ✅ **COMPLETE**
- ✅ Create `.gitignore`
- ✅ Create `README.md`
- ✅ Create `requirements.txt`
- ✅ Create `.env.example`

#### Priority 2: Data Quality Resolution (1-2 days)
- [ ] Investigate negative abundance generation
- [ ] Document synthetic data generation methodology
- [ ] Regenerate dataset with biological constraints
- [ ] Add "Deficient" class to Nutrient_Availability
- [ ] Verify orchard sampling structure

#### Priority 3: Zone Intelligence Implementation (6-9 days)
- [ ] Implement `src/zone_intelligence/zone_profile.py`
- [ ] Implement `src/zone_intelligence/orchard_matching.py`
- [ ] Implement `src/zone_intelligence/reference_yield.py`
- [ ] Implement `src/zone_intelligence/yield_gap.py`
- [ ] Implement `src/zone_intelligence/limiting_factors.py`

#### Priority 4: DSS Integration (2-3 days)
- [ ] Extend API with zone intelligence endpoints
- [ ] Add benchmarking visualization to dashboard
- [ ] Add yield gap display
- [ ] Add limiting factor ranking
- [ ] Generate zone-aware orchard reports

#### Priority 5: Documentation (1 day)
- [ ] Create `ZONE_INTELLIGENCE_METHODOLOGY.md`
- [ ] Create `YIELD_GAP_METHODOLOGY.md`
- [ ] Create `ARCHITECTURE.md`
- [ ] Update this README with new features

#### Priority 6: Real-World Validation (Ongoing)
- [ ] Collect real soil samples from Malihabad
- [ ] Conduct laboratory analysis (soil + microbiome)
- [ ] Validate predictions against observed yields
- [ ] Refine models with real data
- [ ] Publish research findings

**Estimated Time to Full System Identity:** 12-18 working days (2.5-3.5 weeks)

---

## 📊 Dataset Schema

### Metadata (10 columns)
- Sample_ID, Orchard_ID, Village, GPS coordinates
- Mango_Variety, Tree_Age, Soil_Depth, Sampling_Season, Management

### Soil Physicochemical (18 columns)
- pH, EC, Organic_Carbon, Total_Nitrogen, Available_P, Available_K
- Soil_Moisture, Soil_Temperature, Bulk_Density, CEC
- Sand, Silt, Clay, Zn, Fe, Mn, Cu, C_N_Ratio

### Climate (4 columns)
- Air_Temp_Avg, Rainfall, Humidity, Solar_Radiation

### Microbiome Diversity (5 columns)
- OTU_Count, Shannon_Index, Simpson_Index, Chao1_Richness, Pielou_Evenness

### Taxonomic Abundance (12 columns)
- Bacteria: Proteobacteria, Actinobacteria, Acidobacteria, Firmicutes, Bacteroidetes
- Fungi: Ascomycota, Basidiomycota, Glomeromycota, Mortierellomycota, Zygomycota
- Archaea: Thaumarchaeota, Euryarchaeota

### Functional Groups (8 columns)
- Nitrogen_Fixers, Phosphate_Solubilizers_PSB, Potassium_Solubilizers
- Mycorrhizae_AMF, Trichoderma, Pseudomonas_PGPR, Fusarium, Pathogen_Load_Index

### Engineered Features (3 columns)
- Microbial_Richness_Score, Nutrient_Balance_Ratio, Soil_Health_Index

### Targets (3 columns)
- Mango_Yield (regression, kg/tree)
- Disease_Risk (classification, Low/Medium/High)
- Nutrient_Availability (classification, Deficient/Optimal/High)

---

## 🤝 Contributing

This is currently a research project under active development. Contributions are welcome after the core zone intelligence implementation is complete.

**Contribution areas:**
- Real-world data collection
- Model improvements
- Zone intelligence algorithms
- Visualization enhancements
- Documentation
- Testing

---

## 📄 License

**License status:** To be determined (currently research prototype)

Consider appropriate license for agricultural research software:
- MIT License (permissive, industry-friendly)
- Apache 2.0 (patent protection)
- GPL v3 (copyleft, ensures openness)

---

## 📚 Citation

If you use this work in your research, please cite:

```
[Citation to be added after publication]

Project: Zone-Aware Mango Soil Intelligence and Yield Gap Decision Support System
Institution: [Institution Name]
Location: Malihabad, Uttar Pradesh, India
Year: 2026
```

---

## 👥 Research Team

**Primary Investigator:** [Name]  
**Institution:** [Institution Name]  
**Location:** Malihabad Region, Uttar Pradesh, India

---

## 📞 Contact

**For research inquiries:**  
[Contact information]

**For technical support:**  
[Technical contact]

**For collaboration opportunities:**  
[Collaboration contact]

---

## 🙏 Acknowledgments

- Farmers and orchard managers in Malihabad, Rahimabad, Kakori, and Mall
- Laboratory partners for soil and microbiome analysis
- Agricultural extension officers in Uttar Pradesh
- [Additional acknowledgments]

---

## 📖 Additional Documentation

- [Project Audit Report](docs/PROJECT_AUDIT.md) — Comprehensive repository assessment
- [Detailed Research Outline](Detailed_Research_Work_Outline.md) — Full methodology
- [Final Research Report](Final_Research_Report.md) — Current findings
- [Phase-Specific Documentation](phase_1_literature_review/README.md) — 10 research phases

---

## ⚠️ Disclaimer

**Research Prototype:** This system is a research prototype using synthetic data. Predictions and recommendations are for research and development purposes only.

**Agricultural Guidance:** All agronomic recommendations should be verified by qualified agricultural experts before implementation. This system is a decision support tool, not a replacement for professional agronomic consultation.

**No Warranties:** The software is provided "as is" without warranty of any kind. The authors and contributors are not liable for any consequences arising from the use of this software or its recommendations.

---

## 🔄 Version History

**Version 1.0.0** (2026-10-03)
- Initial repository hygiene establishment
- Comprehensive audit completed
- .gitignore, requirements.txt, .env.example created
- README.md documentation
- ML pipeline functional (Phases 5-10)
- XAI implementation complete
- DSS functional (FastAPI + Streamlit)
- **Zone Intelligence: NOT YET IMPLEMENTED**

---

**Built with ❤️ for sustainable mango cultivation in Uttar Pradesh**

🥭 **Transforming Mango Agriculture Through AI and Soil Microbiome Intelligence** 🥭

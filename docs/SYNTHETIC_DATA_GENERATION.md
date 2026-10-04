# SYNTHETIC DATA GENERATION METHODOLOGY

**Script:** `src/data/generate_synthetic_data.py`  
**Version:** v2  
**Created:** 2026-10-04  
**Output:** `data/raw/mango_microbiome_dataset_v2.csv`  
**Random Seed:** 42 (reproducible)

---

## OVERVIEW

This document describes the methodology for generating the synthetic mango soil microbiome dataset used for ML pipeline development and testing.

**Purpose:** Create a biologically plausible dataset for:
1. ML algorithm prototyping
2. DSS interface development
3. XAI framework testing
4. Zone Intelligence validation

**Critical Disclaimer:** This is SYNTHETIC data. Model performance on this data does NOT represent real-world performance. Real field validation is required before production deployment.

---

## CONFIGURATION

```python
RANDOM_STATE = 42
N_SAMPLES = 20,000
N_ORCHARDS = 50
SAMPLES_PER_ORCHARD = 400 (exactly uniform)
```

**Geographic Coverage:**
- Villages: 4 (Malihabad, Rahimabad, Kakori, Mall)
- Varieties: 4 (Dashehari, Chausa, Safeda, Langra)
- Seasons: 3 (Pre-monsoon, Post-monsoon, Winter)
- Management: 3 (Organic, Conventional, Integrated)

---

## DATA GENERATION STEPS

### Step 1: Metadata (9 features)

All metadata assigned via random sampling with NO correlation to features:

- **Sample_ID:** Sequential S00001-S20000
- **Orchard_ID:** 50 orchards × 400 samples each (perfectly uniform)
- **Village:** Evenly distributed (5,000 per village)
- **GPS:** Centered on Malihabad (26.95°N, 80.75°E) + N(0, 0.08) noise
- **Variety, Tree_Age, Depth, Season, Management:** Random uniform

**Issue:** GPS independent of Village assignment (spatial mismatch)

### Step 2: Soil Chemistry (18 features)

All drawn from **independent uniform distributions**:

| Feature | Range | Distribution |
|---------|-------|--------------|
| pH | 6.5 - 8.5 | Uniform |
| EC | 0.2 - 0.9 dS/m | Uniform |
| Organic_Carbon | 0.3 - 0.9 % | Uniform |
| Total_Nitrogen | 150 - 400 kg/ha | Uniform |
| Available_P | 8 - 30 kg/ha | Uniform |
| Available_K | 120 - 350 kg/ha | Uniform |
| Sand, Clay, Silt | Constrained sum=100% | Special |
| Micronutrients (Zn,Fe,Mn,Cu) | Realistic ranges | Uniform |

**C_N_Ratio:** Derived = (OC × 10) / (TN / 100)

**Issue:** No inter-feature correlations (unrealistic)

### Step 3: Climate (4 features)

| Feature | Range | Distribution |
|---------|-------|--------------|
| Air_Temp_Avg | 15 - 42 °C | Uniform |
| Rainfall | 5 - 300 mm | Uniform |
| Humidity | 30 - 90 % | Uniform |
| Solar_Radiation | 12 - 26 MJ/m²/day | Uniform |

### Step 4: Microbiome Diversity (5 features)

| Feature | Range | Distribution |
|---------|-------|--------------|
| OTU_Count | 800 - 3,499 | Uniform int |
| Shannon_Index | 2.5 - 6.0 | Uniform |
| Simpson_Index | 0.6 - 1.0 | Uniform |
| Chao1_Richness | 900 - 3,499 | Uniform int |
| Pielou_Evenness | 0.5 - 1.0 | Uniform |

**Issue:** Indices independent of taxonomic abundances (biologically impossible)

### Step 5: Taxonomic Abundances (12 features) ✅ V2 FIX

**Method:** Dirichlet distribution with fixed kingdom ratios

**Bacteria (50% total):** α = [4.0, 3.0, 2.0, 2.0, 3.0]
- Proteobacteria, Actinobacteria, Acidobacteria, Firmicutes, Bacteroidetes

**Fungi (40% total):** α = [4.0, 3.0, 2.0, 2.0, 1.5]
- Ascomycota, Basidiomycota, Glomeromycota, Mortierellomycota, Zygomycota

**Archaea (10% total):** α = [1.0, 0.8]
- Thaumarchaeota, Euryarchaeota

**Result:** All samples sum to exactly 100.0%, no negative values

**Issue:** Kingdom ratio (50:40:10) fixed for all samples (unrealistic)

### Step 6: Functional Groups (8 features)

| Group | Range | Unit |
|-------|-------|------|
| Nitrogen_Fixers | 100K - 10M | CFU/g |
| P_Solubilizers | 10K - 1M | CFU/g |
| K_Solubilizers | 5K - 100K | CFU/g |
| Mycorrhizae_AMF | 50 - 400 | spores/g |
| Trichoderma | 1K - 100K | CFU/g |
| Pseudomonas_PGPR | 10K - 1M | CFU/g |
| Fusarium | 100 - 100K | CFU/g |

**Pathogen_Load_Index (derived):**
```
PLI = 0.7×(Fusarium/100K) + 0.15×(1-Trichoderma/100K) + 0.15×(1-Pseudomonas/1M)
PLI = clip(PLI, 0, 1)
```

### Step 7: Engineered Features (3 features)

**Microbial_Richness_Score:**
```
MRS = 0.4×(Shannon/6) + 0.3×Simpson + 0.3×Pielou
MRS scaled to 0-100
```

**Nutrient_Balance_Ratio:**
```
NBR = (P_norm + K_norm + N_norm) / 3
NBR = clip(NBR, 0.3, 1.0)
where X_norm = (X - X_min) / (X_max - X_min)
```

**Soil_Health_Index:**
```
SHI = 15×pH_norm + 20×OC_norm + 10×(1-EC_norm) + 
      15×CEC_norm + 20×NBR + 20×(MRS/100)
SHI = clip(SHI, 40, 95)
```

---

## TARGET GENERATION ⚠️ CRITICAL SECTION

### TARGET 1: Mango_Yield (kg/tree)

```python
base = 15.0
yield = base + 
        5.0 × (Soil_Health_Index / 100) +
        4.0 × Nutrient_Balance_Ratio +
        3.0 × (1 - Pathogen_Load_Index) +
        2.0 × (clip(Tree_Age, 10, 40) / 40) +
        1.0 × (Rainfall / 300) -
        0.5 × (|Air_Temp - 28| / 28) +
        N(0, 1.5) noise

yield = clip(yield, 10.5, 25.0)
```

**Driving Features:** Soil_Health_Index (max 5), Nutrient_Balance_Ratio (max 4), Pathogen_Load_Index (max 3)

**Issue:** Soil_Health_Index included as both feature and yield driver (partial leakage)

### TARGET 2: Disease_Risk (categorical) ⚠️ LEAKAGE

```python
if Pathogen_Load_Index < 0.3:
    Disease_Risk = 'Low'
elif Pathogen_Load_Index < 0.7:
    Disease_Risk = 'Medium'
else:
    Disease_Risk = 'High'
```

**CRITICAL:** Deterministic function of Pathogen_Load_Index. Including PLI as feature = 100% accuracy.

### TARGET 3: Nutrient_Availability (categorical) ⚠️ LEAKAGE

```python
if Nutrient_Balance_Ratio < 0.58:
    Nutrient_Availability = 'Deficient'
elif Nutrient_Balance_Ratio < 0.74:
    Nutrient_Availability = 'Optimal'
else:
    Nutrient_Availability = 'High'
```

**CRITICAL:** Deterministic function of Nutrient_Balance_Ratio. Including NBR as feature = perfect classification.

---

## DEPENDENCY DIAGRAM

```
RAW FEATURES (independent)
    ↓
ENGINEERED FEATURES
    Pathogen_Load_Index ──→ Disease_Risk (deterministic)
    Nutrient_Balance_Ratio ──→ Nutrient_Availability (deterministic)
    Soil_Health_Index ──→ Mango_Yield (dominant component)
    ↓
TARGETS (with leakage)
```

---

## KNOWN ISSUES

### 1. Target Leakage (CRITICAL)
- Disease_Risk = f(Pathogen_Load_Index)
- Nutrient_Availability = f(Nutrient_Balance_Ratio)
- Reported 99.2% accuracy is artifact

**Mitigation:** Remove engineered features from model inputs OR disclose leakage

### 2. Pseudo-Replication (CRITICAL)
- All 50 orchards have exactly 400 samples
- No within-orchard correlation
- Inflates effective N from 50 to 20,000

**Mitigation:** Use GroupKFold with Orchard_ID

### 3. No Feature Correlations
- pH-CEC: r ≈ 0 (should be 0.6)
- OC-TN: independent (should be correlated)
- Real soil shows strong correlations

**Mitigation:** Use multivariate distributions in v3

### 4. Diversity-Abundance Independence
- Shannon, Simpson, Pielou independent of taxonomic abundances
- Biologically impossible

**Mitigation:** Compute diversity FROM abundances in v3

### 5. Fixed Kingdom Ratios
- Bacteria:Fungi:Archaea = 50:40:10 for ALL samples
- No village/management effects

**Mitigation:** Variable kingdom ratios in v3

### 6. Metadata-Feature Independence
- Village has zero effect on soil/microbiome
- Undermines "zone-aware" framework

**Mitigation:** Introduce village-level parameter shifts in v3

---

## V1 TO V2 CHANGES

**V1 Issues:**
- ❌ Negative abundances (Zygomycota: 3,717 rows, min=-22%)
- ❌ Compositional violation (sum = 207%, range 201-213%)

**V2 Fixes:**
- ✅ Dirichlet distribution (guarantees non-negative, sum=100%)
- ✅ Assert statements verify constraints
- ✅ Versioned output filename

---

## REPRODUCIBILITY

**To regenerate the dataset:**
```bash
cd /path/to/project
python src/data/generate_synthetic_data.py
```

**Output:** `data/raw/mango_microbiome_dataset_v2.csv`

**Dependencies:** pandas, numpy (standard)

**Seed:** 42 (fixed for reproducibility)

---

## USAGE IN RESEARCH

**Methods Section Disclosure:**

> "A synthetic dataset (N=20,000) was generated to prototype the ML pipeline. Targets were computed as deterministic functions of engineered features (Pathogen_Load_Index → Disease_Risk, Nutrient_Balance_Ratio → Nutrient_Availability). Models including these features achieve near-perfect accuracy by learning generation rules, representing a theoretical upper bound. Real-world performance requires field validation with independent orchard samples."

**Limitations Section:**

> "The synthetic dataset has several limitations: (1) features are statistically independent (no correlations), (2) microbiome diversity indices are not derived from taxonomic abundances, (3) all orchards have exactly 400 samples (pseudo-replication), (4) village and management metadata have no effect on feature distributions. These artifacts may cause models to overfit synthetic patterns that don't generalize to real soil data."

---

## FUTURE IMPROVEMENTS (V3)

1. **Remove leakage:** Generate targets independently
2. **Add correlations:** Use Gaussian copulas for correlated features
3. **Derive diversity:** Compute Shannon/Simpson FROM abundances
4. **Variable structure:** Random samples per orchard (50-500)
5. **Zone effects:** Village-level parameter shifts
6. **Management effects:** Organic vs Conventional differences
7. **Temporal structure:** Seasonal parameter variation

---

**Documentation Updated:** 2026-10-04  
**Script Location:** `src/data/generate_synthetic_data.py`  
**For Questions:** Contact Research Team Lead

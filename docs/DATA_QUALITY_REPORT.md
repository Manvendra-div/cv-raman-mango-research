# DATA QUALITY REPORT
## Mango Soil Microbiome Dataset - Comprehensive Audit

**Audit Date:** 2026-10-04  
**Dataset Version:** v2 (mango_microbiome_dataset.csv)  
**Samples:** 20,000  
**Features:** 63  
**Audit Results:** `outputs/data_quality_audit_results.json`

---

## EXECUTIVE SUMMARY

The dataset (v2) is **biologically valid and statistically clean** with zero missing values. However, **severe target leakage** and **orchard pseudo-replication** compromise ML validation.

**Quality Grade: B (80/100)**

**Strengths:**
- ✅ Zero missing values (1.26M cells)
- ✅ No negative abundances (v1 fixed)
- ✅ Perfect compositional constraint (sum=100%)
- ✅ Biologically plausible ranges

**Critical Issues:**
- ❌ **Target leakage:** Pathogen_Load_Index→Disease_Risk (deterministic)
- ❌ **Pseudo-replication:** 400 samples/orchard (no independence)
- ⚠️ **Class imbalance:** 67% Deficient in Nutrient_Availability
- ⚠️ **No correlations:** Features independent (unrealistic)

---

## DETAILED FINDINGS

### 1. Target Leakage (CRITICAL)

**Disease_Risk** = deterministic threshold on Pathogen_Load_Index:
- PLI < 0.3 → Low
- PLI < 0.7 → Medium  
- PLI ≥ 0.7 → High

**Nutrient_Availability** = deterministic threshold on Nutrient_Balance_Ratio:
- NBR < 0.58 → Deficient (67% of samples)
- NBR < 0.74 → Optimal
- NBR ≥ 0.74 → High

**Impact:** Reported 99.2% accuracy is artifact of learning generation rules.

### 2. Orchard Structure (CRITICAL)

All 50 orchards have exactly 400 samples (perfectly uniform). Samples within orchards are NOT independent. Requires GroupKFold validation.

### 3. Class Imbalance (HIGH)

Nutrient_Availability: 67.4% Deficient, 24.5% Optimal, 8.1% High

Requires: class_weight='balanced', SMOTE, stratified CV

### 4. V1→V2 Improvements (RESOLVED)

- ✅ Negative values: Fixed (Zygomycota: 3,717→0, Bacteroidetes: 15→0)
- ✅ Compositional: Fixed (sum 207%→100%)
- ✅ Ranges: All within bounds

---

## RECOMMENDATIONS

**Priority 1 (Critical):**
1. Remove engineered features from model inputs OR disclose leakage
2. Implement GroupKFold with Orchard_ID groups
3. Update CLAUDE.md (Deficient class exists, not missing)

**Priority 2 (High):**
4. Apply class_weight='balanced' for Nutrient_Availability
5. Report per-class metrics (not just accuracy)

**Priority 3 (Medium):**
6. For v3: Add realistic feature correlations
7. For v3: Variable kingdom ratios (not fixed 50:40:10)

---

**Full Report:** See complete analysis in this document  
**Audit Script:** `outputs/data_quality_audit.py`  
**JSON Results:** `outputs/data_quality_audit_results.json` (24.8 KB)

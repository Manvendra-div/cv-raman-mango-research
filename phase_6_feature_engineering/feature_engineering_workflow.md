# Feature Engineering Workflow

## 1. Objective

Create interpretable agronomic and microbiome features from the Phase 5 clean master dataset.

## 2. Implemented Script

Main script:

```text
src/feature_engineering/phase6_feature_engineering.py
```

Run command:

```powershell
python src\feature_engineering\phase6_feature_engineering.py
```

## 3. Feature Groups Created

| Feature group | Examples |
|---|---|
| Diversity scores | `Diversity_Score_Phase6`, `Richness_Evenness_Balance_Phase6` |
| Taxonomic structure | `Bacterial_Dominance_Index_Phase6`, `Fungal_Dominance_Index_Phase6`, `Archaeal_Dominance_Index_Phase6` |
| Functional microbial summaries | `Beneficial_Microbial_Index_Phase6`, `Nutrient_Cycling_Index_Phase6`, `Biocontrol_Index_Phase6` |
| Pathogen metrics | `Pathogen_Load_Index_Phase6`, `Pathogen_Beneficial_Ratio_Phase6`, `Beneficial_to_Pathogen_Log_Ratio_Phase6` |
| Nutrient balance | `NPK_Balance_Score_Phase6`, `Micronutrient_Balance_Score_Phase6` |
| Soil condition | `Texture_Balance_Score_Phase6`, `Soil_Physical_Condition_Score_Phase6`, `Soil_Chemical_Fertility_Score_Phase6` |
| Climate context | `Climate_Comfort_Score_Phase6` |
| Integrated soil health | `Soil_Health_Index_Phase6` |

## 4. Formula Principles

- Raw diversity and soil variables are normalized to comparable 0-1 scales before scoring.
- Beneficial microbial groups are log-transformed before normalization because count-like microbial values span large ranges.
- Pathogen pressure is represented both as a normalized `Fusarium` load and as a pathogen-beneficial ratio.
- Nutrient balance is penalized when N, P, and K are uneven rather than simply high.
- Soil-health scoring combines chemical, physical, microbial, climate, and pathogen-pressure components.

## 5. Training-Split Feature Selection

Feature selection uses the Phase 5 training split only.

Selection steps:

1. Compute target associations on training rows.
2. Assign biological priority to key agronomic and microbiome features.
3. Rank by biological priority and target association.
4. Remove highly redundant features at abs correlation >= 0.95.
5. Keep a selected numeric feature set of 34 features.

Categorical features from Phase 5 remain available for encoding:

- `Village`
- `Mango_Variety`
- `Soil_Depth`
- `Sampling_Season`
- `Management`

## 6. Redundancy and Multicollinearity

The pipeline writes:

- `outputs/feature_engineering/redundancy_pairs.csv`
- `outputs/feature_engineering/multicollinearity_vif.csv`

High VIF is expected for:

- Texture fractions that sum to 100.
- Taxonomic groups normalized within domains.
- Composite engineered indices derived from raw variables.

This does not automatically mean the features are invalid. It means Phase 7 should compare raw, engineered, and reduced feature sets carefully.

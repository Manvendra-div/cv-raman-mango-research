# Feature Documentation

Machine-readable feature documentation is stored at:

```text
data/processed/feature_documentation.csv
```

## Phase 6 Feature Families

### Microbiome Diversity

`Diversity_Score_Phase6` combines OTU count, Chao1 richness, Shannon diversity, Simpson index, and Pielou evenness. It summarizes microbial richness, diversity, and evenness.

`Richness_Evenness_Balance_Phase6` focuses on whether richness is accompanied by even community structure.

### Functional Microbial Summaries

`Beneficial_Microbial_Index_Phase6` summarizes nitrogen fixers, phosphate solubilizers, potassium solubilizers, AMF, Trichoderma, and Pseudomonas PGPR.

`Nutrient_Cycling_Index_Phase6` focuses on nutrient-cycling microbes.

`Biocontrol_Index_Phase6` summarizes Trichoderma and Pseudomonas PGPR.

### Pathogen Pressure

`Pathogen_Load_Index_Phase6` normalizes Fusarium load.

`Pathogen_Beneficial_Ratio_Phase6` compares Fusarium load against beneficial microbial abundance.

`Beneficial_to_Pathogen_Log_Ratio_Phase6` measures beneficial dominance over pathogen pressure.

### Nutrient and Soil Health

`NPK_Balance_Score_Phase6` summarizes balanced nitrogen, phosphorus, and potassium status.

`Micronutrient_Balance_Score_Phase6` summarizes zinc, iron, manganese, and copper balance.

`Texture_Balance_Score_Phase6`, `Soil_Physical_Condition_Score_Phase6`, and `Soil_Chemical_Fertility_Score_Phase6` describe soil physical and chemical suitability.

`Soil_Health_Index_Phase6` integrates soil chemical, soil physical, microbial diversity, beneficial microbes, climate comfort, and pathogen penalty into one interpretable index.

## Interpretation Caution

These features are interpretable proxies. They support modeling and explanation, but they are not direct causal proof and should be validated with real orchard samples.

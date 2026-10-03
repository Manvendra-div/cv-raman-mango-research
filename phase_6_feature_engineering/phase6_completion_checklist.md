# Phase 6 Completion Checklist

| Phase 6 task from outline | Status | Evidence |
|---|---|---|
| Calculate diversity scores from OTU or ASV tables | Complete for current OTU-style columns | `Diversity_Score_Phase6`; `Richness_Evenness_Balance_Phase6`; `src/feature_engineering/phase6_feature_engineering.py` |
| Calculate pathogen-load metrics | Complete | `Pathogen_Load_Index_Phase6`; `Pathogen_Beneficial_Ratio_Phase6`; `Beneficial_to_Pathogen_Log_Ratio_Phase6` |
| Calculate nutrient-balance indicators | Complete | `NPK_Balance_Score_Phase6`; `Micronutrient_Balance_Score_Phase6` |
| Calculate soil-health index | Complete | `Soil_Health_Index_Phase6` |
| Create microbial functional group summaries | Complete | `Beneficial_Microbial_Index_Phase6`; `Nutrient_Cycling_Index_Phase6`; `Biocontrol_Index_Phase6` |
| Evaluate feature redundancy and multicollinearity | Complete | `outputs/feature_engineering/redundancy_pairs.csv`; `outputs/feature_engineering/multicollinearity_vif.csv` |
| Select biologically meaningful features for modeling | Complete | `data/processed/selected_features.json`; `outputs/reports/phase6_feature_engineering/feature_selection_report.md` |
| Produce engineered feature table | Complete | `data/processed/engineered_feature_table.csv` |
| Produce feature documentation | Complete | `data/processed/feature_documentation.csv`; `feature_documentation.md` |
| Produce feature-selection report | Complete | `outputs/reports/phase6_feature_engineering/feature_selection_report.md` |

## Phase 6 Exit Decision

Phase 6 is complete for the currently available synthetic dataset. The next implementation phase should be Phase 7: Model Development.

## Locked Phase 6 Decisions

| Topic | Decision |
|---|---|
| Feature-engineering script | `src/feature_engineering/phase6_feature_engineering.py` |
| Engineered feature table | `data/processed/engineered_feature_table.csv` |
| Full feature table | `data/processed/feature_table.csv` |
| Feature documentation | `data/processed/feature_documentation.csv` |
| Feature selection split | Phase 5 train split only |
| Selected numeric feature count | 34 |
| Categorical features retained separately | Village, mango variety, soil depth, sampling season, management |
| Redundancy threshold | abs correlation >= 0.95 for feature-selection filtering |

## Carry-Forward Notes for Phase 7

- High VIF values are expected because taxonomic and texture values have sum constraints and because composite indices are derived from raw variables.
- Phase 7 should compare raw, engineered, selected, and combined feature sets.
- Selected features are not final proof of biological importance; XAI and validation phases must confirm useful interpretation.

# Diversity-Index Table

## 1. Purpose

The diversity-index table stores sample-level microbiome diversity metrics calculated from ASV or OTU tables. It supports microbial richness analysis, soil-health interpretation, and feature engineering.

Editable CSV template:

- `templates/diversity_index_table_template.csv`

Recommended output location:

- `data/interim/diversity_indices/`

## 2. Row Granularity

Use one row per parent composite per sequencing target.

Example:

```text
Parent_Composite_ID + Sequencing_Target
```

This allows separate 16S and ITS diversity values. Phase 5 or Phase 6 may later create combined diversity features.

## 3. Required Metrics

| Metric | Meaning |
|---|---|
| `OTU_Count` or `ASV_Count` | Observed features |
| `Shannon_Index` | Alpha diversity |
| `Simpson_Index` | Dominance/diversity |
| `Chao1_Richness` | Estimated richness, if supported |
| `Pielou_Evenness` | Evenness |

## 4. Calculation Metadata

Record:

- `Feature_Table_Source`
- `Rarefaction_Depth`
- `Normalization_Method`
- `Bioinformatics_Run_ID`
- `Diversity_QC_Status`

## 5. Acceptance Rules

Flag as `Conditional` when:

- Read depth is low.
- Rarefaction depth excludes many samples.
- Chao1 is not supported by the chosen workflow.
- Diversity values are calculated from a filtered subset.

Flag as `Fail` when:

- Feature table cannot be traced to a sequencing target.
- Sample ID cannot be merged to the parent composite.
- Metric values are impossible, such as negative richness.

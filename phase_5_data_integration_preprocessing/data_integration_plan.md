# Data Integration Plan

## 1. Objective

Merge field metadata, soil chemistry, climate context, microbiome outputs, and target records into a clean master dataset suitable for feature engineering and modeling.

## 2. Current Synthetic Dataset Path

For the current workspace, Phase 5 uses:

```text
data/raw/mango_microbiome_dataset.csv
```

This file already contains integrated metadata, soil, climate, microbiome, engineered, and target columns. The Phase 5 script therefore performs cleaning, standardization, validation, splitting, encoding, and scaling directly on this file.

## 3. Future Real-Data Integration Inputs

When real Phase 3 and Phase 4 data exist, the clean master dataset should be built from:

| Data type | Expected source |
|---|---|
| Field metadata | `data/raw/field_metadata/` |
| Initial parent-composite dataset | `data/raw/real_sample_dataset/` |
| Soil chemistry | `data/interim/soil_qc/` |
| DNA extraction records | `data/interim/dna_extraction/` |
| Microbiome QC | `data/interim/microbiome_qc/` |
| ASV/OTU abundance | `data/interim/otu_or_asv_tables/` |
| Taxonomy | `data/interim/taxonomy_tables/` |
| Diversity indices | `data/interim/diversity_indices/` |
| Wide taxonomic abundance | `data/interim/microbial_abundance/` |
| Yield and disease records | Field metadata or later agronomic follow-up tables |

## 4. Primary Merge Keys

| Merge level | Key |
|---|---|
| Parent composite | `Parent_Composite_ID` |
| Soil chemistry | `Parent_Composite_ID` + `Chem_Sample_ID` |
| 16S microbiome | `Parent_Composite_ID` + `DNA_Sample_ID` + `Sequencing_Target=16S` |
| ITS microbiome | `Parent_Composite_ID` + `DNA_Sample_ID` + `Sequencing_Target=ITS` |
| Synthetic prototype | `Sample_ID` |

Do not merge real lab outputs only by village, orchard, date, or depth because duplicates and QC samples may exist.

## 5. Integration Order for Real Data

1. Start with the Phase 3 initial real-sample dataset.
2. Keep one row per `Parent_Composite_ID`.
3. Join QC-approved soil chemistry rows.
4. Join QC-approved diversity-index summaries.
5. Join QC-approved wide taxonomic abundance summaries.
6. Join field disease and yield records.
7. Mark row-level status as `Ready`, `Conditional`, or `Rejected`.
8. Exclude rejected rows from model-ready outputs.

## 6. Current Synthetic Cleaning Rules

The implemented preprocessing script:

- Preserves the raw CSV unchanged.
- Standardizes text fields.
- Repairs soil-depth mojibake to `0-15` and `15-30`.
- Clips negative taxonomic abundance values to zero.
- Normalizes bacterial, fungal, and archaeal taxonomic groups separately.
- Adds preprocessing metadata columns.
- Writes a clean master dataset.

## 7. Source Manifest

Use this template to record future real-data input files:

- `templates/integration_source_manifest_template.csv`

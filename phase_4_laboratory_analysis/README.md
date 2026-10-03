# Phase 4: Laboratory Analysis

Implemented on: 2026-06-26

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 4 from `Detailed_Research_Work_Outline.md`. Phase 4 receives Phase 3 field samples and produces laboratory and microbiome outputs needed for integration, preprocessing, feature engineering, and modeling.

## Source Inputs Used

- `Detailed_Research_Work_Outline.md`
- `phase_3_soil_microbiome_data_collection/initial_real_sample_dataset.md`
- `phase_3_soil_microbiome_data_collection/chain_of_custody.md`
- `phase_1_literature_review/final_technical_workflow.md`

## Phase 4 Outputs

| Output required by methodology | Implemented artifact |
|---|---|
| Soil chemistry table | `soil_chemistry_table.md`, `templates/soil_chemistry_table_template.csv` |
| Microbial abundance table | `microbial_abundance_table.md`, `templates/asv_abundance_table_template.csv`, `templates/sample_taxa_abundance_wide_template.csv` |
| Diversity-index table | `diversity_index_table.md`, `templates/diversity_index_table_template.csv` |
| Taxonomic table | `taxonomic_table.md`, `templates/taxonomic_assignment_table_template.csv` |
| Quality-control report | `quality_control_report.md`, `templates/lab_qc_report_template.csv`, `templates/sequencing_qc_summary_template.csv` |
| Soil testing SOP | `soil_physicochemical_testing_sop.md` |
| DNA extraction and sequencing target plan | `dna_extraction_and_sequencing_plan.md` |
| Sequencing read generation SOP | `sequencing_read_generation_sop.md` |
| Bioinformatics pipeline | `bioinformatics_pipeline.md` |
| Completion evidence | `phase4_completion_checklist.md` |

## Data Folders Created

Raw inputs:

- `data/raw/lab_soil_tests/`
- `data/raw/sequencing_reads/16S/`
- `data/raw/sequencing_reads/ITS/`

Interim outputs:

- `data/interim/soil_qc/`
- `data/interim/dna_extraction/`
- `data/interim/sequencing_manifests/`
- `data/interim/microbiome_qc/`
- `data/interim/otu_or_asv_tables/`
- `data/interim/taxonomy_tables/`
- `data/interim/diversity_indices/`
- `data/interim/microbial_abundance/`

Reports:

- `outputs/reports/phase4_lab_analysis/`

## Phase 4 Boundary

Actual laboratory measurements and sequencing runs must be performed by the laboratory or sequencing facility. This implementation completes the project-side Phase 4 structure, SOPs, table schemas, QC logic, and bioinformatics handoff plan.

## Ready for Phase 5

Phase 4 is ready for Phase 5 when:

- Soil chemistry results are complete and QC-reviewed.
- DNA extraction records are complete.
- 16S and ITS sequencing read files are received and manifest files are valid.
- ASV/OTU tables are generated.
- Taxonomic assignments are generated.
- Diversity-index tables are generated.
- Lab and sequencing QC reports are signed off.

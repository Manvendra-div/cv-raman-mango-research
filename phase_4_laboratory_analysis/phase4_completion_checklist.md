# Phase 4 Completion Checklist

| Phase 4 task from outline | Status | Evidence |
|---|---|---|
| Test soil physicochemical properties: pH, EC, organic carbon, N, P, K, soil moisture, soil temperature, bulk density, CEC, texture, micronutrients | Complete as SOP and table schema | `soil_physicochemical_testing_sop.md`; `soil_chemistry_table.md`; `templates/soil_chemistry_table_template.csv` |
| Perform microbial DNA extraction | Complete as SOP and log schema | `dna_extraction_and_sequencing_plan.md`; `templates/dna_extraction_log_template.csv` |
| Define sequencing targets clearly: 16S rRNA for bacteria/archaea and ITS for fungi | Complete | `dna_extraction_and_sequencing_plan.md`, Section 3 |
| Generate sequencing reads | Complete as SOP and manifest schema | `sequencing_read_generation_sop.md`; `templates/sequencing_manifest_16s_template.csv`; `templates/sequencing_manifest_its_template.csv` |
| Process reads using a bioinformatics pipeline | Complete as reproducible workflow contract | `bioinformatics_pipeline.md` |
| Generate OTU or ASV tables and taxonomic assignments | Complete as output schemas | `microbial_abundance_table.md`; `taxonomic_table.md`; `templates/asv_abundance_table_template.csv`; `templates/taxonomic_assignment_table_template.csv` |
| Produce soil chemistry table | Complete | `soil_chemistry_table.md`; `templates/soil_chemistry_table_template.csv` |
| Produce microbial abundance table | Complete | `microbial_abundance_table.md`; `templates/asv_abundance_table_template.csv`; `templates/sample_taxa_abundance_wide_template.csv` |
| Produce diversity-index table | Complete | `diversity_index_table.md`; `templates/diversity_index_table_template.csv` |
| Produce taxonomic table | Complete | `taxonomic_table.md`; `templates/taxonomic_assignment_table_template.csv` |
| Produce quality-control report | Complete | `quality_control_report.md`; `templates/lab_qc_report_template.csv`; `templates/sequencing_qc_summary_template.csv` |

## Phase 4 Exit Decision

Phase 4 project-side implementation is complete. Physical laboratory tests, DNA extraction, sequencing, and bioinformatics execution must now be performed using these SOPs and templates once real Phase 3 samples exist.

## Locked Phase 4 Decisions

| Topic | Decision |
|---|---|
| Soil chemistry key | `Parent_Composite_ID` plus `Chem_Sample_ID` |
| Microbiome key | `Parent_Composite_ID` plus `DNA_Sample_ID` |
| Bacteria/archaea sequencing target | 16S rRNA |
| Fungal sequencing target | ITS |
| Preferred feature unit | ASV where workflow supports it |
| 16S taxonomy database | SILVA or documented equivalent |
| ITS taxonomy database | UNITE or documented equivalent |
| Diversity metrics | ASV/OTU count, Shannon, Simpson, Chao1, Pielou |
| QC vocabulary | Pass, Conditional, Fail, Pending |
| Primary Phase 5 merge key | `Parent_Composite_ID` |

## Raw and Interim Data Landing Folders

- `data/raw/lab_soil_tests/`
- `data/raw/sequencing_reads/16S/`
- `data/raw/sequencing_reads/ITS/`
- `data/interim/soil_qc/`
- `data/interim/dna_extraction/`
- `data/interim/sequencing_manifests/`
- `data/interim/microbiome_qc/`
- `data/interim/otu_or_asv_tables/`
- `data/interim/taxonomy_tables/`
- `data/interim/diversity_indices/`
- `data/interim/microbial_abundance/`
- `outputs/reports/phase4_lab_analysis/`

## Ready-To-Use Templates

- `templates/soil_chemistry_table_template.csv`
- `templates/dna_extraction_log_template.csv`
- `templates/sequencing_manifest_16s_template.csv`
- `templates/sequencing_manifest_its_template.csv`
- `templates/asv_abundance_table_template.csv`
- `templates/sample_taxa_abundance_wide_template.csv`
- `templates/diversity_index_table_template.csv`
- `templates/taxonomic_assignment_table_template.csv`
- `templates/lab_qc_report_template.csv`
- `templates/sequencing_qc_summary_template.csv`

## Carry-Forward Notes for Phase 5

- Only `Pass` and approved `Conditional` rows should enter the clean master dataset.
- Keep 16S and ITS outputs separate until normalization and integration rules are applied.
- Do not treat relative abundance as absolute microbial load.
- Keep database versions and bioinformatics parameters in the QC report.
- Preserve `Parent_Composite_ID` in every Phase 5 merge.

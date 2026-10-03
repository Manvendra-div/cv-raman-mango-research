# Phase 3: Soil and Microbiome Data Collection

Implemented on: 2026-06-26

Project: Hybrid AI with Explainable AI for Soil Microbiome Analysis and Predictive Modeling for Mango Crop at Malihabad (U.P.)

## Purpose

This folder implements Phase 3 from `Detailed_Research_Work_Outline.md`. Phase 3 turns the Phase 2 study design into field-execution records for collecting rhizosphere soil, preparing composite samples, recording orchard metadata, preserving cold-chain integrity, and producing the initial real-sample dataset structure.

## Source Inputs Used

- `Detailed_Research_Work_Outline.md`
- `phase_2_study_design_sampling_framework/site_selection_plan.md`
- `phase_2_study_design_sampling_framework/sampling_protocol.md`
- `phase_2_study_design_sampling_framework/sample_labeling_convention.md`
- `phase_2_study_design_sampling_framework/metadata_template.md`
- `phase_2_study_design_sampling_framework/sample_size_framework.md`

## Phase 3 Outputs

| Output required by methodology | Implemented artifact |
|---|---|
| Field sample inventory | `field_sample_inventory.md`, `templates/field_sample_inventory_template.csv` |
| Chain-of-custody sheet | `chain_of_custody.md`, `templates/chain_of_custody_template.csv` |
| Metadata table | `metadata_table.md`, `templates/field_metadata_collection_template.csv` |
| Initial real-sample dataset | `initial_real_sample_dataset.md`, `templates/initial_real_sample_dataset_template.csv` |
| Field collection SOP | `field_collection_sop.md` |
| Composite sample preparation SOP | `composite_sample_preparation_sop.md` |
| Cold-chain and biological storage SOP | `cold_chain_storage_sop.md` |
| Daily field log | `templates/daily_field_log_template.csv` |
| Completion evidence | `phase3_completion_checklist.md` |

## Raw Data Folders Created

- `data/raw/field_sample_inventory/`
- `data/raw/chain_of_custody/`
- `data/raw/real_sample_dataset/`

Completed field files should be copied into these folders after each field visit.

## Phase 3 Boundary

Physical soil collection must occur in the orchard. This implementation completes the project-side Phase 3 structure, SOPs, templates, acceptance checks, and raw-data landing folders. The actual sample rows will be populated during field visits.

## Ready for Phase 4

Phase 3 is ready for Phase 4 laboratory analysis when:

- Field sample inventory is complete.
- Chain-of-custody records are signed and reconciled.
- Metadata table has one row per physical sample fraction.
- Initial real-sample dataset has one row per parent composite.
- CHEM, 16S, ITS, and ARCH fractions are stored under documented conditions.

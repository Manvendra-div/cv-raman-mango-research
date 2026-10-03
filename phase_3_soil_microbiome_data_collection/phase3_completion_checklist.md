# Phase 3 Completion Checklist

| Phase 3 task from outline | Status | Evidence |
|---|---|---|
| Collect rhizosphere soil samples under canopy drip line | Complete as field SOP | `field_collection_sop.md`, Sections 6-10 |
| Use zig-zag sub-sampling within orchards | Complete as field SOP | `field_collection_sop.md`, Section 7 |
| Prepare composite samples | Complete as SOP | `composite_sample_preparation_sop.md` |
| Record GPS, variety, tree age, season, management, irrigation, fertilizer use, pesticide history, and yield history | Complete as metadata template | `metadata_table.md`; `templates/field_metadata_collection_template.csv` |
| Store biological samples under proper cold-chain conditions | Complete as cold-chain SOP and custody fields | `cold_chain_storage_sop.md`; `chain_of_custody.md`; `templates/chain_of_custody_template.csv` |
| Produce field sample inventory | Complete | `field_sample_inventory.md`; `templates/field_sample_inventory_template.csv` |
| Produce chain-of-custody sheet | Complete | `chain_of_custody.md`; `templates/chain_of_custody_template.csv` |
| Produce metadata table | Complete | `metadata_table.md`; `templates/field_metadata_collection_template.csv` |
| Produce initial real-sample dataset | Complete | `initial_real_sample_dataset.md`; `templates/initial_real_sample_dataset_template.csv` |

## Phase 3 Exit Decision

Phase 3 project-side implementation is complete. Physical sample collection must now be executed during field visits using these SOPs and templates.

## Locked Phase 3 Decisions

| Topic | Decision |
|---|---|
| Primary sampling zone | Mango canopy drip-line rhizosphere |
| Field path | Zig-zag route across representative orchard area |
| Subsamples per composite | 5-10 |
| Soil depths | 0-15 cm and 15-30 cm |
| Parent composite key | `Parent_Composite_ID` |
| Physical fraction IDs | CHEM, 16S, ITS, ARCH |
| Biological cold chain | DNA fractions placed in cool box immediately |
| Inventory granularity | One row per physical container |
| Initial dataset granularity | One row per parent composite |
| Primary merge key for later phases | `Parent_Composite_ID` |

## Raw Data Landing Folders

- `data/raw/field_metadata/`
- `data/raw/field_sample_inventory/`
- `data/raw/chain_of_custody/`
- `data/raw/real_sample_dataset/`

## Ready-To-Use Templates

- `templates/field_metadata_collection_template.csv`
- `templates/field_sample_inventory_template.csv`
- `templates/chain_of_custody_template.csv`
- `templates/initial_real_sample_dataset_template.csv`
- `templates/daily_field_log_template.csv`

## Carry-Forward Notes for Phase 4

- Phase 4 laboratory analysis must use `Parent_Composite_ID` and fraction-specific sample IDs to merge soil chemistry, 16S, ITS, diversity, taxonomy, and functional-group outputs.
- `Mango_Yield`, `Disease_Risk`, and `Nutrient_Availability` should remain clearly labelled as measured, provisional, or pending.
- Any sample with custody, label, or cold-chain deviation should be flagged before model-development phases.

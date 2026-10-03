# Phase 2 Completion Checklist

| Phase 2 task from outline | Status | Evidence |
|---|---|---|
| Select representative mango orchards across Malihabad and nearby mango-growing villages | Complete | `site_selection_plan.md`, Sections 2-13 |
| Stratify orchards by yield history, management type, soil type, tree age, and variety | Complete | `site_selection_plan.md`, Sections 7-10 |
| Define sampling depths, seasons, replicate count, and composite sampling protocol | Complete | `sampling_protocol.md`, Sections 2-8; `sample_size_framework.md` |
| Define metadata collection form | Complete | `metadata_template.md`; `templates/field_metadata_template.csv`; `templates/orchard_registry_template.csv` |
| Define minimum real-world sample size for pilot validation and later model refinement | Complete | `sample_size_framework.md` |
| Produce site selection plan | Complete | `site_selection_plan.md` |
| Produce sampling protocol | Complete | `sampling_protocol.md` |
| Produce metadata template | Complete | `metadata_template.md`; `templates/field_metadata_template.csv` |
| Produce field visit schedule | Complete | `field_visit_schedule.md`; `templates/field_visit_schedule.csv` |
| Produce sample labeling convention | Complete | `sample_labeling_convention.md` |

## Phase 2 Exit Decision

Phase 2 is ready to close. The next implementation phase should be Phase 3: Soil and Microbiome Data Collection.

## Locked Phase 2 Decisions

| Topic | Decision |
|---|---|
| Study villages | Malihabad, Rahimabad, Kakori, Mall |
| Village codes | MLD, RHB, KKR, MLL |
| Minimum pilot design | 12 orchards, 72 core composites/year plus QC |
| Recommended design | 36 orchards, 216 core composites/year plus QC |
| Optional quarterly design | 36 orchards, 288 core composites/year plus QC |
| Soil depths | 0-15 cm and 15-30 cm |
| Subsamples per composite | 5-10 |
| QC duplicate rate | 10 percent or at least one duplicate per field day |
| First complete annual cycle | 2027, because 2026 winter and pre-monsoon windows have already passed |
| Sample ID pattern | `MNG-{VILLAGE}-{ORCHARD}-{YYYYMMDD}-{SEASON}-{DEPTH}-C{COMPOSITE}-{FRACTION}` |
| Raw metadata storage | `data/raw/field_metadata/` |

## Ready-To-Use Files

- `templates/orchard_registry_template.csv`
- `templates/field_metadata_template.csv`
- `templates/field_visit_schedule.csv`

## Carry-Forward Notes for Phase 3

- Print labels before field visits.
- Complete orchard registry before sample collection.
- Confirm cold-chain and lab receiving workflow before collecting DNA fractions.
- Use `Parent_Composite_ID` to link CHEM, 16S, ITS, and ARCH fractions.
- Keep farmer-identifying information outside analysis metadata.
- Record disease severity and symptoms even when final diagnosis is uncertain.

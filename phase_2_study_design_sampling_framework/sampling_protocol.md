# Sampling Protocol

## 1. Objective

Define a consistent soil sampling protocol for mango orchard rhizosphere and soil-health data collection across Malihabad, Rahimabad, Kakori, and Mall. The protocol is designed to support later physicochemical testing, microbial DNA sequencing, feature engineering, model validation, and explainable AI analysis.

## 2. Sampling Design Summary

Recommended design:

- Tier B model-refinement design from `sample_size_framework.md`.
- 36 orchards.
- 3 model-compatible seasonal windows per year.
- 2 soil depths per orchard per visit.
- 1 composite sample per orchard-depth-visit.
- 5-10 subsamples per composite.
- 10 percent field duplicates.

Minimum design:

- Tier A pilot-validation design.
- 12 orchards.
- 3 seasonal windows.
- 2 depths.
- 72 core composites per year plus QC.

## 3. Soil Depths

| Depth class | Depth code | Purpose |
|---|---|---|
| 0-15 cm | D015 | Topsoil, organic matter, fertilizer, mulch, surface biological activity |
| 15-30 cm | D1530 | Root-zone/rhizosphere soil, consistent with the original real-sample proposal |

Depth should be measured from the mineral soil surface after removing loose litter.

## 4. Seasonal Windows

| Field season | Season code | Model season | Indicative period | Crop stage |
|---|---|---|---|---|
| Winter/pre-flowering | WIN | Winter | January-February | Pre-flowering and flowering preparation |
| Pre-monsoon/fruit development | PRE | Pre-monsoon | April-May | Fruit setting and development |
| Monsoon/post-harvest | MON | Post-monsoon | July-August | Post-harvest and vegetative growth |
| Post-monsoon/dormancy preparation | POST | Post-monsoon | October-November | Dormancy preparation and next-cycle recovery |

The current synthetic CSV uses `Winter`, `Pre-monsoon`, and `Post-monsoon`. Real field forms should record both `Field_Season` and `Model_Season` to preserve detail without breaking compatibility.

## 5. Per-Orchard Sampling Layout

For each orchard:

1. Confirm orchard ID, village, GPS, consent code, variety, management, and visit ID.
2. Select representative trees using a zig-zag path across the orchard.
3. Avoid border rows unless border conditions are a deliberate study feature.
4. Avoid visibly disturbed patches unless sampling a disease/stress zone is explicitly recorded.
5. Collect subsamples under the canopy drip line where fine-root activity is expected.
6. Keep 0-15 cm and 15-30 cm samples separate.

Recommended subsample count:

- Minimum: 5 subsamples per depth-specific composite.
- Preferred: 8-10 subsamples per depth-specific composite.

## 6. Composite Sampling Procedure

For one orchard, one depth, one visit:

1. Label collection bag or container before soil is added.
2. Remove surface litter without removing mineral soil.
3. Use cleaned auger, corer, or trowel to collect the required depth interval.
4. Collect 5-10 subsamples from separate trees or points along the zig-zag route.
5. Place all subsamples for the same orchard-depth-visit into a clean mixing tray or sterile bag.
6. Mix thoroughly using cleaned tools.
7. Remove roots, stones, and large debris only after recording visible root condition.
8. Split the composite into analysis fractions.
9. Record sample condition, moisture, temperature, visible roots, and any unusual smell, color, or contamination.

## 7. Analysis Fractions

Each depth-specific composite should be split into:

| Fraction | Suggested amount | Container | Handling |
|---|---:|---|---|
| Soil chemistry | 300-500 g | Clean labeled soil bag | Cool and dry/air-dry later according to lab protocol |
| Microbial DNA 16S | 20-50 g | Sterile tube or sterile bag | Keep cold immediately |
| Microbial DNA ITS | 20-50 g | Sterile tube or sterile bag | Keep cold immediately |
| Archive | 50-100 g | Labeled archive bag/tube | Store as backup if freezer/cold storage is available |

If lab policy prefers one DNA fraction for both 16S and ITS extraction, record that in `Intended_Analyses`.

## 8. Field Duplicate and QC Rules

| QC sample | Frequency | Purpose |
|---|---|---|
| Field duplicate composite | 10 percent of core composites or at least 1 per field day | Estimate within-orchard and sampling variability |
| Equipment blank | At least 1 per field day when sterile water/material is available | Check cross-contamination from tools |
| Travel blank | At least 1 per sampling trip for DNA containers if feasible | Check transport contamination |
| Label audit | Every sample before leaving site | Prevent ID mismatch |

Field duplicates must be independently collected, not just split from the same mixed composite.

## 9. Tool Cleaning Between Samples

Between orchard-depth combinations:

1. Remove visible soil from tools.
2. Wash or wipe tools with clean water.
3. Disinfect according to lab-approved field protocol.
4. Dry or wipe before the next sample.
5. Change gloves when moving between orchards and whenever contamination is suspected.

Keep DNA sampling tools and soil-chemistry tools separate where feasible.

## 10. Cold Chain and Transport

Microbial DNA fractions:

- Keep in an ice box immediately after collection.
- Record cold-chain start time.
- Transfer to laboratory cold storage as soon as possible.
- Record lab receipt date and time.

Soil chemistry fractions:

- Keep labeled and protected from contamination.
- Avoid prolonged direct sunlight.
- Follow laboratory instructions for drying, sieving, and storage.

## 11. Field Metadata Collection

At each orchard visit, record:

- Sample IDs and parent composite IDs.
- GPS coordinates and accuracy.
- Date, time, field season, model season.
- Variety, tree age, management type.
- Soil depth and number of subsamples.
- Yield history and current crop stage.
- Fertilizer, pesticide, irrigation, and organic amendment history.
- Visible disease symptoms and severity score.
- Field soil moisture and temperature where instruments are available.
- Weather context and rainfall in the previous week if known.
- Sample condition and notes.

Use:

- `metadata_template.md`
- `templates/field_metadata_template.csv`

## 12. Disease and Plant Health Scoring

Record disease observations even if disease diagnosis is not final.

Suggested field severity score:

| Score | Description |
|---:|---|
| 0 | No visible symptoms |
| 1 | Very mild symptoms on few leaves/twigs/fruits |
| 2 | Mild but clear symptoms |
| 3 | Moderate symptoms across multiple trees |
| 4 | Severe symptoms affecting production |
| 5 | Very severe symptoms or widespread decline |

Also record suspected symptom category:

- Anthracnose-like lesions
- Malformation-like symptoms
- Dieback
- Root-zone stress
- Yellowing/chlorosis
- Fruit rot
- Other
- Unknown

## 13. Sample Acceptance Criteria

A sample is acceptable if:

1. Sample ID matches metadata and label.
2. Orchard ID and GPS are recorded.
3. Depth and field season are recorded.
4. Subsample count is recorded.
5. Analysis fractions are labelled.
6. DNA fraction cold-chain time is recorded.
7. No major contamination event occurred.

If any criterion fails, flag the sample as `Conditional` or `Reject` in metadata.

## 14. Handover to Phase 3

At the end of each field day:

1. Reconcile sample labels against metadata rows.
2. Count expected and actual containers.
3. Record missing, damaged, or conditional samples.
4. Transfer DNA fractions to cold storage.
5. Transfer soil chemistry fractions according to lab protocol.
6. Save the field metadata file in `data/raw/field_metadata/`.
7. Create a daily field note file or scan field forms.

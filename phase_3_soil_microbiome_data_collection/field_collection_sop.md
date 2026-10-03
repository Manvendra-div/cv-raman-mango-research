# Field Collection SOP

## 1. Objective

Collect mango orchard rhizosphere soil samples under the canopy drip line using a consistent zig-zag subsampling method, while recording the metadata needed for soil chemistry, microbiome analysis, yield interpretation, disease-risk analysis, and later AI/XAI modeling.

## 2. Scope

This SOP applies to all Phase 3 field visits in:

- Malihabad
- Rahimabad
- Kakori
- Mall

It supports both the Tier A pilot design and Tier B recommended model-refinement design from Phase 2.

## 3. Required Field Materials

| Category | Items |
|---|---|
| Identification | Printed labels, waterproof marker, daily sample sheet, orchard registry, sample ID list |
| Sampling | Soil auger/corer/trowel, measuring tape or depth marker, clean mixing tray, sterile bags/tubes, gloves |
| Cleaning | Clean water, brush, lint-free wipes, disinfectant approved by the lab, waste bag |
| Cold chain | Cool box, ice packs, thermometer or temperature logger, cold-chain log |
| Field measurement | GPS device/phone, soil thermometer, soil moisture meter if available, camera if permitted |
| Documentation | Metadata forms, field inventory sheet, chain-of-custody sheet, daily field log |
| Safety | First-aid kit, drinking water, sun protection, field footwear |

## 4. Pre-Departure Checklist

Before leaving for the field:

1. Confirm visit ID, village route, selected orchards, and replacement orchards.
2. Print labels for all expected CHEM, 16S, ITS, ARCH, QC, and blank samples.
3. Load or print metadata templates.
4. Confirm cool boxes and ice packs are ready.
5. Confirm lab receiving person and expected arrival window.
6. Check sampling tools are clean.
7. Carry spare labels and blank forms.
8. Record field team members in the daily field log.

## 5. Orchard Arrival Procedure

At each orchard:

1. Confirm orchard identity using `Orchard_ID`, village, and consent code.
2. Record GPS coordinates and GPS accuracy.
3. Confirm mango variety, approximate tree age, management type, irrigation type, and recent inputs.
4. Record field season, model season, date, time, and phenological stage.
5. Walk the orchard and note disease symptoms, canopy condition, unusual soil condition, waterlogging, or recent disturbance.
6. Confirm sampling points before opening sterile containers.

## 6. Rhizosphere Sampling Zone

Collect from the canopy drip line, where active roots and microbial interactions are expected.

Avoid:

- Direct trunk base unless specifically sampling root-zone disease.
- Field borders, roadsides, compost piles, dumping zones, drainage channels, and visibly contaminated patches.
- Fresh fertilizer granules, pesticide spill points, or irrigation leakage points unless intentionally recorded as a stress zone.

Record any deviation in `Notes`.

## 7. Zig-Zag Subsampling Method

For each orchard-depth combination:

1. Start near one corner or accessible edge of the orchard.
2. Walk a zig-zag route across the representative production area.
3. Select 5-10 trees or sampling points along the route.
4. Keep points spatially separated enough to represent the orchard.
5. Collect from beneath the canopy drip line at each selected tree.
6. Record `Subsample_Count` and `Zigzag_Point_Count`.

Recommended:

- Tier A: 5-8 subsamples per composite.
- Tier B: 8-10 subsamples per composite where field time allows.

## 8. Depth Collection Procedure

Depths:

- `D015`: 0-15 cm.
- `D1530`: 15-30 cm.

Steps:

1. Remove loose surface litter without removing mineral soil.
2. Insert auger/corer/trowel to the required depth interval.
3. Keep depth intervals separate.
4. Place soil from all subsampling points for the same depth into the same depth-specific composite container or mixing bag.
5. Clean the tool before switching orchard, depth, or QC sample as required.

## 9. Required Metadata at Collection

Record these at the time of sampling:

- GPS latitude and longitude.
- GPS accuracy.
- Mango variety.
- Tree age and age class.
- Field season and model season.
- Management type.
- Irrigation type and last irrigation date if known.
- Fertilizer use in last 30 days.
- Pesticide use in last 30 days.
- Organic amendment use in last 90 days.
- Yield history.
- Productivity history.
- Disease symptoms and severity score.
- Soil depth and subsample count.
- Field soil moisture and temperature if available.

## 10. Immediate Fraction Handling

After preparing the composite, create these fractions:

| Fraction | Code | Handling priority |
|---|---|---|
| Microbial DNA 16S | 16S | Highest; place in cold box immediately |
| Microbial DNA ITS | ITS | Highest; place in cold box immediately |
| Soil chemistry | CHEM | Protect from contamination and sunlight |
| Archive | ARCH | Store as backup under documented condition |

If one DNA extraction will support both 16S and ITS, still record intended analyses clearly.

## 11. Label Audit

Before leaving the orchard:

1. Match each physical container to a metadata row.
2. Confirm sample ID, parent composite ID, orchard ID, date, depth, and fraction.
3. Mark `Label_Audit_Status=Pass`, `Conditional`, or `Fail`.
4. Correct labels only before samples leave the orchard.
5. Never reuse a sample ID after a failed label.

## 12. End-of-Day Procedure

At the end of each field day:

1. Count all physical containers.
2. Reconcile inventory, metadata, and chain-of-custody sheets.
3. Confirm cold-chain entries for all 16S and ITS fractions.
4. Hand over samples to lab or storage contact.
5. Save completed CSV files into the matching `data/raw/` folders.
6. Note any rejected, damaged, missing, delayed, or conditional samples.

## 13. Field Safety and Ethics

- Do not record farmer names in analysis files.
- Use consent codes only.
- Follow farmer/manager instructions about access and tree handling.
- Do not damage roots unnecessarily.
- Restore disturbed soil as much as possible after collection.

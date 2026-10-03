# Metadata Table

## 1. Purpose

The Phase 3 metadata table records field observations and sample handling details needed to connect each physical sample fraction to its orchard, visit, composite, field condition, and later laboratory results.

Editable CSV template:

- `templates/field_metadata_collection_template.csv`

Completed raw metadata should be saved in:

- `data/raw/field_metadata/`

## 2. Row Granularity

Use one row per physical sample fraction when container-level traceability is required.

For one parent composite, expected rows may include:

- CHEM
- 16S
- ITS
- ARCH

Use `Parent_Composite_ID` to link these fraction rows back to the same composite.

## 3. Required Field Metadata

Phase 3 specifically requires recording:

- GPS coordinates.
- Mango variety.
- Tree age.
- Field season and model season.
- Management.
- Irrigation history.
- Fertilizer history.
- Pesticide history.
- Yield history.

The metadata template also includes disease scoring, field conditions, cold-chain timing, and sample acceptance fields.

## 4. Metadata Quality Rules

1. `Sample_ID` must be unique.
2. `Parent_Composite_ID` must be identical across all fractions from the same composite.
3. `Orchard_ID`, `Village`, `Sampling_Date`, `Depth_Code`, and `Fraction` must never be blank.
4. DNA fractions must have `Cold_Chain_Start_Time`.
5. `Label_Audit_Status` must be completed before the sample leaves the orchard.
6. `Sample_Status` must be `Collected`, `Conditional`, `Rejected`, or `Missing`.
7. Unknown management or input history should be recorded as `Unknown`, not guessed.
8. Farmer-identifying information must not be stored in the metadata table.

## 5. Field Disease and Yield Notes

Field disease observations should be treated as field labels until verified. Use:

- `Visible_Disease`
- `Primary_Disease_Symptom`
- `Disease_Severity_0_5`
- `Disease_Risk_Field`

Yield fields should capture what is available:

- `Yield_History_kg_per_tree`
- `Yield_History_Source`
- `Productivity_History`

If measured yield is unavailable, record the source as `Farmer_Record`, `Orchard_Manager_Estimate`, `Extension_Record`, or `Unknown`.

## 6. Handover to Initial Dataset

After each field visit:

1. Reconcile metadata with sample inventory.
2. Collapse physical fraction rows into parent composite rows.
3. Create or append to the initial real-sample dataset.
4. Leave Phase 4 lab-result columns blank until laboratory analysis is complete.

# Soil Chemistry Table

## 1. Purpose

The soil chemistry table stores Phase 4 physicochemical results for each parent composite sample. It is the primary lab output for soil fertility, texture, salinity, micronutrient status, and soil-health feature engineering.

Editable CSV template:

- `templates/soil_chemistry_table_template.csv`

Recommended output locations:

- Raw lab files: `data/raw/lab_soil_tests/`
- QC-reviewed table: `data/interim/soil_qc/`

## 2. Row Granularity

Use one row per parent composite sample.

Primary key:

```text
Parent_Composite_ID
```

Also record:

- `Chem_Sample_ID`
- `Visit_ID`
- `Orchard_ID`
- `Depth_Code`
- `Analysis_Date`

## 3. Required Columns

The table includes all soil physicochemical variables from the project schema:

- `pH`
- `EC`
- `Organic_Carbon`
- `Total_Nitrogen`
- `Available_P`
- `Available_K`
- `Soil_Moisture`
- `Soil_Temperature`
- `Bulk_Density`
- `CEC`
- `Sand`
- `Silt`
- `Clay`
- `Zn`
- `Fe`
- `Mn`
- `Cu`
- `C_N_Ratio`

## 4. QC Columns

Every row must include:

- `Lab_Method_Set`
- `Analyst`
- `Lab_Batch_ID`
- `Duplicate_Flag`
- `Reference_Material_Status`
- `Texture_Sum_Check`
- `Soil_QC_Status`
- `Soil_QC_Notes`

## 5. Acceptance Rules

Flag as `Conditional` or `Fail` if:

- Required sample IDs are missing.
- pH or EC is outside method reportable range.
- Any concentration is negative without documented method explanation.
- Sand + silt + clay is far from 100 percent.
- Duplicate or reference material fails lab acceptance criteria.
- Chain-of-custody status is not acceptable.

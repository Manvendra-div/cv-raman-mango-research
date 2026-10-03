# Metadata Template

## 1. Purpose

This metadata template defines the fields required during Phase 3 field collection so that real samples can later be merged with soil chemistry, microbiome sequencing, yield, disease, climate, and model-output tables.

Editable CSV templates:

- `templates/orchard_registry_template.csv`
- `templates/field_metadata_template.csv`

Raw completed field metadata should be stored in:

- `data/raw/field_metadata/`

## 2. Metadata Design Rules

1. Use one row per physical analysis fraction when container-level tracking is needed.
2. Use `Parent_Composite_ID` to group CHEM, 16S, ITS, and ARCH fractions from the same composite.
3. Keep `Sample_ID` unique across the whole project.
4. Record both `Field_Season` and `Model_Season`.
5. Do not store farmer names in analysis files. Use coded consent IDs.
6. Use blank fields only when a value is truly unavailable; avoid informal values such as `ok`, `same`, or `normal`.
7. Store dates as `YYYY-MM-DD`.
8. Store times as `HH:MM` in 24-hour format.
9. Record units in column names where possible.

## 3. Orchard Registry Fields

| Field | Description | Example |
|---|---|---|
| `Orchard_ID` | Permanent full orchard identifier | `ORCH-MLD-001` |
| `Village` | Village name | `Malihabad` |
| `Village_Code` | Stable village code | `MLD` |
| `Latitude` | Orchard GPS latitude | `26.95` |
| `Longitude` | Orchard GPS longitude | `80.72` |
| `GPS_Accuracy_m` | Approximate GPS accuracy in meters | `5` |
| `Consent_Code` | Farmer/manager consent code | `CONS-MLD-001` |
| `Orchard_Area_Acre` | Orchard area | `2.5` |
| `Dominant_Mango_Variety` | Main mango variety | `Dashehari` |
| `Secondary_Varieties` | Other varieties if present | `Langra` |
| `Dominant_Tree_Age_Years` | Approximate dominant tree age | `25` |
| `Tree_Age_Class` | Young, Mature, Old | `Mature` |
| `Management` | Organic, Conventional, Integrated | `Integrated` |
| `Productivity_History` | Low, Medium, High | `High` |
| `Yield_History_kg_per_tree` | Recent average if known | `22` |
| `Soil_Type_Local` | Farmer/local soil type | `Alluvial loam` |
| `Irrigation_Type` | Drip, flood, rainfed, mixed | `Flood` |
| `Disease_History` | Known disease history | `Mild anthracnose-like symptoms` |
| `Accessibility_All_Seasons` | Yes/No | `Yes` |
| `Selected_For_Tier` | Pilot, Recommended, Replacement, Excluded | `Recommended` |
| `Selection_Notes` | Reason for selection or exclusion | `High-productivity integrated orchard` |

## 4. Field Metadata Field Groups

### 4.1 Identity Fields

- `Project_ID`
- `Visit_ID`
- `Sample_ID`
- `Parent_Composite_ID`
- `Subsample_ID`
- `Orchard_ID`
- `Village`
- `Village_Code`
- `QC_Type`
- `Fraction`
- `Intended_Analyses`

### 4.2 Location and Time Fields

- `Latitude`
- `Longitude`
- `GPS_Accuracy_m`
- `Sampling_Date`
- `Sampling_Time`
- `Field_Season`
- `Model_Season`
- `Phenological_Stage`

### 4.3 Orchard and Agronomy Fields

- `Mango_Variety`
- `Tree_Age_Years`
- `Tree_Age_Class`
- `Orchard_Area_Acre`
- `Productivity_History`
- `Yield_History_kg_per_tree`
- `Management`
- `Soil_Type_Local`
- `Irrigation_Type`
- `Last_Irrigation_Date`
- `Fertilizer_Last_30d`
- `Fertilizer_Type`
- `Pesticide_Last_30d`
- `Pesticide_Type`
- `Organic_Amendment_Last_90d`

### 4.4 Sampling Fields

- `Soil_Depth_cm`
- `Depth_Code`
- `Composite_Number`
- `Subsample_Count`
- `Zigzag_Point_Count`
- `Canopy_Position`
- `Rhizosphere_Collection`
- `Sample_Condition`
- `Label_Audit_Status`

### 4.5 Disease and Health Fields

- `Visible_Disease`
- `Primary_Disease_Symptom`
- `Disease_Severity_0_5`
- `Disease_Risk_Field`
- `Canopy_Health_0_5`
- `Weed_Cover_Percent`

### 4.6 Field Environment Fields

- `Soil_Moisture_Field`
- `Soil_Temperature_Field_C`
- `Air_Temp_Field_C`
- `Humidity_Field_Percent`
- `Rainfall_Last_7d_mm`

### 4.7 Chain-of-Custody Fields

- `Enumerator`
- `Cold_Chain_Start_Time`
- `Lab_Received_Date`
- `Lab_Received_Time`
- `Received_By`
- `Storage_Condition`
- `Notes`

## 5. Controlled Vocabularies

| Field | Allowed values |
|---|---|
| `Village_Code` | MLD, RHB, KKR, MLL, or approved new code |
| `Management` | Organic, Conventional, Integrated |
| `Productivity_History` | Low, Medium, High, Unknown |
| `Tree_Age_Class` | Young, Mature, Old, Unknown |
| `Field_Season` | Winter_PreFlowering, PreMonsoon_FruitDevelopment, Monsoon_PostHarvest, PostMonsoon_Dormancy |
| `Model_Season` | Winter, Pre-monsoon, Post-monsoon |
| `Depth_Code` | D015, D1530 |
| `QC_Type` | Core, Field_Duplicate, Equipment_Blank, Travel_Blank |
| `Fraction` | CHEM, 16S, ITS, ARCH |
| `Rhizosphere_Collection` | Yes, No |
| `Visible_Disease` | Yes, No, Unclear |
| `Disease_Risk_Field` | Low, Medium, High, Unknown |
| `Label_Audit_Status` | Pass, Conditional, Fail |
| `Sample_Condition` | Good, Wet, Dry, Contaminated, Insufficient, Conditional |

## 6. Minimum Required Fields

A metadata row is incomplete if any of these are missing:

- `Sample_ID`
- `Parent_Composite_ID`
- `Orchard_ID`
- `Village`
- `Sampling_Date`
- `Field_Season`
- `Model_Season`
- `Soil_Depth_cm`
- `Depth_Code`
- `Composite_Number`
- `Subsample_Count`
- `Fraction`
- `Intended_Analyses`
- `Label_Audit_Status`

## 7. Example Sample Group

For one orchard-depth-visit composite, there may be four physical fractions:

```text
Parent_Composite_ID: MNG-MLD-O001-20270120-WIN-D1530-C01
Sample_ID: MNG-MLD-O001-20270120-WIN-D1530-C01-CHEM
Sample_ID: MNG-MLD-O001-20270120-WIN-D1530-C01-16S
Sample_ID: MNG-MLD-O001-20270120-WIN-D1530-C01-ITS
Sample_ID: MNG-MLD-O001-20270120-WIN-D1530-C01-ARCH
```

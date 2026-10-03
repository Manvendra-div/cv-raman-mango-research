# Field Sample Inventory

## 1. Purpose

The field sample inventory is the master container-level list of what was collected during each field visit. It is used to reconcile:

- Physical sample containers.
- Metadata rows.
- Chain-of-custody entries.
- Laboratory receipt.
- Later Phase 4 analysis files.

Editable CSV template:

- `templates/field_sample_inventory_template.csv`

Completed raw inventories should be saved in:

- `data/raw/field_sample_inventory/`

## 2. Inventory Granularity

Use one row per physical container.

Example parent composite:

```text
MNG-MLD-O001-20270120-WIN-D1530-C01
```

Expected physical container rows:

```text
MNG-MLD-O001-20270120-WIN-D1530-C01-CHEM
MNG-MLD-O001-20270120-WIN-D1530-C01-16S
MNG-MLD-O001-20270120-WIN-D1530-C01-ITS
MNG-MLD-O001-20270120-WIN-D1530-C01-ARCH
```

## 3. Required Columns

| Column | Purpose |
|---|---|
| `Inventory_ID` | Unique inventory row ID |
| `Visit_ID` | Field visit ID such as V1 |
| `Sample_ID` | Physical container ID |
| `Parent_Composite_ID` | Composite grouping ID |
| `Orchard_ID` | Full orchard ID |
| `Village` | Village name |
| `Village_Code` | Village code |
| `Sampling_Date` | Field date |
| `Season_Code` | WIN, PRE, MON, POST |
| `Depth_Code` | D015 or D1530 |
| `Soil_Depth_cm` | 0-15 or 15-30 |
| `Composite_Number` | C01, C02, etc. |
| `Fraction` | CHEM, 16S, ITS, ARCH |
| `QC_Type` | Core, Field_Duplicate, Equipment_Blank, Travel_Blank |
| `Related_Sample_ID` | Link to core sample for duplicates/blanks if applicable |
| `Container_Type` | Bag, tube, vial, etc. |
| `Expected_Mass_g` | Planned mass |
| `Actual_Mass_g` | Field mass if measured |
| `Subsample_Count` | Number of subsamples mixed |
| `Collector` | Field collector |
| `Label_Audit_Status` | Pass, Conditional, Fail |
| `Sample_Status` | Collected, Conditional, Rejected, Missing |
| `Storage_Condition_Field` | Cool box, ambient shaded, etc. |
| `Notes` | Any field issue |

## 4. Inventory Reconciliation

At the end of each orchard:

1. Count physical containers.
2. Check each sample ID against the inventory.
3. Confirm every DNA fraction has a cold-chain start time in metadata or custody records.
4. Mark missing planned fractions as `Missing`, not blank.
5. Mark damaged or uncertain samples as `Conditional` or `Rejected`.

At the end of each field day:

1. Inventory count must match chain-of-custody transfer count.
2. CHEM, 16S, ITS, and ARCH counts should be summarized separately.
3. QC samples must be counted separately from core samples.
4. Deviations must be listed in the daily field log.

## 5. Expected Counts

For one core parent composite:

| Fraction plan | Physical rows |
|---|---:|
| CHEM + 16S + ITS + ARCH | 4 |
| CHEM + combined DNA + ARCH | 3, if lab uses one DNA fraction |
| CHEM + 16S + ITS only | 3, if archive is not collected |

For Tier B, one visit has:

```text
36 orchards x 2 depths = 72 core parent composites
```

With four fractions per composite:

```text
72 parent composites x 4 fractions = 288 core physical containers per visit
```

QC samples are additional.

## 6. File Naming

Use:

```text
field_sample_inventory_VISITID_YYYY-MM-DD.csv
```

Example:

```text
field_sample_inventory_V1_2027-01-20.csv
```

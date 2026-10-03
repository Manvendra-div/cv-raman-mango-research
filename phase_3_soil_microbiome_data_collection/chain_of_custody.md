# Chain-of-Custody Sheet

## 1. Purpose

The chain-of-custody sheet documents every transfer of field samples from collection to transport, laboratory receipt, and storage. It protects sample traceability and helps identify cold-chain or handling deviations before laboratory analysis.

Editable CSV template:

- `templates/chain_of_custody_template.csv`

Completed raw custody files should be saved in:

- `data/raw/chain_of_custody/`

## 2. Custody Scope

Track every physical sample container:

- CHEM
- 16S
- ITS
- ARCH
- Field duplicates
- Equipment blanks
- Travel blanks

## 3. Custody Events

Use one row per sample per custody event, or one row per sample if the sheet captures field collection through lab receipt in a single record.

Recommended event values:

- `Collected`
- `Placed_In_Cold_Box`
- `Transferred_To_Field_Lead`
- `Transferred_To_Lab`
- `Received_By_Lab`
- `Stored`
- `Rejected`

## 4. Required Columns

| Column | Purpose |
|---|---|
| `Custody_Record_ID` | Unique custody row ID |
| `Visit_ID` | Field visit ID |
| `Sample_ID` | Physical container ID |
| `Parent_Composite_ID` | Composite grouping ID |
| `Fraction` | CHEM, 16S, ITS, ARCH |
| `QC_Type` | Core, Field_Duplicate, Equipment_Blank, Travel_Blank |
| `Custody_Event` | Transfer/status event |
| `Event_Date` | Date of event |
| `Event_Time` | Time of event |
| `Released_By` | Person handing over |
| `Received_By` | Person receiving |
| `Container_Condition` | Intact, leaked, damaged, missing, unreadable label |
| `Label_Condition` | Clear, smudged, partial, unreadable |
| `Cold_Box_ID` | Cold box identifier for biological fractions |
| `Cold_Box_Temperature_C` | Temperature if available |
| `Storage_Condition` | Cool box, refrigerated, frozen, ambient, air-drying |
| `Custody_Status` | In_Transit, Received, Stored, Conditional, Rejected |
| `Deviation_Flag` | Yes/No |
| `Deviation_Description` | Short deviation text |
| `Corrective_Action` | Action taken |

## 5. Custody Rules

1. No sample leaves the orchard without a sample ID and inventory row.
2. DNA fractions must have a cold-chain event.
3. Every handover must record released-by and received-by names or initials.
4. If a label is unreadable, do not guess the ID. Mark as `Conditional` and reconcile from metadata and inventory.
5. If a container leaks, mark container condition and notify the laboratory contact before analysis.
6. Rejected samples remain in the custody file with reason documented.

## 6. Lab Receipt Reconciliation

At lab receipt:

1. Compare custody sheet with field inventory.
2. Count physical containers by fraction.
3. Confirm cold-chain records for 16S and ITS.
4. Assign lab storage location if available.
5. Mark each row `Received`, `Stored`, `Conditional`, or `Rejected`.

## 7. Deviation Examples

| Deviation | Example corrective action |
|---|---|
| Cold box temperature unavailable | Mark temperature unavailable; document ice-pack status |
| Cold-chain start delayed | Flag conditional; lab reviews DNA suitability |
| Label smudged | Reconcile with inventory and metadata before lab ID assignment |
| Container leaked | Photograph if permitted; isolate container; lab decides rejection |
| Sample count mismatch | Stop handover and reconcile before storage |

## 8. File Naming

Use:

```text
chain_of_custody_VISITID_YYYY-MM-DD.csv
```

Example:

```text
chain_of_custody_V1_2027-01-20.csv
```

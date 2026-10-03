# Sample Labeling Convention

## 1. Purpose

The sample labeling system ensures that every field sample, subsample, composite, lab aliquot, sequencing file, and analysis result can be traced back to the orchard, visit, season, depth, and intended analysis.

## 2. Core ID Pattern

Use this pattern for composite and lab-fraction IDs:

```text
MNG-{VILLAGE}-{ORCHARD}-{YYYYMMDD}-{SEASON}-{DEPTH}-C{COMPOSITE}-{FRACTION}
```

Example:

```text
MNG-MLD-O001-20270120-WIN-D1530-C01-16S
```

Meaning:

- `MNG`: mango project prefix.
- `MLD`: Malihabad village code.
- `O001`: orchard number within village.
- `20270120`: sampling date, January 20, 2027.
- `WIN`: winter/pre-flowering field season.
- `D1530`: 15-30 cm depth.
- `C01`: composite sample 1.
- `16S`: analysis fraction for bacterial/archaeal sequencing.

## 3. Orchard ID Pattern

Use:

```text
ORCH-{VILLAGE}-{NUMBER}
```

Examples:

```text
ORCH-MLD-001
ORCH-RHB-004
ORCH-KKR-009
ORCH-MLL-002
```

The short orchard code used inside sample labels is:

```text
O001
O004
O009
O002
```

The full orchard ID must be stored in metadata.

## 4. Village Codes

| Village | Code |
|---|---|
| Malihabad | MLD |
| Rahimabad | RHB |
| Kakori | KKR |
| Mall | MLL |

If a new village is added, assign a unique 3-letter code and document it in the orchard registry.

## 5. Season Codes

| Field season | Code | Model-season mapping |
|---|---|---|
| Winter/pre-flowering | WIN | Winter |
| Pre-monsoon/fruit development | PRE | Pre-monsoon |
| Monsoon/post-harvest | MON | Post-monsoon |
| Post-monsoon/dormancy preparation | POST | Post-monsoon |

## 6. Depth Codes

| Depth | Code |
|---|---|
| 0-15 cm | D015 |
| 15-30 cm | D1530 |

## 7. Fraction Codes

| Fraction | Code | Description |
|---|---|---|
| Soil chemistry | CHEM | Soil pH, EC, organic carbon, NPK, texture, micronutrients, CEC |
| 16S rRNA sequencing | 16S | Bacterial and archaeal microbiome |
| ITS sequencing | ITS | Fungal microbiome |
| Archive | ARCH | Backup soil fraction |
| Field duplicate | DUP | Duplicate composite marker, used with fraction code in metadata |
| Equipment blank | EBLK | Equipment blank |
| Travel blank | TBLK | Travel blank |

For field duplicates, keep the same structure and use the next composite number, then set `QC_Type=Field_Duplicate` in metadata.

Example:

```text
MNG-MLD-O001-20270120-WIN-D1530-C02-16S
```

## 8. Subsample ID Pattern

Use this pattern if individual subsamples are tracked before compositing:

```text
MNG-{VILLAGE}-{ORCHARD}-{YYYYMMDD}-{SEASON}-{DEPTH}-C{COMPOSITE}-SS{SUBSAMPLE}
```

Example:

```text
MNG-MLD-O001-20270120-WIN-D1530-C01-SS03
```

Subsample IDs are optional if only composite-level metadata is collected, but the subsample count is always required.

## 9. QC Sample ID Pattern

Equipment blank:

```text
MNG-{VILLAGE}-FIELD-{YYYYMMDD}-{SEASON}-EBLK-{NUMBER}
```

Travel blank:

```text
MNG-{VILLAGE}-FIELD-{YYYYMMDD}-{SEASON}-TBLK-{NUMBER}
```

Examples:

```text
MNG-MLD-FIELD-20270120-WIN-EBLK-01
MNG-MLD-FIELD-20270120-WIN-TBLK-01
```

## 10. Label Printing Rules

Labels must include:

- Sample ID.
- Orchard ID.
- Village.
- Date.
- Depth.
- Fraction.
- QR/barcode if available.

Write labels before soil enters the container. Use waterproof marker or printed waterproof labels.

## 11. Metadata Requirements

Every physical container ID must appear in the metadata file.

Required ID fields:

- `Sample_ID`
- `Parent_Composite_ID`
- `Subsample_ID` if tracked
- `Orchard_ID`
- `Visit_ID`
- `QC_Type`
- `Fraction`
- `Intended_Analyses`

## 12. Label Audit Procedure

Before leaving each orchard:

1. Read every label aloud.
2. Match it against the metadata row.
3. Confirm depth, fraction, date, and orchard.
4. Mark `Label_Audit_Status=Pass`.
5. Photograph labels if field team policy allows it.

## 13. Common Error Prevention

| Error | Prevention |
|---|---|
| Same sample ID used twice | Keep a printed daily sample sheet and mark each ID after collection. |
| Depth swapped | Use separate color stickers or bags for `D015` and `D1530`. |
| Chemistry and DNA fractions confused | Use fraction code at the end of every ID. |
| Orchard ID mismatch | Confirm full `ORCH-{VILLAGE}-{NUMBER}` before sampling. |
| Date format variation | Always use `YYYYMMDD` in IDs and `YYYY-MM-DD` in metadata. |

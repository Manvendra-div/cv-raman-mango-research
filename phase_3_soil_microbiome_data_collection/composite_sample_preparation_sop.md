# Composite Sample Preparation SOP

## 1. Objective

Prepare representative depth-specific composite soil samples from multiple rhizosphere subsamples collected under mango canopy drip lines.

## 2. Composite Definition

A parent composite represents:

```text
one orchard + one visit + one field season + one soil depth + one composite number
```

Example:

```text
MNG-MLD-O001-20270120-WIN-D1530-C01
```

The parent composite can produce multiple physical fractions:

- CHEM
- 16S
- ITS
- ARCH

## 3. Subsample Count

Minimum:

- 5 subsamples per depth-specific composite.

Preferred:

- 8-10 subsamples per depth-specific composite.

Record actual count in `Subsample_Count`.

## 4. Mixing Procedure

For each orchard-depth-visit:

1. Confirm all subsamples came from the same orchard, visit, depth, and composite number.
2. Place subsamples into a clean mixing tray or sterile mixing bag.
3. Break large clods gently using cleaned tools.
4. Remove stones and large roots only after noting root condition.
5. Mix until soil texture and color appear visually uniform.
6. Do not mix samples from different depths.
7. Do not mix core and field duplicate composites.

## 5. Fraction Split

After mixing, split the composite into physical fractions:

| Fraction | Sample ID suffix | Suggested amount | Priority |
|---|---|---:|---|
| Soil chemistry | `CHEM` | 300-500 g | Medium |
| Bacterial/archaeal DNA | `16S` | 20-50 g | High |
| Fungal DNA | `ITS` | 20-50 g | High |
| Archive | `ARCH` | 50-100 g | Medium |

If sample mass is limited:

1. Prioritize 16S and ITS fractions.
2. Preserve enough CHEM fraction for required soil testing.
3. Mark ARCH as `Not_Collected` in inventory if archive is skipped.

## 6. Field Duplicate Preparation

A field duplicate is independently collected from the same orchard-depth-visit condition. It is not a split from the same parent composite.

Rules:

- Assign a separate composite number, such as `C02`.
- Set `QC_Type=Field_Duplicate`.
- Use the same depth and season codes.
- Record field duplicate relationship in `Related_Sample_ID`.

## 7. Equipment Blank and Travel Blank

Equipment blanks and travel blanks are for contamination checks.

Equipment blank:

- Collected after tool cleaning.
- Uses field blank ID pattern.
- Set `QC_Type=Equipment_Blank`.

Travel blank:

- Opened only if the lab protocol requires it, otherwise transported sealed.
- Set `QC_Type=Travel_Blank`.

## 8. Composite Acceptance Checks

Before fraction split:

- Orchard ID confirmed.
- Depth confirmed.
- Subsample count recorded.
- Mixing container clean.
- No obvious foreign contamination.
- Label available for each fraction.

After fraction split:

- All physical fractions labelled.
- Inventory row created.
- Metadata row created.
- Chain-of-custody row created.
- DNA fractions moved to cold box.

## 9. Conditional or Rejected Composites

Set `Sample_Status=Conditional` if:

- Subsample count is below target but usable.
- Cold-chain start was delayed.
- GPS accuracy is poor but orchard identity is reliable.
- A minor metadata field is missing.

Set `Sample_Status=Reject` if:

- Orchard identity is uncertain.
- Depth is unknown or mixed.
- Sample label cannot be reconciled.
- Container leaked or sample was contaminated.
- DNA fraction was left warm beyond the accepted field window.

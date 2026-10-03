# Cold-Chain and Storage SOP

## 1. Objective

Preserve biological sample integrity for microbial DNA analysis from field collection until laboratory receipt and storage.

## 2. Scope

This SOP applies to:

- 16S rRNA sequencing fractions.
- ITS sequencing fractions.
- Archive fractions intended for biological backup.

Soil chemistry fractions do not require the same cold-chain priority, but they must still be protected from contamination and excessive heat.

## 3. Cold-Chain Rule

DNA fractions must be placed in the cool box immediately after fraction split.

Record:

- `Cold_Chain_Start_Time`
- `Cold_Box_ID`
- `Cold_Box_Temperature_C` if available
- `Lab_Received_Date`
- `Lab_Received_Time`
- `Storage_Condition`

## 4. Target Handling

| Fraction | Field handling | Lab/storage handling |
|---|---|---|
| 16S | Cool box immediately | Refrigerate short-term or freeze according to lab protocol |
| ITS | Cool box immediately | Refrigerate short-term or freeze according to lab protocol |
| ARCH | Cool box if biological archive; otherwise documented storage | Freeze if intended as biological archive |
| CHEM | Keep clean, shaded, and labelled | Air-dry/sieve or store according to soil lab protocol |

## 5. Temperature Monitoring

Recommended:

- Record cool-box temperature at start of day.
- Record temperature when first DNA fraction enters the box.
- Record temperature at each village stop.
- Record temperature at lab handover.

If a thermometer/logger is unavailable, record `Temperature_Not_Available` and note ice-pack condition.

## 6. Time Limits

Use lab-specific limits whenever available. Until then, use conservative field flags:

| Condition | Action |
|---|---|
| DNA fraction placed in cool box immediately | Accept |
| Cold-chain start delayed under 30 minutes | Conditional; document reason |
| Cold-chain start delayed over 30 minutes | Conditional or reject after lab review |
| Sample reached lab same day | Accept if label and temperature are acceptable |
| Sample held overnight without validated cold storage | Conditional or reject after lab review |

## 7. Handover Procedure

At laboratory or storage handover:

1. Count containers by fraction.
2. Match sample IDs against inventory.
3. Record receiving person.
4. Record date and time.
5. Record condition of container and label.
6. Record storage location and condition.
7. Mark `Custody_Status=Received`, `Conditional`, or `Rejected`.

## 8. Cold-Chain Deviation Report

Create a deviation note if:

- Cool box warmed unexpectedly.
- Ice packs melted before lab arrival.
- Sample was misplaced.
- Container leaked.
- Label became unreadable.
- Handover was delayed.

Record deviation in:

- `templates/chain_of_custody_template.csv`
- `templates/daily_field_log_template.csv`

## 9. Storage Labels

Each storage container must retain:

- Sample ID.
- Parent composite ID.
- Fraction.
- Date.
- Orchard ID.
- Depth code.
- Storage location.

Do not replace field sample IDs with lab-only IDs unless both IDs are recorded in the chain-of-custody table.

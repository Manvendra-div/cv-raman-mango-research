# Field Visit Schedule

## 1. Schedule Basis

Current date: 2026-06-26.

Because the January-May 2026 sampling windows have already passed, the first complete annual field cycle should be scheduled for 2027. The remainder of 2026 should be used for orchard registry preparation, consent, route planning, label printing, equipment preparation, and a small dry-run visit if needed.

Editable schedule:

- `templates/field_visit_schedule.csv`

## 2. Preparation Period

Recommended preparation window:

```text
2026-07-01 to 2026-12-15
```

Preparation tasks:

1. Build candidate orchard registry.
2. Select Tier A or Tier B sampling design.
3. Confirm consent codes.
4. Verify GPS coordinates.
5. Finalize field team and laboratory contacts.
6. Prepare labels and metadata sheets.
7. Procure sterile containers, sample bags, gloves, cool boxes, ice packs, GPS device, field meter, auger/corer, cleaning materials, and markers.
8. Conduct one dry-run sampling day if possible.

## 3. First Full Annual Cycle: 2027

| Visit | Planned window | Field season | Model season | Crop stage | Core task |
|---|---|---|---|---|---|
| V1 | 2027-01-15 to 2027-02-15 | Winter_PreFlowering | Winter | Pre-flowering and flowering preparation | Baseline winter soil and microbiome profile |
| V2 | 2027-04-15 to 2027-05-15 | PreMonsoon_FruitDevelopment | Pre-monsoon | Fruit setting and development | Pre-monsoon stress and nutrient status |
| V3 | 2027-07-15 to 2027-08-15 | Monsoon_PostHarvest | Post-monsoon | Post-harvest and vegetative growth | Monsoon/post-harvest microbiome shift |
| V4 | 2027-10-15 to 2027-11-15 | PostMonsoon_Dormancy | Post-monsoon | Dormancy preparation | Recovery and next-cycle soil status |

If only three model-compatible seasonal windows are funded, prioritize V1, V2, and V4. If the quarterly plan is funded, include all four visits.

## 4. Per-Visit Sample Counts

### Tier A

```text
12 orchards x 2 depths = 24 core composites per visit
```

With 10 percent QC:

```text
24 core + 3 QC = 27 composites per visit
```

### Tier B

```text
36 orchards x 2 depths = 72 core composites per visit
```

With 10 percent QC:

```text
72 core + 8 QC = 80 composites per visit
```

## 5. Suggested Village Routing

Use village-wise route days to reduce transport time and label confusion.

Suggested Tier B routing:

| Day | Village | Orchards | Core composites |
|---|---|---:|---:|
| Day 1 | Malihabad | 9 | 18 |
| Day 2 | Rahimabad | 9 | 18 |
| Day 3 | Kakori | 9 | 18 |
| Day 4 | Mall | 9 | 18 |
| Day 5 | QC catch-up and missed samples | As needed | As needed |

Tier A can usually be completed in 2-3 field days per visit depending on travel distance and lab handling capacity.

## 6. Visit Readiness Checklist

Before every visit:

- Orchard list finalized.
- Labels printed.
- Metadata sheets loaded or printed.
- Field equipment cleaned.
- Cool boxes and ice packs ready.
- Lab notified of expected sample count.
- Weather forecast checked.
- Replacement orchards confirmed.
- Transport arranged.

## 7. Visit Close-Out Checklist

After every visit:

- Sample IDs reconciled against metadata.
- Conditional or missing samples flagged.
- DNA fractions transferred to cold storage.
- Soil-chemistry fractions handed over or prepared for drying.
- Daily field notes saved.
- Metadata file copied to `data/raw/field_metadata/`.
- Sample count summary updated.

## 8. Annual Schedule Decision

Recommended for Phase 2:

- Use Tier B with V1, V2, and V4 as the minimum real-data cycle.
- Add V3 if budget and lab capacity permit quarterly monitoring.

This produces either:

- 216 core composites/year plus QC for the 3-window Tier B plan.
- 288 core composites/year plus QC for the 4-window Tier C quarterly plan.

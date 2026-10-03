# Initial Real-Sample Dataset

## 1. Purpose

The initial real-sample dataset is the first real-data table created after field collection. It should contain one row per parent composite sample, with field metadata populated and laboratory/microbiome result columns left blank until Phase 4.

Editable CSV template:

- `templates/initial_real_sample_dataset_template.csv`

Completed raw real-sample datasets should be saved in:

- `data/raw/real_sample_dataset/`

## 2. Row Granularity

Use one row per parent composite:

```text
one orchard + one visit + one season + one soil depth + one composite number
```

Example parent composite:

```text
MNG-MLD-O001-20270120-WIN-D1530-C01
```

## 3. Relationship to Physical Fractions

The initial dataset should include physical sample IDs for each fraction:

- `Chem_Sample_ID`
- `SixteenS_Sample_ID`
- `ITS_Sample_ID`
- `Archive_Sample_ID`

This allows Phase 4 lab outputs to be merged back to the parent composite.

## 4. Field Columns Populated in Phase 3

Phase 3 should populate:

- Site and sample metadata.
- Sampling date and season.
- GPS coordinates.
- Mango variety and tree age.
- Management and input history.
- Soil depth and subsampling details.
- Field disease observations.
- Yield history.
- Fraction collection statuses.
- Cold-chain status.

## 5. Lab Columns Reserved for Phase 4

The following should remain blank until measured:

- Soil chemistry: pH, EC, organic carbon, N, P, K, CEC, texture, micronutrients.
- Microbiome diversity: OTU/ASV count, Shannon, Simpson, Chao1, Pielou.
- Taxonomy: bacterial, fungal, and archaeal relative abundance.
- Functional microbial groups.
- Pathogen-load metrics.

## 6. Target Columns

Target columns should be handled carefully:

| Target | Phase 3 status |
|---|---|
| `Mango_Yield` | Use only measured or documented yield history; mark source. |
| `Disease_Risk` | Use field disease-risk label only as provisional until validated. |
| `Nutrient_Availability` | Leave blank until soil testing thresholds are applied. |

## 7. Dataset Status Values

Use `Dataset_Row_Status`:

- `Field_Collected`
- `Field_Conditional`
- `Field_Rejected`
- `Lab_Pending`
- `Ready_For_Phase4`

## 8. Merge Rule for Later Phases

The primary merge key is:

```text
Parent_Composite_ID
```

Do not merge Phase 4 lab results only by orchard, village, date, or depth because duplicate composites and QC samples may exist.

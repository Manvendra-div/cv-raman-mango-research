# Real-Sample Validation Protocol

## Objective

Validate whether the trained pipeline predicts measured orchard outcomes from real soil, microbiome, climate, and management observations.

## Input File

Use:

```text
data/validation/real_sample_validation_input.csv
```

If the file does not exist, Phase 10 creates it from:

```text
data/validation/real_sample_validation_template.csv
```

## Required Observations

Each row should represent one real orchard sample. Fill the model feature columns exactly as named in the template, then add observed targets where available:

| Column | Meaning |
|---|---|
| `Sample_ID` | Unique sample identifier |
| `Orchard_ID` | Orchard identifier |
| selected feature columns | Soil, microbiome, climate, site, and management features used by the model |
| `Observed_Mango_Yield` | Measured yield for the sample or orchard |
| `Observed_Disease_Risk` | Observed disease condition mapped to the model labels |
| `Observed_Nutrient_Availability` | Lab or expert nutrient status mapped to the model labels |
| `Observed_Disease_Notes` | Field notes, symptoms, or assay comments |
| `Measurement_Date` | Date of observation |

## Output

After data is added and Phase 10 is rerun, predictions are written to:

```text
outputs/validation/phase10/phase10_real_sample_predictions.csv
```

The script compares observed and predicted values when observed target columns are populated.

## Failure Documentation

Use `Observed_Disease_Notes` for mismatches caused by sampling date, irrigation stress, cultivar-specific effects, unmeasured pathogens, inconsistent lab methods, or assumptions inherited from synthetic-data generation.

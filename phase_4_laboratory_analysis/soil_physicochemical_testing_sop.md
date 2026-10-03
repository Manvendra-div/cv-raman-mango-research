# Soil Physicochemical Testing SOP

## 1. Objective

Measure soil physicochemical properties required for mango orchard soil-health interpretation, feature engineering, and predictive modeling.

## 2. Input Fraction

Use the Phase 3 `CHEM` fraction for soil chemistry testing.

Required identifiers:

- `Parent_Composite_ID`
- `Chem_Sample_ID`
- `Orchard_ID`
- `Visit_ID`
- `Depth_Code`
- `Sampling_Date`

## 3. Required Soil Tests

| Variable | Unit | Purpose |
|---|---|---|
| `pH` | unitless | Acidity/alkalinity and nutrient availability |
| `EC` | dS/m | Salinity/electrical conductivity |
| `Organic_Carbon` | percent | Soil organic matter status |
| `Total_Nitrogen` | kg/ha | Primary nutrient availability |
| `Available_P` | kg/ha | Available phosphorus |
| `Available_K` | kg/ha | Available potassium |
| `Soil_Moisture` | percent | Field or lab moisture status |
| `Soil_Temperature` | deg C | Field/lab temperature context |
| `Bulk_Density` | g/cm3 | Soil physical condition |
| `CEC` | cmol/kg | Cation exchange capacity |
| `Sand` | percent | Texture fraction |
| `Silt` | percent | Texture fraction |
| `Clay` | percent | Texture fraction |
| `Zn` | ppm | Micronutrient |
| `Fe` | ppm | Micronutrient |
| `Mn` | ppm | Micronutrient |
| `Cu` | ppm | Micronutrient |
| `C_N_Ratio` | ratio | Carbon-to-nitrogen balance |

## 4. Laboratory Workflow

1. Receive CHEM fraction and verify chain-of-custody.
2. Confirm sample label, parent composite ID, and container condition.
3. Air-dry or process according to lab method requirements.
4. Sieve using the lab-specified mesh size.
5. Run required soil tests.
6. Record method name, instrument or kit, analyst, analysis date, and QC status.
7. Flag values outside plausible ranges or method detection limits.
8. Save results using `templates/soil_chemistry_table_template.csv`.

## 5. QC Requirements

Recommended QC:

- Method blank where applicable.
- Laboratory duplicate.
- Certified reference material or standard where available.
- Calibration record for pH, EC, and analytical instruments.
- Texture sum check: sand + silt + clay should be close to 100 percent.
- Negative values must be rejected unless they are valid instrument-coded values documented by the lab.

## 6. Derived Calculations

If both carbon and nitrogen values are available, calculate:

```text
C_N_Ratio = carbon measurement / nitrogen measurement
```

Use a documented conversion if nitrogen is reported in a different unit.

## 7. Acceptance Status

Use `Soil_QC_Status`:

- `Pass`
- `Conditional`
- `Fail`
- `Pending`

Use `Conditional` when a result is usable but has a documented limitation. Use `Fail` when the result should not be merged into the master dataset.

## 8. Output Location

Raw or lab-supplied files:

- `data/raw/lab_soil_tests/`

QC-reviewed interim table:

- `data/interim/soil_qc/`

Output template:

- `templates/soil_chemistry_table_template.csv`

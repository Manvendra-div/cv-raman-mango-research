# Split Strategy

## 1. Objective

Create train, validation, test, and geographic hold-out files that support reproducible model development and external-style validation.

## 2. Geographic Hold-Out

Hold-out village:

```text
Rahimabad
```

Reason:

- The outline identifies Rahimabad as a useful geographic hold-out.
- The current synthetic dataset has 5,059 Rahimabad rows.
- Holding out a village tests whether models generalize beyond random row splitting.

Output:

```text
data/splits/holdout_rahimabad.csv
```

## 3. Internal Split

Rows from Malihabad, Kakori, and Mall are split into:

| Split | Fraction of non-holdout data | Current rows |
|---|---:|---:|
| Train | 70 percent | 10,458 |
| Validation | 15 percent | 2,241 |
| Test | 15 percent | 2,242 |

Stratification:

- `Disease_Risk` is used for stratified splitting where feasible.

Random state:

```text
42
```

## 4. Split Outputs

- `data/splits/train.csv`
- `data/splits/validation.csv`
- `data/splits/test.csv`
- `data/splits/holdout_rahimabad.csv`
- `data/splits/split_membership.csv`

## 5. Leakage Controls

The current implementation:

- Fits encoders and scalers on train only.
- Applies the fitted preprocessing to validation, test, and hold-out.
- Excludes `Sample_ID`, targets, and `Orchard_ID` from the default model-ready feature matrix.
- Keeps `Orchard_ID` in split CSVs for future grouped validation checks.

Future real-data improvement:

- Add orchard-grouped splitting if repeated field samples from the same orchard create leakage risk.

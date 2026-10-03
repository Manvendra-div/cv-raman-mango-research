# Data Splits

Phase 5 train, validation, test, and geographic hold-out splits are stored here.

Current split strategy:

- Rahimabad is held out geographically.
- Remaining villages are split into train, validation, and test sets.
- `Disease_Risk` is used for stratification where feasible.

Files:

- `train.csv`
- `validation.csv`
- `test.csv`
- `holdout_rahimabad.csv`
- `split_membership.csv`

# Field Intervention Validation Protocol

## Objective

Evaluate whether DSS recommendations improve orchard outcomes compared with control orchards.

## Input File

Use:

```text
data/validation/field_intervention_validation_input.csv
```

If the file does not exist, Phase 10 creates it from:

```text
data/validation/field_intervention_validation_template.csv
```

## Recommended Design

Use paired treatment and control orchards when possible. Record baseline measurements before recommendations are applied, then repeat measurements at a defined follow-up interval.

## Required Tracking Fields

| Field | Purpose |
|---|---|
| `Intervention_ID` | Unique intervention record |
| `Orchard_ID` | Orchard identifier |
| `Village` | Village/site context |
| `Treatment_Group` | `Treatment` or `Control` |
| `Recommendation_Rule_ID` | Recommendation source rule when applicable |
| `Recommendation_Applied` | Intervention actually applied |
| `Baseline_*` columns | Pre-intervention soil, disease, and yield status |
| `Followup_*` columns | Post-intervention status |
| `Monitoring_Notes` | Field observations and deviations from plan |

## Output

After field rows are added and Phase 10 is rerun, treatment/control summaries are written to:

```text
outputs/validation/phase10/phase10_field_intervention_summary.csv
```

The summary reports mean changes in soil health, pathogen load, yield, and disease incidence by treatment group.

## Interpretation

A useful intervention pattern should show improved soil health, reduced pathogen load, reduced disease incidence, or improved yield in treatment orchards relative to controls. The comparison should be interpreted with weather, cultivar, irrigation, and management notes.

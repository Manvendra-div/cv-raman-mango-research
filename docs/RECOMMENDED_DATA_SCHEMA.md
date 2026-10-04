# RECOMMENDED DATA SCHEMA
Future fields are **requirements, not observations**. All `required:false`, all nullable, all excluded from current model inputs. No values invented.
See `data/schemas/extended_mango_dataset_schema.json`.
## Why extend
Current 63 cols lack: fertilizer doses/dates, irrigation method/quantity, fungicide history, historical yields (Y1-3), flower/fruit counts, canopy scores, intervention baseline→follow-up pairs. Without these, recommendations cannot be dose-prescriptive and causality cannot be claimed.
## Validation rules
- Units mandatory (kg/ha, L/tree, kg/tree, date ISO-8601).
- Historical yields: 0–200 kg/tree, else reject.
- Canopy_Health_Score 0–10.
- Intervention block requires Sampling_Date + Intervention_Type + Post_Intervention_Yield to enable DiD analysis.
## Migration
When real data arrives: add columns per JSON, keep raw immutable, re-run `src/data/validate_dataset.py`.

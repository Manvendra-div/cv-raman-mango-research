# Minimum Real-World Sample Size Framework

## 1. Purpose

This document defines the minimum real-world sample size for pilot validation and the recommended sample size for later model refinement. It directly addresses the limitation identified in the outline: 12 composite datasets per year is too small for robust ML/XAI model development.

## 2. Sampling Unit Definitions

| Term | Definition |
|---|---|
| Orchard | A selected mango orchard with stable `Orchard_ID`, village, GPS coordinate, management type, productivity history, variety, and tree-age information. |
| Subsample | Soil collected from one tree or sampling point under the canopy drip line. |
| Composite sample | Mixed soil from 5-10 subsamples within one orchard, one depth, one visit window. |
| Depth-specific composite | One composite sample for one depth class, such as 0-15 cm or 15-30 cm. |
| Field duplicate | A second independently collected composite from the same orchard-depth-visit combination, used for QC. |
| Core composite count | The count excluding field duplicates, blanks, and lab QC aliquots. |

## 3. Required Depths and Seasons

Depths:

- 0-15 cm: active topsoil and organic input zone.
- 15-30 cm: rhizosphere/root-activity zone used in the existing real-sample proposal.

Model-compatible seasonal windows:

- Winter
- Pre-monsoon
- Post-monsoon

Optional field schedule window:

- Monsoon/post-harvest may be recorded separately as `Field_Season`, then mapped to model-compatible season rules during preprocessing.

## 4. Tier A: Minimum Pilot-Validation Design

Use this tier when the goal is to validate the synthetic-data prototype with real samples, not to train a final model from scratch.

Design:

- 4 villages.
- 3 orchards per village.
- 12 orchards total.
- 3 productivity histories represented in each village: Low, Medium, High.
- 3 seasonal windows per year.
- 2 soil depths per orchard per visit.
- 1 composite per orchard-depth-visit.
- 5-10 subsamples per composite.
- 10 percent field duplicates or at least 1 duplicate per field day.

Core composite count:

```text
12 orchards x 3 seasons x 2 depths x 1 composite = 72 core composites/year
```

QC estimate:

```text
72 core composites x 10 percent = 8 field duplicates/year after rounding up
```

Total expected field composites:

```text
72 core + 8 QC = 80 composites/year
```

Use Tier A for:

- First real-world validation.
- Testing logistics and lab workflow.
- Comparing synthetic assumptions with real measurements.
- Producing an initial real-sample dataset.

Do not use Tier A as the only basis for final ML model-development claims.

## 5. Tier B: Recommended Model-Refinement Design

Use this tier when the goal is to produce enough real data for model refinement and stronger XAI analysis.

Design:

- 4 villages.
- 9 orchards per village.
- 36 orchards total.
- 3 management types per village: Organic, Conventional, Integrated.
- 3 productivity histories within each village-management group where feasible: Low, Medium, High.
- 3 seasonal windows per year.
- 2 soil depths per orchard per visit.
- 1 composite per orchard-depth-visit.
- 5-10 subsamples per composite.
- 10 percent field duplicates.

Core composite count:

```text
36 orchards x 3 seasons x 2 depths x 1 composite = 216 core composites/year
```

QC estimate:

```text
216 core composites x 10 percent = 22 field duplicates/year after rounding up
```

Total expected field composites:

```text
216 core + 22 QC = 238 composites/year
```

Use Tier B for:

- Model refinement using real data.
- More stable village-wise analysis.
- Stronger disease-risk and nutrient-availability validation.
- XAI explanations that are less dependent on synthetic assumptions.

## 6. Tier C: Optional Quarterly Full-Season Design

Use this tier if the project chooses to keep the quarterly rhythm from the real-sample proposal.

Design:

- 36 orchards.
- 4 field windows per year.
- 2 soil depths.
- 1 composite per orchard-depth-visit.
- 10 percent field duplicates.

Core composite count:

```text
36 orchards x 4 field windows x 2 depths = 288 core composites/year
```

QC estimate:

```text
288 core composites x 10 percent = 29 field duplicates/year after rounding up
```

Total expected field composites:

```text
288 core + 29 QC = 317 composites/year
```

Use Tier C for:

- Capturing monsoon/post-harvest dynamics separately.
- Stronger seasonal microbiome analysis.
- Multi-season DSS validation.

## 7. Enhanced Replicate Option

If budget allows, collect a second independent composite in 25 percent of orchards at each visit. This improves estimation of within-orchard variability without doubling the entire project cost.

For Tier B:

```text
36 orchards x 25 percent = 9 orchards with enhanced duplicate composites per visit
9 orchards x 3 seasons x 2 depths = 54 additional composites/year
```

## 8. Recommended Decision

The recommended Phase 2 decision is Tier B:

- It is much stronger than the original 12-composite annual plan.
- It remains more feasible than a fully replicated, multi-year design.
- It preserves village, management, productivity, season, and depth variation needed for later ML/XAI validation.

## 9. Multi-Year Recommendation

For thesis-level evidence:

- Minimum: 1 full annual cycle using Tier B.
- Stronger: 2 annual cycles using Tier B.
- Best for deployment claims: Tier B or C plus real yield and disease outcome follow-up for at least 2 years.

Two years of Tier B produce:

```text
216 core composites/year x 2 years = 432 core composites
```

Two years of Tier C produce:

```text
288 core composites/year x 2 years = 576 core composites
```

## 10. Sample-Size Summary

| Tier | Orchards | Seasons/windows | Depths | Core composites/year | QC estimate | Total/year | Main use |
|---|---:|---:|---:|---:|---:|---:|---|
| Prior proposal | 3 | 4 | 1 | 12 | Not defined | 12+ | Too small except as a tiny feasibility check |
| Tier A | 12 | 3 | 2 | 72 | 8 | 80 | Pilot validation |
| Tier B | 36 | 3 | 2 | 216 | 22 | 238 | Recommended model refinement |
| Tier C | 36 | 4 | 2 | 288 | 29 | 317 | Full quarterly monitoring |

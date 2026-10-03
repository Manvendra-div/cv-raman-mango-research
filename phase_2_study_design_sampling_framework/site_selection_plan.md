# Site Selection Plan

## 1. Objective

Select representative mango orchards across Malihabad and nearby mango-growing villages so that later soil, microbiome, yield, disease-risk, and nutrient-availability models are not based on a narrow or biased field sample.

## 2. Target Study Region

The Phase 2 study area follows the current research outline and synthetic dataset coverage:

| Village | Code | Role in design |
|---|---|---|
| Malihabad | MLD | Core study location and primary mango belt signal |
| Rahimabad | RHB | Geographic generalization and future hold-out candidate |
| Kakori | KKR | Nearby mango-growing comparison area |
| Mall | MLL | Nearby mango-growing comparison area |

Additional villages may be added only if they are documented in the orchard registry and assigned stable village codes.

## 3. Selection Principles

1. Cover the known mango-growing geography rather than sampling only the easiest orchards.
2. Balance productivity history, management type, soil type, tree age, and variety.
3. Preserve village identity so one village can be held out during later geographic validation.
4. Avoid repeated sampling from only one owner, one soil condition, or one management practice.
5. Use permanent orchard IDs and GPS coordinates so samples can be revisited across seasons.

## 4. Candidate Orchard Registry

Before final selection, create a registry of at least 50 candidate orchards. This matches the synthetic dataset's 50-orchard structure and gives replacements if orchards become inaccessible.

Required registry fields are provided in:

- `templates/orchard_registry_template.csv`

Minimum screening fields:

- Village
- GPS coordinates
- Orchard area
- Mango variety
- Dominant tree age
- Management type
- Productivity history
- Soil type or texture class
- Irrigation type
- Disease history
- Farmer or manager consent code
- Accessibility during all planned seasons

## 5. Inclusion Criteria

An orchard is eligible if it meets all of the following:

1. Located in one of the selected villages or approved nearby mango-growing sites.
2. Has mango trees with known or estimable age.
3. Has a stable management history for at least the most recent season.
4. Can provide yield history or productivity category.
5. Allows GPS recording and repeated seasonal visits.
6. Allows soil sampling under the canopy drip line.
7. Provides farmer or manager consent through a coded consent record.

## 6. Exclusion Criteria

Exclude orchards if:

1. Major land disturbance, excavation, or soil filling occurred in the last 6 months.
2. The orchard was recently converted from non-orchard land and lacks stable mango production history.
3. Chemical spill, flooding, sewage contamination, or construction contamination is suspected.
4. Access cannot be guaranteed across planned sampling windows.
5. Orchard identity, management history, or consent cannot be documented.

## 7. Stratification Variables

| Stratification axis | Classes to capture | Notes |
|---|---|---|
| Village | MLD, RHB, KKR, MLL | Keep village identity for geographic validation. |
| Productivity history | Low, Medium, High | Use measured kg/tree if available; otherwise use farmer records and local expert classification. |
| Management type | Organic, Conventional, Integrated | Match current dataset categories. |
| Soil type or texture | Sandy loam, loam, clay loam, silty/clayey alluvial, local class | Record local name and later map to measured sand/silt/clay. |
| Tree age | Young, Mature, Old | Suggested classes: 5-10 years, 11-30 years, over 30 years. |
| Variety | Dashehari/Dusseheri, Langra, Chausa, Safeda, other | Standardize spelling during metadata cleaning. |
| Disease status | No visible symptoms, mild, moderate, severe | Field disease scoring supports future disease-risk labels. |

## 8. Productivity History Classification

Use measured yield if available. If measured yield is not available, use farmer records, local extension knowledge, and tree condition as provisional classification.

| Class | Provisional definition |
|---|---|
| Low | Lower third of local yield history, or approximately below 15 kg/tree when using the synthetic prototype scale. |
| Medium | Middle third of local yield history, or approximately 15-20 kg/tree when using the synthetic prototype scale. |
| High | Upper third of local yield history, or approximately above 20 kg/tree when using the synthetic prototype scale. |

The kg/tree thresholds are only provisional. Real thresholds should be recalculated after field yield records are collected.

## 9. Orchard Selection Matrix

### Minimum Pilot-Validation Design

Select 12 orchards:

| Village | Low productivity | Medium productivity | High productivity | Village total |
|---|---:|---:|---:|---:|
| Malihabad | 1 | 1 | 1 | 3 |
| Rahimabad | 1 | 1 | 1 | 3 |
| Kakori | 1 | 1 | 1 | 3 |
| Mall | 1 | 1 | 1 | 3 |
| Total | 4 | 4 | 4 | 12 |

Management types should be balanced across the 12 orchards:

- 4 organic or low-chemical orchards where available.
- 4 conventional orchards.
- 4 integrated-management orchards.

If perfect management balance is impossible, document the reason and select the closest available replacement.

### Recommended Model-Refinement Design

Select 36 orchards:

| Village | Organic | Conventional | Integrated | Village total |
|---|---:|---:|---:|---:|
| Malihabad | 3 | 3 | 3 | 9 |
| Rahimabad | 3 | 3 | 3 | 9 |
| Kakori | 3 | 3 | 3 | 9 |
| Mall | 3 | 3 | 3 | 9 |
| Total | 12 | 12 | 12 | 36 |

Within each village-management group, choose one low-productivity, one medium-productivity, and one high-productivity orchard where feasible.

## 10. Variety and Tree-Age Quotas

For the 36-orchard design:

- At least 50 percent of orchards should be Dashehari/Dusseheri if field reality supports this.
- Include Langra, Chausa, Safeda, or other varieties where present so variety effects can be examined.
- Each village should include at least one young, one mature, and one old orchard when feasible.
- If a village is strongly dominated by one age or variety class, record that as a site characteristic instead of forcing artificial balance.

## 11. Spatial Separation Rule

Where feasible:

- Avoid selecting orchards that are immediately adjacent unless they intentionally represent different management or disease conditions.
- Record GPS coordinates at orchard center and sampling zone.
- Maintain a replacement orchard list for each village and stratum.

## 12. Replacement Rule

If a selected orchard becomes unavailable:

1. Replace from the same village, management type, and productivity class.
2. If unavailable, keep the same village and productivity class, then match management as closely as possible.
3. If still unavailable, document the deviation in the orchard registry and field report.

## 13. Final Site Selection Outputs

By the end of Phase 2, the team should have:

- A filled orchard registry.
- 12 minimum pilot orchards or 36 recommended model-refinement orchards.
- Replacement orchard list.
- Consent code for each orchard.
- GPS points checked.
- Stratum coverage table.
- Field visit route grouping by village.

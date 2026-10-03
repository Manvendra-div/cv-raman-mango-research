# Microbial Abundance Table

## 1. Purpose

The microbial abundance output stores ASV/OTU-level counts and sample-level relative abundance summaries from 16S and ITS sequencing. These tables support diversity analysis, taxonomic feature engineering, pathogen-load calculation, and model input construction.

## 2. Output Tables

### Feature-Level Abundance Table

Template:

- `templates/asv_abundance_table_template.csv`

Use this as the detailed long-format microbiome table.

Row granularity:

```text
one parent composite + one sequencing target + one feature/ASV/OTU
```

### Sample-Level Wide Taxa Abundance Table

Template:

- `templates/sample_taxa_abundance_wide_template.csv`

Use this as the model-ready taxonomic abundance summary aligned with the synthetic dataset schema.

Row granularity:

```text
one parent composite
```

## 3. Required Merge Keys

Both tables must include:

- `Parent_Composite_ID`
- `Sequencing_Target`
- `Run_ID`
- `Bioinformatics_Run_ID`

For feature-level tables, also include:

- `Feature_ID`

## 4. Relative Abundance Rules

Relative abundance values:

- Must be numeric.
- Must be non-negative.
- Should be expressed as percent in the wide table.
- Should document normalization method.

Do not force bacterial, fungal, and archaeal groups to sum to 100 together unless the sequencing design supports that interpretation. Keep target/domain normalization documented.

## 5. Output Locations

Feature-level table:

- `data/interim/otu_or_asv_tables/`

Wide abundance table:

- `data/interim/microbial_abundance/`

## 6. QC Checks

Before accepting abundance outputs:

- Confirm no negative values.
- Confirm feature IDs match the taxonomic assignment table.
- Confirm sample IDs match sequencing manifest.
- Confirm blank/control samples were reviewed.
- Flag low-read samples as `Conditional` if retained.

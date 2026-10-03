# Taxonomic Table

## 1. Purpose

The taxonomic table stores feature-level taxonomic assignments for 16S and ITS ASV/OTU features. It links microbiome features to bacterial, archaeal, and fungal groups used in the project.

Editable CSV template:

- `templates/taxonomic_assignment_table_template.csv`

Recommended output location:

- `data/interim/taxonomy_tables/`

## 2. Row Granularity

Use one row per feature ID per sequencing target.

Required key:

```text
Sequencing_Target + Feature_ID
```

## 3. Required Taxonomy Fields

Record:

- Full taxonomy string.
- Kingdom.
- Phylum.
- Class.
- Order.
- Family.
- Genus.
- Species if available.
- Confidence score if available.
- Reference database.
- Reference database version.

## 4. Target-Specific Databases

| Sequencing target | Recommended database |
|---|---|
| 16S | SILVA or documented equivalent |
| ITS | UNITE or documented equivalent |

## 5. Broad Group Mapping

The table supports downstream mapping to:

- Proteobacteria
- Actinobacteria
- Acidobacteria
- Firmicutes
- Bacteroidetes
- Ascomycota
- Basidiomycota
- Glomeromycota
- Mortierellomycota
- Zygomycota
- Thaumarchaeota
- Euryarchaeota

If taxonomy updates use different names for older groups, record the original classifier output and document mapping rules in Phase 5/6.

## 6. QC Rules

Flag taxonomy as `Conditional` if:

- Confidence is below lab-defined threshold.
- Feature is unclassified below high taxonomic rank.
- Reference database version is missing.

Flag as `Fail` if:

- Feature ID does not exist in abundance table.
- Target/database mismatch occurs, such as ITS classified using 16S database.

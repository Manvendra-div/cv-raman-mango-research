# DNA Extraction and Sequencing Plan

## 1. Objective

Extract microbial DNA from Phase 3 biological fractions and define sequencing targets clearly for bacterial, archaeal, and fungal microbiome profiling.

## 2. Input Fractions

| Fraction | Intended target |
|---|---|
| `16S` | Bacterial and archaeal 16S rRNA amplicon profiling |
| `ITS` | Fungal ITS amplicon profiling |
| `ARCH` | Backup only unless re-analysis is required |

## 3. Required Sequencing Targets

The project locks the following Phase 4 target decision:

| Domain | Target | Output |
|---|---|---|
| Bacteria and archaea | 16S rRNA | Bacterial/archaeal ASV or OTU table and taxonomy |
| Fungi | ITS | Fungal ASV or OTU table and taxonomy |

If the sequencing provider uses specific primer regions, record them in the DNA extraction log and sequencing manifest.

## 4. DNA Extraction Workflow

1. Verify DNA fraction against chain-of-custody.
2. Record sample receipt condition and storage condition.
3. Homogenize biological soil fraction according to extraction kit or lab SOP.
4. Extract DNA using the approved soil DNA extraction protocol.
5. Record extraction batch ID.
6. Measure DNA concentration and purity.
7. Store extracted DNA under documented conditions.
8. Prepare 16S and ITS libraries according to sequencing provider requirements.

## 5. DNA QC Fields

Record:

- `DNA_Concentration_ng_per_uL`
- `A260_280`
- `A260_230`
- `Extraction_Blank_ID`
- `Extraction_Batch_ID`
- `DNA_QC_Status`
- `DNA_QC_Notes`

## 6. DNA QC Status

Use:

- `Pass`
- `Conditional`
- `Fail`
- `Pending`

Examples:

| Condition | Status |
|---|---|
| Good concentration and purity, no blank contamination | Pass |
| Low concentration but still accepted by sequencing facility | Conditional |
| Blank contamination suspected | Conditional or Fail |
| Sample failed library prep | Fail |

## 7. Output Files

DNA extraction log:

- `templates/dna_extraction_log_template.csv`
- `data/interim/dna_extraction/`

Sequencing manifests:

- `templates/sequencing_manifest_16s_template.csv`
- `templates/sequencing_manifest_its_template.csv`
- `data/interim/sequencing_manifests/`

Raw reads:

- `data/raw/sequencing_reads/16S/`
- `data/raw/sequencing_reads/ITS/`

## 8. Required Merge Keys

Every DNA and sequencing record must include:

- `Parent_Composite_ID`
- `DNA_Sample_ID`
- `Sequencing_Target`
- `Run_ID`
- `Library_ID`

Do not rely only on sequencing-provider sample names.

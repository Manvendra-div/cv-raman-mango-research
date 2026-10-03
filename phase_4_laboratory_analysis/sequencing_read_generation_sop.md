# Sequencing Read Generation SOP

## 1. Objective

Generate or receive sequencing reads for 16S rRNA and ITS amplicon targets while preserving traceability from field sample to raw read file.

## 2. Input

DNA extracts produced from:

- 16S fraction for bacteria/archaea.
- ITS fraction for fungi.

## 3. Required Read File Metadata

Each read file must be traceable with:

- `Parent_Composite_ID`
- `DNA_Sample_ID`
- `Library_ID`
- `Run_ID`
- `Sequencing_Target`
- `Forward_Read_File`
- `Reverse_Read_File`
- `Barcode_or_Index`
- `Sequencing_Platform`
- `Sequencing_Facility`

## 4. Read File Storage

Store raw read files without editing:

```text
data/raw/sequencing_reads/16S/
data/raw/sequencing_reads/ITS/
```

Do not rename provider files unless a mapping file is preserved.

## 5. Manifest Files

Create sequencing manifest files before importing reads into a bioinformatics workflow:

- `templates/sequencing_manifest_16s_template.csv`
- `templates/sequencing_manifest_its_template.csv`

Recommended interim location:

- `data/interim/sequencing_manifests/`

## 6. Sequencing QC Checks

At minimum, report:

- Total reads per sample.
- Forward and reverse read file presence.
- Read quality summary.
- Primer trimming status.
- Denoising status.
- Non-chimeric reads.
- Feature count after denoising or clustering.
- Taxonomic assignment status.

Use:

- `templates/sequencing_qc_summary_template.csv`

## 7. Read Acceptance Status

Use `Read_QC_Status`:

- `Pass`
- `Conditional`
- `Fail`
- `Pending`

Typical flags:

- Missing reverse read.
- Very low reads.
- Poor quality.
- High chimera rate.
- Unexpected blank contamination.
- Sample index mismatch.

## 8. Handover to Bioinformatics

Before running the pipeline:

1. Confirm each sample appears in the manifest.
2. Confirm read file paths exist.
3. Confirm sample IDs match Phase 3 and DNA extraction logs.
4. Confirm blanks and controls are included.
5. Save manifest and read QC summary.

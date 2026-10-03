# Bioinformatics Pipeline

## 1. Objective

Process 16S rRNA and ITS sequencing reads into ASV or OTU abundance tables, taxonomic assignments, diversity-index tables, and microbiome QC summaries.

## 2. Input Files

| Input | Location |
|---|---|
| 16S raw reads | `data/raw/sequencing_reads/16S/` |
| ITS raw reads | `data/raw/sequencing_reads/ITS/` |
| 16S manifest | `data/interim/sequencing_manifests/` |
| ITS manifest | `data/interim/sequencing_manifests/` |
| DNA extraction log | `data/interim/dna_extraction/` |
| Field metadata | `data/raw/field_metadata/` |

## 3. Recommended Tooling

Use a reproducible microbiome workflow such as QIIME 2 with DADA2 or an equivalent documented workflow.

Locked Phase 4 decisions from Phase 1:

- 16S rRNA for bacteria and archaea.
- ITS for fungi.
- SILVA or documented equivalent for 16S taxonomy.
- UNITE or documented equivalent for ITS taxonomy.
- ASV generation preferred where read quality and method allow.

## 4. Pipeline Overview

```text
raw reads
  -> manifest validation
  -> import reads
  -> demultiplex/quality summary
  -> primer/adaptor trimming
  -> denoising or OTU clustering
  -> chimera removal
  -> feature table generation
  -> representative sequences
  -> taxonomy assignment
  -> abundance normalization/export
  -> alpha diversity calculation
  -> QC summary
```

## 5. 16S Pipeline Skeleton

The exact commands depend on installed QIIME 2 version, read layout, and primer design. Keep command logs with the run.

Example command skeleton:

```text
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path data/interim/sequencing_manifests/manifest_16s.csv \
  --output-path data/interim/microbiome_qc/16s_demux.qza \
  --input-format PairedEndFastqManifestPhred33V2

qiime demux summarize \
  --i-data data/interim/microbiome_qc/16s_demux.qza \
  --o-visualization data/interim/microbiome_qc/16s_demux.qzv

qiime dada2 denoise-paired \
  --i-demultiplexed-seqs data/interim/microbiome_qc/16s_demux.qza \
  --p-trunc-len-f 0 \
  --p-trunc-len-r 0 \
  --o-table data/interim/otu_or_asv_tables/16s_feature_table.qza \
  --o-representative-sequences data/interim/otu_or_asv_tables/16s_rep_seqs.qza \
  --o-denoising-stats data/interim/microbiome_qc/16s_denoising_stats.qza
```

Taxonomy assignment skeleton:

```text
qiime feature-classifier classify-sklearn \
  --i-classifier reference_databases/silva_16s_classifier.qza \
  --i-reads data/interim/otu_or_asv_tables/16s_rep_seqs.qza \
  --o-classification data/interim/taxonomy_tables/16s_taxonomy.qza
```

## 6. ITS Pipeline Skeleton

ITS reads may require ITS-specific trimming and classifier choices. Record primer and region details.

Example command skeleton:

```text
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path data/interim/sequencing_manifests/manifest_its.csv \
  --output-path data/interim/microbiome_qc/its_demux.qza \
  --input-format PairedEndFastqManifestPhred33V2

qiime demux summarize \
  --i-data data/interim/microbiome_qc/its_demux.qza \
  --o-visualization data/interim/microbiome_qc/its_demux.qzv

qiime dada2 denoise-paired \
  --i-demultiplexed-seqs data/interim/microbiome_qc/its_demux.qza \
  --p-trunc-len-f 0 \
  --p-trunc-len-r 0 \
  --o-table data/interim/otu_or_asv_tables/its_feature_table.qza \
  --o-representative-sequences data/interim/otu_or_asv_tables/its_rep_seqs.qza \
  --o-denoising-stats data/interim/microbiome_qc/its_denoising_stats.qza
```

Taxonomy assignment skeleton:

```text
qiime feature-classifier classify-sklearn \
  --i-classifier reference_databases/unite_its_classifier.qza \
  --i-reads data/interim/otu_or_asv_tables/its_rep_seqs.qza \
  --o-classification data/interim/taxonomy_tables/its_taxonomy.qza
```

## 7. Diversity Indices

Generate sample-level alpha diversity:

- Observed features or ASV/OTU count.
- Shannon index.
- Simpson index.
- Chao1 richness if supported by workflow.
- Pielou evenness.

Output:

- `templates/diversity_index_table_template.csv`
- `data/interim/diversity_indices/`

## 8. Abundance Outputs

Generate:

1. Feature-level abundance table:
   - `templates/asv_abundance_table_template.csv`
2. Sample-level wide taxonomic abundance table matching model columns:
   - `templates/sample_taxa_abundance_wide_template.csv`

The wide table should include the taxonomic groups already present in the synthetic dataset:

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

## 9. Taxonomic Assignment Outputs

Generate feature-level taxonomy:

- Feature or ASV ID.
- Sequencing target.
- Full taxonomy string.
- Rank fields.
- Confidence score where available.
- Reference database and version.

Use:

- `templates/taxonomic_assignment_table_template.csv`

## 10. QC Gates

Before outputs are accepted:

| Gate | Requirement |
|---|---|
| Manifest check | Every raw read sample maps to known `Parent_Composite_ID`. |
| Blank check | Extraction and sequencing blanks reviewed. |
| Read count check | Low-read samples flagged. |
| Denoising check | Non-chimeric read retention reviewed. |
| Taxonomy check | Classifier/database recorded. |
| Negative abundance check | Relative abundance values must be non-negative. |
| Merge check | Sample IDs can merge to Phase 3 initial dataset. |

## 11. Output Locations

| Output type | Location |
|---|---|
| Microbiome QC | `data/interim/microbiome_qc/` |
| ASV/OTU tables | `data/interim/otu_or_asv_tables/` |
| Taxonomy tables | `data/interim/taxonomy_tables/` |
| Diversity indices | `data/interim/diversity_indices/` |
| Microbial abundance | `data/interim/microbial_abundance/` |
| QC reports | `outputs/reports/phase4_lab_analysis/` |

## 12. Reproducibility Requirements

Record:

- Bioinformatics tool and version.
- Command log.
- Manifest file used.
- Primer/target information.
- Denoising/trimming parameters.
- Reference database name and version.
- Date processed.
- Analyst.
- Output file checksums if available.

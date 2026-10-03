# Quality-Control Report

## 1. Purpose

The Phase 4 quality-control report summarizes laboratory and bioinformatics quality checks before data move into Phase 5 integration and preprocessing.

Templates:

- `templates/lab_qc_report_template.csv`
- `templates/sequencing_qc_summary_template.csv`

Recommended report location:

- `outputs/reports/phase4_lab_analysis/`

## 2. QC Scope

QC covers:

- Soil chemistry.
- Chain-of-custody.
- DNA extraction.
- Sequencing reads.
- Bioinformatics processing.
- ASV/OTU abundance.
- Taxonomy.
- Diversity indices.

## 3. Sample-Level QC Status

Use the same status vocabulary wherever possible:

- `Pass`
- `Conditional`
- `Fail`
- `Pending`

## 4. Required QC Questions

| QC area | Question |
|---|---|
| Custody | Did sample ID, label, and custody records reconcile? |
| Chemistry | Did soil-test duplicates, standards, and plausible ranges pass? |
| DNA | Did concentration, purity, and blank checks pass? |
| Reads | Are paired read files present and sufficient? |
| Denoising | Were enough non-chimeric reads retained? |
| Taxonomy | Was the correct database used for the target? |
| Diversity | Were diversity metrics generated from accepted feature tables? |
| Merge readiness | Can all accepted rows merge by `Parent_Composite_ID`? |

## 5. Phase 5 Blocking Conditions

Do not move a sample into Phase 5 as accepted if:

- `Parent_Composite_ID` is missing.
- Custody status is rejected.
- Chemistry sample failed and no valid re-run exists.
- DNA sample failed and sequencing is unavailable.
- Sequencing target/database mismatch is unresolved.
- Abundance values include negative numbers.
- Taxonomy table cannot be joined to abundance features.

Conditional samples may move forward only with a clear flag and reason.

## 6. Final Phase 4 Sign-Off

The QC report should include:

- Analyst name.
- Review date.
- Number of accepted, conditional, failed, and pending samples.
- List of samples needing re-run.
- Notes for Phase 5 preprocessing.

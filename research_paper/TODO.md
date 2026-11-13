# To-do — LNCS paper (`mango_dss_paper.tex`)

Status as of Wed Nov 04 2026. File lives in `research_paper/`.
Work is section-by-section; no commit/push without authorization.

## Done
- [x] Template alignment against `bookchapter.tex` (Springer LNCS):
  - Class and geometry: `\documentclass[runningheads,a4paper]{llncs}` verified.
  - Front matter: Title, running heads, `\toctitle`, `\tocauthor`, `\maketitle`.
  - Abstract word count: 139 words (strictly meets 70–150 word limit).
  - Heading capitalization: All 26 subsection headings converted to Title Case per LNCS rules.
  - Citations: All 5 bibliography entries cited via in-text `\cite{...}` commands.
  - Margin hygiene: Zero overfull/underfull `\hbox`es; Table 4 and paths formatted to fit 122 mm text width.
  - Declarations: Formatted as unnumbered `\subsubsection*{Declarations}` with `\paragraph{}` blocks.
  - PDF compilation: Clean 14-page compilation verified via `pdflatex`.
- [x] Section 1 — Introduction (Background, Problem statement, Research gap, Objectives, Research questions)
- [x] Section 2 — Materials and Methods (all subsections; paths and formulas verified)
- [x] Section 3 — Results (all 10 figures linked and verified, tables formatted)
- [x] Section 4 — Discussion (8 subsections per outline)
- [x] Section 5 — Limitations (epistemic guardrails on synthetic data and causality)
- [x] Section 6 — Future Work
- [x] Section 7 — Conclusion
- [x] Declarations subsections (Data availability, Code availability, Funding, Conflict of interest, Ethics, Author contributions)
- [x] Bibliography — 5 verified entries with hyperlinked URLs

## Needs author action
- [ ] **Author names and affiliations** (Currently placeholder "Research Team", CV Raman Research Work)
  - Insert actual author names, institutional affiliations, postal addresses, and contact emails.
- [ ] **Author contributions** (Declarations, currently standard CRediT taxonomy summary)
  - Adjust per specific journal/volume taxonomy if needed.
- [ ] **Funding** (Declarations, currently institutional grant statement)
  - Insert verified grant numbers or specific funding body if applicable.
- [ ] **Conflict of interest** (Declarations, currently "The authors declare no competing financial interests")
  - Confirm with all co-authors.
- [ ] **Repository commit identifier** (Section 2 Software)
  - Record the final release tag or commit hash upon manuscript freeze.
- [ ] **Metric consistency** — verified against frozen artifacts:
  - Yield geographic RMSE: 1.984 kg/tree, MAE 1.594, R² ≈ 0.273 (Linear Regression)
  - Disease macro-F1 geo: 0.990 (Gradient Boosting)
  - Nutrient macro-F1 geo: 0.9998 (Random Forest)
- [ ] **Real-field status** — keep honest: synthetic dataset, prototype decision support framework, no real-sample validation, no field-intervention data, no causal claims.

## Rules to keep
- Never fabricate metrics, real field data, causal claims, or model artifacts; synthetic ≠ real
- Geographic hold-out must not leak; feature selection/preprocessing inside training folds only
- No fertilizer doses from SHAP; no invented local thresholds
- XAI documents baseline, ± contributions, limitations; no hard-coded feature rankings
- Final comparison document: no code, no branch talk, easy journal language
- Do not overwrite/delete useful existing work; no commits/pushes without authorization

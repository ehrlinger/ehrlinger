# John Ehrlinger, PhD

**Assistant Staff, Lead Data Scientist** · Cardiovascular Outcomes, Registries and Research (CORR)
Heart, Vascular & Thoracic Institute · Cleveland Clinic
**Clinical Assistant Professor** (Joint Appointment) · Cleveland Clinic Lerner College of Medicine

I develop statistical methods and machine learning tools for cardiovascular outcomes research — with a focus on survival analysis, longitudinal data, and reproducible clinical workflows.

📄 [CV (PDF)](https://ehrlinger.github.io/CV/JohnEhrlinger-CV.pdf) &nbsp;|&nbsp; 📝 [CV (Web)](https://github.com/ehrlinger/CV/blob/gh-pages/JohnEhrlinger-CV.md) &nbsp;|&nbsp; 🔗 [LinkedIn](https://linkedin.com/in/ehrlinger) &nbsp;|&nbsp; 📘 [ORCID](https://orcid.org/0000-0002-5340-5154)

---

## Open-Source Software

<!-- BEGIN:packages -->
| Package | Description |
|---|---|
| [ggRandomForests](https://github.com/ehrlinger/ggRandomForests) | Visual exploration of random forest models — graphical analysis of survival, regression, and classification forests — [on CRAN](https://CRAN.R-project.org/package=ggRandomForests) |
| [TemporalHazard](https://github.com/ehrlinger/temporal_hazard) | R port of the C computational core underlying the Cleveland Clinic Hazard SAS module — [on CRAN](https://CRAN.R-project.org/package=TemporalHazard) |
| [hazard](https://github.com/ehrlinger/hazard) | SAS and C implementation of multi-phase hazard analysis for time-to-event decomposition. (Maintainer) |
| [HVTI Recipes](https://ehrlinger.github.io/hvti_graphics/) | Catalog of publication-ready figures, tables, and datasets for clinical outcomes research — Kaplan-Meier, propensity balance, CONSORT, random-forest visualizations — each paired with reproducible code. (Quarto book, CC BY 4.0) |

### The HVTI R package family

[`hvtiR`](https://github.com/ehrlinger/hvtiR) — a one-command installer, version status
table, and environment diagnostic — resolves the family from public GitHub repositories
and version-checks it as a unit: eleven member packages, the nine below plus
`ggRandomForests` and `TemporalHazard` above.

| Package | Description |
|---|---|
| [hvtiBoostmtree](https://github.com/ehrlinger/hvtiBoostmtree) | Boosted multivariate trees for longitudinal data; an extended fork of boostmtree. |
| [hvtiPlotR](https://github.com/ehrlinger/hvtiPlotR) | HVTI-standard publication graphics for reproducible clinical research figures. |
| [hvtiRbootstrap](https://github.com/ehrlinger/hvtiRbootstrap) | Bootstrap model building — fit across many replicates and report how often each variable survives selection; an R port of the bootreg, SUMBOOT and cluster SAS macros. (in active development) |
| [hvtiRdatasets](https://github.com/ehrlinger/hvtiRdatasets) | Analysis-ready clinical datasets for HVTI CORR studies, verified against the legacy SAS datasets they replace. (in active development) |
| [hvtiRlifetables](https://github.com/ehrlinger/hvtiRlifetables) | Age-, sex- and race-matched US reference survival; replaces the usmatchd SAS macro by evaluating a stored three-phase parametric hazard fit rather than interpolating a life table. (in active development) |
| [hvtiRpropensity](https://github.com/ehrlinger/hvtiPropensityScores) | Propensity score estimation, matching and IPTW with standardized balance diagnostics, for cardiac surgery comparative-effectiveness research. (in active development) |
| [hvtiRtables](https://github.com/ehrlinger/hvtiRtables) | Manuscript-compliant Word tables from gtsummary objects, following HVTI CORR table construction standards, with a JTCVS submission mode. |
| [hvtiRtemplates](https://github.com/ehrlinger/hvtiRtemplates) | Versioned analysis job templates and the analysis-prefix taxonomy the CORR group organizes jobs by, so a study binds to a versioned template rather than to a copy. |
| [hvtiRutilities](https://github.com/ehrlinger/hvtiRutilities) | Utility functions supporting reproducible HVTI research workflows. |
<!-- END:packages -->

---

## Research Interests

Applied statistical machine learning research conducted in close collaboration with cardiovascular surgeons and clinicians. Methodological focus spans random forest and ensemble methods, clustering, deep learning, and time series analysis, with emphasis on time-to-event and longitudinal data in cardiovascular outcomes. A sustained focus is the translation of methodological advances into clinical practice through open-source software development and reproducible analytical workflows, with current work centered on open-source implementations of multi-phase hazard analysis methods.

---

*PhD Statistics, Case Western Reserve University (2011)*
*Dissertation: Regularization: Stagewise Regression and Bagging · Advisor: Hemant Ishwaran*

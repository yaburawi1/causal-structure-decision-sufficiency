# When Is Causal Structure Enough?

Reproducibility materials for the manuscript:

**When Is Causal Structure Enough? Decision Sufficiency of Binary Structural Evidence in Educational AI**

**Authors**  
Yousef Abdurahman Aburawi — Internet Computing Department, Faculty of Information Technology, Misurata University, Misurata, Libya  
Mohamed Ahmed Sullabi — Computer Science Department, Faculty of Information Technology, Misurata University, Misurata, Libya

## Purpose

This repository is the paper-specific reproducibility package. It is intentionally separated from the wider LENS-C PhD project and contains only material needed to understand, audit, and reproduce the analyses reported in this manuscript.

The paper studies a narrow decision-oriented question: **when can binary structural causal evidence, used by itself, support a pairwise intervention choice?** It distinguishes structural evidence from intervention-specific effect evidence and evaluates both under explicit policy and synthetic-ground-truth boundaries.

## Scientific scope

The repository follows these boundaries:

- Representation is not prerequisite dependency.
- Structural evidence is not intervention-effect evidence.
- Intervention-effect evidence is not a decision by itself.
- Synthetic ground truth validates only within the corresponding benchmark or data-generating process.
- The study does not claim real-world educational causal truth.

## Repository structure

```text
configs/         Frozen or publication-facing experiment configuration
src/             Minimal code required for paper reproduction
notebooks/       Clean reproduction notebooks, where retained
results/         Canonical tables and machine-readable reported outputs
figures/         Reproducible figure assets or generation instructions
data/            Data provenance and acquisition instructions; no private data
supplementary/   Supplementary material and supporting diagnostics
```

Directories are populated only with paper-relevant artifacts. Development scratch files, unrelated LENS-C stages, private institutional data, and personal data are intentionally excluded.

## Data

The primary analysis uses the publicly released **NeurIPS 2022 Causal Insights for Learning Paths in Education** benchmark. External validation uses author-generated synthetic dynamic causal environments.

This repository will not redistribute third-party benchmark data unless its license explicitly permits redistribution. Where redistribution is inappropriate, `data/README.md` will provide provenance and acquisition instructions instead.

## Reproducibility status

This repository is being prepared as the archival companion to the manuscript. Canonical analysis artifacts and the minimal reproduction path will be added before journal submission is finalized.

The intended reproduction principle is **one canonical path per reported analysis**, with fixed configuration and no post-hoc retuning hidden from the reader.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). The final journal citation and DOI will be added after publication.

## Correspondence

Yousef Abdurahman Aburawi  
Faculty of Information Technology, Misurata University  
Email: yaburawi@it.misuratau.edu.ly

## License

A repository license will be added after the authors confirm the licensing choice for code and author-generated materials. Third-party data remain subject to their original licenses.

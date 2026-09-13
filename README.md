# When Is Causal Structure Enough? Decision Sufficiency of Binary Structural Indicators for Pairwise Intervention Choice in Educational AI

**Authors:** Yousef Abdurahman Aburawi and Mohamed Ahmed Sullabi

This repository provides the frozen protocols, publication code, synthetic
data, canonical results, figures, and supplementary table for the paper. It
supports audit and reproduction of the reported distinction between binary
structural indicators, intervention-specific effects, and intervention
decisions.

The scientific boundary is narrow: results concern the tested synthetic
benchmark and external synthetic data-generating processes. They do not claim
real-world educational causal validity, and structural indicators are not
treated as interchangeable with effect evidence or action selection. Binary
refers to the presence or absence of a structural relation for each
candidate–outcome pair. The present study evaluates pairwise intervention
choice; it does not assume that intervention spaces are generally limited to
two actions. Multi-action intervention choice is outside the current empirical
scope, and no multi-action experiment is claimed.

## Repository structure

- `configs/`: frozen paper protocols and implementation specification.
- `data/`: acquisition and local-placement instructions for third-party data.
- `figures/`: the three manuscript figures.
- `notebooks/`: publication notebooks for the decision analysis and external
  synthetic validation.
- `results/`: canonical inputs, predictions, ground truth, and reported
  diagnostics.
- `src/`: audit and deterministic reproduction commands.
- `supplementary/`: machine-readable Supplementary Table S1 and its notes.

`MANIFEST.csv` inventories every public file except itself. Its hashes cover
the final publication files and intentionally avoid recursive self-reference.

## Data acquisition

The repository does not redistribute the NeurIPS 2022 CausalML Challenge,
“Causal Insights for Learning Paths in Education,” or any other third-party
archive. Obtain the official public data and keep it locally. Exact identifiers,
required archive members, and expected placement are documented in
`data/README.md`.

## Installation

Python 3.11 is required. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Minimal reproduction workflow

1. Obtain the public benchmark archives described in `data/README.md`.

2. Audit all archived reported values:

   ```bash
   python src/audit_reported_results.py
   ```

3. Reproduce the structural bootstrap and paired comparison:

   ```bash
   python src/reproduce_structural_bootstrap.py
   ```

4. Reproduce Method-D sensitivity from the official Task-1 archive:

   ```bash
   python src/reproduce_method_d_sensitivity.py \
     --task1-zip /path/to/Task_1_local_public.zip
   ```

5. Reproduce the secondary Pooled Ridge comparison:

   ```bash
   python src/reproduce_pooled_ridge.py
   ```

6. Regenerate and compare the complete external-synthetic workflow in an
   isolated temporary directory:

   ```bash
   python src/verify_external_reproducibility.py
   ```

7. Regenerate all manuscript figures:

   ```bash
   python src/make_figures.py
   ```

The decision-analysis notebook additionally requires both official public
Task-1 and Task-2 archives in the local locations described in
`data/README.md`. Notebook outputs and execution counts are intentionally
cleared in the repository.

## Reported-output audit

`src/audit_reported_results.py` checks the direct and ancestry decision counts,
regrets, bootstrap metadata, paired comparison, Method-D sensitivity grid,
external B2A errors, zero/nonzero diagnostics, sign result, Pooled Ridge
aggregate, and Supplementary Table S1. The external reproducibility utility
executes the publication notebook in isolation and compares regenerated
scientific content with the archived artifacts while ignoring non-scientific
packaging metadata.

## Figures and tables

| Item | Public producer or audit |
|---|---|
| Figure 1 | `src/make_figures.py`; `configs/DECISION_PROTOCOL_V1.md` |
| Figure 2 | `src/make_figures.py`; direct and ancestry query-level results |
| Figure 3 | `src/make_figures.py`; structural-transition results |
| Table 1 | decision notebook; `src/reproduce_structural_bootstrap.py` |
| Table 2 | `src/reproduce_method_d_sensitivity.py` |
| Table 3 | external notebook; `src/audit_reported_results.py`; `src/reproduce_pooled_ridge.py` |
| Supplementary Table S1 | `supplementary/table_s1_environment_level_diagnostics.csv` |

See `REPRODUCIBILITY_MAP.md` for the complete artifact mapping and
classification.

## Citation

Citation metadata are provided in `CITATION.cff`.

## Licensing

Source code in this repository is licensed under the MIT License; see `LICENSE-CODE`.

Documentation, figures, supplementary materials, and author-generated synthetic data are licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0); see `LICENSE-CONTENT`.

Third-party benchmark data are not redistributed by this repository and remain subject to their original terms and licenses.

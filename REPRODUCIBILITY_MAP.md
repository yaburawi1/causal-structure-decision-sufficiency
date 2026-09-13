# Reproducibility map

| Manuscript item | Public producer | Canonical public input or result | Classification | Notes |
|---|---|---|---|---|
| Figure 1: structural indicators versus intervention-effect evidence | `src/make_figures.py` | `configs/DECISION_PROTOCOL_V1.md` | **FULLY REPRODUCIBLE** | Non-quantitative schematic; it asserts no effect magnitude. |
| Figure 2: decision-state composition | `src/make_figures.py` | `results/structure_effect_decision_v1_query_level.csv`; `results/structure_effect_path_robustness_v1_query_level.csv` | **FULLY REPRODUCIBLE** | All four 50-query state-count vectors are computed from canonical rows. |
| Figure 3: direct-to-ancestry transition matrices | `src/make_figures.py` | `results/draft2_reviewer_structural_transitions_v1.csv` | **FULLY REPRODUCIBLE** | Both 3×3 count matrices are generated from the canonical transition table. |
| Table 1: unified direct/ancestry structural outcomes | `notebooks/structure_effect_decision_experiment.ipynb`; `src/reproduce_structural_bootstrap.py` | Direct and ancestry query rows; bootstrap and paired-comparison CSVs | **FULLY REPRODUCIBLE** | The script reproduces all single-policy and paired 10,000-replicate intervals with seed 20260910. |
| Table 2: Method-D edge-budget sensitivity | `src/reproduce_method_d_sensitivity.py` | Official public Task-1 archive; `results/task1_method_d_edges.csv`; sensitivity CSV | **FULLY REPRODUCIBLE** | The complete 775-edge factor-1.00 graph, all five budgets, and all reported metrics are checked exactly. |
| Table 3: external B2A zero/nonzero effect recovery | `notebooks/b2a_external_synthetic_validation.ipynb`; `src/audit_reported_results.py`; `src/verify_external_reproducibility.py` | External predictions, ground truth, summaries, and baseline comparison | **FULLY REPRODUCIBLE** | The isolated workflow regenerates and compares the stable scientific payload without repository-history or wall-clock dependencies. |
| Supplementary Table S1: environment-level external diagnostics | `src/audit_reported_results.py` | External environment summary; zero-composition CSV; `supplementary/table_s1_environment_level_diagnostics.csv` | **FULLY REPRODUCIBLE** | The table is an exact canonical-field selection. |

All three figures, all three manuscript tables, and Supplementary Table S1 are
fully reproducible. The third-party benchmark is not redistributed; acquisition
and local placement are documented in `data/README.md`.

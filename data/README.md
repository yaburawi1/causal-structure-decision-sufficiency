# Public benchmark acquisition and local placement

The external benchmark is the **NeurIPS 2022 CausalML Challenge: “Causal
Insights for Learning Paths in Education.”** Stable public identifiers are:

- NeurIPS 2022 Competition Track entry: “Causal Insights for Learning Paths in
  Education”
- CodaLab competition ID: **5626**
- Official competition guide: **arXiv:2208.12610**

This repository does not redistribute third-party benchmark archives. Obtain
the public files from the original competition source, retain their original
filenames, and keep them locally. Do not add private or leaderboard-private
data.

The default local layout is:

```text
data/neurips-2022-causal-education/Task_1_local_public.zip
data/neurips-2022-causal-education/Task_2_local_public.zip
```

The reproduction steps use the archives as follows:

- `python src/reproduce_method_d_sensitivity.py --task1-zip <path>` requires
  `Task_1_local_public.zip`, specifically
  `Task_1_data_local_dev_csv/dataset_0/train.csv` through
  `Task_1_data_local_dev_csv/dataset_4/train.csv`. It reconstructs the Method-D
  rankings, checks exact equality of the 775 factor-1.00 edges, and checks all
  five Table 2 sensitivity settings.
- `notebooks/structure_effect_decision_experiment.ipynb` requires
  `Task_1_local_public.zip::Task_1_data_local_dev_csv/adj_matrix.npy` for the
  five evaluation structures.
- The same decision notebook requires `Task_2_local_public.zip`, specifically
  `Task_2_data_local_dev/intervention_0.json` through `intervention_4.json` and
  `Task_2_data_local_dev/cate_estimate.npy`, for the 50 query definitions and
  evaluation-only ground-truth effects.
- `src/audit_reported_results.py`, `src/reproduce_structural_bootstrap.py`,
  `src/reproduce_pooled_ridge.py`, `src/verify_external_reproducibility.py`, and
  `src/make_figures.py` use only files included in this repository.

The `EXT0`–`EXT5` arrays are author-generated synthetic data and are included
in `results/b2a_external_synthetic_training_v1.npz` with their specification,
queries, predictions, and paired-Monte-Carlo ground truth.

"""Reproduce Table 1 structural intervals and paired comparisons.

This paper-only script uses the two canonical query-level result tables. The
five observed environments remain fixed; within each environment, ten query
indices are sampled with replacement for 10,000 replicates. Environment blocks
are drawn vectorially in fixed environment order with NumPy's default_rng and
seed 20260910. Conditional quantities are undefined for all-abstaining draws.
Regret is averaged over each policy/source's own decided subset.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SEED = 20260910
REPLICATES = 10_000
ENVIRONMENTS = tuple(range(5))
METRICS = (
    "coverage",
    "ambiguity_rate",
    "conditional_decision_accuracy",
    "unconditional_misleading_rate",
    "conditional_misleading_rate",
    "mean_selective_regret",
    "median_selective_regret",
)


def load_policy_frames() -> dict[tuple[str, str], pd.DataFrame]:
    direct = pd.read_csv(RESULTS / "structure_effect_decision_v1_query_level.csv")
    path = pd.read_csv(RESULTS / "structure_effect_path_robustness_v1_query_level.csv")
    keys = ["dataset_id", "query_id"]
    direct = direct.sort_values(keys).reset_index(drop=True)
    frames: dict[tuple[str, str], pd.DataFrame] = {}
    for source, prefix in (("GT", "gt_structure"), ("METHOD_D", "method_d")):
        frames[(source, "DIRECT")] = pd.DataFrame({
            "dataset_id": direct.dataset_id.astype(int),
            "decision": direct[f"{prefix}_decision"],
            "state": direct[f"{prefix}_state"],
            "regret": direct[f"{prefix}_regret"].astype(float),
        })
    for source, value in (("GT", "gt"), ("METHOD_D", "method_d")):
        part = path.loc[path.structural_source.eq(value)].sort_values(keys).reset_index(drop=True)
        frames[(source, "PATH")] = pd.DataFrame({
            "dataset_id": part.dataset_id.astype(int),
            "decision": part.path_decision,
            "state": part.path_state,
            "regret": part.selective_regret.astype(float),
        })
    for frame in frames.values():
        assert len(frame) == 50
        assert frame.groupby("dataset_id", sort=True).size().eq(10).all()
    return frames


def metric_values(frame: pd.DataFrame) -> dict[str, float]:
    decided = frame.decision.ne("ABSTAIN")
    n_decided = int(decided.sum())
    sufficient = frame.state.eq("STRUCTURE_SUFFICIENT")
    misleading = frame.state.eq("STRUCTURE_MISLEADING")
    if n_decided:
        conditional_accuracy = float(sufficient.sum() / n_decided)
        conditional_misleading = float(misleading.sum() / n_decided)
        decided_regret = frame.loc[decided, "regret"].to_numpy(float)
        mean_regret = float(decided_regret.mean())
        median_regret = float(np.median(decided_regret))
    else:
        conditional_accuracy = np.nan
        conditional_misleading = np.nan
        mean_regret = np.nan
        median_regret = np.nan
    return {
        "coverage": float(decided.mean()),
        "ambiguity_rate": float((~decided).mean()),
        "conditional_decision_accuracy": conditional_accuracy,
        "unconditional_misleading_rate": float(misleading.mean()),
        "conditional_misleading_rate": conditional_misleading,
        "mean_selective_regret": mean_regret,
        "median_selective_regret": median_regret,
    }


def environment_major_samples(frame: pd.DataFrame) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    groups = [
        np.flatnonzero(frame.dataset_id.to_numpy() == environment)
        for environment in ENVIRONMENTS
    ]
    assert all(len(group) == 10 for group in groups)
    return np.concatenate([
        rng.choice(group, size=(REPLICATES, len(group)), replace=True)
        for group in groups
    ], axis=1)


def reproduce_single_policy(frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    samples = environment_major_samples(frames[("GT", "DIRECT")])
    rows = []
    for source in ("GT", "METHOD_D"):
        for policy in ("DIRECT", "PATH"):
            frame = frames[(source, policy)]
            observed = metric_values(frame)
            values = {metric: np.full(REPLICATES, np.nan) for metric in METRICS}
            for replicate, indices in enumerate(samples):
                record = metric_values(frame.iloc[indices])
                for metric in METRICS:
                    values[metric][replicate] = record[metric]
            for metric in METRICS:
                finite = values[metric][np.isfinite(values[metric])]
                low, high = np.quantile(finite, [0.025, 0.975])
                rows.append({
                    "structural_source": source,
                    "policy": policy,
                    "metric": metric,
                    "estimate": observed[metric],
                    "bootstrap_ci_low": low,
                    "bootstrap_ci_high": high,
                    "valid_bootstrap_replicates": len(finite),
                    "bootstrap_replicates": REPLICATES,
                    "bootstrap_seed": SEED,
                    "resampling": "query_indices_within_environment_preserving_environment_sizes",
                })
    return pd.DataFrame(rows)


def reproduce_paired(frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    paired_metrics = ("coverage", "ambiguity_rate", "unconditional_misleading_rate", "mean_selective_regret")
    output_names = {"unconditional_misleading_rate": "misleading_rate"}
    rows = []
    for policy in ("DIRECT", "PATH"):
        gt = frames[("GT", policy)]
        method_d = frames[("METHOD_D", policy)]
        gt_observed = metric_values(gt)
        method_observed = metric_values(method_d)
        # The historical paired notebook generated draws replicate-major.
        rng = np.random.default_rng(SEED)
        groups = [np.flatnonzero(gt.dataset_id.to_numpy() == e) for e in ENVIRONMENTS]
        replicate_major = np.array([
            np.concatenate([rng.choice(group, len(group), replace=True) for group in groups])
            for _ in range(REPLICATES)
        ])
        differences = {metric: np.full(REPLICATES, np.nan) for metric in paired_metrics}
        for replicate, indices in enumerate(replicate_major):
            gt_values = metric_values(gt.iloc[indices])
            method_values = metric_values(method_d.iloc[indices])
            for metric in paired_metrics:
                differences[metric][replicate] = gt_values[metric] - method_values[metric]
        for metric in paired_metrics:
            finite = differences[metric][np.isfinite(differences[metric])]
            low, high = np.quantile(finite, [0.025, 0.975])
            rows.append({
                "policy": policy,
                "metric": output_names.get(metric, metric),
                "difference_definition": "GT_minus_Method_D",
                "gt_estimate": gt_observed[metric],
                "method_d_estimate": method_observed[metric],
                "delta_gt_minus_method_d": gt_observed[metric] - method_observed[metric],
                "bootstrap_ci_low": low,
                "bootstrap_ci_high": high,
                "bootstrap_replicates": REPLICATES,
                "valid_bootstrap_replicates": len(finite),
                "bootstrap_seed": SEED,
                "resampling": "paired_query_indices_within_environment",
            })
    return pd.DataFrame(rows)


def assert_matches(reproduced: pd.DataFrame, canonical_path: Path, keys: list[str]) -> None:
    canonical = pd.read_csv(canonical_path)
    left = reproduced.sort_values(keys).reset_index(drop=True)
    right = canonical.sort_values(keys).reset_index(drop=True)
    assert list(left.columns) == list(right.columns)
    assert left[keys].equals(right[keys])
    numeric = left.select_dtypes(include=[np.number]).columns
    np.testing.assert_allclose(left[numeric], right[numeric], rtol=0.0, atol=5e-15, equal_nan=True)
    text_columns = [column for column in left.columns if column not in numeric and column not in keys]
    assert left[text_columns].equals(right[text_columns])


def main() -> None:
    frames = load_policy_frames()
    single = reproduce_single_policy(frames)
    paired = reproduce_paired(frames)
    assert_matches(
        single,
        RESULTS / "draft2_reviewer_structural_bootstrap_v1.csv",
        ["structural_source", "policy", "metric"],
    )
    assert_matches(
        paired,
        RESULTS / "structure_effect_paired_comparison_v1.csv",
        ["policy", "metric"],
    )
    print("PASS: reproduced all frozen structural and paired bootstrap values.")


if __name__ == "__main__":
    main()

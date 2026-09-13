"""Audit the numeric results reported throughout Sections 4.1--4.9.

This script reads only publication-package artifacts. It does not regenerate
benchmark predictions, alter frozen results, or access data outside this repository.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def close(actual: float, expected: float, atol: float = 1e-12) -> None:
    assert np.isclose(actual, expected, rtol=0.0, atol=atol), (actual, expected)


def direct_checks() -> None:
    frame = pd.read_csv(RESULTS / "structure_effect_decision_v1_query_level.csv")
    assert len(frame) == 50
    expected = {
        "gt_structure": (13, 10, 27, 0.04144105494918368),
        "method_d": (6, 7, 37, 0.044543247420893654),
    }
    for prefix, (sufficient, misleading, ambiguous, mean_regret) in expected.items():
        states = frame[f"{prefix}_state"]
        assert int(states.eq("STRUCTURE_SUFFICIENT").sum()) == sufficient
        assert int(states.eq("STRUCTURE_MISLEADING").sum()) == misleading
        assert int(states.eq("STRUCTURE_AMBIGUOUS").sum()) == ambiguous
        close(frame[f"{prefix}_regret"].mean(), mean_regret)


def path_checks() -> None:
    frame = pd.read_csv(RESULTS / "structure_effect_path_robustness_v1_query_level.csv")
    assert len(frame) == 100
    expected = {
        "gt": (5, 13, 32, 0.09585784664103579),
        "method_d": (5, 17, 28, 0.07070392207077919),
    }
    for source, (sufficient, misleading, ambiguous, mean_regret) in expected.items():
        part = frame.loc[frame["structural_source"] == source]
        assert len(part) == 50
        assert int(part["path_state"].eq("STRUCTURE_SUFFICIENT").sum()) == sufficient
        assert int(part["path_state"].eq("STRUCTURE_MISLEADING").sum()) == misleading
        assert int(part["path_state"].eq("STRUCTURE_AMBIGUOUS").sum()) == ambiguous
        close(part["selective_regret"].mean(), mean_regret)


def uncertainty_and_sensitivity_checks() -> None:
    boot = pd.read_csv(RESULTS / "draft2_reviewer_structural_bootstrap_v1.csv")
    assert len(boot) == 28
    assert boot["bootstrap_replicates"].eq(10_000).all()
    assert boot["bootstrap_seed"].eq(20260910).all()
    gt_direct = boot.query("structural_source == 'GT' and policy == 'DIRECT'")
    coverage = gt_direct.loc[gt_direct.metric == "coverage"].iloc[0]
    accuracy = gt_direct.loc[
        gt_direct.metric == "conditional_decision_accuracy"
    ].iloc[0]
    close(coverage.estimate, 0.46)
    close(coverage.bootstrap_ci_low, 0.32)
    close(coverage.bootstrap_ci_high, 0.60)
    close(accuracy.estimate, 13 / 23)

    paired = pd.read_csv(RESULTS / "structure_effect_paired_comparison_v1.csv")
    direct_coverage = paired.query("policy == 'DIRECT' and metric == 'coverage'").iloc[0]
    close(direct_coverage.delta_gt_minus_method_d, 0.20)
    close(direct_coverage.bootstrap_ci_low, 0.06)
    close(direct_coverage.bootstrap_ci_high, 0.34)

    sensitivity = pd.read_csv(
        RESULTS / "draft2_reviewer_method_d_threshold_sensitivity_v1.csv"
    )
    assert sensitivity["setting_factor"].drop_duplicates().tolist() == [
        0.75, 0.90, 1.00, 1.10, 1.25
    ]
    assert sensitivity.groupby("setting_factor").size().eq(2).all()
    assert sensitivity["total_edge_count"].drop_duplicates().tolist() == [
        585, 700, 775, 855, 975
    ]


def external_checks() -> None:
    pred = pd.read_csv(RESULTS / "b2a_external_synthetic_predictions_v1.csv")
    gt = pd.read_csv(RESULTS / "b2a_external_synthetic_ground_truth_v1.csv")
    frame = pred.merge(gt[["environment_id", "query_id", "tau_gt"]])
    assert len(frame) == 240
    error = frame["tau_hat"] - frame["tau_gt"]
    close(np.abs(error).mean(), 0.01485313835741137)
    close(np.sqrt(np.square(error).mean()), 0.019287765017673184)
    assert int(frame["tau_gt"].eq(0.0).sum()) == 158

    nonzero = frame.loc[frame["tau_gt"].ne(0.0)]
    assert len(nonzero) == 82
    close(np.abs(nonzero.tau_hat - nonzero.tau_gt).mean(), 0.015624448384963737)
    close(stats.pearsonr(nonzero.tau_hat, nonzero.tau_gt).statistic, 0.9882345609486735)
    close(stats.spearmanr(nonzero.tau_hat, nonzero.tau_gt).statistic, 0.969765239821073)
    assert np.sign(nonzero.tau_hat).eq(np.sign(nonzero.tau_gt)).all()
    ci_low = stats.beta.ppf(0.025, 82, 1)
    close(ci_low, 0.9560105458131576)

    zero = frame.loc[frame["tau_gt"].eq(0.0)]
    assert int(zero.tau_hat.gt(0).sum()) == 73
    assert int(zero.tau_hat.lt(0).sum()) == 85
    assert int(zero.tau_hat.eq(0).sum()) == 0
    close(zero.tau_hat.abs().max(), 0.07888304368593663)

    comparison = pd.read_csv(
        RESULTS / "b2a_external_synthetic_baseline_comparison_v1.csv"
    ).set_index("method")
    close(comparison.loc["POOLED_RIDGE", "mae"], 0.004514998499575508)
    close(comparison.loc["POOLED_RIDGE", "rmse"], 0.006277943520055233)

    pooled = pd.read_csv(
        RESULTS / "pooled_ridge_predictions_reconstructed_for_release.csv"
    )
    pooled_evaluation = pooled.merge(
        gt[["environment_id", "query_id", "tau_gt"]],
        on=["environment_id", "query_id"],
        validate="one_to_one",
    )
    pooled_error = pooled_evaluation.tau_hat - pooled_evaluation.tau_gt
    close(pooled_error.abs().mean(), comparison.loc["POOLED_RIDGE", "mae"])
    close(np.sqrt(np.square(pooled_error).mean()), comparison.loc["POOLED_RIDGE", "rmse"])

    environment = pd.read_csv(
        RESULTS / "b2a_external_synthetic_environment_summary_v1.csv"
    )
    composition = pd.read_csv(
        RESULTS / "draft2_reviewer_zero_composition_by_environment_v1.csv"
    )
    expected_s1 = environment[[
        "environment_id", "n_queries", "mae", "rmse", "pearson", "spearman"
    ]].merge(composition[[
        "environment_id", "exact_zero_count", "nonzero_count",
        "zero_proportion", "mean_abs_tau_gt",
    ]])[[
        "environment_id", "n_queries", "exact_zero_count", "nonzero_count",
        "zero_proportion", "mean_abs_tau_gt", "mae", "rmse", "pearson", "spearman",
    ]]
    table_s1 = pd.read_csv(
        ROOT / "supplementary/table_s1_environment_level_diagnostics.csv"
    )
    pd.testing.assert_frame_equal(table_s1, expected_s1, rtol=0.0, atol=5e-15)

    dgp = json.loads((RESULTS / "b2a_external_synthetic_dgp_spec_v1.json").read_text())
    assert [e["environment_id"] for e in dgp["environments"]] == [
        f"EXT{i}" for i in range(6)
    ]


def main() -> None:
    direct_checks()
    path_checks()
    uncertainty_and_sensitivity_checks()
    external_checks()
    print("PASS: all audited manuscript values match the frozen public artifacts.")


if __name__ == "__main__":
    main()

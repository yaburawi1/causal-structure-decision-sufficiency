"""Reconstruct the secondary post-validation Pooled Ridge predictions.

This paper-specific reconstruction fits one untuned multi-output Ridge model
per external synthetic environment using 20 state features plus eight one-hot
action indicators. It uses alpha=1, the default intercept and solver, no
standardization, and no delta or graph features. The result is explicitly a
release reconstruction, not a frozen historical prediction artifact.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ENVIRONMENTS = tuple(f"EXT{i}" for i in range(6))
STATE_COLUMNS = tuple(f"x_{node:02d}" for node in range(20))
OUTPUT = RESULTS / "pooled_ridge_predictions_reconstructed_for_release.csv"


def reconstruct() -> pd.DataFrame:
    with np.load(
        RESULTS / "b2a_external_synthetic_training_v1.npz", allow_pickle=False
    ) as archive:
        training = {key: archive[key] for key in archive.files}
    queries = pd.read_csv(
        RESULTS / "b2a_external_synthetic_queries_v1.csv", float_precision="round_trip"
    ).sort_values(["environment_id", "query_id"])
    records = []
    identity = np.eye(8, dtype=np.float64)
    for environment in ENVIRONMENTS:
        states = training[f"{environment}_states"]
        actions = training[f"{environment}_actions"]
        assert states.shape == (400, 120, 20)
        assert actions.shape == (400, 119)
        aligned_states = states[:, 10:117, :].reshape(-1, 20)
        aligned_actions = actions[:, 11:118].reshape(-1).astype(np.int64)
        aligned_targets = states[:, 13:120, :].reshape(-1, 20)
        features = np.concatenate([aligned_states, identity[aligned_actions]], axis=1)
        assert features.shape == (42_800, 28)
        assert aligned_targets.shape == (42_800, 20)

        model = Ridge(alpha=1.0)
        model.fit(features, aligned_targets)
        part = queries.loc[queries.environment_id.eq(environment)].sort_values("query_id")
        query_states = part[list(STATE_COLUMNS)].to_numpy(dtype=np.float64)
        intervention_actions = part.intervention_action.to_numpy(dtype=np.int64)
        reference_actions = part.reference_action.to_numpy(dtype=np.int64)
        intervention_inputs = np.concatenate(
            [query_states, identity[intervention_actions]], axis=1
        )
        reference_inputs = np.concatenate(
            [query_states, identity[reference_actions]], axis=1
        )
        intervention_predictions = model.predict(intervention_inputs)
        reference_predictions = model.predict(reference_inputs)
        for index, query in enumerate(part.itertuples(index=False)):
            target = int(query.target_construct)
            records.append({
                "environment_id": environment,
                "query_id": int(query.query_id),
                "intervention_action": int(query.intervention_action),
                "reference_action": int(query.reference_action),
                "target": target,
                "tau_hat": float(
                    intervention_predictions[index, target]
                    - reference_predictions[index, target]
                ),
            })
    output = pd.DataFrame(records).sort_values(
        ["environment_id", "query_id"]
    ).reset_index(drop=True)
    assert output.shape == (240, 6)
    assert not output[["environment_id", "query_id"]].duplicated().any()
    assert np.isfinite(output.tau_hat).all()
    return output


def validate(predictions: pd.DataFrame) -> None:
    ground_truth = pd.read_csv(
        RESULTS / "b2a_external_synthetic_ground_truth_v1.csv",
        float_precision="round_trip",
    )[["environment_id", "query_id", "tau_gt"]]
    evaluation = predictions.merge(
        ground_truth, on=["environment_id", "query_id"], validate="one_to_one"
    )
    error = evaluation.tau_hat - evaluation.tau_gt
    zero = evaluation.loc[evaluation.tau_gt.eq(0.0)]
    nonzero = evaluation.loc[evaluation.tau_gt.ne(0.0)]
    metrics = {
        "mae": float(error.abs().mean()),
        "rmse": float(np.sqrt(np.square(error).mean())),
        "gt_zero_mae": float(zero.tau_hat.abs().mean()),
        "gt_nonzero_mae": float((nonzero.tau_hat - nonzero.tau_gt).abs().mean()),
        "gt_nonzero_sign_agreement": float(
            np.sign(nonzero.tau_hat).eq(np.sign(nonzero.tau_gt)).mean()
        ),
    }
    canonical = pd.read_csv(
        RESULTS / "b2a_external_synthetic_baseline_comparison_v1.csv"
    ).set_index("method").loc["POOLED_RIDGE"]
    for metric, value in metrics.items():
        np.testing.assert_allclose(value, canonical[metric], rtol=0.0, atol=5e-15)


def main() -> None:
    first = reconstruct()
    second = reconstruct()
    pd.testing.assert_frame_equal(first, second, check_exact=True)
    validate(first)
    first.to_csv(OUTPUT, index=False)
    print(f"PASS: deterministic Pooled Ridge reconstruction written to {OUTPUT.name}.")


if __name__ == "__main__":
    main()

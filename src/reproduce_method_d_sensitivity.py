"""Exactly reconstruct Table 2 Method-D edge-budget sensitivity.

This is the minimal retained Method-D implementation from the original Task-1
ranked-DAG notebook. It reads only the public Task-1 training archive and the
paper's canonical query-level result table. It first requires exact edge-set
identity at factor 1.00, then checks all reported metrics at all five budgets.
No scores, thresholds, graph rules, or decision rules are tuned here.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
N_CONSTRUCTS = 50
ENVIRONMENTS = tuple(range(5))
BASE_BUDGETS = (75, 150, 200, 150, 200)
FACTORS = ("0.75", "0.90", "1.00", "1.10", "1.25")


def compute_b1(raw: np.ndarray) -> np.ndarray:
    """Compute E[delta_j|A=i] - E[delta_j] at lag two, exactly as retained."""
    sum_by_action = np.zeros((N_CONSTRUCTS, N_CONSTRUCTS), dtype=float)
    count_by_action = np.zeros(N_CONSTRUCTS, dtype=int)
    overall_sum = np.zeros(N_CONSTRUCTS, dtype=float)
    overall_count = 0
    for student_id in np.unique(raw[:, 0]):
        rows = raw[raw[:, 0] == student_id]
        actions = rows[:-2, 1].astype(int)
        delta = rows[2:, 2:] - rows[:-2, 2:]
        overall_sum += delta.sum(axis=0)
        overall_count += len(delta)
        for action in np.unique(actions):
            mask = actions == action
            sum_by_action[action] += delta[mask].sum(axis=0)
            count_by_action[action] += int(mask.sum())
    if np.any(count_by_action == 0):
        raise ValueError("At least one action has zero support.")
    return sum_by_action / count_by_action[:, None] - overall_sum[None, :] / overall_count


def ranked_candidates(scores: np.ndarray) -> list[tuple[int, int, float]]:
    candidates = []
    for i in range(N_CONSTRUCTS):
        for j in range(i + 1, N_CONSTRUCTS):
            if scores[i, j] >= scores[j, i]:
                source, target, score = i, j, scores[i, j]
            else:
                source, target, score = j, i, scores[j, i]
            if score > 0:
                candidates.append((source, target, float(score)))
    candidates.sort(key=lambda row: row[2], reverse=True)
    return candidates


def path_exists(adjacency: np.ndarray, start: int, goal: int) -> bool:
    stack = [start]
    visited = set()
    while stack:
        node = stack.pop()
        if node == goal:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(np.flatnonzero(adjacency[node]).tolist())
    return False


def assemble_ranked_dag(
    candidates: list[tuple[int, int, float]], target_k: int
) -> np.ndarray:
    adjacency = np.zeros((N_CONSTRUCTS, N_CONSTRUCTS), dtype=bool)
    accepted = 0
    for source, target, _ in candidates:
        if path_exists(adjacency, target, source):
            continue
        adjacency[source, target] = True
        accepted += 1
        if accepted == target_k:
            return adjacency
    raise ValueError(f"Only {accepted} acyclic candidates available; requested {target_k}.")


def directed_reachability(adjacency: np.ndarray) -> np.ndarray:
    reach = adjacency.copy()
    for intermediate in range(N_CONSTRUCTS):
        reach |= reach[:, intermediate, None] & reach[None, intermediate, :]
    return reach


def rounded_budget(base: int, factor: str) -> int:
    units = (Decimal(base) * Decimal(factor) / Decimal(5)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return int(units * 5)


def evaluate(graphs: dict[int, np.ndarray], queries: pd.DataFrame, path: bool) -> dict[str, float]:
    evidence = {
        environment: directed_reachability(graph) if path else graph
        for environment, graph in graphs.items()
    }
    states, regrets = [], []
    for row in queries.itertuples(index=False):
        graph = evidence[int(row.dataset_id)]
        intervention_edge = bool(graph[int(row.intervention), int(row.target)])
        reference_edge = bool(graph[int(row.reference), int(row.target)])
        if intervention_edge and not reference_edge:
            decision = "I"
        elif reference_edge and not intervention_edge:
            decision = "R"
        else:
            decision = "ABSTAIN"
        if decision == "ABSTAIN":
            state, regret = "AMBIGUOUS", np.nan
        elif decision == row.oracle_decision:
            state, regret = "SUFFICIENT", 0.0
        else:
            state, regret = "MISLEADING", abs(float(row.tau_gt))
        states.append(state)
        regrets.append(regret)
    states = np.asarray(states)
    regrets = np.asarray(regrets, dtype=float)
    decided = states != "AMBIGUOUS"
    n_decided = int(decided.sum())
    misleading = states == "MISLEADING"
    sufficient = states == "SUFFICIENT"
    return {
        "coverage": float(decided.mean()),
        "ambiguity_rate": float((~decided).mean()),
        "conditional_decision_accuracy": float(sufficient.sum() / n_decided),
        "unconditional_misleading_rate": float(misleading.mean()),
        "conditional_misleading_rate": float(misleading.sum() / n_decided),
        "mean_selective_regret": float(np.nanmean(regrets)),
        "median_selective_regret": float(np.nanmedian(regrets)),
    }


def reconstruct(task1_zip: Path) -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    queries = pd.read_csv(RESULTS / "structure_effect_decision_v1_query_level.csv")
    candidate_lists = {}
    with zipfile.ZipFile(task1_zip) as archive:
        for environment in ENVIRONMENTS:
            member = f"Task_1_data_local_dev_csv/dataset_{environment}/train.csv"
            with archive.open(member) as handle:
                raw = np.loadtxt(handle, delimiter=",")
            assert raw.shape[1] == 52
            assert len(np.unique(raw[:, 0])) == 100
            candidate_lists[environment] = ranked_candidates(compute_b1(raw))

    rows = []
    frozen_graphs = {}
    for factor in FACTORS:
        budgets = {
            environment: rounded_budget(BASE_BUDGETS[environment], factor)
            for environment in ENVIRONMENTS
        }
        graphs = {
            environment: assemble_ranked_dag(candidate_lists[environment], budget)
            for environment, budget in budgets.items()
        }
        if factor == "1.00":
            frozen_graphs = {environment: graph.copy() for environment, graph in graphs.items()}
        total_edges = sum(int(graph.sum()) for graph in graphs.values())
        for policy, use_paths in (("DIRECT", False), ("PATH", True)):
            rows.append({
                "setting_factor": float(factor),
                "setting_role": "FROZEN" if factor == "1.00" else "POST_HOC_SENSITIVITY",
                "rounding_rule": "nearest_multiple_of_5_half_up",
                "k_by_environment": json.dumps({str(k): v for k, v in budgets.items()}),
                "total_edge_count": total_edges,
                "pooled_directed_density_no_self": total_edges / (5 * 50 * 49),
                "policy": policy,
                **evaluate(graphs, queries, use_paths),
                "selection_note": "descriptive_grid_not_optimized_against_decision_ground_truth",
            })
    return pd.DataFrame(rows), frozen_graphs


def validate(reproduced: pd.DataFrame, frozen_graphs: dict[int, np.ndarray]) -> None:
    canonical_edges = pd.read_csv(RESULTS / "task1_method_d_edges.csv")
    expected_edge_set = set(map(tuple, canonical_edges[
        ["dataset_id", "source_construct", "target_construct"]
    ].astype(int).to_numpy()))
    actual_edge_set = {
        (environment, int(source), int(target))
        for environment, graph in frozen_graphs.items()
        for source, target in zip(*np.where(graph))
    }
    assert actual_edge_set == expected_edge_set, (
        f"factor-1.00 edge mismatch: reconstructed-only={len(actual_edge_set - expected_edge_set)}, "
        f"canonical-only={len(expected_edge_set - actual_edge_set)}"
    )

    canonical = pd.read_csv(
        RESULTS / "draft2_reviewer_method_d_threshold_sensitivity_v1.csv"
    )
    keys = ["setting_factor", "policy"]
    left = reproduced.sort_values(keys).reset_index(drop=True)
    right = canonical.sort_values(keys).reset_index(drop=True)
    assert list(left.columns) == list(right.columns)
    numeric = left.select_dtypes(include=[np.number]).columns
    np.testing.assert_allclose(left[numeric], right[numeric], rtol=0.0, atol=5e-15)
    text = [column for column in left.columns if column not in numeric]
    assert left[text].equals(right[text])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task1-zip",
        type=Path,
        default=ROOT / "data/neurips-2022-causal-education/Task_1_local_public.zip",
        help="Official NeurIPS 2022 Task_1_local_public.zip",
    )
    args = parser.parse_args()
    if not args.task1_zip.is_file():
        parser.error(f"Task-1 archive not found: {args.task1_zip}")
    reproduced, frozen_graphs = reconstruct(args.task1_zip)
    validate(reproduced, frozen_graphs)
    print("PASS: factor-1.00 edge set and all five sensitivity settings match exactly.")


if __name__ == "__main__":
    main()

"""Regenerate and compare the external-synthetic scientific payload.

By default, the publication notebook is executed in an isolated temporary
copy. The regenerated arrays, queries, predictions, ground truth, summaries,
and baseline comparison are then checked against the archived publication
artifacts. Repository history, timestamps, runtime labels, and other
non-scientific metadata are excluded from the comparison.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
ARCHIVED_RESULTS = ROOT / "results"
NOTEBOOK = "b2a_external_synthetic_validation.ipynb"

GENERATED_FILES = (
    "b2a_external_synthetic_dgp_spec_v1.json",
    "b2a_external_synthetic_queries_v1.csv",
    "b2a_external_synthetic_training_v1.npz",
    "b2a_external_synthetic_manifest_v1.json",
    "b2a_external_synthetic_predictions_v1.csv",
    "b2a_external_synthetic_ground_truth_v1.csv",
    "b2a_external_synthetic_summary_v1.csv",
    "b2a_external_synthetic_environment_summary_v1.csv",
    "b2a_external_synthetic_baseline_comparison_v1.csv",
    "b2a_external_synthetic_baseline_environment_v1.csv",
)

CANONICAL_CSV_FILES = (
    "b2a_external_synthetic_queries_v1.csv",
    "b2a_external_synthetic_predictions_v1.csv",
    "b2a_external_synthetic_ground_truth_v1.csv",
    "b2a_external_synthetic_summary_v1.csv",
    "b2a_external_synthetic_environment_summary_v1.csv",
    "b2a_external_synthetic_baseline_comparison_v1.csv",
)


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def dgp_scientific_sha256(path: Path) -> str:
    dgp = json.loads(path.read_text(encoding="utf-8"))
    payload = canonical_json_bytes({"environments": dgp["environments"]})
    return hashlib.sha256(payload).hexdigest()


def training_scientific_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with np.load(path, allow_pickle=False) as arrays:
        for key in sorted(arrays.files):
            array = np.ascontiguousarray(arrays[key])
            tokens = (
                key.encode("utf-8"),
                array.dtype.str.encode("ascii"),
                canonical_json_bytes(list(array.shape)),
            )
            for token in tokens:
                digest.update(len(token).to_bytes(8, "big"))
                digest.update(token)
            digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def execute_isolated_copy() -> tempfile.TemporaryDirectory:
    temporary = tempfile.TemporaryDirectory(prefix="external-reproduction-")
    work = Path(temporary.name)
    for directory in ("configs", "notebooks", "results"):
        shutil.copytree(ROOT / directory, work / directory)
    for filename in GENERATED_FILES:
        path = work / "results" / filename
        if path.exists():
            path.unlink()

    notebook_path = work / "notebooks" / NOTEBOOK
    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=1800,
        kernel_name="python3",
        resources={"metadata": {"path": str(work)}},
    )
    client.execute()
    return temporary


def compare_npz(regenerated: Path) -> None:
    archived_path = ARCHIVED_RESULTS / "b2a_external_synthetic_training_v1.npz"
    regenerated_path = regenerated / "b2a_external_synthetic_training_v1.npz"
    with np.load(archived_path, allow_pickle=False) as archived, np.load(
        regenerated_path, allow_pickle=False
    ) as reproduced:
        assert archived.files == reproduced.files
        for key in archived.files:
            np.testing.assert_array_equal(archived[key], reproduced[key])


def compare_dgp(regenerated: Path) -> None:
    archived = json.loads(
        (ARCHIVED_RESULTS / "b2a_external_synthetic_dgp_spec_v1.json").read_text()
    )
    reproduced = json.loads(
        (regenerated / "b2a_external_synthetic_dgp_spec_v1.json").read_text()
    )
    assert archived["environments"] == reproduced["environments"]
    assert dgp_scientific_sha256(
        ARCHIVED_RESULTS / "b2a_external_synthetic_dgp_spec_v1.json"
    ) == dgp_scientific_sha256(
        regenerated / "b2a_external_synthetic_dgp_spec_v1.json"
    )


def compare_csv_files(regenerated: Path) -> None:
    for filename in CANONICAL_CSV_FILES:
        archived = pd.read_csv(
            ARCHIVED_RESULTS / filename, float_precision="round_trip"
        )
        reproduced = pd.read_csv(
            regenerated / filename, float_precision="round_trip"
        )
        pd.testing.assert_frame_equal(archived, reproduced, check_exact=True)


def validate_manifest(results: Path) -> None:
    manifest = json.loads(
        (results / "b2a_external_synthetic_manifest_v1.json").read_text()
    )
    assert manifest["schema_version"] == "b2a_external_synthetic_manifest_v1"
    assert manifest["protocol_version"] == (
        "B2A_EXTERNAL_SYNTHETIC_VALIDATION_PROTOCOL_V1_1"
    )
    assert manifest["implementation_spec_version"] == (
        "B2A_EXTERNAL_SYNTHETIC_IMPLEMENTATION_SPEC_V1"
    )
    records = {record["relative_path"]: record for record in manifest["artifacts"]}
    expected = {
        "results/b2a_external_synthetic_dgp_spec_v1.json": dgp_scientific_sha256(
            results / "b2a_external_synthetic_dgp_spec_v1.json"
        ),
        "results/b2a_external_synthetic_queries_v1.csv": hashlib.sha256(
            (results / "b2a_external_synthetic_queries_v1.csv").read_bytes()
        ).hexdigest(),
        "results/b2a_external_synthetic_training_v1.npz": (
            training_scientific_sha256(
                results / "b2a_external_synthetic_training_v1.npz"
            )
        ),
    }
    assert set(records) == set(expected)
    for relative_path, expected_hash in expected.items():
        assert records[relative_path]["scientific_payload_sha256"] == expected_hash


def compare(regenerated: Path) -> None:
    compare_dgp(regenerated)
    compare_npz(regenerated)
    compare_csv_files(regenerated)
    validate_manifest(ARCHIVED_RESULTS)
    validate_manifest(regenerated)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--regenerated-results",
        type=Path,
        help="Compare an existing regenerated results directory instead of executing the notebook.",
    )
    args = parser.parse_args()
    if args.regenerated_results is not None:
        compare(args.regenerated_results.resolve())
    else:
        temporary = execute_isolated_copy()
        try:
            compare(Path(temporary.name) / "results")
        finally:
            temporary.cleanup()
    print(
        "PASS: external-synthetic scientific content reproduces independently "
        "of repository history, wall-clock time, and absolute paths."
    )


if __name__ == "__main__":
    main()

"""Execute the existing behavior of the dependency-free consumer seeds.

Journey acceptance is a separately frozen, on-demand observation, not a
standing evaluator or a test that pins documentation wording/file inventories.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

JOURNEY_ROOT = Path(__file__).resolve().parents[1] / "evals/fixtures/consumer-journeys"


@pytest.mark.boundary_contract(
    reason="execute copied consumer seeds through their documented unittest boundary"
)
@pytest.mark.parametrize("fixture_id", ["spec-impl-alias", "create-cli-refresh"])
def test_seed_baseline(tmp_path: Path, fixture_id: str) -> None:
    consumer = tmp_path / fixture_id
    shutil.copytree(JOURNEY_ROOT / fixture_id / "seed", consumer)
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=consumer,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

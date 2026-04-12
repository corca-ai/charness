from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_check_coverage_passes_on_current_repo() -> None:
    result = run_script("scripts/check-coverage.py", "--repo-root", str(ROOT), "--json")
    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 1
    assert payload["scope"] == "control-plane"
    assert payload["coverage"] >= 0.60
    assert any(item["path"] == "scripts/control_plane_lib.py" for item in payload["files"])

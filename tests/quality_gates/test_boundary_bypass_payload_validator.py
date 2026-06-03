from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "skills/public/quality/references/boundary-bypass-payload.example.json"


def test_validates_stack_neutral_boundary_bypass_example() -> None:
    result = run_script(
        "skills/public/quality/scripts/validate_boundary_bypass_payload.py",
        "--input",
        str(EXAMPLE),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["summary"]["candidate_count"] == 3
    assert payload["summary"]["internal_boundary_count"] == 1


def test_rejects_summary_count_drift(tmp_path: Path) -> None:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    payload["summary"]["convertible_count"] = 99
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = run_script(
        "skills/public/quality/scripts/validate_boundary_bypass_payload.py",
        "--input",
        str(path),
        "--json",
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert "summary.convertible_count" in report["error"]

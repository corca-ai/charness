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


def test_debug_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: demo", "language: en", "output_dir: charness-artifacts/debug", ""]),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/debug/scripts/scaffold_debug_artifact.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/debug/latest.md"
    assert payload["validator_command"] == "python3 scripts/validate-debug-artifact.py --repo-root ."
    assert "# Debug Review" in payload["template"]
    assert "## Reproduction" in payload["template"]
    assert "## Seam Risk" in payload["template"]
    assert "- Interrupt ID: TODO" in payload["template"]
    assert "## Interrupt Decision" in payload["template"]
    assert "- Next Step: impl" in payload["template"]
    assert "## Verification" in payload["template"]

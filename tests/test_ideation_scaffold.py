from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

import scripts.export_plugin as export_plugin_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]

SCAFFOLD = "skills/public/ideation/scripts/scaffold_ideation_artifact.py"


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_ideation_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    # `ideation` has no adapter: the scaffold is self-contained and writes a
    # dated record under a fixed default directory.
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"].startswith("charness-artifacts/ideation/")
    assert payload["artifact_path"].endswith(".md")
    assert payload["artifact_role"] == "record"
    assert payload["write_artifact_path"] == payload["artifact_path"]
    # The validator is path-based, so the command carries the write target.
    assert "validate_ideation_artifact.py" in payload["validator_command"]
    assert f"--paths {payload['write_artifact_path']}" in payload["validator_command"]

    template = payload["template"]
    assert "## Structured Questions" in template
    # The structured block must carry valid enum values the validator asserts on.
    assert "- Q1 | urgency: must-resolve | depends-on: null | action: spec |" in template
    assert "- Q2 | urgency: probe-in-impl | depends-on: Q1 | action: impl |" in template

    # Dogfood: the emitted skeleton must pass the real validator unedited, and
    # the validator must actually validate it (not skip it as off-prefix).
    artifact_path = repo / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(template, encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr
    assert "Validated 1 ideation artifact" in validation.stdout


def test_exported_ideation_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
    export_root = tmp_path / "export"
    export_result = run_loaded_script_main(
        "export_plugin.py",
        export_plugin_module,
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(export_root),
    )
    assert export_result.returncode == 0, export_result.stderr
    plugin_root = export_root / "plugins" / "charness"
    scaffold = plugin_root / "skills" / "ideation" / "scripts" / "scaffold_ideation_artifact.py"

    consumer = tmp_path / "consumer"
    consumer.mkdir()

    result = run_script(str(scaffold), "--repo-root", str(consumer), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_role"] == "record"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_ideation_artifact.py" in payload["validator_command"]

    artifact_path = consumer / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(payload["template"], encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr
    assert "Validated 1 ideation artifact" in validation.stdout

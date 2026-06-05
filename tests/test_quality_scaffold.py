from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAFFOLD = "skills/public/quality/scripts/scaffold_quality_artifact.py"

# Headings the scaffold must emit so an author starts from a validator-passing
# skeleton instead of rediscovering scripts/validate_quality_artifact.py by
# trial-and-error.
REQUIRED_HEADINGS = (
    "## Scope",
    "## Current Gates",
    "## Runtime Signals",
    "## Healthy",
    "## Weak",
    "## Missing",
    "## Deferred",
    "## Advisory",
    "## Delegated Review",
    "## Commands Run",
    "## Recommended Next Gates",
    "## History",
)


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _write_adapter(repo: Path, repo_name: str) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            ["version: 1", f"repo: {repo_name}", "language: en", "output_dir: charness-artifacts/quality", ""]
        ),
        encoding="utf-8",
    )


def test_quality_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")

    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/quality/latest.md"
    assert payload["artifact_role"] == "current_pointer"
    assert payload["write_artifact_path"] == "charness-artifacts/quality/latest.md"
    assert payload["write_artifact_role"] == "current_pointer"
    assert payload["current_pointer_symlink_target"] is None
    assert payload["validator_command"].endswith("scripts/validate_quality_artifact.py --repo-root .")

    template = payload["template"]
    assert template.startswith("# Quality Review\n")
    for heading in REQUIRED_HEADINGS:
        assert heading in template, heading
    # Runtime Signals carries the four prefixes the validator asserts on.
    assert "- runtime source: structured metrics" in template
    assert "rendered by `render_runtime_summary.py`" in template
    assert "- runtime hot spots:" in template
    assert "- coverage gate:" in template
    assert "- evaluator depth:" in template
    # Delegated Review default is a fillable not_applicable that names the slow-gate lenses.
    assert "Delegated Review: not_applicable" in template
    assert "fixture-economics, parallel-critical-path, duplicated-proof" in template

    # Dogfood: the emitted skeleton must pass the real validator unedited.
    artifact_path = repo / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(template, encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr


def test_quality_scaffold_resolves_symlinked_current_pointer_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")
    quality_dir = repo / "charness-artifacts" / "quality"
    quality_dir.mkdir(parents=True)
    target = quality_dir / "2026-05-06-quality-review.md"
    target.write_text("# Quality Review\n", encoding="utf-8")
    (quality_dir / "latest.md").symlink_to(target.name)

    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/quality/latest.md"
    assert payload["write_artifact_path"] == "charness-artifacts/quality/2026-05-06-quality-review.md"
    assert payload["write_artifact_role"] == "current_pointer_target"
    assert payload["current_pointer_symlink_target"] == "2026-05-06-quality-review.md"


def test_exported_quality_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
    export_root = tmp_path / "export"
    export_result = run_script(
        "scripts/export_plugin.py",
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(export_root),
    )
    assert export_result.returncode == 0, export_result.stderr
    plugin_root = export_root / "plugins" / "charness"
    scaffold = plugin_root / "skills" / "quality" / "scripts" / "scaffold_quality_artifact.py"

    consumer = tmp_path / "consumer"
    _write_adapter(consumer, "consumer")

    result = run_script(str(scaffold), "--repo-root", str(consumer), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_role"] == "current_pointer"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_quality_artifact.py" in payload["validator_command"]

    artifact_path = consumer / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(payload["template"], encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr

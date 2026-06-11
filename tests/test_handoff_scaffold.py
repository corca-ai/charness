from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_export_plugin = import_repo_module(__file__, "scripts.export_plugin")

SCAFFOLD = "skills/public/handoff/scripts/scaffold_handoff_artifact.py"

# Headings the scaffold must emit so an author starts from a validator-passing
# skeleton instead of rediscovering scripts/validate_handoff_artifact.py (which
# enforces an exact H2 set, a `# ... Handoff` title, and a <=70 line ceiling) by
# trial-and-error.
REQUIRED_HEADINGS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
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
    (repo / ".agents" / "handoff-adapter.yaml").write_text(
        "\n".join(["version: 1", f"repo: {repo_name}", "language: en", "output_dir: docs", ""]),
        encoding="utf-8",
    )


def test_handoff_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")

    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "docs/handoff.md"
    assert payload["artifact_role"] == "rolling"
    assert payload["write_artifact_path"] == "docs/handoff.md"
    assert payload["validator_command"].endswith("scripts/validate_handoff_artifact.py --repo-root .")

    template = payload["template"]
    assert template.startswith("# Session Handoff\n")
    for heading in REQUIRED_HEADINGS:
        assert heading in template, heading
    # `## References` must carry a markdown link the validator asserts on.
    assert "](docs/handoff.md)" in template
    # Stay under the strict 70-line ceiling out of the box.
    assert len(template.splitlines()) <= 70

    # Dogfood: the emitted skeleton must pass the real validator unedited.
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


def test_handoff_scaffold_guards_custom_title(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")
    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--title", "Auth Migration", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    # A custom title without "handoff" still yields a validator-passing `# ... Handoff` line.
    assert payload["template"].startswith("# Auth Migration Handoff\n")


def test_exported_handoff_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
    export_root = tmp_path / "export"
    manifest = _export_plugin.load_manifest(ROOT, "charness")
    plugin_root = _export_plugin.export_plugin(
        ROOT,
        export_root,
        manifest,
        "codex",
        with_marketplace=False,
    )
    scaffold = plugin_root / "skills" / "handoff" / "scripts" / "scaffold_handoff_artifact.py"

    consumer = tmp_path / "consumer"
    _write_adapter(consumer, "consumer")

    result = run_script(str(scaffold), "--repo-root", str(consumer), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_role"] == "rolling"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_handoff_artifact.py" in payload["validator_command"]

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

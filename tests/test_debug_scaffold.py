from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_scaffold_debug = import_repo_module(
    ROOT / "skills" / "public" / "debug" / "scripts" / "scaffold_debug_artifact.py",
    "skills.public.debug.scripts.scaffold_debug_artifact",
)


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

    payload = _scaffold_debug.payload_for(repo, title=None)
    assert payload["artifact_path"] == "charness-artifacts/debug/latest.md"
    assert payload["artifact_role"] == "current_pointer"
    assert payload["write_artifact_path"] == "charness-artifacts/debug/latest.md"
    assert payload["write_artifact_role"] == "current_pointer"
    assert payload["current_pointer_symlink_target"] is None
    assert payload["validator_command"].endswith("scripts/validate_debug_artifact.py --repo-root .")
    assert "# Debug Review" in payload["template"]
    assert "## Reproduction" in payload["template"]
    assert "## Detection Gap" in payload["template"]
    assert "## Sibling Search" in payload["template"]
    assert "- Mental model: TODO" in payload["template"]
    assert "decision: TODO | proof: TODO" in payload["template"]
    assert "## Seam Risk" in payload["template"]
    assert "- Interrupt ID: TODO" in payload["template"]
    assert "## Interrupt Decision" in payload["template"]
    assert "- Next Step: impl" in payload["template"]
    assert "## Verification" in payload["template"]
    assert "## Invariant Proof" in payload["template"]
    assert "- Producer Proof: n/a" in payload["template"]
    assert "- Final-Consumer Proof: n/a" in payload["template"]
    assert "- Interface-Shape Sibling Scan: n/a" in payload["template"]
    assert "- Non-Claims: n/a" in payload["template"]

    artifact_path = repo / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(payload["template"], encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr


def test_debug_scaffold_resolves_symlinked_current_pointer_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: demo", "language: en", "output_dir: charness-artifacts/debug", ""]),
        encoding="utf-8",
    )
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text("# Demo Debug\n", encoding="utf-8")
    (debug_dir / "latest.md").symlink_to(target.name)

    payload = _scaffold_debug.payload_for(repo, title=None)
    assert payload["artifact_path"] == "charness-artifacts/debug/latest.md"
    assert payload["write_artifact_path"] == "charness-artifacts/debug/debug-2026-05-06-demo.md"
    assert payload["write_artifact_role"] == "current_pointer_target"
    assert payload["current_pointer_symlink_target"] == "debug-2026-05-06-demo.md"


def test_exported_debug_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
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
    scaffold = plugin_root / "skills" / "debug" / "scripts" / "scaffold_debug_artifact.py"

    consumer = tmp_path / "consumer"
    (consumer / ".agents").mkdir(parents=True)
    (consumer / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: consumer", "language: en", "output_dir: charness-artifacts/debug", ""]),
        encoding="utf-8",
    )

    result = run_script(str(scaffold), "--repo-root", str(consumer), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_role"] == "current_pointer"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_debug_artifact.py" in payload["validator_command"]

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

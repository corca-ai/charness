from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAFFOLD = "skills/public/critique/scripts/scaffold_critique_artifact.py"


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_critique_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    # The critique adapter falls back to inferred defaults (output_dir
    # charness-artifacts/critique) with no adapter file present.
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"].startswith("charness-artifacts/critique/")
    assert payload["artifact_path"].endswith(".md")
    assert payload["artifact_role"] == "record"
    # The validator file is the plural validate_critique_artifacts.py.
    assert "validate_critique_artifacts.py" in payload["validator_command"]
    assert f"--paths {payload['write_artifact_path']}" in payload["validator_command"]

    template = payload["template"]
    # Exercise the three schemas the validator enforces when present.
    assert "## Structured Findings" in template
    assert "- F1 | bin: act-before-ship | evidence: moderate |" in template
    assert "## Reviewer Tier Evidence" in template
    assert "Host exposure state: pending-parent-spawn" in template
    assert "## Fresh-Eye Satisfaction" in template
    # The fresh-eye status must not carry the literal "blocked" token, which
    # would otherwise demand a host/tool signal citation.
    assert "blocked" not in template.lower()

    # The scaffold surfaces the validator's allowed enums at author time as an
    # inline legend, so an author substituting a value picks from the valid set
    # instead of inventing one that only fails at validate-time (the documented
    # 3-round-trip critique-authoring trap). The legend is an HTML comment so it
    # is ignored by both the validator's `- `-only parsers and markdownlint.
    assert "allowed enums (substitute only these)" in template
    assert "bundle-anyway" in template and "valid-but-defer" in template
    assert "file-issue" in template and "document" in template
    assert "allowed Host exposure state:" in template
    assert "requested_fields_sent" in template and "host-defaulted" in template
    # Same enums exposed programmatically for non-template consumers.
    enums = payload["allowed_enums"]
    assert enums["structured_findings"]["bin"]
    assert "host-confirmed:" in " ".join(enums["couplings"])

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
    assert "Validated 1 critique artifact" in validation.stdout


def test_scaffold_surfaced_enums_match_validator_frozensets(tmp_path: Path) -> None:
    """By-construction single-source-of-truth: the enums the scaffold surfaces at
    author time MUST equal the validator's enforced frozensets, so the legend can
    never silently drift from the contract it is meant to make discoverable. If a
    future change adds/renames a validator enum without updating the scaffold (or
    vice versa), this test fails instead of an author hitting a validate->fix
    round-trip on a value the scaffold told them was allowed."""
    from scripts import validate_critique_artifacts as validator

    result = run_script(SCAFFOLD, "--repo-root", str(tmp_path), "--json")
    assert result.returncode == 0, result.stderr
    enums = json.loads(result.stdout)["allowed_enums"]

    assert set(enums["structured_findings"]["bin"]) == set(validator.STRUCTURED_BINS)
    assert set(enums["structured_findings"]["evidence"]) == set(validator.STRUCTURED_EVIDENCE)
    assert set(enums["structured_findings"]["action"]) == set(validator.STRUCTURED_ACTIONS)
    assert set(enums["reviewer_tier_host_exposure_state"]) == set(
        validator.REVIEWER_TIER_HOST_STATES
    )


def test_exported_critique_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
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
    scaffold = plugin_root / "skills" / "critique" / "scripts" / "scaffold_critique_artifact.py"

    consumer = tmp_path / "consumer"
    consumer.mkdir()

    result = run_script(str(scaffold), "--repo-root", str(consumer), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_role"] == "record"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_critique_artifacts.py" in payload["validator_command"]

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
    assert "Validated 1 critique artifact" in validation.stdout

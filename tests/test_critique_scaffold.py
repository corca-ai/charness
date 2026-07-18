from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_export_plugin = import_repo_module(__file__, "scripts.export_plugin")

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

    result = run_script(SCAFFOLD, "--repo-root", str(repo))
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
    assert "## Reviewed Input Identity" in template
    assert "exact Packet SHA256" in template
    assert "- Packet path:" not in template
    # The fresh-eye status must not carry the literal "blocked" token, which
    # would otherwise demand a host/tool signal citation.
    assert "blocked" not in template.lower()
    # The boundary-ownership presence floor's section + verdict legend, with the
    # `Verdict:` deliberately NOT a typed value (same rubber-stamp rationale as
    # the fresh-eye stub — proven raw-fails-post-cutoff in
    # tests/quality_gates/test_critique_boundary_ownership_presence.py).
    assert "## Boundary Ownership" in template
    assert "single-surface" in template and "escalated-to-issue-spec" in template
    assert "boundary-ownership-brief.md" in template

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

    # The scaffold's `## Fresh-Eye Satisfaction` placeholder is deliberately
    # NOT a typed value (scaffold_critique_artifact.py's module comment) — an
    # unedited stub must not satisfy the floor, or every author could ship a
    # same-observer rubber-stamp for free. Round-trip validation here exercises
    # the FILLED-IN shape (what an author submits after the reviewer actually
    # runs), which is what "shape-by-construction" is meant to prove; the
    # raw-stub-fails-once-post-cutoff case has its own dedicated test in
    # tests/quality_gates/test_critique_fresh_eye_presence.py.
    head, heading, _ = template.partition("## Fresh-Eye Satisfaction")
    assert heading, "template must still carry the Fresh-Eye Satisfaction heading"
    # Fill BOTH date-gated floors (fresh-eye + boundary ownership); the boundary
    # section renders after Fresh-Eye Satisfaction, so the partition drops the
    # scaffold's TODO stub and we re-add a filled one. This proves the filled
    # shape validates regardless of the machine date.
    filled_in_template = (
        f"{head}{heading}\n\nparent-delegated.\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
    )

    artifact_path = repo / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(filled_in_template, encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr
    assert "Validated 1 critique artifact" in validation.stdout


def test_critique_scaffold_title_with_no_alnum_chars_falls_back_to_critique_slug(tmp_path: Path) -> None:
    # `_slug` normalizes a title down to `[a-z0-9]` runs joined by `-`, then
    # strips leading/trailing dashes. A title with no alnum characters
    # normalizes to an empty string, so `_slug` must fall back to "critique"
    # (`slug or "critique"`) rather than writing a path with an empty/blank
    # slug component.
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--title", "!!!")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["title"] == "!!!"
    assert payload["write_artifact_path"].endswith("-critique.md")
    assert payload["artifact_path"] == payload["write_artifact_path"]


def test_scaffold_surfaced_enums_match_validator_frozensets(tmp_path: Path) -> None:
    """By-construction single-source-of-truth: the enums the scaffold surfaces at
    author time MUST equal the validator's enforced frozensets, so the legend can
    never silently drift from the contract it is meant to make discoverable. If a
    future change adds/renames a validator enum without updating the scaffold (or
    vice versa), this test fails instead of an author hitting a validate->fix
    round-trip on a value the scaffold told them was allowed."""
    from scripts import validate_critique_artifacts as validator

    result = run_script(SCAFFOLD, "--repo-root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    enums = json.loads(result.stdout)["allowed_enums"]

    assert set(enums["structured_findings"]["bin"]) == set(validator.STRUCTURED_BINS)
    assert set(enums["structured_findings"]["evidence"]) == set(validator.STRUCTURED_EVIDENCE)
    assert set(enums["structured_findings"]["action"]) == set(validator.STRUCTURED_ACTIONS)
    assert set(enums["reviewer_tier_host_exposure_state"]) == set(
        validator.REVIEWER_TIER_HOST_STATES
    )
    assert set(enums["boundary_ownership"]["verdict"]) == set(validator.BOUNDARY_VERDICT_VALUES)


def test_exported_critique_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
    export_root = tmp_path / "export"
    manifest = _export_plugin.load_manifest(ROOT, "charness")
    plugin_root = _export_plugin.export_plugin(
        ROOT,
        export_root,
        manifest,
        "codex",
        with_marketplace=False,
    )
    scaffold = plugin_root / "skills" / "critique" / "scripts" / "scaffold_critique_artifact.py"

    consumer = tmp_path / "consumer"
    consumer.mkdir()

    result = run_script(str(scaffold), "--repo-root", str(consumer))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_role"] == "record"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_critique_artifacts.py" in payload["validator_command"]

    # Same fill-in-before-validate rationale as test_critique_scaffold_reports_
    # validator_and_template above: the raw stub's Fresh-Eye Satisfaction line
    # is deliberately not a typed value, so round-trip here proves the FILLED-
    # IN shape validates through the exported plugin's copy of the validator.
    head, heading, _ = payload["template"].partition("## Fresh-Eye Satisfaction")
    assert heading, "template must still carry the Fresh-Eye Satisfaction heading"
    # Same both-floors fill as the in-repo round-trip above.
    filled_in_template = (
        f"{head}{heading}\n\nparent-delegated.\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
    )

    artifact_path = consumer / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(filled_in_template, encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr
    assert "Validated 1 critique artifact" in validation.stdout

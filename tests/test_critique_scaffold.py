from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

import yaml

from runtime_bootstrap import import_repo_module
from skills.public.critique.scripts.verification_retry import build_retry_key
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]
_export_plugin = import_repo_module(__file__, "scripts.export_plugin")

SCAFFOLD = "skills/public/critique/scripts/scaffold_critique_artifact.py"


def filled_in_template(template: str) -> str:
    """The scaffold's template as an author submits it AFTER the reviewer ran.

    Both round-trips below claim to exercise the filled-in shape, and both used
    to fill only the two floors that refuse an unedited stub outright (fresh-eye
    + boundary verdict) while leaving the `## Reviewer Tier Evidence` block at its
    scaffold defaults — `Requested tier: TODO ...` and `pending-parent-spawn`. So
    the asserted-green shape was a `parent-delegated` claim sitting over a record
    saying no reviewer was ever spawned: the artifact the fresh-eye floor exists
    to refuse, pinned by the floor's own tests as correct. Filling the spawn
    record here is what makes these tests assert what their comments always said
    they asserted.
    """
    head, heading, _ = template.partition("## Fresh-Eye Satisfaction")
    assert heading, "template must still carry the Fresh-Eye Satisfaction heading"
    scope_values = {
        "Claim under test": "the scaffolded critique record binds its retry decision",
        "Changed surfaces": "critique scaffold and its validator consumer",
        "Minimum sufficient proof": "validator recomputes the retry key",
        "Deliberately omitted checks": "the subject suite is outside this fixture",
        "Verifier contract": "critique artifact validator reads this section",
        "Failure classification": "none",
        "Negative control": "none with rationale: fixture has no verifier-only claim",
        "Subject identity": "sha256:" + "1" * 64,
        "Verifier identity": "sha256:" + "2" * 64,
        "Input identity": "sha256:" + "3" * 64,
        "Failure identity": "stable:gate-failed",
        "Evidence identity": "none",
        "Retry disposition": "first-attempt",
    }
    for field, value in scope_values.items():
        head, replacements = re.subn(
            rf"^- {re.escape(field)}:.*$",
            f"- {field}: {value}",
            head,
            flags=re.MULTILINE,
        )
        assert replacements == 1, f"scaffold field not found: {field}"
    retry_key = build_retry_key(
        subject=scope_values["Subject identity"],
        verifier=scope_values["Verifier identity"],
        input_identity=scope_values["Input identity"],
        failure=scope_values["Failure identity"],
    )
    head, replacements = re.subn(r"^- Retry key:.*$", f"- Retry key: {retry_key}", head, flags=re.MULTILINE)
    assert replacements == 1
    # Replace the scaffold's tier block in place rather than appending a filled
    # one: `_section_field_map` reads the FIRST matching heading, so an appended
    # block would be shadowed by the TODO stub and the test would go on asserting
    # the unedited shape while looking like it fills it.
    before_tier, tier_heading, _rest = head.partition("## Reviewer Tier Evidence")
    assert tier_heading, "template must still carry the Reviewer Tier Evidence heading"
    # The boundary section renders after Fresh-Eye Satisfaction, so the partition
    # drops the scaffold's TODO stub and we re-add a filled one. Filling every
    # date-gated floor proves the shape validates regardless of the machine date.
    return (
        f"{before_tier}{tier_heading}\n\n"
        "- Requested tier: bounded-reviewer\n"
        "- Requested spawn fields: model, reasoning effort\n"
        "- Host exposure state: requested_fields_sent\n"
        "- Application state: n/a\n"
        "- Delivery state: findings-received\n\n"
        "- Execution mode: file-backed-worker\n\n"
        f"{heading}\n\nparent-delegated.\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
    )





def test_critique_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    # The critique adapter falls back to inferred defaults (output_dir
    # charness-artifacts/critique) with no adapter file present.
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCAFFOLD, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_path"].startswith("charness-artifacts/critique/")
    assert payload["artifact_path"].endswith(".md")
    assert payload["artifact_role"] == "record"
    # The validator file is the plural validate_critique_artifacts.py.
    assert "validate_critique_artifacts.py" in payload["validator_command"]
    assert f"--paths {payload['write_artifact_path']}" in payload["validator_command"]

    template = payload["template"]
    # Exercise the three schemas the validator enforces when present.
    assert "## Verification Scope Decision" in template
    assert "Minimum sufficient proof" in template
    assert "Verifier contract" in template
    assert "scope-too-broad | verifier-defect | subject-defect" in template
    assert "Negative control:" in template
    assert "Evidence identity:" in template
    assert "stop-no-progress" in template
    assert "## Structured Findings" in template
    assert "- F1 | bin: act-before-ship | evidence: moderate |" in template
    assert "## Reviewer Tier Evidence" in template
    assert "Host exposure state: pending-parent-spawn" in template
    assert "Execution mode: file-backed-worker" in template
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
    filled = filled_in_template(template)

    artifact_path = repo / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(filled, encoding="utf-8")
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
    payload = yaml.safe_load(result.stdout)

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
    from scripts import critique_reviewer_evidence as reviewer_shape
    from scripts import validate_critique_artifacts as validator

    result = run_script(SCAFFOLD, "--repo-root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    enums = yaml.safe_load(result.stdout)["allowed_enums"]

    assert set(enums["structured_findings"]["bin"]) == set(validator.STRUCTURED_BINS)
    assert set(enums["structured_findings"]["evidence"]) == set(validator.STRUCTURED_EVIDENCE)
    assert set(enums["structured_findings"]["action"]) == set(validator.STRUCTURED_ACTIONS)
    assert set(enums["reviewer_tier_host_exposure_state"]) == set(
        validator.REVIEWER_TIER_HOST_STATES
    )
    assert set(enums["reviewer_delivery_state"]) == set(validator.DELIVERY_STATE_VALUES)
    assert set(enums["reviewer_execution_mode"]) == set(reviewer_shape.REVIEWER_EXECUTION_MODE_VALUES)
    assert set(enums["boundary_ownership"]["verdict"]) == set(validator.BOUNDARY_VERDICT_VALUES)
    assert set(enums["verification_scope"]["failure_classification"]) == set(
        validator.VERIFICATION_FAILURE_CLASSIFICATIONS
    )
    assert set(enums["verification_scope"]["retry_disposition"]) == set(
        validator.VERIFICATION_RETRY_DISPOSITIONS
    )


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
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_role"] == "record"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_critique_artifacts.py" in payload["validator_command"]

    # Same fill-in-before-validate rationale as test_critique_scaffold_reports_
    # validator_and_template above: the raw stub's Fresh-Eye Satisfaction line
    # is deliberately not a typed value, so round-trip here proves the FILLED-
    # IN shape validates through the exported plugin's copy of the validator.
    filled = filled_in_template(payload["template"])

    artifact_path = consumer / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(filled, encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr
    assert "Validated 1 critique artifact" in validation.stdout


def test_payload_for_requires_the_title_to_be_named(tmp_path: Path) -> None:
    """`payload_for(repo_root, *, title=...)` — the `*` is a real contract.

    A surviving mutant in the #457 run turned that `*` into `/`, which still lets
    `title` be passed by keyword and so changed nothing at any current call site.
    What `/` DOES allow is a positional title: `payload_for(repo, None)` would
    silently become a title argument. Asserting the keyword-only boundary is what
    distinguishes the two, and it is the reason the marker was written.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("_critique_scaffold", ROOT / SCAFFOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    repo = tmp_path / "repo"
    repo.mkdir()
    # Keyword form is the supported call and must work.
    assert module.payload_for(repo, title=None)["write_artifact_path"]
    # Positional title must be rejected rather than silently accepted.
    try:
        module.payload_for(repo, "Some Title")
    except TypeError as exc:
        assert "positional" in str(exc)
    else:
        raise AssertionError("payload_for must not accept a positional title")

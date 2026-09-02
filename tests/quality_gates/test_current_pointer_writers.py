"""Do the current-pointer WRITERS behave: symlinks, no-ops, and refusals.

Split from `test_current_pointer_writes.py` when the 2026-08-14 YAML migration pushed
that file past its code-line cap. The split is by SUBJECT, not to dodge the cap
(D33): this file covers the surfaces that WRITE a `latest.*` pointer -- the shared
writer lib, the release artifact, the capability catalog, the HITL sync, and
`refresh_current_pointer.py` -- while the original keeps the SCANNER gate that
detects unsafe pointer writes. "Does the writer behave" and "does the gate catch a
violation" are two questions, and they were only ever in one file because they share
a subject noun.
"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.adapters.capability_catalog_artifact import persist_catalog
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

from .seeding_support import load_module
from .support import ROOT, run_script

WRITER = load_module(
    "current_pointer_writer_lib", ROOT / "scripts" / "current_pointer_writer_lib.py"
)
RELEASE_ARTIFACT = load_module(
    "publish_release_artifact",
    ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_artifact.py",
)

HITL_SYNC_REVIEW_ARTIFACT = load_script_module(
    "tests.quality_gates.current_pointer_hitl_sync_review_artifact",
    ROOT / "skills/public/hitl/scripts/sync_review_artifact.py",
)

REFRESH_CURRENT_POINTER = load_script_module(
    "refresh_current_pointer_under_test", ROOT / "scripts" / "refresh_current_pointer.py"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_hitl_sync_review_artifact(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["sync_review_artifact.py", *args])
    code = HITL_SYNC_REVIEW_ARTIFACT.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_current_pointer_writer_replaces_symlink_without_mutating_target(tmp_path: Path) -> None:
    output = tmp_path / "artifacts"
    output.mkdir()
    prior = output / "2026-05-01-prior.md"
    prior.write_text("# prior\n", encoding="utf-8")
    pointer = output / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha(prior)

    payload = WRITER.write_current_pointer_text(pointer, "# latest\n")

    assert payload["status"] == "updated"
    assert payload["pointer_was_symlink"] is True
    assert not pointer.is_symlink()
    assert pointer.read_text(encoding="utf-8") == "# latest\n"
    assert _sha(prior) == prior_sha


def test_release_artifact_does_not_follow_symlinked_latest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    release_dir = repo / "charness-artifacts" / "release"
    release_dir.mkdir(parents=True)
    prior = release_dir / "2026-05-01-prior.md"
    prior.write_text("# prior release\n", encoding="utf-8")
    pointer = release_dir / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha(prior)

    relpath = RELEASE_ARTIFACT.write_release_artifact(
        repo,
        output_dir="charness-artifacts/release",
        package_id="demo",
        previous_version="0.1.0",
        target_version="0.2.0",
        remote="origin",
        branch="main",
        quality_command="./scripts/run-quality.sh",
        release_url=None,
        update_instructions=[],
    )

    assert relpath == "charness-artifacts/release/latest.md"
    assert not pointer.is_symlink()
    text = pointer.read_text(encoding="utf-8")
    assert f"Date: {datetime.now().astimezone().date().isoformat()}" in text
    assert "target version: `0.2.0`" in text
    assert _sha(prior) == prior_sha


def test_release_artifact_records_adapter_preflight_non_claim(tmp_path: Path) -> None:
    repo = tmp_path / "repo"

    relpath = RELEASE_ARTIFACT.write_release_artifact(
        repo,
        output_dir="charness-artifacts/release",
        package_id="demo",
        previous_version="0.1.0",
        target_version="0.2.0",
        remote="origin",
        branch="main",
        quality_command="./scripts/run-quality.sh",
        release_url=None,
        update_instructions=[],
        release_adapter_preflight_payload={
            "status": "not_evaluable",
            "reason": "release adapter changed, but no previous release tag is available for field diff",
            "commands": [],
        },
    )

    text = (repo / relpath).read_text(encoding="utf-8")
    assert "## Release Adapter Preflight" in text
    assert "Release adapter focused preflight status: `not_evaluable`." in text
    # `none planned`, not the old `none executed`: this list is the PLAN, and describing a
    # plan with an execution word is the same plan-vs-run conflation the execution line
    # below exists to end. Whether anything ran is now a separate, separately-worded line.
    assert "Focused preflight commands: none planned." in text
    assert "Focused preflight execution: NOT recorded by this helper invocation" in text


def _release_record(repo: Path, **kwargs) -> str:
    relpath = RELEASE_ARTIFACT.write_release_artifact(
        repo,
        output_dir="charness-artifacts/release",
        package_id="demo",
        previous_version="0.1.0",
        target_version="0.2.0",
        remote="origin",
        branch="main",
        quality_command="./scripts/run-quality.sh",
        release_url=None,
        update_instructions=[],
        **kwargs,
    )
    return (repo / relpath).read_text(encoding="utf-8")


def test_release_record_states_an_absent_bump_rationale_rather_than_omitting_it(
    tmp_path: Path,
) -> None:
    """No section at all reads as "nothing needed explaining"."""
    text = _release_record(tmp_path / "repo")

    assert "## Bump Rationale" in text
    assert "Bump rationale: NOT recorded by this helper invocation." in text
    assert "unexplained judgment call" in text


def test_release_record_carries_the_bump_rationale_it_is_given(tmp_path: Path) -> None:
    text = _release_record(
        tmp_path / "repo",
        bump_rationale="`patch`, 6.0.0 -> 6.0.1.\nA gate catching more is a validation repair.",
    )

    assert "## Bump Rationale" in text
    assert "`patch`, 6.0.0 -> 6.0.1." in text
    assert "A gate catching more is a validation repair." in text
    assert "NOT recorded by this helper invocation" not in text.split("## Verification")[0]


def test_bump_rationale_cannot_inject_a_heading_that_moves_the_state_ledger(tmp_path: Path) -> None:
    """`audit_public_release_narrative` reads the five-entry ledger as the span from
    `## Release State` to the next `## ` line, so a heading in rationale prose would move
    where that span starts.

    `# ## Release State` is the case a single-pass demotion missed: `#+` cannot cross
    whitespace, so one substitution left `## Release State` at column 0 -- a real heading
    above the genuine one. Parameterised over the nesting shapes rather than the one
    marker, because the single-marker case is what passed while this class was open.
    """
    for injected in (
        "## Release State",
        "# ## Release State",
        "#\t## Release State",
        "  #  ## Release State",
    ):
        text = _release_record(
            tmp_path / f"repo-{abs(hash(injected))}",
            bump_rationale=f"{injected}\n- local release mutation: forged",
        )

        heading_lines = [line for line in text.splitlines() if line.startswith("## ")]
        assert heading_lines.count("## Release State") == 1, injected
        # The real ledger still terminates where the audit expects, with its own entries.
        ledger = text.split("\n## Release State\n", 1)[1].split("\n## ", 1)[0]
        assert "- local release mutation: complete" in ledger, injected
        assert "forged" not in ledger, injected


def test_bump_rationale_lines_cannot_be_read_as_record_claims_or_fences(tmp_path: Path) -> None:
    """Quoting, not a blacklist, is what makes operator prose structurally inert.

    Two readers anchor at line start and both were reachable: a `- target version: X`
    line makes `validate_current_pointer_freshness` refuse every later push for
    "disagreeing target-version claims" -- inside a record that is already tagged and
    published on the claims lane -- and an unterminated fence makes the narrative audit
    blank the rest of the record and suppress the blocker that would explain it.
    """
    text = _release_record(
        tmp_path / "repo",
        bump_rationale="- target version: 9.9.9 was rejected\n```\nrelease.py --part patch",
    )

    body = text.split("## Bump Rationale", 1)[1].split("## Verification", 1)[0]
    assert "> - target version: 9.9.9 was rejected" in body
    assert "> ```" in body
    # No line of the rationale is a claim or a fence at column 0.
    for line in body.splitlines():
        assert not line.startswith("- target version:")
        assert not line.startswith("```")
    # The only unquoted target-version claim in the record is the record's own.
    claims = [line for line in text.splitlines() if line.startswith("- target version:")]
    assert claims == ["- target version: `0.2.0`"]


def test_bump_rationale_that_renders_empty_still_says_it_is_absent(tmp_path: Path) -> None:
    """Absence is decided on the LINE LIST -- neither the raw argument nor the rendered
    text, and both of those were tried -- so a heading is never emitted over nothing.

    NON-CLAIM: a line list is not visibility. A rationale that is only an invisible
    element yields one line and renders as an empty quote bar under the heading. Not
    closed here, and the same non-claim is recorded beside the code.
    """
    for supplied in ("", "   ", "\n\n", "\n \n"):
        text = _release_record(tmp_path / f"repo-{abs(hash(supplied))}", bump_rationale=supplied)

        assert "Bump rationale: NOT recorded by this helper invocation." in text, repr(supplied)


def test_the_record_carries_the_operators_words_unaltered(tmp_path: Path) -> None:
    """The record must say what it was GIVEN. An earlier repair stripped leading `#`
    runs to make headings inert, which quoting already does -- and it silently rewrote
    hash-prefixed issue references at the start of a line into bare numbers, inside a
    document that is committed, tagged and published before any human re-reads it. It
    also manufactured the very substring it was meant to suppress: `# ## Release State`
    demoted to the literal `## Release State`.
    """
    supplied = "#4028 forced the level.\n## and a heading-looking line\n# alone"
    text = _release_record(tmp_path / "repo", bump_rationale=supplied)

    body = text.split("## Bump Rationale", 1)[1].split("## Verification", 1)[0]
    for line in supplied.splitlines():
        assert f"> {line}" in body, line
    # Inert despite being verbatim: no line of the rationale is a heading.
    assert [line for line in body.splitlines() if line.startswith("#")] == []


@pytest.mark.parametrize(
    "version_drift_check",
    [
        None,
        {"checked_version": "0.2.0"},
        {
            "checked_version": 200,
            "versioned_surfaces": ["packaging_manifest"],
            "presence_surfaces": [],
        },
    ],
)
def test_release_record_refuses_to_claim_no_drift_when_check_evidence_is_invalid(
    tmp_path: Path, version_drift_check: dict | None
) -> None:
    text = _release_record(tmp_path / "repo", version_drift_check=version_drift_check)

    assert "Version drift check: NOT recorded by this helper invocation" in text
    assert "reported no version drift" not in text


def test_release_record_binds_the_no_drift_claim_to_the_check_that_ran(tmp_path: Path) -> None:
    text = _release_record(
        tmp_path / "repo",
        version_drift_check={
            "status": "passed",
            "stage": "post-bump, pre-commit",
            "checked_version": "0.2.0",
            "versioned_surfaces": ["claude_plugin", "packaging_manifest"],
            "presence_surfaces": ["codex_marketplace_source_path"],
            "drift": [],
        },
    )

    assert (
        "reported no version drift across 2 versioned surface(s), with 1 presence-only "
        "surface(s) not version-checked against target `0.2.0`"
    ) in text
    assert "checked at `post-bump, pre-commit`" in text


def test_release_record_states_that_a_required_preflight_was_not_executed(tmp_path: Path) -> None:
    """`status: required` plus a command list is a plan, not evidence it ran."""
    text = _release_record(
        tmp_path / "repo",
        release_adapter_preflight_payload={
            "status": "required",
            "commands": [["pytest", "tests/quality_gates/test_release_backend.py", "-q"]],
        },
    )

    assert "Focused preflight execution: NOT recorded by this helper invocation" in text


def test_release_record_reports_the_executed_preflight_commands(tmp_path: Path) -> None:
    text = _release_record(
        tmp_path / "repo",
        release_adapter_preflight_payload={
            "status": "required",
            "commands": [["pytest", "tests/quality_gates/test_release_backend.py", "-q"]],
            "execution": {
                "status": "passed",
                "executed_commands": ["pytest tests/quality_gates/test_release_backend.py -q"],
            },
        },
    )

    assert "Focused preflight execution: `passed`." in text
    assert "  - executed: `pytest tests/quality_gates/test_release_backend.py -q`" in text


def test_release_record_names_the_preflight_command_that_failed(tmp_path: Path) -> None:
    """A failed preflight aborts the publish, but the record it already wrote is what
    a reader inspects afterwards; it has to name which command failed and what had
    run before it, not just that the section exists."""
    text = _release_record(
        tmp_path / "repo",
        release_adapter_preflight_payload={
            "status": "required",
            "previous_ref": "refs/tags/v0.1.0",
            "adapter_paths": [".agents/release-adapter.yaml"],
            "changed_fields": ["fresh_checkout_probes"],
            "commands": [["pytest", "a", "-q"], ["pytest", "b", "-q"]],
            "execution": {
                "status": "failed",
                "executed_commands": ["pytest a -q"],
                "failed_command": "pytest b -q",
            },
        },
    )

    assert "- Previous release ref: `refs/tags/v0.1.0`" in text
    assert "- Adapter paths in release delta:" in text
    assert "  - `.agents/release-adapter.yaml`" in text
    assert "- Changed adapter fields:" in text
    assert "  - `fresh_checkout_probes`" in text
    assert "Focused preflight execution: `failed`." in text
    assert "  - executed: `pytest a -q`" in text
    assert "  - failed: `pytest b -q`" in text
    # The token is never alone. A mutation inverting this branch survived the whole
    # suite: the record then published `execution: \`failed\`.` with no sentence saying
    # what that means, which is the "a reader who sees a status word infers the thing
    # happened" failure the branch exists to prevent.
    assert "recorded absence, not a passing preflight" in text


def test_capability_catalog_noops_when_canonical_inventory_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    inventory = {
        "public_skills": [],
        "support_skills": [],
        "support_capabilities": [],
        "integrations": [],
        "trusted_skills": [],
        "tool_recommendations": [{"id": "query-only"}],
        "tool_recommendation_query": {"mode": "task_text"},
        "support_skill_recommendations": [],
        "support_recommendation_query": None,
        "support_recommendation_note": "query note",
        "workflow_recommendations": [],
    }

    first = persist_catalog(repo, inventory)
    output = repo / "charness-artifacts" / "capability-catalog"
    first_text = (output / "latest.json").read_text(encoding="utf-8")
    second = persist_catalog(repo, inventory)

    assert first["updated"] is True
    assert second["updated"] is False
    assert (output / "latest.json").read_text(encoding="utf-8") == first_text


def test_hitl_sync_artifact_does_not_follow_symlinked_latest(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    target = repo / "docs" / "decision.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Decision\n", encoding="utf-8")

    bootstrap = run_script(
        "skills/public/hitl/scripts/bootstrap_review.py",
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-symlink",
        "--target",
        str(target),
    )
    assert bootstrap.returncode == 0, bootstrap.stderr

    hitl_dir = repo / "charness-artifacts" / "hitl"
    hitl_dir.mkdir(parents=True, exist_ok=True)
    prior = hitl_dir / "2026-05-01-prior.md"
    prior.write_text("# prior hitl record\n", encoding="utf-8")
    pointer = hitl_dir / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha(prior)

    sync = run_hitl_sync_review_artifact(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-symlink",
    )

    assert sync.returncode == 0, sync.stderr
    payload = yaml.safe_load(sync.stdout)
    assert payload["status"] == "synced"
    assert payload["artifact_path"] == "charness-artifacts/hitl/latest.md"
    assert not pointer.is_symlink()
    assert "<!-- hitl-runtime-sync" in pointer.read_text(encoding="utf-8")
    assert _sha(prior) == prior_sha


def _refresh_pointer(repo: Path, record: Path):
    """In-process, not a subprocess: the verdict under test is the returned payload
    rather than any process-level behavior."""
    return run_loaded_script_main(
        "refresh_current_pointer.py",
        REFRESH_CURRENT_POINTER,
        "--repo-root",
        str(repo),
        "--skill-id",
        "gather",
        "--record-artifact-path",
        f"charness-artifacts/gather/{record.name}",
        "--execute",
    )


def test_refresh_current_pointer_refuses_an_empty_record(tmp_path: Path) -> None:
    """Sweep row S19's destructive half, at the surface that actually owns it.

    The gather writer was fixed to refuse empty content, but `is_file()` was the only
    content check in `scripts/refresh_current_pointer.py` — the GENERIC pointer writer
    every skill routes through — and a 0-byte file passes it. Repointing `latest.md` at
    nothing destroys the asset other sessions read as current and reports
    `{"status": "updated"}`, which is the same wrong output one command over."""
    repo = tmp_path / "repo"
    gather = repo / "charness-artifacts" / "gather"
    gather.mkdir(parents=True)
    real = gather / "2026-05-09-real.md"
    real.write_text("# Real asset\n\nGathered text.\n", encoding="utf-8")
    pointer = gather / "latest.md"
    pointer.symlink_to(real.name)

    for label, body in (("empty", ""), ("whitespace-only", "  \n\n\t\n")):
        record = gather / f"2026-05-10-{label}.md"
        record.write_text(body, encoding="utf-8")
        result = _refresh_pointer(repo, record)
        assert result.returncode == 1, label
        payload = yaml.safe_load(result.stdout)
        assert payload["status"] == "blocked", label
        assert "record artifact is empty" in payload["reason"], label
        assert payload["would_update"] is False, label
        assert os.readlink(pointer) == real.name, f"pointer repointed by the {label} record"

    # Falsifiable counterpart: a record with real bytes still repoints the pointer, so
    # the refusal is about emptiness and not about the writer having been broken.
    fresh = gather / "2026-05-11-fresh.md"
    fresh.write_text("# Fresh asset\n\nMore gathered text.\n", encoding="utf-8")
    ok = _refresh_pointer(repo, fresh)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert os.readlink(pointer) == fresh.name


def test_refresh_current_pointer_refuses_an_unreadable_record(tmp_path: Path) -> None:
    """`is_file()` is not `can_read()`.

    The emptiness guard above reads the record to judge it. A record that exists but
    cannot be READ (mode 000, a stale mount, an ACL) raises inside that read, and an
    unhandled raise on the generic pointer writer either crashes the caller or — worse,
    if the read were moved after the write — leaves `latest.md` already repointed. The
    refusal has to be a payload, on the same channel as every other blocked reason, so
    the caller distinguishes "the pointer was not moved" from "the tool fell over".
    """
    repo = tmp_path / "repo"
    gather = repo / "charness-artifacts" / "gather"
    gather.mkdir(parents=True)
    real = gather / "2026-05-09-real.md"
    real.write_text("# Real asset\n\nGathered text.\n", encoding="utf-8")
    pointer = gather / "latest.md"
    pointer.symlink_to(real.name)

    unreadable = gather / "2026-05-12-unreadable.md"
    unreadable.write_text("# Has content\n\nBut cannot be read.\n", encoding="utf-8")
    unreadable.chmod(0o000)
    if os.access(unreadable, os.R_OK):  # running as root: the mode is not a barrier
        pytest.skip("cannot make a file unreadable for this user")

    try:
        result = _refresh_pointer(repo, unreadable)
    finally:
        unreadable.chmod(0o644)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert "could not be read" in payload["reason"]
    assert payload["would_update"] is False
    assert os.readlink(pointer) == real.name, "pointer repointed by an unreadable record"


@pytest.mark.parametrize(
    "hider",
    ["<script>", "<style>", "<textarea>", "<plaintext>", '<span title="unterminated', "<!--"],
)
def test_a_hiding_construct_in_the_rationale_has_nothing_below_it(
    tmp_path: Path, hider: str
) -> None:
    """Position, not a refusal, is what closes the hidden-record class.

    Each of these puts the rest of a rendered document inside something an HTML parser
    does not read as markup. The section is emitted LAST, so the rest is empty: the
    state ledger, the "NOT recorded" sentences and the claims verdict are all ABOVE it
    and survive whatever the operator wrote. This works for every renderer, including
    ones nothing in this repo can run.
    """
    text = _release_record(tmp_path / f"repo-{abs(hash(hider))}", bump_rationale=f"patch. {hider}")

    headings = [line for line in text.splitlines() if line.startswith("## ")]
    assert headings[-1] == "## Bump Rationale", headings
    ledger_start = text.index("\n## Release State\n")
    assert text.index("## Bump Rationale") > ledger_start
    for entry in ("- local release mutation:", "- branch/tag push:", "- audit narrative:"):
        assert entry in text[ledger_start : text.index("## Bump Rationale")], entry
    # And the operator's bytes are unaltered.
    assert f"> patch. {hider}" in text

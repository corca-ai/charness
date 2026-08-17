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
import importlib.util
import os
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.capability_catalog_artifact import persist_catalog
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

from .support import ROOT, run_script

WRITER_SPEC = importlib.util.spec_from_file_location(
    "current_pointer_writer_lib", ROOT / "scripts" / "current_pointer_writer_lib.py"
)
assert WRITER_SPEC is not None and WRITER_SPEC.loader is not None
WRITER = importlib.util.module_from_spec(WRITER_SPEC)
WRITER_SPEC.loader.exec_module(WRITER)

RELEASE_SPEC = importlib.util.spec_from_file_location(
    "publish_release_artifact",
    ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_artifact.py",
)
assert RELEASE_SPEC is not None and RELEASE_SPEC.loader is not None
RELEASE_ARTIFACT = importlib.util.module_from_spec(RELEASE_SPEC)
RELEASE_SPEC.loader.exec_module(RELEASE_ARTIFACT)

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
        real_host_payload={"required": False},
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
        real_host_payload={"required": False},
        release_adapter_preflight_payload={
            "status": "not_evaluable",
            "reason": "release adapter changed, but no previous release tag is available for field diff",
            "commands": [],
        },
    )

    text = (repo / relpath).read_text(encoding="utf-8")
    assert "## Release Adapter Preflight" in text
    assert "Release adapter focused preflight status: `not_evaluable`." in text
    assert "Focused preflight commands: none executed." in text


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
        real_host_payload={"required": False},
        **kwargs,
    )
    return (repo / relpath).read_text(encoding="utf-8")


def test_release_record_states_an_absent_bump_rationale_rather_than_omitting_it(tmp_path: Path) -> None:
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
    `## Release State` to the next `## ` line. A heading supplied as rationale prose
    would move where that span starts, so headings are demoted at render time."""
    text = _release_record(
        tmp_path / "repo",
        bump_rationale="## Release State\n- local release mutation: forged",
    )

    heading_lines = [line for line in text.splitlines() if line.startswith("## ")]
    assert heading_lines.count("## Release State") == 1
    # Demoted, not dropped: the operator's words survive, minus their heading marker.
    assert "Release State" in text.split("## Verification")[0]
    assert "- local release mutation: forged" in text
    assert "- local release mutation: complete" in text
    # The real ledger still terminates where the audit expects, with all five entries.
    ledger = text.split("\n## Release State\n", 1)[1].split("\n## ", 1)[0]
    assert "- local release mutation: complete" in ledger
    assert "- audit narrative:" in ledger


def test_release_record_refuses_to_claim_no_drift_when_no_check_was_recorded(tmp_path: Path) -> None:
    text = _release_record(tmp_path / "repo")

    assert "Version drift check: NOT recorded by this helper invocation" in text
    assert "reported no version drift" not in text


def test_release_record_binds_the_no_drift_claim_to_the_check_that_ran(tmp_path: Path) -> None:
    text = _release_record(
        tmp_path / "repo",
        version_drift_check={
            "status": "passed",
            "stage": "post-bump, pre-commit",
            "checked_version": "0.2.0",
            "surfaces": ["claude_plugin", "packaging_manifest"],
            "drift": [],
        },
    )

    assert "reported no version drift across 2 read surface(s) against target `0.2.0`" in text
    assert "checked at `post-bump, pre-commit`" in text


def test_release_record_states_that_a_required_preflight_was_not_executed(tmp_path: Path) -> None:
    """`status: required` plus a command list is a plan, not evidence it ran."""
    text = _release_record(
        tmp_path / "repo",
        release_adapter_preflight_payload={
            "status": "required",
            "commands": [["pytest", "tests/quality_gates/test_release_real_host.py", "-q"]],
        },
    )

    assert "Focused preflight execution: NOT recorded by this helper invocation" in text


def test_release_record_reports_the_executed_preflight_commands(tmp_path: Path) -> None:
    text = _release_record(
        tmp_path / "repo",
        release_adapter_preflight_payload={
            "status": "required",
            "commands": [["pytest", "tests/quality_gates/test_release_real_host.py", "-q"]],
            "execution": {
                "status": "passed",
                "executed_commands": ["pytest tests/quality_gates/test_release_real_host.py -q"],
            },
        },
    )

    assert "Focused preflight execution: `passed`." in text
    assert "  - executed: `pytest tests/quality_gates/test_release_real_host.py -q`" in text


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


def test_hitl_sync_artifact_does_not_follow_symlinked_latest(tmp_path: Path, monkeypatch, capsys) -> None:
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
    """In-process, not a subprocess: the boundary-bypass ratchet classifies this
    crossing as convertible, and the verdict under test is the returned payload rather
    than any process-level behavior."""
    return run_loaded_script_main(
        "refresh_current_pointer.py",
        REFRESH_CURRENT_POINTER,
        "--repo-root", str(repo),
        "--skill-id", "gather",
        "--record-artifact-path", f"charness-artifacts/gather/{record.name}",
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

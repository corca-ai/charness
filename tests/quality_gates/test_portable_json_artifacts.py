from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from string import Template
from types import SimpleNamespace
from typing import Any

from tests.script_loader import load_script_module

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]

ANNOUNCEMENT_RECORD = load_script_module(
    "tests.quality_gates.portable_record_announcement",
    ROOT / "skills/public/announcement/scripts/record_announcement.py",
)
FIND_SKILLS_LIST = load_script_module(
    "tests.quality_gates.portable_list_capabilities",
    ROOT / "skills/public/find-skills/scripts/list_capabilities.py",
)
HITL_CHECK_REVIEW_STATE = load_script_module(
    "tests.quality_gates.portable_hitl_check_review_state",
    ROOT / "skills/public/hitl/scripts/check_review_state.py",
)
HITL_SYNC_REVIEW_ARTIFACT = load_script_module(
    "tests.quality_gates.portable_hitl_sync_review_artifact",
    ROOT / "skills/public/hitl/scripts/sync_review_artifact.py",
)
RETRO_PERSIST_ARTIFACT = load_script_module(
    "tests.quality_gates.portable_retro_persist_artifact",
    ROOT / "skills/public/retro/scripts/persist_retro_artifact.py",
)
MARKDOWN_PREVIEW_RENDER = load_script_module(
    "tests.quality_gates.portable_render_markdown_preview",
    ROOT / "skills/support/markdown-preview/scripts/render_markdown_preview.py",
)


def _load_script_module(module_name: str) -> Any:
    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return __import__(f"scripts.{module_name}", fromlist=["build_summary"])


def run_loaded_script(monkeypatch, capsys, script_name: str, module: object, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [script_name, *args])
    returncode = 0
    stderr_suffix = ""
    try:
        returncode = module.main() or 0
    except SystemExit as exc:
        if isinstance(exc.code, int):
            returncode = exc.code
        elif exc.code is None:
            returncode = 0
        else:
            returncode = 1
            stderr_suffix = f"{exc.code}\n"
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err + stderr_suffix)


def _assert_no_repo_absolute_path(payload: object, repo: Path) -> None:
    rendered = json.dumps(payload, ensure_ascii=False)
    assert str(repo.resolve()) not in rendered


def test_find_skills_inventory_persists_portable_adapter_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    agents_dir = repo / ".agents"
    skill_dir.mkdir(parents=True)
    agents_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: demo\ndescription: Demo.\n---\n\n# Demo\n", encoding="utf-8")
    (agents_dir / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/find-skills",
                "trusted_skill_roots: []",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_loaded_script(
        monkeypatch,
        capsys,
        "list_capabilities.py",
        FIND_SKILLS_LIST,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["adapter"]["path"] == ".agents/find-skills-adapter.yaml"
    latest = json.loads((repo / "charness-artifacts" / "find-skills" / "latest.json").read_text(encoding="utf-8"))
    assert latest["inventory"]["adapter"]["path"] == ".agents/find-skills-adapter.yaml"
    _assert_no_repo_absolute_path(latest, repo)


def test_markdown_preview_manifest_omits_absolute_repo_root(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n", encoding="utf-8")

    result = run_loaded_script(
        monkeypatch,
        capsys,
        "render_markdown_preview.py",
        MARKDOWN_PREVIEW_RENDER,
        "--repo-root",
        str(repo),
        "--file",
        "README.md",
        "--artifact-dir",
        ".artifacts/preview",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["repo"] == "repo"
    assert "repo_root" not in payload
    manifest = json.loads((repo / ".artifacts" / "preview" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["artifact_dir"] == ".artifacts/preview"
    _assert_no_repo_absolute_path(manifest, repo)


def test_announcement_record_normalizes_artifact_path_and_stdout(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "announcement" / "latest.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Announcement\n", encoding="utf-8")

    result = run_loaded_script(
        monkeypatch,
        capsys,
        "record_announcement.py",
        ANNOUNCEMENT_RECORD,
        "--repo-root",
        str(repo),
        "--head-commit",
        "abc123",
        "--artifact-path",
        str(artifact),
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ".charness/announcement/announcements.jsonl"
    record = json.loads((repo / ".charness" / "announcement" / "announcements.jsonl").read_text(encoding="utf-8"))
    assert record["artifact_path"] == "charness-artifacts/announcement/latest.md"
    assert record["artifact_path_provenance"]["kind"] == "repo-root-relative"
    _assert_no_repo_absolute_path(record, repo)


def test_hitl_bootstrap_normalizes_target_and_output_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    target = repo / "docs" / "decision.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Decision\n", encoding="utf-8")

    result = run_script(
        "skills/public/hitl/scripts/bootstrap_review.py",
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-test",
        "--target",
        str(target),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["session_dir"] == ".charness/hitl/runtime/hitl-test"
    assert payload["require_explicit_apply"] is True
    assert payload["apply_mode"] == "explicit-after-all-chunks"
    state = (repo / payload["state_file"]).read_text(encoding="utf-8")
    assert "require_explicit_apply: true" in state
    assert "apply_mode: explicit-after-all-chunks" in state
    assert "accepted_rules: []" in state
    assert "active_rules_applied: []" in state
    assert "target_cursor_checked: false" in state
    assert 'target_cursor_check_result: ""' in state
    assert "applied_rewrite_review_status: inactive" in state
    assert 'pending_rewrite_chunk_id: ""' in state
    assert 'pending_rewrite_source_anchor: ""' in state
    assert "full_target_review_item_id: full_target_review" in state
    assert "full_target_review_status: pending_after_chunks" in state
    scratchpad = (repo / payload["scratchpad"]).read_text(encoding="utf-8")
    assert "## Pre-Edit Constraints" in scratchpad
    assert "- Accepted Rules: []" in scratchpad
    assert "- Active Rules Applied:" in scratchpad
    assert "- Target/Cursor Checked: false" in scratchpad
    assert "Target/Cursor Check Result:" in scratchpad
    assert "## Applied Rewrite Review" in scratchpad
    assert "inactive until a reviewer-requested rewrite is applied" in scratchpad
    assert "applied chunk excerpt with line or hunk anchor" in scratchpad
    assert "- Pending Chunk ID:" in scratchpad
    assert "- Source Anchor:" in scratchpad
    assert "- Applied Excerpt:" in scratchpad
    assert "- Verification:" in scratchpad
    assert "- Review Result:" in scratchpad
    assert "## Full Target Review" in scratchpad
    assert "Review the full updated target before accepting the target as complete." in scratchpad
    updated_line = next(line for line in scratchpad.splitlines() if line.startswith("- Updated: "))
    template = Template(
        (
            ROOT
            / "skills"
            / "public"
            / "hitl"
            / "scripts"
            / "templates"
            / "scratchpad.md.txt"
        ).read_text(encoding="utf-8")
    )
    assert scratchpad == template.substitute(
        session_id="hitl-test",
        updated=updated_line.removeprefix("- Updated: "),
        portable_target="docs/decision.md",
        base_ref="main",
        scope="all",
        mode="explicit-after-all-chunks",
    )
    queue = json.loads((repo / payload["queue_file"]).read_text(encoding="utf-8"))
    assert queue["target"] == "docs/decision.md"
    assert queue["target_provenance"]["kind"] == "repo-root-relative"
    assert queue["require_explicit_apply"] is True
    assert queue["apply_mode"] == "explicit-after-all-chunks"
    assert queue["applied_rewrite_review"] == {
        "id": "applied_rewrite_review",
        "type": "applied_rewrite_review_policy",
        "status": "inactive_until_reviewer_requested_rewrite_is_applied",
        "requires_applied_excerpt_before_cursor_advance": True,
        "anchor_preference": "line-or-hunk-anchor",
        "verification_role": "secondary",
        "decision_needed": "Decide whether the rewritten chunk is accepted or needs another revision.",
    }
    assert queue["full_target_review"] == {
        "id": "full_target_review",
        "type": "full_target_review",
        "status": "pending_after_chunks",
        "target": "docs/decision.md",
        "scope": "all",
        "requires_whole_target_judgment": True,
        "activation_condition": "all_chunks_reviewed_and_target_edit_applied_or_staged",
        "decision_needed": "Review the full updated target before accepting the target as complete.",
    }
    assert queue["completion_item_ids"] == ["full_target_review"]
    assert queue["items"] == [queue["full_target_review"]]
    _assert_no_repo_absolute_path(payload, repo)
    _assert_no_repo_absolute_path(queue, repo)


def test_hitl_bootstrap_surfaces_adapter_apply_mode(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "hitl-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/hitl",
                "require_explicit_apply: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/hitl/scripts/bootstrap_review.py",
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-apply-mode",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["require_explicit_apply"] is False
    assert payload["apply_mode"] == "accepted-chunk-or-final-apply-boundary"
    state = (repo / payload["state_file"]).read_text(encoding="utf-8")
    assert "require_explicit_apply: false" in state
    assert "apply_mode: accepted-chunk-or-final-apply-boundary" in state


def test_hitl_sync_review_artifact_projects_runtime_and_checks_freshness(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    target = repo / "docs" / "decision.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Decision\n", encoding="utf-8")

    bootstrap = run_script(
        "skills/public/hitl/scripts/bootstrap_review.py",
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-sync",
        "--target",
        str(target),
    )

    assert bootstrap.returncode == 0, bootstrap.stderr
    payload = json.loads(bootstrap.stdout)
    state_path = repo / payload["state_file"]
    state = state_path.read_text(encoding="utf-8")
    state_path.write_text(
        state.replace("accepted_rules: []", "accepted_rules:\n  - avoid summary-only chunks")
        .replace('last_presented_chunk_id: ""', "last_presented_chunk_id: C1")
        .replace("target_cursor_checked: false", "target_cursor_checked: true")
        .replace('target_cursor_check_result: ""', "target_cursor_check_result: C1 docs/decision.md lines 1-1 epoch 1"),
        encoding="utf-8",
    )

    sync = run_loaded_script(
        monkeypatch,
        capsys,
        "sync_review_artifact.py",
        HITL_SYNC_REVIEW_ARTIFACT,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-sync",
    )

    assert sync.returncode == 0, sync.stderr
    sync_payload = json.loads(sync.stdout)
    assert sync_payload["status"] == "synced"
    assert sync_payload["artifact_path"] == "charness-artifacts/hitl/latest.md"
    artifact = (repo / "charness-artifacts" / "hitl" / "latest.md").read_text(encoding="utf-8")
    assert "<!-- hitl-runtime-sync" in artifact
    assert "accepted_rules_digest:" in artifact
    assert "queue_items_digest:" in artifact
    assert "queue_state_digest:" in artifact
    assert "approval_state_digest:" in artifact
    assert "Synced From Session: `hitl-sync`" in artifact
    assert "Target: `docs/decision.md`" in artifact
    assert "- avoid summary-only chunks" in artifact
    assert "Target/Cursor Checked: `True`" in artifact
    assert "Next Chunk To Present" in artifact
    assert ".charness/hitl/runtime/hitl-sync/state.yaml" in artifact

    check = run_loaded_script(
        monkeypatch,
        capsys,
        "sync_review_artifact.py",
        HITL_SYNC_REVIEW_ARTIFACT,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-sync",
        "--check",
    )

    assert check.returncode == 0, check.stderr
    assert json.loads(check.stdout)["status"] == "current"
    state_path.write_text(state_path.read_text(encoding="utf-8").replace("target: docs/decision.md", "target: docs/other.md"), encoding="utf-8")
    stale = run_loaded_script(
        monkeypatch,
        capsys,
        "sync_review_artifact.py",
        HITL_SYNC_REVIEW_ARTIFACT,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-sync",
        "--check",
    )

    assert stale.returncode == 1
    assert json.loads(stale.stdout)["status"] == "stale"
    assert "target mismatch" in stale.stdout
    _assert_no_repo_absolute_path(sync_payload, repo)


def test_hitl_check_review_state_blocks_unsafe_transitions(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    bootstrap = run_script(
        "skills/public/hitl/scripts/bootstrap_review.py",
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-check",
    )

    assert bootstrap.returncode == 0, bootstrap.stderr
    payload = json.loads(bootstrap.stdout)
    state_path = repo / payload["state_file"]
    blocked = run_loaded_script(
        monkeypatch,
        capsys,
        "check_review_state.py",
        HITL_CHECK_REVIEW_STATE,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-check",
        "--phase",
        "cursor-advance",
    )

    assert blocked.returncode == 1
    blocked_payload = json.loads(blocked.stdout)
    assert blocked_payload["status"] == "blocked"
    assert "target_cursor_checked must be true before editing or advancing" in blocked.stdout

    state = state_path.read_text(encoding="utf-8")
    state_path.write_text(
        state.replace("accepted_rules: []", "accepted_rules:\n  - keep public terms")
        .replace("active_rules_applied: []", "active_rules_applied:\n  - keep public terms")
        .replace("target_cursor_checked: false", "target_cursor_checked: true")
        .replace('target_cursor_check_result: ""', "target_cursor_check_result: git-diff C1 item C1 lines 1-5 epoch 1")
        .replace("applied_rewrite_review_status: inactive", "applied_rewrite_review_status: pending"),
        encoding="utf-8",
    )
    pending = run_loaded_script(
        monkeypatch,
        capsys,
        "check_review_state.py",
        HITL_CHECK_REVIEW_STATE,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-check",
        "--phase",
        "cursor-advance",
    )

    assert pending.returncode == 1
    assert "applied_rewrite_review_status is pending" in pending.stdout
    state_path.write_text(
        state_path.read_text(encoding="utf-8").replace(
            "target_cursor_check_result: git-diff C1 item C1 lines 1-5 epoch 1",
            "target_cursor_check_result: C1 item C1 epoch 1",
        ),
        encoding="utf-8",
    )
    malformed = run_loaded_script(
        monkeypatch,
        capsys,
        "check_review_state.py",
        HITL_CHECK_REVIEW_STATE,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-check",
        "--phase",
        "pre-edit",
    )

    assert malformed.returncode == 1
    assert "must name the current target" in malformed.stdout
    assert "must name line bounds" in malformed.stdout
    state_path.write_text(
        state_path.read_text(encoding="utf-8").replace(
            "target_cursor_check_result: C1 item C1 epoch 1",
            "target_cursor_check_result: git-diff C1 item C1 lines 1-5 epoch 1",
        ).replace(
            "applied_rewrite_review_status: pending", "applied_rewrite_review_status: accepted"
        ),
        encoding="utf-8",
    )
    passed = run_loaded_script(
        monkeypatch,
        capsys,
        "check_review_state.py",
        HITL_CHECK_REVIEW_STATE,
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-check",
        "--phase",
        "cursor-advance",
    )

    assert passed.returncode == 0, passed.stderr
    assert json.loads(passed.stdout)["status"] == "pass"


def test_retro_snapshot_sanitizes_path_fields(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot_file = repo / "snapshot.json"
    snapshot_file.write_text(json.dumps({"source_path": str(repo / "docs" / "notes.md")}), encoding="utf-8")
    markdown_file = repo / "retro.md"
    markdown_file.write_text("# Retro\n", encoding="utf-8")
    (repo / ".agents").mkdir()
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/retro",
                "snapshot_path: .charness/retro/latest.json",
                "evidence_paths: []",
                "metrics_commands: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_loaded_script(
        monkeypatch,
        capsys,
        "persist_retro_artifact.py",
        RETRO_PERSIST_ARTIFACT,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "session.md",
        "--markdown-file",
        str(markdown_file),
        "--snapshot-file",
        str(snapshot_file),
    )

    assert result.returncode == 0, result.stderr
    snapshot = json.loads((repo / ".charness" / "retro" / "latest.json").read_text(encoding="utf-8"))
    assert snapshot["source_path"] == "docs/notes.md"
    _assert_no_repo_absolute_path(snapshot, repo)


def test_cautilus_summaries_sanitize_diagnostics_and_external_worktree_paths(tmp_path: Path) -> None:
    build_cautilus_scenario_summary = _load_script_module("eval_cautilus_scenarios").build_summary
    build_chatbot_proposals_summary = _load_script_module("eval_cautilus_chatbot_proposals").build_summary
    build_chatbot_compare_summary = _load_script_module("eval_cautilus_chatbot_compare").build_summary
    repo = tmp_path / "repo"
    repo.mkdir()
    completed = subprocess.CompletedProcess(
        args=["python3", "scripts/run_evals.py"],
        returncode=0,
        stdout=f"checked {repo / 'AGENTS.md'}",
        stderr=f"warning {repo / 'docs' / 'guide.md'}",
    )
    scenario_summary = build_cautilus_scenario_summary(
        repo_root=repo,
        mode="held_out",
        profile="evaluator-required",
        baseline_ref="origin/main",
        samples=1,
        command=completed,
        skills=[{"skill_id": "demo", "scenario_ids": ["demo-case"]}],
    )
    assert scenario_summary["run_evals"]["stdout"] == "checked ./AGENTS.md"
    assert scenario_summary["run_evals"]["stderr"] == "warning ./docs/guide.md"

    proposals_summary = build_chatbot_proposals_summary(
        repo_root=repo,
        input_path=repo / "evals" / "inputs.json",
        input_packet={"proposalCandidates": [{"proposalKey": "one", "tags": ["demo"]}]},
        proposals_packet={
            "proposals": [{"proposalKey": "one", "source_path": str(repo / "skills" / "demo" / "SKILL.md")}],
            "attentionView": {
                "proposalKeys": ["one"],
                "reasonCodesByProposalKey": {"one": ["demo"]},
                "selectedCount": 1,
                "truncated": False,
                "fallbackUsed": False,
            },
            "proposalTelemetry": {},
            "schemaVersion": "cautilus.scenario_proposals.v1",
        },
        command=completed,
    )
    assert proposals_summary["proposals_packet"]["proposals"][0]["source_path"] == "skills/demo/SKILL.md"
    _assert_no_repo_absolute_path(proposals_summary, repo)

    external = tmp_path / "external-worktree"
    external.mkdir()
    compare_summary = build_chatbot_compare_summary(
        baseline_repo=external,
        candidate_repo=repo,
        baseline_summary=proposals_summary,
        candidate_summary=proposals_summary,
    )
    assert compare_summary["baseline_repo"] == "external-baseline-worktree:external-worktree"
    assert compare_summary["baseline_repo_provenance"] == {"kind": "external-path", "basename": "external-worktree"}
    assert compare_summary["candidate_repo"] == "external-candidate-worktree:repo"
    assert compare_summary["candidate_repo_provenance"] == {"kind": "external-path", "basename": "repo"}
    _assert_no_repo_absolute_path(compare_summary, tmp_path)

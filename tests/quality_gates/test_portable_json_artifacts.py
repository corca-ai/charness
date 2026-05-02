from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]


def _load_script_module(module_name: str) -> Any:
    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return __import__(f"scripts.{module_name}", fromlist=["build_summary"])


def _assert_no_repo_absolute_path(payload: object, repo: Path) -> None:
    rendered = json.dumps(payload, ensure_ascii=False)
    assert str(repo.resolve()) not in rendered


def test_find_skills_inventory_persists_portable_adapter_paths(tmp_path: Path) -> None:
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

    result = run_script("skills/public/find-skills/scripts/list_capabilities.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["adapter"]["path"] == ".agents/find-skills-adapter.yaml"
    latest = json.loads((repo / "charness-artifacts" / "find-skills" / "latest.json").read_text(encoding="utf-8"))
    assert latest["inventory"]["adapter"]["path"] == ".agents/find-skills-adapter.yaml"
    _assert_no_repo_absolute_path(latest, repo)


def test_markdown_preview_manifest_omits_absolute_repo_root(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n", encoding="utf-8")

    result = run_script(
        "skills/support/markdown-preview/scripts/render_markdown_preview.py",
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


def test_announcement_record_normalizes_artifact_path_and_stdout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "announcement" / "latest.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Announcement\n", encoding="utf-8")

    result = run_script(
        "skills/public/announcement/scripts/record_announcement.py",
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
    queue = json.loads((repo / payload["queue_file"]).read_text(encoding="utf-8"))
    assert queue["target"] == "docs/decision.md"
    assert queue["target_provenance"]["kind"] == "repo-root-relative"
    assert queue["require_explicit_apply"] is True
    assert queue["apply_mode"] == "explicit-after-all-chunks"
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


def test_hitl_report_mode_does_not_turn_suggestions_into_default_approval(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "cautilus-review",
                "title": "Cautilus Review",
                "agent_next_step": "Apply only explicit human decisions.",
                "items": [
                    {
                        "id": "claim-1",
                        "question": "Should the claim be accepted?",
                        "why": "The next agent may otherwise treat a recommendation as approval.",
                        "suggested_decision": "approve",
                        "evidence_links": [{"label": "Report", "path": "report.md"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(packet))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    decisions = json.loads((repo / payload["decisions_path"]).read_text(encoding="utf-8"))
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert payload["reviewed_item_count"] == 0
    assert decisions["items"] == []
    assert decisions["dropped_unreviewed_item_ids"] == ["claim-1"]
    assert 'value="unreviewed" checked' in html
    assert "Suggested action" in html
    assert "Apply only explicit human decisions." in html
    assert "Report" in html
    assert "Defaults stay unreviewed" in html
    _assert_no_repo_absolute_path(payload, repo)
    _assert_no_repo_absolute_path(decisions, repo)


def test_hitl_report_mode_saves_only_touched_decisions_and_explains_tables(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    review = repo / "review.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "table-review",
                "title": "Table Review",
                "items": [
                    {
                        "id": "matrix-1",
                        "question": "Which row needs follow-up?",
                        "why": "The reviewer should not have to decode the table unaided.",
                        "suggested_decision": "approve",
                        "table": [
                            {"Claim": "routing", "Status": "weak", "Reason": "missing evidence"},
                            {"Claim": "storage", "Status": "ok", "Reason": "artifact linked"},
                        ],
                    },
                    {
                        "id": "matrix-2",
                        "question": "Should this stay deferred?",
                        "why": "Untouched items should not become approvals.",
                        "suggested_decision": "approve",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    review.write_text(
        json.dumps({"items": [{"id": "matrix-1", "decision": "request_changes", "comment": "Fix routing."}]}),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(packet),
        "--review-input",
        str(review),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    decisions = json.loads((repo / payload["decisions_path"]).read_text(encoding="utf-8"))
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert [item["id"] for item in decisions["items"]] == ["matrix-1"]
    assert decisions["items"][0]["decision"] == "request_changes"
    assert decisions["items"][0]["suggested_decision"] == "approve"
    assert decisions["items"][0]["suggestion_display_only"] is True
    assert decisions["items"][0]["table_rows"] == [
        {"Claim": "routing", "Status": "weak", "Reason": "missing evidence"},
        {"Claim": "storage", "Status": "ok", "Reason": "artifact linked"},
    ]
    assert decisions["dropped_unreviewed_item_ids"] == ["matrix-2"]
    assert "Claim: routing; Status: weak; Reason: missing evidence" in html
    assert "<summary>Raw table</summary>" in html
    _assert_no_repo_absolute_path(payload, repo)
    _assert_no_repo_absolute_path(decisions, repo)


def test_hitl_report_mode_rejects_duplicate_ids_and_sanitizes_report_html(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    duplicate_packet = repo / "duplicate.json"
    unsafe_packet = repo / "unsafe.json"
    duplicate_packet.write_text(
        json.dumps({"items": [{"id": "same", "question": "One"}, {"id": "same", "question": "Two"}]}),
        encoding="utf-8",
    )
    unsafe_packet.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": "x</script><script>alert(1)</script>",
                        "question": "Is this safe?",
                        "evidence_links": [{"label": "Bad", "href": "javascript:alert(1)"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    duplicate = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(duplicate_packet))
    unsafe = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(unsafe_packet))

    assert duplicate.returncode == 1
    assert "duplicate item id" in duplicate.stderr
    assert unsafe.returncode == 0, unsafe.stderr
    payload = json.loads(unsafe.stdout)
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert 'href="javascript:' not in html
    assert "querySelectorAll(\".card\")" in html
    assert "x&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_retro_snapshot_sanitizes_path_fields(tmp_path: Path) -> None:
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

    result = run_script(
        "skills/public/retro/scripts/persist_retro_artifact.py",
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

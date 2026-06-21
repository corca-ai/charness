from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

import pytest

from scripts.adapter_lib import load_yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = _load("achieve_adapter_policy")
closeout = _load("goal_artifact_closeout_evidence")
ADAPTER_CONTRACT = ROOT / "skills" / "public" / "achieve" / "references" / "adapter-contract.md"


def _write(repo: Path, rel: str, text: str) -> Path:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_adapter_uses_audit_only_defaults(tmp_path: Path) -> None:
    adapter = policy.load_adapter(tmp_path)

    assert adapter["found"] is False
    assert adapter["valid"] is True
    assert adapter["data"]["closeout_publication"]["default_mode"] == "audit-only"
    assert adapter["data"]["closeout_publication"]["issue_closeout_carrier"] == "none"
    assert adapter["data"]["auto_retro"]["disposition_floor"] == "review-required"
    assert adapter["data"]["scaffold"]["draft_active_frame_lines"]


def test_repo_adapter_can_declare_handoff_only_direct_commit_policy(tmp_path: Path) -> None:
    _write(
        tmp_path,
        ".agents/achieve-adapter.yaml",
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "closeout_publication:",
                "  default_mode: handoff-only",
                "  issue_closeout_carrier: direct-commit",
                "  require_draft_validation: true",
                '  draft_validation_command_template: "python3 skills/public/issue/scripts/issue_tool.py validate-closeout-draft --repo-root . --repo owner/repo --number {issue_number} --classification {classification} --carrier direct-commit --commit-message-file {commit_message_file}"',
                "auto_retro:",
                "  disposition_floor: review-required",
                "  valid_dispositions:",
                "    - applied",
                "    - issue",
                "scaffold:",
                "  draft_active_frame_lines:",
                "    - '- Current slice: real draft/backlog awaiting activation.'",
                "    - '- Next action: activate with `/goal @{goal_rel}` after review.'",
            ]
        )
        + "\n",
    )

    report = policy.closeout_policy_report(tmp_path)

    assert report["found"] is True
    assert report["valid"] is True
    assert report["publication_default"] == "handoff-only"
    assert report["issue_closeout_carrier"] == "direct-commit"
    assert report["draft_validation_required"] is True
    assert report["auto_retro_valid_dispositions"] == ["applied", "issue"]

    adapter = policy.load_adapter(tmp_path)
    assert adapter["data"]["scaffold"]["draft_active_frame_lines"][0].startswith("- Current slice: real draft")


def test_discussion_deploy_vocab_resolves_from_adapter_else_empty(tmp_path: Path) -> None:
    # WS-3b b-ii: the discussion-gate deploy vocabulary is adapter-provided. No
    # adapter -> [] (the discussion gate then uses its English default).
    assert policy.resolve_discussion_deploy_vocab(tmp_path) == []
    _write(
        tmp_path,
        ".agents/achieve-adapter.yaml",
        "version: 1\ndiscussion_deploy_vocab:\n  - rollout\n  - hotfix\n",
    )
    adapter = policy.load_adapter(tmp_path)
    assert adapter["valid"] is True
    assert adapter["data"]["discussion_deploy_vocab"] == ["rollout", "hotfix"]
    assert policy.resolve_discussion_deploy_vocab(tmp_path) == ["rollout", "hotfix"]


def test_adapter_contract_yaml_documents_top_level_scaffold() -> None:
    text = ADAPTER_CONTRACT.read_text(encoding="utf-8")
    match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    assert match is not None

    data = load_yaml(match.group(1))

    assert "scaffold" in data
    assert "scaffold" not in data["auto_retro"]
    assert data["scaffold"]["draft_active_frame_lines"][0].startswith("- Current slice: real draft")


def test_scaffold_frame_lines_must_be_nonempty_and_not_headings(tmp_path: Path) -> None:
    _write(
        tmp_path,
        ".agents/achieve-adapter.yaml",
        "\n".join(
            [
                "version: 1",
                "scaffold:",
                "  draft_active_frame_lines:",
                "    - '## Not a frame line'",
            ]
        )
        + "\n",
    )

    adapter = policy.load_adapter(tmp_path)

    assert adapter["valid"] is False
    assert "scaffold.draft_active_frame_lines" in adapter["errors"][0]


def test_scaffold_frame_lines_must_not_be_empty(tmp_path: Path) -> None:
    _write(
        tmp_path,
        ".agents/achieve-adapter.yaml",
        "\n".join(
            [
                "version: 1",
                "scaffold:",
                "  draft_active_frame_lines: []",
            ]
        )
        + "\n",
    )

    adapter = policy.load_adapter(tmp_path)

    assert adapter["valid"] is False
    assert "must not be empty" in adapter["errors"][0]


def test_scaffold_loader_reports_missing_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    policy._scaffold = None
    original_spec_from_file_location = importlib.util.spec_from_file_location

    def missing_scaffold(name: str, location: Path):
        if location.name == "goal_artifact_scaffold.py":
            return None
        return original_spec_from_file_location(name, location)

    monkeypatch.setattr(policy.importlib.util, "spec_from_file_location", missing_scaffold)

    with pytest.raises(ImportError, match="goal_artifact_scaffold.py not found"):
        policy._load_scaffold()


def test_direct_commit_policy_requires_rehearsal_command_shape(tmp_path: Path) -> None:
    _write(
        tmp_path,
        ".agents/achieve-adapter.yaml",
        "\n".join(
            [
                "version: 1",
                "closeout_publication:",
                "  issue_closeout_carrier: direct-commit",
                "  require_draft_validation: true",
                '  draft_validation_command_template: "python3 issue.py validate-closeout-draft --carrier direct-commit"',
            ]
        )
        + "\n",
    )

    adapter = policy.load_adapter(tmp_path)

    assert adapter["valid"] is False
    assert "--commit-message-file" in adapter["errors"][0]


def test_complete_evidence_surfaces_adapter_policy_and_blocks_invalid_adapter(tmp_path: Path) -> None:
    created = "2026-05-29"
    slug = "adapter-policy"
    _write(tmp_path, f"charness-artifacts/retro/{created}-{slug}.md", "# Retro\n\n## Next Improvements\n\nnone\n")
    _write(tmp_path, f"charness-artifacts/probe/{created}-{slug}.json", '{"host":"test"}\n')
    _write(
        tmp_path,
        ".agents/achieve-adapter.yaml",
        "\n".join(
            [
                "version: 1",
                "closeout_publication:",
                "  default_mode: not-a-mode",
            ]
        )
        + "\n",
    )
    goal = (
        "# Achieve Goal: Adapter policy\n\n"
        f"Status: complete\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{slug}.md`\n\n"
        "## Final Verification\n\n"
        f"Retro: charness-artifacts/retro/{created}-{slug}.md\n"
        f"Host log probe: charness-artifacts/probe/{created}-{slug}.json\n\n"
        "## Auto-Retro\n\napplied: checked adapter policy\n"
    )

    report = closeout.check_complete_evidence(tmp_path, goal)

    assert report["achieve_adapter_policy"]["valid"] is False
    assert report["achieve_adapter_policy"]["errors"]
    assert report["ok"] is False


def test_resolve_adapter_cli_outputs_adapter_payload(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "python3",
            str(SCRIPTS / "resolve_adapter.py"),
            "--repo-root",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["found"] is False
    assert payload["data"]["closeout_publication"]["default_mode"] == "audit-only"


def test_init_adapter_scaffolds_resolvable_policy(tmp_path: Path) -> None:
    subprocess.run(
        [
            "python3",
            str(SCRIPTS / "init_adapter.py"),
            "--repo-root",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = policy.load_adapter(tmp_path)
    assert payload["found"] is True
    assert payload["valid"] is True
    data = payload["data"]
    assert data["closeout_publication"]["issue_closeout_carrier"] == "direct-commit"
    # Pin the irreversible-boundary defaults the scaffold ships: silently flipping
    # any of these to False removes a human-confirmation / post-publish-verify gate
    # at a publish boundary (a contract downgrade, not a refactor).
    assert data["version"] == 1
    assert data["closeout_publication"]["require_draft_validation"] is True
    assert data["closeout_publication"]["require_post_publication_verify"] is True
    assert data["closeout_publication"]["publish_requires_user_confirmation"] is True
    assert data["auto_retro"]["allow_host_blocked_disposition_review_skip"] is True
    assert data["auto_retro"]["allow_none_optout"] is True

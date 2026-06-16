from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = _load("achieve_adapter_policy")
closeout = _load("goal_artifact_closeout_evidence")


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
    assert payload["data"]["closeout_publication"]["issue_closeout_carrier"] == "direct-commit"

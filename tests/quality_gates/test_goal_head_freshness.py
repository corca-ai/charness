from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

from tests.quality_gates.support import run_script

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hf = _load("goal_artifact_head_freshness")


def _goal_with_context(context: str) -> str:
    sections = (
        "## Goal\nx\n\n"
        "## Non-Goals\nx\n\n"
        "## Boundaries\nx\n\n"
        "## User Acceptance\nx\n\n"
        "## Agent Verification Plan\nx\n\n"
        "## Slice Plan\nx\n\n"
        "## Slice Log\nx\n\n"
        "## Off-Goal Findings\nx\n\n"
        "## Final Verification\nx\n\n"
        "## User Verification Instructions\nx\n\n"
        "## Auto-Retro\nx\n\n"
        "## Context Sources\nx\n\n"
        "## Interview Decisions\nx\n\n"
        "## Plan Critique Findings\nx\n"
    )
    return (
        "# Achieve Goal: T\n\n"
        "Status: active\n"
        "Activation: `/goal @charness-artifacts/goals/2026-05-31-t.md`\n\n"
        f"{context}\n\n"
        f"{sections}"
    )


def _init_git(repo: Path) -> str:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "--allow-empty", "-m", "seed"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def test_current_head_wording_rejects_stale_immutable_sha() -> None:
    report = hf.check_head_freshness(
        "Context: current HEAD is `deadbee` after the final verification.\n",
        head_sha="abc1234567890",
    )

    assert report["ok"] is False
    assert report["findings"][0]["line"] == 1
    assert report["findings"][0]["stale_shas"] == ["deadbee"]


def test_before_prefix_does_not_exempt_current_head_claim() -> None:
    report = hf.check_head_freshness(
        "Before calling completion, current HEAD is `deadbee`.\n",
        head_sha="abc1234567890",
    )

    assert report["ok"] is False


def test_current_head_wording_accepts_matching_short_sha() -> None:
    report = hf.check_head_freshness(
        "Context: HEAD is `abc1234` after closeout.\n",
        head_sha="abc1234567890",
    )

    assert report["ok"] is True


def test_base_sha_on_same_line_does_not_bind_to_head_claim() -> None:
    report = hf.check_head_freshness(
        "Context: origin/main is `deadbee`; HEAD is `abc1234` now.\n",
        head_sha="abc1234567890",
    )

    assert report["ok"] is True


def test_direct_historical_head_claim_is_allowed_on_same_line() -> None:
    text = (
        "Context: historical HEAD is `deadbee`.\n"
        "Context: HEAD is `deadbee` (not current).\n"
    )

    report = hf.check_head_freshness(text, head_sha="abc1234567890")

    assert report["ok"] is True


def test_historical_or_live_command_lines_are_not_stale_claims() -> None:
    text = (
        "Context: HEAD is 10 commits ahead (`deadbee` before final closeout).\n"
        "PASS: check_changed_line --base-sha deadbee --head-sha HEAD.\n"
    )

    report = hf.check_head_freshness(text, head_sha="abc1234567890")

    assert report["ok"] is True


def test_wrapped_current_head_claim_still_checks_sha() -> None:
    text = "Context: current HEAD is\n`deadbee` after final verification.\n"

    report = hf.check_head_freshness(text, head_sha="abc1234567890")

    assert report["ok"] is False
    assert report["findings"][0]["line"] == 2


def test_current_head_returns_none_when_git_is_unavailable(monkeypatch) -> None:
    def boom(*args, **kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(hf.subprocess, "run", boom)

    assert hf.current_head(Path(".")) is None


def test_fenced_examples_are_ignored() -> None:
    text = "```md\nContext: current HEAD is `deadbee`.\n```\n"

    assert hf.check_head_freshness(text, head_sha="abc1234567890")["ok"] is True


def test_check_goal_artifact_cli_reports_head_freshness_failure(tmp_path: Path) -> None:
    _init_git(tmp_path)
    goal_path = tmp_path / "charness-artifacts/goals/2026-05-31-t.md"
    goal_path.parent.mkdir(parents=True)
    goal_path.write_text(
        _goal_with_context("Context: current HEAD is `deadbee`."),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/achieve/scripts/check_goal_artifact.py",
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal_path),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["head_freshness"]["ok"] is False
    assert "mutable HEAD freshness" in payload["issues"][-1]

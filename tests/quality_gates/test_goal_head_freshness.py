from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from tests.quality_gates.support import run_script

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hf = _load("goal_artifact_head_freshness")
cga = _load("check_goal_artifact")


def run_check_goal_artifact(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_goal_artifact.py", *args])
    returncode = cga.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def _goal_with_context(context: str) -> str:
    sections = (
        "## Active Operating Frame\nx\n\n"
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


def _complete_goal(
    *,
    created: str,
    slug: str,
    final_verification: str,
    activation_slug: str | None = None,
) -> str:
    sections = (
        "## Active Operating Frame\nx\n\n"
        "## Goal\nx\n\n"
        "## Non-Goals\nx\n\n"
        "## Boundaries\nx\n\n"
        "## User Acceptance\nx\n\n"
        "## Agent Verification Plan\nx\n\n"
        "## Slice Plan\nx\n\n"
        "## Slice Log\nx\n\n"
        "## Off-Goal Findings\nx\n\n"
        "## User Verification Instructions\nx\n\n"
        "## Auto-Retro\napplied: no deferred disposition remains\n\n"
        "## Context Sources\nx\n\n"
        "## Interview Decisions\nx\n\n"
        "## Plan Critique Findings\nx\n"
    )
    activation = activation_slug or slug
    return (
        "# Achieve Goal: T\n\n"
        "Status: complete\n"
        f"Created: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{activation}.md`\n\n"
        f"{sections}\n\n"
        f"## Final Verification\n\n{final_verification}\n"
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


def test_check_goal_artifact_cli_pursue_ready_return_codes(tmp_path: Path, monkeypatch, capsys) -> None:
    ready_path = tmp_path / "ready.md"
    ready_path.write_text("Status: active\n## Goal\nshaped\n", encoding="utf-8")
    result = run_check_goal_artifact(
        monkeypatch,
        capsys,
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(ready_path),
        "--pursue-ready",
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["pursue_ready"] is True

    unshaped_path = tmp_path / "unshaped.md"
    unshaped_path.write_text(
        "Status: draft\n## Goal\nto be filled by the achieve before-phase\n",
        encoding="utf-8",
    )
    result = run_check_goal_artifact(
        monkeypatch,
        capsys,
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(unshaped_path),
        "--pursue-ready",
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["pursue_ready"] is False


def test_check_goal_artifact_cli_missing_goal_path_returns_usage_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"
    result = run_script(
        "skills/public/achieve/scripts/check_goal_artifact.py",
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(missing),
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["issues"] == [f"goal artifact not found: {missing.resolve()}"]


def test_check_goal_artifact_cli_reports_missing_evidence_files(tmp_path: Path, monkeypatch, capsys) -> None:
    created = "2026-05-29"
    slug = "missing-evidence"
    goal_path = tmp_path / f"charness-artifacts/goals/{created}-{slug}.md"
    goal_path.parent.mkdir(parents=True)
    goal_path.write_text(
        _complete_goal(
            created=created,
            slug=slug,
            final_verification=(
                f"Retro: charness-artifacts/retro/{created}-{slug}.md\n"
                f"Host log probe: charness-artifacts/probe/{created}-{slug}.json\n"
            ),
        ),
        encoding="utf-8",
    )

    result = run_check_goal_artifact(
        monkeypatch,
        capsys,
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal_path),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "missing files: retro_artifact, host_log_probe" in payload["issues"][-1]


def test_check_goal_artifact_cli_reports_invalid_skips(tmp_path: Path, monkeypatch, capsys) -> None:
    created = "2026-05-29"
    slug = "invalid-skips"
    goal_path = tmp_path / f"charness-artifacts/goals/{created}-{slug}.md"
    goal_path.parent.mkdir(parents=True)
    goal_path.write_text(
        _complete_goal(
            created=created,
            slug=slug,
            final_verification=(
                "Retro: skipped: vague-host-limit\n"
                "Host log probe: skipped: vague-host-limit\n"
            ),
        ),
        encoding="utf-8",
    )

    result = run_check_goal_artifact(
        monkeypatch,
        capsys,
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal_path),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "invalid skips: retro_artifact, host_log_probe" in payload["issues"][-1]


def test_check_goal_artifact_cli_reports_unbound_evidence(tmp_path: Path, monkeypatch, capsys) -> None:
    created = "2026-05-29"
    slug = "bind-cli"
    retro = tmp_path / "charness-artifacts/retro/unrelated.md"
    probe = tmp_path / "charness-artifacts/probe/unrelated.json"
    retro.parent.mkdir(parents=True)
    probe.parent.mkdir(parents=True)
    retro.write_text("# Retro\n\n## Next Improvements\n\nnone\n", encoding="utf-8")
    probe.write_text('{"host":"test"}\n', encoding="utf-8")
    goal_path = tmp_path / f"charness-artifacts/goals/{created}-{slug}.md"
    goal_path.parent.mkdir(parents=True)
    goal_path.write_text(
        _complete_goal(
            created=created,
            slug=slug,
            final_verification=(
                "Retro: charness-artifacts/retro/unrelated.md\n"
                "Host log probe: charness-artifacts/probe/unrelated.json\n"
            ),
        ),
        encoding="utf-8",
    )

    result = run_check_goal_artifact(
        monkeypatch,
        capsys,
        "--repo-root",
        str(tmp_path),
        "--goal-path",
        str(goal_path),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "evidence not bound to this goal: retro_artifact, host_log_probe" in payload["issues"][-1]

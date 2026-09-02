from __future__ import annotations

import sys
from pathlib import Path

import yaml

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_plan_risk_interrupt_cli = import_repo_module(__file__, "scripts.gates_support.plan_risk_interrupt")
_risk_interrupt_lib = import_repo_module(__file__, "scripts.gates_support.risk_interrupt_lib")


def seed_repo(tmp_path: Path, *, debug_body: str, spec_body: str | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "spec").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/debug",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(debug_body, encoding="utf-8")
    if spec_body is not None:
        (repo / "charness-artifacts" / "spec" / "interrupt-demo.md").write_text(spec_body, encoding="utf-8")
    return repo


def debug_artifact(*, risk_class: str = "external-seam") -> str:
    return (
        "\n".join(
            [
                "# Debug Review",
                "Date: 2026-04-22",
                "",
                "## Problem",
                "",
                "problem",
                "",
                "## Correct Behavior",
                "",
                "correct",
                "",
                "## Observed Facts",
                "",
                "- fact",
                "",
                "## Reproduction",
                "",
                "repro",
                "",
                "## Candidate Causes",
                "",
                "- one",
                "- two",
                "- three",
                "",
                "## Hypothesis",
                "",
                "hypothesis",
                "",
                "## Verification",
                "",
                "verification",
                "",
                "## Root Cause",
                "",
                "root cause",
                "",
                "## Seam Risk",
                "",
                "- Interrupt ID: seam-demo",
                f"- Risk Class: {risk_class}",
                "- Seam: slack-thread-activation",
                "- Disproving Observation: live host disproved local reasoning",
                "- What Local Reasoning Cannot Prove: thread visibility semantics",
                "- Generalization Pressure: factor-now",
                "",
                "## Interrupt Decision",
                "",
                "- Critique Required: yes",
                "- Next Step: spec",
                "- Handoff Artifact: charness-artifacts/spec/interrupt-demo.md",
                "",
                "## Prevention",
                "",
                "prevention",
                "",
            ]
        )
        + "\n"
    )


def resolved_spec(*, chosen_next_step: str = "factor-first", impl_status: str = "blocked") -> str:
    return (
        "\n".join(
            [
                "# Problem",
                "",
                "problem",
                "",
                "# Critique",
                "",
                "- Interrupt Source: seam-demo",
                "- Seam Summary: slack-thread-activation",
                f"- Chosen Next Step: {chosen_next_step}",
                f"- Impl Status: {impl_status}",
                "- Impl Status Reason: live seam still needs factor-first work",
                "- What Disproving Observation Is Resolved: spec now carries the host-visible risk forward",
                "",
            ]
        )
        + "\n"
    )


def test_plan_risk_interrupt_blocks_without_current_slice_spec_refresh(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())
    payload = _risk_interrupt_lib.plan_risk_interrupt(repo)
    assert payload["status"] == "blocked"
    assert "refresh `charness-artifacts/spec/interrupt-demo.md`" in payload["next_action"]


def test_plan_risk_interrupt_records_handoff_when_matching_spec_is_refreshed(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())
    payload = _risk_interrupt_lib.plan_risk_interrupt(
        repo,
        changed_paths=[
            "charness-artifacts/debug/latest.md",
            "charness-artifacts/spec/interrupt-demo.md",
        ],
    )
    assert payload["status"] == "handoff-recorded"
    assert payload["chosen_next_step"] == "factor-first"
    assert payload["impl_status"] == "blocked"


def test_plan_risk_interrupt_ignores_stale_current_debug_for_unrelated_slice(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())
    payload = _risk_interrupt_lib.plan_risk_interrupt(repo, changed_paths=["README.md"])
    assert payload["status"] == "not-applicable"
    assert payload["reason"] == "current debug interrupt was not refreshed in this slice"


def test_plan_risk_interrupt_distinguishes_explicit_empty_scope_from_global_discovery(
    tmp_path: Path,
) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())

    global_payload = _risk_interrupt_lib.plan_risk_interrupt(repo)
    empty_payload = _risk_interrupt_lib.plan_risk_interrupt(repo, changed_paths=[])

    assert global_payload["status"] == "blocked"
    assert empty_payload["status"] == "not-applicable"
    assert empty_payload["required"] is False
    assert empty_payload["reason"] == "current slice has no Git-observed paths"


def test_plan_risk_interrupt_cli_maps_blocked_plan_to_exit_one(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())
    monkeypatch.setattr(sys, "argv", ["plan_risk_interrupt.py", "--repo-root", str(repo), "--detail"])

    assert _plan_risk_interrupt_cli.main() == 1
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "blocked"


def test_plan_risk_interrupt_cli_checks_helper_provenance_before_planning(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact())
    calls: list[tuple[Path, Path, str]] = []

    def fake_guard(script_file, target_root, *, scan):
        calls.append((Path(script_file), Path(target_root), scan))
        return {"status": "consuming-repo"}

    monkeypatch.setattr(_plan_risk_interrupt_cli, "require_repo_local_helper", fake_guard)
    monkeypatch.setattr(
        _plan_risk_interrupt_cli,
        "plan_risk_interrupt",
        lambda target_root, changed_paths=None: {
            "status": "not-applicable",
            "required": False,
        },
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["plan_risk_interrupt.py", "--repo-root", str(repo), "--detail"],
    )

    assert _plan_risk_interrupt_cli.main() == 0
    assert calls == [(ROOT / "scripts" / "gates_support" / "plan_risk_interrupt.py", repo.resolve(), "tree")]
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "not-applicable"

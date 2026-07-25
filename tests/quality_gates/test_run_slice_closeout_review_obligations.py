from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def demo_surface(
    *,
    source_paths: list[str] | None = None,
    derived_paths: list[str] | None = None,
    sync_commands: list[str] | None = None,
    verify_commands: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, object]:
    return {
        "surface_id": "demo-surface",
        "description": "demo",
        "source_paths": source_paths if source_paths is not None else ["README.md"],
        "derived_paths": derived_paths if derived_paths is not None else [],
        "sync_commands": sync_commands if sync_commands is not None else [],
        "verify_commands": verify_commands if verify_commands is not None else [],
        "notes": notes if notes is not None else [],
    }

def write_surface_manifest(repo: Path, *surfaces: dict[str, object]) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps({"version": 1, "surfaces": list(surfaces)}, indent=2) + "\n",
        encoding="utf-8",
    )

def test_run_slice_closeout_blocks_public_skill_review_until_acknowledged() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/setup/scripts/inspect_repo.py",
        "--skip-sync",
        "--skip-verify",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "public-skill validation review is required" in payload["error"]
    assert "--ack-cautilus-skill-review" in payload["error"]
    assert payload["cautilus_plan"]["run_mode"] == "ask"
    assert payload["cautilus_plan"]["status"] == "not-required"
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is True
    assert payload["cautilus_plan"]["changed_public_skills"] == ["setup"]
    assert any(
        item["skill_id"] == "setup"
        for item in payload["cautilus_plan"]["skill_validation_recommendations"]
    )


def test_run_slice_closeout_allows_acknowledged_public_skill_review() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/setup/scripts/inspect_repo.py",
        "--skip-sync",
        "--skip-verify",
        "--ack-cautilus-skill-review",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is True
    assert payload["executed_commands"] == []


def test_run_slice_closeout_blocks_hitl_recommended_public_skill_review_until_acknowledged() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/critique/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
        "--skip-sync",
        "--skip-verify",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["cautilus_plan"]["run_mode"] == "ask"
    assert payload["cautilus_plan"]["status"] == "ready-for-validation"
    assert payload["cautilus_plan"]["artifact_changed"] is True
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is False
    assert payload["cautilus_plan"]["changed_public_skills"] == ["critique"]
    assert payload["cautilus_plan"]["skill_validation_recommendations"][0]["validation_tier"] == "hitl-recommended"
    assert "public-skill validation review is required" in payload["error"]


def test_run_slice_closeout_blocks_for_forced_risk_interrupt_without_spec_refresh(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "spec").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
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
    write_surface_manifest(
        repo,
        demo_surface(
            source_paths=[
                "README.md",
                "charness-artifacts/debug/latest.md",
                "charness-artifacts/spec/*.md",
            ],
        ),
    )
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
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
                "- Risk Class: host-disproves-local",
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
        + "\n",
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "spec" / "interrupt-demo.md").write_text(
        "# Critique\n\n- Interrupt Source: seam-demo\n",
        encoding="utf-8",
    )

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "charness-artifacts/debug/latest.md",
        "--json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["risk_interrupt_plan"]["status"] == "blocked"

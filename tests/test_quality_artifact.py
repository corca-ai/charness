from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]


def run_script(
    *args: str,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=None if env is None else {**os.environ, **env},
    )


def seed_repo(tmp_path: Path, artifact_body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality" / "history").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(artifact_body, encoding="utf-8")
    (repo / "charness-artifacts" / "quality" / "history" / "one.md").write_text("# One\n", encoding="utf-8")
    return repo
def test_validate_quality_artifact_rejects_missing_history_section(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Runtime Signals",
                "",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: adapter bootstrap only",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Advisory",
                "",
                "- advisory",
                "",
                "## Delegated Review",
                "",
                "- status: executed; bounded subagent review ran.",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- active AUTO_CANDIDATE: next",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required section `## History`" in result.stderr


def test_validate_quality_artifact_rejects_missing_history_link(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Runtime Signals",
                "",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: adapter bootstrap only",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Advisory",
                "",
                "- advisory",
                "",
                "## Delegated Review",
                "",
                "- status: executed; bounded subagent review ran.",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- active AUTO_CANDIDATE: next",
                "",
                "## History",
                "",
                "- archive pending",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "history/*.md" in result.stderr


def test_validate_quality_artifact_requires_runtime_closeout_fields(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Runtime Signals",
                "",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Advisory",
                "",
                "- advisory",
                "",
                "## Delegated Review",
                "",
                "- status: executed; bounded subagent review ran.",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- active AUTO_CANDIDATE: next",
                "",
                "## History",
                "",
                "- [archive](history/one.md)",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Runtime Signals" in result.stderr


def test_validate_quality_artifact_rejects_explicit_allowance_as_subagent_blocker(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Runtime Signals",
                "",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: degraded local pass only",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- canonical fresh-eye path was blocked because this session did not explicitly allow subagents.",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Advisory",
                "",
                "- advisory",
                "",
                "## Delegated Review",
                "",
                "- status: executed; bounded subagent review ran.",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- active AUTO_CANDIDATE: next",
                "",
                "## History",
                "",
                "- [archive](history/one.md)",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must not treat missing explicit subagent allowance" in result.stderr


def test_validate_quality_artifact_requires_advisory_and_delegated_review(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Runtime Signals",
                "",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: adapter bootstrap only",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- active AUTO_CANDIDATE: next",
                "",
                "## History",
                "",
                "- [archive](history/one.md)",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required section `## Advisory`" in result.stderr


def test_validate_quality_artifact_requires_inventory_backed_empty_advisory(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Runtime Signals",
                "",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: adapter bootstrap only",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Advisory",
                "",
                "- none",
                "",
                "## Delegated Review",
                "",
                "- status: executed; bounded subagent review ran.",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- active AUTO_CANDIDATE: next",
                "",
                "## History",
                "",
                "- [archive](history/one.md)",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "none found by inventory" in result.stderr


def test_validate_quality_artifact_requires_blocked_delegated_review_signal(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Runtime Signals",
                "",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: adapter bootstrap only",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Advisory",
                "",
                "- none found by inventory: `inventory_adapter_gate_design.py`.",
                "",
                "## Delegated Review",
                "",
                "- status: blocked; subagents unavailable.",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- active AUTO_CANDIDATE: next",
                "",
                "## History",
                "",
                "- [archive](history/one.md)",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "concrete host signal or tool signal" in result.stderr

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
        "\n".join([
            "version: 1",
            "repo: demo",
            "language: en",
            "output_dir: charness-artifacts/quality",
        ]),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(artifact_body, encoding="utf-8")
    (repo / "charness-artifacts" / "quality" / "history" / "one.md").write_text("# One\n", encoding="utf-8")
    return repo


def valid_quality_artifact(*, runtime_source: str) -> str:
    return (
        "\n".join([
            "# Quality Review",
            "Date: 2026-04-20",
            "## Scope",
            "- demo",
            "## Current Gates",
            "- gate",
            "## Runtime Signals",
            f"- runtime source: {runtime_source}",
            "- runtime hot spots: `pytest` 10s",
            "- coverage gate: none",
            "- evaluator depth: adapter bootstrap only",
            "## Healthy",
            "- healthy",
            "## Weak",
            "- weak",
            "## Missing",
            "- missing",
            "## Deferred",
            "- deferred",
            "## Advisory",
            "- inventory: `demo-inventory` found advisory signal.",
            "## Delegated Review",
            "- status: executed; bounded subagent review ran.",
            "## Commands Run",
            "- cmd",
            "## Recommended Next Quality Moves",
            "- active AUTO_CANDIDATE: next",
            "## History",
            "- [archive](history/one.md)",
        ])
        + "\n"
    )


def _multi_violation_artifact() -> str:
    return (
        "\n".join([
            "# Quality Review",
            "Date: 2026-04-20",
            "## Scope",
            "- demo",
            "## Current Gates",
            "- gate",
            "## Runtime Signals",
            "- runtime source: manual timing copied from `charness-artifacts/quality/latest.md`.",
            "- runtime hot spots: `pytest` 10s",
            "- coverage gate: none",
            "- evaluator depth: adapter bootstrap only",
            "## Healthy",
            "- healthy",
            "## Weak",
            "- weak",
            "## Missing",
            "- missing",
            "## Deferred",
            "- deferred",
            "## Advisory",
            "- none",
            "## Delegated Review",
            "- status: executed; bounded subagent review ran.",
            "## Commands Run",
            "- cmd",
            "## Recommended Next Quality Moves",
            "- passive AUTO_CANDIDATE: do later",
            "## History",
            "- [archive](history/one.md)",
        ])
        + "\n"
    )


def test_validate_quality_artifact_default_mode_fails_fast(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "runtime source must not be markdown" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "passive recommended next quality moves" not in result.stderr


def test_validate_quality_artifact_report_all_lists_every_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo), "--report-all")
    assert result.returncode == 1
    assert "quality artifact rule violation(s)" in result.stderr
    assert "runtime source must not be markdown" in result.stderr
    assert "none found by inventory" in result.stderr
    assert "passive recommended next quality moves must explain" in result.stderr


def test_validate_quality_artifact_report_all_passes_clean_artifact(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_quality_artifact(
            runtime_source=(
                "structured metrics from `artifacts/runtime-timing.jsonl` "
                "rendered by `scripts/summarize-runtime.py`; profile `ci`."
            ),
        ),
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo), "--report-all")
    assert result.returncode == 0, result.stderr

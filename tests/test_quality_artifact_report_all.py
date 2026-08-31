from __future__ import annotations

from pathlib import Path

from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]


SURFACE_CONTRACT_FIXTURE = """## Surface Contract Review
- semantic coverage: `observed` — contract packet is covered.
- surface: demo surface
- owner: demo owner
- projections: DOM and command output
- state scope: request
- transitions: success and failure
- proof boundary: focused test
- unexamined axes: none
"""


def seed_repo(tmp_path: Path, artifact_body: str) -> Path:
    if "## Surface Contract Review" not in artifact_body:
        artifact_body = artifact_body.replace(
            "## Current Gates\n", SURFACE_CONTRACT_FIXTURE + "## Current Gates\n", 1
        )
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
            "## Surface Contract Review",
            "- semantic coverage: `observed` — contract packet is covered.",
            "- surface: demo surface",
            "- owner: demo owner",
            "- projections: DOM and command output",
            "- state scope: request",
            "- transitions: success and failure",
            "- proof boundary: focused test",
            "- unexamined axes: none",
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
            "## Surface Contract Review",
            "- semantic coverage: `observed` — contract packet is covered.",
            "- surface: demo surface",
            "- owner: demo owner",
            "- projections: DOM and command output",
            "- state scope: request",
            "- transitions: success and failure",
            "- proof boundary: focused test",
            "- unexamined axes: none",
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


def test_validate_quality_artifact_default_mode_reports_all(tmp_path: Path) -> None:
    # Closeout-churn fix: the bare CLI now batches every violation into one pass
    # so a multi-rule draft is fixed in one edit pass, not one rule per gate run.
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "quality artifact rule violation(s)" in result.stderr
    assert "runtime source must not be markdown" in result.stderr
    assert "passive recommended next quality moves must explain" in result.stderr


def test_validate_quality_artifact_fail_fast_stops_at_first_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo), "--fail-fast")
    assert result.returncode == 1
    assert "runtime source must not be markdown" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "passive recommended next quality moves" not in result.stderr

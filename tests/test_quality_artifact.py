from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Mapping

import pytest

from scripts.validate_quality_artifact import ValidationError, _skill_ergonomics_counts

ROOT = Path(__file__).resolve().parents[1]


def cautilus_supports(*subcommand: str, timeout: float = 30.0) -> bool:
    """Whether the installed cautilus exposes the given subcommand surface.

    Eval tests gate on usability rather than binary presence so a drifted or
    older cautilus skips instead of hard-failing. See issue #225.
    """
    if shutil.which("cautilus") is None:
        return False
    try:
        result = subprocess.run(
            ["cautilus", *subcommand, "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


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
            ]
        ),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(artifact_body, encoding="utf-8")
    (repo / "charness-artifacts" / "quality" / "history" / "one.md").write_text("# One\n", encoding="utf-8")
    return repo


def seed_skill(repo: Path, skill_id: str = "retro") -> None:
    skill_dir = repo / "skills" / "public" / skill_id
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {skill_id}",
                'description: "Demo skill."',
                "---",
                "# Demo",
                "",
                "Use this skill.",
                "",
                "## Bootstrap",
                "",
                "Run it.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "one.md").write_text("# One\n", encoding="utf-8")
    (skill_dir / "references" / "two.md").write_text("# Two\n", encoding="utf-8")
    (skill_dir / "scripts" / "run.py").write_text("print('ok')\n", encoding="utf-8")


def valid_quality_artifact(*, runtime_source: str, runtime_hotspots: str = "`pytest` 10s") -> str:
    return (
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                f"- runtime source: {runtime_source}",
                f"- runtime hot spots: {runtime_hotspots}",
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
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
            ]
        )
        + "\n"
    )


def test_validate_quality_artifact_accepts_generic_structured_runtime_source(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_quality_artifact(
            runtime_source=(
                "structured metrics from `artifacts/runtime-timing.jsonl` "
                "rendered by `scripts/summarize-runtime.py`; profile `ci`."
            ),
        ),
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_quality_artifact_rejects_markdown_runtime_source(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_quality_artifact(runtime_source="manual timing copied from `charness-artifacts/quality/latest.md`."),
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "runtime source must not be markdown" in result.stderr


def test_validate_quality_artifact_rejects_numeric_hotspots_without_renderer(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_quality_artifact(runtime_source="structured metrics from `artifacts/runtime-timing.jsonl`."),
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must cite the summary helper" in result.stderr


def test_validate_quality_artifact_rejects_stale_skill_ergonomics_counts(tmp_path: Path) -> None:
    body = valid_quality_artifact(
        runtime_source=(
            "structured metrics from `artifacts/runtime-timing.jsonl` "
            "rendered by `scripts/summarize-runtime.py`; profile `ci`."
        )
    ).replace(
        "## Current Gates\n- gate",
        (
            "## Current Gates\n"
            "- `retro` core remains inside the skill ergonomics budget:\n"
            "  `core_nonempty_lines=999`, `reference_file_count=2`, `script_file_count=1`,\n"
            "  `unlisted_reference_files=[]`."
        ),
    )
    repo = seed_repo(tmp_path, body)
    seed_skill(repo)

    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "stale skill ergonomics counts for `retro`" in result.stderr


def test_validate_quality_artifact_rejects_differently_worded_stale_count_claim(tmp_path: Path) -> None:
    body = valid_quality_artifact(
        runtime_source=(
            "structured metrics from `artifacts/runtime-timing.jsonl` "
            "rendered by `scripts/summarize-runtime.py`; profile `ci`."
        )
    ).replace(
        "## Current Gates\n- gate",
        (
            "## Current Gates\n"
            "- Skill pressure for `retro` was sampled directly: "
            "`core_nonempty_lines=4`, `reference_file_count=999`, `script_file_count=1`."
        ),
    )
    repo = seed_repo(tmp_path, body)
    seed_skill(repo)

    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "stale skill ergonomics counts for `retro`" in result.stderr


def test_validate_quality_artifact_rejects_count_claim_without_public_skill_id(tmp_path: Path) -> None:
    body = valid_quality_artifact(
        runtime_source=(
            "structured metrics from `artifacts/runtime-timing.jsonl` "
            "rendered by `scripts/summarize-runtime.py`; profile `ci`."
        )
    ).replace(
        "## Current Gates\n- gate",
        (
            "## Current Gates\n"
            "- Skill pressure was sampled directly: "
            "`core_nonempty_lines=4`, `reference_file_count=2`, `script_file_count=1`."
        ),
    )
    repo = seed_repo(tmp_path, body)

    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "no backticked public skill id" in result.stderr


def test_skill_ergonomics_counts_missing_skill_fails(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="missing skill `retro`"):
        _skill_ergonomics_counts(tmp_path, "retro")


def test_validate_quality_artifact_accepts_counts_when_skill_has_no_refs_or_scripts(tmp_path: Path) -> None:
    body = valid_quality_artifact(
        runtime_source=(
            "structured metrics from `artifacts/runtime-timing.jsonl` "
            "rendered by `scripts/summarize-runtime.py`; profile `ci`."
        )
    ).replace(
        "## Current Gates\n- gate",
        (
            "## Current Gates\n"
            "- Skill pressure for `retro` was sampled directly: "
            "`core_nonempty_lines=4`, `reference_file_count=0`, `script_file_count=0`."
        ),
    )
    repo = seed_repo(tmp_path, body)
    seed_skill(repo)
    shutil.rmtree(repo / "skills" / "public" / "retro" / "references")
    shutil.rmtree(repo / "skills" / "public" / "retro" / "scripts")

    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_validate_quality_artifact_accepts_current_skill_ergonomics_counts(tmp_path: Path) -> None:
    body = valid_quality_artifact(
        runtime_source=(
            "structured metrics from `artifacts/runtime-timing.jsonl` "
            "rendered by `scripts/summarize-runtime.py`; profile `ci`."
        )
    ).replace(
        "## Current Gates\n- gate",
        (
            "## Current Gates\n"
            "- `retro` core remains inside the skill ergonomics budget:\n"
            "  `core_nonempty_lines=4`, `reference_file_count=2`, `script_file_count=1`,\n"
            "  `unlisted_reference_files=[]`."
        ),
    )
    repo = seed_repo(tmp_path, body)
    seed_skill(repo)

    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_validate_quality_artifact_allows_missing_runtime_source_without_numbers(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_quality_artifact(
            runtime_source="not configured; add structured timing capture before reporting timing trends.",
            runtime_hotspots="unavailable until structured runtime metrics have samples.",
        ),
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_quality_artifact_rejects_missing_runtime_source_with_numbers(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_quality_artifact(
            runtime_source="not configured; add structured timing capture before reporting timing trends.",
            runtime_hotspots="`pytest` 10s",
        ),
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "runtime hot spot timings require a structured runtime source" in result.stderr
def test_validate_quality_artifact_rejects_missing_history_section(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
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
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
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
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
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
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- archive pending",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "history/*.md" in result.stderr


def test_validate_quality_artifact_accepts_dot_slash_history_link(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `metrics.json` rendered by `render_runtime_summary.py`",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: pass",
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
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](./history/one.md)",
            ]
        )
        + "\n",
    )

    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_validate_quality_artifact_requires_runtime_closeout_fields(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
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
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
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
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: degraded local pass only",
                "## Healthy",
                "- healthy",
                "## Weak",
                "- canonical fresh-eye path was blocked because this session did not explicitly allow subagents.",
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
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
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
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
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
                "## Commands Run",
                "- cmd",
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
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
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
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
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "none found by inventory" in result.stderr


def test_validate_quality_artifact_rejects_unevidenced_advisory_bullets(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
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
                "- advisory",
                "## Delegated Review",
                "- status: executed; bounded subagent review ran.",
                "## Commands Run",
                "- cmd",
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "advisory bullets must cite inventory" in result.stderr


def test_validate_quality_artifact_requires_blocked_delegated_review_signal(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
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
                "- none found by inventory: `inventory_adapter_gate_design.py`.",
                "## Delegated Review",
                "- status: blocked; subagents unavailable.",
                "## Commands Run",
                "- cmd",
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "concrete host signal or tool signal" in result.stderr


def test_validate_quality_artifact_rejects_missed_delegated_review(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "## Scope",
                "- demo",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.",
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
                "- none found by inventory: `inventory_adapter_gate_design.py`.",
                "## Delegated Review",
                "- status: missed; not executed in this run.",
                "## Commands Run",
                "- cmd",
                "## Recommended Next Gates",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must not report a missed review" in result.stderr


def _multi_violation_artifact() -> str:
    # Breaks three independent rules at once: a markdown runtime source, an empty
    # `none` advisory claim, and a passive next-gate without a `because`/`until`
    # rationale. Used to exercise --report-all vs the fail-fast default.
    return (
        "\n".join(
            [
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
                "## Recommended Next Gates",
                "- passive AUTO_CANDIDATE: do later",
                "## History",
                "- [archive](history/one.md)",
            ]
        )
        + "\n"
    )


def test_validate_quality_artifact_default_mode_fails_fast(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script("scripts/validate_quality_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    # Default mode raises on the first failing check (runtime signals) only.
    assert "runtime source must not be markdown" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "passive recommended next gates" not in result.stderr


def test_validate_quality_artifact_report_all_lists_every_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script(
        "scripts/validate_quality_artifact.py", "--repo-root", str(repo), "--report-all"
    )
    assert result.returncode == 1
    assert "quality artifact rule violation(s)" in result.stderr
    # All three independent violations surface in one pass.
    assert "runtime source must not be markdown" in result.stderr
    assert "none found by inventory" in result.stderr
    assert "passive recommended next gates must explain" in result.stderr


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
    result = run_script(
        "scripts/validate_quality_artifact.py", "--repo-root", str(repo), "--report-all"
    )
    assert result.returncode == 0, result.stderr

from __future__ import annotations

from pathlib import Path

from .support import run_script


def seed_repo(
    tmp_path: Path,
    *,
    handoff_text: str = "# Demo Handoff\n\n## Next Session\n\n- Extend current pointer freshness.\n",
    quality_text: str = "# Quality Review\n\n## Missing\n\n- Freshness validator exists; extend concrete claim coverage.\n",
    queued: bool = True,
) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "skills" / "public" / "quality" / "scripts").mkdir(parents=True)
    queue_line = (
        'queue_selected "validate-current-pointer-freshness" '
        'python3 scripts/validate_current_pointer_freshness.py --repo-root "$REPO_ROOT"\n'
        if queued
        else ""
    )
    (repo / "scripts" / "run-quality.sh").write_text(queue_line, encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text(handoff_text, encoding="utf-8")
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(quality_text, encoding="utf-8")
    (repo / ".gitignore").write_text(".charness/quality/runtime-smoothing.json\n", encoding="utf-8")
    (repo / "scripts" / "record_quality_runtime.py").write_text(
        "\n".join(
            [
                'SMOOTHING_FILENAME = "runtime-smoothing.json"',
                "SMOOTHING_ALPHA_BASE = 0.35",
                "SMOOTHING_WARMUP_N = 5",
                '"advisory": True',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "check_coverage.py").write_text("# coverage\n", encoding="utf-8")
    (repo / "scripts" / "check_test_production_ratio.py").write_text("# ratio\n", encoding="utf-8")
    (repo / "skills" / "public" / "quality" / "scripts" / "check_runtime_budget.py").write_text(
        "\n".join(
            [
                'SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"',
                "ewma_advisory_elapsed_ms",
                "ewma {ewma:.1f}ms advisory",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def test_current_pointer_freshness_accepts_queued_non_stale_pointers(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 0
    assert "Validated rolling current-pointer freshness claims." in result.stdout


def test_current_pointer_freshness_requires_run_quality_queue(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, queued=False)
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must queue `validate-current-pointer-freshness`" in result.stderr


def test_current_pointer_freshness_rejects_stale_handoff_first_slice_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        handoff_text=(
            "# Demo Handoff\n\n"
            "## Next Session\n\n"
            "- derived memory 작업은 freshness validator를 첫 slice로 잡는다.\n"
        ),
    )
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "docs/handoff.md" in result.stderr
    assert "freshness validator" in result.stderr


def test_current_pointer_freshness_rejects_stale_quality_missing_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Missing\n\n"
            "- No deterministic freshness check yet cross-validates current pointers.\n"
        ),
    )
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "charness-artifacts/quality/latest.md" in result.stderr
    assert "No deterministic freshness check yet" in result.stderr


def test_current_pointer_freshness_rejects_missing_command_script_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Commands Run\n\n"
            "- `python3 scripts/missing_inventory.py --repo-root .`\n"
        ),
    )
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "quality pointer command claims are stale" in result.stderr
    assert "scripts/missing_inventory.py" in result.stderr


def test_current_pointer_freshness_rejects_runtime_smoothing_claim_drift(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Current Gates\n\n"
            "- Runtime EWMA is advisory in `.charness/quality/runtime-smoothing.json`.\n"
        ),
    )
    (repo / ".gitignore").write_text("", encoding="utf-8")
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "runtime smoothing claim is stale" in result.stderr
    assert ".charness/quality/runtime-smoothing.json" in result.stderr

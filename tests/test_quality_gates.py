from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def make_minimal_skill_repo(tmp_path: Path, description: str) -> Path:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                f"description: {description}",
                "---",
                "",
                "# Demo",
            ]
        ),
        encoding="utf-8",
    )
    return repo


def test_validate_skills_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-skills.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_unquoted_description(tmp_path: Path) -> None:
    repo = make_minimal_skill_repo(
        tmp_path,
        "Use when something has punctuation: this should be rejected.",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "double-quoted" in result.stderr


def test_validate_profiles_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_profiles_rejects_missing_skill_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    profiles_dir.mkdir(parents=True)
    (profiles_dir / "constitutional.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "constitutional",
                "display_name": "Constitutional",
                "purpose": "Test",
                "bundles": {"public_skills": ["missing-skill"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing artifact `missing-skill`" in result.stderr


def test_validate_adapters_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-adapters.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_foreign_absolute_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(
        "[bad](/tmp/not-in-repo.md)\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "foreign absolute link" in result.stderr


def test_check_duplicates_reports_current_hotspots() -> None:
    result = run_script("scripts/check-duplicates.py", "--repo-root", str(ROOT), "--json")
    assert result.returncode == 0, result.stderr
    duplicates = json.loads(result.stdout)
    assert isinstance(duplicates, list)
    assert duplicates, "expected current repo to have duplicate helper hotspots"

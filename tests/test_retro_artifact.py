from __future__ import annotations

import subprocess
from pathlib import Path

from tests.quality_gates.support import run_script

_PRELUDE = "# Session Retro: Demo\nDate: 2026-05-23\nMode: session\n\n## Waste\n\n- something\n\n"


def _seed(repo: Path, body: str, name: str = "2026-05-23-demo.md") -> Path:
    artifact = repo / "charness-artifacts" / "retro" / name
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(body, encoding="utf-8")
    return artifact


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_retro_sibling_search_accepts_followup(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- same layer: skills/public/x/SKILL.md:10 | decision: valid follow-up outside the slice | proof: static scan | follow-up: https://github.com/x/y/issues/9\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_sibling_search_accepts_trivial_short_circuit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- n/a — trivial fix; no plausible siblings\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_sibling_search_rejects_followup_without_identifier(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- abstraction up: scripts/foo.py:1 | decision: valid follow-up outside the slice | proof: static scan\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "follow-up:" in result.stderr
    assert "abstraction up: scripts/foo.py:1" in result.stderr


def test_retro_sibling_search_rejects_bare_deferred(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- same layer: scripts/foo.py:1 | decision: valid follow-up outside the slice | proof: static | follow-up: deferred\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "follow-up:" in result.stderr


def test_retro_sibling_search_is_opt_in(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = _PRELUDE + "## Next Improvements\n\n- workflow: do better\n\n## Persisted\n\nPersisted: yes path\n"
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_validator_skips_generated_digest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    # recent-lessons.md is generated; a stray bad sibling block in it must not gate.
    body = (
        "# Recent Lessons\n\n## Sibling Search\n\n"
        + "- same layer: a:1 | decision: valid follow-up outside the slice | proof: x\n"
    )
    _seed(repo, body, name="recent-lessons.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr
    assert "Validated 0 retro artifact(s)." in result.stdout


def test_retro_validator_no_artifacts_passes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_persisted_form_rejects_future_legacy_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n"
        "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body, name="2026-06-25-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "`## Persisted` has invalid persisted status" in result.stderr


def test_retro_persisted_form_rejects_future_missing_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n"
    )
    _seed(repo, body, name="2026-06-25-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "`## Persisted` must state" in result.stderr


def test_retro_persisted_form_accepts_future_canonical_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-06-25-demo.md\n"
    )
    _seed(repo, body, name="2026-06-25-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_validator_uses_changed_path_discovery(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init")
    _run_git(repo, "config", "user.email", "test@example.com")
    _run_git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "seed")
    _seed(
        repo,
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-06-25-demo.md\n",
        name="2026-06-25-demo.md",
    )

    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "Validated 1 retro artifact(s)." in result.stdout

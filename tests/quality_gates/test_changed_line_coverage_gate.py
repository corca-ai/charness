from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/check_changed_line_coverage.py"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _rev(repo: Path, ref: str = "HEAD") -> str:
    return subprocess.run(
        ["git", "rev-parse", ref], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _write_adapter(repo: Path, eligible_globs: list[str]) -> None:
    lines = [
        "version: 1",
        "repo: testrepo",
        "output_dir: charness-artifacts/quality",
        "changed_line_mutation_gate:",
        "  coverage_json: cov.json",
    ]
    if eligible_globs:
        lines.append("  eligible_globs:")
        lines += [f"    - {g}" for g in eligible_globs]
    else:
        lines.append("  eligible_globs: []")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_repo(tmp_path: Path) -> tuple[Path, str]:
    """A git repo whose pkg/foo.py gains line 4 in a second commit. Returns (repo, base_sha)."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "pkg" / "foo.py").write_text("a = 1\nb = 2\nc = 3\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base")
    base = _rev(repo)
    (repo / "pkg" / "foo.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add line 4")
    return repo, base


def _write_coverage(repo: Path, *, missing: list[int], executed: list[int]) -> None:
    (repo / "cov.json").write_text(
        json.dumps({"files": {"pkg/foo.py": {"executed_lines": executed, "missing_lines": missing}}}),
        encoding="utf-8",
    )


def _stamp(repo: Path, base: str) -> None:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--stamp-marker", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["fingerprint"]


def test_flags_uncovered_changed_line(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    _stamp(repo, base)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD", "--json")
    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload["blocking"] == ["pkg/foo.py"]


def test_passes_when_changed_line_covered(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[], executed=[1, 2, 3, 4])
    _stamp(repo, base)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert payload["changed_pool_files"] == ["pkg/foo.py"]


def test_inert_when_no_eligible_globs(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, [])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["inert"] is True


def test_stale_coverage_skips_non_blocking(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    # No marker stamped => coverage is treated as stale => non-blocking skip.
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "stale" in payload["reason"]


def test_no_base_sha_is_non_blocking(tmp_path: Path) -> None:
    repo, _ = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", "", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["ok"] is True


def test_invalid_adapter_fails_closed(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nchanged_line_mutation_gate: not-a-mapping\n", encoding="utf-8"
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert any("changed_line_mutation_gate must be a mapping" in e for e in payload["adapter_errors"])

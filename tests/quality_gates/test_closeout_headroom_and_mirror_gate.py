"""Tests for the closeout-ergonomics gates: #256 length headroom (advisory) and
#257 staged plugin-mirror drift (hard pre-commit gate).

A new file on purpose: ``test_python_and_security_gates.py`` is itself at
715/720 (the warn band), so piling on would trip the very near-limit trap #256
exists to surface.
"""
from __future__ import annotations

import importlib
import subprocess
import tarfile
from pathlib import Path

from .support import ROOT, init_git_repo, run_script

# --- #256 length headroom (advisory) ---------------------------------------


def _skill_helper(repo: Path, name: str, lines: int) -> Path:
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True, exist_ok=True)
    path = helper_dir / name
    path.write_text("\n".join(f"x = {i}" for i in range(lines)) + "\n", encoding="utf-8")
    return path


def test_headroom_reports_limit_minus_current_and_flags_near_limit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    near = _skill_helper(repo, "near.py", 340)  # warn 330 / limit 360 -> near-limit
    short = _skill_helper(repo, "short.py", 10)
    result = run_script(
        "scripts/check_python_lengths.py",
        "--repo-root",
        str(repo),
        "--headroom",
        "--paths",
        str(near),
        str(short),
    )
    assert result.returncode == 0  # advisory: never blocks
    assert "near.py: 340/360 code lines (20 left) NEAR-LIMIT" in result.stdout
    assert "short.py: 10/360 code lines (350 left)" in result.stdout
    assert "WARN:" in result.stdout and "near.py" in result.stdout.split("WARN:")[1]


def test_headroom_json_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    near = _skill_helper(repo, "near.py", 340)
    result = run_script(
        "scripts/check_python_lengths.py",
        "--repo-root",
        str(repo),
        "--headroom",
        "--json",
        "--paths",
        str(near),
    )
    import json

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    row = payload["headroom"][0]
    assert row["lines"] == 340 and row["limit"] == 360 and row["headroom"] == 20
    assert row["measurement"] == "tokei-python-code-lines"
    assert row["near_limit"] is True


def test_headroom_ignores_non_gated_paths(tmp_path: Path) -> None:
    # A path outside the gated universe (e.g. a top-level file) is silently
    # excluded — headroom only speaks for files the length gate would gate.
    repo = tmp_path / "repo"
    (repo).mkdir(parents=True, exist_ok=True)
    top = repo / "top_level.py"
    top.write_text("x = 1\n", encoding="utf-8")
    result = run_script(
        "scripts/check_python_lengths.py", "--repo-root", str(repo), "--headroom", "--paths", str(top)
    )
    assert result.returncode == 0
    assert "top_level.py" not in result.stdout


# --- #257 staged plugin-mirror drift (hard gate) ---------------------------

mirror_gate = importlib.import_module("scripts.check_staged_mirror_drift")


def test_staged_index_tree_reflects_staged_not_head(tmp_path: Path) -> None:
    """The gate validates the *staged* state, so write-tree must capture the
    index (not HEAD) — this is what lets it catch a source staged without its
    mirror, which a HEAD-based check cannot see until after the commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "f.txt").write_text("committed\n", encoding="utf-8")
    init_git_repo(repo, "f.txt")
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "init"],
                   cwd=repo, check=True, capture_output=True, text=True)
    # stage a modification (do NOT commit)
    (repo / "f.txt").write_text("staged-change\n", encoding="utf-8")
    subprocess.run(["git", "add", "f.txt"], cwd=repo, check=True, capture_output=True, text=True)

    tree = mirror_gate.staged_index_tree(repo)
    assert len(tree) == 40  # a real tree sha
    archive = subprocess.run(["git", "archive", "--format=tar", tree], cwd=repo,
                             check=True, capture_output=True)
    import io

    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as tar:
        member = tar.extractfile("f.txt")
        assert member is not None
        assert member.read().decode() == "staged-change\n"  # staged, not the committed content


def test_main_blocks_on_drift_and_passes_when_clean(tmp_path: Path, monkeypatch, capsys) -> None:
    """The wrapper returns 1 + prints actionable guidance on drift, 0 when clean —
    independent of the (already-tested) validate_packaging machinery it reuses."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "f.txt").write_text("x\n", encoding="utf-8")
    init_git_repo(repo, "f.txt")
    monkeypatch.setattr(mirror_gate, "staged_index_tree", lambda _root: "0" * 40)
    monkeypatch.setattr(mirror_gate._vpc, "extract_snapshot", lambda *a, **k: None)
    monkeypatch.setattr(
        mirror_gate._vpc, "validate_snapshot",
        lambda _snap: subprocess.CompletedProcess([], 1, "drift at plugins/x", ""),
    )
    monkeypatch.setattr("sys.argv", ["check_staged_mirror_drift.py", "--repo-root", str(repo)])
    assert mirror_gate.main() == 1
    err = capsys.readouterr().err
    assert "STAGED plugin mirror is out of sync" in err
    assert "sync_root_plugin_manifests.py" in err

    monkeypatch.setattr(
        mirror_gate._vpc, "validate_snapshot",
        lambda _snap: subprocess.CompletedProcess([], 0, "ok", ""),
    )
    assert mirror_gate.main() == 0


def test_gate_passes_on_real_repo_in_sync() -> None:
    """End-to-end happy path against the real repo (committed mirror is in sync).
    Exercises git write-tree + archive + the real validate_packaging."""
    result = run_script("scripts/check_staged_mirror_drift.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "matches staged sources" in result.stdout

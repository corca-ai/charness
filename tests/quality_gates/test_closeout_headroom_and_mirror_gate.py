"""Tests for the closeout-ergonomics gates: #256 length headroom (advisory) and
#257 staged plugin-mirror drift (hard pre-commit gate).

A new file on purpose: ``test_python_and_security_gates.py`` is itself at
715/720 (the warn band), so piling on would trip the very near-limit trap #256
exists to surface.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .support import run_script

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
    payload = yaml.safe_load(result.stdout)
    rows = {row["path"].rsplit("/", 1)[-1]: row for row in payload["headroom"]}
    # `limit - current` per file, and the near-limit judgment, for both the
    # near-limit and the roomy file.
    assert (rows["near.py"]["lines"], rows["near.py"]["limit"], rows["near.py"]["headroom"]) == (340, 360, 20)
    assert rows["near.py"]["near_limit"] is True
    assert (rows["short.py"]["lines"], rows["short.py"]["limit"], rows["short.py"]["headroom"]) == (10, 360, 350)
    assert rows["short.py"]["near_limit"] is False
    # The near-limit roll-up and its "new module before adding more" advice —
    # carried by the retired `WARN:` line — are payload keys now, and they name
    # only the near-limit file.
    assert [path.rsplit("/", 1)[-1] for path in payload["near_limit_paths"]] == ["near.py"]
    assert payload["advisory"].startswith("WARN: 1 file(s) near the length limit")
    assert "consider a new" in payload["advisory"]


def test_headroom_payload_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    near = _skill_helper(repo, "near.py", 340)
    result = run_script(
        "scripts/check_python_lengths.py",
        "--repo-root",
        str(repo),
        "--headroom",
        "--paths",
        str(near),
    )

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    row = payload["headroom"][0]
    assert row["lines"] == 340 and row["limit"] == 360 and row["headroom"] == 20
    assert row["measurement"] == "tokei-python-code-lines"
    assert row["near_limit"] is True
    # The self-declaration rides only when a near-limit smell is present, and
    # only the exact `limit - current` values above are verified facts.
    assert payload["interpretation"]["proxy_for"]


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

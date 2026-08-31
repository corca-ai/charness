from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.quality_gates.repo_shapes import install_committed_repo
from tests.script_main import run_loaded_script_main

from .support import run_script

PYTHON_LENGTHS = importlib.import_module("scripts.check_code_lengths")

def test_check_code_lengths_strict_listing_fails_closed_outside_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "short.py").write_text("def short():\n    return 1\n", encoding="utf-8")

    result = run_script(
        "scripts/check_code_lengths.py",
        "--repo-root",
        str(repo),
        "--require-git-file-listing",
        real_process=True,
    )

    assert result.returncode == 1
    assert "repo file listing failed" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr


def test_check_python_runtime_inheritance_strict_listing_fails_closed_outside_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "short.py").write_text("def short():\n    return 1\n", encoding="utf-8")

    result = run_script(
        "scripts/check_python_runtime_inheritance.py",
        "--repo-root",
        str(repo),
        "--require-git-file-listing",
    )

    assert result.returncode == 1
    assert "repo file listing failed" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr


def test_check_code_lengths_rejects_too_long_skill_helper_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "helper.py").write_text("\n".join(f"print({i})" for i in range(361)) + "\n", encoding="utf-8")
    result = run_script("scripts/check_code_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tokei code lines 361 exceed limit 360" in result.stderr


def test_check_code_lengths_reports_all_over_limit_files_in_one_run(tmp_path: Path) -> None:
    """One bad file must not hide later hard failures in the same listing."""
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    scripts_dir = repo / "scripts"
    helper_dir.mkdir(parents=True)
    scripts_dir.mkdir(parents=True)
    (helper_dir / "helper.py").write_text(
        "\n".join(f"print({i})" for i in range(361)) + "\n", encoding="utf-8"
    )
    (scripts_dir / "tool.py").write_text(
        "\n".join(f"print({i})" for i in range(481)) + "\n", encoding="utf-8"
    )

    result = run_loaded_script_main(
        "check_code_lengths.py", PYTHON_LENGTHS, "--repo-root", str(repo)
    )

    assert result.returncode == 1
    assert "skills/public/demo/scripts/helper.py: tokei code lines 361 exceed limit 360" in result.stderr
    assert "scripts/tool.py: tokei code lines 481 exceed limit 480" in result.stderr
    assert "Validation failed for 2 file(s)" in result.stderr


def test_check_code_lengths_uses_tokei_code_lines_not_comments_or_blanks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    physical_lines = ["# generated note" for _ in range(420)]
    physical_lines.extend(["", "", "print(1)", "print(2)"])
    (helper_dir / "comment_heavy.py").write_text("\n".join(physical_lines) + "\n", encoding="utf-8")

    result = run_script("scripts/check_code_lengths.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "comment_heavy.py" not in result.stderr
    assert "comment_heavy.py" not in result.stdout


def test_check_code_lengths_fails_when_tokei_missing_instead_of_falling_back(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "helper.py").write_text("print(1)\n", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(sys.executable)
    git_path = shutil.which("git")
    assert git_path is not None
    (bin_dir / "git").symlink_to(git_path)

    result = run_script(
        "scripts/check_code_lengths.py",
        "--repo-root",
        str(repo),
        env={**os.environ, "PATH": str(bin_dir)},
        real_process=True,
    )

    assert result.returncode == 1
    assert "tokei binary not found on PATH" in result.stderr
    assert "does not fall back to physical splitlines totals" in result.stderr


def test_tokei_code_counts_rejects_missing_code_field(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "target.py"
    target.write_text("print(1)\n", encoding="utf-8")

    monkeypatch.setattr(PYTHON_LENGTHS.shutil, "which", lambda _name: "/fake/tokei")
    monkeypatch.setattr(
        PYTHON_LENGTHS.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0],
            0,
            json.dumps({"Python": {"reports": [{"name": str(target), "stats": {}}]}}),
            "",
        ),
    )

    with pytest.raises(PYTHON_LENGTHS.TokeiError, match="stats.code"):
        PYTHON_LENGTHS.tokei_code_counts([target])


def test_tokei_code_counts_rejects_invalid_json(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "target.py"
    target.write_text("print(1)\n", encoding="utf-8")

    monkeypatch.setattr(PYTHON_LENGTHS.shutil, "which", lambda _name: "/fake/tokei")
    monkeypatch.setattr(
        PYTHON_LENGTHS.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "{not-json", ""),
    )

    with pytest.raises(PYTHON_LENGTHS.TokeiError, match="invalid JSON"):
        PYTHON_LENGTHS.tokei_code_counts([target])


def test_check_code_lengths_ignores_gitignored_python_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "scripts/generated_*.py\ntests/generated_*.py\n",
            "scripts/kept.py": "def short():\n    return 1\n",
            "tests/kept_test.py": "def test_short():\n    assert True\n",
        },
    )
    (repo / "scripts" / "generated_long.py").write_text(
        "\n".join(f"print({i})" for i in range(381)) + "\n", encoding="utf-8"
    )
    (repo / "tests" / "generated_long.py").write_text(
        "\n".join(["def test_generated():", *[f"    value_{i} = {i}" for i in range(151)], "    assert True", ""]),
        encoding="utf-8",
    )

    result = run_script("scripts/check_code_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_code_lengths_rejects_too_long_test_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tests_dir = repo / "tests"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_big.py").write_text("\n".join(f"VALUE_{i} = {i}" for i in range(801)) + "\n", encoding="utf-8")
    result = run_script("scripts/check_code_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tokei code lines 801 exceed limit 800" in result.stderr


def test_check_code_lengths_warns_for_in_band_files_across_classes(tmp_path: Path) -> None:
    """A file in each class's advisory ``[warn, limit]`` band keeps exit 0 but
    emits a line-start ``WARN:`` so ``run-quality.sh`` surfaces it on a pass."""
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    scripts_dir = repo / "scripts"
    tests_dir = repo / "tests"
    for directory in (helper_dir, scripts_dir, tests_dir):
        directory.mkdir(parents=True)
    # skill helper band [330, 360]; repo script band [432, 480]; test band [720, 800].
    (helper_dir / "helper.py").write_text("\n".join(f"print({i})" for i in range(340)) + "\n", encoding="utf-8")
    (scripts_dir / "tool.py").write_text("\n".join(f"print({i})" for i in range(440)) + "\n", encoding="utf-8")
    (tests_dir / "test_band.py").write_text("\n".join(f"VALUE_{i} = {i}" for i in range(730)) + "\n", encoding="utf-8")

    result = run_script("scripts/check_code_lengths.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    warn_lines = [line for line in result.stdout.splitlines() if line.startswith("WARN: ")]
    assert any("helper.py: tokei code lines 340 are within the advisory warn band [330, 360]" in line for line in warn_lines)
    assert any("scripts/tool.py: tokei code lines 440 are within the advisory warn band [432, 480]" in line for line in warn_lines)
    assert any("tests/test_band.py: tokei code lines 730 are within the advisory warn band [720, 800]" in line for line in warn_lines)


def test_check_code_lengths_does_not_warn_just_below_band(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    # 329 lines: one below the skill-helper warn floor of 330.
    (helper_dir / "helper.py").write_text("\n".join(f"print({i})" for i in range(329)) + "\n", encoding="utf-8")
    result = run_script("scripts/check_code_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "WARN:" not in result.stdout


def test_check_code_lengths_paths_mode_rejects_over_limit_staged_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "over.py").write_text("\n".join(f"print({i})" for i in range(361)) + "\n", encoding="utf-8")
    result = run_script(
        "scripts/check_code_lengths.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/demo/scripts/over.py",
    )
    assert result.returncode == 1
    assert "tokei code lines 361 exceed limit 360" in result.stderr


def test_check_code_lengths_paths_mode_warns_for_in_band_staged_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    # 340 lines: inside the skill-helper warn band [330, 360].
    (helper_dir / "band.py").write_text("\n".join(f"print({i})" for i in range(340)) + "\n", encoding="utf-8")
    result = run_script(
        "scripts/check_code_lengths.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/demo/scripts/band.py",
    )
    assert result.returncode == 0, result.stderr
    warn_lines = [line for line in result.stdout.splitlines() if line.startswith("WARN: ")]
    assert any("band.py: tokei code lines 340 are within the advisory warn band [330, 360]" in line for line in warn_lines)


def test_check_code_lengths_paths_mode_checks_only_listed_paths(tmp_path: Path) -> None:
    """Staged-only: only files in ``--paths`` are gated. An over-limit file not
    in the list is left to the pre-push whole-repo run; a small staged file
    passes quietly."""
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "trap.py").write_text("\n".join(f"print({i})" for i in range(400)) + "\n", encoding="utf-8")
    (helper_dir / "small.py").write_text("print(1)\n", encoding="utf-8")
    result = run_script(
        "scripts/check_code_lengths.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/demo/scripts/small.py",
    )
    assert result.returncode == 0, result.stderr
    assert "WARN:" not in result.stdout
    assert "trap.py" not in result.stdout
    assert "trap.py" not in result.stderr


def test_check_code_lengths_over_limit_message_teaches_split_or_delete(tmp_path: Path) -> None:
    # Operator mandate (charness-artifacts/gather/2026-07-04-enforcing-quality-of-
    # ai-generated-code.md): the max-file-length constraint STAYS blocking; the
    # improvement is that the message teaches the north-star response instead of
    # leaving the _extra_lib/_lib evasion path implicit.
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "over.py").write_text("\n".join(f"print({i})" for i in range(361)) + "\n", encoding="utf-8")
    result = run_script(
        "scripts/check_code_lengths.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/demo/scripts/over.py",
    )
    assert result.returncode == 1
    assert "tokei code lines 361 exceed limit 360" in result.stderr
    assert "Split the file into a cohesive new module or delete code" in result.stderr
    assert "do not mechanically spill into an _extra_lib/_lib companion" in result.stderr

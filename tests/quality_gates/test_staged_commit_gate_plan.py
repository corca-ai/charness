from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from scripts.staged_commit_gate_plan import staged_commit_gate_plan

from .support import ROOT, run_script


def _labels(paths: list[str]) -> list[str]:
    return [command.label for command in staged_commit_gate_plan(ROOT, paths, ruff_path="")]


def _write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _git_init_and_stage(repo: Path, path: str, body: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", path], cwd=repo, check=True, capture_output=True, text=True)


def _write_predict_commit_stubs(repo: Path, *, length_fails: bool = False, attention_fails: bool = False) -> dict[str, str]:
    scripts = repo / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    length_exit = "1" if length_fails else "0"
    attention_exit = "1" if attention_fails else "0"
    _write_executable(
        scripts / "check_python_lengths.py",
        f"#!/usr/bin/env python3\nprint('length gate')\nraise SystemExit({length_exit})\n",
    )
    _write_executable(
        scripts / "validate_attention_state_visibility.py",
        f"#!/usr/bin/env python3\nprint('attention gate')\nraise SystemExit({attention_exit})\n",
    )
    _write_executable(
        scripts / "check_staged_mirror_drift.py",
        "#!/usr/bin/env python3\nprint('mirror gate')\n",
    )
    fake_bin = repo / "bin"
    fake_bin.mkdir()
    _write_executable(fake_bin / "ruff", "#!/usr/bin/env bash\necho ruff gate\n")
    return {**os.environ, "PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"}


def test_staged_commit_plan_includes_commit_only_python_gates() -> None:
    labels = _labels(["scripts/new_helper.py"])

    assert "py_compile (staged)" in labels
    assert "check-python-lengths (staged)" in labels
    assert "validate-attention-state-visibility" in labels
    assert "staged-plugin-mirror-drift" in labels


def test_run_slice_closeout_predict_commit_uses_shared_plan() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--predict-commit",
        "--paths",
        "scripts/new_helper.py",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    planned_labels = [command["label"] for command in payload["planned_commands"]]
    assert planned_labels == [command.label for command in staged_commit_gate_plan(ROOT, ["scripts/new_helper.py"])]


def test_predict_commit_rejects_length_violating_staged_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init_and_stage(repo, "scripts/too_long.py", "print('valid')\n")
    env = _write_predict_commit_stubs(repo, length_fails=True)

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--predict-commit", "--json", env=env)

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert payload["executed_commands"][-1]["command"].startswith("python3 scripts/check_python_lengths.py")


def test_predict_commit_rejects_attention_violating_staged_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init_and_stage(repo, "scripts/bad_attention.py", "print('valid')\n")
    env = _write_predict_commit_stubs(repo, attention_fails=True)

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--predict-commit", "--json", env=env)

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert payload["executed_commands"][-1]["command"].startswith("python3 scripts/validate_attention_state_visibility.py")


def test_predict_commit_accepts_clean_staged_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init_and_stage(repo, "scripts/clean.py", "print('valid')\n")
    env = _write_predict_commit_stubs(repo)

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--predict-commit", "--json", env=env)

    payload = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "completed"
    assert [step["returncode"] for step in payload["executed_commands"]] == [0, 0, 0, 0, 0]

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

from scripts.staged_commit_gate_plan import (
    GateCommand,
    collect_staged_paths,
    run_predict_commit,
    staged_commit_gate_plan,
)

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
        scripts / "check_staged_reversion.py",
        "#!/usr/bin/env python3\nprint('staged reversion gate')\n",
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

    assert "check-staged-reversion" in labels
    assert "py_compile (staged)" in labels
    assert "check-python-lengths (staged)" in labels
    assert "validate-attention-state-visibility" in labels
    assert "staged-plugin-mirror-drift" in labels


def test_gate_command_serializes_to_dict() -> None:
    assert GateCommand("demo", ("python3", "demo.py")).as_dict() == {
        "label": "demo",
        "argv": ["python3", "demo.py"],
    }


def test_collect_staged_paths_reports_git_error(monkeypatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args=[], returncode=1, stderr="no index\n"),
    )

    try:
        collect_staged_paths(ROOT)
    except RuntimeError as exc:
        assert str(exc) == "no index"
    else:
        raise AssertionError("expected RuntimeError")


def test_staged_commit_plan_covers_domain_and_markdown_triggers() -> None:
    labels = _labels(
        [
            "skills/public/demo/SKILL.md",
            "profiles/default/profile.yaml",
            ".agents/surfaces.json",
            "presets/default.yaml",
            "integrations/tool.json",
            "docs/usage.md",
        ]
    )

    assert "validate-skills" in labels
    assert "run-evals" in labels
    assert "validate-profiles" in labels
    assert "validate-adapters" in labels
    assert "validate-presets" in labels
    assert "validate-integrations" in labels
    assert "staged-plugin-mirror-drift" in labels
    assert "check-doc-links" in labels
    assert "check-markdown" in labels


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


def test_staged_commit_gate_plan_cli_json_and_text() -> None:
    json_result = run_script(
        "scripts/staged_commit_gate_plan.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert json_result.returncode == 0, json_result.stderr
    assert [item["label"] for item in json.loads(json_result.stdout)] == [
        "check-staged-reversion",
        "staged-plugin-mirror-drift",
        "check-doc-links",
        "check-markdown",
    ]

    text_result = run_script(
        "scripts/staged_commit_gate_plan.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/new_helper.py",
        "--no-ruff",
    )
    assert text_result.returncode == 0, text_result.stderr
    assert "check-python-lengths (staged)" in text_result.stdout
    assert "ruff (staged)" not in text_result.stdout


def _payload_sink(payload: dict[str, object], *, as_json: bool) -> int:
    assert as_json is True
    assert payload["status"] in {"planned", "failed", "completed"}
    return 0 if payload["status"] != "failed" else 1


def _runner(returncode: int, stdout: str = "", stderr: str = "") -> Callable[[Path, str, str], dict[str, object]]:
    def run_command(repo_root: Path, command: str, phase: str) -> dict[str, object]:
        return {"phase": phase, "command": command, "returncode": returncode, "stdout": stdout, "stderr": stderr}

    return run_command


def test_run_predict_commit_non_json_plan_empty_fail_and_success(capsys) -> None:
    assert run_predict_commit(ROOT, paths=[], as_json=False, plan_only=True, run_command=_runner(0), emit_payload=_payload_sink) == 0
    assert run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=False,
        plan_only=True,
        run_command=_runner(0),
        emit_payload=_payload_sink,
    ) == 0
    assert "charness pre-commit: check-doc-links" in capsys.readouterr().out
    assert run_predict_commit(ROOT, paths=[], as_json=False, plan_only=False, run_command=_runner(0), emit_payload=_payload_sink) == 0

    failure_rc = run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=False,
        plan_only=False,
        run_command=_runner(7, "bad stdout\n", "bad stderr\n"),
        emit_payload=_payload_sink,
    )
    captured = capsys.readouterr()
    assert failure_rc == 1
    assert "bad stdout" in captured.out
    assert "bad stderr" in captured.err

    success_rc = run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=False,
        plan_only=False,
        run_command=_runner(0),
        emit_payload=_payload_sink,
    )
    assert success_rc == 0
    assert "charness pre-commit: ok" in capsys.readouterr().out


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
    assert [step["returncode"] for step in payload["executed_commands"]] == [0, 0, 0, 0, 0, 0]

"""Muse lane-executor coverage for `charness task run`.

Cohesive home for the muse-executor slice: argument shape, curated effort
presets, executor validation, the prompt-file lane, and the lane-runner
bootstrap insert flagged by the release changed-line gate.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.task_run import task_run, task_run_plan

from .test_task_run_fixtures import _repo, _run


def test_lane_runner_module_bootstraps_repo_root_on_import() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "task_run" / "task_run_lane_runner.py"
    probe = (
        "import sys; "
        f"root = {str(repo_root)!r}; "
        "sys.path = [entry for entry in sys.path if entry not in ('', root)]; "
        "import importlib.util; "
        "spec = importlib.util.spec_from_file_location("
        f"'lane_runner_probe', {str(module_path)!r}); "
        "module = importlib.util.module_from_spec(spec); "
        "spec.loader.exec_module(module); "
        "assert root in sys.path, 'bootstrap did not root the repo'"
    )
    # Children inherit os.environ (minus PYTHONPATH) so coverage tracing
    # propagates under the release changed-line gate.
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd="/tmp",
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_muse_arguments_pin_high_effort_and_prompt_file(tmp_path: Path) -> None:
    git_common_dir = tmp_path / ".git"
    git_common_dir.mkdir()
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("implement the slice", encoding="utf-8")
    assert task_run.build_muse_args(
        effort="high",
        prompt_file=prompt_file,
        writable_dirs=[git_common_dir],
    ) == [
        "--reasoning-effort",
        "high",
        "--disable-approval",
        "--workspace",
        str(git_common_dir),
        "--prompt-file",
        str(prompt_file),
    ]


def test_muse_effort_is_limited_to_curated_presets() -> None:
    with pytest.raises(task_run.TaskRunError, match="medium, high, xhigh, max"):
        task_run.build_muse_args(effort="ultra", prompt_file=Path("prompt.md"))
    with pytest.raises(task_run.TaskRunError, match="--executor must be one of"):
        task_run_plan.resolve_task_inputs(
            Path("."),
            target_path=Path("lane"),
            branch="lane/x",
            base="HEAD",
            lane=None,
            scopes=["module.py"],
            prompt="instructions",
            codex="codex",
            executor="bogus",
            effort="high",
            task_id=None,
            prepare=None,
            require_change=None,
            skip_prepare=False,
            allow_no_change=False,
            timeout_seconds=1,
        )


def test_task_run_muse_executor_uses_prompt_file_and_high_effort(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    captured_args = tmp_path / "muse-args.txt"
    captured_prompt = tmp_path / "muse-prompt.txt"
    executable = tmp_path / "muse"
    executable.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$@\" > {shlex.quote(os.fspath(captured_args))}\n"
        "prev=\"\"\n"
        "for arg in \"$@\"; do\n"
        f"  if [ \"$prev\" = \"--prompt-file\" ]; then cat \"$arg\" > {shlex.quote(os.fspath(captured_prompt))}; fi\n"
        "  prev=\"$arg\"\n"
        "done\n"
        "printf 'VALUE = 2\\n' > module.py\n"
        "printf 'task complete\\n'\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)

    payload = _run(
        repo,
        tmp_path,
        executable,
        executor="muse",
        effort="high",
    )

    assert payload["status"] == "completed", payload
    assert payload["executor"]["kind"] == "muse"
    assert payload["executor"]["effort"] == "high"
    assert payload["executor"]["model"] == "default"
    assert payload["executor"]["timeout_scope"] == "muse-exec"
    assert "codex" not in payload
    args = captured_args.read_text(encoding="utf-8").splitlines()
    assert args[:2] == ["exec", "--reasoning-effort"]
    assert args[args.index("--reasoning-effort") + 1] == "high"
    assert "--disable-approval" in args
    assert "-m" not in args
    assert "-" not in args
    prompt_path = Path(args[args.index("--prompt-file") + 1])
    assert prompt_path.name == "prompt.md"
    assert captured_prompt.read_text(encoding="utf-8") == "update the module"

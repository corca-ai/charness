"""Lane runner command construction and receipt recording."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import task_run_support as _support  # noqa: E402

build_codex_command = _support.build_codex_command
build_muse_command = _support.build_muse_command


def lane_command(
    *,
    executor: str,
    executable: str,
    effort: str,
    prompt: str,
    execution_runtime_path: Path,
    writable_dirs: Sequence[Path],
) -> list[str]:
    """Build the lane runner command for the selected executor.

    Codex lanes read the prompt from stdin (`-`); `muse exec` takes no stdin
    prompt, so muse lanes carry it via a prompt file in the lane-private
    execution root.
    """
    if executor == "muse":
        prompt_file = execution_runtime_path / "prompt.md"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt, encoding="utf-8")
        return build_muse_command(
            executable,
            effort=effort,
            prompt_file=prompt_file,
            writable_dirs=writable_dirs,
        )
    return build_codex_command(
        executable,
        effort=effort,
        writable_dirs=writable_dirs,
    )


def record_lane_runner(
    payload: dict[str, Any],
    *,
    executor: str,
    executable: str,
    effort: str,
    timeout_seconds: int,
) -> None:
    """Record the lane runner block and its legacy `codex` alias."""
    block = {
        "kind": executor,
        "executable": executable,
        "model": _support.TASK_MODEL if executor == "codex" else _support.TASK_MUSE_MODEL,
        "effort": effort,
        "timeout_seconds": timeout_seconds,
        "timeout_scope": f"{executor}-exec",
    }
    payload["executor"] = block
    if executor == "codex":
        # Legacy alias: result.json readers address the runner as "codex".
        payload["codex"] = block

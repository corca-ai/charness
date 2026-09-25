"""Hooks status command."""

from __future__ import annotations

import argparse


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    CharnessError,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.process import (  # noqa: E402
    _load_task_run_lib,
)


def cmd_hooks_status(args: argparse.Namespace) -> int:
    _load_task_run_lib(args)
    from scripts.hooks import host_hook_command_guard_install as guard_install

    try:
        adapter = guard_install.adapter_from_file(args.adapter_file)
    except ValueError as exc:
        raise CharnessError(str(exc)) from exc
    payload, code = guard_install.status_payload(
        args.repo_root.resolve(), args.home_root.resolve(), adapter
    )
    emit_yaml(payload)
    return code

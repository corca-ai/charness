"""Goal Run command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli import bootstrap as _bootstrap  # noqa: E402
from scripts.cli.bootstrap import (  # noqa: E402
    REPO_URL,
    CharnessError,
    ensure_checkout,
    resolve_repo_root,
    run,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.common import (  # noqa: E402
    parse_repo_script_payload,
)
from scripts.cli.process import (  # noqa: E402
    resolve_repo_python,
)


def _resolve_goal_run_helper_repo_root(args: argparse.Namespace) -> Path:
    if args.charness_checkout is not None:
        repo_root = args.charness_checkout.resolve()
        managed = False
    elif _bootstrap.EMBEDDED_REPO_ROOT is not None:
        repo_root = _bootstrap.EMBEDDED_REPO_ROOT
        managed = False
    else:
        repo_root, managed = resolve_repo_root(args.home_root.resolve(), None)
    ensure_checkout(
        repo_root,
        managed=managed,
        repo_url=getattr(args, "repo_url", REPO_URL),
        allow_clone=False,
        allow_pull=False,
    )
    helper = repo_root / "skills" / "public" / "achieve" / "scripts" / "goal_run_pickup.py"
    if not helper.is_file():
        raise CharnessError(
            "missing issue-native Goal Run pickup `skills/public/achieve/scripts/goal_run_pickup.py`; "
            f"searched stable source checkout `{repo_root}`. Run `charness update`, or pass "
            "`--charness-checkout <path>` to a checkout that contains the current pickup helper."
        )
    return repo_root


def _goal_run_script_args(args: argparse.Namespace, target_repo_root: Path) -> list[str]:
    return [
        "--repo-root",
        str(target_repo_root),
        "--objective",
        args.objective,
    ]


def cmd_goal_run(args: argparse.Namespace) -> int:
    helper_repo_root = _resolve_goal_run_helper_repo_root(args)
    target_repo_root = (args.repo_root or Path.cwd()).resolve()
    script_args = _goal_run_script_args(args, target_repo_root)
    python_executable = resolve_repo_python(helper_repo_root)
    result = run(
        [
            python_executable,
            "skills/public/achieve/scripts/goal_run_pickup.py",
            *script_args,
        ],
        cwd=helper_repo_root,
    )
    stdout = result.stdout.strip()
    payload: object | None = None
    if stdout:
        try:
            payload = parse_repo_script_payload(
                stdout, "skills/public/achieve/scripts/goal_run_pickup.py"
            )
        except CharnessError:
            payload = None
        if not isinstance(payload, (dict, list)):
            # Keep a malformed helper response visible without mixing it into stderr.
            payload = None
    if payload is not None:
        emit_yaml(payload)
    elif stdout:
        emit_yaml({"helper_stdout": stdout})
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    return result.returncode

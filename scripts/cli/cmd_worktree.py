"""Worktree commands."""

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

from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.process import (  # noqa: E402
    _load_worktree_audit_lib,
    _load_worktree_cleanup_lib,
    _load_worktree_create_lib,
    _load_worktree_exec_lib,
    _load_worktree_lib,
    _resolve_worktree_target,
)


def cmd_worktree_doctor(args: argparse.Namespace) -> int:
    lib = _load_worktree_lib(args)
    payload = lib.run_doctor(
        _resolve_worktree_target(args),
        require_isolation=getattr(args, "require_isolation", False),
    )
    emit_yaml(payload)
    return 0 if payload.get("status") == lib.PASS else 1


def cmd_worktree_prepare(args: argparse.Namespace) -> int:
    lib = _load_worktree_lib(args)
    payload = lib.run_prepare(
        _resolve_worktree_target(args),
        force=args.force,
        dependency_reuse=not args.no_dependency_reuse,
    )
    emit_yaml(payload)
    return 0 if payload.get("status") == lib.PASS else 1


def cmd_worktree_audit(args: argparse.Namespace) -> int:
    lib = _load_worktree_audit_lib(args)
    target = _resolve_worktree_target(args)
    audit_payload = lib.run_audit(target, stale_days=args.stale_days, include_doctor=args.doctor)
    output: dict[str, object] = {"audit": audit_payload}

    if audit_payload.get("status") == lib.PASS:
        exit_code = 0
    elif audit_payload.get("status") == lib.WARN:
        exit_code = 1
    else:
        exit_code = 2

    if args.prune and audit_payload.get("status") != lib.FAIL:
        prune_payload = lib.run_prune(target)
        output["prune"] = prune_payload
        if prune_payload["status"] != lib.PASS:
            exit_code = max(exit_code, 2)
        else:
            remaining = prune_payload.get("remaining_after_prune") or {}
            if remaining.get("prunable", 0) == 0 and remaining.get("stale", 0) == 0:
                exit_code = 0
    emit_yaml(output)
    return exit_code


def cmd_worktree_cleanup(args: argparse.Namespace) -> int:
    lib = _load_worktree_cleanup_lib(args)
    payload = lib.run_cleanup(
        _resolve_worktree_target(args),
        target_path=args.path,
        delete_merged_branch=args.delete_merged_branch,
        branch_base=args.branch_base,
        yes=args.yes,
        force=args.force,
    )
    emit_yaml(payload)
    return 0 if payload.get("status") == lib.PASS else 1


def cmd_worktree_create(args: argparse.Namespace) -> int:
    lib = _load_worktree_create_lib(args)
    payload = lib.run_create(
        _resolve_worktree_target(args),
        target_path=args.path,
        branch=args.branch,
        base=args.base,
        detach=args.detach,
        prepare=args.prepare,
        dry_run=args.dry_run,
        force=args.force,
        ephemeral=args.ephemeral,
        owned=args.owned,
    )
    emit_yaml(payload)
    if payload.get("status") == lib.PASS:
        return 0
    if payload.get("status") == lib.WARN:
        return 1
    return 2


def cmd_worktree_exec(args: argparse.Namespace) -> int:
    target = _resolve_worktree_target(args)
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    try:
        lib = _load_worktree_exec_lib(args)
        return lib.run_exec(target, command, allow_main=args.allow_main)
    except (RuntimeError, ImportError, OSError) as exc:
        emit_yaml(
            {
                "status": "fail",
                "repo_root": str(target),
                "command": command,
                "error": str(exc),
            }
        )
        return 2

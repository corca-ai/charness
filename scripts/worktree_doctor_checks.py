from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_state = import_repo_module(__file__, "scripts.worktree_doctor_state")
CheckResult = _state.CheckResult
DEFAULT_DOCTOR_TIMEOUT_SECONDS = _state.DEFAULT_DOCTOR_TIMEOUT_SECONDS
FAIL = _state.FAIL
PASS = _state.PASS
SKIPPED = _state.SKIPPED
tail = _state.tail


def git_common_dir(repo_root: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (repo_root / candidate).resolve()
    return candidate if candidate.is_dir() else None


def git_config_value(repo_root: Path, key: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def resolve_hooks_dir(repo_root: Path, common_dir: Path | None) -> tuple[Path | None, str]:
    configured = git_config_value(repo_root, "core.hooksPath")
    if configured:
        candidate = Path(configured)
        if not candidate.is_absolute():
            candidate = (repo_root / candidate).resolve()
        return candidate, "configured"
    if common_dir is not None:
        return common_dir / "hooks", "default"
    return None, "unknown"


def shim_references_lefthook(hook_path: Path) -> bool:
    try:
        text = hook_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "lefthook" in text.lower()


def lefthook_resolves_from_worktree(repo_root: Path) -> tuple[bool, str]:
    node_modules = repo_root / "node_modules"
    if node_modules.is_dir():
        for entry in node_modules.glob("lefthook-*/bin/lefthook"):
            if entry.is_file() and os.access(entry, os.X_OK):
                return True, str(entry.relative_to(repo_root))
        bin_lefthook = node_modules / ".bin" / "lefthook"
        if bin_lefthook.is_file() and os.access(bin_lefthook, os.X_OK):
            return True, str(bin_lefthook.relative_to(repo_root))
    on_path = shutil.which("lefthook")
    if on_path:
        return True, f"PATH:{on_path}"
    return False, ""


def husky_marker_directory(hooks_path_value: str) -> Path | None:
    """Return the worktree-relative `_/` directory that must exist for husky's
    hook surface to work, or None if `core.hooksPath` does not look husky-shaped.

    Husky 9 (current default) sets `core.hooksPath=.husky`; the actual hook
    entry points live under `.husky/_/`. Husky 8 set `core.hooksPath=.husky/_`
    directly. Both shapes need `.husky/_/` to exist in this worktree.
    """
    if not hooks_path_value:
        return None
    candidate = Path(hooks_path_value)
    parts = candidate.parts
    if not parts:
        return None
    if parts[-1].startswith("_"):
        return candidate
    if parts[-1] == ".husky":
        return candidate / "_"
    return None


def _check_git_common_dir(common_dir: Path | None) -> CheckResult:
    if common_dir is None:
        return CheckResult(
            id="git_common_dir",
            status=FAIL,
            detail="`git rev-parse --git-common-dir` did not return a usable directory; this path is not a git checkout.",
            next_action="Run charness worktree doctor inside a git worktree.",
        )
    return CheckResult(
        id="git_common_dir",
        status=PASS,
        detail=f"git common dir resolved at {common_dir}",
    )


def _check_hooks_path(configured: str | None, hooks_dir: Path | None, source: str) -> CheckResult:
    if configured is None:
        return CheckResult(
            id="hooks_path",
            status=SKIPPED,
            detail="core.hooksPath is unset; using git's default hooks directory.",
        )
    if hooks_dir is None or not hooks_dir.is_dir():
        return CheckResult(
            id="hooks_path",
            status=FAIL,
            detail=f"core.hooksPath={configured!r} but the resolved directory does not exist in this worktree.",
            next_action="Run `charness worktree prepare` so the hook manager re-installs the hooksPath target for this worktree.",
        )
    return CheckResult(
        id="hooks_path",
        status=PASS,
        detail=f"core.hooksPath={configured!r} -> {hooks_dir} ({source})",
    )


def _check_lefthook_shim(repo_root: Path, hooks_dir: Path | None) -> CheckResult:
    if hooks_dir is None:
        return CheckResult(
            id="lefthook_shim",
            status=SKIPPED,
            detail="No hooks directory could be resolved; skipping lefthook shim probe.",
        )
    shim_path = hooks_dir / "pre-commit"
    if not shim_path.is_file():
        return CheckResult(
            id="lefthook_shim",
            status=SKIPPED,
            detail=f"No pre-commit hook at {shim_path}; nothing to probe.",
        )
    if not shim_references_lefthook(shim_path):
        return CheckResult(
            id="lefthook_shim",
            status=SKIPPED,
            detail=f"pre-commit hook at {shim_path} does not reference lefthook.",
        )
    resolved, where = lefthook_resolves_from_worktree(repo_root)
    if resolved:
        return CheckResult(
            id="lefthook_shim",
            status=PASS,
            detail=f"lefthook resolvable from this worktree via {where}.",
        )
    return CheckResult(
        id="lefthook_shim",
        status=FAIL,
        detail=(
            "pre-commit shim references lefthook but no node_modules/lefthook-*/bin/lefthook is present "
            "and `lefthook` is not on PATH for this worktree. The shim will silently exit 0 and skip hooks."
        ),
        next_action="Run `charness worktree prepare` to install dependencies and re-run `lefthook install` for this worktree.",
    )


def _check_husky_dir(repo_root: Path, configured: str | None) -> CheckResult:
    marker = husky_marker_directory(configured or "")
    if marker is None:
        return CheckResult(
            id="husky_dir",
            status=SKIPPED,
            detail="core.hooksPath does not point at a husky `_` directory; skipping.",
        )
    target = repo_root / marker
    if target.is_dir():
        return CheckResult(
            id="husky_dir",
            status=PASS,
            detail=f"husky directory {target} present in this worktree.",
        )
    return CheckResult(
        id="husky_dir",
        status=FAIL,
        detail=f"core.hooksPath references {marker} but {target} does not exist in this worktree.",
        next_action="Run `charness worktree prepare` so the husky install step regenerates the hooks directory for this worktree.",
    )


def run_canonical_checks(repo_root: Path, *, disabled: set[str]) -> list[CheckResult]:
    repo_root = repo_root.resolve()
    results: list[CheckResult] = []
    common_dir = git_common_dir(repo_root)
    hooks_dir, hooks_source = resolve_hooks_dir(repo_root, common_dir)
    configured_hooks_path = git_config_value(repo_root, "core.hooksPath")
    canonical_specs = (
        ("git_common_dir", lambda: _check_git_common_dir(common_dir)),
        ("hooks_path", lambda: _check_hooks_path(configured_hooks_path, hooks_dir, hooks_source)),
        ("lefthook_shim", lambda: _check_lefthook_shim(repo_root, hooks_dir)),
        ("husky_dir", lambda: _check_husky_dir(repo_root, configured_hooks_path)),
    )
    for check_id, runner in canonical_specs:
        if check_id in disabled:
            continue
        results.append(runner())
    return results


def _run_manifest_doctor_command(
    entry: dict[str, Any], repo_root: Path
) -> CheckResult:
    check_id = entry.get("id")
    argv = list(entry.get("argv") or [])
    timeout = int(entry.get("timeout_seconds") or DEFAULT_DOCTOR_TIMEOUT_SECONDS)
    expect_exit = int(entry.get("expect_exit_code", 0))
    next_hint = entry.get("next_action_hint")
    try:
        result = subprocess.run(
            argv,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        return CheckResult(
            id=check_id,
            status=FAIL,
            detail=f"command not found: {exc.filename or argv[0]}",
            next_action=next_hint,
            source="manifest",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            id=check_id,
            status=FAIL,
            detail=f"command timed out after {timeout}s: {argv}",
            next_action=next_hint,
            source="manifest",
        )
    if result.returncode == expect_exit:
        return CheckResult(
            id=check_id,
            status=PASS,
            detail=f"exit_code={result.returncode}",
            source="manifest",
        )
    last = tail((result.stderr or result.stdout or "").strip())
    return CheckResult(
        id=check_id,
        status=FAIL,
        detail=f"exit_code={result.returncode} (expected {expect_exit}); tail: {last}",
        next_action=next_hint,
        source="manifest",
    )


def run_manifest_doctor_checks(repo_root: Path, manifest: dict[str, Any]) -> list[CheckResult]:
    doctor = manifest.get("doctor") or {}
    checks = doctor.get("checks") or []
    return [_run_manifest_doctor_command(entry, repo_root) for entry in checks]

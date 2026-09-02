from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from runtime_bootstrap import import_repo_module

_state = import_repo_module(__file__, "scripts.worktree_doctor_state")
CheckResult = _state.CheckResult
FAIL = _state.FAIL
PASS = _state.PASS
SKIPPED = _state.SKIPPED
_manifest = import_repo_module(__file__, "scripts.worktree_doctor_manifest")
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
TIMEOUT_EXIT_CODE = _subprocess_guard.TIMEOUT_EXIT_CODE
run_manifest_doctor_checks = _manifest.run_manifest_doctor_checks


# `git rev-parse` answers about the repository it DISCOVERS, and these three
# variables override that discovery. Left in place, a doctor run from inside a
# git hook or under `git rebase --exec` would render a verdict about a repository
# the caller never named -- silently, since the output looks identical. Scrubbed
# for every probe here so a verdict is always about `--repo-root`.
_GIT_DISCOVERY_ENV = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")


def _git_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in _GIT_DISCOVERY_ENV}


def _git_output(repo_root: Path, *args: str) -> str | None:
    """One read-only git probe, discovery-scrubbed. `None` for any non-answer.

    Every git question this module asks goes through here so the discovery scrub
    cannot be applied to some probes and not others.
    """
    try:
        result = run_process(
            ["git", *args],
            cwd=repo_root,
            timeout_seconds=5,
            env=_git_env(),
        )
    except (FileNotFoundError, NotADirectoryError):
        return None
    if result.returncode in (TIMEOUT_EXIT_CODE,):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


@dataclass(frozen=True)
class GitCheckoutFacts:
    """One coherent read of the checkout facts consumed by canonical doctor checks."""

    common_dir: Path | None
    own_dir: Path | None
    is_bare: bool | None
    hooks_path: Path | None


def _resolved_git_output_path(
    repo_root: Path, raw: str, *, require_directory: bool = True
) -> Path | None:
    try:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        resolved = candidate.resolve()
    except (OSError, RuntimeError, ValueError):
        return None
    return resolved if not require_directory or resolved.is_dir() else None


def _hooks_path_from_layout(repo_root: Path, layout) -> Path:
    for config in (layout.git_dir / "config", layout.common_dir / "config"):
        try:
            text = config.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.lower().startswith("hookspath"):
                continue
            _, _, value = stripped.partition("=")
            value = value.strip().strip('"')
            if not value:
                continue
            path = Path(value)
            if not path.is_absolute():
                path = repo_root / path
            try:
                return path.resolve()
            except OSError:
                return path
    return layout.common_dir / "hooks"


def git_checkout_facts(repo_root: Path, *, include_hooks_path: bool = True) -> GitCheckoutFacts:
    """Read one checkout snapshot, optionally omitting the hooks target."""
    from scripts.core.git_checkout import is_bare_repository, layout_from_files

    layout = layout_from_files(repo_root)
    if layout is not None:
        return GitCheckoutFacts(
            layout.common_dir,
            layout.git_dir,
            is_bare_repository(repo_root),
            _hooks_path_from_layout(repo_root, layout) if include_hooks_path else None,
        )
    rev_parse_args = [
        "rev-parse",
        "--git-common-dir",
        "--git-dir",
        "--is-bare-repository",
    ]
    expected_lines = 3
    if include_hooks_path:
        rev_parse_args.extend(["--git-path", "hooks"])
        expected_lines = 4
    raw = _git_output(
        repo_root,
        *rev_parse_args,
    )
    lines = raw.splitlines() if raw is not None else []
    if len(lines) != expected_lines:
        common_dir = own_dir = None
        is_bare = None
        hooks_path = None
    else:
        common_dir = _resolved_git_output_path(repo_root, lines[0])
        own_dir = _resolved_git_output_path(repo_root, lines[1])
        is_bare = lines[2] == "true" if lines[2] in {"true", "false"} else None
        hooks_path = (
            _resolved_git_output_path(repo_root, lines[3], require_directory=False)
            if include_hooks_path
            else None
        )
    return GitCheckoutFacts(
        common_dir=common_dir,
        own_dir=own_dir,
        is_bare=is_bare,
        hooks_path=hooks_path,
    )


def main_worktree(common_dir: Path | None) -> Path | None:
    """The checkout that owns the repository, for REPORTING only.

    Best-effort by design and deliberately not the discriminator: a repository
    created with `--separate-git-dir`, or one whose git dir is simply not named
    `.git`, has no `<common>/..` main worktree to name. `checkout_isolation`
    decides isolation without this, so a `None` here costs a nicer message and
    never a verdict.
    """
    if common_dir is None or common_dir.name != ".git":
        return None
    return common_dir.parent


def checkout_isolation(facts: GitCheckoutFacts) -> bool | None:
    """Derive the index-sharing verdict from an already-read checkout snapshot."""
    if facts.is_bare is not False or facts.own_dir is None or facts.common_dir is None:
        return None
    return facts.own_dir != facts.common_dir


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
    """Return the hooks target's `_/` directory required by husky, or None if
    the effective hooks path does not look husky-shaped.

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
            next_step="Run charness worktree doctor inside a git worktree.",
        )
    return CheckResult(
        id="git_common_dir",
        status=PASS,
        detail=f"git common dir resolved at {common_dir}",
    )


def _check_hooks_path(hooks_dir: Path | None, source: str) -> CheckResult:
    if hooks_dir is None:
        return CheckResult(
            id="hooks_path",
            status=FAIL,
            detail="`git rev-parse --git-path hooks` did not return a usable hooks directory.",
            next_step="Run charness worktree doctor inside a git worktree.",
        )
    if source == "default":
        return CheckResult(
            id="hooks_path",
            status=SKIPPED,
            detail=f"effective hooks target is Git's default directory: {hooks_dir}.",
        )
    if not hooks_dir.is_dir():
        return CheckResult(
            id="hooks_path",
            status=FAIL,
            detail=f"effective core.hooksPath target {hooks_dir} does not exist in this worktree.",
            next_step="Run `charness worktree prepare` so the hook manager re-installs the hooksPath target for this worktree.",
        )
    return CheckResult(
        id="hooks_path",
        status=PASS,
        detail=f"effective core.hooksPath target {hooks_dir} ({source}).",
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
        next_step="Run `charness worktree prepare` to install dependencies and re-run `lefthook install` for this worktree.",
    )


def _check_husky_dir(repo_root: Path, hooks_path: Path | str | None) -> CheckResult:
    marker = husky_marker_directory(str(hooks_path) if hooks_path is not None else "")
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
        next_step="Run `charness worktree prepare` so the husky install step regenerates the hooks directory for this worktree.",
    )


def _check_worktree_isolation(
    repo_root: Path,
    facts: GitCheckoutFacts,
    *,
    require_isolation: bool,
) -> CheckResult:
    """Does this checkout share the parent's worktree and index, or its own?

    SC10 / owner ruling 2026-08-15. The rule this replaces was a prose sentence in
    a spawn prompt telling write-capable subagents not to run mutating git ops,
    which is not enforcement: five of them ran concurrently in one shared tree
    under it. Isolation gives the agent its own index and HEAD instead of
    policing the parent's. Said plainly, because the ruling gives something up:
    there is no refusal message, and a mutating git op still SUCCEEDS -- in a
    throwaway tree where it harms nothing.

    What this check does NOT establish, since the PASS message used to imply it:
    the config plane is still shared. `core.hooksPath` in a linked worktree
    points into the parent, so the agent's commits run parent-owned hook scripts.
    "Separate index and HEAD" is the measured property; "the parent is
    unreachable" is not.

    The fact is reported on every run; it is ENFORCED only when the caller says
    isolation is required. A solo operator working in the main worktree is doing
    nothing wrong, so failing there unasked would train operators to ignore this
    check -- and a check operators ignore protects nothing. The parent spawning a
    write-capable agent is the one who knows, and it is the one that passes
    `--require-isolation`.
    """
    common_dir = facts.common_dir
    isolated = checkout_isolation(facts)
    if isolated is None:
        return CheckResult(
            id="worktree_isolation",
            status=FAIL if require_isolation else SKIPPED,
            detail=(
                "this checkout's own git dir could not be compared against the shared one "
                "(a bare repository, or `git rev-parse` did not answer), so whether it is "
                "isolated is UNKNOWN -- not confirmed."
            ),
            next_step=(
                "Give the write-capable agent a decidable checkout: `charness worktree "
                "create --path <path> --branch <branch> --prepare`, then re-run here."
            )
            if require_isolation
            else None,
        )
    if isolated:
        main = main_worktree(common_dir)
        where = f"; the main worktree is at {main}" if main is not None else ""
        return CheckResult(
            id="worktree_isolation",
            status=PASS,
            # States what was MEASURED -- a separate git dir, hence a separate
            # index and HEAD -- rather than the broader "the parent is not
            # reachable", which this check does not establish and which is not
            # even true of the config plane: `core.hooksPath` here still points
            # into the parent, so the agent's commits run parent-owned hooks.
            detail=(
                f"{repo_root} has its own git dir ({facts.own_dir}), separate from the "
                f"shared one ({common_dir}), so its index and HEAD are its own{where}."
            ),
        )
    if not require_isolation:
        return CheckResult(
            id="worktree_isolation",
            status=SKIPPED,
            detail=(
                f"{repo_root} IS the main worktree. Correct for an operator working directly; "
                "a write-capable subagent spawned here would share this tree and index."
            ),
        )
    return CheckResult(
        id="worktree_isolation",
        status=FAIL,
        detail=(
            f"isolation was required but {repo_root} is the main worktree, so a write-capable "
            "agent here shares the parent's tree and index. A stray `git checkout`, `reset`, or "
            "`add` lands in the commit the parent is preparing."
        ),
        next_step=(
            "Create the agent its own checkout first: `charness worktree create --path "
            "<path> --branch <branch> --prepare`, and run the write-capable work there."
        ),
    )


def run_canonical_checks_with_facts(
    repo_root: Path, *, disabled: set[str], require_isolation: bool = False
) -> tuple[list[CheckResult], GitCheckoutFacts]:
    repo_root = repo_root.resolve()
    results: list[CheckResult] = []
    hook_check_ids = {"hooks_path", "lefthook_shim", "husky_dir"}
    facts = git_checkout_facts(
        repo_root,
        include_hooks_path=bool(hook_check_ids.difference(disabled)),
    )
    common_dir = facts.common_dir
    hooks_dir = facts.hooks_path
    if hooks_dir is None:
        hooks_source = "unknown"
    elif common_dir is not None and hooks_dir == common_dir / "hooks":
        hooks_source = "default"
    else:
        hooks_source = "configured"
    canonical_specs = (
        ("git_common_dir", lambda: _check_git_common_dir(common_dir)),
        (
            "worktree_isolation",
            lambda: _check_worktree_isolation(
                repo_root, facts, require_isolation=require_isolation
            ),
        ),
        ("hooks_path", lambda: _check_hooks_path(hooks_dir, hooks_source)),
        ("lefthook_shim", lambda: _check_lefthook_shim(repo_root, hooks_dir)),
        ("husky_dir", lambda: _check_husky_dir(repo_root, hooks_dir)),
    )
    for check_id, runner in canonical_specs:
        if check_id in disabled:
            continue
        results.append(runner())
    return results, facts


def run_canonical_checks(
    repo_root: Path, *, disabled: set[str], require_isolation: bool = False
) -> list[CheckResult]:
    """Run canonical checks while keeping the established list return shape."""
    results, _facts = run_canonical_checks_with_facts(
        repo_root,
        disabled=disabled,
        require_isolation=require_isolation,
    )
    return results

"""Standalone-copy bootstrap closure: repo resolution, checkout, and CLI re-exec."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

PACKAGE_ID = "charness"
REPO_URL = "https://github.com/corca-ai/charness"
BLOCKING_DOCTOR_DISPOSITIONS = {
    "blocking-support-sync-needed",
    "blocking-install-needed",
    "blocking-failure",
}
TOOL_UPDATE_FAILURE_STATUSES = frozenset({"failed", "updated-not-ready", "refreshed-not-ready"})
TOOL_SUPPORT_FAILURE_STATUSES = frozenset(
    {"failed", "error", "runner_error", "invalid", "not-ready"}
)
TOOL_DOCTOR_FAILURE_STATUSES = frozenset({"failed", "unhealthy", "not-ready"})
BOOTSTRAP_RUNTIME_RELATIVE_PATH = "scripts/core/bootstrap_runtime.py"
_CLI_REEXEC_GUARD_ENV = "CHARNESS_CLI_REEXECUTED"
_MUTATING_TOOL_EVENTS = frozenset(
    {"tool-update", "tool-install", "tool-repair", "tool-sync-support"}
)
REPAIRABLE_TOOL_IDS = {"agent-browser"}
CAPABILITY_LOCAL_GITIGNORE_LINE = "/.charness/local/"
AGENT_BROWSER_REPAIR_CAVEAT = (
    "Runtime repair is post-hoc mitigation only; invocation-bound "
    "agent-browser Chrome/profile teardown remains upstream/unproven."
)
_BOOTSTRAP_PYTHON_CACHE: dict[str, str] = {}


_CLI_TREE_ROOT = Path(__file__).resolve().parent.parent.parent
EMBEDDED_REPO_ROOT = (
    _CLI_TREE_ROOT if (_CLI_TREE_ROOT / "packaging" / "charness.json").is_file() else None
)
SCRIPT_PATH = None


def set_entry_context(embedded_repo_root, script_path):
    """Record the running entry's roots (called by the root shim on import)."""
    global EMBEDDED_REPO_ROOT, SCRIPT_PATH
    EMBEDDED_REPO_ROOT = embedded_repo_root
    SCRIPT_PATH = script_path


class CharnessError(Exception):
    pass


def resolve_state_home(home_root: Path) -> Path:
    override = os.environ.get("CHARNESS_STATE_HOME")
    if override:
        return Path(override).expanduser().resolve()
    xdg_root = os.environ.get("XDG_STATE_HOME")
    if xdg_root:
        return Path(xdg_root).expanduser().resolve()
    return home_root / ".local" / "state"


def default_state_root(home_root: Path) -> Path:
    return resolve_state_home(home_root) / PACKAGE_ID


def managed_checkout_root(home_root: Path) -> Path:
    return home_root / ".agents" / "src" / PACKAGE_ID


def default_plugin_root(home_root: Path) -> Path:
    return home_root / ".codex" / "plugins" / PACKAGE_ID


def default_codex_marketplace_path(home_root: Path) -> Path:
    return home_root / ".agents" / "plugins" / "marketplace.json"


def default_codex_cache_root(home_root: Path) -> Path:
    return home_root / ".codex" / "plugins" / "cache"


def default_claude_wrapper_path(home_root: Path) -> Path:
    return home_root / ".local" / "bin" / "claude-charness"


def default_cli_path(home_root: Path) -> Path:
    return home_root / ".local" / "bin" / "charness"


def default_install_state_path(home_root: Path) -> Path:
    return default_state_root(home_root) / "install-state.json"


def run(
    command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    from scripts.core.subprocess_guard import run_process

    # The repo's one spawn primitive (#768). No timeout so callers keep the
    # historical wait-forever contract; `None` cwd still inherits.
    return run_process(command, cwd=cwd or Path.cwd(), env=env, timeout_seconds=None)


def expect_success(result: subprocess.CompletedProcess[str], context: str) -> None:
    if result.returncode != 0:
        raise CharnessError(
            f"{context} failed with exit code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def is_git_checkout(path: Path) -> bool:
    return (path / ".git").exists()


def has_source_manifest(path: Path) -> bool:
    return (path / "packaging" / f"{PACKAGE_ID}.json").is_file()


def git_has_tracked_changes(path: Path) -> bool:
    result = run(["git", "status", "--short", "--untracked-files=no"], cwd=path)
    expect_success(result, f"git status in `{path}`")
    return any(line.strip() for line in result.stdout.splitlines())


def git_upstream_ref(path: Path) -> str | None:
    result = run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], cwd=path
    )
    if result.returncode != 0:
        return None
    upstream = result.stdout.strip()
    return upstream or None


def git_upstream_divergence(path: Path) -> tuple[str, int, int] | None:
    upstream = git_upstream_ref(path)
    if upstream is None:
        return None
    result = run(["git", "rev-list", "--left-right", "--count", f"HEAD...{upstream}"], cwd=path)
    if result.returncode != 0:
        return None
    counts = result.stdout.strip().split()
    if len(counts) != 2:
        return None
    try:
        ahead = int(counts[0])
        behind = int(counts[1])
    except ValueError:
        return None
    return upstream, ahead, behind


def _diverged_checkout_detail(repo_root: Path, upstream: str, *, max_commits: int = 10) -> str:
    """Name unique local commits and their upstream equivalence, best-effort.

    A diverged managed checkout keeps recurring when work lands in it
    directly: the operator cannot tell redundant commits (already upstream
    under another SHA, safe to reset away) from unique ones (migrate
    first). This never raises; reporting must not break the refusal it
    annotates.
    """
    try:
        log_result = run(
            [
                "git",
                "log",
                "--format=%h %s",
                f"{upstream}..HEAD",
                "--max-count",
                str(max_commits + 1),
            ],
            cwd=repo_root,
        )
        cherry_result = run(["git", "cherry", upstream], cwd=repo_root)
        if log_result.returncode != 0 or cherry_result.returncode != 0:
            return ""
        subjects = [line for line in log_result.stdout.splitlines() if line.strip()]
        unique = sorted(
            line[1:].strip() for line in cherry_result.stdout.splitlines() if line.startswith("+")
        )
        listed = subjects[:max_commits]
        lines = [
            f"Local commits not in `{upstream}`:",
            *[f"- {subject}" for subject in listed],
        ]
        if len(subjects) > max_commits:
            lines.append(f"- ... and {len(subjects) - max_commits} more")
        if not unique:
            lines.append(
                f"Every local commit already has a patch-equivalent commit in `{upstream}`, "
                f"so resetting the managed checkout to `{upstream}` loses no content."
            )
        else:
            lines.append(
                "These commits have no patch-equivalent upstream; migrate them first "
                "(cherry-pick or format-patch them into the dev checkout) and then "
                f"rebase or reset onto `{upstream}`, or keep dogfooding from this checkout."
            )
        return "\n".join(lines)
    except OSError:
        return ""


def packaging_version(path: Path) -> str | None:
    manifest_path = path / "packaging" / f"{PACKAGE_ID}.json"
    if not manifest_path.is_file():
        return None
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = data.get("version")
    return version if isinstance(version, str) else None


def resolve_target_repo_root(target_repo_root: Path | None) -> Path:
    return target_repo_root.resolve() if target_repo_root is not None else Path.cwd().resolve()


def read_install_state(home_root: Path) -> tuple[Path, bool] | None:
    path = default_install_state_path(home_root)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    repo_root = payload.get("repo_root")
    managed_checkout = payload.get("managed_checkout")
    if not isinstance(repo_root, str) or not isinstance(managed_checkout, bool):
        return None
    return Path(repo_root).resolve(), managed_checkout


def resolve_repo_root(home_root: Path, explicit_repo_root: Path | None) -> tuple[Path, bool]:
    if explicit_repo_root is not None:
        return explicit_repo_root.resolve(), False
    remembered = read_install_state(home_root)
    if remembered is not None and remembered[1] is True:
        return remembered
    return managed_checkout_root(home_root), True


def default_bootstrap_repo_url(home_root: Path, configured_repo_url: str) -> str:
    return configured_repo_url


def enforce_managed_cli_contract(
    *,
    home_root: Path,
    repo_root: Path,
    managed_checkout: bool,
    skip_cli_install: bool,
) -> None:
    if managed_checkout:
        return
    if skip_cli_install:
        return
    raise CharnessError(
        "official charness installs must use the managed checkout "
        f"`{managed_checkout_root(home_root)}`; for proof-only runs from another checkout, rerun with `--skip-cli-install`."
    )


def ensure_checkout(
    repo_root: Path, *, managed: bool, repo_url: str, allow_clone: bool, allow_pull: bool
) -> dict[str, object]:
    if has_source_manifest(repo_root):
        cloned = False
        pulled = False
        if allow_pull and managed:
            if not is_git_checkout(repo_root):
                raise CharnessError(
                    f"`{repo_root}` contains a source manifest but is not a git checkout"
                )
            if git_has_tracked_changes(repo_root):
                raise CharnessError(
                    f"managed checkout `{repo_root}` has tracked local changes; stop and resolve them before `charness update`"
                )
            pull_result = run(["git", "pull", "--ff-only"], cwd=repo_root)
            if pull_result.returncode != 0:
                divergence = git_upstream_divergence(repo_root)
                if divergence is not None:
                    upstream, ahead, behind = divergence
                    if ahead > 0 and behind > 0:
                        detail = _diverged_checkout_detail(repo_root, upstream)
                        raise CharnessError(
                            "managed checkout "
                            f"`{repo_root}` diverged from `{upstream}` (ahead {ahead}, behind {behind}); "
                            "`charness update` only fast-forwards managed checkouts. "
                            "If the local commit is intentional dogfood, run "
                            "`charness update --repo-root . --no-pull --skip-cli-install` from that checkout. "
                            f"Otherwise rebase or reset the managed checkout onto `{upstream}` and retry.\n"
                            f"{detail}\n"
                            f"STDOUT:\n{pull_result.stdout}\nSTDERR:\n{pull_result.stderr}"
                        )
            expect_success(pull_result, f"git pull in `{repo_root}`")
            pulled = True
        return {"repo_root": str(repo_root), "managed": managed, "cloned": cloned, "pulled": pulled}

    if repo_root.exists():
        if any(repo_root.iterdir()):
            raise CharnessError(
                f"`{repo_root}` exists but is not a charness source checkout; pass `--repo-root` or clean that path first"
            )
    elif not allow_clone:
        raise CharnessError(f"missing source checkout `{repo_root}`")

    if not managed and not allow_clone:
        raise CharnessError(f"missing explicit source checkout `{repo_root}`")

    repo_root.parent.mkdir(parents=True, exist_ok=True)
    clone_result = run(["git", "clone", repo_url, str(repo_root)])
    expect_success(clone_result, f"git clone into `{repo_root}`")
    return {"repo_root": str(repo_root), "managed": managed, "cloned": True, "pulled": False}


def maybe_reexec_refreshed_cli(
    checkout_repo_root: Path,
    *,
    running_cli: Path | None = None,
    execve: Callable[..., object] | None = None,
) -> dict[str, object] | None:
    checkout_cli = checkout_repo_root / "charness"
    # Post-#873 this module is not the entrypoint: a bare `Path(__file__)`
    # names the feature module, which never byte-matches the checkout CLI, so
    # an omitted `running_cli` re-exec'd every run. Prefer the entry context
    # the root shim publishes; `__file__` only serves direct unit use.
    current_cli = (running_cli or SCRIPT_PATH or Path(__file__)).resolve()
    reexec_child = os.environ.get(_CLI_REEXEC_GUARD_ENV) == str(os.getpid())
    try:
        if (
            not checkout_cli.is_file()
            or checkout_cli.resolve() == current_cli
            or checkout_cli.read_bytes() == current_cli.read_bytes()
        ):
            if reexec_child:
                return {"status": "reexecuted", "checkout_cli": str(checkout_cli)}
            return None
    except OSError:
        return None
    if reexec_child:
        emit_progress(
            "WARNING: running CLI still differs from the refreshed checkout after one re-exec; "
            "continuing without another re-exec — if this run fails, re-run the command.",
        )
        return {
            "status": "skipped",
            "reason": "already re-executed once; loop guard active",
            "checkout_cli": str(checkout_cli),
        }
    emit_progress(
        "STEP: source checkout code differs from the running CLI; re-executing the checkout's CLI so the run matches its scripts",
    )
    env = dict(os.environ)
    env[_CLI_REEXEC_GUARD_ENV] = str(os.getpid())
    try:
        (execve or os.execve)(
            sys.executable, [sys.executable, str(checkout_cli), *sys.argv[1:]], env
        )
    except OSError as exc:
        emit_progress(
            f"WARNING: re-exec of the refreshed CLI failed ({exc}); continuing with the running CLI — "
            "if this run fails, re-run the command.",
        )
        return {
            "status": "failed",
            "reason": f"re-exec failed: {exc}",
            "checkout_cli": str(checkout_cli),
        }
    return None


def emit_progress(message: str) -> None:
    """Keep progress out of the public structured stdout stream."""
    print(message, file=sys.stderr, flush=True)


def resolve_runtime_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    home_root = args.home_root.resolve()
    plugin_root = args.plugin_root.resolve() if args.plugin_root else default_plugin_root(home_root)
    codex_marketplace_path = (
        args.codex_marketplace_path.resolve()
        if args.codex_marketplace_path
        else default_codex_marketplace_path(home_root)
    )
    claude_wrapper_path = (
        args.claude_wrapper_path.resolve()
        if args.claude_wrapper_path
        else default_claude_wrapper_path(home_root)
    )
    cli_path = args.cli_path.resolve() if args.cli_path else default_cli_path(home_root)
    return plugin_root, codex_marketplace_path, claude_wrapper_path, cli_path

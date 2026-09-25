"""Install/uninstall the command-time orchestration guard hooks.

One registry intent per guard (parallel window, verdict channel, discard
worktree); the rule tables live in `host_hook_command_guards`. Each intent
installs one adapter-gated Claude PreToolUse(Bash) hook running the shared
hook script with `--guard <key>`. Other hosts expose no equivalent
command-time hook surface in this machinery, so those intent sections report
`unsupported` instead of pretending.
"""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.hooks import host_hook_install_lib as install_lib  # noqa: E402

PARALLEL_WINDOW_SCRIPT_RELATIVE = Path("scripts/host_parallel_window_hook.py")
VERDICT_CHANNEL_SCRIPT_RELATIVE = Path("scripts/host_verdict_channel_hook.py")
DISCARD_WORKTREE_SCRIPT_RELATIVE = Path("scripts/host_discard_worktree_hook.py")
# Backwards-compatible alias: the registry resolves one script constant per
# row; each row below names its own per-guard entry script instead.
GUARD_SCRIPT_RELATIVE = PARALLEL_WINDOW_SCRIPT_RELATIVE
GUARD_EVENT = "PreToolUse"
GUARD_MATCHER = "Bash"
CODEX_UNSUPPORTED_REASON = (
    "codex exposes no PreToolUse-equivalent command-time hook surface in this "
    "machinery; command-time guards stay Claude-only until such a surface exists"
)

_GUARD_SECTIONS = {
    "parallel-window": "command_guard_parallel_window",
    "verdict-channel": "command_guard_verdict_channel",
    "discard-worktree": "command_guard_discard_worktree",
}
_GUARD_SCRIPTS = {
    "parallel-window": PARALLEL_WINDOW_SCRIPT_RELATIVE,
    "verdict-channel": VERDICT_CHANNEL_SCRIPT_RELATIVE,
    "discard-worktree": DISCARD_WORKTREE_SCRIPT_RELATIVE,
}


def _state_key(host: str, guard: str) -> str:
    return f"{host}:{_GUARD_SECTIONS[guard]}"


def _command(repo_root: Path, guard: str) -> str:
    script = (repo_root / _GUARD_SCRIPTS[guard]).resolve()
    return f"python3 {shlex.quote(str(script))}"


def _install_claude_hook(repo_root: Path, guard: str, *, home: Path) -> dict[str, Any]:
    settings_path = install_lib.default_claude_settings_path(home)
    command = _command(repo_root, guard)
    result = install_lib._install_json_event(
        settings_path, command=command, matcher=GUARD_MATCHER, event=GUARD_EVENT
    )
    if result["action"] in {"installed", "noop"}:
        # State carries this guard's exact `--guard` command, which the
        # shared build_command fallback cannot reconstruct; without it the
        # status probe compares against the wrong command.
        install_lib._record_state_entry(
            repo_root,
            state_key=_state_key("claude", guard),
            settings_path=settings_path,
            kind="claude-json",
            command=command,
        )
    result.update(
        host="claude",
        kind="claude-json",
        command=command,
        intent_section=_GUARD_SECTIONS[guard],
        event=GUARD_EVENT,
    )
    return result


def _uninstall_claude_hook(repo_root: Path, guard: str, *, home: Path) -> dict[str, Any]:
    state = install_lib.read_state(repo_root)
    key = _state_key("claude", guard)
    entry = state.get(key) if isinstance(state.get(key), dict) else None
    command = (
        entry["command"]
        if isinstance(entry, dict) and isinstance(entry.get("command"), str)
        else _command(repo_root, guard)
    )
    settings_path = (
        Path(entry["settings_path"])
        if isinstance(entry, dict) and isinstance(entry.get("settings_path"), str)
        else install_lib.default_claude_settings_path(home)
    )
    result = install_lib._uninstall_json_event(
        settings_path, command=command, event=GUARD_EVENT
    )
    if result["action"] in {"removed", "absent", "not_installed"}:
        install_lib._clear_state_entry(repo_root, key)
    result.update(
        host="claude",
        kind="claude-json",
        command=command,
        intent_section=_GUARD_SECTIONS[guard],
        event=GUARD_EVENT,
    )
    return result


def adapter_from_file(adapter_file: str | Path | None) -> dict[str, Any]:
    """Read an adapter YAML declaring host-hook intents; absent means disabled."""
    if adapter_file is None:
        return {}
    try:
        import yaml
    except ImportError as exc:
        raise ValueError("--adapter-file needs PyYAML to parse the adapter") from exc
    try:
        data = yaml.safe_load(Path(adapter_file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"could not read --adapter-file {adapter_file}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"--adapter-file {adapter_file} must contain a mapping")
    return data


def status_payload(
    repo_root: Path, home: Path, adapter: dict[str, Any]
) -> tuple[dict[str, Any], int]:
    """Report every host-hook intent per host; (payload, exit code)."""
    from scripts.hooks import host_hook_registry as registry

    statuses = registry.sibling_hook_statuses(repo_root, adapter=adapter, home=home)
    in_sync = all(
        isinstance(status, dict) and status.get("in_sync")
        for status in statuses.values()
    )
    return {"intents": statuses}, 0 if in_sync else 1


# NOTE: the `hooks status` parser block stays inline in the root `charness`
# entry on purpose. A copied entry script must build its parser with zero
# sibling imports, so parser construction cannot live in a feature module;
# only the command payload (above) does, loaded lazily at command time.


def _reconcile_guard(
    repo_root: Path, guard: str, *, adapter: dict[str, Any], home: Path
) -> dict[str, Any]:
    """Install (intent enabled) or uninstall (default disabled) one guard hook."""
    section = _GUARD_SECTIONS[guard]
    actions: dict[str, Any] = {}
    claude_intent = install_lib._intent_for(adapter, "claude", section=section)
    actions["claude"] = {"intent": claude_intent}
    try:
        if claude_intent == "enabled":
            actions["claude"]["result"] = _install_claude_hook(
                repo_root, guard, home=home
            )
        else:
            actions["claude"]["result"] = _uninstall_claude_hook(
                repo_root, guard, home=home
            )
    except install_lib.HostHookError as exc:
        actions["claude"]["error"] = str(exc)
    codex_intent = install_lib._intent_for(adapter, "codex", section=section)
    actions["codex"] = {"intent": codex_intent}
    if codex_intent == "enabled":
        actions["codex"]["error"] = CODEX_UNSUPPORTED_REASON
    else:
        actions["codex"]["result"] = {"action": "noop", "reason": CODEX_UNSUPPORTED_REASON}
    return actions


def _guard_status(
    repo_root: Path, guard: str, *, adapter: dict[str, Any] | None, home: Path
) -> dict[str, Any]:
    section = _GUARD_SECTIONS[guard]
    intents = {"claude": install_lib._intent_for(adapter or {}, "claude", section=section)}
    detect_kwargs = {
        "claude": {
            "state_key": _state_key("claude", guard),
            "script_relative": _GUARD_SCRIPTS[guard],
            "event": GUARD_EVENT,
            "matcher": GUARD_MATCHER,
        }
    }
    return install_lib._hook_sync_status(
        repo_root,
        intents=intents,
        home=home,
        noun=f"PreToolUse {guard} hook",
        drift_prefix=f"{section} ",
        detect_kwargs=detect_kwargs,
    )


def reconcile_parallel_window_hooks(
    repo_root: Path, *, adapter: dict[str, Any], home: Path
) -> dict[str, Any]:
    return _reconcile_guard(repo_root, "parallel-window", adapter=adapter, home=home)


def reconcile_verdict_channel_hooks(
    repo_root: Path, *, adapter: dict[str, Any], home: Path
) -> dict[str, Any]:
    return _reconcile_guard(repo_root, "verdict-channel", adapter=adapter, home=home)


def reconcile_discard_worktree_hooks(
    repo_root: Path, *, adapter: dict[str, Any], home: Path
) -> dict[str, Any]:
    return _reconcile_guard(repo_root, "discard-worktree", adapter=adapter, home=home)


def parallel_window_status(
    repo_root: Path, *, adapter: dict[str, Any] | None, home: Path
) -> dict[str, Any]:
    return _guard_status(repo_root, "parallel-window", adapter=adapter, home=home)


def verdict_channel_status(
    repo_root: Path, *, adapter: dict[str, Any] | None, home: Path
) -> dict[str, Any]:
    return _guard_status(repo_root, "verdict-channel", adapter=adapter, home=home)


def discard_worktree_status(
    repo_root: Path, *, adapter: dict[str, Any] | None, home: Path
) -> dict[str, Any]:
    return _guard_status(repo_root, "discard-worktree", adapter=adapter, home=home)

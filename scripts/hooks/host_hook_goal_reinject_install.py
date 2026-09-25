"""Install/uninstall the Goal Run re-injection hook (#871).

One registry intent (`goal_reinject`): an adapter-gated Claude
SessionStart hook running the shared re-injection script. The hook is
installed unscoped (match-all); the script itself prints only for
compactions (`source == "compact"`) inside a checkout whose hook state
carries an active Goal Run entry, so no repo keeps a private pointer
file. Codex exposes no session-start hook surface in this machinery.
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

GOAL_REINJECT_SCRIPT_RELATIVE = Path("scripts/host_goal_reinject_hook.py")
REINJECT_EVENT = "SessionStart"
# Match-all at install; the script scopes to compactions itself, because a
# host matcher for the compact source is not a surface this machinery owns.
REINJECT_MATCHER = ""
REINJECT_SECTION = "goal_reinject"
ACTIVE_STATE_KEY = "goal-reinject:active"
DEFAULT_STATUS_COMMAND = "charness task status"
CODEX_UNSUPPORTED_REASON = (
    "codex exposes no session-start hook surface in this machinery; "
    "goal re-injection stays Claude-only until such a surface exists"
)


def _command(repo_root: Path) -> str:
    script = (repo_root / GOAL_REINJECT_SCRIPT_RELATIVE).resolve()
    return f"python3 {shlex.quote(str(script))}"


def record_active_goal_run(
    repo_root: Path,
    *,
    number: int,
    ledger_path: str,
    status_command: str = DEFAULT_STATUS_COMMAND,
) -> dict[str, Any]:
    """Point this checkout's re-injection hook at the active Goal Run."""
    if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
        raise ValueError(f"goal number must be a positive integer: {number!r}")
    if not isinstance(ledger_path, str) or not ledger_path.strip():
        raise ValueError(f"ledger_path must be a non-empty string: {ledger_path!r}")
    if not isinstance(status_command, str) or not status_command.strip():
        raise ValueError(f"status_command must be a non-empty string: {status_command!r}")
    state = install_lib.read_state(repo_root)
    state[ACTIVE_STATE_KEY] = {
        "number": number,
        "ledger_path": ledger_path.strip(),
        "status_command": status_command.strip(),
    }
    state.setdefault("schema_version", install_lib.STATE_SCHEMA_VERSION)
    install_lib.write_state(repo_root, state)
    return state[ACTIVE_STATE_KEY]


def clear_active_goal_run(repo_root: Path) -> None:
    """Drop the checkout's Goal Run pointer; the hook goes quiet."""
    install_lib._clear_state_entry(repo_root, ACTIVE_STATE_KEY)


def _state_key(host: str) -> str:
    return f"{host}:{REINJECT_SECTION}"


def _install_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path = install_lib.default_claude_settings_path(home)
    command = _command(repo_root)
    result = install_lib._install_json_event(
        settings_path, command=command, matcher=REINJECT_MATCHER, event=REINJECT_EVENT
    )
    if result["action"] in {"installed", "noop"}:
        install_lib._record_state_entry(
            repo_root,
            state_key=_state_key("claude"),
            settings_path=settings_path,
            kind="claude-json",
            command=command,
        )
    result.update(
        host="claude",
        kind="claude-json",
        command=command,
        intent_section=REINJECT_SECTION,
        event=REINJECT_EVENT,
    )
    return result


def _uninstall_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    state = install_lib.read_state(repo_root)
    key = _state_key("claude")
    entry = state.get(key) if isinstance(state.get(key), dict) else None
    command = (
        entry["command"]
        if isinstance(entry, dict) and isinstance(entry.get("command"), str)
        else _command(repo_root)
    )
    settings_path = (
        Path(entry["settings_path"])
        if isinstance(entry, dict) and isinstance(entry.get("settings_path"), str)
        else install_lib.default_claude_settings_path(home)
    )
    result = install_lib._uninstall_json_event(settings_path, command=command, event=REINJECT_EVENT)
    if result["action"] in {"removed", "absent", "not_installed"}:
        install_lib._clear_state_entry(repo_root, key)
    result.update(
        host="claude",
        kind="claude-json",
        command=command,
        intent_section=REINJECT_SECTION,
        event=REINJECT_EVENT,
    )
    return result


def reconcile_goal_reinject_hooks(
    repo_root: Path, *, adapter: dict[str, Any], home: Path
) -> dict[str, Any]:
    """Install (intent enabled) or uninstall (default disabled) the hook."""
    actions: dict[str, Any] = {}
    claude_intent = install_lib._intent_for(adapter, "claude", section=REINJECT_SECTION)
    actions["claude"] = {"intent": claude_intent}
    try:
        if claude_intent == "enabled":
            actions["claude"]["result"] = _install_claude_hook(repo_root, home=home)
        else:
            actions["claude"]["result"] = _uninstall_claude_hook(repo_root, home=home)
    except install_lib.HostHookError as exc:
        actions["claude"]["error"] = str(exc)
    codex_intent = install_lib._intent_for(adapter, "codex", section=REINJECT_SECTION)
    actions["codex"] = {"intent": codex_intent}
    if codex_intent == "enabled":
        actions["codex"]["error"] = CODEX_UNSUPPORTED_REASON
    else:
        actions["codex"]["result"] = {"action": "noop", "reason": CODEX_UNSUPPORTED_REASON}
    return actions


def goal_reinject_status(
    repo_root: Path, *, adapter: dict[str, Any] | None, home: Path
) -> dict[str, Any]:
    intents = {"claude": install_lib._intent_for(adapter or {}, "claude", section=REINJECT_SECTION)}
    detect_kwargs = {
        "claude": {
            "state_key": _state_key("claude"),
            "script_relative": GOAL_REINJECT_SCRIPT_RELATIVE,
            "event": REINJECT_EVENT,
            "matcher": REINJECT_MATCHER,
        }
    }
    return install_lib._hook_sync_status(
        repo_root,
        intents=intents,
        home=home,
        noun="SessionStart goal-reinject hook",
        drift_prefix=f"{REINJECT_SECTION} ",
        detect_kwargs=detect_kwargs,
    )

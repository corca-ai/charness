"""Install/uninstall the contextual SessionStart routing hook (#244).

The #240 routing-reliability fix ships `scripts/session_start_routing.py`
into the plugin, but the host-hook installer only ever wired the usage-episodes
hook, so the routing trigger never fired without a manual per-machine edit. This
module adds a second SessionStart hook — adapter-gated and opt-in via the
`session_routing` intent — installed *parallel* to usage-episodes through the
same primitives in `host_hook_install_lib` (carved into its own file to keep that
module under the Python-length budget, the same split as
`host_hook_codex_toml_lib`). This only wires the script; the 2026-07-04
session-start-routing revision moved the pickup/metadata/catalog routing hint
into the wired script's directive text itself, so the hook remains context-only
rather than a semantic classifier.
"""

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Any

try:
    import host_hook_install_lib as install_lib
    from host_hook_codex_toml_lib import install_codex_toml_block, uninstall_codex_toml_block
except ImportError:  # pragma: no cover - used when invoked as a module from elsewhere
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import host_hook_install_lib as install_lib  # type: ignore[no-redef]
    from host_hook_codex_toml_lib import (  # type: ignore[no-redef]
        install_codex_toml_block,
        uninstall_codex_toml_block,
    )

INTENT_SECTION = "session_routing"
SESSION_ROUTING_SCRIPT_RELATIVE = Path("scripts/session_start_routing.py")
# Claude SessionStart matcher: fire on session-open events, not on `compact`.
SESSION_ROUTING_MATCHER = "startup|resume|clear"
# Distinct TOML marker so it dedups independently of the usage-episodes block.
SESSION_ROUTING_MARKER = "charness:session-routing"
# One-way deletion inventory for host state installed before the v1 rename.
# These values are never accepted as adapter input or advertised as supported.
RETIRED_SESSION_ROUTING_SCRIPT_RELATIVE = Path("scripts/session_start_find_skills.py")
RETIRED_SESSION_ROUTING_TOML_MARKERS = (
    "charness:find-skills-routing",
    "charness:find-skills session-start routing trigger (#240)",
)
RETIRED_SESSION_ROUTING_STATE_SUFFIX = "find_skills_routing"


def _state_key(host: str) -> str:
    return f"{host}:{INTENT_SECTION}"


def _retired_state_key(host: str) -> str:
    """Return the deletion-only pre-v1 ledger key for ``host``."""
    return f"{host}:{RETIRED_SESSION_ROUTING_STATE_SUFFIX}"


def _cleanup_retired_state_entry(repo_root: Path, host: str) -> list[dict[str, Any]]:
    """Delete one retired ledger entry without treating it as live config."""
    state_key = _retired_state_key(host)
    state = install_lib.read_state(repo_root)
    if state_key not in state:
        return []
    state.pop(state_key)
    install_lib.write_state(repo_root, state)
    return [
        {
            "action": "removed",
            "kind": "retired-state-ledger-entry",
            "state_key": state_key,
        }
    ]


def _finish_result(
    repo_root: Path,
    result: dict[str, Any],
    *,
    host: str,
    kind: str,
    command: str,
    retired_state_cleanup: list[dict[str, Any]],
    clear_canonical_state: bool = False,
) -> dict[str, Any]:
    if retired_state_cleanup:
        result["retired_state_cleanup"] = retired_state_cleanup
    if clear_canonical_state and result["action"] in {"removed", "absent", "not_installed"}:
        install_lib._clear_state_entry(repo_root, _state_key(host))
    result.update(host=host, kind=kind, command=command, intent_section=INTENT_SECTION)
    return result


def _routing_intent(adapter: dict[str, Any] | None, host: str) -> str:
    """Read only the canonical session-routing intent."""
    return install_lib._intent_for(adapter or {}, host, section=INTENT_SECTION)


def _command(repo_root: Path, host: str) -> str:
    return install_lib.build_command(repo_root, host, script_relative=SESSION_ROUTING_SCRIPT_RELATIVE)


def _retired_command(repo_root: Path, host: str) -> str:
    return install_lib.build_command(repo_root, host, script_relative=RETIRED_SESSION_ROUTING_SCRIPT_RELATIVE)


def _cleanup_toml_blocks(settings_path: Path, commands: tuple[str, ...], markers: tuple[str, ...]) -> list[dict[str, Any]]:
    cleanup = []
    for command in commands:
        for marker in markers:
            result = uninstall_codex_toml_block(settings_path, command, marker)
            if result["action"] == "removed":
                cleanup.append(result)
    return cleanup


def _cleanup_retired_json_entry(settings_path: Path, repo_root: Path, host: str) -> list[dict[str, Any]]:
    result = install_lib._uninstall_json_event(settings_path, command=_retired_command(repo_root, host))
    return [result] if result["action"] == "removed" else []


def _cleanup_retired_codex_toml(settings_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    cleanup = _cleanup_toml_blocks(
        settings_path,
        (_retired_command(repo_root, "codex"),),
        (SESSION_ROUTING_MARKER, *RETIRED_SESSION_ROUTING_TOML_MARKERS),
    )
    cleanup += _cleanup_toml_blocks(
        settings_path,
        (_command(repo_root, "codex"),),
        RETIRED_SESSION_ROUTING_TOML_MARKERS,
    )
    return cleanup


def install_session_routing_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path = install_lib.default_claude_settings_path(home)
    command = _command(repo_root, "claude")
    retired_state_cleanup = _cleanup_retired_json_entry(settings_path, repo_root, "claude")
    retired_state_cleanup += _cleanup_retired_state_entry(repo_root, "claude")
    result = install_lib._install_json_event(settings_path, command=command, matcher=SESSION_ROUTING_MATCHER)
    if result["action"] == "installed":
        install_lib._record_state_entry(
            repo_root, state_key=_state_key("claude"), settings_path=settings_path,
            kind="claude-json", command=command,
        )
    return _finish_result(
        repo_root,
        result,
        host="claude",
        kind="claude-json",
        command=command,
        retired_state_cleanup=retired_state_cleanup,
    )


def install_session_routing_codex_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path, kind = install_lib.resolve_codex_target(home)
    command = _command(repo_root, "codex")
    if kind == "codex-json":
        retired_state_cleanup = _cleanup_retired_json_entry(settings_path, repo_root, "codex")
        result = install_lib._install_json_event(settings_path, command=command, matcher=SESSION_ROUTING_MATCHER)
        retired_state_cleanup += _cleanup_retired_codex_toml(install_lib.default_codex_config_toml_path(home), repo_root)
    else:
        retired_state_cleanup = _cleanup_retired_codex_toml(settings_path, repo_root)
        result = install_codex_toml_block(settings_path, command, SESSION_ROUTING_MARKER, matcher=SESSION_ROUTING_MATCHER)
    retired_state_cleanup += _cleanup_retired_state_entry(repo_root, "codex")
    if result["action"] in {"installed", "updated"}:
        install_lib._record_state_entry(
            repo_root, state_key=_state_key("codex"), settings_path=settings_path,
            kind=kind, command=command,
        )
    return _finish_result(
        repo_root,
        result,
        host="codex",
        kind=kind,
        command=command,
        retired_state_cleanup=retired_state_cleanup,
    )


def _uninstall_session_routing_hook(repo_root: Path, *, home: Path, host: str) -> dict[str, Any]:
    state = install_lib.read_state(repo_root)
    entry = state.get(_state_key(host)) if isinstance(state.get(_state_key(host)), dict) else None
    command = _command(repo_root, host)
    if host == "claude":
        settings_path = Path(entry["settings_path"]) if isinstance(entry, dict) and isinstance(entry.get("settings_path"), str) else install_lib.default_claude_settings_path(home)
        kind = "claude-json"
        result = install_lib._uninstall_json_event(settings_path, command=command)
        retired_state_cleanup = _cleanup_retired_json_entry(settings_path, repo_root, host)
    elif isinstance(entry, dict):
        settings_path = Path(entry["settings_path"])
        kind = entry.get("kind", "codex-toml")
        retired_state_cleanup = []
    else:
        settings_path, kind = install_lib.resolve_codex_target(home)
        retired_state_cleanup = []
    if host == "codex":
        if kind == "codex-json":
            result = install_lib._uninstall_json_event(settings_path, command=command)
            retired_state_cleanup = _cleanup_retired_json_entry(settings_path, repo_root, host)
            retired_state_cleanup += _cleanup_retired_codex_toml(install_lib.default_codex_config_toml_path(home), repo_root)
        else:
            result = uninstall_codex_toml_block(settings_path, command, SESSION_ROUTING_MARKER)
            retired_state_cleanup = _cleanup_retired_codex_toml(settings_path, repo_root)
    retired_state_cleanup += _cleanup_retired_state_entry(repo_root, host)
    return _finish_result(
        repo_root,
        result,
        host=host,
        kind=kind,
        command=command,
        retired_state_cleanup=retired_state_cleanup,
        clear_canonical_state=True,
    )


uninstall_session_routing_claude_hook = partial(_uninstall_session_routing_hook, host="claude")
uninstall_session_routing_codex_hook = partial(_uninstall_session_routing_hook, host="codex")


def reconcile_session_routing_hooks(repo_root: Path, *, adapter: dict[str, Any], home: Path) -> dict[str, Any]:
    """Install (intent enabled) or uninstall (default disabled) the contextual
    session routing hook per host. Opt-in: an adapter with no `session_routing`
    section leaves every host disabled, so this is a no-op until enabled."""
    actions: dict[str, Any] = {}
    for host, installer, uninstaller in (
        ("claude", install_session_routing_claude_hook, uninstall_session_routing_claude_hook),
        ("codex", install_session_routing_codex_hook, uninstall_session_routing_codex_hook),
    ):
        intent = _routing_intent(adapter, host)
        actions[host] = {"intent": intent}
        try:
            if intent == "enabled":
                actions[host]["result"] = installer(repo_root, home=home)
            else:
                actions[host]["result"] = uninstaller(repo_root, home=home)
        except install_lib.HostHookError as exc:
            actions[host]["error"] = str(exc)
    return actions


def session_routing_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    intents = {host: _routing_intent(adapter, host) for host in ("claude", "codex")}
    detect_kwargs = {
        host: {"state_key": _state_key(host), "script_relative": SESSION_ROUTING_SCRIPT_RELATIVE, "toml_marker": SESSION_ROUTING_MARKER}
        for host in ("claude", "codex")
    }
    # Status and install must agree on what this hook's identity is. Install
    # repairs (claude/codex-json) or rewrites (codex-toml) an entry whose matcher
    # cannot fire; without this, status would keep reporting that same entry
    # present. Both hosts: the codex kind is resolved at RUNTIME, so scoping this
    # to claude left codex-json — a JSON path with the same matcher semantics —
    # matcher-blind while its installer was matcher-keyed.
    for host_kwargs in detect_kwargs.values():
        host_kwargs["matcher"] = SESSION_ROUTING_MATCHER
    status = install_lib._hook_sync_status(repo_root, intents=intents, home=home, noun="SessionStart hook", drift_prefix="session_routing ", detect_kwargs=detect_kwargs)
    config_path = install_lib.default_codex_config_toml_path(home)
    text = install_lib.read_text_or_empty(config_path)
    command = _command(repo_root, "codex")
    retired_markers = [marker for marker in RETIRED_SESSION_ROUTING_TOML_MARKERS if install_lib.find_charness_toml_block(text, command, marker) is not None]
    retired_command = _retired_command(repo_root, "codex")
    retired_markers += [marker for marker in (SESSION_ROUTING_MARKER, *RETIRED_SESSION_ROUTING_TOML_MARKERS) if install_lib.find_charness_toml_block(text, retired_command, marker) is not None]
    if retired_markers:
        status["in_sync"] = False
        status["drift"].append(f"codex: session_routing retired TOML hook state still present at {config_path} ({', '.join(retired_markers)})")
        status["hosts"]["codex"]["actual"]["retired_toml_markers_present"] = retired_markers
    return status

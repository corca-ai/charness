"""Install/uninstall the contextual SessionStart routing hook (#244).

The #240 routing-reliability fix ships `scripts/session_start_routing.py`
into the plugin. This module provides an adapter-gated, opt-in SessionStart
hook via the `session_routing` intent, installed through the
same primitives in `host_hook_install_lib` (carved into its own file to keep that
module under the Python-length budget, the same split as
`host_hook_codex_toml_lib`). This only wires the script; the 2026-07-04
session-start-routing revision moved the pickup/metadata/catalog routing hint
into the wired script's directive text itself, so the hook remains context-only
rather than a semantic classifier. Codex additionally matches the explicit
`compact` SessionStart source so its compact-only recovery context can run.
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
# Claude keeps the session-open matcher; its lesson/routing context does not use
# Codex's compact-specific recovery fragment.
SESSION_ROUTING_MATCHER = "startup|resume|clear"
# Codex exposes `compact` as a distinct SessionStart source too. The installed
# Codex entrypoint must be reachable for that source so compact-only recovery
# context can run without affecting ordinary startup or resume.
CODEX_SESSION_ROUTING_MATCHER = "startup|resume|clear|compact"
# Distinct TOML marker so it dedups independently of other hook blocks.
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


def _matcher_for_host(host: str) -> str:
    return CODEX_SESSION_ROUTING_MATCHER if host == "codex" else SESSION_ROUTING_MATCHER


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


def _cleanup_current_codex_toml(settings_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    """Remove the current routing block when Codex selects JSON instead."""
    return _cleanup_toml_blocks(
        settings_path,
        (_command(repo_root, "codex"),),
        (SESSION_ROUTING_MARKER,),
    )


def _cleanup_current_codex_json(settings_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    result = install_lib._uninstall_json_event(
        settings_path,
        command=_command(repo_root, "codex"),
    )
    return [result] if result["action"] == "removed" else []


def _cleanup_current_codex_toml_and_retired(
    settings_path: Path, repo_root: Path
) -> list[dict[str, Any]]:
    return _cleanup_current_codex_toml(settings_path, repo_root) + _cleanup_retired_codex_toml(
        settings_path, repo_root
    )


def _current_codex_json_present(settings_path: Path, command: str) -> bool:
    """Read back the current Codex JSON representation for duplicate detection."""
    try:
        text = install_lib.read_text_or_empty(settings_path)
        if not text:
            return False
        data = install_lib.json.loads(text)
    except (OSError, install_lib.json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    hooks = data.get("hooks")
    entries = hooks.get("SessionStart") if isinstance(hooks, dict) else None
    if not isinstance(entries, list):
        return False
    return any(
        install_lib.entries_match_command(entry, command)
        for entry in entries
        if isinstance(entry, dict)
    )


def install_session_routing_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path = install_lib.default_claude_settings_path(home)
    command = _command(repo_root, "claude")
    retired_state_cleanup = _cleanup_retired_json_entry(settings_path, repo_root, "claude")
    retired_state_cleanup += _cleanup_retired_state_entry(repo_root, "claude")
    result = install_lib._install_json_event(
        settings_path, command=command, matcher=_matcher_for_host("claude")
    )
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
        result = install_lib._install_json_event(
            settings_path, command=command, matcher=_matcher_for_host("codex")
        )
        retired_state_cleanup += _cleanup_current_codex_toml_and_retired(
            install_lib.default_codex_config_toml_path(home), repo_root
        )
    else:
        retired_state_cleanup = _cleanup_retired_codex_toml(settings_path, repo_root)
        result = install_codex_toml_block(
            settings_path,
            command,
            SESSION_ROUTING_MARKER,
            matcher=_matcher_for_host("codex"),
        )
        retired_state_cleanup += _cleanup_current_codex_json(
            install_lib.default_codex_hooks_json_path(home), repo_root
        )
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
            retired_state_cleanup += _cleanup_current_codex_toml_and_retired(
                install_lib.default_codex_config_toml_path(home), repo_root
            )
        else:
            result = uninstall_codex_toml_block(settings_path, command, SESSION_ROUTING_MARKER)
            retired_state_cleanup = _cleanup_retired_codex_toml(settings_path, repo_root)
            retired_state_cleanup += _cleanup_current_codex_json(
                install_lib.default_codex_hooks_json_path(home), repo_root
            )
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
    for host, host_kwargs in detect_kwargs.items():
        host_kwargs["matcher"] = _matcher_for_host(host)
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
    codex_actual = status["hosts"].get("codex", {}).get("actual", {})
    current_toml = install_lib.find_charness_toml_block(
        text, command, SESSION_ROUTING_MARKER
    )
    selected_toml = (
        codex_actual.get("kind") == "codex-toml"
        and codex_actual.get("settings_path") == str(config_path)
    )
    if current_toml is not None and not selected_toml:
        status["in_sync"] = False
        status["drift"].append(
            f"codex: session_routing duplicate TOML hook remains at {config_path}"
        )
        status["hosts"]["codex"]["actual"]["duplicate_toml_present"] = True
    hooks_json_path = install_lib.default_codex_hooks_json_path(home)
    current_json = _current_codex_json_present(hooks_json_path, command)
    selected_json = (
        codex_actual.get("kind") == "codex-json"
        and codex_actual.get("settings_path") == str(hooks_json_path)
    )
    if current_json and not selected_json:
        status["in_sync"] = False
        status["drift"].append(
            f"codex: session_routing duplicate JSON hook remains at {hooks_json_path}"
        )
        status["hosts"]["codex"]["actual"]["duplicate_json_present"] = True
    return status

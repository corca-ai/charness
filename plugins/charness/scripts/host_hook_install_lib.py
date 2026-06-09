"""Install and uninstall charness usage-episodes SessionStart hooks.

State for what charness installed lives at
`.charness/usage-episodes/host-hooks-state.json`. Reconciliation reads state
first; foreign hooks are identified by absence from state, not by absence of
the marker comment. Codex `config.toml` entries carry an inline
`# charness:usage-episodes` marker for human-visible identification only.
Claude `settings.json` and Codex `hooks.json` are strict JSON, so the marker
pattern is not applied there — state-file matching is the sole identification
path for those formats.
"""

from __future__ import annotations

import json
import os
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from host_hook_codex_toml_lib import (
        CHARNESS_MARKER,
        find_charness_toml_block,
        install_codex_toml_block,
        read_text_or_empty,
        script_basename,
        uninstall_codex_toml_block,
    )
except ImportError:  # pragma: no cover - used when invoked as a module from elsewhere
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from host_hook_codex_toml_lib import (  # type: ignore[no-redef]
        CHARNESS_MARKER,
        find_charness_toml_block,
        install_codex_toml_block,
        read_text_or_empty,
        script_basename,
        uninstall_codex_toml_block,
    )

__all__ = ["CHARNESS_MARKER"]

SESSION_START_EVENT = "SessionStart"
HOST_HOOKS_STATE_RELATIVE = Path(".charness/usage-episodes/host-hooks-state.json")
HOOK_SCRIPT_RELATIVE = Path("scripts/usage_episode_session_start.py")
STATE_SCHEMA_VERSION = 1


class HostHookError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_claude_settings_path(home: Path) -> Path:
    return home / ".claude" / "settings.json"


def default_codex_config_toml_path(home: Path) -> Path:
    return home / ".codex" / "config.toml"


def default_codex_hooks_json_path(home: Path) -> Path:
    return home / ".codex" / "hooks.json"


def _codex_hooks_json_has_entries(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    hooks = data.get("hooks")
    return isinstance(hooks, dict) and bool(hooks)


def resolve_codex_target(home: Path) -> tuple[Path, str]:
    """Return (path, kind) honoring 'one representation per layer' (gather 2026-05-22).

    Defaults to TOML; falls back to JSON when `~/.codex/hooks.json` already
    carries any hook entries.
    """
    hooks_json = default_codex_hooks_json_path(home)
    if _codex_hooks_json_has_entries(hooks_json):
        return hooks_json, "codex-json"
    return default_codex_config_toml_path(home), "codex-toml"


def build_command(repo_root: Path, host: str, *, script_relative: Path = HOOK_SCRIPT_RELATIVE) -> str:
    script_path = (repo_root / script_relative).resolve()
    return f"python3 {shlex.quote(str(script_path))} --host {host}"


def read_state(repo_root: Path) -> dict[str, Any]:
    path = repo_root / HOST_HOOKS_STATE_RELATIVE
    if not path.is_file():
        return {"schema_version": STATE_SCHEMA_VERSION}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": STATE_SCHEMA_VERSION}
    if not isinstance(data, dict):
        return {"schema_version": STATE_SCHEMA_VERSION}
    data.setdefault("schema_version", STATE_SCHEMA_VERSION)
    return data


def write_state(repo_root: Path, state: dict[str, Any]) -> None:
    path = repo_root / HOST_HOOKS_STATE_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _record_state_entry(
    repo_root: Path,
    *,
    state_key: str,
    settings_path: Path,
    kind: str,
    command: str,
) -> dict[str, Any]:
    state = read_state(repo_root)
    state[state_key] = {
        "settings_path": str(settings_path),
        "kind": kind,
        "command": command,
        "installed_at": _now_iso(),
    }
    state.setdefault("schema_version", STATE_SCHEMA_VERSION)
    write_state(repo_root, state)
    return state[state_key]


def _clear_state_entry(repo_root: Path, state_key: str) -> None:
    state = read_state(repo_root)
    if state_key in state:
        state.pop(state_key)
        write_state(repo_root, state)


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _read_json_settings(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HostHookError(f"failed to read JSON settings at {path}: {exc}")
    if not isinstance(data, dict):
        raise HostHookError(f"{path}: top-level JSON must be an object")
    return data


def _ensure_event_array(settings: dict[str, Any], event: str) -> list[Any]:
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise HostHookError("settings 'hooks' must be an object")
    entries = hooks.setdefault(event, [])
    if not isinstance(entries, list):
        raise HostHookError(f"settings hooks.{event} must be an array")
    return entries


def _event_entry(command: str, matcher: str = "") -> dict[str, Any]:
    return {
        "matcher": matcher,
        "hooks": [
            {
                "type": "command",
                "command": command,
            }
        ],
    }


def _entries_match_command(entry: Any, command: str) -> bool:
    """True when `entry` already carries this charness hook.

    Matches on logical identity (the `.py` script basename) as well as the exact
    command string, so the same hook installed from a second checkout — a
    different absolute path, same basename — is recognized as already present and
    not double-installed (corca-ai/charness#245). A foreign hook (no charness
    `.py` basename) only ever exact-matches, so it is never touched.
    """
    if not isinstance(entry, dict):
        return False
    inner = entry.get("hooks")
    if not isinstance(inner, list):
        return False
    target_identity = script_basename(command)
    for item in inner:
        if not (isinstance(item, dict) and item.get("type") == "command"):
            continue
        existing = item.get("command")
        if not isinstance(existing, str):
            continue
        if existing == command:
            return True
        if target_identity is not None and script_basename(existing) == target_identity:
            return True
    return False


def _install_json_event(
    settings_path: Path,
    *,
    command: str,
    matcher: str = "",
    event: str = SESSION_START_EVENT,
) -> dict[str, Any]:
    settings = _read_json_settings(settings_path)
    entries = _ensure_event_array(settings, event)
    already = any(_entries_match_command(entry, command) for entry in entries)
    if not already:
        entries.append(_event_entry(command, matcher))
        _write_json_atomic(settings_path, settings)
    return {
        "settings_path": str(settings_path),
        "action": "noop" if already else "installed",
        "entry_count": len(entries),
    }


def _uninstall_json_event(
    settings_path: Path,
    *,
    command: str,
    event: str = SESSION_START_EVENT,
) -> dict[str, Any]:
    if not settings_path.is_file():
        return {"settings_path": str(settings_path), "action": "absent"}
    settings = _read_json_settings(settings_path)
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return {"settings_path": str(settings_path), "action": "absent"}
    entries = hooks.get(event)
    if not isinstance(entries, list):
        return {"settings_path": str(settings_path), "action": "absent"}
    remaining = [entry for entry in entries if not _entries_match_command(entry, command)]
    if len(remaining) == len(entries):
        return {"settings_path": str(settings_path), "action": "not_installed"}
    if remaining:
        hooks[event] = remaining
    else:
        hooks.pop(event, None)
        if not hooks:
            settings.pop("hooks", None)
    _write_json_atomic(settings_path, settings)
    return {"settings_path": str(settings_path), "action": "removed", "entry_count": len(remaining)}


def install_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path = default_claude_settings_path(home)
    command = build_command(repo_root, host="claude")
    result = _install_json_event(settings_path, command=command)
    if result["action"] == "installed":
        _record_state_entry(
            repo_root,
            state_key="claude",
            settings_path=settings_path,
            kind="claude-json",
            command=command,
        )
    result["host"] = "claude"
    result["kind"] = "claude-json"
    result["command"] = command
    return result


def uninstall_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    state = read_state(repo_root)
    entry = state.get("claude") if isinstance(state.get("claude"), dict) else None
    command = entry.get("command") if isinstance(entry, dict) and isinstance(entry.get("command"), str) else build_command(repo_root, host="claude")
    settings_path = Path(entry["settings_path"]) if isinstance(entry, dict) and isinstance(entry.get("settings_path"), str) else default_claude_settings_path(home)
    result = _uninstall_json_event(settings_path, command=command)
    if result["action"] in {"removed", "absent", "not_installed"}:
        _clear_state_entry(repo_root, "claude")
    result["host"] = "claude"
    result["kind"] = "claude-json"
    result["command"] = command
    return result


def install_codex_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path, kind = resolve_codex_target(home)
    command = build_command(repo_root, host="codex")
    if kind == "codex-json":
        result = _install_json_event(settings_path, command=command)
    else:
        result = install_codex_toml_block(settings_path, command)
    if result["action"] == "installed":
        _record_state_entry(
            repo_root,
            state_key="codex",
            settings_path=settings_path,
            kind=kind,
            command=command,
        )
    result["host"] = "codex"
    result["kind"] = kind
    result["command"] = command
    return result


def uninstall_codex_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    state = read_state(repo_root)
    entry = state.get("codex") if isinstance(state.get("codex"), dict) else None
    if isinstance(entry, dict):
        settings_path = Path(entry["settings_path"])
        kind = entry.get("kind", "codex-toml")
        command = entry.get("command") or build_command(repo_root, host="codex")
    else:
        settings_path, kind = resolve_codex_target(home)
        command = build_command(repo_root, host="codex")
    if kind == "codex-json":
        result = _uninstall_json_event(settings_path, command=command)
    else:
        result = uninstall_codex_toml_block(settings_path, command)
    if result["action"] in {"removed", "absent", "not_installed"}:
        _clear_state_entry(repo_root, "codex")
    result["host"] = "codex"
    result["kind"] = kind
    result["command"] = command
    return result


def _intent_for(adapter: dict[str, Any], host: str, *, section: str = "host_hooks") -> str:
    raw = adapter.get(section)
    if not isinstance(raw, dict):
        return "disabled"
    value = raw.get(host)
    if value == "enabled":
        return "enabled"
    return "disabled"


def reconcile_host_hooks(
    repo_root: Path,
    *,
    adapter: dict[str, Any],
    home: Path,
) -> dict[str, Any]:
    actions: dict[str, Any] = {}
    for host, installer, uninstaller in (
        ("claude", install_claude_hook, uninstall_claude_hook),
        ("codex", install_codex_hook, uninstall_codex_hook),
    ):
        intent = _intent_for(adapter, host)
        actions[host] = {"intent": intent}
        try:
            if intent == "enabled":
                actions[host]["result"] = installer(repo_root, home=home)
            else:
                actions[host]["result"] = uninstaller(repo_root, home=home)
        except HostHookError as exc:
            actions[host]["error"] = str(exc)
    # find-skills routing (#244): opt-in second hook, reconciled in parallel.
    # Lazy import keeps the sibling module's dependency on this one acyclic.
    try:
        from host_hook_find_skills import reconcile_find_skills_hooks
    except ImportError:  # pragma: no cover - module-from-elsewhere fallback
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from host_hook_find_skills import reconcile_find_skills_hooks  # type: ignore[no-redef]
    actions["find_skills_routing"] = reconcile_find_skills_hooks(repo_root, adapter=adapter, home=home)
    # skill #N-anchor edit-time guard: opt-in third hook, reconciled in parallel.
    try:
        from host_hook_skill_anchor_guard import reconcile_skill_anchor_guard_hooks
    except ImportError:  # pragma: no cover - module-from-elsewhere fallback
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from host_hook_skill_anchor_guard import (
            reconcile_skill_anchor_guard_hooks,  # type: ignore[no-redef]
        )
    actions["skill_anchor_edit_guard"] = reconcile_skill_anchor_guard_hooks(repo_root, adapter=adapter, home=home)
    return actions


def detect_host_hook_actual(
    repo_root: Path,
    host: str,
    *,
    home: Path,
    state_key: str | None = None,
    script_relative: Path = HOOK_SCRIPT_RELATIVE,
    toml_marker: str = CHARNESS_MARKER,
    event: str = SESSION_START_EVENT,
) -> dict[str, Any]:
    state = read_state(repo_root)
    key = state_key or host
    state_entry = state.get(key) if isinstance(state.get(key), dict) else None
    if host == "claude":
        settings_path = Path(state_entry["settings_path"]) if isinstance(state_entry, dict) and isinstance(state_entry.get("settings_path"), str) else default_claude_settings_path(home)
        kind = "claude-json"
    else:
        if isinstance(state_entry, dict) and isinstance(state_entry.get("settings_path"), str):
            settings_path = Path(state_entry["settings_path"])
            kind = state_entry.get("kind", "codex-toml")
        else:
            settings_path, kind = resolve_codex_target(home)
    expected_command = state_entry.get("command") if isinstance(state_entry, dict) else None
    if not isinstance(expected_command, str) or not expected_command:
        expected_command = build_command(repo_root, host=host, script_relative=script_relative)
    present = False
    if kind in {"claude-json", "codex-json"} and settings_path.is_file():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        if isinstance(data, dict):
            hooks = data.get("hooks")
            if isinstance(hooks, dict):
                entries = hooks.get(event)
                if isinstance(entries, list):
                    present = any(_entries_match_command(entry, expected_command) for entry in entries)
    elif kind == "codex-toml" and settings_path.is_file():
        text = read_text_or_empty(settings_path)
        present = find_charness_toml_block(text, expected_command, toml_marker) is not None
    return {
        "settings_path": str(settings_path),
        "kind": kind,
        "command": expected_command,
        "present": present,
        "tracked_in_state": isinstance(state_entry, dict),
    }


def _hook_sync_status(
    repo_root: Path,
    *,
    intents: dict[str, str],
    home: Path,
    noun: str,
    drift_prefix: str = "",
    detect_kwargs: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Shared intent-vs-actual SessionStart-hook drift status (session capture
    and find-skills routing differ only in intent section, detect kwargs, and
    the drift noun/prefix)."""
    drift: list[str] = []
    per_host: dict[str, Any] = {}
    for host, intent in intents.items():
        actual = detect_host_hook_actual(repo_root, host, home=home, **(detect_kwargs or {}).get(host, {}))
        in_sync = (intent == "enabled" and actual["present"]) or (intent == "disabled" and not actual["present"])
        if not in_sync:
            detail = f"no {noun} found" if intent == "enabled" else f"{noun} still present"
            drift.append(f"{host}: {drift_prefix}intent={intent} but {detail} at {actual['settings_path']}")
        per_host[host] = {"intent": intent, "actual": actual, "in_sync": in_sync}
    return {"in_sync": not drift, "drift": drift, "hosts": per_host}


def session_capture_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    intents = {host: _intent_for(adapter or {}, host) for host in ("claude", "codex")}
    return _hook_sync_status(repo_root, intents=intents, home=home, noun="charness SessionStart hook")


def find_skills_routing_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    from host_hook_find_skills import find_skills_routing_status as _find_skills_routing_status

    return _find_skills_routing_status(repo_root, adapter=adapter, home=home)


def skill_anchor_guard_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    from host_hook_skill_anchor_guard import skill_anchor_guard_status as _skill_anchor_guard_status

    return _skill_anchor_guard_status(repo_root, adapter=adapter, home=home)

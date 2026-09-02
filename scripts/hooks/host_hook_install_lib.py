"""Shared host-hook installation primitives.

State for what charness installed lives at
`.charness/host-hooks/state.json`. Reconciliation reads state
first; foreign hooks are identified by absence from state. The only supported
host hook is the optional Claude edit-time guard; Charness does not install
startup-context hooks.
"""

from __future__ import annotations

import json
import os
import shlex
from datetime import datetime, timezone
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

from scripts.hooks.host_hook_entry_identity import (  # noqa: E402
    entries_match_command,
    entry_carries_foreign_command,
    event_entry,
    matcher_covers,
)

HOST_HOOKS_STATE_RELATIVE = Path(".charness/host-hooks/state.json")
HOOK_SCRIPT_RELATIVE = Path("scripts/host-hook.py")
STATE_SCHEMA_VERSION = 1


class HostHookError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_claude_settings_path(home: Path) -> Path:
    return home / ".claude" / "settings.json"


def build_command(
    repo_root: Path, host: str, *, script_relative: Path = HOOK_SCRIPT_RELATIVE
) -> str:
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
    tmp.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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


def _install_json_event(
    settings_path: Path,
    *,
    command: str,
    matcher: str,
    event: str,
) -> dict[str, Any]:
    settings = _read_json_settings(settings_path)
    entries = _ensure_event_array(settings, event)
    matched = [entry for entry in entries if entries_match_command(entry, command)]
    # The matcher decides which host events reach the hook, so an entry carrying
    # our command under a matcher that cannot fire for them is installed-but-inert
    # (a PostToolUse guard under matcher "Bash" never sees an edit). Reporting a
    # clean noop over one is the same class this gate family exists to stop.
    inert = [entry for entry in matched if not matcher_covers(entry.get("matcher"), matcher)]
    repaired_matcher = False
    if not matched:
        entries.append(event_entry(command, matcher))
        _write_json_atomic(settings_path, settings)
    elif inert:
        shared = [entry for entry in inert if entry_carries_foreign_command(entry, command)]
        if shared:
            # Repairing would move a foreign command's firing conditions too, and
            # this installer's contract is that a foreign hook is never touched.
            # Refuse and name the entry rather than fix it destructively.
            raise HostHookError(
                f"{settings_path}: hooks.{event} carries this charness hook under matcher "
                f"{shared[0].get('matcher')!r}, which cannot fire for {matcher!r}, but the same "
                "entry also carries a non-charness command; repairing the matcher would change "
                "when that command fires. Split the charness command into its own entry, or set "
                f"the entry matcher to cover {matcher!r}, then re-run."
            )
        for entry in inert:
            entry["matcher"] = matcher
        _write_json_atomic(settings_path, settings)
        repaired_matcher = True
    return {
        "settings_path": str(settings_path),
        "action": "noop" if matched and not repaired_matcher else "installed",
        "repaired_matcher": repaired_matcher,
        "entry_count": len(entries),
    }


def _uninstall_json_event(
    settings_path: Path,
    *,
    command: str,
    event: str,
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
    remaining = [entry for entry in entries if not entries_match_command(entry, command)]
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
    # Only explicitly declared sibling intents are reconciled. There is no
    # default telemetry hook hidden in this common layer.
    from scripts.hooks.host_hook_registry import reconcile_sibling_hooks

    return reconcile_sibling_hooks(repo_root, adapter=adapter, home=home)


def detect_host_hook_actual(
    repo_root: Path,
    host: str,
    *,
    home: Path,
    state_key: str | None = None,
    script_relative: Path = HOOK_SCRIPT_RELATIVE,
    event: str,
    matcher: str,
) -> dict[str, Any]:
    """Report the installed-hook actual for `host`.

    The matcher is part of the hook's identity: an entry carrying the expected
    command under a matcher that cannot fire for the events this hook exists to
    catch is not reported as present. Coverage, not equality — a widened or
    reordered matcher still fires, so it stays present.
    """
    state = read_state(repo_root)
    key = state_key or host
    state_entry = state.get(key) if isinstance(state.get(key), dict) else None
    settings_path = (
        Path(state_entry["settings_path"])
        if isinstance(state_entry, dict) and isinstance(state_entry.get("settings_path"), str)
        else default_claude_settings_path(home)
    )
    kind = "claude-json"
    expected_command = state_entry.get("command") if isinstance(state_entry, dict) else None
    if not isinstance(expected_command, str) or not expected_command:
        expected_command = build_command(repo_root, host=host, script_relative=script_relative)
    present = False
    # An unparseable settings file establishes nothing about presence. `False` is
    # the GREEN answer for a `disabled` intent, so without this flag a mid-edit
    # settings.json reads as "hook correctly absent" over a file nobody could read.
    settings_readable = True
    if settings_path.is_file():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
            settings_readable = False
        if isinstance(data, dict):
            hooks = data.get("hooks")
            if isinstance(hooks, dict):
                entries = hooks.get(event)
                if isinstance(entries, list):
                    present = any(
                        entries_match_command(entry, expected_command)
                        and matcher_covers(entry.get("matcher"), matcher)
                        for entry in entries
                    )
    return {
        "settings_path": str(settings_path),
        "kind": kind,
        "command": expected_command,
        "present": present,
        "settings_readable": settings_readable,
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
    """Shared intent-vs-actual status for the optional edit-time hook."""
    drift: list[str] = []
    per_host: dict[str, Any] = {}
    for host, intent in intents.items():
        actual = detect_host_hook_actual(
            repo_root, host, home=home, **(detect_kwargs or {}).get(host, {})
        )
        in_sync = (intent == "enabled" and actual["present"]) or (
            intent == "disabled" and not actual["present"]
        )
        if not actual.get("settings_readable", True):
            # Reported for BOTH intent directions: `present: False` over an
            # unreadable file happens to agree with a `disabled` intent, and
            # calling that in-sync is a verdict over a scope never read.
            in_sync = False
            drift.append(
                f"{host}: {drift_prefix}settings file unreadable at {actual['settings_path']}; "
                f"{noun} presence not established"
            )
        elif not in_sync:
            detail = f"no {noun} found" if intent == "enabled" else f"{noun} still present"
            drift.append(
                f"{host}: {drift_prefix}intent={intent} but {detail} at {actual['settings_path']}"
            )
        per_host[host] = {"intent": intent, "actual": actual, "in_sync": in_sync}
    return {"in_sync": not drift, "drift": drift, "hosts": per_host}


def skill_anchor_guard_status(
    repo_root: Path, *, adapter: dict[str, Any] | None, home: Path
) -> dict[str, Any]:
    from scripts.hooks.host_hook_skill_anchor_guard import (
        skill_anchor_guard_status as _skill_anchor_guard_status,
    )

    return _skill_anchor_guard_status(repo_root, adapter=adapter, home=home)

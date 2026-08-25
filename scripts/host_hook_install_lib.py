"""Shared host-hook installation primitives.

State for what charness installed lives at
`.charness/host-hooks/state.json`. Reconciliation reads state
first; foreign hooks are identified by absence from state, not by absence of
the marker comment. Codex `config.toml` entries carry an inline marker for
human-visible identification only.
Claude `settings.json` and Codex `hooks.json` are strict JSON, so the marker
pattern is not applied there — state-file matching is the sole identification
path for those formats. Concrete hook intents live in sibling modules.
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
        find_charness_toml_block,
        read_text_or_empty,
        toml_block_matcher,
    )
    from host_hook_entry_identity import (
        entries_match_command,
        entry_carries_foreign_command,
        event_entry,
        matcher_covers,
    )
except ImportError:  # pragma: no cover - used when invoked as a module from elsewhere
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from host_hook_codex_toml_lib import (  # type: ignore[no-redef]
        find_charness_toml_block,
        read_text_or_empty,
        toml_block_matcher,
    )
    from host_hook_entry_identity import (  # type: ignore[no-redef]
        entries_match_command,
        entry_carries_foreign_command,
        event_entry,
        matcher_covers,
    )

SESSION_START_EVENT = "SessionStart"
HOST_HOOKS_STATE_RELATIVE = Path(".charness/host-hooks/state.json")
HOOK_SCRIPT_RELATIVE = Path("scripts/host-hook.py")
STATE_SCHEMA_VERSION = 1
CHARNESS_MARKER = "charness:hook"


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


def _install_json_event(
    settings_path: Path,
    *,
    command: str,
    matcher: str = "",
    event: str = SESSION_START_EVENT,
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
    try:
        from host_hook_registry import reconcile_sibling_hooks
    except ImportError:  # pragma: no cover - module-from-elsewhere fallback
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from host_hook_registry import reconcile_sibling_hooks  # type: ignore[no-redef]
    return reconcile_sibling_hooks(repo_root, adapter=adapter, home=home)


def detect_host_hook_actual(
    repo_root: Path,
    host: str,
    *,
    home: Path,
    state_key: str | None = None,
    script_relative: Path = HOOK_SCRIPT_RELATIVE,
    toml_marker: str = CHARNESS_MARKER,
    event: str = SESSION_START_EVENT,
    matcher: str | None = None,
) -> dict[str, Any]:
    """Report the installed-hook actual for `host`.

    `matcher`, when given, is part of the hook's identity: an entry carrying the
    expected command under a matcher that cannot fire for the events this hook
    exists to catch is not reported as present. Coverage, not equality — a widened
    or reordered matcher still fires, so it stays present (`_matcher_covers`).
    `None` keeps the command-only identity used by callers with no matcher.
    """
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
    # An unparseable settings file establishes nothing about presence. `False` is
    # the GREEN answer for a `disabled` intent, so without this flag a mid-edit
    # settings.json reads as "hook correctly absent" over a file nobody could read.
    settings_readable = True
    if kind in {"claude-json", "codex-json"} and settings_path.is_file():
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
                        and (matcher is None or matcher_covers(entry.get("matcher"), matcher))
                        for entry in entries
                    )
    elif kind == "codex-toml":
        if settings_path.is_file():
            text = read_text_or_empty(settings_path)
            span = find_charness_toml_block(text, expected_command, toml_marker)
            present = span is not None
            if present and matcher is not None:
                # The block writer emits `matcher = "..."`, so coverage IS
                # establishable here; the first cut refused the verdict because the
                # scan never read the line back, which made the honest refusal the
                # only option. Reading it back is the better fix.
                start, end = span
                present = matcher_covers(toml_block_matcher(text[start:end]), matcher)
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
    """Shared intent-vs-actual SessionStart-hook drift status (generic hooks
    and contextual session routing differ only in intent section, detect kwargs, and
    the drift noun/prefix)."""
    drift: list[str] = []
    per_host: dict[str, Any] = {}
    for host, intent in intents.items():
        actual = detect_host_hook_actual(repo_root, host, home=home, **(detect_kwargs or {}).get(host, {}))
        in_sync = (intent == "enabled" and actual["present"]) or (intent == "disabled" and not actual["present"])
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
            drift.append(f"{host}: {drift_prefix}intent={intent} but {detail} at {actual['settings_path']}")
        per_host[host] = {"intent": intent, "actual": actual, "in_sync": in_sync}
    return {"in_sync": not drift, "drift": drift, "hosts": per_host}


def session_routing_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    from host_hook_session_routing import session_routing_status as _session_routing_status

    return _session_routing_status(repo_root, adapter=adapter, home=home)


def skill_anchor_guard_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    from host_hook_skill_anchor_guard import skill_anchor_guard_status as _skill_anchor_guard_status

    return _skill_anchor_guard_status(repo_root, adapter=adapter, home=home)

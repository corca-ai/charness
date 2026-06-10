"""Sibling host-hook intent registry and state-liveness checks.

`reconcile_host_hooks` fans out to every opt-in sibling hook intent
(find-skills routing, the skill anchor edit-time guard). Each sibling used to
be a copied lazy-import block in `host_hook_install_lib`; this registry makes
a new hook intent a table row instead. Per-host error isolation stays inside
each sibling's own reconcile function (an enabled host's failure reports
per-host and never aborts the chain) — the registry only routes.

Multi-checkout posture (decision, 2026-06-10): charness installs ONE logical
hook per machine, deduped by script basename across checkouts; the commit-time
sweep is the backstop for checkouts whose edits no per-checkout hook covers.
Keying hooks per checkout was rejected: shared host events would fire every
checkout's copy of the same guard. The trade is that the surviving hook binds
one checkout's absolute path — `hook_state_liveness` flags a moved checkout or
a missing script from this checkout's own state. A DELETED checkout's leftover
settings entries are not detectable from state (its state file died with it);
`settings_file_scan` closes that gap by reading the host settings files
directly and flagging entries whose command carries a known charness
hook-script basename but whose embedded path no longer exists.
"""

from __future__ import annotations

import importlib
import json
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SiblingHookIntent:
    key: str  # payload key in reconcile/status output
    module: str
    reconcile_function: str
    status_function: str
    # Name of the module-owned `Path` constant for the hook script, resolved
    # via getattr so the script identity stays single-source in the owning
    # module (settings_file_scan derives its known-basename set from these).
    script_relative_attr: str


SIBLING_HOOK_INTENTS: tuple[SiblingHookIntent, ...] = (
    SiblingHookIntent(
        key="find_skills_routing",
        module="host_hook_find_skills",
        reconcile_function="reconcile_find_skills_hooks",
        status_function="find_skills_routing_status",
        script_relative_attr="FIND_SKILLS_SCRIPT_RELATIVE",
    ),
    SiblingHookIntent(
        key="skill_anchor_edit_guard",
        module="host_hook_skill_anchor_guard",
        reconcile_function="reconcile_skill_anchor_guard_hooks",
        status_function="skill_anchor_guard_status",
        script_relative_attr="GUARD_SCRIPT_RELATIVE",
    ),
)


def _import_module(name: str) -> Any:
    try:
        return importlib.import_module(name)
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        return importlib.import_module(name)


def reconcile_sibling_hooks(
    repo_root: Path,
    *,
    adapter: dict[str, Any],
    home: Path,
    intents: tuple[SiblingHookIntent, ...] = SIBLING_HOOK_INTENTS,
) -> dict[str, Any]:
    actions: dict[str, Any] = {}
    for intent in intents:
        module = _import_module(intent.module)
        actions[intent.key] = getattr(module, intent.reconcile_function)(repo_root, adapter=adapter, home=home)
    return actions


def sibling_hook_statuses(
    repo_root: Path,
    *,
    adapter: dict[str, Any] | None,
    home: Path,
    intents: tuple[SiblingHookIntent, ...] = SIBLING_HOOK_INTENTS,
) -> dict[str, Any]:
    statuses: dict[str, Any] = {}
    for intent in intents:
        module = _import_module(intent.module)
        statuses[intent.key] = getattr(module, intent.status_function)(repo_root, adapter=adapter, home=home)
    return statuses


def _command_script_path(command: str) -> Path | None:
    # All tracked commands come from build_command (`python3 <script.py> ...`);
    # tokens[0] is the interpreter, so a command shaped differently surfaces as
    # a loud "no script path found" rather than a silent pass.
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    for token in tokens[1:]:
        if token.endswith(".py"):
            return Path(token)
    return None


def hook_state_liveness(repo_root: Path) -> dict[str, Any]:
    """Dangling-checkout detection: every state-tracked hook's embedded script
    path must still exist. A deleted or moved checkout leaves the host settings
    invoking a missing script — for a PostToolUse hook that is loud exit-2
    noise on every matching event. Status/doctor surfacing only, not a gate."""
    install_lib = _import_module("host_hook_install_lib")
    state = install_lib.read_state(repo_root)
    entries: list[dict[str, Any]] = []
    dangling: list[str] = []
    for key, entry in sorted(state.items()):
        if not isinstance(entry, dict):
            continue
        command = entry.get("command")
        if not isinstance(command, str):
            continue
        script = _command_script_path(command)
        exists = script is not None and script.is_file()
        entries.append(
            {
                "state_key": key,
                "settings_path": entry.get("settings_path"),
                "script_path": str(script) if script is not None else None,
                "script_exists": exists,
            }
        )
        if exists:
            continue
        detail = (
            f"hook script missing at {script}"
            if script is not None
            else f"no script path found in command {command!r}"
        )
        dangling.append(
            f"{key}: state-tracked {detail}; the installing checkout may have been "
            "deleted or moved — reinstall from a live checkout or uninstall the hook"
        )
    return {"entries": entries, "dangling": dangling}


def known_hook_script_basenames(
    intents: tuple[SiblingHookIntent, ...] = SIBLING_HOOK_INTENTS,
) -> set[str]:
    """Charness hook-script basenames, derived from the owning modules'
    constants (the usage-episodes install lib plus each registry row) — never
    a forked literal list, so a new hook intent extends the scan by adding
    its registry row."""
    install_lib = _import_module("host_hook_install_lib")
    names = {install_lib.HOOK_SCRIPT_RELATIVE.name}
    for intent in intents:
        module = _import_module(intent.module)
        names.add(getattr(module, intent.script_relative_attr).name)
    return names


def _json_settings_commands(path: Path) -> list[str]:
    # Claude settings.json and Codex hooks.json share the shape
    # hooks.<event>[] -> {hooks: [{type: "command", command: ...}]}; every
    # event is scanned (SessionStart, PostToolUse, ...). Absent or unreadable
    # files degrade to silence — this is advisory surfacing, not a gate.
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
        return []
    commands: list[str] = []
    for event_entries in data["hooks"].values():
        if not isinstance(event_entries, list):
            continue
        for entry in event_entries:
            inner = entry.get("hooks") if isinstance(entry, dict) else None
            if not isinstance(inner, list):
                continue
            for item in inner:
                if isinstance(item, dict) and item.get("type") == "command" and isinstance(item.get("command"), str):
                    commands.append(item["command"])
    return commands


def _toml_settings_commands(path: Path) -> list[str]:
    toml_lib = _import_module("host_hook_codex_toml_lib")
    try:
        text = toml_lib.read_text_or_empty(path)
    except OSError:
        return []
    commands: list[str] = []
    for line in text.splitlines():
        value = toml_lib.toml_command_value(line.strip())
        if value is not None:
            commands.append(value)
    return commands


def settings_file_scan(
    home: Path,
    *,
    intents: tuple[SiblingHookIntent, ...] = SIBLING_HOOK_INTENTS,
) -> dict[str, Any]:
    """Deleted-checkout detection from the settings side: `hook_state_liveness`
    only sees this checkout's state file, so a DELETED checkout's leftover
    settings entries are invisible to it. This scan reads the host settings
    files themselves and flags any entry whose command carries a known
    charness hook-script basename but whose embedded path no longer exists —
    dangling-from-any-checkout. Foreign hooks (no known charness basename)
    are never flagged; missing/unreadable settings degrade to silence. A
    dangling entry that IS state-tracked here is also reported by
    hook_state_liveness; both point at the same leftover."""
    install_lib = _import_module("host_hook_install_lib")
    toml_lib = _import_module("host_hook_codex_toml_lib")
    known = known_hook_script_basenames(intents)
    entries: list[dict[str, Any]] = []
    dangling: list[str] = []
    sources = (
        (install_lib.default_claude_settings_path(home), "claude-json", _json_settings_commands),
        (install_lib.default_codex_hooks_json_path(home), "codex-json", _json_settings_commands),
        (install_lib.default_codex_config_toml_path(home), "codex-toml", _toml_settings_commands),
    )
    for path, kind, read_commands in sources:
        for command in read_commands(path):
            if toml_lib.script_basename(command) not in known:
                continue
            script = _command_script_path(command)
            exists = script is not None and script.is_file()
            entries.append(
                {
                    "settings_path": str(path),
                    "kind": kind,
                    "script_path": str(script) if script is not None else None,
                    "script_exists": exists,
                }
            )
            if exists:
                continue
            where = f"missing charness hook script {script}" if script is not None else f"no script path found in command {command!r}"
            dangling.append(
                f"{path}: settings entry invokes {where} — likely a deleted "
                "checkout's leftover; remove the entry or reinstall from a live checkout"
            )
    return {"entries": entries, "dangling": dangling}

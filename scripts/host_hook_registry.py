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
settings entries are not detectable from here (its state file died with it);
the remedy is uninstall/reinstall from a live checkout, and a settings-file
scan stays deferred.
"""

from __future__ import annotations

import importlib
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


SIBLING_HOOK_INTENTS: tuple[SiblingHookIntent, ...] = (
    SiblingHookIntent(
        key="find_skills_routing",
        module="host_hook_find_skills",
        reconcile_function="reconcile_find_skills_hooks",
        status_function="find_skills_routing_status",
    ),
    SiblingHookIntent(
        key="skill_anchor_edit_guard",
        module="host_hook_skill_anchor_guard",
        reconcile_function="reconcile_skill_anchor_guard_hooks",
        status_function="skill_anchor_guard_status",
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

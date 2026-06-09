"""Install/uninstall the skill #N-anchor edit-time guard hook.

The `#NNN`-anchor-in-skill-package trap recurred repeatedly and was caught only
by the commit-time validate_skill_ergonomics sweep; the per-file scan
(`skill_issue_anchor_scan.py`) existed but fired only manually. This module
wires it to fire automatically after an edit: an adapter-gated Claude
PostToolUse(Edit|Write) hook runs the repo-owned scan on the file just edited
and surfaces findings immediately, before the commit sweep round-trips. Same
primitives and opt-in shape as `host_hook_find_skills` (the parallel-hook
pattern): the host-specific firing stays adapter-declared while the scan stays
the single repo-owned rule source, and the commit-time sweep stays the
backstop. Codex exposes no equivalent edit-time hook surface in this
machinery, so the intent section is claude-only and an enabled codex intent
reports `unsupported` instead of pretending.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import host_hook_install_lib as install_lib
except ImportError:  # pragma: no cover - used when invoked as a module from elsewhere
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import host_hook_install_lib as install_lib  # type: ignore[no-redef]

INTENT_SECTION = "skill_anchor_edit_guard"
GUARD_SCRIPT_RELATIVE = Path("scripts/post_edit_skill_anchor_guard.py")
GUARD_EVENT = "PostToolUse"
# Fire on file-mutating edit tools only; the guard script itself narrows to
# skill-package paths and fail-opens on everything else.
GUARD_MATCHER = "Edit|Write|MultiEdit"
CODEX_UNSUPPORTED_REASON = (
    "codex exposes no PostToolUse-equivalent edit-time hook surface in this "
    "machinery; the commit-time validate_skill_ergonomics sweep stays the codex "
    "backstop"
)


def _state_key(host: str) -> str:
    return f"{host}:{INTENT_SECTION}"


def _command(repo_root: Path, host: str) -> str:
    return install_lib.build_command(repo_root, host, script_relative=GUARD_SCRIPT_RELATIVE)


def install_skill_anchor_guard_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path = install_lib.default_claude_settings_path(home)
    command = _command(repo_root, "claude")
    result = install_lib._install_json_event(
        settings_path, command=command, matcher=GUARD_MATCHER, event=GUARD_EVENT
    )
    if result["action"] == "installed":
        install_lib._record_state_entry(
            repo_root, state_key=_state_key("claude"), settings_path=settings_path,
            kind="claude-json", command=command,
        )
    result.update(host="claude", kind="claude-json", command=command, intent_section=INTENT_SECTION, event=GUARD_EVENT)
    return result


def uninstall_skill_anchor_guard_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    state = install_lib.read_state(repo_root)
    entry = state.get(_state_key("claude")) if isinstance(state.get(_state_key("claude")), dict) else None
    command = entry["command"] if isinstance(entry, dict) and isinstance(entry.get("command"), str) else _command(repo_root, "claude")
    settings_path = Path(entry["settings_path"]) if isinstance(entry, dict) and isinstance(entry.get("settings_path"), str) else install_lib.default_claude_settings_path(home)
    result = install_lib._uninstall_json_event(settings_path, command=command, event=GUARD_EVENT)
    if result["action"] in {"removed", "absent", "not_installed"}:
        install_lib._clear_state_entry(repo_root, _state_key("claude"))
    result.update(host="claude", kind="claude-json", command=command, intent_section=INTENT_SECTION, event=GUARD_EVENT)
    return result


def reconcile_skill_anchor_guard_hooks(repo_root: Path, *, adapter: dict[str, Any], home: Path) -> dict[str, Any]:
    """Install (intent enabled) or uninstall (default disabled) the edit-time
    anchor-guard hook. Opt-in: an adapter with no `skill_anchor_edit_guard`
    section leaves it disabled, so consumer repos inherit nothing new."""
    actions: dict[str, Any] = {}
    claude_intent = install_lib._intent_for(adapter, "claude", section=INTENT_SECTION)
    actions["claude"] = {"intent": claude_intent}
    try:
        if claude_intent == "enabled":
            actions["claude"]["result"] = install_skill_anchor_guard_claude_hook(repo_root, home=home)
        else:
            actions["claude"]["result"] = uninstall_skill_anchor_guard_claude_hook(repo_root, home=home)
    except install_lib.HostHookError as exc:
        actions["claude"]["error"] = str(exc)
    codex_intent = install_lib._intent_for(adapter, "codex", section=INTENT_SECTION)
    actions["codex"] = {"intent": codex_intent}
    if codex_intent == "enabled":
        actions["codex"]["error"] = CODEX_UNSUPPORTED_REASON
    else:
        actions["codex"]["result"] = {"action": "noop", "reason": CODEX_UNSUPPORTED_REASON}
    return actions


def skill_anchor_guard_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    intents = {"claude": install_lib._intent_for(adapter or {}, "claude", section=INTENT_SECTION)}
    detect_kwargs = {
        "claude": {
            "state_key": _state_key("claude"),
            "script_relative": GUARD_SCRIPT_RELATIVE,
            "event": GUARD_EVENT,
        }
    }
    return install_lib._hook_sync_status(
        repo_root, intents=intents, home=home, noun="PostToolUse anchor-guard hook",
        drift_prefix="skill_anchor_edit_guard ", detect_kwargs=detect_kwargs,
    )

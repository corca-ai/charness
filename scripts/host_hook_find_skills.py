"""Install/uninstall the find-skills SessionStart routing hook (#244).

The #240 routing-reliability fix ships `scripts/session_start_find_skills.py`
into the plugin, but the host-hook installer only ever wired the usage-episodes
hook, so the routing trigger never fired without a manual per-machine edit. This
module adds a second SessionStart hook — adapter-gated and opt-in via the
`find_skills_routing` intent — installed *parallel* to usage-episodes through the
same primitives in `host_hook_install_lib` (carved into its own file to keep that
module under the Python-length budget, the same split as
`host_hook_codex_toml_lib`). The dumb-hook / skill-owns-routing split is
unchanged: this only wires the script; routing intelligence stays in the skill.
"""

from __future__ import annotations

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

INTENT_SECTION = "find_skills_routing"
FIND_SKILLS_SCRIPT_RELATIVE = Path("scripts/session_start_find_skills.py")
# Claude SessionStart matcher: fire on session-open events, not on `compact`.
FIND_SKILLS_MATCHER = "startup|resume|clear"
# Distinct TOML marker so it dedups independently of the usage-episodes block.
FIND_SKILLS_MARKER = "charness:find-skills-routing"
LEGACY_FIND_SKILLS_MARKERS = ("charness:find-skills session-start routing trigger (#240)",)


def _state_key(host: str) -> str:
    return f"{host}:{INTENT_SECTION}"


def _command(repo_root: Path, host: str) -> str:
    return install_lib.build_command(repo_root, host, script_relative=FIND_SKILLS_SCRIPT_RELATIVE)


def _cleanup_codex_toml_markers(settings_path: Path, command: str, markers: tuple[str, ...]) -> list[dict[str, Any]]:
    cleanup = []
    for marker in markers:
        result = uninstall_codex_toml_block(settings_path, command, marker)
        if result["action"] == "removed":
            cleanup.append(result)
    return cleanup


def install_find_skills_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path = install_lib.default_claude_settings_path(home)
    command = _command(repo_root, "claude")
    result = install_lib._install_json_event(settings_path, command=command, matcher=FIND_SKILLS_MATCHER)
    if result["action"] == "installed":
        install_lib._record_state_entry(
            repo_root, state_key=_state_key("claude"), settings_path=settings_path,
            kind="claude-json", command=command,
        )
    result.update(host="claude", kind="claude-json", command=command, intent_section=INTENT_SECTION)
    return result


def uninstall_find_skills_claude_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    state = install_lib.read_state(repo_root)
    entry = state.get(_state_key("claude")) if isinstance(state.get(_state_key("claude")), dict) else None
    command = entry["command"] if isinstance(entry, dict) and isinstance(entry.get("command"), str) else _command(repo_root, "claude")
    settings_path = Path(entry["settings_path"]) if isinstance(entry, dict) and isinstance(entry.get("settings_path"), str) else install_lib.default_claude_settings_path(home)
    result = install_lib._uninstall_json_event(settings_path, command=command)
    if result["action"] in {"removed", "absent", "not_installed"}:
        install_lib._clear_state_entry(repo_root, _state_key("claude"))
    result.update(host="claude", kind="claude-json", command=command, intent_section=INTENT_SECTION)
    return result


def install_find_skills_codex_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    settings_path, kind = install_lib.resolve_codex_target(home)
    command = _command(repo_root, "codex")
    if kind == "codex-json":
        result = install_lib._install_json_event(settings_path, command=command, matcher=FIND_SKILLS_MATCHER)
        legacy_cleanup = _cleanup_codex_toml_markers(
            install_lib.default_codex_config_toml_path(home),
            command,
            (FIND_SKILLS_MARKER, *LEGACY_FIND_SKILLS_MARKERS),
        )
        if legacy_cleanup:
            result["legacy_cleanup"] = legacy_cleanup
    else:
        result = install_codex_toml_block(settings_path, command, FIND_SKILLS_MARKER, matcher=FIND_SKILLS_MATCHER)
        legacy_cleanup = _cleanup_codex_toml_markers(settings_path, command, LEGACY_FIND_SKILLS_MARKERS)
        if legacy_cleanup:
            result["legacy_cleanup"] = legacy_cleanup
    if result["action"] in {"installed", "updated"}:
        install_lib._record_state_entry(
            repo_root, state_key=_state_key("codex"), settings_path=settings_path,
            kind=kind, command=command,
        )
    result.update(host="codex", kind=kind, command=command, intent_section=INTENT_SECTION)
    return result


def uninstall_find_skills_codex_hook(repo_root: Path, *, home: Path) -> dict[str, Any]:
    state = install_lib.read_state(repo_root)
    entry = state.get(_state_key("codex")) if isinstance(state.get(_state_key("codex")), dict) else None
    if isinstance(entry, dict):
        settings_path = Path(entry["settings_path"])
        kind = entry.get("kind", "codex-toml")
        command = entry.get("command") or _command(repo_root, "codex")
    else:
        settings_path, kind = install_lib.resolve_codex_target(home)
        command = _command(repo_root, "codex")
    if kind == "codex-json":
        result = install_lib._uninstall_json_event(settings_path, command=command)
        legacy_cleanup = _cleanup_codex_toml_markers(
            install_lib.default_codex_config_toml_path(home),
            command,
            (FIND_SKILLS_MARKER, *LEGACY_FIND_SKILLS_MARKERS),
        )
    else:
        result = uninstall_codex_toml_block(settings_path, command, FIND_SKILLS_MARKER)
        legacy_cleanup = _cleanup_codex_toml_markers(settings_path, command, LEGACY_FIND_SKILLS_MARKERS)
    if legacy_cleanup:
        result["legacy_cleanup"] = legacy_cleanup
    if result["action"] in {"removed", "absent", "not_installed"}:
        install_lib._clear_state_entry(repo_root, _state_key("codex"))
    result.update(host="codex", kind=kind, command=command, intent_section=INTENT_SECTION)
    return result


def reconcile_find_skills_hooks(repo_root: Path, *, adapter: dict[str, Any], home: Path) -> dict[str, Any]:
    """Install (intent enabled) or uninstall (default disabled) the find-skills
    routing hook per host. Opt-in: an adapter with no `find_skills_routing`
    section leaves every host disabled, so this is a no-op until enabled."""
    actions: dict[str, Any] = {}
    for host, installer, uninstaller in (
        ("claude", install_find_skills_claude_hook, uninstall_find_skills_claude_hook),
        ("codex", install_find_skills_codex_hook, uninstall_find_skills_codex_hook),
    ):
        intent = install_lib._intent_for(adapter, host, section=INTENT_SECTION)
        actions[host] = {"intent": intent}
        try:
            if intent == "enabled":
                actions[host]["result"] = installer(repo_root, home=home)
            else:
                actions[host]["result"] = uninstaller(repo_root, home=home)
        except install_lib.HostHookError as exc:
            actions[host]["error"] = str(exc)
    return actions


def find_skills_routing_status(repo_root: Path, *, adapter: dict[str, Any] | None, home: Path) -> dict[str, Any]:
    intents = {host: install_lib._intent_for(adapter or {}, host, section=INTENT_SECTION) for host in ("claude", "codex")}
    detect_kwargs = {
        host: {"state_key": _state_key(host), "script_relative": FIND_SKILLS_SCRIPT_RELATIVE, "toml_marker": FIND_SKILLS_MARKER}
        for host in ("claude", "codex")
    }
    status = install_lib._hook_sync_status(repo_root, intents=intents, home=home, noun="SessionStart hook", drift_prefix="find_skills_routing ", detect_kwargs=detect_kwargs)
    config_path = install_lib.default_codex_config_toml_path(home)
    text = install_lib.read_text_or_empty(config_path)
    command = _command(repo_root, "codex")
    legacy_markers = [marker for marker in LEGACY_FIND_SKILLS_MARKERS if install_lib.find_charness_toml_block(text, command, marker) is not None]
    if legacy_markers:
        status["in_sync"] = False
        status["drift"].append(f"codex: find_skills_routing legacy TOML hook still present at {config_path} ({', '.join(legacy_markers)})")
        status["hosts"]["codex"]["actual"]["legacy_toml_markers_present"] = legacy_markers
    return status

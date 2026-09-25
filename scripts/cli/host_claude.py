"""Claude and Grok host surface guidance."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    PACKAGE_ID,
    CharnessError,
    expect_success,
    run,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    default_home_root,
)
from scripts.cli.common import (  # noqa: E402
    default_claude_installed_plugins_path,
    default_claude_known_marketplaces_path,
    default_grok_plugin_root,
    shell_quote,
)
from scripts.cli.install_delivery import (  # noqa: E402
    load_json,
    load_packaging,
)


def claude_subprocess_env(home_root: Path) -> dict[str, str] | None:
    """Bind Claude's HOME to the workflow home when it is explicitly custom."""
    if home_root.resolve() == default_home_root():
        return None
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    return env


def run_claude(
    command: list[str], *, cwd: Path, home_root: Path
) -> subprocess.CompletedProcess[str]:
    return run(command, cwd=cwd, env=claude_subprocess_env(home_root))


def write_claude_wrapper(wrapper_path: Path, plugin_root: Path) -> None:
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    wrapper_path.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                f'exec claude --plugin-dir {shell_quote(str(plugin_root))} "$@"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    wrapper_path.chmod(0o755)


def install_cli_binary(target_path: Path, *, source_path: Path) -> None:
    if not source_path.is_file():
        raise CharnessError(f"missing charness entrypoint `{source_path}`")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    source_resolved = source_path.resolve()
    if not target_path.exists() or source_resolved != target_path.resolve():
        shutil.copy2(source_resolved, target_path)
    target_path.chmod(0o755)


def wrapper_in_path(wrapper_path: Path) -> bool:
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    return str(wrapper_path.parent) in path_entries


def claude_marketplace_name(repo_root: Path) -> str:
    packaging = load_packaging(repo_root)
    return str(packaging["claude"]["marketplace"]["name"])


def claude_plugin_ref(repo_root: Path) -> str:
    return f"{PACKAGE_ID}@{claude_marketplace_name(repo_root)}"


def claude_marketplace_source(repo_root: Path) -> str:
    return str(repo_root)


def claude_known_marketplace(path: Path, name: str) -> dict[str, object] | None:
    if not path.is_file():
        return None
    data = load_json(path)
    entry = data.get(name)
    return entry if isinstance(entry, dict) else None


def claude_installed_plugin(path: Path, plugin_ref: str) -> dict[str, object] | None:
    if not path.is_file():
        return None
    data = load_json(path)
    plugins = data.get("plugins")
    if not isinstance(plugins, dict):
        return None
    entries = plugins.get(plugin_ref)
    if not isinstance(entries, list) or not entries:
        return None
    first = entries[0]
    return first if isinstance(first, dict) else None


def claude_enabled_status(repo_root: Path, *, home_root: Path) -> dict[str, object] | None:
    if shutil.which("claude") is None:
        return None
    result = run_claude(["claude", "plugins", "list"], cwd=repo_root, home_root=home_root)
    if result.returncode != 0:
        return {"ok": False, "raw": result.stdout + result.stderr}
    plugin_ref = claude_plugin_ref(repo_root)
    enabled = None
    present = False
    current = None
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("❯ "):
            current = line.removeprefix("❯ ").strip()
            continue
        if current == plugin_ref and line.startswith("Status:"):
            present = True
            enabled = "enabled" in line.lower()
            break
    return {
        "ok": True,
        "plugin_ref": plugin_ref,
        "present": present,
        "enabled": enabled,
        "raw": result.stdout,
    }


def ensure_claude_marketplace(repo_root: Path, *, home_root: Path) -> tuple[list[str], str]:
    if shutil.which("claude") is None:
        return [], "Claude CLI not detected; skipped marketplace bootstrap."
    name = claude_marketplace_name(repo_root)
    source = claude_marketplace_source(repo_root)
    known_path = default_claude_known_marketplaces_path(home_root)
    existing = claude_known_marketplace(known_path, name)
    actions: list[str] = []
    existing_source = existing.get("source") if isinstance(existing, dict) else None
    existing_path = existing_source.get("path") if isinstance(existing_source, dict) else None
    if existing is None:
        result = run_claude(
            ["claude", "plugins", "marketplace", "add", "--scope", "user", source],
            cwd=repo_root,
            home_root=home_root,
        )
        expect_success(result, f"claude marketplace add `{source}`")
        update_result = run_claude(
            ["claude", "plugins", "marketplace", "update", name], cwd=repo_root, home_root=home_root
        )
        expect_success(update_result, f"claude marketplace update `{name}`")
        actions.append("claude_marketplace_added")
        actions.append("claude_marketplace_updated")
        return actions, f"Claude marketplace `{name}` was added from `{source}`."
    if existing_path != source:
        remove_result = run_claude(
            ["claude", "plugins", "marketplace", "remove", name], cwd=repo_root, home_root=home_root
        )
        expect_success(remove_result, f"claude marketplace remove `{name}`")
        add_result = run_claude(
            ["claude", "plugins", "marketplace", "add", "--scope", "user", source],
            cwd=repo_root,
            home_root=home_root,
        )
        expect_success(add_result, f"claude marketplace add `{source}`")
        update_result = run_claude(
            ["claude", "plugins", "marketplace", "update", name], cwd=repo_root, home_root=home_root
        )
        expect_success(update_result, f"claude marketplace update `{name}`")
        actions.extend(
            [
                "claude_marketplace_replaced",
                "claude_marketplace_added",
                "claude_marketplace_updated",
            ]
        )
        return actions, f"Claude marketplace `{name}` was repointed to `{source}`."
    return actions, f"Claude marketplace `{name}` already configured."


def ensure_claude_plugin(
    repo_root: Path, *, home_root: Path, update: bool
) -> tuple[list[str], str]:
    if shutil.which("claude") is None:
        return [], "Claude CLI not detected; skipped plugin install."
    marketplace_name = claude_marketplace_name(repo_root)
    plugin_ref = claude_plugin_ref(repo_root)
    actions: list[str] = []
    if update:
        result = run_claude(
            ["claude", "plugins", "marketplace", "update", marketplace_name],
            cwd=repo_root,
            home_root=home_root,
        )
        expect_success(result, f"claude marketplace update `{marketplace_name}`")
        actions.append("claude_marketplace_updated")
    installed = claude_installed_plugin(
        default_claude_installed_plugins_path(home_root), plugin_ref
    )
    if installed is None:
        result = run_claude(
            ["claude", "plugins", "install", "-s", "user", plugin_ref],
            cwd=repo_root,
            home_root=home_root,
        )
        expect_success(result, f"claude plugin install `{plugin_ref}`")
        actions.append("claude_plugin_installed")
    elif update:
        result = run_claude(
            ["claude", "plugins", "update", "-s", "user", plugin_ref],
            cwd=repo_root,
            home_root=home_root,
        )
        expect_success(result, f"claude plugin update `{plugin_ref}`")
        actions.append("claude_plugin_updated")
    result = run_claude(
        ["claude", "plugins", "enable", "-s", "user", plugin_ref],
        cwd=repo_root,
        home_root=home_root,
    )
    if result.returncode == 0:
        actions.append("claude_plugin_enabled")
    return (
        actions,
        "Restart Claude Code to load the updated charness plugin."
        if update
        else "Restart Claude Code to load charness.",
    )


def ensure_grok_plugin(*, home_root: Path, plugin_root: Path) -> tuple[list[str], str]:
    """Materialize the exported plugin tree into Grok's auto-trusted user plugin dir.

    Grok does not need a marketplace for this path. Operators still list
    `charness` in `~/.grok/config.toml` `[plugins].enabled`.
    """
    dest = default_grok_plugin_root(home_root)
    if not plugin_root.is_dir():
        return [], "Grok plugin source is missing; skipped Grok plugin install."
    existed = dest.exists()
    if existed:
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(plugin_root, dest)
    action = "grok_plugin_updated" if existed else "grok_plugin_installed"
    return [action], (
        "Restart Grok Build to load `~/.grok/plugins/charness`. "
        "List `charness` in `[plugins].enabled`; do not add a marketplace."
    )


def build_grok_host_guidance(*, grok_available: bool, grok_plugin_root: Path) -> dict[str, object]:
    if not grok_available:
        return {
            "status": "unavailable",
            "manual_action_required": False,
            "message": "Grok CLI not detected on this machine.",
        }
    if grok_plugin_root.is_dir():
        return {
            "status": "installed",
            "manual_action_required": False,
            "message": (
                "Grok plugin tree is present at `~/.grok/plugins/charness`. "
                "List `charness` in `[plugins].enabled` (do not add a marketplace), then restart Grok Build."
            ),
        }
    return {
        "status": "needs-install",
        "manual_action_required": False,
        "message": (
            "Grok CLI is available but `~/.grok/plugins/charness` is missing. "
            "Run `charness update`, list `charness` in `[plugins].enabled`, and do not add a marketplace."
        ),
    }


def build_claude_host_guidance(
    *,
    repo_root: Path,
    home_root: Path,
    source_manifest_present: bool,
    marketplace_entry: dict[str, object] | None,
    installed_entry: dict[str, object] | None,
    enabled_status: dict[str, object] | None,
) -> dict[str, object]:
    if shutil.which("claude") is None:
        return {
            "status": "unavailable",
            "manual_action_required": False,
            "message": "Claude CLI not detected on this machine.",
        }
    if not source_manifest_present:
        return {
            "status": "missing-source",
            "manual_action_required": True,
            "message": "No managed charness source checkout was found for this CLI. Run `charness init` to recreate `~/.agents/src/charness` from the configured repo URL or local bootstrap source.",
        }
    plugin_ref = claude_plugin_ref(repo_root)
    if marketplace_entry is None:
        return {
            "status": "needs-marketplace",
            "manual_action_required": True,
            "message": "Run `charness init` to add the Claude marketplace and install charness.",
        }
    listed = enabled_status.get("present") if isinstance(enabled_status, dict) else False
    if installed_entry is None and not listed:
        return {
            "status": "needs-install",
            "manual_action_required": True,
            "message": f"Run `charness init` to install `{plugin_ref}` into Claude.",
        }
    enabled = enabled_status.get("enabled") if isinstance(enabled_status, dict) else None
    if enabled is False:
        return {
            "status": "needs-enable",
            "manual_action_required": True,
            "message": f"`{plugin_ref}` is installed in Claude but disabled; run `claude plugins enable {plugin_ref}` or rerun `charness init`.",
        }
    return {
        "status": "installed",
        "manual_action_required": False,
        "message": "Claude host install markers are present. Restart Claude Code to load or refresh charness.",
    }

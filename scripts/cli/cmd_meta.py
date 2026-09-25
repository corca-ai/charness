"""Version, uninstall, and reset commands."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli import host_claude  # noqa: E402
from scripts.cli.bootstrap import (  # noqa: E402
    PACKAGE_ID,
    CharnessError,
    default_codex_cache_root,
    default_state_root,
    has_source_manifest,
    resolve_repo_root,
    resolve_runtime_paths,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.common import (  # noqa: E402
    default_claude_installed_plugins_path,
    default_claude_known_marketplaces_path,
    default_claude_plugins_root,
    default_codex_config_path,
    default_grok_plugin_root,
    default_host_state_path,
)
from scripts.cli.host_claude import (  # noqa: E402
    claude_marketplace_name,
    claude_plugin_ref,
)
from scripts.cli.install_delivery import (  # noqa: E402
    load_json,
)


def remove_codex_config_entries(config_path: Path) -> list[str]:
    if not config_path.is_file():
        return []
    text = config_path.read_text(encoding="utf-8")
    pattern = re.compile(r'^\[plugins\."([^"]+)"\]\s*$([\s\S]*?)(?=^\[|\Z)', re.MULTILINE)
    removed: list[str] = []
    rebuilt: list[str] = []
    last_end = 0
    for match in pattern.finditer(text):
        plugin_id = match.group(1)
        start, end = match.span()
        rebuilt.append(text[last_end:start])
        if plugin_id.startswith(f"{PACKAGE_ID}@"):
            removed.append(plugin_id)
        else:
            rebuilt.append(text[start:end])
        last_end = end
    rebuilt.append(text[last_end:])
    if removed:
        config_path.write_text("".join(rebuilt).rstrip() + "\n", encoding="utf-8")
    return removed


def ensure_parent_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def remove_claude_installed_entry(path: Path, plugin_ref: str) -> bool:
    if not path.is_file():
        return False
    data = load_json(path)
    plugins = data.get("plugins")
    if not isinstance(plugins, dict) or plugin_ref not in plugins:
        return False
    plugins.pop(plugin_ref, None)
    ensure_parent_json(path, data)
    return True


def remove_claude_marketplace_entry(path: Path, marketplace_name: str) -> bool:
    if not path.is_file():
        return False
    data = load_json(path)
    if marketplace_name not in data:
        return False
    data.pop(marketplace_name, None)
    ensure_parent_json(path, data)
    return True


def remove_grok_plugin(*, home_root: Path) -> bool:
    dest = default_grok_plugin_root(home_root)
    if not dest.exists():
        return False
    shutil.rmtree(dest)
    return True


def remove_codex_marketplace_entry(path: Path) -> bool:
    if not path.is_file():
        return False
    data = load_json(path)
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list):
        raise CharnessError(f"`{path}` field `plugins` must be a list")
    kept = [
        plugin
        for plugin in plugins
        if not (isinstance(plugin, dict) and plugin.get("name") == PACKAGE_ID)
    ]
    removed = len(kept) != len(plugins)
    data["plugins"] = kept
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return removed


def remove_claude_plugin(repo_root: Path, *, home_root: Path) -> bool:
    if shutil.which("claude") is None:
        return False
    plugin_ref = claude_plugin_ref(repo_root)
    # Attribute access (not a from-import binding) so tests patching
    # `scripts.cli.host_claude.run_claude` also intercept the remove paths
    # no matter when `cmd_meta` was first imported (#873 split follow-up).
    result = host_claude.run_claude(
        ["claude", "plugins", "uninstall", "-s", "user", plugin_ref],
        cwd=repo_root,
        home_root=home_root,
    )
    combined = f"{result.stdout}\n{result.stderr}".lower()
    if result.returncode != 0 and "not installed" not in combined and "not found" not in combined:
        raise CharnessError(
            f"claude plugin uninstall `{plugin_ref}` failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    removed_file_entry = remove_claude_installed_entry(
        default_claude_installed_plugins_path(home_root), plugin_ref
    )
    cache_root = (
        default_claude_plugins_root(home_root)
        / "cache"
        / claude_marketplace_name(repo_root)
        / PACKAGE_ID
    )
    removed_cache = False
    if cache_root.exists():
        shutil.rmtree(cache_root)
        removed_cache = True
    return result.returncode == 0 or removed_file_entry or removed_cache


def remove_claude_marketplace(repo_root: Path, *, home_root: Path) -> bool:
    if shutil.which("claude") is None:
        return False
    name = claude_marketplace_name(repo_root)
    result = host_claude.run_claude(
        ["claude", "plugins", "marketplace", "remove", name], cwd=repo_root, home_root=home_root
    )
    combined = f"{result.stdout}\n{result.stderr}".lower()
    if result.returncode != 0 and "not found" not in combined and "no marketplace" not in combined:
        raise CharnessError(
            f"claude marketplace remove `{name}` failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    removed_file_entry = remove_claude_marketplace_entry(
        default_claude_known_marketplaces_path(home_root), name
    )
    return result.returncode == 0 or removed_file_entry


# Self-heal the running-CLI -> checkout code skew: after a checkout refresh,
# the still-running old CLI would execute install_surface against the
# refreshed checkout's scripts and crash on any payload-shape change (observed
# as the v1.3.0 -> v2.0.0 `KeyError: 'next_steps'` mid-update). Re-executing
# the checkout's own CLI finishes the run with code that matches the checkout
def _version_transition_suffix(update: dict[str, object] | None, status: str) -> str:
    version_transition = update.get("version_transition") if isinstance(update, dict) else None
    from_version = None
    to_version = None
    if isinstance(version_transition, dict):
        from_version = version_transition.get("from")
        to_version = version_transition.get("to")
    if isinstance(to_version, str) and to_version:
        if isinstance(from_version, str) and from_version and from_version != to_version:
            return f" {from_version} -> {to_version}"
        return f" {to_version}"
    if status in {"updated", "updated-not-ready"}:
        return " (version unknown)"
    return ""


def print_version_summary(payload: dict[str, object]) -> None:
    print(f"VERSION: {payload.get('current_version') or 'unknown'}")
    if payload.get("current_git_head"):
        print(f"GIT_HEAD: {payload['current_git_head']}")
    provenance = payload.get("version_provenance")
    if isinstance(provenance, dict):
        print(f"INVOCATION: {provenance.get('invocation_kind')}")
        print(f"INSTALL_METHOD: {provenance.get('install_method') or 'unknown'}")
        print(f"REPO_ROOT: {provenance.get('repo_root')}")
    latest_release = payload.get("latest_release_check")
    if isinstance(latest_release, dict):
        latest_tag = (
            latest_release.get("latest_tag") or latest_release.get("latest_version") or "unknown"
        )
        print(f"LATEST_RELEASE: {latest_release.get('status')} {latest_tag}".rstrip())
        if latest_release.get("checked_at"):
            print(f"LATEST_RELEASE_CHECKED_AT: {latest_release['checked_at']}")
        if latest_release.get("update_available") is True:
            print(f"NEXT: {payload.get('update_notice')}")


def cmd_uninstall(args: argparse.Namespace) -> int:
    home_root = args.home_root.resolve()
    repo_root, _managed_checkout = resolve_repo_root(home_root, args.repo_root)
    plugin_root, codex_marketplace_path, claude_wrapper_path, cli_path = resolve_runtime_paths(args)
    removed_marketplace = remove_codex_marketplace_entry(codex_marketplace_path)
    removed_plugin_root = False
    removed_codex_cache = False
    removed_codex_config_entries: list[str] = []
    removed_claude_plugin = False
    removed_claude_marketplace = False
    removed_grok_plugin = False
    removed_checkout = False
    removed_wrapper = False
    removed_cli = False
    removed_host_state = False
    removed_native_core = False
    if plugin_root.exists():
        shutil.rmtree(plugin_root)
        removed_plugin_root = True
    codex_cache_path = default_codex_cache_root(home_root) / PACKAGE_ID
    if codex_cache_path.exists():
        shutil.rmtree(codex_cache_path)
        removed_codex_cache = True
    removed_codex_config_entries = remove_codex_config_entries(default_codex_config_path(home_root))
    if has_source_manifest(repo_root):
        removed_claude_plugin = remove_claude_plugin(repo_root, home_root=home_root)
        removed_claude_marketplace = remove_claude_marketplace(repo_root, home_root=home_root)
    removed_grok_plugin = remove_grok_plugin(home_root=home_root)
    wrapper_path = claude_wrapper_path
    if wrapper_path.exists():
        wrapper_path.unlink()
        removed_wrapper = True
    if getattr(args, "delete_cli", False) and cli_path.exists():
        cli_path.unlink()
        removed_cli = True
    host_state_path = default_host_state_path(home_root)
    if host_state_path.exists():
        host_state_path.unlink()
        removed_host_state = True
    # Residue of the retired native-core distribution layer. Nothing writes here
    # any more -- `repograph` is built from source and installed by
    # `charness tool install repograph` -- but machines that ran the old
    # acquisition phase still hold the directory, and leaving it for a cleanup
    # nothing will ever mention again is silent residue. Self-terminating: once
    # the directory is gone this is a no-op.
    native_root = default_state_root(home_root) / "native"
    native_root_is_safe = True
    try:
        native_root.relative_to(home_root)
    except ValueError:
        native_root_is_safe = False
    if native_root_is_safe and native_root.exists():
        shutil.rmtree(native_root)
        removed_native_core = True
    if getattr(args, "delete_checkout", False):
        if repo_root.exists():
            shutil.rmtree(repo_root)
            removed_checkout = True
    payload = {
        "package_id": PACKAGE_ID,
        "removed_codex_marketplace_entry": removed_marketplace,
        "removed_plugin_root": removed_plugin_root,
        "removed_codex_cache": removed_codex_cache,
        "removed_codex_config_entries": removed_codex_config_entries,
        "removed_claude_plugin": removed_claude_plugin,
        "removed_claude_marketplace": removed_claude_marketplace,
        "removed_grok_plugin": removed_grok_plugin,
        "removed_claude_wrapper": removed_wrapper,
        "removed_cli": removed_cli,
        "removed_checkout": removed_checkout,
        "removed_host_state": removed_host_state,
        "removed_native_core": removed_native_core,
    }
    emit_yaml(payload)
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    return cmd_uninstall(args)

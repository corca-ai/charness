"""Codex host surface guidance and cache refresh."""

from __future__ import annotations

import hashlib
import json
import os
import re
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
)
from scripts.cli.host_codex_rpc import (  # noqa: E402
    refresh_codex_cache_via_app_server as refresh_codex_cache_via_app_server,
)
from scripts.cli.host_codex_rpc import (  # noqa: E402
    send_jsonrpc_message as send_jsonrpc_message,
)
from scripts.cli.host_codex_rpc import (  # noqa: E402
    wait_for_jsonrpc_response as wait_for_jsonrpc_response,
)
from scripts.cli.install_delivery import (  # noqa: E402
    load_json,
    read_host_state,
)


def codex_marketplace_entry(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    data = load_json(path)
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list):
        return None
    for plugin in plugins:
        if isinstance(plugin, dict) and plugin.get("name") == PACKAGE_ID:
            return plugin
    return None


def codex_cache_entries(cache_root: Path) -> list[dict[str, str]]:
    return _codex_cache_entries(cache_root, plugin_glob=PACKAGE_ID)


def _codex_cache_entries(cache_root: Path, *, plugin_glob: str) -> list[dict[str, str]]:
    if not cache_root.is_dir():
        return []
    entries: list[dict[str, str]] = []
    for manifest_path in sorted(cache_root.glob(f"*/{plugin_glob}/*/.codex-plugin/plugin.json")):
        version_root = manifest_path.parents[1]
        plugin_root = manifest_path.parents[2]
        marketplace_root = manifest_path.parents[3]
        manifest_version = None
        manifest_status = "invalid"
        try:
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_version_value = (
                manifest_payload.get("version") if isinstance(manifest_payload, dict) else None
            )
            if isinstance(manifest_version_value, str) and manifest_version_value:
                manifest_version = manifest_version_value
                manifest_status = "valid"
        except (OSError, json.JSONDecodeError):
            manifest_version = None
        entries.append(
            {
                "marketplace": marketplace_root.name,
                "plugin": plugin_root.name,
                "version": version_root.name,
                "version_dir": str(version_root),
                "manifest_path": str(manifest_path),
                "manifest_version": manifest_version or "",
                "manifest_status": manifest_status,
            }
        )
    return entries


def codex_source_manifest_path(plugin_root: Path) -> Path:
    return plugin_root / ".codex-plugin" / "plugin.json"


def codex_source_version(plugin_root: Path) -> str | None:
    manifest_path = codex_source_manifest_path(plugin_root)
    if not manifest_path.is_file():
        return None
    try:
        version = json.loads(manifest_path.read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError):
        return None
    return version if isinstance(version, str) else None


def codex_enabled_plugin_ids(config_entries: list[dict[str, object]]) -> list[str]:
    plugin_ids: list[str] = []
    for entry in config_entries:
        if entry.get("enabled") is True:
            plugin_id = entry.get("plugin_id")
            if isinstance(plugin_id, str):
                plugin_ids.append(plugin_id)
    return plugin_ids


def codex_cache_entry_for_plugin_id(
    cache_entries: list[dict[str, str]], plugin_id: str
) -> dict[str, str] | None:
    if "@" not in plugin_id:
        return None
    plugin_name, marketplace = plugin_id.split("@", 1)
    for entry in cache_entries:
        if entry.get("plugin") == plugin_name and entry.get("marketplace") == marketplace:
            return entry
    return None


def codex_primary_cache_entry(
    cache_entries: list[dict[str, str]],
    *,
    enabled_plugin_ids: list[str],
    source_version: str | None,
) -> tuple[dict[str, str] | None, str | None]:
    enabled_matches: list[tuple[str, dict[str, str]]] = []
    for plugin_id in enabled_plugin_ids:
        entry = codex_cache_entry_for_plugin_id(cache_entries, plugin_id)
        if entry is not None:
            enabled_matches.append((plugin_id, entry))

    if source_version:
        for plugin_id, entry in enabled_matches:
            if entry.get("manifest_version") == source_version:
                return entry, plugin_id

    if enabled_matches:
        return enabled_matches[0][1], enabled_matches[0][0]

    for entry in cache_entries:
        if entry.get("plugin") == PACKAGE_ID:
            return entry, None
    return None, None


def _last_installed_commit(home_root: Path) -> str | None:
    state = read_host_state(home_root)
    entries = [
        (key, state.get(key))
        for key in ("last_update", "last_init")
        if isinstance(state.get(key), dict)
    ]
    if not entries:
        return None
    key_order = {"last_init": 0, "last_update": 1}
    _, entry = max(
        entries,
        key=lambda item: (
            item[1].get("recorded_at", "") if isinstance(item[1], dict) else "",
            key_order.get(item[0], -1),
        ),
    )
    if not isinstance(entry, dict) or entry.get("delivery_verified") is not True:
        return None
    operation_status = entry.get("operation_status")
    if operation_status is not None and operation_status != "success":
        return None
    doctor = entry.get("doctor")
    if isinstance(doctor, dict):
        commit = doctor.get("checkout_git_head")
        if isinstance(commit, str):
            return commit
    return None


def _tree_content_digest(root: Path) -> str | None:
    """Hash a copied plugin tree so same-version cache claims have payload proof."""
    if not root.is_dir():
        return None
    digest = hashlib.sha256()
    try:
        paths = sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())
        for path in paths:
            relative = path.relative_to(root).as_posix().encode("utf-8")
            if path.is_symlink():
                digest.update(b"L\0" + relative + b"\0" + os.readlink(path).encode("utf-8") + b"\n")
            elif path.is_file():
                digest.update(b"F\0" + relative + b"\0")
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                digest.update(b"\n")
            elif not path.is_dir():
                digest.update(b"O\0" + relative + b"\n")
    except OSError:
        return None
    return digest.hexdigest()


def _same_version_cache_readback(doctor_payload: dict[str, object]) -> dict[str, object] | None:
    source_root_value = doctor_payload.get("plugin_root")
    cache_entries = doctor_payload.get("codex_cache_entries")
    enabled_plugin_ids = doctor_payload.get("codex_enabled_plugin_ids")
    source_version = doctor_payload.get("codex_source_version")
    if not isinstance(source_root_value, str) or not isinstance(cache_entries, list):
        return None
    if not isinstance(enabled_plugin_ids, list) or not isinstance(source_version, str):
        return None
    normalized_ids = [item for item in enabled_plugin_ids if isinstance(item, str)]
    cache_entry, _plugin_id = codex_primary_cache_entry(
        [item for item in cache_entries if isinstance(item, dict)],
        enabled_plugin_ids=normalized_ids,
        source_version=source_version,
    )
    if cache_entry is None or cache_entry.get("manifest_version") != source_version:
        return None
    source_digest = _tree_content_digest(Path(source_root_value))
    cache_root_value = cache_entry.get("version_dir")
    cache_digest = (
        _tree_content_digest(Path(cache_root_value)) if isinstance(cache_root_value, str) else None
    )
    if source_digest is None or cache_digest is None or source_digest != cache_digest:
        return None
    return {
        "delivery_verified": True,
        "verification": "same-version-content-readback",
        "source_content_sha256": source_digest,
        "cache_content_sha256": cache_digest,
        "cache_version_dir": cache_root_value,
    }


def _record_post_delivery_readback(
    delivery: dict[str, object],
    doctor_payload: dict[str, object],
    *,
    phase: str,
) -> dict[str, object] | None:
    readback = _same_version_cache_readback(doctor_payload)
    if readback is None:
        delivery.update(
            {
                "delivery_verified": False,
                "verification": "post-refresh-content-readback",
                "post_delivery_readback": {"status": "failed", "phase": phase},
            }
        )
        return None
    delivery.update(readback)
    delivery["post_delivery_readback"] = {
        "status": "verified",
        "phase": phase,
        "verification": readback.get("verification"),
    }
    return readback


def maybe_install_codex_host(
    *,
    home_root: Path,
    codex_marketplace_path: Path,
    doctor_payload: dict[str, object],
    skip: bool,
) -> dict[str, object]:
    if skip:
        return {
            "status": "skipped",
            "reason": "flag-disabled",
            "method": "codex-app-server-plugin-install",
        }
    hosts = doctor_payload.get("hosts")
    if not isinstance(hosts, dict) or hosts.get("codex") is not True:
        return {
            "status": "skipped",
            "reason": "codex-cli-missing",
            "method": "codex-app-server-plugin-install",
        }
    enabled_plugin_ids = doctor_payload.get("codex_enabled_plugin_ids")
    if not isinstance(enabled_plugin_ids, list):
        return {
            "status": "skipped",
            "reason": "missing-config",
            "method": "codex-app-server-plugin-install",
        }
    target_plugin_ids = [
        plugin_id
        for plugin_id in enabled_plugin_ids
        if isinstance(plugin_id, str) and plugin_id.startswith(f"{PACKAGE_ID}@")
    ]
    action = "refresh" if target_plugin_ids else "install"
    source_version = doctor_payload.get("codex_source_version")
    cache_version = doctor_payload.get("codex_cache_manifest_version")
    host_guidance = doctor_payload.get("codex_host_guidance")
    host_status = host_guidance.get("status") if isinstance(host_guidance, dict) else None
    source_commit = doctor_payload.get("checkout_git_head")
    last_installed_commit = _last_installed_commit(home_root)
    if (
        host_status == "installed"
        and isinstance(source_version, str)
        and isinstance(cache_version, str)
        and source_version == cache_version
        and isinstance(source_commit, str)
        and source_commit == last_installed_commit
    ):
        readback = _same_version_cache_readback(doctor_payload)
        if readback is not None:
            return {
                "status": "skipped",
                "reason": "already-current",
                "method": "codex-app-server-plugin-install",
                "action": action,
                "plugin_id": target_plugin_ids[0] if target_plugin_ids else None,
                **readback,
            }
    result = refresh_codex_cache_via_app_server(
        home_root=home_root,
        codex_marketplace_path=codex_marketplace_path,
        plugin_name=PACKAGE_ID,
    )
    result["action"] = action
    if target_plugin_ids:
        result["plugin_id"] = target_plugin_ids[0]
    return result


def codex_config_entries(config_path: Path) -> list[dict[str, object]]:
    if not config_path.is_file():
        return []
    text = config_path.read_text(encoding="utf-8")
    pattern = re.compile(r'^\[plugins\."([^"]+)"\]\s*$([\s\S]*?)(?=^\[|\Z)', re.MULTILINE)
    entries: list[dict[str, object]] = []
    for plugin_id, body in pattern.findall(text):
        if not plugin_id.startswith(f"{PACKAGE_ID}@"):
            continue
        enabled_match = re.search(r"^\s*enabled\s*=\s*(true|false)\s*$", body, re.MULTILINE)
        enabled = None if enabled_match is None else enabled_match.group(1) == "true"
        entries.append({"plugin_id": plugin_id, "enabled": enabled})
    return entries


def build_codex_host_guidance(
    *,
    codex_available: bool,
    codex_marketplace_path: Path,
    source_version: str | None,
    cache_entries: list[dict[str, str]],
    config_entries: list[dict[str, object]],
) -> dict[str, object]:
    if not codex_available:
        return {
            "status": "host-unavailable",
            "manual_action_required": False,
            "message": "Codex CLI not detected; charness prepared the local plugin source and personal marketplace only.",
        }
    if cache_entries:
        enabled_plugin_ids = codex_enabled_plugin_ids(config_entries)
        primary_cache, primary_plugin_id = codex_primary_cache_entry(
            cache_entries,
            enabled_plugin_ids=enabled_plugin_ids,
            source_version=source_version,
        )
        cache_manifest_version = (
            primary_cache.get("manifest_version") if isinstance(primary_cache, dict) else None
        )
        cache_manifest_status = (
            primary_cache.get("manifest_status") if isinstance(primary_cache, dict) else None
        )
        if isinstance(primary_cache, dict) and cache_manifest_status is None:
            cache_manifest_status = "valid" if cache_manifest_version else "invalid"
        if cache_manifest_status == "invalid":
            return {
                "status": "needs-refresh",
                "manual_action_required": True,
                "reason": "invalid-cache-manifest",
                "message": (
                    "Codex has a charness cache directory whose plugin manifest is missing, malformed, or versionless. "
                    "Treat the cache as unverified; run `charness update` to replace it and rerun `charness doctor --detail` before starting a new Codex session."
                ),
            }
        stale_enabled_ids: list[str] = []
        for plugin_id in enabled_plugin_ids:
            if plugin_id == primary_plugin_id:
                continue
            entry = codex_cache_entry_for_plugin_id(cache_entries, plugin_id)
            if entry is None:
                continue
            manifest_version = entry.get("manifest_version")
            if manifest_version and source_version and manifest_version != source_version:
                stale_enabled_ids.append(plugin_id)
        if (
            enabled_plugin_ids
            and source_version
            and cache_manifest_version
            and cache_manifest_version != source_version
        ):
            return {
                "status": "needs-refresh",
                "manual_action_required": True,
                "message": (
                    f"Codex still has installed charness cache version `{cache_manifest_version}` while the source plugin root is `{source_version}`. "
                    "Run `charness update` to retry the official Codex cache refresh, then restart Codex. If `charness doctor` still shows drift, reopen Plugin Directory and reinstall or disable/re-enable the local `charness` entry."
                ),
            }
        return {
            "status": "installed" if enabled_plugin_ids else "cached",
            "manual_action_required": not bool(enabled_plugin_ids),
            "message": (
                "Codex has cached charness but no enabled config entry was found; rerun `charness init` or `charness update` to retry the official install, then reopen Codex if it is still unavailable."
                if not enabled_plugin_ids
                else (
                    "Codex host install markers are present. Start a new Codex session to load charness."
                    if not stale_enabled_ids
                    else "Codex host install markers are present. Start a new Codex session to load charness. Extra stale enabled cache entries remain: "
                    + ", ".join(f"`{plugin_id}`" for plugin_id in stale_enabled_ids)
                    + "."
                )
            ),
        }
    return {
        "status": "needs-host-install",
        "manual_action_required": True,
        "message": (
            "Codex CLI is available but charness is not installed yet. "
            "Run `charness init` or `charness update` to retry the official local plugin install for "
            f"`{codex_marketplace_path}`. If Codex still does not load charness after that, restart Codex and only then fall back to Plugin Directory recovery."
        ),
    }

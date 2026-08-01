#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_fresh_checkout_module = SKILL_RUNTIME.load_local_skill_module(__file__, "check_fresh_checkout_probes")
build_fresh_checkout_payload = _fresh_checkout_module.build_payload


def _read_json(path: Path) -> dict[str, object] | None:
    """`None` when the file cannot be read or is not valid JSON. A half-written
    `plugin.json` is exactly what a failed sync leaves, and raising here killed the drift
    check that exists to notice it."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _version_at(path: Path) -> str | None:
    if not path.is_file():
        return None
    data = _read_json(path)
    if data is None:
        return None
    version = data.get("version")
    return version if isinstance(version, str) else None


def _marketplace_versions(repo_root: Path, package_id: str) -> dict[str, str | None]:
    claude_marketplace = repo_root / ".claude-plugin" / "marketplace.json"
    codex_marketplace = repo_root / ".agents" / "plugins" / "marketplace.json"
    claude_version: str | None = None
    codex_catalog_name: str | None = None
    if claude_marketplace.is_file():
        claude_data = _read_json(claude_marketplace) or {}
        metadata = claude_data.get("metadata", {})
        if isinstance(metadata, dict):
            version = metadata.get("version")
            if isinstance(version, str):
                claude_version = version
    if codex_marketplace.is_file():
        codex_data = _read_json(codex_marketplace) or {}
        plugins = codex_data.get("plugins", [])
        if isinstance(plugins, list):
            for plugin in plugins:
                if isinstance(plugin, dict) and plugin.get("name") == package_id:
                    source = plugin.get("source", {})
                    if isinstance(source, dict):
                        path = source.get("path")
                        if isinstance(path, str):
                            codex_catalog_name = path
                    break
    return {
        "claude_marketplace_version": claude_version,
        "codex_marketplace_source_path": codex_catalog_name,
    }


def _git_status(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_payload(repo_root: Path) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    manifest_path = repo_root / data["packaging_manifest_path"]
    package_id = data["package_id"]
    plugin_root = repo_root / data["checked_in_plugin_root"]
    payload: dict[str, object] = {
        "adapter": {
            "found": adapter["found"],
            "valid": adapter["valid"],
            "path": adapter["path"],
            "warnings": adapter["warnings"],
        },
        "package_id": package_id,
        "packaging_manifest_path": str(manifest_path),
        "checked_in_plugin_root": str(plugin_root),
        "surface_versions": {
            "packaging_manifest": _version_at(manifest_path),
            "claude_plugin": _version_at(plugin_root / ".claude-plugin" / "plugin.json"),
            "codex_plugin": _version_at(plugin_root / ".codex-plugin" / "plugin.json"),
        },
        "git_status": _git_status(repo_root),
        "fresh_checkout_probes": build_fresh_checkout_payload(repo_root, run_probes=False),
    }
    payload["surface_versions"].update(_marketplace_versions(repo_root, package_id))
    expected = payload["surface_versions"]["packaging_manifest"]
    versioned_surfaces = ("claude_plugin", "codex_plugin", "claude_marketplace_version")
    # The codex marketplace is a PRESENCE surface, not a versioned one — it carries a
    # source path, never a version — but the sweep row names it, so it is declarable and
    # reportable on the same axis. Leaving it out is how "deleted by a failed sync" stayed
    # invisible for it.
    presence_surfaces = ("codex_marketplace_source_path",)
    # `packaging_manifest` is deliberately NOT declarable: its absence is drift whether or
    # not anyone declares it, so accepting the declaration would be a silent no-op that
    # reads like it was honored.
    declarable = (*versioned_surfaces, *presence_surfaces)
    # A surface whose version is None is one nothing read a version out of: the file is
    # missing, unreadable, or has no `version`. The drift loop below used to skip those
    # (it needed `actual is not None`), so a codex plugin.json that a failed sync never
    # wrote was indistinguishable from one that matches (sweep row S35) — and `drift` is
    # the gate `publish_release_cli` refuses on and `plan_release_run_packets` routes on.
    # Absence is now legible for every surface INCLUDING the packaging manifest the others
    # are compared against, and becomes drift only for the surfaces the repo's own adapter
    # declares it publishes: a consumer that ships claude-only must not be turned red by a
    # list it never wrote. That declaration is self-authored and defaults to empty — see
    # the closure note on S35; this repair does not claim to have solved that.
    def _state(surface: str) -> str:
        """`absent` when nothing is there to read, `unreadable` when the file exists but
        is not parseable JSON, `no-version` when it parses but yields no usable value.
        Printing `<absent>` for the last two would be a false claim about the filesystem,
        and collapsing unreadable into no-version is the S28 distinction unmade."""
        if surface == "packaging_manifest":
            path = manifest_path
        elif surface == "claude_plugin":
            path = plugin_root / ".claude-plugin" / "plugin.json"
        elif surface == "codex_plugin":
            path = plugin_root / ".codex-plugin" / "plugin.json"
        elif surface == "claude_marketplace_version":
            path = repo_root / ".claude-plugin" / "marketplace.json"
        else:
            path = repo_root / ".agents" / "plugins" / "marketplace.json"
        if not path.is_file():
            return "absent"
        return "no-version" if _read_json(path) is not None else "unreadable"

    all_surfaces = (*versioned_surfaces, *presence_surfaces)
    # `absent_surfaces` means the file is not there — NOT merely that no version came out
    # of it. Building it from the `None` test would report a file that is right on disk as
    # absent, in the one field named for the distinction `_state` exists to make.
    absent = [
        s for s in all_surfaces
        if payload["surface_versions"].get(s) is None and _state(s) == "absent"
    ]
    if expected is None and _state("packaging_manifest") == "absent":
        absent = ["packaging_manifest", *absent]
    declared = data.get("required_release_surfaces") or []
    required = [s for s in declared if s in declarable]
    unknown_required = [s for s in declared if s not in declarable]
    payload["absent_surfaces"] = absent
    payload["required_release_surfaces"] = required
    drift: list[str] = []
    if expected is None:
        # The reference input is missing, so no surface can be compared. Reporting an
        # empty drift list here would render "everything matches" over a deleted or
        # half-written manifest — the batch's own rule, at the top of the chain.
        drift.append(
            f"packaging_manifest=<{_state('packaging_manifest')}>; no expected version to "
            "compare the generated surfaces against"
        )
    for surface in all_surfaces:
        actual = payload["surface_versions"].get(surface)
        if actual is None:
            if surface in required:
                suffix = f" != packaging_manifest={expected}" if expected is not None else ""
                drift.append(f"{surface}=<{_state(surface)}>{suffix}")
            continue
        if expected is not None and surface in versioned_surfaces and actual != expected:
            drift.append(f"{surface}={actual} != packaging_manifest={expected}")
    payload["drift"] = drift
    if unknown_required:
        payload["adapter"]["warnings"] = [
            *payload["adapter"]["warnings"],
            f"required_release_surfaces names surface(s) this check does not read: {unknown_required}. "
            f"Known surfaces: {list(declarable)}.",
        ]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root used to resolve the release adapter")
    args = parser.parse_args()
    print(json.dumps(build_payload(args.repo_root.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

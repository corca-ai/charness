#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _version_at(path: Path) -> str | None:
    if not path.is_file():
        return None
    data = _read_json(path)
    version = data.get("version")
    return version if isinstance(version, str) else None


def _marketplace_versions(repo_root: Path, package_id: str) -> dict[str, str | None]:
    claude_marketplace = repo_root / ".claude-plugin" / "marketplace.json"
    codex_marketplace = repo_root / ".agents" / "plugins" / "marketplace.json"
    claude_version: str | None = None
    codex_catalog_name: str | None = None
    if claude_marketplace.is_file():
        claude_data = _read_json(claude_marketplace)
        metadata = claude_data.get("metadata", {})
        if isinstance(metadata, dict):
            version = metadata.get("version")
            if isinstance(version, str):
                claude_version = version
    if codex_marketplace.is_file():
        codex_data = _read_json(codex_marketplace)
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
    }
    payload["surface_versions"].update(_marketplace_versions(repo_root, package_id))
    expected = payload["surface_versions"]["packaging_manifest"]
    drift: list[str] = []
    for surface in ("claude_plugin", "codex_plugin", "claude_marketplace_version"):
        actual = payload["surface_versions"].get(surface)
        if expected is not None and actual is not None and actual != expected:
            drift.append(f"{surface}={actual} != packaging_manifest={expected}")
    payload["drift"] = drift
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_payload(args.repo_root.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

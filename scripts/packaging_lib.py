#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PACKAGING_PATH = REPO_ROOT / "scripts" / "validate-packaging.py"
VALIDATE_PACKAGING_SPEC = importlib.util.spec_from_file_location(
    "validate_packaging",
    VALIDATE_PACKAGING_PATH,
)
assert VALIDATE_PACKAGING_SPEC is not None and VALIDATE_PACKAGING_SPEC.loader is not None
VALIDATE_PACKAGING = importlib.util.module_from_spec(VALIDATE_PACKAGING_SPEC)
VALIDATE_PACKAGING_SPEC.loader.exec_module(VALIDATE_PACKAGING)


class PackagingError(Exception):
    pass


def load_manifest(repo_root: Path, package_id: str) -> dict:
    manifest_path = repo_root / "packaging" / f"{package_id}.json"
    if not manifest_path.exists():
        raise PackagingError(f"missing packaging manifest `{manifest_path}`")
    try:
        VALIDATE_PACKAGING.validate_packaging_manifest(
            manifest_path,
            repo_root,
            validate_root_artifacts=False,
        )
    except Exception as exc:
        raise PackagingError(str(exc)) from exc
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def manifest_with_version_override(manifest: dict, version_override: str | None) -> dict:
    if version_override is None:
        return manifest
    overridden = json.loads(json.dumps(manifest))
    overridden["version"] = version_override
    overridden["codex"]["manifest"]["version"] = version_override
    overridden["claude"]["manifest"]["version"] = version_override
    return overridden


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src,
        dest,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache"),
    )


def replace_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    copy_tree(src, dest)


def replace_tree_if_present(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    if src.exists():
        copy_tree(src, dest)


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def rewrite_support_capability_path(capability_path: Path) -> None:
    data = json.loads(capability_path.read_text(encoding="utf-8"))
    skill_dir = capability_path.parent.name
    data["support_skill_path"] = f"support/{skill_dir}/SKILL.md"
    write_json(capability_path, data)


def checked_in_plugin_root(manifest: dict) -> Path:
    return Path(manifest["codex"]["repo_marketplace"]["default_source_path"].removeprefix("./"))


def export_plugin_tree(repo_root: Path, plugin_root: Path, manifest: dict) -> None:
    source = manifest["source"]
    copy_file(repo_root / source["readme"], plugin_root / source["readme"])

    public_skills_root = repo_root / source["public_skills_dir"]
    exported_skills_root = plugin_root / "skills"
    if exported_skills_root.exists():
        shutil.rmtree(exported_skills_root)
    exported_skills_root.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(path for path in public_skills_root.iterdir() if path.is_dir()):
        copy_tree(skill_dir, exported_skills_root / skill_dir.name)

    support_root = repo_root / source["support_skills_dir"]
    exported_support_root = plugin_root / "support"
    if exported_support_root.exists():
        shutil.rmtree(exported_support_root)
    exported_support_root.mkdir(parents=True, exist_ok=True)
    for path in sorted(support_root.iterdir()):
        if path.name == "generated":
            continue
        destination = exported_support_root / path.name
        if path.is_dir():
            copy_tree(path, destination)
            capability_path = destination / "capability.json"
            if capability_path.exists():
                rewrite_support_capability_path(capability_path)
        else:
            copy_file(path, destination)

    for field in ("profiles_dir", "presets_dir", "integrations_dir"):
        rel_path = source[field]
        replace_tree(repo_root / rel_path, plugin_root / rel_path)

    locks_root = repo_root / "integrations" / "locks"
    exported_locks_root = plugin_root / "integrations" / "locks"
    replace_tree_if_present(locks_root, exported_locks_root)

    scripts_root = repo_root / "scripts"
    exported_scripts_root = plugin_root / "scripts"
    replace_tree_if_present(scripts_root, exported_scripts_root)

    write_json(plugin_root / manifest["claude"]["manifest_path"], manifest["claude"]["manifest"])
    write_json(plugin_root / manifest["codex"]["manifest_path"], manifest["codex"]["manifest"])


def build_codex_marketplace(manifest: dict, *, source_path: str) -> dict:
    package_id = manifest["package_id"]
    repo_marketplace = manifest["codex"]["repo_marketplace"]
    return {
        "name": package_id,
        "interface": {
            "displayName": repo_marketplace["display_name"],
        },
        "plugins": [
            {
                "name": package_id,
                "source": {
                    "source": "local",
                    "path": source_path,
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": repo_marketplace["category"],
            }
        ],
    }


def build_claude_marketplace(manifest: dict, *, source_path: str) -> dict:
    claude_marketplace = manifest["claude"]["marketplace"]
    return {
        "name": claude_marketplace["name"],
        "owner": {
            "name": manifest["author"]["name"],
        },
        "metadata": {
            "description": manifest["summary"],
            "version": manifest["version"],
        },
        "plugins": [
            {
                "name": manifest["package_id"],
                "source": source_path,
                "version": manifest["version"],
                "description": manifest["summary"],
            }
        ],
    }


def expected_root_artifacts(manifest: dict) -> list[tuple[str, dict]]:
    codex_marketplace = manifest["codex"]["repo_marketplace"]
    claude_marketplace = manifest["claude"]["marketplace"]
    return [
        (
            claude_marketplace["path"],
            build_claude_marketplace(manifest, source_path=claude_marketplace["source_path"]),
        ),
        (
            codex_marketplace["path"],
            build_codex_marketplace(manifest, source_path=codex_marketplace["checked_in_source_path"]),
        ),
    ]

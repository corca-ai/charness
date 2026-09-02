#!/usr/bin/env python3

from __future__ import annotations

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

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    load_path_module,
    repo_root_from_script,
)

REPO_ROOT = repo_root_from_script(__file__)
VALIDATE_PACKAGING_PATH = REPO_ROOT / "scripts" / "plugin_export" / "validate_packaging.py"
VALIDATE_PACKAGING = load_path_module("validate_packaging", VALIDATE_PACKAGING_PATH)
_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.adapters.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
apply_generated_markdown_header = _scripts_surfaces_lib_module.apply_generated_markdown_header
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
lookup_generated_markdown = _scripts_surfaces_lib_module.lookup_generated_markdown
_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.adapters.control_plane_lib")
load_manifests_for_discovery = _scripts_control_plane_lib_module.load_manifests_for_discovery
_scripts_support_sync_lib_module = import_repo_module(__file__, "scripts.support_sync_lib")
support_link_name = _scripts_support_sync_lib_module.support_link_name


class PackagingError(Exception):
    pass


PLUGIN_README_LINK_TARGET_RE = re.compile(r"\]\((\./[^)]+)\)")
PLUGIN_README_SOURCE_ONLY_PREFIXES = (
    "./.agents/",
    "./AGENTS.md",
    "./charness-artifacts/",
    "./docs/",
    "./evals/",
    "./packaging/",
    "./plugins/",
    "./tools/",
    "./tests/",
)


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


def copy_markdown_with_generated_header(
    repo_root: Path,
    src: Path,
    dest: Path,
    *,
    derived_path: str,
) -> None:
    manifest = load_surfaces(repo_root, surfaces_path=SURFACES_PATH, required=False)
    metadata = lookup_generated_markdown(manifest, derived_path)
    body = src.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(apply_generated_markdown_header(body, metadata), encoding="utf-8")


def rewrite_plugin_readme_links(contents: str, *, repository_url: str) -> str:
    repo_url = repository_url.removesuffix(".git").rstrip("/")

    def rewrite(match: re.Match[str]) -> str:
        target = match.group(1)
        if target.startswith("./skills/public/"):
            return f"](./skills/{target.removeprefix('./skills/public/')})"
        if target.startswith("./skills/support/"):
            return f"](./support/{target.removeprefix('./skills/support/')})"
        if target.startswith("./plugins/charness/skills/"):
            return f"](./skills/{target.removeprefix('./plugins/charness/skills/')})"
        if target.startswith("./plugins/charness/support/"):
            return f"](./support/{target.removeprefix('./plugins/charness/support/')})"
        if target.startswith(PLUGIN_README_SOURCE_ONLY_PREFIXES):
            github_mode = "tree" if target.split("#", 1)[0].endswith("/") else "blob"
            return f"]({repo_url}/{github_mode}/main/{target.removeprefix('./')})"
        return match.group(0)

    return PLUGIN_README_LINK_TARGET_RE.sub(rewrite, contents)


def export_lock_surface(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    if not src.exists():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for name in (".gitkeep", "README.md", "lock.schema.json"):
        candidate = src / name
        if candidate.exists():
            copy_file(candidate, dest / name)


def rewrite_support_capability_path(capability_path: Path) -> None:
    data = json.loads(capability_path.read_text(encoding="utf-8"))
    skill_dir = capability_path.parent.name
    data["support_skill_path"] = f"support/{skill_dir}/SKILL.md"

    def rewrite(value):
        if isinstance(value, str):
            return value.replace("skills/support/", "support/")
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, dict):
            return {key: rewrite(item) for key, item in value.items()}
        return value

    data = rewrite(data)
    write_json(capability_path, data)


def rewrite_exported_consumer_validator_catalog(plugin_root: Path) -> None:
    """Make the exported catalog describe the installed package root.

    The authoring catalog is rooted at ``plugins/charness`` while the exported
    plugin is itself the package root. Leaving the source-relative value in the
    generated copy makes installed inventory fail before it can inspect the
    consumer declaration. Keep this rewrite narrow and fail closed if the
    catalog shape it owns changes underneath the exporter.
    """

    catalog_path = (
        plugin_root / "skills" / "quality" / "references" / "consumer-validator-catalog.yaml"
    )
    if not catalog_path.is_file():
        return
    contents = catalog_path.read_text(encoding="utf-8")
    source_marker = "\npackage_root: plugins/charness\n"
    exported_marker = "\npackage_root: .\n"
    if source_marker not in contents:
        if exported_marker in contents:
            return
        raise PackagingError(
            f"{catalog_path}: expected source-relative consumer-validator package_root"
        )
    catalog_path.write_text(contents.replace(source_marker, exported_marker, 1), encoding="utf-8")


def materialized_plugin_root(manifest: dict) -> Path:
    return Path(manifest["codex"]["repo_marketplace"]["default_source_path"].removeprefix("./"))


#: The two files the bootstrap installer reads. Only these — the rest of
#: `packaging/` is this repo's own release plumbing and means nothing to a
#: consumer, and shipping a directory wholesale is how an export grows surface
#: nobody can point at.
BOOTSTRAP_DEPENDENCY_CONTRACT = (
    Path("packaging") / "bootstrap-python.json",
    Path("packaging") / "bootstrap-requirements.txt",
)


def export_bootstrap_dependency_contract(repo_root: Path, plugin_root: Path) -> None:
    """Ship the dependency contract beside the installer that reads it.

    `bootstrap_runtime.py` was exported without it through every release up to
    6.0.0, so `load_contract` raised "missing bootstrap runtime contract" on the
    first consumer machine to try that path, while dozens of exported modules
    imported yaml/jsonschema/packaging bare with no declaration anywhere in the
    artifact. The consuming session concluded there was no declaration to find.
    There was; it just did not travel.
    """
    for relative in BOOTSTRAP_DEPENDENCY_CONTRACT:
        source_path = repo_root / relative
        if source_path.is_file():
            copy_file(source_path, plugin_root / relative)


def export_plugin_tree(repo_root: Path, plugin_root: Path, manifest: dict) -> None:
    source = manifest["source"]
    readme_rel = source["readme"]
    copy_markdown_with_generated_header(
        repo_root,
        repo_root / readme_rel,
        plugin_root / readme_rel,
        derived_path=(materialized_plugin_root(manifest) / readme_rel).as_posix(),
    )
    readme_path = plugin_root / readme_rel
    readme_path.write_text(
        rewrite_plugin_readme_links(
            readme_path.read_text(encoding="utf-8"),
            repository_url=manifest["repository"],
        ),
        encoding="utf-8",
    )

    public_skills_root = repo_root / source["public_skills_dir"]
    exported_skills_root = plugin_root / "skills"
    if exported_skills_root.exists():
        shutil.rmtree(exported_skills_root)
    exported_skills_root.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(path for path in public_skills_root.iterdir() if path.is_dir()):
        copy_tree(skill_dir, exported_skills_root / skill_dir.name)
    rewrite_exported_consumer_validator_catalog(plugin_root)

    shared_refs_root = repo_root / "skills" / "shared"
    replace_tree_if_present(shared_refs_root, plugin_root / "shared")

    # Claude Code discovers typed subagent definitions from a plugin-native
    # ``agents/`` directory.  Keep the authoring surface host-specific under
    # ``.claude/agents`` and materialize it only in the installed plugin;
    # consuming repos must not be told to read a source-tree path.
    claude_agents_root = repo_root / ".claude" / "agents"
    replace_tree_if_present(claude_agents_root, plugin_root / "agents")

    support_root = repo_root / source["support_skills_dir"]
    exported_support_root = plugin_root / "support"
    if exported_support_root.exists():
        shutil.rmtree(exported_support_root)
    exported_support_root.mkdir(parents=True, exist_ok=True)
    upstream_consumed_support_ids = {
        support_link_name(tool_manifest)
        for tool_manifest in load_manifests_for_discovery(repo_root)
        if isinstance(tool_manifest.get("support_skill_source"), dict)
    }
    for path in sorted(support_root.iterdir()):
        if path.name == "generated" or path.name in upstream_consumed_support_ids:
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
    export_lock_surface(locks_root, exported_locks_root)

    worktree_root = repo_root / "integrations" / "worktree"
    if worktree_root.is_dir():
        replace_tree(worktree_root, plugin_root / "integrations" / "worktree")

    scripts_root = repo_root / "scripts"
    exported_scripts_root = plugin_root / "scripts"
    replace_tree_if_present(scripts_root, exported_scripts_root)
    runtime_bootstrap_path = repo_root / "runtime_bootstrap.py"
    if runtime_bootstrap_path.is_file():
        copy_file(runtime_bootstrap_path, plugin_root / "runtime_bootstrap.py")
    # Ships for the same reason as the bootstrap shim above: ~96 exported `scripts/`
    # modules import `yaml_output` bare, which only resolves from the repo root when
    # this shim is present. Omitting it would export a tree whose scripts break the
    # moment a consumer imports one as `scripts.<name>` instead of running it.
    yaml_output_path = repo_root / "yaml_output.py"
    if yaml_output_path.is_file():
        copy_file(yaml_output_path, plugin_root / "yaml_output.py")
    skill_runtime_bootstrap_path = repo_root / "skill_runtime_bootstrap.py"
    if skill_runtime_bootstrap_path.is_file():
        copy_file(skill_runtime_bootstrap_path, plugin_root / "skill_runtime_bootstrap.py")

    export_bootstrap_dependency_contract(repo_root, plugin_root)

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
            build_codex_marketplace(
                manifest, source_path=codex_marketplace["materialized_source_path"]
            ),
        ),
    ]

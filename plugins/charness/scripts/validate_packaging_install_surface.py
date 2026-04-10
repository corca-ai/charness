#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable


def validate_exported_public_skills(
    root: Path,
    plugin_root: Path,
    source: dict[str, object],
    *,
    require_dir: Callable[[Path, str], None],
    require_file: Callable[[Path, str], None],
    validate_relative_path: Callable[[object, str], str],
) -> None:
    source_public_dir = root / validate_relative_path(source.get("public_skills_dir"), "source.public_skills_dir")
    exported_skills_dir = plugin_root / "skills"
    require_dir(exported_skills_dir, "checked_in_plugin.skills")
    if (exported_skills_dir / "public").exists() or (exported_skills_dir / "support").exists():
        raise RuntimeError("checked-in plugin skills must be flat public skill directories, not `skills/public` or `skills/support`")
    expected = sorted(path.name for path in source_public_dir.iterdir() if path.is_dir())
    actual = sorted(path.name for path in exported_skills_dir.iterdir() if path.is_dir())
    if actual != expected:
        raise RuntimeError("checked-in plugin public skills do not match source public skills")
    for skill_id in expected:
        require_file(exported_skills_dir / skill_id / "SKILL.md", f"checked_in_plugin.skills.{skill_id}")


def validate_exported_support_assets(
    root: Path,
    plugin_root: Path,
    source: dict[str, object],
    *,
    require_dir: Callable[[Path, str], None],
    validate_relative_path: Callable[[object, str], str],
) -> None:
    source_support_dir = root / validate_relative_path(source.get("support_skills_dir"), "source.support_skills_dir")
    exported_support_dir = plugin_root / "support"
    require_dir(exported_support_dir, "checked_in_plugin.support")
    if (exported_support_dir / "generated").exists():
        raise RuntimeError("checked-in plugin support assets must exclude machine-generated support artifacts")
    expected = sorted(path.name for path in source_support_dir.iterdir() if path.name != "generated")
    actual = sorted(path.name for path in exported_support_dir.iterdir())
    if actual != expected:
        raise RuntimeError("checked-in plugin support assets do not match source support assets")
    for entry in expected:
        capability_path = exported_support_dir / entry / "capability.json"
        if capability_path.exists():
            capability_data = json.loads(capability_path.read_text(encoding="utf-8"))
            if capability_data.get("support_skill_path") != f"support/{entry}/SKILL.md":
                raise RuntimeError(
                    f"checked-in plugin support capability `{entry}` has an unexpected support_skill_path"
                )


def validate_checked_in_plugin_tree(
    root: Path,
    data: dict[str, object],
    *,
    require_dir: Callable[[Path, str], None],
    require_file: Callable[[Path, str], None],
    require_json_matches: Callable[[Path, dict, str], None],
    validate_relative_path: Callable[[object, str], str],
) -> None:
    plugin_root = root / "plugins" / data["package_id"]
    require_dir(plugin_root, "checked_in_plugin.root")
    require_file(plugin_root / "README.md", "checked_in_plugin.readme")
    require_json_matches(plugin_root / data["claude"]["manifest_path"], data["claude"]["manifest"], "checked_in_plugin.claude.manifest_path")
    require_json_matches(plugin_root / data["codex"]["manifest_path"], data["codex"]["manifest"], "checked_in_plugin.codex.manifest_path")
    source = data["source"]
    if not isinstance(source, dict):
        raise RuntimeError("`source` must be an object")
    validate_exported_public_skills(
        root,
        plugin_root,
        source,
        require_dir=require_dir,
        require_file=require_file,
        validate_relative_path=validate_relative_path,
    )
    validate_exported_support_assets(
        root,
        plugin_root,
        source,
        require_dir=require_dir,
        validate_relative_path=validate_relative_path,
    )
    for field in ("profiles_dir", "presets_dir", "integrations_dir"):
        rel_path = validate_relative_path(source.get(field), f"source.{field}")
        require_dir(plugin_root / rel_path, f"checked_in_plugin.{field}")
    if (root / "integrations" / "locks").is_dir():
        require_dir(plugin_root / "integrations" / "locks", "checked_in_plugin.integrations_locks")
    if (root / "scripts").is_dir():
        require_dir(plugin_root / "scripts", "checked_in_plugin.scripts")
        require_file(plugin_root / "scripts" / "adapter_lib.py", "checked_in_plugin.scripts.adapter_lib")
        require_file(plugin_root / "scripts" / "adapter_init_lib.py", "checked_in_plugin.scripts.adapter_init_lib")
        require_file(plugin_root / "scripts" / "control_plane_lib.py", "checked_in_plugin.scripts.control_plane_lib")

#!/usr/bin/env python3

from __future__ import annotations

import os
from pathlib import Path


def public_skills_dir(repo_root: Path) -> Path:
    source_layout = repo_root / "skills" / "public"
    if source_layout.is_dir():
        return source_layout
    return repo_root / "skills"


def support_dir(repo_root: Path) -> Path:
    source_layout = repo_root / "skills" / "support"
    if source_layout.is_dir():
        return source_layout
    return repo_root / "support"


def support_capability_schema_path(repo_root: Path) -> Path:
    return support_dir(repo_root) / "capability.schema.json"


def support_capability_paths(repo_root: Path) -> list[Path]:
    support_root = support_dir(repo_root)
    return sorted(support_root.glob("*/capability.json"))


def integrations_tools_dir(repo_root: Path) -> Path:
    return repo_root / "integrations" / "tools"


def integrations_locks_dir(repo_root: Path) -> Path:
    return repo_root / "integrations" / "locks"


def generated_support_dir(repo_root: Path) -> Path:
    support_root = support_dir(repo_root)
    return support_root / "generated"


def resolve_cache_home() -> Path:
    override = os.environ.get("CHARNESS_CACHE_HOME")
    if override:
        return Path(override).expanduser().resolve()
    xdg_root = os.environ.get("XDG_CACHE_HOME")
    if xdg_root:
        return Path(xdg_root).expanduser().resolve()
    return Path.home().resolve() / ".cache"


def support_skill_cache_dir() -> Path:
    return resolve_cache_home() / "charness" / "support-skills"

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
    override = os.environ.get("CHARNESS_SUPPORT_DIR")
    if override:
        return Path(override).expanduser().resolve()
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


def discovery_stub_dir(repo_root: Path) -> Path:
    return repo_root / ".agents" / "charness-discovery"


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


# ---- where a repo script lives --------------------------------------------
#
# Since the concept packaging (#770) a repo script is either flat, `scripts/<name>`,
# or inside the one package that owns it, `scripts/<pkg>/<name>`. Every caller that
# needed the answer had written its own search (a `glob`, an `rglob`, an ancestor
# walk), and the rename sweep that followed had nothing to ask, so it swept with a
# regex. This is the one answer; `check_script_lookup_form.py` refuses another.

SCRIPTS_DIR_NAME = "scripts"
_SCRIPT_SEARCH_SKIP_PARTS = frozenset({"__pycache__"})


class RepoScriptMiss(FileNotFoundError):
    """`scripts/<name>` exists neither flat nor inside any concept package."""


class RepoScriptAmbiguity(RepoScriptMiss):
    """More than one concept package owns a script of that name.

    The flat spelling cannot choose between them, and choosing the first sorted
    match would be a silent fallback: the caller gets a script, just not
    necessarily the one it named.
    """


def repo_script(repo_root: Path, name: str) -> Path:
    """The path of repo script `name`: flat under `scripts/`, else packaged.

    `name` is a filename (`yaml_output.py`) or a scripts-relative path
    (`gates/check_docs_graph.py`). A relative path is never searched for: it is
    where it says or it misses, so a caller that already knows the package
    cannot be handed a same-named file from another one.
    """
    scripts_root = Path(repo_root) / SCRIPTS_DIR_NAME
    flat = scripts_root / name
    if flat.is_file():
        return flat
    if "/" in name or not scripts_root.is_dir():
        raise RepoScriptMiss(f"{SCRIPTS_DIR_NAME}/{name} is not in {repo_root}")
    packaged = sorted(
        path
        for path in scripts_root.rglob(name)
        if path.is_file() and not (_SCRIPT_SEARCH_SKIP_PARTS & set(path.parts))
    )
    if len(packaged) == 1:
        return packaged[0]
    if packaged:
        owners = ", ".join(path.relative_to(repo_root).as_posix() for path in packaged)
        raise RepoScriptAmbiguity(f"{name} is owned by more than one package: {owners}")
    raise RepoScriptMiss(f"{SCRIPTS_DIR_NAME}/{name} is neither flat nor packaged in {repo_root}")


def find_repo_script(repo_root: Path, name: str) -> Path | None:
    """`repo_script`, with a miss returned as None. An ambiguity still raises."""
    try:
        return repo_script(repo_root, name)
    except RepoScriptAmbiguity:
        raise
    except RepoScriptMiss:
        return None

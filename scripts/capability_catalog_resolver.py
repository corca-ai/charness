"""Resolve stale host-reported skill paths across plugin cache rotations."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _version_key(path: Path) -> tuple[int, ...]:
    values = [int(item) for item in re.findall(r"\d+", path.name)]
    return tuple(values) if values else (0,)


def _cache_candidates(codex_home: Path, skill_id: str, marketplace: str, plugin: str) -> list[tuple[str, Path]]:
    root = codex_home / "plugins" / "cache" / marketplace / plugin
    if not root.is_dir():
        return []
    source = "codex-versioned-cache" if (marketplace, plugin) == ("local", "charness") else "codex-plugin-cache"
    versions = sorted((item for item in root.iterdir() if item.is_dir()), key=lambda item: (_version_key(item), item.stat().st_mtime), reverse=True)
    return [(source, version / "skills" / skill_id / "SKILL.md") for version in versions]


def resolve_skill_path(*, skill_id: str, repo_root: Path, home: Path, codex_home: Path, reported_path: Path | None, marketplace: str = "local", plugin: str = "charness") -> dict[str, Any]:
    is_charness = (marketplace, plugin) == ("local", "charness")
    candidates: list[tuple[str, Path]] = []
    if reported_path is not None:
        candidates.append(("reported", reported_path))
    if is_charness:
        candidates.extend([("codex-stable-plugin", codex_home / "plugins/charness/skills" / skill_id / "SKILL.md"), ("repo-plugin-export", repo_root / "plugins/charness/skills" / skill_id / "SKILL.md"), ("repo-public-skill", repo_root / "skills/public" / skill_id / "SKILL.md"), ("repo-support-skill", repo_root / "skills/support" / skill_id / "SKILL.md"), ("repo-synced-support-skill", repo_root / "skills/support/generated" / skill_id / "SKILL.md")])
    candidates.extend(_cache_candidates(codex_home, skill_id, marketplace, plugin))
    if is_charness:
        candidates.extend([("managed-checkout-plugin", home / ".agents/src/charness/plugins/charness/skills" / skill_id / "SKILL.md"), ("managed-checkout-public", home / ".agents/src/charness/skills/public" / skill_id / "SKILL.md")])
    existing = [(source, path.expanduser().resolve()) for source, path in candidates if path.expanduser().is_file()]
    resolved_source, resolved = existing[0] if existing else (None, None)
    reported_exists = reported_path.expanduser().is_file() if reported_path is not None else None
    status = "missing" if resolved is None else ("reported-ok" if reported_exists else "stale-reported-path" if reported_path is not None else "ok")
    warnings: list[str] = []
    if reported_path is not None and not reported_exists and resolved is not None:
        warnings.append("Reported host skill path is missing, but a current skill path was found.")
    if resolved_source in {"codex-versioned-cache", "codex-plugin-cache"}:
        warnings.append("Resolved to a versioned cache path; prefer a stable plugin path when available.")
    if resolved is None:
        warnings.append("No installed or repo-local skill path was found for the requested skill id.")
    return {"schema_version": 1, "skill_id": skill_id, "marketplace": marketplace, "plugin": plugin, "reported_path": str(reported_path) if reported_path else None, "reported_exists": reported_exists, "status": status, "resolved_source": resolved_source, "resolved_path": str(resolved) if resolved else None, "candidates": [{"source": source, "path": str(path.expanduser()), "exists": path.expanduser().is_file()} for source, path in candidates], "warnings": warnings, "next_step": f"Read `{resolved}` and continue from that installed skill." if resolved else "Use the repo-local skill source or reinstall the charness plugin surface before continuing."}

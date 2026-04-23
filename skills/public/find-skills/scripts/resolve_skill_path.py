#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


def _version_key(path: Path) -> tuple[int, ...]:
    parts = [int(part) for part in re.findall(r"\d+", path.name)]
    return tuple(parts) if parts else (0,)


def _existing(paths: list[tuple[str, Path]]) -> list[tuple[str, Path]]:
    seen: set[Path] = set()
    result: list[tuple[str, Path]] = []
    for source, path in paths:
        try:
            resolved = path.expanduser().resolve()
        except OSError:
            resolved = path.expanduser()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            result.append((source, resolved))
    return result


def _cache_candidates(codex_home: Path, skill_id: str) -> list[tuple[str, Path]]:
    cache_root = codex_home / "plugins" / "cache" / "local" / "charness"
    if not cache_root.is_dir():
        return []
    versions = sorted(
        [path for path in cache_root.iterdir() if path.is_dir()],
        key=_version_key,
        reverse=True,
    )
    return [
        ("codex-versioned-cache", version / "skills" / skill_id / "SKILL.md")
        for version in versions
    ]


def candidate_paths(
    *,
    skill_id: str,
    repo_root: Path,
    home: Path,
    codex_home: Path,
    reported_path: Path | None,
) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = []
    if reported_path is not None:
        candidates.append(("reported", reported_path))
    candidates.extend(
        [
            ("codex-stable-plugin", codex_home / "plugins" / "charness" / "skills" / skill_id / "SKILL.md"),
            ("repo-plugin-export", repo_root / "plugins" / "charness" / "skills" / skill_id / "SKILL.md"),
            ("repo-public-skill", repo_root / "skills" / "public" / skill_id / "SKILL.md"),
            ("repo-support-skill", repo_root / "skills" / "support" / skill_id / "SKILL.md"),
            ("repo-synced-support-skill", repo_root / "skills" / "support" / "generated" / skill_id / "SKILL.md"),
        ]
    )
    candidates.extend(_cache_candidates(codex_home, skill_id))
    candidates.extend(
        [
            (
                "managed-checkout-plugin",
                home / ".agents" / "src" / "charness" / "plugins" / "charness" / "skills" / skill_id / "SKILL.md",
            ),
            (
                "managed-checkout-public",
                home / ".agents" / "src" / "charness" / "skills" / "public" / skill_id / "SKILL.md",
            ),
        ]
    )
    return candidates


def resolve_skill_path(
    *,
    skill_id: str,
    repo_root: Path,
    home: Path,
    codex_home: Path,
    reported_path: Path | None,
) -> dict[str, Any]:
    candidates = candidate_paths(
        skill_id=skill_id,
        repo_root=repo_root,
        home=home,
        codex_home=codex_home,
        reported_path=reported_path,
    )
    existing = _existing(candidates)
    resolved_source = existing[0][0] if existing else None
    resolved_path = str(existing[0][1]) if existing else None
    reported_exists = reported_path.expanduser().is_file() if reported_path is not None else None
    status = "missing"
    warnings: list[str] = []
    if resolved_path is not None:
        status = "ok"
    if reported_path is not None and not reported_exists and resolved_path is not None:
        status = "stale-reported-path"
        warnings.append("Reported host skill path is missing, but a current skill path was found.")
    elif reported_path is not None and reported_exists:
        status = "reported-ok"
    if resolved_source == "codex-versioned-cache":
        warnings.append("Resolved to a versioned cache path; prefer a stable plugin path when available.")
    if resolved_path is None:
        warnings.append("No installed or repo-local skill path was found for the requested skill id.")
    return {
        "schema_version": 1,
        "skill_id": skill_id,
        "reported_path": str(reported_path) if reported_path is not None else None,
        "reported_exists": reported_exists,
        "status": status,
        "resolved_source": resolved_source,
        "resolved_path": resolved_path,
        "candidates": [
            {"source": source, "path": str(path.expanduser()), "exists": path.expanduser().is_file()}
            for source, path in candidates
        ],
        "warnings": warnings,
        "next_step": (
            f"Read `{resolved_path}` and continue from that installed skill."
            if resolved_path
            else "Use the repo-local skill source or reinstall the charness plugin surface before continuing."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a current charness skill path when a host-reported path is stale.")
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--reported-path", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    args = parser.parse_args()
    payload = resolve_skill_path(
        skill_id=args.skill_id,
        repo_root=args.repo_root.resolve(),
        home=args.home.expanduser().resolve(),
        codex_home=args.codex_home.expanduser().resolve(),
        reported_path=args.reported_path,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["resolved_path"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

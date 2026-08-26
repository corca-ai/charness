"""Resolve adapter-owned skill paths into the quality planner's scope."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def declared_skill_paths(
    repo_root: Path, raw: dict[str, Any], repo_file_listing: Any
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    values = raw.get("skill_ergonomics_skill_paths")
    if not isinstance(values, list):
        return rows
    canonical_repo_root = repo_root.resolve()
    canonical_support_root = repo_file_listing.support_dir(repo_root).resolve()
    support_is_external = canonical_support_root != (
        canonical_repo_root / "skills" / "support"
    ).resolve()
    for value in values:
        if not isinstance(value, str) or not value:
            continue
        declaration = Path(value)
        declaration_error: str | None = None
        if declaration.is_absolute() or ".." in declaration.parts:
            matches = []
            declaration_error = "path must be repo-relative and contain no '..' segment"
            candidate_scope = "repo"
        else:
            try:
                if support_is_external and value.startswith("skills/support/"):
                    support_pattern = value.removeprefix("skills/support/")
                    support_candidate = canonical_support_root / support_pattern
                    patterns = (
                        (f"{support_pattern}/SKILL.md", f"{support_pattern}/*/SKILL.md")
                        if support_candidate.is_dir()
                        else (support_pattern,)
                    )
                    matches = repo_file_listing.iter_matching_repo_files(
                        canonical_support_root, patterns
                    )
                    candidate_scope = "configured-external-support"
                else:
                    repo_candidate = repo_root / value
                    patterns = (
                        (f"{value}/SKILL.md", f"{value}/*/SKILL.md")
                        if repo_candidate.is_dir()
                        else (value,)
                    )
                    matches = repo_file_listing.iter_matching_repo_files(
                        repo_root, patterns
                    )
                    candidate_scope = "repo"
            except (NotImplementedError, OSError, ValueError):
                matches = []
                declaration_error = "path pattern could not be interpreted"
                candidate_scope = "repo"
        skill_matches: list[str] = []
        target_scopes: set[str] = set()
        excluded_match_count = 0
        for path in matches:
            if not path.is_file() or path.name != "SKILL.md":
                continue
            try:
                canonical_path = path.resolve()
            except OSError:
                excluded_match_count += 1
                continue
            if candidate_scope == "repo" and canonical_path.is_relative_to(
                canonical_repo_root
            ):
                skill_matches.append(canonical_path.relative_to(canonical_repo_root).as_posix())
                target_scopes.add("repo")
                continue
            if (
                candidate_scope == "configured-external-support"
                and canonical_path.is_relative_to(canonical_support_root)
            ):
                virtual_path = Path("skills/support") / canonical_path.relative_to(
                    canonical_support_root
                )
                skill_matches.append(virtual_path.as_posix())
                target_scopes.add("configured-external-support")
                continue
            excluded_match_count += 1
        row: dict[str, Any] = {
            "declaration": value,
            "target_state": "resolved" if skill_matches else "unreachable",
            "resolved_paths": sorted(set(skill_matches)),
            "routing_state": "partial" if excluded_match_count else "routed",
            "packet_id": "skill-ergonomics",
        }
        if target_scopes:
            row["target_scope"] = (
                next(iter(target_scopes)) if len(target_scopes) == 1 else "mixed"
            )
        if declaration_error is not None:
            row["declaration_error"] = declaration_error
        if excluded_match_count:
            row["excluded_match_count"] = excluded_match_count
        rows.append(row)
    return rows


def effective_skill_paths(
    discovered: list[str], declared_rows: list[dict[str, Any]], raw: dict[str, Any]
) -> tuple[list[str], str]:
    """Use an explicit adapter skill surface as planner scope when configured."""
    values = raw.get("skill_ergonomics_skill_paths")
    if not isinstance(values, list) or not any(
        isinstance(value, str) and value.strip() for value in values
    ):
        return discovered, "discovered"
    resolved = sorted(
        {
            path
            for row in declared_rows
            if row.get("target_state") == "resolved"
            for path in row.get("resolved_paths", [])
            if isinstance(path, str)
        }
    )
    return resolved, "adapter-declared"

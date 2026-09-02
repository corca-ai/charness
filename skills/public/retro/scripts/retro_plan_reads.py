"""Build the retro planner's required-read inventory.

This module owns the read-side contract of a retro plan: adapter-declared
evidence availability, the artifact-or-scaffold choice, and the required
references needed before writing. Keeping those decisions together lets
``plan_retro_run.py`` own change scope, lens briefing, gate packets, and
envelope assembly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def repo_evidence_read(
    repo_root: Path,
    path: str,
    *,
    read: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Describe optional adapter evidence without pretending directories are files."""
    item: dict[str, Any] = read(
        path,
        "evidence",
        "adapter-declared local evidence; inspect when available, then apply its repo-owned contract",
        base="repo",
    )
    candidate = repo_root / path
    item["available"] = candidate.exists()
    item["path_kind"] = (
        "directory" if candidate.is_dir() else "file" if candidate.is_file() else "missing"
    )
    return item


def required_reads(
    *,
    repo_root: Path,
    adapter: dict[str, Any],
    artifact: dict[str, Any],
    lens_brief: dict[str, str],
    read: Callable[..., dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build the read inventory needed before a retro artifact is written."""
    reads: list[dict[str, Any]] = []
    # The counterfactual is mandatory in every retro and the lens catalog + domain
    # triggers are not inlined in SKILL.md, so expert-lens.md is an unconditional
    # floor. The why carries the work-class-specific lens brief.
    reads.append(read("references/expert-lens.md", "reference", lens_brief["why"], base="skill"))

    if artifact["exists"]:
        reads.append(
            read(
                artifact["path"],
                "artifact",
                "today's retro already started; continue it",
                base="repo",
            )
        )
    else:
        reads.append(
            read(
                "scripts/scaffold_retro_artifact.py",
                "script",
                "no retro artifact yet; scaffold before writing",
                base="skill",
            )
        )

    if not adapter.get("found") or not adapter.get("valid") or adapter.get("errors"):
        reads.append(
            read(
                "references/adapter-contract.md",
                "reference",
                "adapter is missing or invalid; repair before relying on adapter paths",
                base="skill",
            )
        )

    already_named = {str(item["path"]) for item in reads}
    for evidence_path in adapter["data"].get("evidence_paths", []):
        path = str(evidence_path)
        if path and path not in already_named:
            reads.append(repo_evidence_read(repo_root, path, read=read))
            already_named.add(path)
    summary_path = str(adapter["data"].get("summary_path") or "")
    if summary_path and (repo_root / summary_path).is_file():
        reads.append(
            read(
                summary_path,
                "artifact",
                "recent-lessons digest to compare this retro's window against",
                base="repo",
            )
        )
    return reads

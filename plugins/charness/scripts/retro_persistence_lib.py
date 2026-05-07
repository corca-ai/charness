from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from scripts.portable_artifact_lib import sanitize_artifact_json
from scripts.recent_lessons_lib import build_indexed_recent_lessons, write_lesson_selection_index

_STUB_SUMMARY_MARKERS: tuple[str, ...] = (
    "No current focus bullets found in retro lesson index.",
    "No repeat traps extracted from retro lesson index.",
    "No next improvements extracted from retro lesson index.",
)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _write_snapshot(path: Path, snapshot_data: dict[str, Any], *, repo_root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = sanitize_artifact_json(snapshot_data, repo_root=repo_root)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_artifact_name(artifact_name: str) -> tuple[str, bool]:
    """Append `.md` when missing so glob('*.md') downstream readers find the file."""
    if artifact_name.endswith(".md"):
        return artifact_name, False
    return artifact_name + ".md", True


def is_stub_summary(text: str) -> bool:
    """Return True only when the text matches the empty-stub digest signature.

    Used to distinguish a hand-curated `recent-lessons.md` from one that the
    digest builder itself wrote when no candidates were available.
    """
    return all(marker in text for marker in _STUB_SUMMARY_MARKERS)


def persist_retro_artifact(
    *,
    repo_root: Path,
    output_dir: Path,
    artifact_name: str,
    markdown_text: str,
    summary_path: Path | None,
    snapshot_path: Path | None = None,
    snapshot_data: dict[str, Any] | None = None,
    force_empty_summary: bool = False,
) -> dict[str, Any]:
    normalized_name, was_normalized = normalize_artifact_name(artifact_name)
    if was_normalized:
        print(
            f"persist_retro_artifact: --artifact-name '{artifact_name}' lacks .md; "
            f"writing '{normalized_name}' so the lesson-selection-index can read it.",
            file=sys.stderr,
        )

    artifact_path = output_dir / normalized_name
    _write_text(artifact_path, markdown_text)

    result: dict[str, Any] = {
        "artifact_path": str(artifact_path.relative_to(repo_root)),
        "summary_refreshed": False,
    }
    if was_normalized:
        result["artifact_name_normalized"] = True

    if snapshot_path is not None and snapshot_data is not None:
        _write_snapshot(snapshot_path, snapshot_data, repo_root=repo_root)
        result["snapshot_path"] = str(snapshot_path.relative_to(repo_root))

    if summary_path is not None and artifact_path.resolve() != summary_path.resolve():
        digest = build_indexed_recent_lessons(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
        section_counts = digest.section_counts
        no_candidates = sum(section_counts.values()) == 0
        existing_text = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
        existing_is_protected = bool(existing_text.strip()) and not is_stub_summary(existing_text)

        if no_candidates and existing_is_protected and not force_empty_summary:
            print(
                f"persist_retro_artifact: lesson selection produced 0 candidates; "
                f"refusing to overwrite existing summary at "
                f"{summary_path.relative_to(repo_root)}. Pass --force-empty-summary "
                f"once you have confirmed it is safe to replace with the empty-stub digest.",
                file=sys.stderr,
            )
            result["summary_path"] = str(summary_path.relative_to(repo_root))
            result["summary_refreshed"] = False
            result["summary_skipped_reason"] = "no_candidates_existing_summary_protected"
        else:
            _write_text(summary_path, digest.summary_text)
            index_path = write_lesson_selection_index(repo_root, output_dir, summary_path)
            result["summary_path"] = str(summary_path.relative_to(repo_root))
            result["lesson_selection_index_path"] = str(index_path.relative_to(repo_root))
            result["summary_refreshed"] = True

    return result

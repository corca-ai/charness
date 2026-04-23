from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.recent_lessons_lib import build_recent_lessons, write_lesson_selection_index


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _write_snapshot(path: Path, snapshot_data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def persist_retro_artifact(
    *,
    repo_root: Path,
    output_dir: Path,
    artifact_name: str,
    markdown_text: str,
    summary_path: Path | None,
    snapshot_path: Path | None = None,
    snapshot_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifact_path = output_dir / artifact_name
    _write_text(artifact_path, markdown_text)

    result: dict[str, Any] = {
        "artifact_path": str(artifact_path.relative_to(repo_root)),
        "summary_refreshed": False,
    }

    if snapshot_path is not None and snapshot_data is not None:
        _write_snapshot(snapshot_path, snapshot_data)
        result["snapshot_path"] = str(snapshot_path.relative_to(repo_root))

    if summary_path is not None and artifact_path.resolve() != summary_path.resolve():
        digest = build_recent_lessons(artifact_path, repo_root=repo_root)
        _write_text(summary_path, digest.summary_text)
        index_path = write_lesson_selection_index(repo_root, output_dir, summary_path)
        result["summary_path"] = str(summary_path.relative_to(repo_root))
        result["lesson_selection_index_path"] = str(index_path.relative_to(repo_root))
        result["summary_refreshed"] = True

    return result

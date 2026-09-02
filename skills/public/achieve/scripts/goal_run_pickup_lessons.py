#!/usr/bin/env python3
"""Own the bounded, read-only lesson projection used by Goal Run pickup.

This is a separate concept from issue identity, binding, and child selection:
pickup may add advisory lessons from either the configured digest or the ledger
preview, but that projection must never write state or affect selection.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


_SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_retro_paths = _SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.retro_output_dir_lib"
)
_lesson_preview = _SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.lesson_selection_preview_lib"
)

LESSON_SECTIONS = ("Current Focus", "Repeat Traps", "Next-Time Checklist")
LESSON_MAX_CHARS = 1200


def bounded_lesson(text: str) -> str:
    lesson = " ".join(text.split())
    if len(lesson) > LESSON_MAX_CHARS:
        return lesson[: LESSON_MAX_CHARS - 1].rstrip() + "…"
    return lesson


def _read_lesson_digest(path: Path, repo_root: Path) -> dict[str, Any]:
    relative = path.relative_to(repo_root)
    base: dict[str, Any] = {
        "source": str(relative),
        "selection": "first-item-per-section",
    }
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {**base, "status": "unavailable", "reason": type(exc).__name__}

    selected: list[dict[str, str]] = []
    current: str | None = None
    item: list[str] = []

    def finish_item() -> None:
        nonlocal item
        if (
            current in LESSON_SECTIONS
            and item
            and not any(entry["section"] == current for entry in selected)
        ):
            lesson = " ".join(part.strip() for part in item if part.strip())
            selected.append({"section": current, "lesson": bounded_lesson(lesson)})
        item = []

    for line in lines:
        if line.startswith("## "):
            finish_item()
            current = line[3:].strip()
        elif current in LESSON_SECTIONS and line.startswith("- "):
            finish_item()
            item = [line[2:]]
        elif item and line.strip():
            item.append(line)
    finish_item()
    if not selected:
        return {**base, "status": "unavailable", "reason": "projection-empty"}
    return {**base, "status": "selected", "items": selected, "item_count": len(selected)}


def _read_lesson_preview(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    index_path = output_dir / "lesson-selection-index.json"
    base: dict[str, Any] = {
        "source": str(index_path.relative_to(repo_root)),
        "selection": "bounded-ledger-preview",
    }
    try:
        preview = _lesson_preview.build_lesson_selection_preview(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=None,
            seed="goal-run-pickup",
        )
        raw_items = preview.get("items")
        if not isinstance(raw_items, list):
            return {**base, "status": "unavailable", "reason": "preview-items-invalid"}
        selected = [
            {"lesson": bounded_lesson(item["lesson"])}
            for item in raw_items[: len(LESSON_SECTIONS)]
            if isinstance(item, dict)
            and isinstance(item.get("lesson"), str)
            and item["lesson"].strip()
        ]
    except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
        return {**base, "status": "unavailable", "reason": type(exc).__name__}
    if not selected:
        return {**base, "status": "unavailable", "reason": "projection-empty"}
    return {**base, "status": "selected", "items": selected, "item_count": len(selected)}


def read_lesson_projection(repo_root: Path) -> dict[str, Any]:
    """Read one bounded, advisory digest or ledger preview without writing state."""
    try:
        output_dir = _retro_paths.retro_output_dir(repo_root)
        summary_path = _retro_paths.retro_summary_path(repo_root)
    except (FileNotFoundError, KeyError, OSError, TypeError, ValueError):
        output_dir = repo_root / "charness-artifacts/retro"
        summary_path = output_dir / "recent-lessons.md"
    if summary_path is None:
        return _read_lesson_preview(repo_root, output_dir)
    return _read_lesson_digest(summary_path, repo_root)

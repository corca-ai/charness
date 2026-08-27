#!/usr/bin/env python3
"""Read the bounded lesson projection when an achieve goal is entered.

Retro owns the ledger and its derived projections. Achieve only reads the
already-rendered compact digest, or the precomputed selection index when that
digest is absent. It never rebuilds the ledger, refreshes a digest, records a
shown set, or writes a session receipt. Lesson context is useful but optional,
so a missing or malformed projection is reported without blocking goal pickup.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap() -> SimpleNamespace:
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

DEFAULT_OUTPUT_DIR = Path("charness-artifacts/retro")
DEFAULT_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "recent-lessons.md"
INDEX_FILENAME = "lesson-selection-index.json"
KIND = "charness.goal-lesson-pickup/v1"
SECTIONS = (
    ("Current Focus", 2),
    ("Repeat Traps", 4),
    ("Next-Time Checklist", 4),
)


def _relative(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root))


def _safe_repo_path(repo_root: Path, value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"retro adapter {field} must be a non-empty path")
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError(f"retro adapter {field} must be repo-relative")
    resolved_root = repo_root.resolve()
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"retro adapter {field} must stay inside the repository") from exc
    return resolved


def _find_retro_resolver() -> Path | None:
    """Find the sibling retro resolver in authoring and exported layouts."""
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "retro" / "scripts" / "resolve_adapter.py"
        if candidate.is_file():
            return candidate
    return None


def _load_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("achieve_goal_lesson_retro_adapter", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load retro adapter resolver: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _projection_paths(repo_root: Path) -> tuple[Path, Path, str | None]:
    """Resolve retro-owned projection paths without scanning retro artifacts."""
    resolver = _find_retro_resolver()
    if resolver is None:
        return repo_root / DEFAULT_OUTPUT_DIR, repo_root / DEFAULT_SUMMARY_PATH, None
    try:
        adapter = _load_module(resolver).load_adapter(repo_root)
    except (ImportError, OSError, RuntimeError, UnicodeError, ValueError) as exc:
        return (
            repo_root / DEFAULT_OUTPUT_DIR,
            repo_root / DEFAULT_SUMMARY_PATH,
            f"retro-adapter-unavailable: {exc}",
        )
    if not adapter.get("valid"):
        return (
            repo_root / DEFAULT_OUTPUT_DIR,
            repo_root / DEFAULT_SUMMARY_PATH,
            "retro-adapter-invalid",
        )
    data = adapter.get("data")
    if not isinstance(data, dict):
        return (
            repo_root / DEFAULT_OUTPUT_DIR,
            repo_root / DEFAULT_SUMMARY_PATH,
            "retro-adapter-invalid",
        )
    try:
        output_dir = _safe_repo_path(repo_root, data.get("output_dir"), "output_dir")
        summary_value = data.get("summary_path") or "charness-artifacts/retro/recent-lessons.md"
        summary_path = _safe_repo_path(repo_root, summary_value, "summary_path")
    except ValueError as exc:
        return repo_root / DEFAULT_OUTPUT_DIR, repo_root / DEFAULT_SUMMARY_PATH, str(exc)
    return output_dir, summary_path, None


def _sections(text: str) -> dict[str, str]:
    result: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            result[current] = []
        elif current is not None:
            result[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in result.items()}


def _bullets(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("- "):
            if current:
                items.append(" ".join(part.strip() for part in current if part.strip()))
            current = [line[2:].strip()]
        elif current and line.strip():
            current.append(line.strip())
    if current:
        items.append(" ".join(part.strip() for part in current if part.strip()))
    return [item for item in items if item]


def _summary_items(text: str) -> list[dict[str, str]]:
    parsed = _sections(text)
    items: list[dict[str, str]] = []
    for section, limit in SECTIONS:
        items.extend(
            {"section": section, "lesson": item}
            for item in _bullets(parsed.get(section, ""))[:limit]
        )
    return items


def _index_items(path: Path) -> list[dict[str, str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    if not isinstance(payload, dict) or payload.get("kind") != "retro-lesson-selection-index":
        return []
    candidates = payload.get("top_candidates")
    if not isinstance(candidates, list):
        candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return []
    items: list[dict[str, str]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        lesson = candidate.get("lesson")
        section = candidate.get("kind")
        if isinstance(lesson, str) and lesson.strip() and isinstance(section, str):
            items.append({"section": section, "lesson": lesson.strip()})
        if len(items) >= sum(limit for _section, limit in SECTIONS):
            break
    return items


def read_goal_lessons(repo_root: Path, goal_key: str) -> dict[str, Any]:
    """Return one non-blocking, projection-only lesson read for a goal entry."""
    root = repo_root.resolve()
    if not isinstance(goal_key, str) or not goal_key.strip():
        return {"kind": KIND, "status": "unavailable", "reason": "goal-key-missing"}

    output_dir, summary_path, path_error = _projection_paths(root)
    index_path = output_dir / INDEX_FILENAME
    base: dict[str, Any] = {
        "kind": KIND,
        "goal_key": goal_key.strip(),
        "selection": "precomputed-projection-only",
        "freshness": "not-checked",
        "index_path": _relative(root, index_path),
    }
    if path_error is not None:
        base.update(status="unavailable", reason=path_error)
        return base

    try:
        summary_text = summary_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        summary_text = ""
    items = _summary_items(summary_text)
    if items:
        base.update(
            status="selected",
            source="recent-lessons",
            source_path=_relative(root, summary_path),
            items=items,
            item_count=len(items),
        )
        return base

    items = _index_items(index_path)
    if items:
        base.update(
            status="selected",
            source="lesson-selection-index",
            source_path=_relative(root, index_path),
            items=items,
            item_count=len(items),
        )
        return base

    base.update(
        status="unavailable",
        reason="lesson-projection-missing-or-empty",
        expected_paths=[_relative(root, summary_path), _relative(root, index_path)],
    )
    return base


def _emit_yaml(payload: dict[str, Any]) -> None:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        helper = ancestor / "scripts" / "yaml_output.py"
        if not helper.is_file():
            continue
        module = _load_module(helper)
        module.emit_yaml(payload)
        return
    raise RuntimeError("scripts/yaml_output.py not found above goal_lesson_pickup.py")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read the compact lesson projection for one achieve goal entry"
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--goal-key", required=True, help="Stable goal identity for this entry")
    args = parser.parse_args(argv)
    _emit_yaml(read_goal_lessons(args.repo_root, args.goal_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

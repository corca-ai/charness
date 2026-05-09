"""Append-only emit for charness T-events.

T-events are the artifact-level analog of hermes-agent runtime telemetry:
charness skills emit lifecycle records into a consumer repo's
``<storage_path>/<event_type>.jsonl`` so downstream skills (e.g. the Skill-T
mechanism inventory) can read them as Tier C evidence.

Emission is opt-in per consumer repo via ``.agents/t-events-adapter.yaml``
matching ``integrations/t-events/manifest.schema.json``. Without that file,
or when ``enabled: false``, every emit call returns ``{"emitted": False, ...}``
with a structured reason — callers do not need to gate emission themselves.

Records validate against ``integrations/t-events/event.schema.json`` (v1).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ADAPTER_RELATIVE_PATH = ".agents/t-events-adapter.yaml"
DEFAULT_STORAGE_PATH = ".charness/t-events"
VALID_EVENT_TYPES: tuple[str, ...] = ("skill_invoked", "lesson_cited", "anchor_invoked")


def now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def load_adapter(repo_root: Path) -> dict[str, Any] | None:
    """Return parsed manifest or ``None`` when absent or unreadable."""

    adapter_path = repo_root / ADAPTER_RELATIVE_PATH
    if not adapter_path.is_file():
        return None
    try:
        data = yaml.safe_load(adapter_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _resolve_storage_dir(repo_root: Path, adapter: dict[str, Any]) -> Path:
    rel = adapter.get("storage_path") or DEFAULT_STORAGE_PATH
    return repo_root / rel


def _filter_pass(adapter: dict[str, Any], event_type: str) -> bool:
    events = adapter.get("events")
    if events is None:
        return True
    return isinstance(events, list) and event_type in events


def _rotate_if_needed(target: Path, adapter: dict[str, Any]) -> None:
    rotation = adapter.get("rotation")
    if not isinstance(rotation, dict):
        return
    max_size_mb = rotation.get("max_size_mb")
    if not isinstance(max_size_mb, int) or max_size_mb <= 0:
        return
    if not target.is_file() or target.stat().st_size < max_size_mb * 1024 * 1024:
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rotated = target.with_name(f"{target.stem}.{stamp}{target.suffix}")
    target.rename(rotated)
    max_files = rotation.get("max_files")
    if isinstance(max_files, int) and max_files >= 1:
        siblings = sorted(
            (
                p
                for p in target.parent.glob(f"{target.stem}.*{target.suffix}")
                if p != target
            ),
            key=lambda p: p.name,
        )
        excess = len(siblings) - max_files
        for old in siblings[: max(0, excess)]:
            old.unlink(missing_ok=True)


def append_event(
    repo_root: Path,
    event: dict[str, Any],
    *,
    adapter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append one event to ``<storage_path>/<event_type>.jsonl``.

    Returns a structured payload with ``emitted: bool``. When ``emitted`` is
    false, ``reason`` names the gate that suppressed the emit so callers can
    surface it without needing to peek into adapter internals.
    """

    if adapter is None:
        adapter = load_adapter(repo_root)
    if adapter is None:
        return {"emitted": False, "reason": "no_adapter"}
    if not adapter.get("enabled", False):
        return {"emitted": False, "reason": "disabled"}

    event_type = event.get("event_type")
    if event_type not in VALID_EVENT_TYPES:
        return {"emitted": False, "reason": "invalid_event_type"}
    if not _filter_pass(adapter, event_type):
        return {"emitted": False, "reason": "event_filtered"}

    storage_dir = _resolve_storage_dir(repo_root, adapter)
    storage_dir.mkdir(parents=True, exist_ok=True)
    target = storage_dir / f"{event_type}.jsonl"
    _rotate_if_needed(target, adapter)

    line = json.dumps(event, ensure_ascii=False, sort_keys=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    try:
        rel = target.relative_to(repo_root)
        path_value = str(rel)
    except ValueError:
        path_value = str(target)
    return {"emitted": True, "path": path_value}


def emit_lesson_cited(
    repo_root: Path,
    *,
    lesson_path: str,
    citing_skill: str,
    citing_artifact_path: str | None = None,
    timestamp: str | None = None,
    adapter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "event_type": "lesson_cited",
        "timestamp": timestamp or now_iso(),
        "lesson_path": lesson_path,
        "citing_skill": citing_skill,
    }
    if citing_artifact_path:
        event["citing_artifact_path"] = citing_artifact_path
    return append_event(repo_root, event, adapter=adapter)


_INLINE_SOURCE_PATTERN = re.compile(
    r"\(source:\s*`?(charness-artifacts/retro/[^)`\s]+\.md)`?\s*\)"
)
_SOURCES_LIST_PATTERN = re.compile(
    r"^\s*-\s*`?(charness-artifacts/retro/[^`\s]+\.md)`?\s*$",
    re.MULTILINE,
)


def extract_lesson_cites_from_markdown(text: str) -> list[str]:
    """Return ordered, unique retro-artifact cites surfaced in ``text``.

    Both ``(source: charness-artifacts/retro/...)`` inline annotations and
    ``## Sources`` list entries are recognised. Order follows first
    appearance so emit order matches reading order.
    """

    seen: dict[str, None] = {}
    for match in _INLINE_SOURCE_PATTERN.finditer(text):
        seen.setdefault(match.group(1).strip(), None)
    for match in _SOURCES_LIST_PATTERN.finditer(text):
        seen.setdefault(match.group(1).strip(), None)
    return list(seen.keys())


def emit_retro_lesson_cites(
    repo_root: Path,
    *,
    markdown_text: str,
    citing_artifact_path: str,
    citing_skill: str = "retro",
    adapter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Scan ``markdown_text`` for retro cites and emit one event per cite.

    Returns ``{"emitted_count": N, "skipped_count": M, "reasons": {...}}``
    so callers can surface a single-line summary without touching jsonl.
    """

    if adapter is None:
        adapter = load_adapter(repo_root)
    cites = extract_lesson_cites_from_markdown(markdown_text)
    emitted_count = 0
    skipped_count = 0
    reasons: dict[str, int] = {}
    for lesson_path in cites:
        result = emit_lesson_cited(
            repo_root,
            lesson_path=lesson_path,
            citing_skill=citing_skill,
            citing_artifact_path=citing_artifact_path,
            adapter=adapter,
        )
        if result.get("emitted"):
            emitted_count += 1
        else:
            skipped_count += 1
            reason = str(result.get("reason", "unknown"))
            reasons[reason] = reasons.get(reason, 0) + 1
    return {
        "emitted_count": emitted_count,
        "skipped_count": skipped_count,
        "reasons": reasons,
        "cite_count": len(cites),
    }

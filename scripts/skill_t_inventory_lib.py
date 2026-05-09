"""Build the Skill-T mechanism inventory.

The inventory is the Leg 1 deliverable of the issue-135 umbrella spec: each
public skill gets one row populated across four columns that describe how
visible the (H + agent) T-loop is for that skill today.

Columns:

* ``lesson_cite_chain`` (substrate tier B) — retro artifacts under
  ``charness-artifacts/retro/`` whose body references this skill via one of
  the deterministic markers below. Empty list means the cite chain has not
  produced traceable lessons for the skill yet.
* ``lifecycle_survival`` (substrate tier B+) — for every lesson in
  ``charness-artifacts/retro/lesson-selection-index.json`` whose ``lesson``
  text matches this skill's markers, the max ``source_count`` (recurrence)
  and the freshest ``age_days`` (recency rotation) are surfaced.
* ``anchor_wiring`` (orthogonal) — anchor names mentioned anywhere under
  ``skills/public/<skill>/`` (Jackson, Raskin, Weinberg, Gawande, Minto,
  Engelbart, Klein, Kahneman). Captures whether a LAM-critique substrate is
  already wired into the skill's prose.
* ``tier_c_events`` (placeholder, awaiting Leg 2 evidence) — counts of
  T-events from the resolved storage path. When zero events reference the
  skill the field carries the explicit ``"awaiting events"`` marker so the
  absence is visible rather than silent.

Determinism: per-skill markers are decorated patterns rather than bare
``\\bS\\b`` matches because several skill ids (``issue``, ``release``,
``quality``, ``spec``) are common English words. Decorated patterns trade a
small amount of recall for much higher precision.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

ANCHORS: tuple[str, ...] = (
    "Jackson",
    "Raskin",
    "Weinberg",
    "Gawande",
    "Minto",
    "Engelbart",
    "Klein",
    "Kahneman",
)

INVENTORY_VERSION = 1
DEFAULT_STORAGE_PATH = ".charness/t-events"
RETRO_DIR_RELATIVE = "charness-artifacts/retro"
LESSON_INDEX_RELATIVE = f"{RETRO_DIR_RELATIVE}/lesson-selection-index.json"
TIER_C_AWAITING = "awaiting events"
TIER_C_POPULATED = "populated"
PUBLIC_SKILLS_RELATIVE = "skills/public"


def list_public_skill_ids(repo_root: Path) -> list[str]:
    public = repo_root / PUBLIC_SKILLS_RELATIVE
    if not public.is_dir():
        return []
    ids: list[str] = []
    for entry in sorted(public.iterdir()):
        if not entry.is_dir():
            continue
        if not (entry / "SKILL.md").is_file():
            continue
        ids.append(entry.name)
    return ids


def _build_skill_id_patterns(skill_id: str) -> list[re.Pattern[str]]:
    escaped = re.escape(skill_id)
    return [
        re.compile(rf"\bcharness:{escaped}\b"),
        re.compile(rf"skills/public/{escaped}/"),
        re.compile(rf"`{escaped}`"),
        re.compile(rf'"{escaped}"'),
        re.compile(rf"\b{escaped} skill\b"),
        re.compile(rf"\b{escaped} 스킬\b"),
    ]


def _text_mentions_skill(text: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def _retro_artifacts_for_skill(
    repo_root: Path, skill_id: str
) -> list[str]:
    retro_dir = repo_root / RETRO_DIR_RELATIVE
    if not retro_dir.is_dir():
        return []
    patterns = _build_skill_id_patterns(skill_id)
    matches: list[str] = []
    for path in sorted(retro_dir.glob("*.md")):
        if path.name == "recent-lessons.md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _text_mentions_skill(text, patterns):
            matches.append(str(path.relative_to(repo_root)))
    return matches


def _load_lesson_index(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / LESSON_INDEX_RELATIVE
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _lifecycle_for_skill(
    skill_id: str, lesson_index: dict[str, Any] | None
) -> dict[str, Any]:
    base = {
        "matched_lesson_count": 0,
        "max_source_count": 0,
        "freshest_age_days": None,
    }
    if not lesson_index:
        return base
    candidates = lesson_index.get("candidates") or lesson_index.get("top_candidates") or []
    if not isinstance(candidates, list):
        return base
    patterns = _build_skill_id_patterns(skill_id)
    matched = 0
    max_source_count = 0
    freshest_age_days: int | None = None
    for entry in candidates:
        if not isinstance(entry, dict):
            continue
        lesson_text = entry.get("lesson")
        if not isinstance(lesson_text, str):
            continue
        if not _text_mentions_skill(lesson_text, patterns):
            continue
        matched += 1
        source_count = entry.get("source_count")
        if isinstance(source_count, int) and source_count > max_source_count:
            max_source_count = source_count
        age_days = entry.get("age_days")
        if isinstance(age_days, int):
            if freshest_age_days is None or age_days < freshest_age_days:
                freshest_age_days = age_days
    return {
        "matched_lesson_count": matched,
        "max_source_count": max_source_count,
        "freshest_age_days": freshest_age_days,
    }


def _anchors_in_skill_surface(repo_root: Path, skill_id: str) -> list[str]:
    skill_dir = repo_root / PUBLIC_SKILLS_RELATIVE / skill_id
    if not skill_dir.is_dir():
        return []
    anchor_hits: dict[str, None] = {}
    for path in sorted(skill_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for anchor in ANCHORS:
            if anchor in anchor_hits:
                continue
            if re.search(rf"\b{anchor}\b", text):
                anchor_hits[anchor] = None
    return list(anchor_hits.keys())


def _resolve_t_events_storage(repo_root: Path) -> Path:
    adapter_path = repo_root / ".agents" / "t-events-adapter.yaml"
    storage_rel = DEFAULT_STORAGE_PATH
    if adapter_path.is_file():
        try:
            import yaml

            data = yaml.safe_load(adapter_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("storage_path"), str):
                storage_rel = data["storage_path"]
        except Exception:  # noqa: BLE001
            pass
    return repo_root / storage_rel


def _tier_c_for_skill(skill_id: str, storage_dir: Path) -> dict[str, Any]:
    if not storage_dir.is_dir():
        return {
            "status": TIER_C_AWAITING,
            "event_count": 0,
            "event_types": {},
        }
    type_counts: dict[str, int] = {}
    total = 0
    for jsonl_path in sorted(storage_dir.glob("*.jsonl")):
        try:
            lines = jsonl_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            if not _row_references_skill(row, skill_id):
                continue
            row_event_type = row.get("event_type")
            if not isinstance(row_event_type, str):
                continue
            type_counts[row_event_type] = type_counts.get(row_event_type, 0) + 1
            total += 1
    if total == 0:
        return {
            "status": TIER_C_AWAITING,
            "event_count": 0,
            "event_types": {},
        }
    return {
        "status": TIER_C_POPULATED,
        "event_count": total,
        "event_types": dict(sorted(type_counts.items())),
    }


def _row_references_skill(row: dict[str, Any], skill_id: str) -> bool:
    event_type = row.get("event_type")
    if event_type == "skill_invoked":
        return row.get("skill_id") == skill_id
    if event_type in ("lesson_cited", "anchor_invoked"):
        return row.get("citing_skill") == skill_id
    return False


def build_inventory(repo_root: Path) -> dict[str, Any]:
    """Compute the inventory payload for ``repo_root`` deterministically."""

    storage_dir = _resolve_t_events_storage(repo_root)
    lesson_index = _load_lesson_index(repo_root)
    rows: list[dict[str, Any]] = []
    for skill_id in list_public_skill_ids(repo_root):
        cite_chain = _retro_artifacts_for_skill(repo_root, skill_id)
        lifecycle = _lifecycle_for_skill(skill_id, lesson_index)
        anchors = _anchors_in_skill_surface(repo_root, skill_id)
        tier_c = _tier_c_for_skill(skill_id, storage_dir)
        rows.append(
            {
                "skill_id": skill_id,
                "lesson_cite_chain": {
                    "tier": "B",
                    "retro_artifact_count": len(cite_chain),
                    "retro_artifacts": cite_chain,
                },
                "lifecycle_survival": {
                    "tier": "B+",
                    **lifecycle,
                },
                "anchor_wiring": {
                    "orthogonal_to_t_tier": True,
                    "anchors": anchors,
                },
                "tier_c_events": tier_c,
            }
        )
    return {
        "version": INVENTORY_VERSION,
        "kind": "skill-t-mechanism-inventory",
        "spec": "charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md",
        "tier_c_marker": TIER_C_AWAITING,
        "skills": rows,
    }


def render_inventory_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Skill-T Mechanism Inventory")
    lines.append("")
    lines.append(
        "Per-skill view of the (H + agent) T-loop substrate. Each row carries "
        "four columns: lesson-cite-chain (B), lifecycle-survival (B+), "
        "anchor-wiring (orthogonal), tier-c-events (placeholder)."
    )
    lines.append("")
    lines.append(f"- spec: [{payload['spec']}](../{Path(payload['spec']).name})")
    lines.append(f"- tier_c_marker when no events reference a skill: `{payload['tier_c_marker']}`")
    lines.append("")
    lines.append("| skill | cite-chain (retros) | lifecycle (max recurrence / freshest age days) | anchors | tier C events |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in payload["skills"]:
        cite_count = row["lesson_cite_chain"]["retro_artifact_count"]
        max_src = row["lifecycle_survival"]["max_source_count"]
        age_days = row["lifecycle_survival"]["freshest_age_days"]
        age_repr = "—" if age_days is None else str(age_days)
        anchors = row["anchor_wiring"]["anchors"]
        anchor_repr = ", ".join(anchors) if anchors else "—"
        tier_c = row["tier_c_events"]
        if tier_c["status"] == TIER_C_AWAITING:
            tier_c_repr = TIER_C_AWAITING
        else:
            type_breakdown = ", ".join(
                f"{etype}:{count}" for etype, count in tier_c["event_types"].items()
            )
            tier_c_repr = f"{tier_c['event_count']} ({type_breakdown})"
        lines.append(
            f"| `{row['skill_id']}` | {cite_count} | {max_src} / {age_repr} | {anchor_repr} | {tier_c_repr} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_inventory(repo_root: Path, output_dir: Path | None = None) -> dict[str, Path]:
    payload = build_inventory(repo_root)
    if output_dir is None:
        output_dir = repo_root / "charness-artifacts" / "skill-t-mechanism"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "inventory.json"
    md_path = output_dir / "inventory.md"
    json_text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(render_inventory_markdown(payload) + "\n", encoding="utf-8")
    return {"json": json_path, "markdown": md_path}

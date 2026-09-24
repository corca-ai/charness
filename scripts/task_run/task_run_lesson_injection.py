"""Declared-class lesson injection for lane prompts.

Ledger lookup, matching, prompt rendering, and result normalization live here
so the lane runner and completion stay under their file-length caps. Matching
is declared recurrence-class slug equality against the validated ledger only;
scope-path matching is deferred until the ledger has explicit scope tags.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.lessons import lesson_ledger_lib as _lesson_ledger
from scripts.lessons import recent_lesson_selection as _lesson_selection

# Retro text is unbounded; cap one lane's complete added prompt block at 16 KiB.
LESSON_INJECTION_BUDGET_BYTES = 16 * 1024
LESSON_INJECTION_SCHEMA = "charness.task_run_lesson_injection.v1"
LESSON_LEDGER_RELATIVE_PATH = "charness-artifacts/retro/lesson-ledger.json"
# Scope-path matching is deferred until the validated ledger has explicit scope tags.
LESSON_INJECTION_NON_CLAIM = (
    "Scope-path matching is deferred pending ledger scope tags; this result makes "
    "no claim about scope-path coverage."
)


def _declared_recurrence_classes(prompt: str) -> list[str]:
    """Return distinct authored recurrence-class slugs in brief order."""
    return list(
        dict.fromkeys(
            match.group(1).lower()
            for match in _lesson_selection.RECURRENCE_CLASS_RE.finditer(prompt)
        )
    )


def _lesson_texts_for_sources(
    repo_root: Path, replayed: Mapping[str, Mapping[str, Any]], lesson_ids: Sequence[str]
) -> dict[str, str]:
    """Read wording through the retro parser for ledger-validated source refs."""
    source_refs = sorted(
        {
            str(replayed[lesson_id]["source_retro"])
            for lesson_id in lesson_ids
        }
    )
    parsed, _ = _lesson_selection._parse_retro_artifacts(
        [repo_root / source_ref for source_ref in source_refs]
    )
    candidates = _lesson_selection._collect_lesson_candidates(repo_root, parsed)
    texts: dict[str, str] = {}
    for lesson_id in lesson_ids:
        source_ref = str(replayed[lesson_id]["source_retro"])
        candidate = candidates.get(("class", lesson_id))
        source = next(
            (
                entry
                for entry in (candidate or {}).get("sources", [])
                if entry.get("artifact_path") == source_ref
            ),
            None,
        )
        if source is None:
            raise ValueError(
                f"validated lesson `{lesson_id}` has no tagged wording in `{source_ref}`"
            )
        texts[lesson_id] = str(source["lesson"])
    return texts


def _render_lesson_injection(
    ledger_path: str,
    lesson_texts: Mapping[str, str],
    *,
    budget_bytes: int = LESSON_INJECTION_BUDGET_BYTES,
) -> tuple[str, list[str], list[str], int]:
    """Render declared lessons in order, enforcing a UTF-8 byte cap on the block."""
    header = (
        "[charness validated lesson injection]\n"
        f"Full ledger: {ledger_path}\n"
        f"Byte budget: {budget_bytes} UTF-8 bytes for this block.\n"
        "Match rule: declared recurrence-class slug equals validated lesson_id.\n"
    )
    accepted: list[str] = []
    excluded: list[str] = []
    rendered = header
    for lesson_id, lesson in lesson_texts.items():
        line = f"- {lesson_id}: {lesson}"
        lines = [f"- {item}: {lesson_texts[item]}" for item in accepted]
        lines.append(line)
        candidate = header + "\n".join(lines) + "\n"
        if len(candidate.encode("utf-8")) + 2 > budget_bytes:
            excluded.append(lesson_id)
            continue
        accepted.append(lesson_id)
        rendered = candidate
    if not lesson_texts:
        rendered += "No declared slugs matched a validated lesson.\n"
    used_bytes = len(rendered.encode("utf-8")) + 2
    if used_bytes > budget_bytes:
        raise ValueError("lesson injection block header exceeds its byte budget")
    return rendered, accepted, excluded, used_bytes


def _prepare_lesson_injection(
    repo_root: Path,
    prompt: str,
    *,
    budget_bytes: int = LESSON_INJECTION_BUDGET_BYTES,
) -> tuple[str, dict[str, Any]]:
    """Build the declared-class-only prompt block and its auditable receipt facts."""
    declared = _declared_recurrence_classes(prompt)
    result: dict[str, Any] = {
        "schema_version": LESSON_INJECTION_SCHEMA,
        "ledger_path": LESSON_LEDGER_RELATIVE_PATH,
        "declared_slugs": declared,
        "injected_ids": [],
        "unmatched_slugs": [],
        "budget_excluded_ids": [],
        "budget_bytes": budget_bytes,
        "used_bytes": 0,
        "error": None,
        "non_claim": LESSON_INJECTION_NON_CLAIM,
    }
    if not declared:
        return "", result

    output_dir = repo_root / "charness-artifacts" / "retro"
    path = _lesson_ledger.lesson_ledger_path(output_dir)
    try:
        ledger_payload = json.loads(path.read_text(encoding="utf-8"))
        replayed = _lesson_ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=ledger_payload,
        )
        matched = [lesson_id for lesson_id in declared if lesson_id in replayed]
        result["unmatched_slugs"] = [
            lesson_id for lesson_id in declared if lesson_id not in replayed
        ]
        lesson_texts = _lesson_texts_for_sources(repo_root, replayed, matched)
        block, injected, excluded, used_bytes = _render_lesson_injection(
            LESSON_LEDGER_RELATIVE_PATH, lesson_texts, budget_bytes=budget_bytes
        )
        result.update(
            {
                "injected_ids": injected,
                "budget_excluded_ids": excluded,
                "used_bytes": used_bytes,
            }
        )
        return block, result
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        block = (
            "[charness lesson injection unavailable]\n"
            f"Full ledger: {LESSON_LEDGER_RELATIVE_PATH}\n"
            "No lesson was injected because the ledger could not be validated.\n"
        )
        result["used_bytes"] = len(block.encode("utf-8")) + 2
        return block, result


def lesson_injection_unavailable(reason: str, declared: list[str]) -> dict[str, Any]:
    """Receipt facts when injection cannot run before prompt assembly."""
    return {
        "schema_version": LESSON_INJECTION_SCHEMA,
        "ledger_path": LESSON_LEDGER_RELATIVE_PATH,
        "declared_slugs": declared,
        "injected_ids": [],
        "unmatched_slugs": [],
        "budget_excluded_ids": [],
        "budget_bytes": LESSON_INJECTION_BUDGET_BYTES,
        "used_bytes": 0,
        "error": reason,
        "non_claim": LESSON_INJECTION_NON_CLAIM,
    }


def injection_result(value: object) -> dict[str, Any]:
    """Keep lesson facts in the WI-1 receipt without adding a verdict kind."""
    raw = value if isinstance(value, Mapping) else {}

    def string_list(key: str) -> list[str]:
        items = raw.get(key)
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, str)]

    result: dict[str, Any] = {
        "schema_version": LESSON_INJECTION_SCHEMA,
        "ledger_path": raw.get("ledger_path")
        if isinstance(raw.get("ledger_path"), str)
        else LESSON_LEDGER_RELATIVE_PATH,
        "declared_slugs": string_list("declared_slugs"),
        "injected_ids": string_list("injected_ids"),
        "unmatched_slugs": string_list("unmatched_slugs"),
        "budget_excluded_ids": string_list("budget_excluded_ids"),
        "budget_bytes": raw.get("budget_bytes"),
        "used_bytes": raw.get("used_bytes"),
        "prepared": isinstance(value, Mapping),
        "non_claim": LESSON_INJECTION_NON_CLAIM,
    }
    error = raw.get("error")
    if isinstance(error, str) and error:
        result["error"] = error
    return result

"""Lifecycle decisions for the consumer-owned quality adapter.

The generic generated-write planner only answers whether two payloads differ.
This module owns the quality adapter's stronger policy: a difference is a
conflict unless the caller explicitly authorizes migration, and migration must
carry comments forward instead of silently losing them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.adapter_lib import (  # noqa: E402
    _find_mapping_separator,
    inline_comment_start,
    load_yaml,
    plan_generated_write,
    strip_inline_comment,
)
from scripts.adapters.quality_bootstrap_render import render_bootstrap_adapter  # noqa: E402
from scripts.core.path_portability_lib import repo_relative  # noqa: E402


def _value_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def normalized_intent_matches(existing_text: str | None, rendered_text: str) -> bool:
    if existing_text is None:
        return False
    existing = load_yaml(existing_text)
    rendered = load_yaml(rendered_text)
    return isinstance(existing, dict) and isinstance(rendered, dict) and existing == rendered


def _reason_for_surface(surface: str, status: str | None, *, removed: bool = False) -> str:
    if removed:
        return "the generated adapter no longer carries this existing surface"
    return {
        "inferred": "bootstrap inferred this surface from repository evidence",
        "installed": "bootstrap detected an available repository command for this surface",
        "augmented": "bootstrap merged detected data into the existing surface",
        "preserved": "the rendered adapter differs from the existing surface despite its preserved status",
    }.get(status or "", f"bootstrap requested a change to this consumer-owned surface (status: {status or 'unknown'})")


def conflict_changes(
    existing_text: str | None,
    rendered_text: str,
    field_statuses: dict[str, str],
) -> list[dict[str, Any]]:
    """Describe semantic changes that are not default/deferred additions."""
    if existing_text is None:
        return []
    existing = load_yaml(existing_text)
    rendered = load_yaml(rendered_text)
    if not isinstance(existing, dict) or not isinstance(rendered, dict):
        return [
            {
                "surface": "adapter",
                "current_value": existing,
                "requested_value": rendered,
                "requested_change": "replace the existing adapter with the generated mapping",
                "reason": "the adapter could not be compared as a normalized mapping",
                "next_action": "repair or review the adapter, then rerun with --migrate to authorize a rewrite",
            }
        ]

    changes: list[dict[str, Any]] = []
    for surface, current_value in existing.items():
        if surface not in rendered:
            requested_value = None
            requested_change = f"remove `{surface}` from the generated adapter"
            reason = _reason_for_surface(surface, field_statuses.get(surface), removed=True)
        elif rendered[surface] != current_value:
            requested_value = rendered[surface]
            requested_change = f"replace `{surface}` with {_value_text(requested_value)}"
            reason = _reason_for_surface(surface, field_statuses.get(surface))
        else:
            continue
        changes.append(
            {
                "surface": surface,
                "current_value": current_value,
                "requested_value": requested_value,
                "requested_change": requested_change,
                "reason": reason,
                "next_action": (
                    f"review `{surface}`, then rerun with --migrate to authorize this rewrite, "
                    "or edit the adapter manually"
                ),
            }
        )

    for surface, requested_value in rendered.items():
        if surface in existing:
            continue
        status = field_statuses.get(surface)
        changes.append(
            {
                "surface": surface,
                "current_value": None,
                "requested_value": requested_value,
                "requested_change": f"add `{surface}` with {_value_text(requested_value)}",
                "reason": _reason_for_surface(surface, status),
                "next_action": (
                    f"review `{surface}`, then rerun with --migrate to authorize this rewrite, "
                    "or edit the adapter manually"
                ),
            }
        )
    return changes


def conflict_advisory(changes: list[dict[str, Any]]) -> str | None:
    if not changes:
        return None
    surfaces = ", ".join(f"`{change['surface']}`" for change in changes)
    details = "; ".join(
        f"{change['surface']}: {change['requested_change']} because {change['reason']}; "
        f"next action: {change['next_action']}"
        for change in changes
    )
    return (
        f"bootstrap preserved the existing adapter because requested changes affect {surfaces}. "
        f"{details}"
    )


def _comment_start(line: str) -> int | None:
    stripped = line.strip()
    indentation = len(line) - len(line.lstrip())
    value_start = 0
    if stripped.startswith("-"):
        value_start = 1
    else:
        separator = _find_mapping_separator(stripped)
        if separator >= 0:
            value_start = separator + 1
    while value_start < len(stripped) and stripped[value_start] in " \t":
        value_start += 1
    comment = inline_comment_start(stripped[value_start:])
    return None if comment is None else indentation + value_start + comment


def preserved_comment_fragments(existing_text: str | None) -> list[str]:
    if not existing_text:
        return []
    fragments: list[str] = []
    for line in existing_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            fragments.append(line.rstrip())
            continue
        start = _comment_start(line)
        if start is not None and strip_inline_comment(line).strip() != line.strip():
            fragments.append(line[start:].rstrip())
    return fragments


def preserve_comments(existing_text: str | None, rendered_text: str) -> tuple[str, int]:
    """Append existing comment text as a migration-owned comment block."""
    fragments = preserved_comment_fragments(existing_text)
    if not fragments:
        return rendered_text, 0
    retained = rendered_text.rstrip() + "\n\n# Preserved comments from the pre-migration adapter:\n"
    retained += "\n".join(fragments) + "\n"
    return retained, len(fragments)


def bootstrap_quality_adapter(
    *, repo_root: Path, output_path: Path, report_path: Path, dry_run: bool, migrate: bool = False
) -> dict[str, Any]:
    """Run the quality adapter lifecycle with an explicit migration boundary."""
    # Keep the state builder dependency local: the builder owns detection and merge
    # policy, while this module owns write authorization and migration behavior.
    from scripts.adapters.quality_bootstrap_lib import (
        BootstrapValidationError,
        build_bootstrap_state,
    )

    adapter_path = output_path if output_path.is_absolute() else repo_root / output_path
    resolved_report_path = report_path if report_path.is_absolute() else repo_root / report_path
    if adapter_path.resolve() == resolved_report_path.resolve():
        raise BootstrapValidationError(
            f"adapter output and report path resolve to the same file ({adapter_path}); "
            "choose distinct paths before rerunning bootstrap"
        )
    final_data, field_statuses, deferred_setup = build_bootstrap_state(repo_root)
    adapter_text = render_bootstrap_adapter(final_data, field_statuses)
    existing_text = adapter_path.read_text(encoding="utf-8") if adapter_path.is_file() else None

    # Decide what a real run WOULD do before branching on dry_run. A dry run that skips
    # the comparison cannot tell a would-be rewrite from a would-be no-op, so it warned
    # about destroying comments that a real run leaves untouched — a warning that cries
    # wolf on every plan is one an operator stops reading.
    plan = plan_generated_write(existing_text, adapter_text)
    if plan == "differs" and normalized_intent_matches(existing_text, adapter_text):
        plan = "unchanged"
    semantic_changes = conflict_changes(existing_text, adapter_text, field_statuses)
    if plan == "differs" and not semantic_changes:
        # The renderer may differ in a way the lightweight YAML normalizer cannot
        # describe. Preserve the same safety boundary: an unclassified difference is
        # still a conflict, never implicit authorization.
        semantic_changes = [
            {
                "surface": "adapter",
                "current_value": None,
                "requested_value": None,
                "requested_change": "replace the existing adapter with the generated adapter",
                "reason": "the generated adapter differs but no safe normalized surface match was found",
                "next_action": "review the adapter, then rerun with --migrate to authorize a rewrite",
            }
        ]
    would_do = {
        "absent": "written",
        "unchanged": "unchanged",
        "differs": "migrated" if migrate else "conflict",
    }[plan]

    if dry_run:
        adapter_status = "dry-run"
    else:
        adapter_status = would_do
        if would_do == "written":
            adapter_path.parent.mkdir(parents=True, exist_ok=True)
            adapter_path.write_text(adapter_text, encoding="utf-8")
        elif would_do == "migrated":
            migrated_text, comments_preserved = preserve_comments(existing_text, adapter_text)
            adapter_path.parent.mkdir(parents=True, exist_ok=True)
            adapter_path.write_text(migrated_text, encoding="utf-8")
        else:
            comments_preserved = 0

    if plan == "differs" and migrate:
        migrated_text, comments_preserved = preserve_comments(existing_text, adapter_text)
    else:
        comments_preserved = 0

    report = {
        "adapter_path": repo_relative(repo_root, adapter_path),
        "adapter_status": adapter_status,
        "artifact_path": str(Path(final_data["output_dir"]) / "latest.md"),
        "report_path": repo_relative(repo_root, resolved_report_path),
        "preset_lineage": final_data["preset_lineage"],
        "field_statuses": field_statuses,
        "deferred_setup": deferred_setup,
        "deliberately_absent": dict(final_data.get("deliberately_absent") or {}),
        "migration_requested": migrate,
    }
    if dry_run:
        report["would_do"] = would_do
    if plan == "differs":
        report["requested_changes"] = semantic_changes
        if migrate:
            report["migration_changes"] = semantic_changes
            report["comments_preserved"] = comments_preserved
        elif advisory := conflict_advisory(semantic_changes):
            report["customization_warning"] = advisory
    if absence_warnings := final_data.get("_absence_warnings"):
        report["absence_warnings"] = list(absence_warnings)
    if not dry_run:
        resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report

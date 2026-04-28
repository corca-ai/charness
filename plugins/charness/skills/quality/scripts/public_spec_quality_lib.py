from __future__ import annotations

from pathlib import Path
from typing import Any

IGNORED_PARTS = {".git", ".charness", "__pycache__", "node_modules", "plugins", "evals"}
REVIEW_PROMPTS = [
    "Keep public executable pages reader-facing: current claims first, internal structure second.",
    "Check whether source inventory or implementation pinning became the main proof surface.",
    "Audit proof layering, not only proof presence: duplicated happy paths at the wrong layer create maintenance drag.",
    "Delete repeated public-spec, smoke, or on-demand E2E proof once a narrower layer owns the claim honestly.",
]
SMOKE_KEEP = [
    "the smoke test proves a cross-command flow",
    "the smoke test mutates a repo or artifact boundary",
    "a narrower layer cannot own the seam honestly",
]
SMOKE_DELETE = [
    "the smoke test only repeats the same happy-path claim already owned by a public spec",
    "lower-layer tests already own the behavior and the smoke adds no repo-mutation value",
]
E2E_KEEP = [
    "the E2E path proves an external-consumer or environment-heavy seam",
    "the flow is too expensive or unstable for standing smoke or public-spec ownership",
]
E2E_DELETE = [
    "the E2E path only repeats a cheap happy-path contract already owned by a public spec or smoke test",
]


def visible_paths(repo_root: Path, pattern: str) -> list[Path]:
    return sorted(
        path for path in repo_root.rglob(pattern)
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.relative_to(repo_root).parts)
    )


def recommendation(
    action: str,
    scope: str,
    target: str,
    target_items: list[Any],
    *,
    guidance: str | None = None,
    keep_when: list[str] | None = None,
    delete_when: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "action": action,
        "scope": scope,
        "target": target,
        "target_items": target_items,
    }
    if guidance is not None:
        payload["guidance"] = guidance
    if keep_when is not None:
        payload["keep_when"] = keep_when
    if delete_when is not None:
        payload["delete_when"] = delete_when
    return payload


def source_guard_specs(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [spec for spec in specs if "source_inventory_pressure" in spec["heuristics"]]


def implementation_guard_specs(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [spec for spec in specs if "implementation_guard_pressure" in spec["heuristics"]]


def top_source_guard_specs(specs: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    return [
        {
            "spec_path": spec["spec_path"],
            "source_guard_row_count": spec["source_guard_row_count"],
            "source_guard_token_count": spec["source_guard_token_count"],
        }
        for spec in sorted(
            source_guard_specs(specs),
            key=lambda item: (
                item["source_guard_row_count"],
                item["source_guard_token_count"],
                item["spec_path"],
            ),
            reverse=True,
        )[:limit]
    ]


def source_guard_summary(specs: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "source_guard_row_count": sum(spec["source_guard_row_count"] for spec in specs),
        "source_guard_token_count": sum(spec["source_guard_token_count"] for spec in specs),
        "source_guard_pressure_spec_count": len(source_guard_specs(specs)),
        "implementation_guard_pressure_spec_count": len(implementation_guard_specs(specs)),
    }


def source_guard_recommendation(top_specs: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not top_specs:
        return None
    return recommendation(
        "classify_source_guards",
        "public-spec",
        "top_source_guard_specs",
        top_specs,
        guidance=(
            "Classify each high-pressure source guard as `replace_with_contract_check`, "
            "`move_to_unit_test`, `keep_as_reader_facing_contract`, or `delete_if_inventory_only`."
        ),
    )


def public_spec_recommendations(
    *,
    duplicates: list[dict[str, Any]],
    runner_specs: list[str],
    top_source_specs: list[dict[str, Any]],
    smoke_paths: list[str],
    e2e_paths: list[str],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if duplicates:
        items.append(recommendation("delete_or_merge", "public-spec", "duplicate_command_examples", duplicates, guidance="Keep one representative public-spec proof per happy-path command, then delete or merge repeated public-spec copies."))
    if runner_specs:
        items.append(recommendation("move_down", "public-spec", "delegated_runner_specs", runner_specs, guidance="Replace delegated test-runner proof with direct reader-facing command proof in the public spec, and keep detailed assertions in app, unit, or smoke layers."))
    guard_recommendation = source_guard_recommendation(top_source_specs)
    if guard_recommendation:
        items.append(guard_recommendation)
    if smoke_paths:
        items.append(recommendation("keep_if_integration_value", "smoke", "smoke_test_paths", smoke_paths, keep_when=SMOKE_KEEP, delete_when=SMOKE_DELETE))
    if e2e_paths:
        items.append(recommendation("keep_if_integration_value", "on-demand-e2e", "e2e_test_paths", e2e_paths, keep_when=E2E_KEEP, delete_when=E2E_DELETE))
    return items


def layering_heuristics(
    *,
    duplicates: list[dict[str, Any]],
    runner_specs: list[str],
    source_guard_spec_rows: list[dict[str, Any]],
    implementation_guard_spec_rows: list[dict[str, Any]],
    smoke_paths: list[str],
    e2e_paths: list[str],
) -> list[str]:
    heuristics: list[str] = []
    if duplicates:
        heuristics.append("duplicate_public_spec_examples")
    if runner_specs:
        heuristics.append("delegated_test_runner_inside_public_spec")
    if source_guard_spec_rows or implementation_guard_spec_rows:
        heuristics.append("source_guard_pressure_rollup")
    if (smoke_paths or e2e_paths) and (duplicates or runner_specs):
        heuristics.append("proof_layering_review_needed")
    return heuristics


def render_text_summary(payload: dict[str, Any]) -> list[str]:
    summary = payload["summary"]
    lines = [
        "source_guard_rollup: "
        f"rows={summary['source_guard_row_count']} "
        f"tokens={summary['source_guard_token_count']} "
        f"affected_specs={summary['source_guard_pressure_spec_count']}",
    ]
    for spec in payload["public_specs"]:
        heuristics = ", ".join(spec["heuristics"]) or "none"
        lines.append(f"{spec['spec_path']}: heuristics={heuristics}")
    top_specs = payload["layering"]["top_source_guard_specs"]
    if top_specs:
        lines.append("top_source_guard_specs:")
        lines.extend(
            f"- {spec['spec_path']}: rows={spec['source_guard_row_count']} "
            f"tokens={spec['source_guard_token_count']}"
            for spec in top_specs
        )
    lines.extend(
        f"recommendation: {item['action']} {item['target']}"
        for item in payload["layering"]["recommendations"]
        if item["action"] == "classify_source_guards"
    )
    if payload["layering"]["heuristics"]:
        lines.append(f"layering: {', '.join(payload['layering']['heuristics'])}")
    return lines

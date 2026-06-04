"""Validation helpers for agentic handoff chunk proposals."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parent / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            f"{module_name}.py not found beside chunked_routing_agentic_validation.py"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_types = _load_sibling("chunked_routing_types")
_policy = _load_sibling("chunked_routing_agentic_policy")
_facts = _load_sibling("chunked_routing_agentic_facts")
HandoffEntry = _types.HandoffEntry

DEFAULT_MAX_PACKAGE_SOURCES = _policy.DEFAULT_MAX_PACKAGE_SOURCES

_LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _as_int_list(value: Any, *, field: str, label: str, issues: list[str]) -> list[int]:
    if not isinstance(value, list):
        issues.append(f"{label}: `{field}` must be a list")
        return []
    out: list[int] = []
    for item in value:
        if not isinstance(item, int):
            issues.append(f"{label}: `{field}` contains non-integer {item!r}")
            continue
        out.append(item)
    return out


def _entry_by_id(entries: list[HandoffEntry] | tuple[HandoffEntry, ...]) -> dict[int, HandoffEntry]:
    return {entry.index: entry for entry in entries}


def _basis_tokens(entry_ids: list[int], by_id: dict[int, HandoffEntry]) -> set[str]:
    tokens: set[str] = set()
    for source_id in entry_ids:
        entry = by_id.get(source_id)
        if entry is not None:
            tokens.update(entry.boundary_tokens)
    return tokens


def _validate_chunk_shape(
    chunk: dict[str, Any],
    *,
    index: int,
    by_id: dict[int, HandoffEntry],
    max_sources: int,
    broad_tokens: set[str],
    allowed_broad: set[str],
    seen_labels: set[str],
    issues: list[str],
) -> list[int]:
    label = chunk.get("label")
    label_for_message = str(label or f"chunk {index}")
    if not isinstance(label, str) or not _LABEL_RE.match(label):
        issues.append(f"{label_for_message}: invalid label")
    elif label in seen_labels:
        issues.append(f"{label}: duplicate label")
    else:
        seen_labels.add(label)

    source_ids = _as_int_list(
        chunk.get("source_ids"),
        field="source_ids",
        label=label_for_message,
        issues=issues,
    )
    _validate_source_ids(
        source_ids,
        label=label_for_message,
        known_ids=set(by_id),
        max_sources=max_sources,
        issues=issues,
    )
    _validate_excluded_ids(chunk, source_ids, label_for_message, set(by_id), issues)
    _validate_required_text(chunk, label_for_message, issues)
    _validate_basis_tokens(
        chunk,
        source_ids,
        label=label_for_message,
        by_id=by_id,
        broad_tokens=broad_tokens,
        allowed_broad=allowed_broad,
        issues=issues,
    )
    return source_ids


def _validate_source_ids(
    source_ids: list[int],
    *,
    label: str,
    known_ids: set[int],
    max_sources: int,
    issues: list[str],
) -> None:
    if not source_ids:
        issues.append(f"{label}: empty source_ids")
    if len(source_ids) > max_sources:
        issues.append(
            f"{label}: source_ids length {len(source_ids)} exceeds max {max_sources}"
        )
    duplicate_inside = sorted({sid for sid in source_ids if source_ids.count(sid) > 1})
    if duplicate_inside:
        issues.append(f"{label}: duplicate source_ids {duplicate_inside}")
    unknown = sorted(set(source_ids) - known_ids)
    if unknown:
        issues.append(f"{label}: unknown source_ids {unknown}")


def _validate_excluded_ids(
    chunk: dict[str, Any],
    source_ids: list[int],
    label: str,
    known_ids: set[int],
    issues: list[str],
) -> None:
    excluded = _as_int_list(
        chunk.get("excluded_source_ids", []),
        field="excluded_source_ids",
        label=label,
        issues=issues,
    )
    unknown_excluded = sorted(set(excluded) - known_ids)
    if unknown_excluded:
        issues.append(f"{label}: unknown excluded_source_ids {unknown_excluded}")
    overlap_excluded = sorted(set(excluded) & set(source_ids))
    if overlap_excluded:
        issues.append(f"{label}: excluded_source_ids also included {overlap_excluded}")


def _validate_required_text(
    chunk: dict[str, Any], label: str, issues: list[str]
) -> None:
    for field in ("objective_summary", "rationale", "downstream_unlock"):
        value = chunk.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{label}: empty `{field}`")


def _validate_basis_tokens(
    chunk: dict[str, Any],
    source_ids: list[int],
    *,
    label: str,
    by_id: dict[int, HandoffEntry],
    broad_tokens: set[str],
    allowed_broad: set[str],
    issues: list[str],
) -> None:
    basis = chunk.get("basis_boundary_tokens", [])
    if not isinstance(basis, list) or not all(isinstance(token, str) for token in basis):
        issues.append(f"{label}: `basis_boundary_tokens` must be a string list")
        return
    basis_tokens = set(basis)
    unknown_basis = sorted(basis_tokens - _basis_tokens(source_ids, by_id))
    if unknown_basis:
        issues.append(f"{label}: unknown basis_boundary_tokens {unknown_basis}")
    broad_basis = (basis_tokens & broad_tokens) - allowed_broad
    if len(source_ids) > 1 and basis_tokens and basis_tokens <= broad_basis:
        issues.append(
            f"{label}: merge justified only by broad boundary tokens {sorted(basis_tokens)}"
        )


def validate_chunk_proposal_response(
    response: dict[str, Any],
    entries: list[HandoffEntry] | tuple[HandoffEntry, ...],
    *,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate an agent-filled package proposal response."""
    issues: list[str] = []
    effective_policy = policy or _policy.default_chunk_policy()
    by_id = _entry_by_id(entries)
    max_sources = int(
        effective_policy.get("max_package_sources", DEFAULT_MAX_PACKAGE_SOURCES)
    )
    broad_tokens = set(effective_policy.get("broad_boundary_tokens", ()))
    allowed_broad = set(effective_policy.get("allowed_broad_boundary_tokens", ()))

    chunks = response.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        return {"ok": False, "issues": ["missing or empty `chunks` list"]}

    seen_labels: set[str] = set()
    seen_sources: list[int] = []
    merge_policy_facts: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks, start=1):
        if not isinstance(chunk, dict):
            issues.append(f"chunk {index}: must be an object")
            continue
        source_ids = _validate_chunk_shape(
            chunk,
            index=index,
            by_id=by_id,
            max_sources=max_sources,
            broad_tokens=broad_tokens,
            allowed_broad=allowed_broad,
            seen_labels=seen_labels,
            issues=issues,
        )
        seen_sources.extend(source_ids)
        merge_policy_facts.append(
            _facts.merge_policy_fact(
                label=str(chunk.get("label") or f"chunk {index}"),
                source_ids=source_ids,
                basis=chunk.get("basis_boundary_tokens", []),
                valid_basis=_basis_tokens(source_ids, by_id),
                broad_tokens=broad_tokens,
                allowed_broad=allowed_broad,
            )
        )

    duplicate_across = sorted({sid for sid in seen_sources if seen_sources.count(sid) > 1})
    if duplicate_across:
        issues.append(f"duplicate source_ids across chunks {duplicate_across}")
    missing = sorted(set(by_id) - set(seen_sources))
    if missing:
        issues.append(f"missing source_ids {missing}")
    return {"ok": not issues, "issues": issues, "merge_policy_facts": merge_policy_facts}

"""Agentic work-package proposal support for handoff chunked routing.

The deterministic parser owns source identity. This module lets an agent propose
coherent work packages from those sources, then validates that no source was
invented, duplicated, dropped, over-bundled, or justified only by broad labels.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parent / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside chunked_routing_agentic.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_types = _load_sibling("chunked_routing_types")
_policy = _load_sibling("chunked_routing_agentic_policy")
_validation = _load_sibling("chunked_routing_agentic_validation")
HandoffEntry = _types.HandoffEntry
ChunkCandidate = _types.ChunkCandidate
MergeProposal = _types.MergeProposal

CHUNK_PROPOSAL_PACKET_VERSION = _policy.CHUNK_PROPOSAL_PACKET_VERSION
DEFAULT_MAX_PACKAGE_SOURCES = _policy.DEFAULT_MAX_PACKAGE_SOURCES
DEFAULT_BROAD_BOUNDARY_TOKENS = _policy.DEFAULT_BROAD_BOUNDARY_TOKENS
JUDGMENT_SUMMARY_FIELDS = _policy.JUDGMENT_SUMMARY_FIELDS
CHUNK_PROPOSER_PROMPT = _policy.CHUNK_PROPOSER_PROMPT

CHUNK_PROPOSAL_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["chunks"],
    "properties": {
        "chunks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "label",
                    "source_ids",
                    "objective_summary",
                    "rationale",
                    "downstream_unlock",
                    "judgment_summary",
                ],
                "properties": {
                    "label": {"type": "string", "minLength": 1},
                    "source_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "minItems": 1,
                    },
                    "objective_summary": {"type": "string", "minLength": 1},
                    "rationale": {"type": "string", "minLength": 1},
                    "downstream_unlock": {"type": "string", "minLength": 1},
                    "judgment_summary": {
                        "type": "object",
                        "required": list(JUDGMENT_SUMMARY_FIELDS),
                        "properties": {
                            field: {"type": "string", "minLength": 1}
                            for field in JUDGMENT_SUMMARY_FIELDS
                        },
                    },
                    "excluded_source_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                    },
                    "basis_boundary_tokens": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        }
    },
}

default_chunk_policy = _policy.default_chunk_policy
load_chunk_policy_config = _policy.load_chunk_policy_config
validate_chunk_proposal_response = _validation.validate_chunk_proposal_response


def _source_record(entry: HandoffEntry) -> dict[str, Any]:
    return {
        "source_id": entry.index,
        "title": entry.title,
        "body": entry.body,
        "referenced_paths": list(entry.referenced_paths),
        "referenced_issues": list(entry.referenced_issues),
        "referenced_skills": list(entry.referenced_skills),
        "boundary_tokens": list(entry.boundary_tokens),
    }


def _merge_hints(merge_proposal: MergeProposal | None) -> list[dict[str, Any]]:
    if merge_proposal is None:
        return []
    hints: list[dict[str, Any]] = []
    for candidate in merge_proposal.merged:
        hints.append(
            {
                "label": candidate.label,
                "source_ids": [entry.index for entry in candidate.entries],
                "objective_summary": candidate.objective_summary,
                "reason": merge_proposal.shared_boundary_reason.get(candidate.label, ""),
            }
        )
    return hints


def build_chunk_proposal_packet(
    entries: list[HandoffEntry] | tuple[HandoffEntry, ...],
    *,
    merge_proposal: MergeProposal | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the packet an agent fills with work-package proposals."""
    effective_policy = policy or default_chunk_policy()
    return {
        "version": CHUNK_PROPOSAL_PACKET_VERSION,
        "sources": [_source_record(entry) for entry in entries],
        "merge_hints": _merge_hints(merge_proposal),
        "policy": {
            "max_package_sources": int(
                effective_policy.get("max_package_sources", DEFAULT_MAX_PACKAGE_SOURCES)
            ),
            "broad_boundary_tokens": list(
                effective_policy.get("broad_boundary_tokens", ())
            ),
            "allowed_broad_boundary_tokens": list(
                effective_policy.get("allowed_broad_boundary_tokens", ())
            ),
        },
        "merge_decision_contract": {
            "script_role": "facts-only",
            "no_clearance_fields": ["safe_to_merge", "merge_ok"],
            "required_agent_judgment": list(JUDGMENT_SUMMARY_FIELDS),
            "broad_only_overlap_false_means": "policy emitted no broad-only warning; agent still judges semantic fit, implementation boundary, closeout flow, and operator value",
            "unknown_tokens_mean": "policy has no opinion",
        },
        "chunk_proposer_prompt": CHUNK_PROPOSER_PROMPT,
        "response_schema": CHUNK_PROPOSAL_RESPONSE_SCHEMA,
    }


def materialize_chunk_proposal_response(
    response: dict[str, Any],
    entries: list[HandoffEntry] | tuple[HandoffEntry, ...],
) -> MergeProposal:
    """Convert a validated proposal response into ChunkCandidate records."""
    by_id = {entry.index: entry for entry in entries}
    standalone: list[ChunkCandidate] = []
    merged: list[ChunkCandidate] = []
    reasons: dict[str, str] = {}
    for chunk in response.get("chunks", []):
        source_ids = [int(source_id) for source_id in chunk["source_ids"]]
        member_entries = tuple(by_id[source_id] for source_id in source_ids)
        candidate = ChunkCandidate(
            entries=member_entries,
            label=str(chunk["label"]),
            objective_summary=str(chunk["objective_summary"]).strip(),
            judgment_summary=_normalize_judgment_summary(chunk["judgment_summary"]),
        )
        if len(member_entries) == 1:
            standalone.append(candidate)
        else:
            merged.append(candidate)
        reasons[candidate.label] = (
            f"agentic rationale: {str(chunk['rationale']).strip()} "
            f"downstream unlock: {str(chunk['downstream_unlock']).strip()} "
            f"judgment: {_format_judgment_summary(chunk['judgment_summary'])}"
        )
    return MergeProposal(
        standalone=tuple(standalone),
        merged=tuple(merged),
        shared_boundary_reason=reasons,
    )


def _normalize_judgment_summary(summary: dict[str, Any]) -> dict[str, str]:
    return {
        field: str(summary[field]).strip()
        for field in JUDGMENT_SUMMARY_FIELDS
    }


def _format_judgment_summary(summary: dict[str, Any]) -> str:
    return "; ".join(
        f"{field.replace('_', ' ')}: {str(summary[field]).strip()}"
        for field in JUDGMENT_SUMMARY_FIELDS
    )

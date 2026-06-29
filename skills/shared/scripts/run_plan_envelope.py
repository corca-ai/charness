#!/usr/bin/env python3
"""Canonical run-plan envelope shared by every charness skill planner.

North star (spec 2026-06-29-skill-planner-uniformity): a well-formed skill
encodes HOW TO USE IT in a deterministic planner surface, and every planner
speaks ONE protocol so an agent (and plugin user) learns a single shape, not 20
bespoke bootstraps. The minimal common vocabulary is three keys:

- ``required_reads`` — list of ``read()`` items the run must open before broad work
- ``next_action``    — a single ``next_action()`` dict (always carries ``kind``)
- ``gate_packets``   — list of ``gate_packet()`` deterministic evidence packets

Every planner also stamps ``schema_version`` (its own per-skill dialect) and the
shared ``envelope_version`` conformance marker. Skill-specific fields
(``adapter``, ``artifact``, ``mode``, ``on_demand_reads``, ``phase_barriers``,
``lens_brief``, ...) stay as extensions on the same envelope — the envelope
unifies the shared vocabulary without flattening real per-skill structure.

Loading (the uniform planner snippet, mirrors the existing
``SimpleNamespace(**runpy.run_path(...))`` bootstrap idiom)::

    from pathlib import Path
    from types import SimpleNamespace
    import runpy

    ENVELOPE = SimpleNamespace(
        **runpy.run_path(
            str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py")
        )
    )

For a planner at ``.../skills/<skill>/scripts/<planner>.py``,
``Path(__file__).resolve().parents[3]`` resolves to the skills container root in
both the source tree (``skills/`` -> ``skills/shared/scripts``) and the exported
plugin mirror (``plugins/<pkg>/`` -> ``plugins/<pkg>/shared/scripts``) — the
same portable relative-path scheme gather uses (as ``SCRIPT_DIR.parents[2]``) to
reach ``support/web-fetch``.
"""

from __future__ import annotations

from typing import Any

ENVELOPE_VERSION = "charness.run_plan_envelope.v1"

# floor-addition-restraint: REQUIRED_ENVELOPE_KEYS + validate_envelope are NOT a
# new closeout/commit floor or an authoring field a human satisfies by hand. They
# are a shared correctness assertion on planner *output* that REPLACES seven
# bespoke ad hoc plan shapes with one auto-stamped shape — it lowers contract
# weight, not raises it. The detector's REQUIRED_* heuristic is a false positive
# here; recorded per docs/conventions/implementation-discipline.md.
REQUIRED_ENVELOPE_KEYS = (
    "schema_version",
    "envelope_version",
    "required_reads",
    "next_action",
    "gate_packets",
)
GATE_PACKET_CORE_KEYS = ("id", "trust_model", "cost_tier")


class EnvelopeError(ValueError):
    """Raised when a planner emits a payload that breaks the canonical envelope."""


def read(
    path: str,
    why: str,
    *,
    kind: str | None = None,
    base: str | None = None,
    trigger: str | None = None,
    role: str | None = None,
) -> dict[str, str]:
    """Build a canonical ``required_reads`` / ``on_demand_reads`` item.

    ``path`` and ``why`` are always present; ``kind``/``base`` (the
    debug/handoff/retro vocabulary), ``trigger`` (gather/issue), and ``role``
    (issue/quality) are optional extensions, emitted only when supplied so each
    skill keeps the exact item shape it needs without inventing empty fields.
    """
    item: dict[str, str] = {"path": path, "why": why}
    if kind is not None:
        item["kind"] = kind
    if base is not None:
        item["base"] = base
    if trigger is not None:
        item["trigger"] = trigger
    if role is not None:
        item["role"] = role
    return item


def gate_packet(
    packet_id: str,
    trust_model: str,
    *,
    cost_tier: str = "cheap",
    **extra: Any,
) -> dict[str, Any]:
    """Build a canonical ``gate_packets`` evidence packet.

    Core keys are ``id``/``trust_model``/``cost_tier``; everything a skill adds
    (``status``, ``command``, ``available``, ``path``, ``parallel_group``,
    ``run_when``, ``purpose``, ...) rides as an extension.
    """
    return {"id": packet_id, "trust_model": trust_model, "cost_tier": cost_tier, **extra}


def next_action(kind: str, **extra: Any) -> dict[str, Any]:
    """Build the canonical single ``next_action``.

    Always a dict carrying ``kind``; ``command``/``instruction``/``reason``/
    ``why``/``redirect``/artifact pointers ride as extensions.
    """
    return {"kind": kind, **extra}


def adapter_echo(adapter: dict[str, Any]) -> dict[str, Any]:
    """Canonical full adapter-state echo for an envelope's ``adapter`` field.

    The valid/found/path/output_dir/warnings/errors summary that the full-state
    planners (debug, retro) surface verbatim. Planners that need a reduced or
    differently-typed echo (release omits output_dir, handoff uses bool casts) build
    their own dict — this is the shared FULL shape only. Lives here because every
    planner already hard-depends on this module (loaded by relative path), so
    sharing it adds no coupling that portability did not already carry.
    """
    return {
        "valid": adapter.get("valid"),
        "found": adapter.get("found"),
        "path": adapter.get("path"),
        "output_dir": str(adapter["data"]["output_dir"]),
        "warnings": adapter.get("warnings", []),
        "errors": adapter.get("errors", []),
    }


def build_envelope(
    *,
    schema_version: str,
    required_reads: list[dict[str, Any]],
    next_action: dict[str, Any],
    gate_packets: list[dict[str, Any]],
    **extensions: Any,
) -> dict[str, Any]:
    """Assemble + validate a canonical run-plan envelope.

    Stamps ``envelope_version`` and returns the merged payload. Skill-specific
    keys flow through ``extensions`` unchanged. Raises ``EnvelopeError`` if the
    result is not canonical, so a planner that drifts fails in its own code
    (a correctness check on planner output) rather than shipping a malformed
    plan to the agent.

    floor-addition-restraint: this validator is NOT a new closeout/commit floor
    or a new authoring field an operator must satisfy by hand. It is a shared
    correctness assertion on planner *output* (a type-check) that REPLACES seven
    bespoke ad hoc shapes with one — it lowers, not raises, contract weight.
    """
    envelope: dict[str, Any] = {
        "schema_version": schema_version,
        "envelope_version": ENVELOPE_VERSION,
        "required_reads": required_reads,
        "next_action": next_action,
        "gate_packets": gate_packets,
        **extensions,
    }
    validate_envelope(envelope)
    return envelope


def build_linear_envelope(
    *,
    schema_version: str,
    required_reads: list[dict[str, Any]],
    next_action_kind: str,
    next_action_reason: str | None = None,
    gate_packets: list[dict[str, Any]] | None = None,
    **extensions: Any,
) -> dict[str, Any]:
    """Minimal emitter for a linear skill (no real branching briefing decision).

    A linear skill ships ``required_reads`` plus a single fixed ``next_action``
    and no fabricated mode/branch fields (Floor-Addition Restraint: do not
    cargo-cult branches a skill does not have). ``gate_packets`` defaults to an
    empty list when the skill has no deterministic evidence packet yet.
    """
    action = next_action(next_action_kind, **({"reason": next_action_reason} if next_action_reason else {}))
    return build_envelope(
        schema_version=schema_version,
        required_reads=required_reads,
        next_action=action,
        gate_packets=list(gate_packets or []),
        **extensions,
    )


def _validate_reads(required_reads: Any) -> None:
    if not isinstance(required_reads, list):
        raise EnvelopeError("required_reads must be a list")
    for index, item in enumerate(required_reads):
        if not isinstance(item, dict):
            raise EnvelopeError(f"required_reads[{index}] must be a dict")
        for key in ("path", "why"):
            if not isinstance(item.get(key), str) or not item[key]:
                raise EnvelopeError(f"required_reads[{index}] missing non-empty {key!r}")


def _validate_gate_packets(gate_packets: Any) -> None:
    if not isinstance(gate_packets, list):
        raise EnvelopeError("gate_packets must be a list")
    for index, packet in enumerate(gate_packets):
        if not isinstance(packet, dict):
            raise EnvelopeError(f"gate_packets[{index}] must be a dict")
        for key in GATE_PACKET_CORE_KEYS:
            if not isinstance(packet.get(key), str) or not packet[key]:
                raise EnvelopeError(f"gate_packets[{index}] missing non-empty {key!r}")


def validate_envelope(envelope: Any) -> None:
    """Raise ``EnvelopeError`` unless ``envelope`` is a canonical run plan."""
    if not isinstance(envelope, dict):
        raise EnvelopeError("envelope must be a dict")
    for key in REQUIRED_ENVELOPE_KEYS:
        if key not in envelope:
            raise EnvelopeError(f"envelope missing required key {key!r}")
    if not isinstance(envelope["schema_version"], str) or not envelope["schema_version"]:
        raise EnvelopeError("schema_version must be a non-empty string")
    if envelope["envelope_version"] != ENVELOPE_VERSION:
        raise EnvelopeError(
            f"envelope_version must be {ENVELOPE_VERSION!r}, got {envelope['envelope_version']!r}"
        )
    action = envelope["next_action"]
    if not isinstance(action, dict) or not isinstance(action.get("kind"), str) or not action["kind"]:
        raise EnvelopeError("next_action must be a dict carrying a non-empty string 'kind'")
    _validate_reads(envelope["required_reads"])
    _validate_gate_packets(envelope["gate_packets"])

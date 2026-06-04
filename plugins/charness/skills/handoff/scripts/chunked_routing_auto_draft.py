"""Auto-draft writer for chunked-routing output.

Renders the body of a goal artifact from a selected ``ChunkCandidate``
so the handoff -> achieve handoff has a deterministic scaffold. The
placeholder strings here are the empty-section sentinels that the
achieve Before-phase interview fills in.
"""
import importlib.util
import re
from pathlib import Path


def _load_sibling_types():
    spec = importlib.util.spec_from_file_location(
        "chunked_routing_types",
        Path(__file__).resolve().parent / "chunked_routing_types.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            "chunked_routing_types.py not found beside chunked_routing_auto_draft.py"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_types = _load_sibling_types()
ChunkCandidate = _types.ChunkCandidate


USER_ACCEPTANCE_PLACEHOLDER = (
    "*To be filled by the achieve Before-phase interview.*"
)
AGENT_VERIFICATION_PLACEHOLDER = (
    "*To be filled by the achieve Before-phase interview.*"
)
INTERVIEW_DECISIONS_PLACEHOLDER = (
    "*To be filled by the achieve Before-phase interview.*"
)
PLAN_CRITIQUE_PLACEHOLDER = (
    "*To be filled by the achieve plan-critique pass.*"
)

_AUTODRAFT_TEMPLATE = """# Achieve Goal: {title}

Status: draft
Created: {date}
Activation: `/goal @{goal_rel}`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before shaping.
- Next action: run `/achieve @{goal_rel}` to fill the Before-phase placeholders;
  activate only after pursue-readiness passes.
- Verification cadence: to be filled by the achieve Before-phase interview.
- Slice review packet: to be filled by the achieve Before-phase interview.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Final Verification`, and
  `## Auto-Retro`.

## Goal

{goal_body}

## Non-Goals

{non_goals}

## Boundaries

{boundaries}

## User Acceptance

{user_acceptance}

## Agent Verification Plan

{agent_verification}

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Slice Log

## Context Sources

{context_sources}

## Interview Decisions

{interview_decisions}

## Plan Critique Findings

{plan_critique}

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
"""


def _objective_from_chunk(chunk: ChunkCandidate) -> str:
    """Return the one-line objective summary passed as `title`.

    The goal_artifact template at
    ``skills/public/achieve/scripts/goal_artifact_lib.py`` already wraps
    ``{title}`` in ``# Achieve Goal: {title}``. The auto-draft writer
    therefore passes only the objective text, never the literal
    ``Achieve Goal:`` prefix — slice 1 critique finding 1.
    """
    return chunk.objective_summary.strip()


def _quote_entry_body(body: str) -> str:
    """Blockquote a handoff entry's body.

    No marker scrub is needed: the trivial-goal exemption was removed from
    ``goal_artifact_lib``, so the portability gate no longer special-cases any
    ``single-slice goal`` phrase. Quoted handoff prose is safe verbatim.
    """
    return "\n".join(f"> {line}" if line else ">" for line in body.splitlines())


def _render_goal_body(chunk: ChunkCandidate) -> str:
    """Two paragraphs: objective summary + the source handoff entry.

    For merged bundles, each source entry is rendered with its own
    `**Source…**` header and the entries are separated by a `---`
    divider (slice-5 critique bundle-anyway 2).
    """
    objective = _objective_from_chunk(chunk)
    entries = chunk.entries
    sources = []
    for entry in entries:
        sources.append(
            f"**Source handoff entry #{entry.index}: {entry.title}**\n\n"
            f"{_quote_entry_body(entry.body)}"
        )
    separator = "\n\n---\n\n" if len(sources) > 1 else "\n\n"
    return f"{objective}\n\n{separator.join(sources)}"


def _render_non_goals(chunk: ChunkCandidate) -> str:
    """Two default Non-Goals seeded into every auto-drafted artifact."""
    lines = [
        "- Not a release: no plugin version bump expected.",
        "- Do not absorb adjacent handoff entries beyond the selected chunk.",
    ]
    return "\n".join(lines)


def _render_boundaries(chunk: ChunkCandidate) -> str:
    """Boundaries seeded with the in-scope paths + portability invariant."""
    in_scope_paths = sorted(
        {path for entry in chunk.entries for path in entry.referenced_paths}
    )
    if in_scope_paths:
        in_scope = "- In scope: " + ", ".join(f"`{path}`" for path in in_scope_paths)
    else:
        in_scope = (
            "- In scope: paths to be named during the achieve Before-phase "
            "(the source handoff entry referenced no explicit paths)."
        )
    lines = [
        in_scope,
        "- Portable per implementation-discipline: no host-specific assumption.",
        "- Stop conditions: name on first discovery; do not guess.",
    ]
    return "\n".join(lines)


def _render_context_sources(chunk: ChunkCandidate) -> str:
    """Context Sources seeded with the source handoff entry + cited paths.

    Bullet-list only (no intro line) so the standard goal-artifact
    convention is preserved — slice-5 critique bundle-anyway 1.
    """
    lines: list[str] = []
    for entry in chunk.entries:
        lines.append(
            f"- Source: handoff entry #{entry.index} ({entry.title}) — "
            "see [docs/handoff.md](../../docs/handoff.md)."
        )
    cited = sorted(
        {path for entry in chunk.entries for path in entry.referenced_paths}
    )
    for path in cited:
        lines.append(f"- Cited path: `{path}`")
    issues = sorted(
        {issue for entry in chunk.entries for issue in entry.referenced_issues}
    )
    for issue in issues:
        lines.append(f"- Cited issue: #{issue}")
    return "\n".join(lines)


def auto_draft_slug(chunk: ChunkCandidate) -> str:
    """Derive a stable goal slug from the chunk.

    Issue-bearing chunks get an `issue-NNN` prefix; the title's first
    few alphanumeric words follow.
    """
    issues = sorted(
        {issue for entry in chunk.entries for issue in entry.referenced_issues}
    )
    raw = _objective_from_chunk(chunk)
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")[:60]
    if issues:
        return f"issue-{'-'.join(str(i) for i in issues)}-{slug}".strip("-")
    return slug or "auto-draft"


def render_auto_draft_artifact(
    chunk: ChunkCandidate, *, date: str, goal_rel: str
) -> str:
    """Render the auto-drafted goal artifact body.

    ``goal_rel`` is the repo-relative path to the artifact (used in the
    Activation line). The caller is responsible for writing the body to
    that path; this function is pure rendering.

    Source-chunk text is rendered verbatim: the trivial-goal
    exemption from ``goal_artifact_lib``, so there is no longer a marker
    phrase a quoted handoff entry could use to neuter the portability gate.
    """
    return _AUTODRAFT_TEMPLATE.format(
        title=_objective_from_chunk(chunk),
        date=date,
        goal_rel=goal_rel,
        goal_body=_render_goal_body(chunk),
        non_goals=_render_non_goals(chunk),
        boundaries=_render_boundaries(chunk),
        user_acceptance=USER_ACCEPTANCE_PLACEHOLDER,
        agent_verification=AGENT_VERIFICATION_PLACEHOLDER,
        context_sources=_render_context_sources(chunk),
        interview_decisions=INTERVIEW_DECISIONS_PLACEHOLDER,
        plan_critique=PLAN_CRITIQUE_PLACEHOLDER,
    )

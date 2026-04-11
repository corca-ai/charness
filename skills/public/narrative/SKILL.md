---
name: narrative
description: "Use when a repo's source-of-truth docs, current product or project story, and stakeholder-facing brief need to be aligned together. Tighten the durable narrative first, then derive a self-contained brief when an audience needs one."
---

# Narrative

Use this when the repo already has a product, project, or operating story, but
that story needs to be created, realigned, or compressed into a human-facing
brief without leaving the durable docs behind.

`narrative` is one public concept:

- map the current source-of-truth surface
- surface contradictions, stale assumptions, and missing decisions
- rewrite the durable docs so the current story is honest in one place
- derive an audience-facing brief from that aligned story when useful

If the idea is still under-shaped, use `ideation` first. If the docs are
already aligned and the user only wants delivery-ready wording, use
`announcement`.
If the repo has little or no durable truth surface yet, use `init-repo` to
bootstrap that surface before treating the task as narrative alignment.

## Bootstrap

Resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Default durable artifact:

- `skill-outputs/narrative/narrative.md`

If the repo would benefit from an explicit truth surface, scaffold an adapter:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

Then inspect current state:

```bash
sed -n '1,220p' skill-outputs/narrative/narrative.md 2>/dev/null || true
python3 "$SKILL_DIR/scripts/map_sources.py" --repo-root .
git status --short
```

## Workflow

1. Restate the narrative goal.
   - bootstrap a new durable story surface
   - realign stale source-of-truth docs
   - realign docs and also produce an audience-facing brief
2. Map the current truth surface.
   - read the source documents before inventing a fresh summary
   - check whether local context may be stale relative to git remote state
   - if freshness is ambiguous and the repo cannot be trusted as-is, surface
     that risk before editing
   - if the source map is effectively empty or only placeholder-level, stop and
     recommend `init-repo` rather than pretending there is already a narrative
     surface to align
3. Tighten the durable story first.
   - rewrite contradictions instead of layering parallel narratives
   - propagate user-confirmed direction changes into source-of-truth docs, not
     only into the brief
   - keep README, roadmap, handoff, operator docs, and adjacent maintainer docs
     consistent enough that the next session does not inherit drift
4. Derive the brief second.
   - external or mixed audiences: self-contained by default
   - internal audiences: pointers are allowed when they reduce repetition and
     the reader is likely to open the repo
   - keep audience, language, and ephemerality explicit when they affect the
     artifact shape
5. Show the aligned edits and the brief draft before any delivery action.
6. Hand off to `announcement` only when the user explicitly wants human-facing
   backend delivery after the narrative itself is aligned.

## Output Shape

The result should usually include:

- `Source Map`
- `Narrative Drift`
- `Updated Truth`
- `Brief`
- `Open Questions`
- `Next Step`

## Guardrails

- Do not use `narrative` as a substitute for `ideation` when the concept is
  still vague or upstream decisions are genuinely unresolved.
- Do not leave user-confirmed direction changes only in an ephemeral brief.
- Do not treat a stale handoff as the sole truth surface when git freshness
  suggests the repo may have moved.
- Do not collapse durable truth docs and audience-specific briefs into one file
  when their lifecycles differ.
- Do not re-ask audience, language, channel, or ephemerality values the user
  already fixed in the session.
- For external or mixed audiences, do not rely on repo-internal paths, decision
  numbers, or stage labels unless they are explained inline.
- If delivery backend execution is the only remaining task, prefer
  `announcement` rather than growing `narrative` into a transport skill.

## References

- `references/adapter-contract.md`
- `references/source-map.md`
- `references/brief-shape.md`
- `scripts/map_sources.py`

---
name: handoff
description: "Use when the user wants the next session prepared or asks to update a handoff artifact. Keep the handoff short, current, and operationally useful, and treat mention-only pickup as an instruction to continue the workflow named in the handoff trigger."
---

# Handoff

Use this when the goal is to let the next operator continue without re-deriving
the session state.

The handoff should describe the exact next pickup path, not preserve a diary of
everything that happened.
Keep Christopher Alexander-style sequence discipline in the baton pass: record
the next move in the order it should unfold, not in the order this session
happened. See `references/continuation-sequence.md` when several plausible
pickups exist.

## Bootstrap

Resolve the adapter first, then start from the current handoff artifact and live
repo state.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

By default, `handoff` writes its durable artifact to
`<repo-root>/docs/handoff.md`. Repos can override the directory with
`<repo-root>/.agents/handoff-adapter.yaml`.

Keep the handoff inside the repo-owned size and shape gate. Default to a
signal target of 30-60 lines and treat 70 lines as the usual hard stop unless
the repo names a different gate. If the current handoff approaches that range,
preserve only information that changes the next action and spill durable detail
before appending more prose. Multiple dated `## This Session (<date>)` sections
are a hard diary smell. See `references/spill-targets.md` for the default spill
destinations. Assume a competent next operator can follow one good link and
infer stable repo defaults; do not restate those defaults just to feel safe.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. current handoff and adjacent plan or roadmap context
sed -n '1,220p' <resolved-handoff-artifact> 2>/dev/null || true
wc -l <resolved-handoff-artifact> 2>/dev/null || true
if test -f <resolved-handoff-artifact>; then rg -n "^## This Session \\(" <resolved-handoff-artifact>; fi
rg -n "Session|Goal|Deliverables|Exit criteria|Next Session|Discuss" docs charness-artifacts .agents

# 2. current repo state
git status --short
git log --oneline -5

# 3. current skill surfaces that change the next step
rg --files skills/public docs
```

If the user referenced the handoff to resume work rather than refresh it, read
the `Workflow Trigger` first and continue with that workflow.

## Workflow

1. Chunked routing (conditional). When the user mentions the handoff
   doc/skill with no explicit task directive, invoke the chunker
   pipeline before refresh-vs-pickup classification. See
   `references/chunked-routing.md` for the deterministic trigger rule,
   pipeline, and auto-draft handoff into `/achieve`.
2. Determine whether this is pickup or refresh.
   - for pickup, treat the workflow trigger as authoritative next-step
     instruction
   - for refresh, inspect only the live state that changes the next action
   - if the current handoff exceeds the size gate or stacks dated
     `This Session` sections, prune or spill before adding new prose
3. Identify the canonical handoff artifact.
   - default to the adapter-resolved artifact path
   - if the repo already has a checked-in handoff surface, point the adapter
     there instead of hardcoding the host choice into the skill
4. Rewrite the handoff around continuation, not history.
   - exact workflow trigger
   - current state facts that change the next action
   - ordered next actions
   - open decisions that still need user input
   - tight reference list
   - one reference to the owning artifact for metrics, history, or proof detail
     instead of replaying that detail inline
   - if the handoff carries a standing invariant, recurring workflow rule, or
     future-regression guard, promote it to the owning contract, reference, or
     validator surface and leave only a short pickup pointer
   - leave always-loaded host instruction surfaces out of `References` by
     default; include them only when omitting them would realistically change
     the first action
   - when the next action depends on an external originating context, carry
     canonical source identity (URL, gathered-artifact path, access mode,
     freshness) per `../../shared/references/closeout-discipline.md` so the
     next session does not rediscover the source
5. Keep the trigger explicit.
   - if a named workflow or skill should run next, say it directly
   - if the next pickup depends on reading specific files first, name them
6. Run a bounded misunderstanding critique when the handoff changed materially.
   - call `critique` for material workflow or ownership changes
   - focuses: wrong next action, workflow trigger ambiguity, ownership/boundary
     misread, and examples that could be over-literalized
   - use `../../shared/references/fresh-eye-subagent-review.md` before reporting
     the reviewer path as blocked
   - incorporate only concrete clarity fixes, not speculative churn
7. Finish with a clean baton pass.
   - the next operator should know what to do first without interpretation

## Output Shape

The handoff should usually contain:

- `Workflow Trigger`
- `Current State`
- `Next Session`
- `Discuss`
- `References`

## Guardrails

- Do not preserve stale detail that no longer changes the next action.
- Do not copy quality, retro, debug, changelog, or commit-history detail into
  the handoff when a link to the owning artifact is enough.
- Do not accumulate dated `This Session (<date>)` sections across sessions;
  replace the old one or spill durable detail into the right sibling artifact.
- Do not hide the real next workflow behind vague prose.
- Do not write unverified state as fact.
- Do not let the handoff drift away from the current repo state.
- Do not add new top-level sections just to preserve history; prune or move the
  durable detail instead.
- Do not use the line budget as permission to keep process narrative; the
  budget is a failure guard, not a target.
- Do not restate stable repo defaults, release numbers, or gate metrics when a
  link to the owning artifact would leave the next action unchanged.
- Do not let recurring capability invariants live only in handoff. Handoff may
  point to an owner artifact, but the durable rule belongs in the skill,
  support-runtime contract, spec, validator, or operator document that owns the
  behavior.
- Do not list always-loaded host instruction surfaces in `References` by
  default when the host already injects them automatically at session start.
- Do not assume your own interpretation of the handoff is the only plausible
  one when a bounded critique could catch a likely misread.
- If the handoff changed materially, treat it as a real artifact update rather
  than an afterthought.

## References

- `references/adapter-contract.md`
- `references/chunked-routing.md`
- `references/continuation-sequence.md`
- `references/workflow-trigger.md`
- `references/state-selection.md`
- `references/document-seams.md`
- `references/spill-targets.md`
- `../../shared/references/closeout-discipline.md`
- `../../shared/references/fresh-eye-subagent-review.md`

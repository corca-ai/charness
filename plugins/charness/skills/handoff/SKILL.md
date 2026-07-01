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

Plan the run first, then read only the artifact, references, and gates named by
the plan.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/plan_handoff_run.py" --repo-root . --intent auto --invocation-text "<current user request>" --json
```

By default, `handoff` writes its durable artifact to
`<repo-root>/docs/handoff.md`. Repos can override the directory with
`<repo-root>/.agents/handoff-adapter.yaml`.

The planner resolves the adapter, summarizes the artifact, detects chunked
routing triggers, lists `required_reads`, and names cheap `gate_packets`.
For a bare direct skill invocation, add `--invoked-directly`; for a task-shaped
invocation, pass the user's task text so the deterministic chunker can bypass.
Open the listed reads using each entry's `base` before broader exploration.
Treat deterministic gates as evidence for shape and freshness, then use
judgment for the actual baton pass. The repo-owned size target is 30-60 lines;
70 lines is the usual hard stop. Multiple dated `## This Session (<date>)`
sections are a hard diary smell.
Assume a competent next operator can follow one good link.

## Workflow

1. Chunked routing (conditional). A handoff doc/skill invocation with no task
   directive — including a bare `/handoff` call, not only a doc mention
   — fires the chunker before pickup/refresh; it reasons over the live backlog
   (issues unioned with handoff entries via `--with-issues`). See
   `references/chunked-routing.md` for the trigger rule, pipeline, end-only write discipline, and `/achieve` draft.
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
   - continuation capability the next operator must have after reading
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
- `Continuation Capability`
- `Current State`
- `Next Session`
- `Discuss`
- `References`

## Guardrails

- On a session-open pickup — including one routed here by `find-skills` after a
  bare handoff-doc mention — invoke the workflow named in the `Workflow Trigger`
  instead of only re-reading the handoff; mention-only reading is the
  recurring routing miss this contract guards against.
- Do not write unverified state as fact.
- Handoff is a continuation pointer, not a diary: keep only what changes the next
  action and honor the size gate as a failure guard, not a target. The keep/drop,
  stale-detail, and dated-`This Session` rules live in
  `references/continuation-sequence.md` and `references/state-selection.md`.
- Single-source detail to the owning artifact (Workflow step 4): never replay
  quality/retro/debug/changelog/release detail or promote a recurring capability
  invariant inline, and leave host instruction surfaces out of `References` when
  the host already injects them automatically (`references/spill-targets.md`).

## References

- `references/adapter-contract.md`
- `references/chunked-routing.md`
- `references/continuation-sequence.md`
- `references/workflow-trigger.md`
- `references/state-selection.md`
- `references/spill-targets.md`
- `../../shared/references/closeout-discipline.md`
- `../../shared/references/fresh-eye-subagent-review.md`

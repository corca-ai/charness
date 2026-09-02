---
name: achieve
description: "Use when shaping a consequential objective into a frozen planning record, binding it to a provider-backed Goal Run, or resuming that run with `/goal #N`."
---

# Achieve

Use this skill to shape planning truth for a long-running objective and hand
execution to the issue-owned Goal Run. The Goal Draft is a planning record, not
a local tracker.

## Planning

Read the repository context, current adapter, relevant design material, and
provider state before asking the operator. Create or update the single planning
record with `upsert_goal.py`; its scaffold and upsert paths share one writer.
The writer preserves authored planning sections and refuses to rewrite a draft
once its sibling Goal Binding exists.

The record keeps the outcome, non-goals, boundaries, acceptance, verification
plan, planned slices, context sources, interview decisions, critique findings,
and any consequential decision that must be settled before activation. Safe
repository-relative paths are required when planning prose names an executable
checkout path. Markdown shape and fence balance are checked without treating
the draft as execution state.

## Interview

Resolve `interview.max_questions` from the adapter, defaulting to 15. Each
run treats it as a ceiling, not a quota. First retire ambiguity answered by the
repository, provider, prior operator answers, or evidence. Then ask only from
the resolution frontier: unresolved distinctions that could change the goal,
boundary, acceptance, or execution order. Collapse answered branches, do not
reopen them without contradictory evidence, and stop when finer resolution
would not change activation or the next action.

Each consequential question records alternatives, tradeoffs, a recommendation
and reason, the operator answer, and rejected alternatives. If the ceiling is
reached with a decision unanswered, return `interview-cap-reached` and wait for
the ordinary operator answer; do not create a binding or provider parent.

An unanswered ordinary planning question is not a local blocked status. It is
simply an unresolved planning decision. The draft remains mutable until the
operator approves the complete plan.

## Approval and identity

After planning and explicit approval of the exact briefing and draft bytes:

1. read the intended parent through the selected issue provider;
2. freeze and hash the complete Goal Draft; and
3. create the immutable Goal Binding containing the parent identity and approved
   Work Item manifest.

The binding is the frozen identity. The Goal Draft is not edited during
execution, and no local status or progress mutation is authorized.

## Exact pickup

The only issue-native resume input is trimmed text matching
`^/goal[ ]+#[1-9][0-9]*$`:

```bash
python3 "$SKILL_DIR/scripts/goal_run_pickup.py" \
  --repo-root . --objective "/goal #<parent-number>"
```

Pickup resolves the repository, reads the provider-backed parent once,
validates the Goal Run metadata, immutable binding, frozen draft identity, and
managed parent cursor, then reads only the cursor's next open child. It returns
`verified-read` or a typed refusal. It never falls back to local artifact state,
reconciles the graph, or mutates provider state.

The same read returns one bounded advisory projection from the ledger selection
preview. When a consumer adapter declares a digest, pickup keeps that digest as
the fallback. Missing lesson context never blocks pickup, and Achieve neither
rebuilds the ledger nor records session continuity.

Use the issue-owned Goal Run bootstrap, sync, and close commands for provider
establishment, graph repair, mutation, and closeout. Achieve does not duplicate
those authorities.

## References

- `references/index.md`
- `../../shared/references/bootstrap-resolution.md`

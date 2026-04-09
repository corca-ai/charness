---
name: handoff
description: Use when the user wants the next session prepared or asks to update a handoff artifact. Keep the handoff short, current, and operationally useful, and treat mention-only pickup as an instruction to continue the workflow named in the handoff trigger.
---

# Handoff

Use this when the goal is to let the next operator continue without re-deriving
the session state.

The handoff should describe the exact next pickup path, not preserve a diary of
everything that happened.

## Bootstrap

Start from the current handoff artifact and live repo state.

```bash
# 1. current handoff and adjacent plan
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
sed -n '1,220p' docs/master-plan.md

# 2. current repo state
git status --short
git log --oneline -5

# 3. current skill surfaces that change the next step
rg --files skills/public docs
```

If the user referenced the handoff to resume work rather than refresh it, read
the `Workflow Trigger` first and continue with that workflow.

## Workflow

1. Determine whether this is pickup or refresh.
   - for pickup, treat the workflow trigger as authoritative next-step
     instruction
   - for refresh, inspect only the live state that changes the next action
2. Identify the canonical handoff artifact.
   - in this repo, prefer `docs/handoff.md`
   - in another host, use the current durable handoff surface instead of
     forcing one filename
3. Rewrite the handoff around continuation, not history.
   - exact workflow trigger
   - current state facts that matter
   - ordered next actions
   - open decisions that still need user input
   - tight reference list
4. Keep the trigger explicit.
   - if a named workflow or skill should run next, say it directly
   - if the next pickup depends on reading specific files first, name them
5. Finish with a clean baton pass.
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
- Do not hide the real next workflow behind vague prose.
- Do not write unverified state as fact.
- Do not let the handoff drift away from the current repo state.
- If the handoff changed materially, treat it as a real artifact update rather
  than an afterthought.

## References

- `references/workflow-trigger.md`
- `references/state-selection.md`
- `references/document-seams.md`

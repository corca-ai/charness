# Goal Artifact

The goal artifact is a reviewable activation artifact and the living scratchpad
for one autonomous goal run.

## Location

```text
charness-artifacts/goals/<yyyy-mm-dd-slug>.md
```

This is operational harness state, not product docs: safe to commit with other
Charness artifacts, and outside manually maintained documentation. The location
is fixed for the first version.

## Shape

```markdown
# Achieve Goal: <title>

Status: draft | active | blocked | complete
Created: <date>
Activation: `/goal @charness-artifacts/goals/<file>.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

## Non-Goals

## Boundaries

## User Acceptance

What the user can do to verify completion directly.

## Agent Verification Plan

### Low-Cost Checks

### High-Confidence Checks

### External Or Live Proof

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Slice Log

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
```

## Helper Scripts

Use the helpers instead of hand-editing the markdown; they preserve manual
content and avoid timestamp-only churn. Resolve `$SKILL_DIR` per
`../../../shared/references/bootstrap-resolution.md` first.

```bash
# Scaffold a new goal (status draft), or update only the status of an existing one.
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . \
  --slug ceal-184-push-confidence --title "Ceal 184 push confidence" \
  --goal-body "Make the accumulated local commits safe to push."

# Append one slice report to the Slice Log.
python3 "$SKILL_DIR/scripts/append_slice_log.py" --repo-root . \
  --slug ceal-184-push-confidence --date 2026-05-26 --name "Inventory local risk" \
  --objective "Map the full unpushed surface" --verification "git diff --stat origin/main..HEAD"

# Flip status as the run progresses (draft -> active -> blocked/complete).
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . \
  --slug ceal-184-push-confidence --title "Ceal 184 push confidence" --status active

# Check required sections, status, and activation line before completion.
python3 "$SKILL_DIR/scripts/check_goal_artifact.py" --repo-root . \
  --slug ceal-184-push-confidence --date 2026-05-26
```

`upsert_goal.py` never overwrites an existing artifact body; on a second call it
only rewrites the `Status:` line, and only when the value changed. The slice
number in `append_slice_log.py` is derived from the existing `### Slice N:`
headings, so reports stay ordered without a counter argument.

## Metrics Honesty

Slice and final metrics use host-agnostic shallow signals. Prefer
`retro`'s `probe_host_logs.py` for token / turn / tool-call availability rather
than asserting counts the host log does not expose. Deep per-session counting is
Codex-specific and best-effort; record `Metrics: when available` instead of
fabricating numbers.

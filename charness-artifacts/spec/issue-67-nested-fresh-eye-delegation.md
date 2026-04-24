# Spec: Issue #67 - nested fresh-eye review requirements

Source: https://github.com/corca-ai/charness/issues/67

## Problem

Premortem and counterweight guidance currently says fresh-eye review requires
subagents, but it does not distinguish parent-level delegation from recursive
delegation inside an already spawned subagent.

That ambiguity can make a delegated reviewer think it must spawn another
reviewer before performing its assigned lens. When the nested runtime lacks
spawn tools, the reviewer reports a blocked canonical path even though the
parent already satisfied the fresh-eye requirement by spawning that reviewer.

## Current Slice

Clarify the public `premortem` contract and shared subagent capability check:

- parent agents own spawning the bounded angle and counterweight reviewers
- delegated subagents perform the assigned lens directly
- recursive delegation happens only when the caller explicitly requests it
- review artifacts record `Fresh-Eye Satisfaction` as
  `parent-delegated`, `nested-delegated`, or `blocked <host-signal>`

## Fixed Decisions

- **No new public skill.** This is a clarification to the existing premortem
  execution contract.
- **Central rule lives in `subagent-capability-check.md`.** `spec`, `quality`,
  and `handoff` already reference that shared check.
- **`premortem/SKILL.md` gets a concise hook.** Detailed nested-runtime behavior
  belongs in the reference.
- **No recursive spawning by default.** Recursive delegation is opt-in and must
  be named by the caller.

## Acceptance Checks

- `rg -n "parent-delegated|nested-delegated|recursive" skills/public/premortem`
  finds the delegation context rule.
- `rg -n "already the bounded fresh-eye subagent|do not spawn another" skills/public/premortem`
  finds the subagent-side instruction.
- `python3 scripts/validate_skills.py --repo-root .` passes.
- Prompt-surface proof is refreshed or the exact blocker is recorded.

## Non-Goals

- No attempt to make subagents available inside every subagent runtime.
- No same-agent fallback for parent sessions when no parent-level spawn is
  available.
- No change to the minimum angle/counterweight review counts.

## Premortem

The likely failure is overcorrecting into same-agent fallback. The wording must
say that parent-level delegation satisfies the fresh-eye requirement only for
the delegated reviewer, not for a parent session that never spawned anyone.

## Canonical Artifact

`charness-artifacts/spec/issue-67-nested-fresh-eye-delegation.md`

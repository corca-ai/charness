---
name: premortem
description: "Use when a non-trivial design, deletion, rename, release, or workflow decision needs a before-the-fact failure review. Probe distinct failure angles, then run a counterweight pass that separates real blockers from over-worry before the caller locks the decision."
---

# Premortem

Use this when the next risk is not implementation detail alone, but locking the
wrong decision or carrying the wrong fear into implementation.

`premortem` is the structured before-the-fact counterpart to `retro`.
It should stress a pending decision from distinct angles, then perform one
counterweight pass so the findings become actionable instead of a paranoia pile.
Caller skills should use it as the reusable subroutine for non-trivial
decision review rather than rewriting angle selection or counterweight logic
inline.
Routine slices do not need `premortem` at all.
When a caller needs one, `premortem` always means a fresh bounded subagent
review. `bounded` limits scope and time box, not execution mode. There is no
same-agent or local `premortem` variant.

Caller contract:

- pass the pending decision artifact or a tight source summary
- state success and out-of-scope lines up front
- consume the returned four-bin triage directly:
  `Act Before Ship`, `Bundle Anyway`, `Over-Worry`, `Valid but Defer`
- write any decision-changing result back into the caller's durable contract
- if the host blocks the canonical subagent path, treat that as a blocked state
  for this run instead of rewriting the outcome as a local review

## Bootstrap

Read only the smallest decision surface that makes the choice legible.

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
rg --files docs skills
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
rg -n "spec|decision|follow-up|non-goal|out of scope|acceptance|risk|rename|delete|remove|migration" .
```

If a current spec, plan, PR proposal, or issue already exists, use that as the
decision contract. Do not restate the whole project history.

## Workflow

1. Restate the pending decision.
   - what is being changed, removed, or locked
   - what would count as success
   - what is explicitly out of scope for this pass
2. Pick a bounded set of contrasting angles.
   - use subagents as the canonical path
   - use at least two angle subagents plus one separate counterweight subagent
   - default to three angle subagents for a normal non-trivial decision
   - expand to four angle subagents only when the change is clearly broad:
     cross-surface, breaking, migration-heavy, or release plus doc cascade
   - choose angles that can disagree meaningfully, not five near-duplicates
   - see `references/angle-selection.md`
3. Run the angle pass.
   - use bounded fresh-eye subagents with one angle each
   - do not collapse the counterweight into one of the angle subagents; keep it
     as a separate skeptical pass
   - before reporting the canonical path as blocked, run the capability check
     in `references/subagent-capability-check.md`: attempt the bounded subagent
     setup, resolve any availability uncertainty, and cite the concrete signal
     that made the host unable to provide subagents
   - if the host cannot provide subagents, stop and report that the canonical
     premortem path is unavailable; fixing the host-side subagent contract is
     the next move instead of inventing a local substitute
   - do not collapse into a same-agent local pass or degraded variant
4. Collapse the findings into one candidate concern list.
   - deduplicate overlap
   - keep evidence and cited source paths with each concern when available
   - prefer concerns that would change the next move, not generic worry
5. Run one counterweight pass.
   - act like a skeptical senior engineer pushing back on paranoia,
     speculative consumers, and expensive hypotheticals
   - triage each concern using `references/counterweight-triage.md`
   - preserve the four bins explicitly so caller skills can consume the result
     without re-triaging the same fear list
6. Persist the decision memory.
   - if a concern changes the decision, tighten the spec, plan, or release
     contract immediately
   - if a rejected concern matters to future readers, write it into a short
     `Deliberately Not Doing` or equivalent section in the durable artifact
7. End with the next move.
   - what must change before implementation or release
   - what can be bundled cheaply
   - what is over-worry and should be ignored
   - what is valid but explicitly deferred

## Output Shape

The result should usually include:

- `Execution`
- `Decision`
- `Angles`
- `Findings`
- `Counterweight Triage`
- `Deliberately Not Doing`
- `Next Move`

If the host blocks the canonical subagent path before execution, report
`Execution: blocked <host-signal>` and the next move instead of inventing a
degraded concern list.

## Guardrails

- Do not turn premortem into broad ideation. Start from an actual pending
  decision.
- Do not open more angles than you can triage honestly.
- Do not keep rejected alternatives only in chat when the same debate will
  likely recur.
- Do not treat every surfaced concern as equally important.
- Do not skip the counterweight pass; a paranoia backlog without triage is not
  decision support.
- Do not silently downgrade premortem into a same-agent local pass. Before
  declaring subagents unavailable, run `references/subagent-capability-check.md`
  and cite the concrete host signal. Assuming a cap from priors is the failure
  mode the check exists to stop. If the host still cannot provide subagents,
  stop and leave the host-side contract gap visible instead of improvising a
  degraded premortem.

## References

- `references/angle-selection.md`
- `references/counterweight-triage.md`
- `references/subagent-capability-check.md`

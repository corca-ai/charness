---
name: critique
description: "Use when a non-trivial design decision, code change, release, rename, deletion, spec, or workflow change needs a before-the-fact critique. Probe distinct failure angles, then run a counterweight pass that separates real blockers from over-worry before the change locks in."
---

# Critique

Use this when the next risk is not implementation detail alone, but locking the
wrong change or carrying the wrong fear into the next slice.

`critique` is the structured before-the-fact counterpart to `retro`. The
substrate is the same across targets — pre-lock-in stress with anchor-
discriminated multi-angle review followed by one counterweight pass — and the
target reference shapes the angle distribution and output. Decision pre-mortem
(Klein lineage) is one of those targets; code/PR critique, release critique,
rename critique, and spec critique reuse the same substrate.

Task-completing repo work always records critique before closeout. Scale the
pass, not the obligation: small local-risk slices may use a short scoped
critique in the caller's closeout artifact, while non-trivial design,
deletion, rename, release, workflow, compatibility, install/update,
host-proof, prompt-surface, public-skill, validator, or export changes use
this standalone skill.

When this standalone `critique` skill runs, it always means a fresh bounded
subagent review. `bounded` limits scope and time box, not execution mode. There
is no same-agent or local standalone `critique` variant.

Delegated reviewer fast path: if the current assignment says you are a bounded
angle reviewer, counterweight reviewer, or fresh-eye reviewer spawned by a
parent, perform that assigned lens directly and return the requested triage.
Do not run host capability checks or require nested spawn access.
Do not report blocked for missing nested subagents unless the parent
explicitly asked for recursive delegation.

Before any host-capability question, honor `<repo-root>/AGENTS.md`
`Subagent Delegation`: required bounded review is already delegated. If the
parent agent already delegated a bounded angle or counterweight review to a
subagent, that subagent performs its assigned lens directly; it should not
spawn another reviewer unless the caller explicitly requests recursive
delegation. See `../../shared/references/fresh-eye-subagent-review.md`.

Caller contract:

- pass the pending change artifact or a tight source summary
- state success and out-of-scope lines up front
- consume the returned four-bin triage directly:
  `Act Before Ship`, `Bundle Anyway`, `Over-Worry`, `Valid but Defer`
- write any change-affecting result back into the caller's durable contract
- record `Fresh-Eye Satisfaction` as
  `parent-delegated`, `nested-delegated`, or `blocked <host-signal>`
- if the host blocks the canonical subagent path, treat that as a blocked state
  for this run instead of rewriting the outcome as a local review

## Target Selection

Pick the reference that matches the change. The target reference owns the
angle distribution, the counterweight-bin specifics, and the output shape;
the substrate (angles + counterweight + four bins) is shared.

| Trigger phrase                                  | Reference                          |
|-------------------------------------------------|------------------------------------|
| `decision premortem`, design lock-in            | `references/premortem-decision.md` |
| `code critique`, PR/commit/snippet/repo review  | `references/code-critique.md`      |
| `release critique`, release lock-in             | `references/release-critique.md`   |
| `rename critique`, deletion, slug churn         | `references/rename-critique.md`    |
| `spec critique`, pre-impl spec lock-in          | `references/spec-critique.md`      |

If the call is ambiguous, ask which target reference applies before spawning
angles. Do not silently pick a target that changes the angle distribution
(for example, treating a release critique as a generic decision premortem
loses the surface-lock inventory).

## Bootstrap

Read only the smallest change surface that makes the next move legible.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
rg --files docs skills
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
rg -n "spec|decision|follow-up|non-goal|out of scope|acceptance|risk|rename|delete|remove|migration" .
```

If a current spec, plan, PR proposal, issue, diff, or release artifact already
exists, use that as the change contract. Do not restate the whole project
history.

## Workflow

1. Restate the pending change.
   - what is being changed, removed, or locked
   - what would count as success
   - what is explicitly out of scope for this pass
2. Pick a bounded set of contrasting angles.
   - use subagents as the canonical path
   - use at least two angle subagents plus one separate counterweight subagent
   - default to three angle subagents for a normal non-trivial change
   - expand to four angle subagents only when the change is clearly broad:
     cross-surface, breaking, migration-heavy, or release plus doc cascade
   - choose angles that can disagree meaningfully, not five near-duplicates
   - the target reference's `Anchor Angle Distribution` section names the
     anchor-by-anchor weighting; see also `references/angle-selection.md`
3. Run the angle pass.
   - use bounded fresh-eye subagents with one angle each
   - do not collapse the counterweight into one of the angle subagents; keep
     it as a separate skeptical pass
   - before reporting the canonical path as blocked, use
     `../../shared/references/fresh-eye-subagent-review.md`
   - if you are already the bounded fresh-eye subagent for one assigned angle,
     counterweight, or reviewer lens, do the assignment directly; do not run
     the capability check again unless the assignment explicitly asks for
     nested delegation
   - if the host cannot provide subagents, stop and report that the canonical
     critique path is unavailable; fixing the host-side subagent contract is
     the next move instead of inventing a local substitute
   - do not collapse into a same-agent local pass or degraded variant
4. Collapse the findings into one candidate concern list.
   - deduplicate overlap
   - keep evidence and cited source paths with each concern when available
   - prefer concerns that would change the next move, not generic worry
5. Run one counterweight pass.
   - act like a skeptical senior engineer pushing back on paranoia,
     speculative consumers, and expensive hypotheticals
   - triage each concern using `references/counterweight-triage.md` plus the
     target reference's `Counterweight Bins` specifics
   - preserve the four bins explicitly so caller skills can consume the result
     without re-triaging the same fear list
6. Persist the change memory.
   - if a concern changes the change, tighten the spec, plan, release contract,
     code diff, or rename plan immediately
   - if a rejected concern matters to future readers, write it into a short
     `Deliberately Not Doing` or equivalent section in the durable artifact
7. End with the next move.
   - what must change before implementation, merge, or release
   - what can be bundled cheaply
   - what is over-worry and should be ignored
   - what is valid but explicitly deferred

## Output Shape

The result should usually include:

- `Execution`
- `Fresh-Eye Satisfaction`
- `Target` — which reference shaped this run
- `Change`
- `Angles`
- `Findings`
- `Counterweight Triage`
- `Deliberately Not Doing`
- `Next Move`

The target reference's `Output Shape` section names additional sections
required for that target (for example, release surface-lock inventory or
rename slug-drift evidence).

If the host blocks the canonical subagent path before execution, report
`Execution: blocked <host-signal>` and the next move instead of inventing a
degraded concern list.
If parent-level delegation satisfied the fresh-eye requirement, report
`Fresh-Eye Satisfaction: parent-delegated`; use `nested-delegated` only when
recursive delegation was explicitly required and actually ran.

## Guardrails

- Do not turn critique into broad ideation. Start from an actual pending
  change.
- Do not pick a target reference that changes the angle distribution from
  what the caller actually asked for.
- Do not open more angles than you can triage honestly.
- Do not keep rejected alternatives only in chat when the same debate will
  likely recur.
- Do not treat every surfaced concern as equally important.
- Do not skip the counterweight pass; a paranoia backlog without triage is
  not change support.
- Do not silently downgrade critique into a same-agent local pass. Before
  declaring subagents unavailable, use
  `../../shared/references/fresh-eye-subagent-review.md` and cite the concrete
  host signal. If the host still cannot provide subagents, stop and leave the
  host-side contract gap visible instead of improvising a degraded critique.
- Do not make an already delegated angle or counterweight reviewer spawn
  another reviewer unless recursive delegation was explicitly requested.

## References

- `references/premortem-decision.md`
- `references/code-critique.md`
- `references/release-critique.md`
- `references/rename-critique.md`
- `references/spec-critique.md`
- `references/angle-selection.md`
- `references/counterweight-triage.md`
- `../../shared/references/agent-assessment-invariant.md`
- `../../shared/references/fresh-eye-subagent-review.md`

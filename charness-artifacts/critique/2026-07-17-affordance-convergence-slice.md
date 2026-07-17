# CLI output affordance convergence slice

Date: 2026-07-17

## Decision Under Review

Operator-approved breaking convergence per
`charness-artifacts/spec/cli-output-affordance-contract.md` Current Slice 2:
worktree libs' string `next_action` → `next_step`, runtime doctor host map
`next_steps` → `host_next_steps` (list-shape `next_steps` keeps the name),
tool-attention string `next_action` → `next_step`, human affordance prefix
unified to `NEXT:`, docs/specdown/CLI-reference converged, mirror re-synced.
No compatibility aliases; ships under a major version bump.

## Failure Angles

- Missed rename site or stale consumer silently reading a removed key/prefix.
- Wrong rename: a structured `next_action` object or list-shape `next_steps`
  swept up by the mechanical sed.
- Documented convention text diverging from actual emitted shapes.
- Contract overstatement: spec claims the diff does not deliver.
- Kept exceptions (`next_action_hint`, planner strings, `--next-action` flag)
  creating a new trap.

## Counterweight Pass

- Reviewer confirmed every changed emitter moved in lockstep with its
  consumers, both mirrors synced, structured objects and list shapes
  untouched, and no consumer left reading a stale key. Real blockers: none.
- Two should-fixes were real and cheap, so they were fixed in-slice (F1, F2).
  The prefix "everywhere" wording and scope notes were spec overstatements,
  not code defects; the spec text was corrected rather than widening the
  breaking surface further (F3–F7).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/charness_cli/test_worktree_audit.py:138 | action: fix | note: the `next:`→`NEXT:` renderer change had zero regression coverage; added `NEXT:`-prefix (and no-`next: `) assertions to the audit and doctor text-renderer tests.
- F2 | bin: act-before-ship | evidence: strong | ref: .charness/specdown/report.json | action: fix | note: tracked specdown report still asserted the old `next_steps` shape; re-ran `specdown run` (4 specs / 8 cases PASS, including the live `host_next_steps` doctor assertion) so the committed report matches the committed spec.
- F3 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/spec/cli-output-affordance-contract.md | action: fix | note: spec said prefix unified "everywhere" while quality-plane advisory scripts keep `Next action:` prose; reworded to scope the claim to the `charness` CLI output boundary and named the `suggest_mutation_coverage_command.py` inclusion the diff actually made.
- F4 | bin: act-before-ship | evidence: moderate | ref: scripts/render_cli_reference.py | action: fix | note: convention parenthetical omitted the gather-advise list surface the contract enumerates; added and regenerated.
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness:4051 | action: document | note: `charness doctor --next-action` emits `{"next_action": <string>}` as a flag-named message projection; recorded in the spec's Deferred Decisions as intentional, revisit only if a machine consumer trips.
- F6 | bin: over-worry | evidence: weak | ref: scripts/worktree_audit_lib.py | action: document | note: inline `next_step=` metadata vs standalone `NEXT:` line are two roles (key=value annotation vs affordance line), not two spellings of one contract; recorded here, no code change.

## Reviewer Tier Evidence

- Requested tier: per-host contract (AGENTS.md Subagent Delegation split
  2026-07-17) — Claude Code host, typed `bounded-reviewer` agent with
  session-model inheritance; no Codex-scoped model request applies here.
- Requested spawn fields: subagent_type=bounded-reviewer.
- Host exposure state: host-defaulted
- Application state: the typed `bounded-reviewer` agent ran with the inherited
  session model, which is exactly what the Claude Code host contract requests;
  contract-conformant under the per-host split.

## Fresh-Eye Satisfaction

parent-delegated — bounded read-only reviewer (Read/Grep/Glob only) ran in the
shared worktree over the spec plus the full working diff;
`reviewer_boundary_fingerprint.py` snapshot/verify around the review returned
`ok: true` with empty drift. Reviewer verdict: no blockers, two should-fixes
(both fixed in-slice), notes dispositioned above.

## Boundary Ownership

- Producer: the root `charness` CLI (worktree, runtime doctor/update/init,
  tool aggregate payloads and human summaries) plus the mirrored worktree libs.
- Consumer: agents and operators resuming from payloads, persisted state, or
  human summaries without out-of-band field-name knowledge.
- Owning surface: root `charness` CLI + generated CLI reference header +
  `specs/tool-doctor.spec.md` executable assertion.
- Verdict: owned-correctly — the convention, its executable proof, and the
  breaking-change record live on surfaces this repo owns; the kept exceptions
  are recorded in the spec's Deferred Decisions rather than in chat.

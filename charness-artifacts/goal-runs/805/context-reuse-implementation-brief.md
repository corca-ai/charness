# Bounded implementation: context reuse (#808)

Implement the approved context-reuse WorkItem and capability brief:

- `charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/context-reuse.md`
- `charness-artifacts/create-skill/2026-09-06-context-reuse-brief.md`
- `charness-artifacts/goal-runs/805/reviews/design-disposition.md`

Read the delivered design repair review before changing behavior. This lane
starts only after the parent's design disposition. Do not repeat standalone
design reviews, broaden the task, or spawn nested agents. Preserve the exact
consumer contract; parent owns final integration, export, first-reader execution,
four-arm comparison, provider state and publication. No actual pilot has run.

## Deliverable

Make small coherent changes to spec/debug/retro core and the direct reference/
planner consumers named in the capability brief. Remove redundant operations,
not responsibilities. No modes, new cache, eligibility artifact, universal
bootstrap helper or new standing semantic evaluator. Keep frontmatter, parsed
artifact contracts, falsifiability, independent risk boundaries, emitted debug
validator and subject/evidence-mode routing. Core owns conditional selection.

For retro, explicit no-write wins over every automatic write; a preexisting
output directory alone does not select persistence. Durable/metrics/follow-up
routes retain owned persistence and validation. A concrete counterfactual is
required; names/second lens add distinct insight, not quotas. Reconcile emitted
planner text and direct references without creating a chat flag: chat consumers
simply do not invoke the durable planner. Keep direct lenses possible within
the selected path, and retain useful optional catalog guidance.

For debug, warm reuse only applies to the known same open investigation,
subject/evidence/output/validator contract, with current relevant pointer/risk
deltas. Unknown/new/resolved/mismatched cases use the existing emitted planner
commands. One evidenced cause plus a falsifier is valid; competing causes need
discriminating observations. Replace both quota and plural-only guardrail.

For spec, use known current contract/acceptance reality and relevant deltas.
Broad discovery is conditional; required live provider/risk reads are not cached.
Inspect impl's existing reuse rule as precedent; do not edit impl or AGENTS.

## Scope and checks

Writable canonical skills: `skills/public/spec/`, `skills/public/debug/`,
`skills/public/retro/`. Direct contract guard: `tools/check_skill_contracts.py`
only when an assertion genuinely freezes redundant wording, with the remaining
behavioral owner/negative control demonstrated. Do not bulk-delete pins.

Tests are part of the deliverable: existing spec/debug/retro tests by those
names, especially `tests/test_retro_plan.py`, planner/scaffold/artifact tests,
and `tests/quality_gates/test_skill_contracts_validation.py`, retro installed
plan/auto-trigger/persistence tests. Do not edit shared reviewer, issue or release
tests. The task scope allows direct tests by those existing globs; if a missing
write scope is essential, report it instead of editing outside scope.

Run the repository standing pytest wrapper with explicit focused targets and
the selected skill-contract/markdown/adapter validators. Use external runtime
cache/basetemp roots. Keep deterministic tests about emitted structured behavior
and parsed boundaries; do not replace one exact prose expectation with another
as semantic proof. Existing first-prompt cases and the brief's concrete
intersections define parent-run consumer proof after export.

Do not edit generated `plugins/`, marketplace/version/manifests, baselines,
root AGENTS/CLAUDE, provider artifacts, lesson/RCA ledgers, or the parent index.
The task runner owns lane completion/retention and changed-line receipt; leave a
focused patch and concise result naming files, executed checks, unresolved
probes and non-claims. Do not claim installed/consumer behavior from unit tests.

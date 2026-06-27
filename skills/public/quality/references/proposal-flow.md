# Proposal Flow

`quality` is not only a gate-reporting skill. It is also a proposal skill.

## Principle

If a useful gate is missing, propose the smallest concrete setup that would
improve confidence materially.

If the issue is automatable, propose the gate before proposing more prose.

## Good Proposals

Good proposals name:

- the seam the gate would protect
- the command or tool family to use
- where it should run
- why it is the next best improvement
- whether the proposal is `AUTO_CANDIDATE` or `NON_AUTOMATABLE`
- the result of an existing-convention check (`git log -S <subject>`,
  `grep -rn <subject>`, marker scan in `pyproject.toml`/SKILL files); if a
  convention already governs the cost, the proposal must be the routing fix
  that honors it, not an additive new gate
- what local install or permission is required when the gate depends on an
  external binary or service
- the exact verification command when a repo-owned doctor or recommendation
  helper already exposes one
- for `NON_AUTOMATABLE` recommendations, the smallest experiment or review loop
  that would produce better evidence, including the observation point and
  revisit cadence

## Measurement Evidence

Numbers in proposals (sizes, runtimes, footprints, counts) must come from a
command run this turn — `du`, `wc`, `time`, an inventory helper, a runtime
budget snapshot, etc. The artifact body should cite the command in
`## Commands Run`.

Estimates are allowed only when measurement is genuinely blocked (e.g.,
external surface, future state). Label them explicitly as "estimate" and
name what would have been measured. Loose mental-model numbers ("~1 GiB
each") tend to compound across artifacts and bias toward the wrong fix; the
discipline exists to make a wrong number visible early.

## Anti-Need Before Need

Before drafting `Recommended Next Quality Moves`, run the existing-convention
check above for each candidate. If the cost or risk is already declared
(`@pytest.mark.<marker>`, marker docs in `pyproject.toml`, repo-owned policy
files, comments at the origin commit), the recommendation must be the
routing fix or deletion that honors the prior declaration — not an additive
new gate. A new gate is correct only after confirming no existing convention
is being violated.

Examples:

- add `ruff check` in CI because Python linting is currently absent and the repo
  already uses `<repo-root>/pyproject.toml`
- move repeated skill helper logic into a shared module because duplicate
  bootstrap code is already drifting across multiple skills
- collapse repeated checked-in guidance into one source document because the
  same rules now exist in multiple docs and will drift
- add one focused integration test because the failure path is user-visible and
  unit tests cannot prove it honestly
- remove one broad E2E smoke because a cheaper direct proof now covers the same
  seam and the old path only adds runtime cost
- split one oversized test module into seam-specific files because maintainers
  and agents can no longer navigate or refactor it cheaply as one surface
- split behavior proof below a CLI, subprocess, browser, or other delivery
  boundary before adding an affected-test selector that would only hide the
  broad seam; see `testability-and-selection.md`
- add dependency review in CI because supply-chain changes are currently
  invisible in pull requests
- replace repeated documentation guidance with `markdownlint` or a repo-owned
  validator because the rule is deterministic and repeated manually today
- run `scripts/check_title_slug_drift.py` against `docs/specs/` and other
  rename-prone Markdown roots after concept renames because H1-vs-slug drift
  is detectable mechanically and easy to miss in prose review
- run a one-week HITL review over three real handoffs because the issue is
  judgment quality rather than a deterministic lint rule, and record which
  observations would justify automation later

## Adapter-Driven Probes

When the resolved adapter has no errors, run any adapter-driven proposal
probes that quality ships and surface their `status: missing` results as
active recommendations:

- `propose_mutation_testing.py` — installs the `mutation_testing` block and
  workflow template when the consumer has not opted in. See
  `mutation-testing.md` for the protocol and the `--execute` install flow.

Behavior-test recommendations use the Cautilus robustness contract in
`behavior-testing.md`. They remain recommend-only unless the user supplies an
explicit log-backed behavior source and the Cautilus planner allows execution;
do not install a Charness-owned runner for this class of proof.

Skip adapter-driven probes entirely when validator errors are non-empty;
their output is not meaningful against a broken adapter.

## HITL Handoff

When a `NON_AUTOMATABLE` proposal needs deliberate human judgment, shape it so
`hitl` can start a bounded review loop without rediscovering the problem.

Before handoff, include the agent's Agent Assessment + Recommended Disposition
per `../../../shared/references/agent-assessment-invariant.md`. The human
reviews judgment, not first-pass thinking.

Include:

- `target`: the bounded artifacts, diffs, conversations, or decisions to review
- `review_question`: the question human judgment must answer
- `decision_needed`: what the reviewer must approve, reject, classify, or
  refine
- `must_not_auto_decide`: what should remain human-governed during this loop
- `observation_point`: what evidence would change the next move
- `revisit_cadence`: after how many items, days, or events the loop should be
  evaluated
- `automation_candidate`: what repeated rule, if observed, might later become a
  validator, script, or gate

## Bad Proposals

Bad proposals sound like:

- improve code quality
- add more tests
- harden security

Those are ambitions, not next steps.

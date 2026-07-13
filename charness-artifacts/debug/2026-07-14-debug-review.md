# Debug Review
Date: 2026-07-14

## Problem

The pre-release full quality gate failed after updating Cautilus and splitting
three overgrown test modules: two Cautilus proposal fixtures were rejected and
the boundary-bypass ratchet reported new candidate keys.

## Correct Behavior

Given the current supported Cautilus release and a behavior-preserving test-file
split, when the full read-only quality gate runs, then proposal fixtures satisfy
the supported schema and boundary accounting remains neutral.

## Observed Facts

- Cautilus changed from 0.18.0 to 0.19.3 and doctor reports it current/ready.
- Pytest rejected `proposalCandidates[0].evidence[0].sourceKind` with the exact
  allowed set `human_conversation, agent_run, skill_evaluation, workflow_run`.
- After correcting that enum, the same final-consumer tests reported that
  `discover scenarios propose` did not emit valid JSON; Cautilus 0.19.3 emits
  YAML unless its structured format is selected explicitly.
- The focused six-module suite passed 129 tests; full quality reported three new
  file-qualified boundary candidate keys after the modules moved.

## Reproduction

- `./scripts/run-quality.sh --read-only` reproduces both failures.

## Candidate Causes

- Cautilus 0.19.3 tightened a previously permissive proposal evidence enum.
- Charness invokes a different binary or schema path than the updated doctor reports.
- Test moves duplicated subprocess helpers or changed file-key accounting rather
  than only relocating existing boundary tests.

## Hypothesis

- falsifiable claim: the fixture contains an enum outside the 0.19.3 schema and
  the ratchet delta is entirely explained by file-qualified moved tests, and
  every Cautilus stdout consumer must request JSON explicitly; using a supported
  enum, explicit JSON format, and reviewed boundary exemptions will clear the
  failures without changing domain assertions | disconfirmer: inspect the tagged
  upstream schema, run the command with/without `--json`, and compare inventory
  keys before editing production behavior.

## Verification

- result: confirmed — the tagged upstream schema documents `skill_evaluation`
  and excludes the fixture's `skill_contract`; the current inventory adds only
  the three file-qualified keys produced by the moved boundary-contract tests.
- focused proof: 138 tests passed across the split-module, Cautilus command,
  and live installed-tool consumers; Ruff and the boundary ratchet pass.
- final-consumer proof: `./scripts/run-quality.sh --read-only` passed 81 gates
  and 4,587 tests after sync.

## Root Cause

Three integration assumptions were stale. The proposal fixture used an
evidence-kind spelling outside Cautilus 0.19.3's supported enum, and the adapter
relied on the old JSON default instead of requesting its parsed format.
Separately, the boundary ratchet keys intentional subprocess tests by test file,
so moving them created new keys even though assertions and targets were unchanged.

## Invariant Proof

- Invariant: supported external-tool fixtures and behavior-preserving test moves
  must remain accepted by their final quality consumers.
- Producer Proof: 138 focused tests pass; both parsing subprocess command-shape
  tests assert an explicit `--json` request.
- Final-Consumer Proof: full read-only quality passed 81/81 gates and 4,587 tests.
- Interface-Shape Sibling Scan: inspect every proposal `sourceKind` and each moved
  subprocess-boundary key; all nine fixture values and all three moved keys are
  dispositioned, and no sibling stdout JSON parser was found.
- Non-Claims: no Cautilus evaluation or public runtime/API change.

## Detection Gap

- focused six-module pytest | did not exercise installed-Cautilus proposal tests
  or repository-wide boundary inventory | full quality correctly fired before release.

## Sibling Search

- Mental model: a dependency update and file move are not behavior-neutral until
  their schema and repository-wide keyed consumers agree.
- schema axis: all proposal evidence inputs | decision: repair | proof: all nine
  obsolete values now use supported `skill_evaluation`.
- output-format axis: all live Cautilus subprocess stdout parsers | decision:
  repair | proof: the two parsing consumers request `--json`; the evaluation
  runner is an intentional stdout passthrough.
- accounting axis: all three moved test families | decision: exempt moved keys |
  proof: reasoned, revisit-bounded exemptions keep candidate count neutral.
- cross-file: Cautilus proposal inputs and boundary baseline are sibling consumers.

## Seam Risk

- Interrupt ID: pre-release-advisory-integration
- Risk Class: external-seam
- Seam: installed Cautilus schema and output defaults consumed by integration scripts
- Disproving Observation: upgrading 0.18.0 to 0.19.3 broke a fixture enum and
  changed default output from JSON to YAML while explicit JSON remained available.
- What Local Reasoning Cannot Prove: that a future upstream version will retain
  the same enum or explicit-format flag without running its final consumers.
- Generalization Pressure: monitor

Keep explicit format selection at every parsing subprocess boundary; centralize
only if a third live consumer appears.

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-07-14-cautilus-structured-output-compatibility.md

## Prevention

Keep the full quality gate before release critique and publication; it is the
existing final consumer for optional installed-tool and repository-wide keyed
inventory effects.

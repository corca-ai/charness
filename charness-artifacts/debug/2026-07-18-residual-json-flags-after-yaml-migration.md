# Residual JSON Flags After YAML Migration Debug
Date: 2026-07-18

## Problem

Public `charness` stdout moved to YAML in `28e237f3`, but public skill
instructions still tell agents to invoke planner and evidence scripts with
`--json`. The mismatch caused this session to issue obsolete-format calls and
made the operator reasonably doubt whether the YAML migration was complete.

## Correct Behavior

Given a public skill that asks an agent to consume structured command output,
when the documented command runs, then its public format vocabulary must match
the root CLI: YAML by default, with `--detail` only when a fuller payload is
needed. Hidden legacy `--json` parsing may remain temporarily for compatibility,
but public skill prose and help must not teach it.

## Observed Facts

- Commit `28e237f3` explicitly changed the **public root CLI boundary** to YAML;
  `charness` now removes legacy `--json` from argv and its help omits the flag.
- Eleven public/support `SKILL.md` files mention `--json`; eight are executable
  workflow instructions and `create-cli` still recommends JSON-shaped public
  command contracts.
- `plan_handoff_run.py`, `plan_retro_run.py`, and `plan_debug_run.py` emit the
  same JSON-shaped packet with or without `--json`; the flag is redundant.
- Quality, risk-interrupt, setup-routing, prove-boundary, and release planners
  use `--json` to select a full machine payload over a human summary.
- The repo's governing `AGENTS.md` and Cautilus operator reference still taught
  `plan_cautilus_proof.py --json`, so the drift also crossed the session-opening
  operating contract rather than stopping at public skill bodies.

## Reproduction

- `./charness version --json` emits YAML and `./charness --help` omits
  `--json`, while `python3 skills/public/quality/scripts/plan_quality_run.py
  --repo-root . --json` emits JSON syntax and the quality skill instructs that
  exact call. Removing `--json` changes quality to a human summary, proving the
  drift is on the skill-helper contract rather than the root CLI renderer.

## Candidate Causes

- The root YAML migration may have failed to reach some root CLI subcommands.
- Internal planner JSON may be intentionally out of scope, and only skill prose
  accidentally implies it is the same public structured-output contract.
- Public skill planners may have retained `--json` as a compatibility selector
  because no shared YAML/detail helper or migration acceptance test covered
  their agent-facing commands.

## Hypothesis

- The third cause is true: if the drift is the missing public-skill migration,
  root CLI tests/help will already prove YAML while skill bodies and planner
  parsers still advertise `--json`; migrating those calls to YAML/default or
  `--detail` will remove the contradiction without changing root CLI behavior.
  Disconfirmer: inspect the root help/tests and compare planner outputs with and
  without the flag.

## Verification

- confirmed — root CLI help and YAML parsing tests already enforce the migrated
  boundary; direct planner comparisons locate the residual vocabulary and mode
  selection in public skill helper surfaces.
- implemented — 164 focused tests passed after the final critique fixes,
  covering default/detail YAML, hidden real-JSON compatibility, help hiding,
  source/plugin public docs, and the missing-PyYAML fallback.

## Root Cause

The July 15 migration drew the ownership boundary at the `charness` executable.
Public skills remained a separate family of agent-facing command surfaces, and
their older `--json` detail selectors were neither included in acceptance nor
linked to the new YAML/default-plus-detail convention. Copyable skill commands
therefore preserved the old mental model after the root command changed.

## Invariant Proof

- Invariant: when a public skill produces a copyable structured-output command,
  the invoked helper must surface YAML/default-or-detail vocabulary before an
  agent can treat that instruction as current.
- Producer Proof: `rg --glob SKILL.md -- --json skills/public skills/support`
  identifies the copyable producers and their intended helper scripts.
- Final-Consumer Proof: this session executed the debug/handoff/retro planner
  commands exactly as written and exposed the mismatch to the operator.
- Interface-Shape Sibling Scan: planner bootstraps in debug, handoff, quality,
  release, retro, impl/spec, prove, setup, and create-skill plus downstream CLI
  guidance in create-cli and the repo-level Cautilus preflight instruction.
- Non-Claims: repo-internal test fixtures, third-party tools whose native API is
  JSON, and persisted `.json` artifacts are not output-vocabulary violations.

## Detection Gap

- Root CLI YAML tests | cover only `charness`, not copyable public-skill helper
  commands | add focused helper tests that parse the new YAML detail output and
  assert public `SKILL.md` files no longer teach `--json`.
- Skill validation | validates metadata/shape but not structured-output
  vocabulary | a narrow source assertion in the focused migration tests is
  enough; do not add a broad prose classifier.
- Boundary-bypass inventory | recognized `json.loads(stdout)` as behavior proof
  but not the equivalent `yaml.safe_load(stdout)` | teach the existing heuristic
  both structured-output parsers so a format migration does not inflate the
  keep-boundary count.
- Representative skill-contract checker | pinned the old risk-interrupt command
  as a required snippet | update its deterministic contract to require
  `--detail`, so the scenario gate enforces the migrated instruction.

## Sibling Search

- Mental model: changing the root executable changes every copyable command
  contract agents encounter.
- same layer: public planner bootstraps in debug/handoff/quality/release/retro | decision: same bug, fix now | proof: static scan plus direct output comparison
- abstraction up: impl/spec/prove/setup/create-skill structured evidence calls | decision: same bug, fix now | proof: `SKILL.md` scan and parser inspection
- specialization down: repo-internal tests and provider-native JSON flags | decision: intentional plain-text or non-rendering boundary | proof: not public Charness output surfaces
- mental-model siblings: create-cli guidance teaching `--json` to new CLIs | decision: same bug, fix now | proof: public skill contract inspection
- cross-file: skills/public/create-cli/SKILL.md and skills/public/quality/SKILL.md
- cross-file: AGENTS.md and skills/public/quality/references/cautilus-on-demand.md

## Seam Risk

- Interrupt ID: public-skill-yaml-output-drift
- Risk Class: contract-freeze-risk
- Seam: public skill instruction -> helper parser/output -> agent command use.
- Disproving Observation: a migrated helper still requires or advertises
  `--json`, or its YAML output cannot be parsed by the prescribed consumer.
- What Local Reasoning Cannot Prove: installed host caches consume the changed
  skill prose before a later update/release.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/debug/2026-07-18-residual-json-flags-after-yaml-migration.md

## Prevention

Implemented copyable public-skill helper calls as YAML/default or `--detail`,
kept legacy `--json` hidden with actual JSON output for parser compatibility,
updated the repo-level Cautilus preflight to `--detail`, updated tests and
create-cli policy, synced plugin exports, and limited the owned-command checks
so third-party/native JSON remains out of scope.

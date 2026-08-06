# Issue #518 Quality Declaration Reconciliation Debug
Date: 2026-08-07

## Problem

`quality` can receive a preset, adapter, or declared surface without proving
that the declaration reached an executable gate and the final quality verdict.
At the pinned `cmanki@aac5feca85afadc233da58201ad77e2135e712ec`, several
quality helpers returned a completed-looking result while scope or applicability
was incomplete.

## Correct Behavior

Given a declared preset, adapter field, product surface, or markdown surface,
quality must resolve it to an executable reader and record covered, unexamined,
unsupported, deferred, or failed status. When a declaration cannot be consumed,
the final quality result must expose an enforcement gap and must not present the
run as fully healthy.

## Observed Facts

- GitHub #518 is open, labeled `bug`, and its comments were read successfully.
- The causal reviewer confirmed the bug classification but returned `Causal review: substrate incomplete` before this artifact existed.
- Re-reading `cmanki` at commit `aac5feca...` preserved `preset_lineage` and
  produced a bootstrap conflict around coverage-floor paths rather than silently
  authorizing a rewrite (`scripts/quality_bootstrap_lib.py:222-234` is the local
  lineage merge seam).
- `craken-agents` provides a positive comparison: `package.json` is the exact
  gate source, `npm run quality` expands through named quality phases, hooks use
  smaller explicit gates, and every intentional skip has a removal condition
  (`/home/hwidong/codes/craken-agents/docs/code-quality.md:3-32,154-160`).

## Reproduction

- Created a temporary read-only archive from `/home/hwidong/codes/cmanki` at
  `aac5feca85afadc233da58201ad77e2135e712ec`; the source worktree stayed clean.
- Ran the five issue repro commands against that archive. All returned exit 0:
  `bootstrap_adapter.py` emitted `adapter_status: conflict` and named stale
  coverage-floor paths; `inventory_adapter_gate_design.py` emitted
  `findings: []` with a narrow default reviewed-path set;
  `run_dead_code_advisory.py` emitted `Primary (80%): clean (0 findings)` and
  `Sweep (60%): clean (0 findings)` on the TypeScript consumer;
  `inventory_skill_ergonomics.py` inspected only the configured support
  `SKILL.md` paths; and `inventory_entrypoint_docs_ergonomics.py` independently
  flagged `AGENTS.md` and long docs.
- Cheapest disconfirmers still required: run the same archive through the final quality report consumer and a fixture with a declared-but-unresolvable path; neither has yet been executed here, so no end-to-end green-verdict claim is made.

## Candidate Causes

- Preset lineage is treated as retained metadata instead of a reconciled,
  executable contract.
- Adapter declarations and consumer paths are inspected by separate helpers
  without one typed declaration-to-applicability-to-coverage record.
- Language- or scope-inapplicable helpers collapse to `clean` or empty output;
  the dead-code helper scans tracked Python paths and maps exit 0 to `clean`
  (`skills/public/quality/scripts/run_dead_code_advisory.py:41-51,234-242`).
- The skill inventory consumes `skill_ergonomics_skill_paths` as its input and
  does not join it to `canonical_markdown_surfaces`
  (`skills/public/quality/scripts/inventory_skill_ergonomics.py:138-171`).
- The final consumer can lack a required readiness/applicability fold even when
  producer helpers emit useful scope facts; this is the same status-propagation
  class previously recorded for #511.

## Hypothesis

Hypothesis: the structural cause is a missing typed contract from declaration to
final verdict: a declaration can be present, a producer can run, and a helper
can return zero findings without proving that the intended surface was
consumed.
disconfirmer: run a pinned consumer fixture with one declared but unreachable
surface and one language-inapplicable scan through the final quality artifact;
if both render as explicit gap/inapplicable states, this hypothesis is too
broad. This has not yet run, so no end-to-end green-verdict claim is made.
Source substrate: `skills/public/debug/references/disconfirmer-first.md` and
`skills/public/debug/references/five-whys-causal-chain.md`.

## Verification

still-candidate — the pinned five-command reproduction confirms concrete
declaration/scope symptoms, while final quality-artifact consumption and a
minimal cross-language fixture remain to be run before implementation.

## Root Cause

Candidate structural root cause: the quality control plane has no single
machine-readable lifecycle binding `declared intent → resolved reader →
applicability/scope → observed finding state → final verdict`. This permits
preserved-but-unreconciled presets, unreachable surfaces, and inapplicable
language scans to look like ordinary clean output. This is a candidate, not a
final root-cause claim, until the final-consumer reproduction is complete.

## Invariant Proof

- Invariant: when an adapter/preset producer emits declared scope or
  applicability, the final quality consumer must surface covered, unexamined,
  unsupported, deferred, or failed status before a healthy verdict.
- Producer Proof: the pinned `cmanki` archive produced the bootstrap conflict,
  clean TypeScript dead-code output, configured-skill-only inventory, and
  separate AGENTS detection described above.
- Final-Consumer Proof: not yet available; `quality:report` and a fixture fold
  have not been run against the pinned archive.
- Interface-Shape Sibling Scan: #507 (generated adapter lifecycle) and #511
  (default scope to advisory receipt) share declaration/producer/consumer status
  propagation; `craken-agents` is a positive comparison, not proof of Charness.
- Non-Claims: no current live provider, CI, installed plugin, or consumer
  runtime behavior is claimed. `cmanki` history is local evidence only.

## Detection Gap

- `quality_bootstrap_lib.py:222-234` | preset lineage is merged/preserved | add
  a reconciliation result that requires a reader and explicit unresolved gap.
- `inventory_adapter_gate_design.py:98-116` | adapter inspection can be empty
  for a defective declaration surface | assert inspected paths and applicable
  contract fields before returning clean.
- `run_dead_code_advisory.py:41-51,234-242` | a TypeScript repo can receive
  Python `clean` | return typed `inapplicable`/`unsupported` and make the final
  consumer refuse to fold it into healthy coverage.
- `inventory_skill_ergonomics.py:138-171` | configured skill paths are not
  joined to canonical markdown surfaces | test declared AGENTS/CLAUDE inputs
  and unreachable entries explicitly.
- `skills/public/quality/SKILL.md:98-107` | policy says unresolved gaps must be
  named, but the final artifact must enforce that status path | add a consumer
  assertion rather than only producer advice.

## Sibling Search

- Mental model: “a named surface is covered because a helper accepted its
  declaration or returned exit 0.”
- same layer: `scripts/quality_bootstrap_lib.py` and
  `skills/public/quality/scripts/inventory_adapter_gate_design.py` | decision:
  same class, diagnostic-only for this slice until final-consumer proof | proof:
  local payload proof.
- abstraction up: #511's scope-status-to-receipt path and #507's
  config-write authorization path | decision: same class, fix now in the
  unified declaration/evidence contract | proof: local debug artifacts.
- specialization down: `run_dead_code_advisory.py` and
  `inventory_skill_ergonomics.py` | decision: same bug, fix now if the final
  consumer reproduces the false-green fold | proof: pinned local payload.
- mental-model sibling: `/home/hwidong/codes/craken-agents/docs/code-quality.md`
  and `package.json` | decision: intentional positive comparison, not a Charness
  fix target | proof: static scan only.
- cross-file: quality bootstrap, adapter inventory, dead-code, skill ergonomics,
  #507/#511 artifacts, and the two sibling repositories above.

## Seam Risk

- Interrupt ID: issue-518-declaration-to-verdict
- Risk Class: external-seam
- Seam: consumer adapter/preset declaration → quality helper/adapter mirror →
  final quality artifact and operator verdict
- Disproving Observation: a pinned consumer fixture with an unreachable declared
  surface and an inapplicable scan is explicitly represented as a non-healthy
  status by the final artifact.
- What Local Reasoning Cannot Prove: final consumer behavior in every consumer,
  installed plugin projections, and provider/CI execution.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-07-issue-518-quality-declaration-reconciliation-contract.md

## Prevention

Make #518 a required first diagnostic/contract slice in the unified goal:
reproduce the pinned consumer history, bind every declaration to a resolved
reader and typed applicability/scope status, make unsupported/inapplicable/
unreachable states visible to the final quality artifact, and add consumer-fold
tests. Then apply the same contract to #515's surface routing and #514's
deterministic evidence assembly. Preserve #507 and #511 as regression fixtures;
do not call a producer-only clean result a repaired issue.

## Related Prior Incidents

- `charness-artifacts/debug/2026-08-05-debug-review-followup.md` (#507):
  generated adapter differences must not become implicit writes.
- `charness-artifacts/debug/2026-08-05-debug-review-followup-2.md` (#511):
  missing/default scope must not become a completed inventory.

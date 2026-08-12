# Issue 584 Planner Read Cost Implementation Debug
Date: 2026-08-13

## Problem

The shared run-plan envelope exposes required-read paths and rationale but no
measured local read size. The quality and handoff planners know their own path
bases, yet both emit the unmeasured shared shape.

## Correct Behavior

Representative quality (skill-relative) and handoff (repo- and skill-relative)
plans disclose each required local read as either a non-negative `size_bytes`
or an explicit typed unavailable state. The shared envelope validates a supplied
disclosure without trying to guess a planner's path base.

## Observed Facts

- `run_plan_envelope.read()` and `_validate_reads()` only model `path` and
  `why`; its generic layer has no safe root to resolve mixed planner paths.
- Quality catalog paths are relative to the quality skill root. Handoff mixes
  an adapter-resolved repository artifact with handoff-skill references.
- The default quality renderer also omitted any available structured cost fact.

## Reproduction

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`
  emits required reads without `size_bytes` or an unavailable disclosure.

## Candidate Causes

- The envelope was designed as prose-shaped metadata, not measured work.
- Generic resolution would conflate a planner's declared `base` semantics with
  a universal repository root.
- Existing tests treated a required read as a path set, so the final consumer
  could remain silent about a newly available measurement.

## Hypothesis

- Planner-owned resolution plus an additive shared disclosure validator fixes
  the representative paths without changing selection; disconfirmer: a mixed
  handoff fixture cannot measure both bases or report a missing path explicitly.

## Verification

- Result: confirmed by causal review of the shared envelope, quality catalog,
  handoff read builder, and human renderer.

## Root Cause

Read measurement was missing at the producer/consumer boundary, while the
generic envelope correctly lacked the context needed to resolve every planner's
relative paths.

## Invariant Proof

- Invariant: a representative planner-required local read reaches its consumer
  with measured bytes or a typed unavailable reason.
- Producer Proof: quality and handoff own their explicit skill/repo roots.
- Final-Consumer Proof: quality's human rendering must expose the disclosure;
  structured handoff YAML carries the same fields.
- Interface-Shape Sibling Scan: debug, retro, issue, and gather remain
  deliberately unmodified first-slice siblings.
- Non-Claims: no token estimate, total/limit, selection priority, or universal
  rollout is claimed.

## Detection Gap

- Shared envelope tests accepted unmeasured items and planner tests did not
  exercise actual file sizes or typed unavailable paths.

## Sibling Search

- Mental model: each planner owns path interpretation; the envelope owns only
  disclosure shape.
- planner base: quality and handoff | decision: implement representative slice
  | proof: source and plugin fixture plans.
- other planner: debug/retro/issue/gather | decision: defer widening | proof:
  static causal scan only.
- cross-file: quality human renderer | decision: include consumer visibility |
  proof: formatted output assertion.

## Seam Risk

- Interrupt ID: issue-584-read-cost-contract
- Risk Class: repeated-symptom
- Seam: planner-owned base resolution to shared envelope to agent consumer.
- Disproving Observation: a generic root can correctly interpret all bases.
- What Local Reasoning Cannot Prove: universal planner rollout.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/planner-required-read-cost-contract.md

## Prevention

Keep path resolution at the owning planner and test unavailable disclosures as
explicit states, never zero-byte substitutes.
Shared disclosure schema, quality and handoff producer paths, and source /
shipped-plugin fixtures passed 80 focused tests and Ruff. R1 repaired plugin
mixed-base proof and scoped acceptance language; R2 repaired symlink-loop
`RuntimeError` conversion to `stat-failed` under the verdict-logic two-round
accepted-unreviewed cap.

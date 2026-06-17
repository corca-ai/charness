# Debug Review
Date: 2026-06-17

## Problem

HOTL proving-surface staleness wording taught path-diff staleness as automatic
proof debt instead of a candidate signal requiring agent adjudication.

## Correct Behavior

Given a verified HOTL ledger entry with `proving_surface_refs`, when one of
those refs changed after the recorded proof baseline, then tooling may surface a
stale candidate but the agent must adjudicate whether it is actual proof debt
before requiring live reproof.

## Observed Facts

- Issue #382 reports a 2026-06-17 ceal issue-resolution session where
  close-loop/HOTL treated path-diff staleness as deterministic `needs_reproof`.
- `skills/public/hotl/SKILL.md:85-87` said a stale proving-surface ref
  "demands re-proof, narrower refs, or an explicit disposition".
- `skills/public/hotl/references/ledger-and-dispositions.md:38-47` said
  staleness is proof debt and unresolved staleness warnings block pre-live and
  completion audits.
- No HOTL regression test pinned the distinction between stale candidate,
  adjudication, and actual proof debt.

## Reproduction

Static contract reproduction:

```bash
rg -n "proving_surface_refs|Staleness|demands re-proof|proof debt" \
  skills/public/hotl plugins/charness/skills/hotl tests/quality_gates/test_hotl_adapter.py
```

Before the fix this finds deterministic reproof language in the public HOTL
skill and ledger reference, and matching exported plugin text.

## Candidate Causes

- The staleness section collapsed candidate detection and final disposition into
  one rule.
- The workflow bullet in `SKILL.md` optimized for proof safety but omitted the
  agent's semantic adjudication step.
- Tests covered adapter shape and bootstrap behavior, not HOTL proof-semantics
  vocabulary.

## Hypothesis

If HOTL names staleness as `stale_candidate` / `needs_adjudication`, enumerates
valid adjudication outcomes, and pins that wording in a focused test, then the
public skill will stop teaching path-diff-as-proof-debt while still blocking
unresolved proof risk.

## Verification

Planned focused verification:

```bash
python3 -m pytest -q tests/quality_gates/test_hotl_adapter.py
python3 scripts/validate_debug_artifact.py --repo-root .
python3 scripts/validate_skills.py --repo-root .
```

Full closeout will also run the repo slice closeout after plugin mirror sync.

## Root Cause

The structural cause was a missing distinction in the HOTL contract between
change detection and proof disposition. The skill encoded the safety outcome at
the detection boundary, so a broad path diff could be reported as proof debt
before semantic review. This maps to the debug five-whys substrate in
`skills/public/debug/references/five-whys-causal-chain.md`: the fixable bottom
is a missing contract plus missing test, not operator error.

## Invariant Proof

- Invariant: When HOTL tooling or an agent emits a staleness signal, the final
  HOTL closeout consumer must block unresolved adjudication without claiming
  every candidate requires reproof.
- Producer Proof: Static producer text existed at
  `skills/public/hotl/SKILL.md:85-87` and
  `skills/public/hotl/references/ledger-and-dispositions.md:38-47`.
- Final-Consumer Proof: The public skill and plugin mirror are the consumer
  surfaces loaded by future agents; focused tests will assert the final text
  contains adjudication vocabulary and excludes deterministic proof-debt wording.
- Interface-Shape Sibling Scan: Searched HOTL public source, plugin mirror, and
  nearby proof vocabulary with `rg`; sibling source is the plugin export mirror.
- Non-Claims: This fix does not prove or change any consuming repo's private
  HOTL ledger tooling, ceal-local guard, or live provider behavior.

## Detection Gap

- `tests/quality_gates/test_hotl_adapter.py` covered adapter validation and
  bootstrap, but no assertion covered HOTL staleness semantics. Smallest change:
  add a text-level regression test that rejects deterministic reproof wording
  and requires the candidate/adjudication vocabulary.
- Human review caught the issue before an upstream fix existed; automated
  detection should be a focused regression, not a broad new blocking floor.

## Sibling Search

- Mental model: a changed proving-surface path is enough to decide proof debt.
- same layer: `plugins/charness/skills/hotl/SKILL.md` and
  `plugins/charness/skills/hotl/references/ledger-and-dispositions.md` mirror
  the same public text | decision: same bug, fix now | proof: static scan only.
- abstraction up: proof-safety language can collapse signal, adjudication, and
  result in other proof workflows. `skills/public/quality/references/quality-signal-scorecard.md`
  mentions re-proof implications but does not assert path diffs are proof debt
  | decision: same class, diagnostic-only for this slice | proof: static scan
  only; no-action reason: it asks reviewers to consider re-proof, not to skip
  adjudication.
- specialization down: HOTL status vocabulary had final ledger statuses but no
  staleness-specific adjudication outcomes | decision: same bug, fix now |
  proof: static scan only.
- cross-file: `plugins/charness/skills/hotl/references/ledger-and-dispositions.md`
  is the exported sibling that must be synced after source edits.

## Seam Risk

- Interrupt ID: issue-382-hotl-staleness-adjudication
- Risk Class: none
- Seam: public skill export mirror
- Disproving Observation: plugin mirror sync and validation pass.
- What Local Reasoning Cannot Prove: downstream ceal behavior or live HOTL
  provider loops.
- Generalization Pressure: none
- Generalization Note: the policy was already factored into the public HOTL
  skill/reference in this slice, so no spec handoff remains.

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Add candidate/adjudication wording to HOTL, enumerate the allowed staleness
adjudications, sync the plugin mirror, and pin the contract with a focused HOTL
adapter test.

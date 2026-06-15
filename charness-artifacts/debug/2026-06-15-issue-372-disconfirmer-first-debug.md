# Issue 372 Disconfirmer-First Debug
Date: 2026-06-15

## Problem

Issue #372 reports a recurring diagnosis failure: agents state absence,
attribution, liveness, or frequency conclusions from narrow partial evidence,
then run the cheap disconfirming check only after the claim has already shaped
the diagnosis.

## Correct Behavior

Before a debug workflow states one of those claim types as confirmed, it should
name and run the single cheapest falsifier. Until then, the statement remains a
candidate claim. Runtime-state claims should prefer runtime probes over source
inference.

## Observed Facts

- The live issue names four claim classes: absence, attribution, liveness, and
  frequency.
- `skills/public/debug/SKILL.md` already required named-target runtime
  verification, but that rule was narrower than the issue: it fired only when a
  symptom blamed a specific named target.
- No `disconfirmer-first.md` reference existed under `skills/public/debug/references/`.
- `tests/quality_gates/test_debug_rca_reference_cite_chain.py` already guards
  important debug reference hooks, making it the closest deterministic test
  surface for this workflow rule.

## Reproduction

Before this slice, `rg -n "disconfirmer|cheapest falsifier|absence, attribution, liveness, or frequency" skills/public/debug tests/quality_gates/test_debug_rca_reference_cite_chain.py` found no general disconfirmer-first rung. The workflow could still satisfy the named-target rule while making an unproven absence or frequency claim.

## Candidate Causes

- The existing named-target verification rule solved one concrete runtime-name
  misread, but did not generalize to claim types.
- The RCA references emphasize structural-cause proof after a problem is framed,
  not the earlier moment where a candidate claim becomes a conclusion.
- No deterministic test pinned the trigger words or runtime-over-source
  preference, so a future edit could omit the rung without failing.

## Hypothesis

Adding a debug reference for disconfirmer-first claims, linking it from the core
debug workflow, and pinning the hook and required claim classes in the existing
debug reference tests will close the issue without expanding unrelated
diagnosis surfaces.

## Verification

- `pytest -q tests/quality_gates/test_debug_rca_reference_cite_chain.py` passed.
- `python3 scripts/validate_debug_artifact.py --repo-root . --report-all` passed.
- `python3 scripts/build_debug_seam_risk_index.py --repo-root . --check` passed.
- `python3 scripts/validate_skills.py --repo-root .` passed.
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --changed-skill-md skills/public/debug/SKILL.md --run-checks` passed.
- Fresh-eye critique found one issue-resolution cite-chain recurrence path; this was fixed by adding `disconfirmer-first.md` to `skills/public/issue/references/causal-review.md` and the focused test.

## Root Cause

The debug contract lacked a claim-type gate. It had runtime verification for
specific named targets, but no reusable rule saying that absence, attribution,
liveness, and frequency claims need their cheapest falsifier before being
promoted from candidate to confirmed.

## Invariant Proof

- Invariant: when a debug diagnosis asserts an absence, attribution, liveness,
  or frequency claim that would steer the next action, the workflow must record
  the candidate claim, cheapest falsifier, and result before treating it as
  confirmed.
- Producer proof: `skills/public/debug/references/disconfirmer-first.md` defines
  the claim triggers, probe preference, output fields, and over-reach boundary.
- Final-consumer proof: `skills/public/debug/SKILL.md` links the rung from the
  workflow step where correct behavior and assumptions are separated;
  `skills/public/issue/references/causal-review.md` includes the rung in the
  bug-class issue causal-review substrate; and
  `tests/quality_gates/test_debug_rca_reference_cite_chain.py` asserts those
  hooks and reference content.
- Non-claims: this slice does not prove every other public skill applies this
  diagnostic habit; it places the durable rule in debug, the substrate issue
  resolution already invokes for bug-class causal review.

## Detection Gap

The repo had tests for five-whys, invariant-first, and sibling-search reference
hooks, but no test that debug included a disconfirmer-first claim gate or that
the reference named the four trigger classes.

## Sibling Search

- same layer: `named-target-verification.md` is complementary, not a duplicate;
  it verifies concrete named targets while this slice gates claim classes.
- abstraction up: bug-class `issue resolve` consumes debug substrate through
  causal review, so the debug reference is the right shared home for RCA use.
  Fresh-eye critique caught that causal review also needed to name this new
  substrate explicitly; that cite-chain fix is bundled in this slice.
- specialization down: liveness/wired/running examples are covered by the
  runtime-over-source probe preference in the new reference.
- mental-model sibling: "one narrow source search is enough to conclude
  absence" is explicitly covered by the absence trigger and runtime/source
  preference.

## Seam Risk

- Interrupt ID: disconfirmer-first-372
- Risk Class: none
- Seam: diagnostic workflow instructions and debug reference tests
- Disproving Observation: if a future debug workflow omits the four claim types
  or cheapest-falsifier hook, the focused test fails
- What Local Reasoning Cannot Prove: that agents will always choose the best
  falsifier in live diagnosis; the rule instead makes the obligation explicit
  and auditable
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

Continue implementation. The fix is small, prompt-surface affecting, and needs
fresh-eye review before commit.

## Prevention

Keep the disconfirmer-first rule as a referenced debug rung and a focused
quality-gate test. If later slices find the same claim-type bug in another
workflow, route that workflow to debug substrate instead of duplicating a new
rule.

## Related Prior Incidents

- `2026-06-14-issue-365-agent-browser-orphan-ownership.md` — a liveness/ownership
  diagnosis where direct runtime observation disproved the convenient local
  model.

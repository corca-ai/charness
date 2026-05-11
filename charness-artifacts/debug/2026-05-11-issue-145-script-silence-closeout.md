# Issue 145 Script-Silence Closeout Debug
Date: 2026-05-11

## Problem

Issue #145 reports a cross-skill contract bug: scripts that return no-op,
benign, or already-present signals can be treated as closeout even when public
skill prose claims responsibility for a broader judgment area.

## Correct Behavior

Given a public skill delegates part of its workflow to a helper script, when the
script cannot measure the full prose-level contract, then its payload should
surface the unmeasured review boundary instead of silently implying healthy
closeout.

Given an existing generated block or adapter config is present, when the helper
detects drift or missing config, then it should distinguish matching,
drifted, missing, and intentionally empty states.

## Observed Facts

- `setup` rendered a canonical `Skill Routing` block with the unsafe
  "task-oriented sessions" qualifier, then returned `leave_as_is` whenever
  `## Skill Routing` existed.
- `quality` docs inventory counted outbound entrypoint signals but not inbound
  links, orphan docs, or top-level docs that may need an audience owner.
- `retro` auto-trigger checks returned `triggered: false` for absent trigger
  config without saying whether the absence was intentional.
- The causal-review subagent confirmed the concrete setup, quality, and retro
  sibling surfaces and recommended bundling those only.

## Reproduction

Before the fix:

```bash
python3 skills/public/setup/scripts/render_skill_routing.py --repo-root <repo-with-drifted-AGENTS> --json
python3 skills/public/quality/scripts/inventory_entrypoint_docs_ergonomics.py --repo-root <repo-with-docs-orphan> --json
python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root <repo-with-retro-adapter-missing-trigger-fields>
```

The setup helper reports no review action for a drifted block, the quality
helper has no inbound/audience fields to inspect, and the retro helper's
no-config payload is observationally identical to explicit opt-out.

## Candidate Causes

- Helper scripts may lack state classifications rich enough to represent prose
  contract boundaries.
- Public skill prose may overstate what helper scripts prove.
- Tests may assert only happy-path payload shape and miss false-negative
  distinctions.
- Existing no-op branches may have been optimized for non-destructive setup
  without preserving review signals.

## Hypothesis

If each reported helper emits explicit state for the contract boundary it owns,
then the agent can no longer treat script silence as complete closeout for the
reported surfaces.

## Verification

Focused regression tests were added and executed for:

- drifted existing `Skill Routing` blocks returning
  `review_existing_skill_routing`
- inbound doc links, top-level audience review, and unlinked top-level docs
- missing retro trigger config versus explicit empty opt-out

Executed proof:

- `pytest -q tests/quality_gates/test_setup_render_skill_routing.py tests/quality_gates/test_quality_entrypoint_docs_ergonomics.py tests/quality_gates/test_retro_auto_trigger.py` -> 11 passed
- `pytest -q tests/test_cautilus_scenarios.py::test_eval_cautilus_scenarios_writes_summary` -> 1 passed after updating the pinned setup wording
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py` -> 805 passed, 4 skipped
- surface validators for packaging, skills, public-skill dogfood, markdown links/lint, py_compile, ruff, and debug seam-risk index passed

## Root Cause

The helpers collapsed distinct states into one benign outcome:

1. Reported symptom: agents treated no-op helper output as closeout.
2. Why: setup, quality, and retro helpers emitted payloads that did not expose
   drifted block content, inbound docs/audience placement, or missing-vs-empty
   trigger config.
3. Why: the scripts were designed around producer-side safety and simple
   inventory shape rather than the public skill prose contract they support.
4. Why: regression tests covered existing output shape but not the false
   negative distinctions needed for closeout judgment.
5. Structural bottom: missing contract state in helper outputs plus missing
   regression tests for those state distinctions.

## Seam Risk

- Interrupt ID: issue-145-script-silence-closeout
- Risk Class: contract-freeze-risk
- Seam: public skill prose versus helper-script proof boundaries
- Disproving Observation: targeted tests fail if the three reported helper
  payloads collapse the newly separated states again
- What Local Reasoning Cannot Prove: whether every other public skill qualifier
  has an equivalent runnable false-negative path
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep helper outputs rich enough to distinguish source-of-truth rewrite status
from review status. Preserve focused tests for drifted generated blocks,
inbound/audience docs signals, and missing-versus-intentional trigger config.
Broader qualifier cleanup stays deferred until a concrete helper/prose
false-negative repeats.
Related prior incident: `charness-artifacts/debug/2026-04-23-auto-retro-missing-surfaces.md`.

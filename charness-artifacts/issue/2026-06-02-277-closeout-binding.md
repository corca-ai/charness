# Issue #277 Closeout Binding Carrier

Date: 2026-06-02
Repo: corca-ai/charness
Goal: `charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`

## Carrier Scope

Close:

- #277 goal-run issue closeout can miss auto-close carriers and over-satisfy
  bundled critique evidence.

## Close Comment

Resolved the #277 closeout binding bug.

JTBD: when a goal-run or bundled issue closeout claims a GitHub issue is
resolved, the carrier must prove the close keyword, classification ledger, and
resolution critique are bound to the selected issue instead of to a neighboring
issue or the bundle as a whole.

Classification: bug.

Root cause: issue closeout treated resolution critique as one carrier-level
field. Repeated `--number` selectors still checked the first usable
`Critique:` evidence globally, so a bundle could over-satisfy an issue whose
own critique evidence was missing or unrelated.

Debug artifact: charness-artifacts/issue/2026-06-02-277-closeout-binding.md.

Siblings: direct commit closeout verifier, draft closeout verifier, active-goal
close-intent cue, and handoff active-goal pickup filtering | decision: bundle
per-issue critique binding, stale doc/render sync, and active-goal cue/handoff
hardening; defer a deterministic `Issue closeout:` goal floor | proof:
fresh-eye causal review plus post-implementation critique in
`charness-artifacts/critique/2026-06-02-277-closeout-binding-resolution.md`.

Prevention: `issue_resolution_critique.py` parses issue-bound critique headers
outside code fences, keeps single-issue shorthand compatibility, requires
bundled carriers to bind every selected issue, and uses evidence basename or
content binding for each number. Regression tests cover the historical
unqualified-bundle failure, missing bundle evidence, artifact binding failures,
and fenced false positives.

Critique #277: charness-artifacts/critique/2026-06-02-277-closeout-binding-resolution.md

Close #277.

Evidence:

- Closeout verifier helper:
  `skills/public/issue/scripts/issue_resolution_critique.py`
- Source verifier:
  `skills/public/issue/scripts/issue_verify_closeout.py`
- Plugin export:
  `plugins/charness/skills/issue/scripts/issue_resolution_critique.py`
- Tests:
  `tests/quality_gates/test_issue_closeout_verifier_critique.py`
- Active goal:
  `charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`
- Resolution critique:
  `charness-artifacts/critique/2026-06-02-277-closeout-binding-resolution.md`
- Draft carrier proof:
  `issue_tool.py validate-closeout-draft --repo-root . --repo
  corca-ai/charness --number 277 --classification bug --carrier pr-body
  --body-file charness-artifacts/issue/2026-06-02-277-closeout-binding.md`
  passed.
- Slice closeout aggregate:
  `python3 scripts/run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review` passed.

## Non-Claims

- GitHub issue #277 is not claimed closed until the commit is pushed and
  `verify-closeout --expect-state CLOSED` passes.
- A broader deterministic goal-artifact floor for `Issue closeout:` cues is not
  implemented in this carrier.
- No release surface is part of this carrier.

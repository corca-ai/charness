# Session Retro
Date: 2026-07-09

## Mode

session

## Context

This retro covers the autonomous repo-improvement slice that resolved the local
#427 scorer proof-honesty bug and reconciled handoff/prompt-mutation policy
state. The user asked to solve all current problems autonomously; the run
bounded that to live actionable issues, stale handoff state, and provable local
quality risks.

## Evidence Summary

- Commits: `87963dab`, `9e97902f`, `2f988fff`.
- Focused scorer proof: `python3 -m pytest -q tests/test_score_prompt_mutation_survival.py` = 29 passed.
- #421 spot check: `python3 -m pytest -q tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view tests/quality_gates/test_mutation_baseline_abort.py` = 26 passed.
- Issue closeout draft: `issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 427 --classification bug --carrier direct-commit` returned `status: draft_verified`.
- Critique record: `charness-artifacts/critique/2026-07-09-critique-review.md`.
- Goal artifact: `charness-artifacts/goals/2026-07-09-autonomous-repo-improvement-issues.md`.

## Waste

The first fix was too narrow: it repaired stream prose matching but did not
initially inspect the primary trace-digest path. Fresh-eye causal review caught
that `trace-digest.jsonl` could also carry non-command `args` from tools like
Read or Task.

The second fix still left a split-brain rule: trace digest became Bash-only but
stream fallback accepted any tool with an `input.command` field. Code critique
caught this before closeout, and `2f988fff` bundled the missing Bash-name guard.

## Critical Decisions

- Treat #427 as a bug-class issue, not a feature, because it could fake baseline
  validity or `NO-OBSERVED-EFFECT`.
- Keep the fix at the scoring consumer rather than broadening the advisory
  blinding scanner; one surface is execution proof, the other is taint detection.
- Leave `prompt_mutation_bundle_lib.stream_command_blob` as valid-but-defer
  cleanup because survival scoring no longer imports it.

## Expert Counterfactuals

- John Ousterhout design lens: split helper names by semantics earlier. A broad
  "all tool input strings" helper should not be reused under an execution-proof
  name without a narrow wrapper.
- Gary Klein premortem lens: before the first patch, ask how the same false-fire
  class could still pass through another evidence channel. That would have found
  trace digest and non-Bash stream `input.command` in one pass.

## Sibling Search

- same layer: `score_prompt_mutation_survival_lib` trace + stream marker paths | decision: same waste, fix now | proof: new non-fire tests for prose, non-command input, non-Bash trace args, and non-Bash stream command fields | follow-up: n/a — bundled in commits `9e97902f` and `2f988fff`
- abstraction up: `prompt_mutation_bundle_lib.stream_command_blob` broad helper naming | decision: valid follow-up outside the slice | proof: scorer no longer imports it, but the name can mislead a future execution-proof consumer | follow-up: deferred prompt-mutation-helper-contract
- mental-model siblings: advisory blinding scanner | decision: intentional boundary | proof: `check_prompt_mutation_blinding.py` scans broadly for taint, not execution proof | follow-up: n/a — not a #427 blocker

## Next Improvements

- workflow: applied: bug-class issue closeout now runs fresh-eye causal review plus code critique before final carrier validation; this caught and fixed two same-class siblings.
- capability: applied: `trace_command_marker` scoring now requires Bash command-bearing evidence in both trace digest and stream fallback, with focused regression tests.
- memory: applied: `docs/prompt-mutation-policy.md` and `docs/handoff.md` record the Bash-only marker evidence rule and #427 push/verify boundary.
- capability: deferred prompt-mutation-helper-contract — rename or split `prompt_mutation_bundle_lib.stream_command_blob` when a future consumer needs execution-proof stream semantics.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-09-autonomous-repo-improvement-issues-retro.md

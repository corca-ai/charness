# WI-7: self-review phase plus landing review trigger

Goal #844 slice 7 of 14. Hard dependency: WI-1 (the `self_review` block extends the envelope). Integration gate: WI-8a (the landing-trigger half starts after the train lands; verified standalone with a stub fast-forward fixture).

## Objective

Add the fresh-eye review phase before a lane reports, default-on only for lanes touching an irreversible boundary (provider close, publish/push, external writes, proof-surface/verdict-logic edits, uncertain deletions) and cheap opt-in elsewhere, with findings as fixed, deferred, or disputed. An unavailable reviewer skips cleanly and the skip is recorded as a non-claim, never as review-passed. Every fast-forward additionally starts a non-blocking fresh-eye review of the landed range: P1s go to the next unit, P2/P3 batch.

## Touchpoints

- `scripts/task_run/task_run_execution.py`: self-review phase orchestration plus unavailable-skip.
- `scripts/task_run/task_run_state.py`, `scripts/task_run/task_run_completion.py`: `self_review` block (fixed/deferred/disputed).
- Train landing path (WI-8a seam): fast-forward review trigger.
- New `tests/charness_cli/test_task_run_self_review.py`: disposition mapping, clean-skip-with-reason, stub fast-forward trigger cases.

## Acceptance

- The result YAML carries a `self_review` block listing findings as fixed, deferred, or disputed (#839).
- The phase skips cleanly when the reviewer executor is unavailable, and the result says so as a non-claim (#839).
- Every fast-forward starts a non-blocking fresh-eye review; P1 goes to the next unit, P2/P3 batch (#843-12).

## Out of scope

No post-integration review changes; no reviewer CLI changes; no metrics on findings (WI-10a). Default-on never extends beyond irreversible-boundary lanes without a new briefing decision.

<!-- charness-work-item-key: wi-7-review -->

#387 is resolved.

Classification: deferred-work
Manual Fallback Reason: auto-close-failed-after-remote-verification
Critique: charness-artifacts/critique/2026-06-24-issue-387-closeout.md

JTBD: make achieve goal closeout evidence repair one-pass instead of forcing operators through repeated complete-flip validator failures.
Boundary: closeout authoring affordance only; `check_goal_artifact.py` remains the authoritative complete-flip validator, and no validator strictness is weakened.
Resolution brief: inline (no pause) — ship a goal-conditional describe mode that reads the in-progress goal and projects the live closeout/timebox reports into a missing/satisfied floor list with accepted forms.
Implementation: `describe_goal_closeout_shape.py --goal-path <artifact>` now emits only the floors that goal triggers, shows which are missing or satisfied, appends the live form reference, and the achieve After-phase points authors to that command before flipping to complete.
Prevention: focused tests cover the missing/satisfied split, grandfathered omission, runtime-conditional floors, render behavior, and static catalog backward compatibility; the remaining recurrence risk is future floor additions, covered by the floor-addition advisory/test discipline.
Behavior #387: verified via distinct local evidence — focused pytest for `tests/quality_gates/test_describe_goal_closeout_shape.py`, fresh-eye smoke of `--goal-path`, and direct source/docs inspection; this is not inferred from GitHub state.
AI-provenance: agent-authored closeout comment, with bounded fresh-eye critique recorded in `charness-artifacts/critique/2026-06-24-issue-387-closeout.md`.

Evidence:
- Fix commit on `origin/main`: `e6d1a59a Make achieve closeout describe goal-conditional (A2)`.
- Follow-up coverage commit on `origin/main`: `49748a25 Cover the changed-line edge branches of A2 + the floor-addition nudge`.
- Local verification in this closeout session: `python3 -m pytest -q tests/quality_gates/test_describe_goal_closeout_shape.py tests/quality_gates/test_goal_disposition_gate.py` passed with `53 passed`.
- Fresh-eye reviewer independently ran focused describe tests (`9 passed`) and smoke-ran `--goal-path` against a temp goal.

Manual close is used because the resolving commits were already pushed without an auto-close keyword; the fix is present on `origin/main` and this comment supplies the missing issue-resolution carrier.

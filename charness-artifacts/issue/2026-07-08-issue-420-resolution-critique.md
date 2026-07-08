# Resolution Critique — corca-ai/charness#420 close (2026-07-08)

Bounded fresh-eye reviewer (parent-delegated, high-leverage tier), recurrence
focus: "what would let a repo-wide quantity gate's hard-block posture punish a
legitimate slice shape again, or the advisory demotion silently lose the
signal entirely."

Decision artifact: issue #420 + landed commit `6415175b` + close comment
draft. Reviewer verified empirically: focused pytest 8/8; `run-quality.sh:505`
runs `check_test_production_ratio.py --advisory`;
`check_test_production_ratio.py:203-214` prints `WARN (advisory)` and returns
0 on the advisory path; `git show 6415175b` matches the described diff.

## Act Before Ship

none

## Bundle Anyway

- Close-comment wording overclaimed that the live test pins the gate's
  advisory posture; the live test pins script-level behavior only — nothing
  pins the `--advisory` flag in `run-quality.sh:505`. Folded: comment now says
  the posture is recorded in `run-quality.sh:505` and only script behavior is
  test-pinned.

## Valid but Defer

- No gate pins the `--advisory` flag itself; silently dropping it restores the
  hard-block posture with no test failing. Deferred per floor-addition
  restraint (add only on recurrence). Recorded in the close comment.

## Over-Worry

- "Advisory demotion loses the signal entirely" — dismissed: the WARN line
  still renders, and the bare-CLI exit-1-over-max lane is unchanged by design.
- "Synthetic rc-0 fixture masks real-repo regressions" — dismissed: the
  fixture tests the script's branch behavior; live degenerate-zero checks
  remain.

Fresh-Eye Satisfaction: parent-delegated
Reviewer tier: high-leverage requested; host default reviewer model spawn
(no per-spawn tier fields exposed to confirm application).

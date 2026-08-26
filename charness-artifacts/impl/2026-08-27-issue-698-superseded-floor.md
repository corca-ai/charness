# Implementation Contract: Issue #698

Date: 2026-08-27 Asia/Seoul

## Current Slice

Close the Charness-owned lifecycle boundary for `superseded`: preserve the
existing `Superseded by:` handoff identity and prevent a bound retro's surfaced
improvements from disappearing. Keep the non-complete status distinct from
`complete` and do not import complete-only closeout friction.

## Fixed Decisions

- `Superseded by:` remains the required handoff/remainder record, including an
  explicit `none — <reason>` abandonment form.
- A superseded artifact must carry `Retro:` evidence or an allowed typed skip.
  A skip is surfaced as an explicit non-claim that retro contents and surfaced
  improvements were not verified.
- When the bound retro has `## Next Improvements`, the existing deterministic
  `## Auto-Retro` disposition rungs apply. The complete-only host-log,
  disposition-review, coordination, and other After-phase floors do not apply.
- Both `check_goal_artifact.py` and the status writer enforce the same smaller
  floor; a refused writer transition leaves the artifact's status unchanged.
- `skills/public/` is canonical. The checked-in `plugins/charness/` mirror is
  synchronized for the changed achieve scripts and reference.
- No hosted enforcement, release, push, installed-host claim, or issue closure
  is part of this slice.
- Per user direction, no forced fresh-eye review, handoff update, or micro-slice
  ceremony is claimed.

## Acceptance Checks

1. A superseded goal with a bound improving retro and an applied disposition is
   accepted by the production checker.
2. A superseded goal with a bound improving retro and a blank Auto-Retro is
   refused by the production checker with an actionable disposition reason.
3. The status writer refuses the same undispositioned transition before writing
   and preserves `Status: active`.
4. A valid explicit retro skip passes only as a recorded non-claim.
5. Existing successor-pointer and terminal-readiness behavior remains green.
6. Canonical source and checked-in plugin mirror remain byte-identical for every
   changed mirrored surface.

## Owned Surface

- `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
- `skills/public/achieve/scripts/goal_artifact_superseded.py`
- `skills/public/achieve/scripts/goal_artifact_lib.py`
- `skills/public/achieve/scripts/check_goal_artifact.py`
- `skills/public/achieve/references/goal-artifact.md`
- matching `plugins/charness/skills/achieve/` mirrors
- `docs/prescribed-skill-closeout-contract.md`
- `tests/quality_gates/test_goal_superseded_status.py`
- this implementation artifact and the evidence-led debug artifact

## Verification Ledger

- Baseline executable reproduction: superseded with an improving retro and
  unresolved Auto-Retro returned `ok: true` before the repair; receipt:
  `charness-artifacts/debug/receipts/issue-698-superseded-bypass.json`.
- Focused standing gate:
  `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_superseded_status.py`
  — 43 passed.
- Related standing gates: `test_goal_artifact_lib.py` — 33 passed;
  `test_goal_disposition_gate.py` — 50 passed;
  `test_disposition_form_floor.py` — 65 passed;
  `test_goal_coordination_floors.py` — 73 passed.
- Documentation composite gate: `bash scripts/check-docs.sh` — pass; existing
  inline-code advisories remain non-blocking.
- Python length gate: changed files pass; `goal_artifact_lib.py` remains at
  359 code lines in the advisory band, so the new superseded logic stays in its
  cohesive owner module rather than increasing that file.
- Cache isolation: `PYTHONPYCACHEPREFIX` and pytest `cache_dir` were directed
  outside the worktree; no `__pycache__` or `.pytest_cache` remains here.
- Source/plugin parity: checker, closeout evidence, library, superseded helper,
  and goal-artifact reference comparisons all pass.
- Commit sequence: `5ff5769f5f9af10da6e3174486721ddac2e300ca` implemented the
  floor; `9e3aa04050169a58b6933ec62038996c83ef0ac5` covered refusal categories;
  `90345b46a546f062b371b4fb5692e5500edf098f` covered the create-success path.
- Changed-line proof worktree: `/tmp/charness-698-proof-20260827`, named branch
  `proof/issue-698-superseded-floor-20260827`, clean and non-detached.
- Changed-line proof scope: base
  `5345a5a467e1b2723fa072d9fe270007123014a1`, target
  `90345b46a546f062b371b4fb5692e5500edf098f`, explicit changed-path set from
  that range, four mapped implementation files, zero unmapped and zero
  blocking lines, consumer exit 0. Proof coverage and pytest caches were
  outside the worktree.
- The first two proof attempts blocked on real uncovered branches; those branches
  were covered by tests before the final proof passed. Issue closeout and Goal
  Run advancement remain separate operations.

## Non-Claims

This local proof does not establish fresh-eye approval, host/provider
roundtrip, installed export behavior beyond the checked-in mirror, remote CI,
issue closure, release, push, or consumer-repository migration. A valid retro
skip does not claim that retro contents or surfaced improvements were reviewed.

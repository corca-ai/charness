# Issue #503 — local closeout carrier

Date: 2026-08-04
Status: locally closed; remote issue remains open and out of scope
Issue: https://github.com/corca-ai/charness/issues/503

## Closeout scope

This is a local proof carrier for the #503 goal track. It does not close or
modify the remote GitHub issue, and it makes no claim about remote CI, release,
cross-repo telemetry, or future runtime relief.

## Selected cohort and owner

- Cohort: exact `phase=verify` plus command
  `pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py`
  in `gate_runtime.over_budget`, from the current readable
  `.charness/usage-episodes/closeout_telemetry.jsonl` stream.
- Population: 1,326 retained schema-1 closeout records from
  `2026-06-13T11:33:19Z` through `2026-08-04T01:16:44Z`; live replay status
  counts are 949 `completed`, 248 `failed`, and 129 `blocked`. Rotation and
  lost history remain unknown.
- Cohort: 16 matching entries in the window
  `2026-06-13T11:57:31Z` through `2026-06-15T21:54:08Z`; 12 parent records were
  `completed` and 4 were `failed`. These are not 16 successful suite runs.
- Metric: 16 finite elapsed observations, total 6,257.15s, median 447.03s,
  peak 475.46s, 120.0s budget, and 4,337.15s paired excess.
- Decision owner: Charness quality/achieve maintainer operating this goal;
  the detail miner remains the derivation producer, not the owner of the
  optimization decision.

## Action and preservation

Selected action is an opt-in `--detail` operator receipt in the existing
retro miner. It audits the readable schema-1 population, preserves exact
cohort and parent-record identity, rejects non-finite elapsed values, keeps
elapsed/budget pairs aligned, and states retention/provenance/unit
non-claims. Default miner output, telemetry schema, gate behavior, CI
placement, and proof scope are unchanged.

The operator runs:

    python3 skills/public/retro/scripts/mine_closeout_telemetry.py --repo-root . --detail

and records retain, a named bounded proof-preserving experiment, or an
evidence-backed no-safe-change result. The receipt itself records no runtime
relief: measured relief is 0 seconds until a later comparable window proves
otherwise.

## Residuals and reopen trigger

- No runner/profile/run identity, command exit status, or suite pass/fail
  identity exists in the stream; none is inferred.
- The separate `over_slice` signal remains occurrences/trailing-run length,
  not gate seconds.
- No named lower-layer seam and separate correctness channel currently justify
  an optimization experiment.
- Reopen the decision after a later current-readable retained window has at
  least two occurrences (`recur_min >= 2`) of the same exact phase/command
  key. Recurrence alone never authorizes weakening, skipping, rescheduling, or
  moving proof.

## Exact changed paths

- `skills/public/retro/scripts/mine_closeout_telemetry.py`
- `plugins/charness/skills/retro/scripts/mine_closeout_telemetry.py`
- `skills/public/retro/references/closeout-telemetry.md`
- `plugins/charness/skills/retro/references/closeout-telemetry.md`
- `tests/quality_gates/test_retro_closeout_telemetry_mining.py`
- `docs/public-skill-dogfood.json`
- `charness-artifacts/issue/2026-08-04-issue-503-slice-a-cohort.md`
- `charness-artifacts/issue/2026-08-04-issue-503-slice-b-decision.md`
- `charness-artifacts/issue/2026-08-04-issue-503-local-closeout.md`
- `charness-artifacts/critique/2026-08-04-slice-b-503-metric-report-code-critique.md`
- `charness-artifacts/critique/2026-08-04-slice-b-metric-report-final-packet.json`
- `charness-artifacts/critique/2026-08-04-slice-b-metric-report-final-packet.md`
- `charness-artifacts/gather/2026-08-04-issue-503-closeout-cost.md`
- `charness-artifacts/gather/latest.md`
- `charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`

## Verification and non-claims

- Focused telemetry-miner standing pytest: 15 passed.
- Pre-lock `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`:
  completed all deterministic checks; broad pytest is intentionally deferred
  to the final verification lock.
- `check_dup_ratchet.py --summary`: clean, zero new fixable-eligible families.
- Source/plugin miner bytes are identical; the real local detail replay
  reproduces the selected cohort and finite paired summary.
- The bounded critique found and repaired the report's semantic blockers; the
  repository's second-round cap records those repairs as accepted-unreviewed,
  with final broad proof still required.
- No predicate recommendation is made for #496. #496 remains an independent
  reproduction and repair track.
- Remote issue closure is not claimed or requested by this carrier.

## Fresh-observer acceptance

Accepted by delegated fresh-eye reviewer Boole
(`019fca59-f76c-7c10-8664-9e9a16920138`) after a repair read. The reviewer
confirmed the live 1,326-record snapshot and unchanged 16-entry cohort,
accepted the owner/action/preservation/residuals/changed-path claims, and
found no remaining blocker. Boundary verification for the review window is
recorded by
`.charness/reviewer-boundary/issue-503-local-closeout-before.json` with
`verdict: parent-attributed` and `drift: []`.

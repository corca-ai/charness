# Lesson-Evaluation Observability Closeout
Date: 2026-08-13

## Implemented

- A repo-local lesson-session opener that declares the existing deterministic
  snapshot, completes and flushes exact stdout bytes, and writes a subordinate
  receipt only after that write boundary succeeds.
- An exact Charness retro disposition grammar with affirmative `no-effect` and
  distinct `missing-start`, `emission-unproven`, and
  `presentation-unproven` states.
- A read-only continuity reporter and Charness quality-gate entry that reconcile
  eligible durable retros, sessions, receipts, and score events.
- Generic public-retro adapter seams for artifact sections and metric commands;
  Charness-specific grammar remains in `.agents/retro-adapter.yaml` and
  `docs/development.md`.

## Capability Delivered

From 2026-08-14 onward, every dated root-level durable retro in the defined
cohort must carry one typed lesson-evaluation disposition. The report can expose
a skipped start, invalid emission receipt, uncertain presentation, duplicate
session use, score mismatch, or overdue unclaimed emission without treating
more scores as healthier behavior.

This is durable-retro continuity only. It does not observe every host chat and
does not prove that emitted lessons were displayed, read, used, beneficial, or
opened before the affected work.

## Contract Source

`charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md`

## Verification

- `python3 -m pytest -q tests/test_lesson_evaluation_continuity.py tests/test_lesson_evaluation_contract_boundaries.py tests/test_retro_plan.py tests/test_retro_scaffold.py tests/quality_gates/test_quality_runner.py`
  — 146 passed after the claims-review and changed-line repairs.
- `python3 scripts/validate_retro_artifact.py --repo-root . --paths charness-artifacts/retro/2026-08-13-session-retro.md`
  — passed with the honest pre-activation `missing-start` disposition.
- `python3 scripts/check_lesson_evaluation_continuity.py --repo-root . --as-of 2026-08-13 --json`
  — activation-eve baseline: 0 eligible durable retros, 0 dispositions, 6
  historical score events, 0 violations. This is not future-operation proof.
- `python3 scripts/run_slice_closeout.py --repo-root . --base origin/main
  --verification-lock --produce-mutation-coverage
  --ack-cautilus-skill-review` — completed; its committed-range changed-line
  consumer passed after boundary and CLI coverage was added. A manual mutation
  of the listed `scripts/open_lesson_session.py:37` error type made the bound
  invalid-write test fail and was reverted before the passing run.
- Cautilus was not run because evaluator execution is ask-before-run and no
  phase-scoped grant was given.

## Lint Gate

Lint Gate: ran-pass `bash .githooks/pre-commit` — producer-reported because the
hook emits no success output; the terminal run follows all claims-review repairs.

## Truth Surface Sync

`docs/development.md` owns the exact local procedure and forms;
`docs/handoff.md` links the continuity contract and orders the first real
session before #614; `charness-artifacts/retro/2026-08-13-session-retro.md`
records why reminders alone failed and why this work has no retroactive score.
Checked-in plugin exports mirror the canonical scripts and public retro assets.

## Boundary Ownership

Boundary Ownership: moved-to-owner — the ledger owns immutable session identity,
the receipt owns bounded stdout-write evidence, the retro author owns the human
disposition, the reporter owns the derived verdict, and the Charness adapter
owns repository-specific grammar.

## Critique

Critique: full
`charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-implementation.md`.
Round 1 repaired short-write, state-space, quality-registration, and evidence
claims. Round 2 caught Charness policy leaking into the public scaffold; the
ownership repair is explicitly accepted-unreviewed under the two-round cap.

The separate closeout claims review re-derived the then-current 102 focused
tests and activation-eve baseline, then blocked completion because the promised
one-line human summary and several acceptance fixtures were absent. The repair
now emits one aggregate line followed only by typed violation detail and adds
CLI exit/JSON, reverse date disagreement, missing/foreign/mismatch/invalid
receipt, and many-score-versus-zero-score assertions. The aggregate human and
JSON views include stable zero-or-more counts for score mismatch, duplicate
session reference, and unclaimed emission. This is a claims-review repair, not
a claimed third code-review round. The final claims readback independently
reran 106 focused tests, matched canonical/exported reporters, and accepted the
repaired closeout assertions with no remaining blocker.

The first post-commit changed-line run then rejected uncovered validation and
CLI branches in the three new repo-local scripts. Boundary, receipt, reporter,
and entrypoint tests were added and split into a cohesive contract-boundary
module to stay below the test-file length ceiling. The terminal producer then
passed the committed-range changed-line consumer. These test-only repairs are
accepted-unreviewed under the two-round code-review cap.

Fresh-eye pass: scripts/check_lesson_evaluation_continuity.py — proof surface;
rounds 1 and 2 inspected its verdict boundary, and the capped claims repairs
add only contract-promised aggregate rendering/fixtures without a third code
approval claim.

Fresh-eye pass: scripts/lesson_evaluation_continuity_lib.py — proof surface;
rounds 1 and 2 found and repaired false-clean state, receipt, identity, and
ownership paths; later claims repairs remain accepted-unreviewed under the cap.

Fresh-eye pass: scripts/open_lesson_session.py — not a proof surface; it
produces a bounded declaration/receipt and no verdict about other code or
artifacts. Round 1 still reviewed its write/flush and unsafe-ID behavior.

## Contract Updates

The living contract now fixes the 1:1 session-to-retro relation, shared observed
date, exact status/receipt/score truth table, byte-level receipt non-claims, and
compact human/JSON report shape. Its only report-layout probe is resolved.

## Residual Risks

- The first eligible cohort does not exist until 2026-08-14, so continued
  operation remains future evidence rather than a closeout fact.
- Meaningful host work with no durable retro remains outside the denominator.
- The receipt detects consistency and accidental edits, not authenticity or
  human exposure.

## Next Slice

Before #614, run the documented opener, actually present the selected list,
retain its session ID through one retro disposition, and run the continuity
report after persistence. Do not add a score unless an anchored effect occurred.

## Completion Categories

- durable: contract, implementation, tests, critique, retro, development guide,
  and handoff are repository artifacts.
- test-only: seeded failure matrices and CLI snapshots exercise the lifecycle;
  they are not a claim about future sessions.
- verification: provider level `agent_choice` for deterministic local commands;
  no provider roundtrip or evaluator run is claimed.
- external-writes: none.
- unverified-future: first post-activation session operation and any host-chat
  denominator.

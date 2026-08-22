# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn — the REPO'S OWN copy, never the installed one:
  the installed-copy declare wrote a receipt without a ledger event, the half-written
  state the continuity gate then refuses (`unknown session` on every score).
- Then run `## Next Session` item 1.

## Continuation Capability

- The [tracker requalification packet](../charness-artifacts/issues/2026-08-22-tracker-requalification.md)
  holds the per-issue probe commands, the controls that prove each defect path was
  entered, and the stated evidence gap per issue.
- The [closeout critique](../charness-artifacts/critique/2026-08-22-issue-closeout-critique.md)
  holds both review rounds, the mutant that survived three tests, and the rung-2
  judgment on the typed probe-record dispositions.
- The [recent-lessons digest](../charness-artifacts/retro/recent-lessons.md) holds
  the session-start recurrence traps and parallel/timeout discipline.

## Current State

- Fourteen issues were closed at `b9cea1829` after a behavioral sweep requalified
  sixteen against the installed plugin (`charness version`) and source: #635, #638, #639, #670, #672, #676,
  #677, #678, #679, #681, #682, #683, #685, #686. Counted, not estimated —
  population: 16 probed; removed: 14 closed.
- **A probe that does not enter the defect branch proves nothing about it.** The
  predecessor packet cleared #681 from a checker run against a goal artifact with no
  `Gate cadence:` bullet, on a goal since gone `complete` where the floor skips
  outright. #681 was still live on the installed plugin and on source, and is repaired at
  `b9cea1829`.
- The ten `repair/issue-*` branches in `git worktree list` are **stale predecessors,
  not pending work**. Every target file and test already exists on `main` in an
  evolved form, and `repair/issue-635` cherry-picks as an empty diff. Do not re-land
  them; the worktrees can be pruned.
- Held open deliberately: **#671** (the issue named two invariants; no critique angle
  file mentions path portability and `Path portability disposition:` appears in no
  shipped markdown) and **#688** (reproduced from none of six constructed bullet
  shapes; a comment asking for the verbatim source bullet is posted).
- Three residuals were filed rather than folded in: **#692** (`init_adapter.py` idempotence is wired into only one of the skills
  that ship the script; recount with
  `find skills -name init_adapter.py | xargs grep -l existing_adapter_is_valid | wc -l`
  against `find skills -name init_adapter.py | wc -l`), **#693**
  (`critique/SKILL.md:114` claims a refusal no code implements), **#694** (the
  gate-cadence floor reads a negated or two-clause flag mention as a deferral and
  refuses a truthful artifact).
- Two bounded review rounds ran on the #681 repair and the cap is consumed. Round 2
  predicted a mutant that survives all three new tests; it was executed, survived,
  and now fails after a positive pin. Round-2 repairs are otherwise recorded as
  accepted-unreviewed under the cap.
- **A subagent violated its read-only instruction** (detail and restore evidence in
  the [closeout retro](../charness-artifacts/retro/2026-08-22-tracker-closeout-retro.md))
  and reverted
  the [session-start lesson context](../scripts/session_start_lesson_context.py)
  module in the shared tree, dropping its unclaimed-session routing emitter. Restored from `HEAD`,
  byte-verified, re-covered by tests; the issue whose surface it touched was
  re-probed by the parent. Attribution is inferred from content match with
  `73cf9ce6a^`, not proven. **Verify the staged set before every commit in a
  concurrent-subagent session** — that is what caught it.
- The `#681` repair shipped in `6.2.2` and is **confirmed on the installed
  copy**: after `charness update`, the reproduction fixture returns the repaired
  payload citing the parsed line, and the scaffold's own seeded frame still
  refuses correctly with the disambiguator first. Evidence:
  [installed replay](../charness-artifacts/probe/2026-08-22-v6.2.2-installed-681-replay.json).
- #687's host-side terminal event remains explicitly unproven. Cautilus was not run.

## Next Session

1. **`6.3.0` is NOT published, and this is the first thing to know.** `6.2.2` is
   still the published version. Slices C, B and A are committed on `main`; the
   release was prepared four times and dropped four times, because four claims
   rounds all returned `unproven`. No tag, nothing pushed, no issue closed.
   Read [the v6.3.0 claims narrative](../charness-artifacts/release-review/2026-08-22-v6.3.0-prepared-claims-review.md)
   before touching the release — it holds all four rounds.
2. **Fix #701 before attempting the release again.** Not one of the ~14 claims
   blockers was in the shipped code: every round confirmed the quality-status
   owner mechanism, all five version surfaces and every derived figure. Every
   blocker was prose ABOUT the review, in artifacts that ship inside the bundle
   being reviewed — a loop with no fixed point. The predecessor's own durable
   claims record, added to satisfy a round-3 finding, landed inside the prepared
   commit and made a `pass` structurally unpublishable
   (`publish_release_claims_review.py:258-278` wants the narrative ADDED by the
   evidence commit). Continue from
   [the successor goal](../charness-artifacts/goals/2026-08-22-claims-review-convergence-then-ship-6-3-0.md),
   which fixes the loop first and publishes second, in that order and for that
   reason.
3. **Reproduce before repairing a review finding.** Twelve of twenty-seven
   blockers this run got a wrong first repair, and in two more the reviewer's own
   proposed fix was wrong. Repairing prose by re-reading prose is what failed;
   the one repair that held was derived from `git log` / `git show`.
4. #694 is decided and implemented (decline an ambiguous line, do not block
   activation), but stays open on a second blind shape: a deferral flag named
   only for a terminal step, with no earlier deferral, still reads as a deferral.
5. Do not run a third review round on the `#681` repair; the two-round cap is
   consumed and the round-2 repairs are recorded as accepted-unreviewed.
6. For a new work unit, run the repo-owned opener before any review or brief —
   `python3 scripts/open_lesson_session.py --repo-root . --session-id <slug> --seed <slug>`
   — and preserve the commit -> changed-line -> broad-quality ordering.
5. Do not claim a verdict from timeout, exit code, transcript, screen output, HTTP
   reachability, tag presence, or any other media alone; the
   [consumer report](../skills/shared/scripts/reviewer_worker_report.py) must accept a
   typed receipt with matching provenance and terminal state.

## Discuss

- **This bullet IS an SC14 anchor — do not tidy it away.** The
  [dominance test](../tests/quality_gates/test_command_dominance.py) substitutes into the
  real handoff and needs the bare backticked `python3 scripts/run_standing_pytest.py`, with no flags inside
  the backticks, present here.

## References

- The [design north star](./design-north-star.md) holds the different-observer rule and
  the proof-surface reading of the irreversible boundary.
- The [operating contract](./conventions/operating-contract.md) holds the two-round
  critique floor and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) holds the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
- [Validator timing layers](./conventions/validator-timing-layers.md) holds which gate runs
  at which boundary and why.

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

- Fourteen issues closed at `b9cea1829` (16 probed, 14 closed) — the per-issue
  probes and the requalification are in the
  [tracker packet](../charness-artifacts/issues/2026-08-22-tracker-requalification.md) (probe commands, evidence gaps).
- **A probe that does not enter the defect branch proves nothing about it.** That
  is how #681 was cleared while still live on the installed plugin.
- The `repair/issue-*` worktrees (`git worktree list`) are **stale
  predecessors, not pending work** — `repair/issue-635` cherry-picks as an
  empty diff. Prune, do not re-land.
- Held open deliberately: **#671** (second invariant unmet) and **#688** (not
  reproduced from six constructed shapes; awaiting the verbatim source bullet).
- Residuals filed rather than folded: **#692**, **#693**, **#694** (decided and
  implemented this session; still open on a second blind shape).
- The #681 repair's two review rounds are consumed; round-2 repairs are
  accepted-unreviewed under the cap.
- **A subagent violated its read-only instruction** and reverted a module in the
  shared tree; restored and re-covered. Forensics in the
  [closeout retro](../charness-artifacts/retro/2026-08-22-tracker-closeout-retro.md) (restore evidence, attribution caveat).
  **Verify the staged set before every commit in a concurrent-subagent session** —
  that is what caught it.
- The #681 repair is confirmed on the installed copy by the
  [installed replay](../charness-artifacts/probe/2026-08-22-v6.2.2-installed-681-replay.json) probe record.
- #687's host-side terminal event remains explicitly unproven. Cautilus was not run.

## Next Session

1. **`check-artifact-referents` is new and it reads what you are about to
   write.** Between the existing form floor and fresh-eye review it adds a
   REFERENT rung: `issue #N`, an `applied:` naming a path that does not exist,
   and an unresolvable SHA are all refused. `{{q:<id>=<value>}}` markers make a
   restated count agree with itself. Two edges: it can exit **3**
   (`UNESTABLISHED`) when git cannot resolve SHAs — that is "ran, established
   nothing", not a pass — and quantity consistency is PER FILE, so goal-vs-retro
   drift is still yours to catch.
2. **A claims round now declares what its verdict is ABOUT** (#701) — shipped
   surfaces gate the tag, dated session narrative is reported and published
   known-inaccurate; the contract is in
   [critique-boundary.md](../skills/public/release/references/critique-boundary.md).
   Before authoring a claims record, derive the scope with
   `claims_review_scope.partition` over `<previous-tag>..<prepared>`; the
   validator re-derives it and refuses a scope that moves a path or omits a
   blocking one. Every checked-in example predates `v3`, so copying one as a
   template gets refused after the prepared commit exists, where the only repair
   is an in-place amend.
3. **A new gate now catches the class that cost this session four claims
   rounds**, and it is worth knowing before writing a goal or retro.
   [The referent gate](../scripts/check_artifact_referents.py), wired into
   `run-quality.sh`, enforces a
   third rung between the existing two: FORM (a disposition is well-shaped, owned
   by the skill floors) -> **REFERENT (the thing it names is real)** -> SUBSTANCE
   (it is the right thing, still the fresh-eye reviewer's call). It refuses
   `issue #N`, an `applied:` naming a path that does not exist, and a SHA that
   does not resolve. `{{q:<id>=<value>}}` markers make a count that is restated
   agree with itself. Two things to know: the gate can exit **3**
   (`UNESTABLISHED`) when git cannot resolve SHAs — that is "ran, established
   nothing", not a pass — and quantity consistency is checked PER FILE, so
   goal-vs-retro drift is still on you.
4. **Reproduce before repairing a review finding.** Twelve of twenty-seven
   blockers this run got a wrong first repair, and in two more the reviewer's own
   proposed fix was wrong. Repairing prose by re-reading prose is what failed;
   the one repair that held was derived from `git log` / `git show`.
5. #694 is decided and implemented (decline an ambiguous line, do not block
   activation), but stays open on a second blind shape: a deferral flag named
   only for a terminal step, with no earlier deferral, still reads as a deferral.
6. Do not run a third review round on the `#681` repair; the two-round cap is
   consumed and the round-2 repairs are recorded as accepted-unreviewed.
7. For a new work unit, run the repo-owned opener before any review or brief —
   `python3 scripts/open_lesson_session.py --repo-root . --session-id <slug> --seed <slug>`
   — and preserve the commit -> changed-line -> broad-quality ordering.
8. Do not claim a verdict from timeout, exit code, transcript, screen output, HTTP
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

# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn — the REPO'S OWN copy, never the installed one:
  the installed-copy declare wrote a receipt without a ledger event, the half-written
  state the continuity gate then refuses (`unknown session` on every score).
- Then run `## Next Session` item 1.

## Continuation Capability

- The [adapter consumer census](../scripts/adapter-consumer-classification.json) holds the
  live answer to "what does this file do when an adapter's version was refused", one row
  per consumer. `python3 scripts/check_adapter_consumer_classification.py --repo-root .`
  prints the per-verdict counts and the remaining accepted risk.
- The [quality record](../charness-artifacts/quality/2026-08-18-quality-review.md) holds
  gates, runtime signals, and the recommended next quality moves.
- The [digest](../charness-artifacts/retro/recent-lessons.md) holds what a session reads
  before work. Version: `git describe --tags --abbrev=0`.

## Current State

- **The adapter-consumer debt is paid down row by row, each by a MEASURED behavioral
  flip.** The census records the COVERAGE LEVEL, not one `guarded` token, and the guard
  refuses on the CONDITION ("this reader honored nothing the repo declared") through all
  three channels a resolver REPORTS — a refused `version`, a refused parse, a silently
  dropped line. Keying on only the first was measured as an escape: `version: !!int 9`
  walked past every guard and wrote two durable files to a directory the repo never named.
  Recount with `python3 scripts/check_adapter_consumer_classification.py --repo-root .`;
  never read a count off this file — **nor off that gate's own comments, one of which
  undercounts its blind consumers by one.**
- **Every batch owes two bounded review rounds and NOT ONE has been clean.** Round 2 keeps
  finding that round 1's REPAIRS carry the class they repaired — three times in one slice,
  and three more on a PLANNING artifact. The cheap detector is always the same question:
  what is the cheapest input that still gets past this. Per-round ledgers live in each
  goal's `## Slice Log` or `## Plan Critique Findings`.
- **A probe record's reproduction steps are MECHANICALLY checked**, but only under
  `check_probe_record.py --replay-stimulus`; `--require-evaluated` alone does NOT replay,
  and operator ruling 2026-08-19 keeps them unfolded. The corpus sweep gate runs the
  replay in the standing lane.
- **A red on [test_web_fetch_cleanup.py](../tests/test_web_fetch_cleanup.py) means
  investigate a HANG** — the flake's bar is repaired and the 120s wall clock is only a
  backstop. It is NOT an expected red to absorb.
- **Issue triage ran against current HEAD**; `#628`, `#673` and three umbrellas await an
  owner readback. Inventory: `gh issue list --repo corca-ai/charness --state open`.
- **Nothing reads a `path:line` an artifact asserts** — one shaping session produced nine
  citation defects, four load-bearing ([#677](https://github.com/corca-ai/charness/issues/677)).
  Verify citations BEFORE spawning a reviewer; a round is a costly grep.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then
  `python3 -m pytest -q -m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **The successor goal is SHAPED and inert; activation is the operator's call.**
   `/goal @charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md` is
   `pursue_ready`, scoped to detector-plus-two-spends (`#676`), with four operator rulings
   in its `## Discuss Before Activation`. Slice 0 is a STOP: no six per-instance SHAs in
   `#676`'s table, no corpus, goal halts there.
2. **Its round-2 repairs are `accepted-unreviewed`** under the two-round cap; the `## Goal`
   rewrite and the negative-control requirement are where a third instance would sit.
3. **The consumer count behind the two blind libraries is FIVE, not four**, and the census
   recount CANNOT evidence slice 2b (`safe-checks-errors` is outside `GUARDED_LEVELS`).
   Sources: that goal's `## User Acceptance` item 8 and `## Off-Goal Findings`.
4. **The last goal closed at three of five slices**, resolving `#673`, `#674`, `#675`; its
   acceptance item 4 is PARTIAL and item 5 NOT met, with per-item verdicts in
   [adapter debt tooling and remainder](../charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder.md) under `## User Verification Instructions`.
5. **Seventeen debt rows remain**, not the old plan's nineteen — slices 2 and 3 moved rows
   in both directions. Recount them; each row's consequence is one row of the
   [census manifest](../scripts/adapter-consumer-classification.json), never a number here.
6. **[#668](https://github.com/corca-ai/charness/issues/668) is still an operator ruling** —
   should the pytest bar measure wall time at all. Read `#546` in the same sitting.
7. **Reconcile [#677](https://github.com/corca-ai/charness/issues/677) with that goal's
   slice 1 before building either** — both ask whether a cited thing contains what the
   text claims, so shipping both is `one-engine-per-pattern` at the tooling layer.

## Discuss

- **The boundary-bypass gate still has no scoped rotation accept.** This session rewrote
  its whole baseline for ONE rotated key with every count unchanged — a second data point
  for adopting the dup ratchet's `--accept-rotation` shape.
- **Fourteen per-skill `adapter-contract.md` files say nothing about version containment.**
  The runtime refusal now names the file and the line to fix, which may be the better
  channel than fanning prose across fourteen docs. Owner's call.
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

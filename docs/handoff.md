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

- **The adapter-consumer debt is being paid down row by row, each by a MEASURED
  behavioral flip.** The census records the COVERAGE LEVEL now, not one `guarded` token:
  `guarded-all-doors`, `guarded-errors-only` (blind to a silently dropped line — a one-typo
  bypass, 3 rows), and `guarded-upstream` (owes an enumerated `covering_rows` list). That
  split moved the reported accepted risk 11 to 6 — in BOTH directions during review, because
  some rows were already covered upstream and one migrated that should not have. The guard refuses on the CONDITION
  ("this reader honored nothing the repo declared") through the channels a resolver
  REPORTS — a refused `version`, a refused parse, a silently dropped line. ALL SIXTEEN
  report all three since [#673](https://github.com/corca-ai/charness/issues/673); records
  written while five were blind are correct for their revision. Keying on only the first was measured as an
  escape: `version: !!int 9` walked past every guard in the repo and wrote two durable
  files to a directory the repo never named. Recount with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`; never read a
  count off this file.
- **Every batch owes two bounded review rounds and NOT ONE has been clean.** Round 2 keeps
  finding that round 1's REPAIRS carry the class they repaired — three times in one slice.
  The cheap detector is always the same question: what is the cheapest input that still
  gets past this. Per-round ledgers live in each goal's `## Slice Log`.
- **A probe record's reproduction steps are now MECHANICALLY checked.**
  `check_probe_record.py --replay-stimulus` resolves each adapter declaration a record's
  `## Stimulus` writes and refuses the ones no reader honors; the corpus sweep gate runs it
  in the standing lane. It found a fifth dead control no review round had.
  [probe_record_lib](../scripts/probe_record_lib.py) still types what a record ESTABLISHES;
  its floor stays at REVIEW severity by operator ruling, pinned by test.
- **The standing-lane flake's BAR is repaired**; a 120s wall clock remains as a HANG
  BACKSTOP, so a red on
  [test_web_fetch_cleanup.py](../tests/test_web_fetch_cleanup.py) means investigate a
  hang — it is NOT an expected red to absorb.
- **Issue triage ran against current HEAD**; `#628`, `#673` and three umbrellas await an
  owner readback. Inventory: `gh issue list --repo corca-ai/charness --state open`.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then
  `python3 -m pytest -q -m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **Start the successor goal**, drafted from what the last run MEASURED — its slice 1 is
   the affordance for a repair shipping the class it repairs (six times, three surfaces,
   every one caught by the second review round), and it carries the unfinished rows:
   [repairs that carry their class](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md) holds that plan.
2. **The last goal closed at three of five slices**, halted by its own stop rule, and
   resolved `#673`, `#674`, `#675`; TWO of its five acceptance items are NOT met and one is
   partial, with the per-item verdict and command in its `## User Verification Instructions`:
   [adapter debt tooling and remainder](../charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder.md) holds that record.
3. **Seventeen debt rows remain**, not the nineteen the old plan projected: slices 2 and 3
   moved rows in both directions. Each row's consequence is in the
   [census manifest](../scripts/adapter-consumer-classification.json); count them with
   `python3 scripts/check_adapter_consumer_classification.py --repo-root .` and never off
   this file.
4. **[#668](https://github.com/corca-ai/charness/issues/668) is still an operator ruling** —
   should the pytest bar measure wall time at all. Read `#546` in the same sitting.

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

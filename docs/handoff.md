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
  behavioral flip.** Thirteen rows are `guarded`; the guard refuses on the CONDITION
  ("this reader honored nothing the repo declared"), which has two doors — an unspeakable
  `version` and a document the parser refused. Keying on only the first was measured as an
  escape: `version: !!int 9` walked past every guard in the repo and wrote two durable
  files to a directory the repo never named. Recount with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`; never read a
  count off this file.
- **Every batch has owed and received two bounded review rounds, and NOT ONE has been
  clean.** The rounds have caught, in order: a guard keyed on one check's wording instead
  of the condition; a read-site rationale published into eight surfaces that the code
  refutes; a repair applied to the shared helper and not to three consumers that bypass
  it; a gate witness its own repair's COMMENT satisfied; and a narrowing that landed in one
  of five surfaces. The cheap detector each time was the same question — what is the
  cheapest input that still gets past this — plus grepping the phrase rather than the file.
  Per-round ledger:
  [the goal's `## Slice Log`](../charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md).
- **A behavioral probe can now say it measured NOTHING, and two boundaries read it.**
  The [probe record library](../scripts/probe_record_lib.py) types a record in
  `boundary_probe_lib`'s existing
  vocabulary; the issue-close and release close-issue floors read it. Held at REVIEW
  severity by operator ruling (`issue_probe_record_floor.PROBE_RECORD_SEVERITY`) until
  slice 5 reports what a record costs across 45 real rows — the mechanism and its proof
  are complete, the veto is not armed, and both severities are pinned by test.
- **The standing-lane flake's BAR is repaired**; a 120s wall clock remains as a HANG
  BACKSTOP, so a red on
  [test_web_fetch_cleanup.py](../tests/test_web_fetch_cleanup.py) means investigate a
  hang — it is NOT an expected red to absorb.
- **Issue triage ran against current HEAD**; `#628` and three umbrellas
  (`#582`/`#583`/`#584`) await an owner readback. Inventory:
  `gh issue list --repo corca-ai/charness --state open`.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then
  `python3 -m pytest -q -m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **Continue the active goal.** The current slice, the next action, and the review state
   all live in the goal's own `## Active Operating Frame`, which is the surface to read
   rather than this list while it is active:
   the [probe-provenance and adapter-consumer-debt goal](../charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md)
   holds that frame plus the slice log. Slices 1-3 have landed; slice 4 part 1 landed and
   PART 2 IS BLOCKED on an operator ruling; slice 5 has paid down thirteen rows in three
   batches, each with both bounded rounds. Do not re-derive what the frame already
   measured.
2. **The debt rows are the goal's slice 5** — severity order, release gates first, and
   the `no-version-validation` rows need the shared resolver rather than a check they have
   nothing to check. Each row's consequence is in the
   [census manifest](../scripts/adapter-consumer-classification.json); count them with
   `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
3. **[#668](https://github.com/corca-ai/charness/issues/668) is still an operator ruling**,
   not a code fix: should the pytest bar measure wall time at all. `#546` sits in the same
   file and should be read in the same sitting.

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

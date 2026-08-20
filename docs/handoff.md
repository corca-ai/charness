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
  flip.** The census records the COVERAGE LEVEL, and the guard refuses on the CONDITION
  through all three channels a resolver REPORTS — refused `version`, refused parse,
  silently dropped line. Keying on the first alone was a measured escape:
  `version: !!int 9` walked past every guard. Recount with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`; never read a
  count off this file — **nor off that gate's own comments, one of which undercounts its
  blind consumers by one.**
- **Every batch owes two bounded review rounds and NOT ONE has been clean.** Round 2 keeps
  finding that round 1's REPAIRS carry the class they repaired — most recently a
  fail-open grandfather whose own branch no test took, so mutating it green-lit the whole
  repo. The cheap detector is always: what is the cheapest input that still gets past
  this. Per-round ledgers live in each goal's `## Slice Log` / `## Plan Critique Findings`.
- **Every prose artifact budget charges WORDS, not lines** (handoff 900, debug 1200,
  quality 1100, cautilus 800/1200); [artifact_size_budget](../scripts/artifact_size_budget.py)
  owns why. A line count charged for wrap width — one bar admitted
  a 5.4-7.5x spread of words — and `MD013` is off, so rewrapping was the cheapest way to
  comply. `max_content_lines` / `max_artifact_lines` are REFUSED adapter keys, not ignored
  ones. Dated records before 2026-08-19 are grandfathered; the rolling handoff is not.
- **`check_probe_record.py --replay-stimulus` is the form that refuses**;
  `--require-evaluated` alone does NOT replay, by operator ruling 2026-08-19.
- **A red on [test_web_fetch_cleanup.py](../tests/test_web_fetch_cleanup.py) means
  investigate a HANG** — the 120s wall clock is only a backstop, not an expected red.
- **Release-goal shaping read 29 open issues through `#680` at `38775dfeb`.** Activation
  must recount; the goal separates claims, refutations, decisions, and conditional work.
- **Nothing reads a `path:line` an artifact asserts**
  ([#677](https://github.com/corca-ai/charness/issues/677)). Verify citations BEFORE
  spawning a reviewer; a round is a costly grep.
- **The standing and release lanes are NOT the broad lane.** `bash scripts/run-quality.sh`
  runs corpus sweeps neither touches; a budget change went green on both while that lane
  was red on seven artifacts. Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then
  `python3 -m pytest -q -m release_only`, then the broad lane.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **Activate the broad, inert, `pursue_ready` release goal:**
   `/goal @charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`.
   A lower-capacity executor should follow `## Execution Runbook` literally.
2. The [release goal](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md)
   holds Slice 0's recount, raw planner receipts, exactly-once ledger, reviewed validator,
   intake-lock commit, and no-writer-before-lock boundary.
3. **Release-path work goes first:** `#679` is reproduced at shaping HEAD;
   `#612/#668/#669/#667` become blockers only after live reproduction. `#669a` orphan
   reaping and conditional `#669b` timeout attribution are separate packages.
4. **Then execute every qualified disjoint package.** The goal fixes entry files, tests,
   branches, path ownership, amendment rules, and non-work candidates for evidence,
   semantic inspection, packaging/discovery, and conditional `#634/#676/#677` work.
5. The [release goal](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md)
   holds the planner-selected bump, separate semantic/release candidates, scoped final
   release grant, ambiguous-push resume, distinct hosted/install proof, post-release issue
   closure, and the ungranted Cautilus boundary.

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

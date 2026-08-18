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

- **A reader that cannot speak an adapter's `version` now honors NOTHING it declares**, and
  the surfaces that act on a payload REFUSE instead of silently using a charness default.
  Before this, a declared mandatory release review reported `not_configured`, the retro
  gate printed `Validated 0 retro artifact(s).` exit 0 over an artifact it was handed by
  name, and the debug gate enforced its shipped ceiling over a repo that declared a lower
  one. All three were reproduced on the real CLIs, not argued.
- **The remaining debt is COUNTED, not fixed.** Every consumer carries a written verdict;
  the `accepted-risk-unguarded` rows are the ones that would still use a charness default.
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .` prints that count
  on every run so it stays decided rather than forgotten.
- **The standing-lane flake's BAR is repaired**, so the lane no longer blocks pre-push.
  `test_acquire_closes_session_on_sigterm_mid_render` in
  [test_web_fetch_cleanup.py](../tests/test_web_fetch_cleanup.py) bounded its readiness
  wait with a 10s wall deadline, which measured the MACHINE — everything the child does
  before the `open` call is unbounded work sized by how many xdist workers run beside it.
  It now waits on the child's process state and fails fast and distinguishably if the
  child exits. Proven on the bound observable rather than by a green run: against a child
  reaching its `open` line at 12s, the old loop raises `AssertionError` at 10.0s and the
  new one passes at 12.1s. Residual: a wall clock remains at 120s as a HANG BACKSTOP, so
  a red there means investigate a hang — it is NOT an expected red to absorb.
- **Issue triage ran against current HEAD.** Over half of the open set still reproduces;
  four are closeable with commit-level evidence (`#629`, `#628`, `#608`, `#528`) and three
  umbrellas (`#582`, `#583`, `#584`) are ready for an owner readback because their tracked
  children are reported fixed. Inventory:
  `gh issue list --repo corca-ai/charness --state open`.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then
  `python3 -m pytest -q -m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **Continue the active goal.** The current slice, the next action, and the discharged
   precondition all live in the goal's own `## Active Operating Frame`, which is the
   surface to read rather than this list while it is active:
   the [probe-provenance and adapter-consumer-debt goal](../charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md)
   holds that frame plus the slice log. Slice 1 (the probe record) has landed with two
   bounded review rounds. The pre-push flake that used to head this list is discharged.
2. **Pay down `accepted-risk-unguarded` in severity order, not file order.** The sharpest
   class is a gate that reports the OPPOSITE of truth — a declared trigger read back as
   "this repo declares none", exit 0. Release gates lead that class. Each row's consequence
   is in the [census manifest](../scripts/adapter-consumer-classification.json).
3. **The [`no-version-validation`](../scripts/adapter-consumer-classification.json) rows
   need a DIFFERENT fix**: they read
   `.agents/*-adapter.yaml` with a raw YAML load and never reconcile a version, so there is
   no `errors` for anyone to check. Wire them onto the shared resolver rather than adding a
   check they have nothing to check.
4. **Close `#629`, `#628`, `#608` and `#528` through the `issue` closeout floor**, not in
   bulk — one triage row cited a commit date that was wrong while its conclusion held, and
   a close that lands is not undoable by pushing again.
5. **[#668](https://github.com/corca-ai/charness/issues/668) is still an operator ruling**,
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

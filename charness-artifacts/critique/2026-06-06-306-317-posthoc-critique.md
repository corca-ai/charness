# Post-hoc code critique — v0.23.0 / 306-317 shipped bundle

Target: code-critique (already-shipped). Run at operator request before session
end, because the in-workflow review returned 0 findings yet the broad `--release`
gate still caught a real #316 defect — so a fresh adversarial pass was warranted.

Execution: bounded fresh-eye subagents — 4 angle reviewers + 1 separate
counterweight. Fresh-Eye Satisfaction: parent-delegated (per AGENTS.md Subagent
Delegation). Packet Consumed: `charness-artifacts/critique/2026-06-05-225242-packet.md`.

## Change

Commits `497116a5..d1ac803b` (16 commits): #306/#311/#314/#315/#316/#317
implemented via the dynamic workflow + closeout + the v0.23.0 release (pushed to
`main`, public).

## Angles (each tried to falsify the prior reviews)

- **Correctness / behavioral regression — CLEAN.** #314 gate rewire is
  behavior-preserving (`_MIRROR_PREFIXES` byte-identical; allowlist routes the
  two fast checkers to the right surfaces; no false-neg/pos). #306 coverage is
  REAL (measured: validator-fallback + symlink branches leave the missing set;
  `__file__` monkeypatch sound); non-weakening test genuinely blocks. #311/#317
  inspectors fire on intended inputs, don't false-fire on current docs.
- **Test & gate integrity / non-weakening — CLEAN.** #315 `_PLACEHOLDER_MARKER`
  has no exploitable hole (and is backstopped by a file-existence + goal-binding
  check); skip channel closed; seeded Auto-Retro placeholder still reads blank.
  #314 drift-guard real; #306 non-weakening real. No loosened threshold / removed
  assertion / xfail / skip in the diff. Source↔mirror parity confirms deployed
  gates equal tested gates.
- **Honesty / over-claim — MOSTLY CLEAN.** Live state matches every "closed /
  released / verified" claim. #311 `manual_fallback_used: true` is an honestly-
  reported verification-timing artifact over a correct `Close #311` carrier (the
  issue actually closed via its own slice commit `c688e66c`). One LOW finding
  (see A).
- **Portability / cross-surface & mirror drift — PASS.** Mirrors byte-identical
  and idempotent on re-sync; no portable host-path or issue-anchor leak; version
  surfaces uniform 0.23.0. One WATCH (see B).

## Findings

- **A [LOW — honesty/consistency].** The goal artifact's *plan/boundaries*
  sections still carry the pre-correction "one remote CI" assumption in 3 spots
  (`## Boundaries`, `### External Or Live Proof`, `## Slice Plan` S8 row still
  `planned` / "CI green"), un-reconciled with the no-push-CI correction that the
  authoritative *outcome* sections carry 5×.
- **B [LOW/WATCH — length].** `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
  is 329 code lines, one line below the advisory WARN band (330; hard limit 360).
  Passes today; the next net +1-line edit trips a non-blocking WARN.

## Counterweight Triage (four bins)

- **Act Now:** none.
- **Bundle Anyway:** Finding A — if this file is ever touched again, a 30-second
  ride-along strike-through on the S8 row + a parenthetical on the two prose
  spots; not worth its own commit.
- **Over-Worry (ignore):** Finding A as a standalone action (rewriting a frozen,
  `Status: complete` goal scratchpad's plan history would erase the honest
  "assumed → corrected" trail the outcome sections deliberately preserve), and
  Finding B (a green file one line below a non-blocking advisory that the WARN
  band is designed to surface to the next author at zero cost now).
- **Valid but Defer:** none new — Finding B's general pattern is already tracked
  by #319.

## Deliberately Not Doing

- Not rewriting the completed goal's plan/boundaries CI lines: the outcome
  sections already correct them, and preserving the wrong-assumption→correction
  trail is more honest than cosmetic consistency.
- Not filing/fixing the 329/330 length watch: no failing gate, no behavior
  change; the WARN band handles it at the next edit, and #319 owns the pattern.

## Next Move

None. Ship stands. The one real defect this run produced (#316 compressing
`achieve/SKILL.md` to the 160 core limit) was caught by the `--release` gate
before the irreversible push, fixed in `54e1b6b1`, and its general pattern filed
as #319 — the system catching and routing its own mistake. No re-open.

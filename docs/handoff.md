# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn — the REPO'S OWN copy, never the installed one:
  the installed-copy declare wrote a receipt without a ledger event, the half-written
  state the continuity gate then refuses (`unknown session` on every score).
- Then run `## Next Session` item 1.

## Continuation Capability

- The [active release goal](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md) holds
  the macro-slice control panel, issue boundaries, proof plan, and current R2 slice log.
- The [reviewer consumer contract](../skills/shared/scripts/reviewer_worker_report.py) holds
  the fail-closed rule requiring typed fresh output, matching provenance, and `findings-received`.
- The [recent-lessons digest](../charness-artifacts/retro/recent-lessons.md) holds
  the session-start recurrence traps and parallel/timeout discipline.

## Current State

- The [R2 slice record](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md) holds
  the worker/consumer changes, focused evidence, timeout non-claim, and fresh-eye delivery state.
- The [#687 debug/spec pair](../charness-artifacts/debug/2026-08-21-fresh-eye-interrupted-delivery.md) holds
  the causal delivery boundary and the Charness/host ownership split.
- The [R2 RCA ledger](../charness-artifacts/metrics/rca-ledger.jsonl) holds
  the converted classes for media-versus-verdict confusion and process-tree timeout leakage.
- `git status --short` is the current worktree check; the last committed closeout passed
  mirror, standalone-import, contract, lint, and 18 staged pre-commit checks.
- The [recent lessons](../charness-artifacts/retro/recent-lessons.md) keep the next run
  sensitive to wrong calls, timeout loss, and repairing inside an open review window.

## Next Session

1. Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`;
   this repo-owned session receipt is the prerequisite for the next review or brief.
2. Run `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha "$(git rev-parse 495af8a20^)" --refuse-unestablished`;
   this binds the whole R2 code slice, not an empty post-commit diff, before the broad lane.
3. Activate `/goal @charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`;
   its `## Active Operating Frame` now names R2 rebinding and the qualified disjoint lanes.
4. Rebind the semantic candidate using the [goal closeout binding plan](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md):
   bind the current R2 packet, source/plugin mirror, changed-line receipt, and verification lock before fan-out.
5. Read the [goal runbook](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md)
   for P0 #679 reproduction first, then fan out only lanes with a current reproducer, owner,
   acceptance, disjoint path budget, and proof plan; serialize exports, ledger, generated docs,
   version, release, index, and proof truth surfaces.
6. Keep version/export/release-record mutation, tag, push, and publication on hold until all
   claimed lanes are integrated and the [goal release boundary](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md) is re-proven.
7. Do not claim fresh-eye approval unless the [consumer report](../skills/shared/scripts/reviewer_worker_report.py)
   accepts a typed successful receipt and matching current-packet delivery ledger; timeout,
   exit code, transcript, screen output, or any other media alone is non-delivery.

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

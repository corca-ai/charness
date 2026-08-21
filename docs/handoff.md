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
  the fail-closed rule requiring a typed fresh output, matching provenance, the
  terminal `findings-received` state, and the combined report's `delivery_complete`.
- The [recent-lessons digest](../charness-artifacts/retro/recent-lessons.md) holds
  the session-start recurrence traps and parallel/timeout discipline.

## Current State

- The [#687 debug/spec pair](../charness-artifacts/debug/2026-08-21-fresh-eye-interrupted-delivery.md) holds
  the causal delivery boundary and the Charness/host ownership split.
- The [current-open requalification packet](../charness-artifacts/issues/2026-08-21-current-requalification.md)
  separates historical post-lock reproductions from current source,
  installed, and host evidence for #681–#687. It is not an issue-close or
  publication receipt.
- The blocked [R3 release-readiness critique](../charness-artifacts/critique/2026-08-21-r3-release-readiness.md)
  found a real process-success-versus-host-delivery exit gap in root `charness
  init/update`, plus status-surface and candidate-install proof gaps. Its four
  file-backed worker findings were delivered with clean boundary verification;
  all verdicts were `block`, not approval.
- [Root CLI repair](../charness) is committed in the current semantic candidate
  `502c8a8adbbe77781f1714cb6c4383a85d6e3683` (delivery/readback repair at
  `19fb9b5a1`, boundary-coverage repair at `502c8a8ad`): failed host delivery
  exits 1; failed/skipped delivery cannot advance provenance; retries cannot be
  suppressed by old success. Same-version cache claims require content
  readback, and failure output carries typed scope/retry state. Its exact packet
  is `../charness-artifacts/critique/2026-08-21-r3-delivery-provenance-repair-current-exact-packet.json`
  (SHA256 `5a936834bce7fe68db1f894e5e6764de336d9b8dbd4e69fd26f472ab07632ef7`,
  reviewed-input identity
  `26f29ca25c71bf4d704854285c787734f9a1e99bc7d770a9df8674ee3778dfc2`).
  Candidate package/install/host proof remains pending; the older `7676ec…`
  packet is historical.
- The release-quality repair is integrated at `e6eb040cb`; current HEAD is
  `26f31a872` after the gate-owned SLOC inventory refresh. The exact release
  gate passed `98 passed, 0 failed`; the generated-only follow-up does not
  change the semantic candidate or packet.
- The [R2 RCA ledger](../charness-artifacts/metrics/rca-ledger.jsonl) holds
  the converted classes for media-versus-verdict confusion, process-tree
  timeout leakage, provider-schema closure, and the reviewer-runtime output
  boundary. The round-2 findings are durably recorded in
  [the critique round record](../charness-artifacts/critique/rounds/2026-08-21-r2-semantic-candidate-provider-schema-round-2b.md);
  all three reviewer verdicts are `block`, so no fresh-eye approval is claimed.
- The [changed-line consumer-gap debug record](../charness-artifacts/debug/2026-08-21-changed-line-review-consumer-gaps.md)
  records the post-commit counterexample repair; the exact-base rerun is now
  clean at `362221694` with `blocking_targets: {}`.
- The current exact-base changed-line proof is `status: clean` from base
  `d9995e0079326ae9ad0a35f9ade64a9f951c4fbf`, with 2 mapped changed-pool files,
  every changed line covered, and `blocking_targets: {}`. This is local
  semantic-candidate proof only.
- Release-boundary verification at integrated HEAD `26f31a872` is current:
  the release gate returned `98 passed, 0 failed`; the broad changed-line proof
  from `38775dfeb` is clean across 53 mapped files; fresh-checkout probes are
  5/5; real-host proof is required and its checklist is recorded; and the
  requested-review gate is clear. This is not publication or host readback.
- Two unsupported release-check invocations were attempted during this run:
  `./charness current-release --detail` (wrong command surface), followed by
  `current_release.py --detail` (unsupported flag). Both are non-pass
  command-boundary smells; the supported script invocation was then run
  successfully. Neither rejected call is evidence of a release check.
- Broad `./scripts/run-quality.sh --release` completed with `98 passed, 0
  failed` in `323.9s` (pytest-release `196.2s`, changed-line mutation
  `300.1s`). Length/ratio/markdown/nose findings remain advisory.
- The [recent lessons](../charness-artifacts/retro/recent-lessons.md) keep this run
  sensitive to wrong calls, timeout loss, and repairs inside an open review window.
- The [current closeout evidence](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md#final-verification)
  also records the structural command-boundary rule: resolve owned
  help/inventory before composing a path or flag, and preserve duplicate
  wrong-call signals as non-approval evidence rather than silently retrying.

## Next Session

1. Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`;
   this repo-owned session receipt is the prerequisite for the next review or brief.
2. Re-read the [fresh-eye delivery boundary spec](../charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md)
   and the two implementation commits above; do not repeat the repaired
   semantic slice or claim a third bounded review under the cap.
   Also re-read the [goal continuation retro](../charness-artifacts/retro/2026-08-21-goal-continuation-retro.md),
   including `recurrence-class: parallel-coverage-runtime-collision` and
   `recurrence-class: unclaimed-session-disposition`.
3. Re-read the [goal's final-verification proof plan](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md#final-verification)
   and the semantic candidate/packet join above; do not reuse the
   older dirty-worktree `UNPROVEN` receipt as changed-line proof, and do not
   confuse the direct producer's advisory coverage warning with the runner's
   typed verdict.
4. Read the [requalification packet](../charness-artifacts/issues/2026-08-21-current-requalification.md)
   and the [blocked R3 release critique](../charness-artifacts/critique/2026-08-21-r3-release-readiness.md),
   then activate `/goal` for the [active release goal](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md);
   its `## Active Operating Frame` names the root-CLI repair, normalized status
   axes, and remaining candidate/install boundary.
5. Read the [goal runbook](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md)
   for P0 #679 reproduction first, then fan out only lanes with a current reproducer, owner,
   acceptance, disjoint path budget, and proof plan; serialize exports, ledger, generated docs,
   version, release, index, and proof truth surfaces.
6. The exact semantic candidate and packet are bound above. The bounded review
   cap is already consumed; do not run a third review or substitute a same-agent
   pass. Execute candidate/install proof next. Keep
   version/export/release-record mutation, tag, push, and publication on hold
   until the [goal release boundary](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md)
   is re-proven. Current HEAD is `26f31a872`; remaining work is the versioned
   candidate, publication, post-publish readback, and issue closeout.
7. Do not claim fresh-eye approval unless the [consumer report](../skills/shared/scripts/reviewer_worker_report.py)
   accepts a typed successful receipt and matching current-packet delivery ledger; timeout,
   exit code, transcript, screen output, or any other media alone is non-delivery.

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

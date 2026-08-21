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
  The older `7676ec…` packet is historical. The semantic candidate was carried
  into published `6.2.1`; issue-specific host behavior remains bounded by the
  requalification packet below.
- The release-quality repair is integrated at `e6eb040cb`; current HEAD is
  `26f31a872` after the gate-owned SLOC inventory refresh. The exact pre-publish release
  gate passed `98 passed, 0 failed`; the generated-only follow-up does not
  change the semantic candidate or packet. The published release record and
  post-publish artifact verification are now at `d0df6dc7a`.
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
- Pre-publish release-boundary verification at integrated HEAD `26f31a872` was
  current for the release cut:
  the release gate returned `98 passed, 0 failed`; the broad changed-line proof
  from `38775dfeb` is clean across 53 mapped files; fresh-checkout probes are
  5/5; real-host proof is required and its checklist is recorded; and the
  requested-review gate is clear. Publication and post-publish readback are
  recorded below.
- Published release truth is current: tag `v6.2.1` points to
  `46169b7ad7491e1d4b1a50b5411ebf5a08f03a68`, `origin/main` and the managed
  install are at `d0df6dc7ac9c761b14bd1d5c5ef8b95bd1f2ec9d`, and
  `gh release view v6.2.1` confirmed a non-draft, non-prerelease GitHub
  Release. `charness version` reports `6.2.1`; `charness doctor --detail`
  reports a valid Codex cache manifest and `source_cache_drift: false`.
- The goal-bound release retros
  [`2026-08-21-goal-r2-resume-final.md`](../charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md),
  [`2026-08-21-r2-semantic-packet-final.md`](../charness-artifacts/retro/2026-08-21-r2-semantic-packet-final.md),
  and [`2026-08-21-r3-delivery-review-final.md`](../charness-artifacts/retro/2026-08-21-r3-delivery-review-final.md)
  close the receipted lesson sessions; continuity is clean. Fresh-eye approval
  remains unclaimed, Cautilus was not run, and issue tracker closeout was not
  requested. #687's host-side terminal event remains explicitly unproven.
- Two unsupported release-check invocations were attempted during this run:
  the retired current-release subcommand was invoked with the detail flag,
  followed by the current-release script with that unsupported flag. Both are
  non-pass command-boundary smells; the supported script invocation was then
  run successfully. The [goal closeout evidence](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md#final-verification)
  owns the detail; neither rejected call is evidence of a release check.
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

1. Start from the published truth at `d0df6dc7a` and the
   [goal final verification](../charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md#final-verification);
   do not regress routing to the pre-version `26f31a872` state.
2. Keep the bounded fresh-eye cap consumed: do not run a third review or
   substitute a same-agent pass. The [R3 critique packet](../charness-artifacts/critique/2026-08-21-r3-current-candidate-release-critique.md)
   records that the claims review is not fresh-eye approval.
3. Read the [requalification packet](../charness-artifacts/issues/2026-08-21-current-requalification.md)
   before changing issue status. Issue-specific semantic probes and tracker
   closeout remain separate decisions; #687 host resolution is not claimed.
4. For a new work unit, run the repo-owned lesson session opener before any
   review or brief and preserve the commit -> changed-line -> broad-quality
   ordering; the [recent-lessons digest](../charness-artifacts/retro/recent-lessons.md)
   owns the lesson-session requirement.
5. Do not claim a verdict from timeout, exit code, transcript, screen output,
   HTTP reachability, tag presence, or any other media alone. The
   [consumer report](../skills/shared/scripts/reviewer_worker_report.py) must
   accept a typed receipt with matching provenance and terminal state.

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

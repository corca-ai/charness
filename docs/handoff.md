# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- v2.3.1 is PUBLISHED and confirmed by distinct observers: GitHub API
  `gh release view` (non-draft), the remote tag `v2.3.1 -> eb5bbc57`, and installed
  `charness version -> 2.3.1`; install refresh (`charness update`) rc 0.
- The flaky/parallel-suite OPEN SMELL is RESOLVED and shipped in v2.3.1. Two root
  causes: (a) release-failure retention evicted by coarse-granularity `st_mtime_ns`
  (now orders by the embedded `time.time_ns()` stamp), and (b) the `--release`
  mass-error burst was a pytest temp-tree deletion race — the standing runner's
  lock-less `pytest-*` basetemp deleted mid-run by nested pytest cleanup (leaf
  renamed to `charness-run-<ns>`). Both pinned by deterministic regression tests;
  the `mtime-recency-tiebreak` and `unlink-missing_ok` follow-ups are resolved. RCAs
  and release state in References.
- The abstracted-pattern sibling-scan Tier-1 (A/B/C) and Tier-2 (D) findings are
  FIXED with regression tests and clean fresh-eye reviews
  ([Tier-1 fixes critique](../charness-artifacts/critique/2026-07-20-tier1-sibling-scan-fixes-critique.md);
  Tier 2's approve + accepted `sessions`-file nit is in its commit ledger). The
  live usage-episodes guard now ignores live-writer-owned paths while keeping
  strict #194 leak teeth.
- Durable prior context (all closed, do not reopen without regression evidence):
  v2.3.0 adapter-owned measurement-contract discovery, the Gajae goal, dead-code
  dynamic-entrypoint review, standing-xdist speedups, and quality's portable
  proof-path method.

## Next Session

1. The sibling scan is closed through Tier 2; Tier 3 (E-J) stays opportunistic /
   boy-scout only. Recommended next: pick from the Discuss items below or the
   deferred discovery follow-ups (inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory).
2. For clean-start mutating workflows, enumerate owned mutations before coding and
   make every failure either restore the start state or emit a typed, resumable
   state; for irreversible operations, prove the exact consumed range (see recent
   lessons in References).
3. Keep D18 ignored unless the operator explicitly reopens it.
4. For mutation-pool changes, ask the selector before widening a producer by hand:
   direct reference, nearest recognized loader ancestor, then broad fallback.
5. When adding a new dynamic-call syntax, add wrong-path, wrong-loader,
   wrong-receiver, and disconnected-control-flow fixtures before recognizing it.
6. Intentionally deferred: reaping stale `charness-run-*` basetemps from failed
   standing runs — an ad-hoc reaper would reintroduce the deletion-race class just
   fixed, and the seed-budget gate already bounds the footprint.

## Discuss

- RESOLVED: the `verified` additive migration shipped (`verify-closeout` emits
  `confirmation` {observer, channel, scope, line}; old artifacts grandfathered);
  pre-commit rollback persistence was already shipped before the entry was written.
- RESOLVED locally: distinct-channel records now name observer identity (the
  credential-distinct, host-shared HTTP probe says so explicitly); the
  machine-distinct CI-side observer is tracked in #449.

## References

- [abstracted-pattern sibling scan (next-session fix backlog)](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [retention RCA](../charness-artifacts/debug/2026-07-20-debug-review.md)
- [basetemp deletion-race RCA](../charness-artifacts/debug/2026-07-20-standing-pytest-basetemp-deletion-race.md)
- [release state](../charness-artifacts/release/latest.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

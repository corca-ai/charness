# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- v2.4.3 is PUBLISHED (tag `v2.4.3 -> 7dddb494`, public GitHub release and
  unauthenticated HTTPS observer verified, installed refresh confirmed
  `charness version -> 2.4.3`). Scope: #451 mutation-score test-coverage fix,
  #452 create-cli named-option order-independence baseline, and a recorded
  decision not to build #449's CI-side release observer —
  [release critique](../charness-artifacts/critique/2026-07-23-v2-4-3-release-critique.md).
- v2.4.2 (tag `5fb4b7a4`) is superseded by v2.4.3.
- All previously-tracked issues are CLOSED as of 2026-07-23: #446 (scheduled
  green Mutation Tests auto-close), #448 (closed directly by the operator),
  #449 (declined feature, not built — [brief](../charness-artifacts/issue/2026-07-23-issue-449-brief.md)),
  #450 (fix had already landed pre-session in `543785c3` without a close
  keyword; closed this session after re-verification), #451/#452 (resolved
  end-to-end this session; critiques in References). Re-check
  `gh issue list --state open` fresh rather than trusting this line.
- Sibling scan closed through Tier 2; Tier 3 (E-J) stays boy-scout only.

## Next Session

1. Treat v2.4.3 as the published baseline; use `charness update` and restart
   the active host session before diagnosing a version mismatch.
2. No open issues remain as of this session's close; start any new backlog
   scan from a fresh `gh issue list`.
3. Deferred discovery follow-ups remain available: inline `.rglob`/`ls-files`
   pathspec discovery, `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero
   test-surface advisory.
4. Keep D18 ignored unless the operator explicitly reopens it. Stale
   `charness-run-*` basetemp reaping stays intentionally deferred.
5. For mutation-pool changes, ask the selector before widening a producer by
   hand; for new dynamic-call syntax, add wrong-path/loader/receiver and
   disconnected-control-flow fixtures first.
6. #451's causal review deferred two siblings, neither acted on: ~20 sibling
   `init_adapter.py` scaffolds share a thin-assertion emit idiom, and an
   unconfirmed identifier-literal comparison blind spot at
   `scripts/announcement_adapter_lib.py:125` — see its critique before acting.
7. #449 was designed then explicitly declined over the new CI write-
   permission surface it would need; do not re-propose without new
   information — see the brief.

## Discuss

- #448 scoped-accept deferred items (its critique): overlay-missing advisory
  in scoped mode, refused-early-return advisories, explicit `--accept-family`
  of an intentional id test — pick up only with the next dup-ratchet slice.

## References

- [v2.4.3 release critique](../charness-artifacts/critique/2026-07-23-v2-4-3-release-critique.md)
- [#451 critique](../charness-artifacts/critique/2026-07-23-issue-451-resolution-critique.md) · [#452 critique](../charness-artifacts/critique/2026-07-23-issue-452-resolution-critique.md)
- [#449 brief and decision](../charness-artifacts/issue/2026-07-23-issue-449-brief.md)
- [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [retention RCA](../charness-artifacts/debug/2026-07-20-debug-review.md)
- [basetemp deletion-race RCA](../charness-artifacts/debug/2026-07-20-standing-pytest-basetemp-deletion-race.md)
- [release state](../charness-artifacts/release/latest.md) · [quality review](../charness-artifacts/quality/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

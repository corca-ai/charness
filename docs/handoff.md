# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

Closed #460/#461/#463 in one commit (unpushed), then ran an evidence-surface bug
hunt that reproduced **30 defects** across the repo's proof surfaces. All are
tracked in the
[bug hunt record](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
with per-item status, file:line, and confirmed repro. Nothing is fixed yet; the
operator's standing decision is **no push and no release until they are fixed**,
so `HEAD` stays local until the fix sessions land. No GitHub issues are open
(the three close on push). No decisions pending.

## Current State

- **The chunker reports staleness facts before ranking, and the auto-draft now
  renders them.** Each entry carries `missing_paths` / `closed_issues` /
  `unresolved_issues`; the packet carries a `staleness` block saying which
  checks ran. An empty list means "open" only when the matching check is
  reported as run — markers render from non-empty facts only, so an unmarked
  citation is never a freshness claim. Shipped in `2.11.2`.
- **The handoff budget counts CONTENT lines now, not file length.** Blank lines,
  the required `##` headings, and all of `## References` are free. Trimming
  formatting or shortening links buys nothing — cut state instead.
- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.

## Next Session

1. **Fix the bug-hunt backlog, in the order the record proposes.** Start with
   A1+A2 (the provenance guard exempts the repo's own `plugins/` install source,
   which is the 2026-07-27 incident's actual mechanism), then A3-A5 (the commit
   boundary: a deletion-only commit schedules zero gates today), then B1-B3 (the
   issue-close carrier, where a false PASS closes a real issue). Decide the
   cross-cutting move first: one shared typed scope field (evaluated / empty /
   not-configured) would close A4, A7, C5, D7, E2, E5 as a family.
2. **The drafter cannot see whether a staleness check ran.** The parser's
   top-level `staleness` block dies at `materialize_chunk_proposal_response`
   and the ranker packet — `ChunkCandidate` has no field for it. So the
   auto-draft marks positively-reported staleness (F9, now closed) but cannot
   distinguish "issue states checked, none closed" from "never asked". The
   path check always runs; the residual is issue citations only, because the
   issue check is gated behind `--with-issues`.
3. **D28 remainder** (`emit_payload_main --write`, scaffold fill guards). Fill
   guards want an observed n-fold rework instance before landing.
4. **Suite speed.** 11756 spawns, git 68% (`rev-parse` 1322, `ls-files` 774,
   `add` 672). In-process `run_script` is the unmeasured lever; spawn count is
   the honest metric, 16-worker wall-clock is noise.
5. **Sibling-scan Tier 2 finding D** (operator-scheduled). Two tests snapshot the
   real shared `.charness/usage-episodes/` tree and assert byte-identity after a CLI
   subprocess, so a live SessionStart hook or concurrent `run-quality.sh` fails them
   for unrelated reasons. Needs design; detail in the
   [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md).

## Discuss

- Run release/skill helpers from `skills/public/.../scripts/`, NOT the installed
  copy. An installed copy carrying an older lesson-index schema gets rejected by
  this repo's own gate mid-publish. The provenance guard now also runs at the
  irreversible entrypoints, but it lives in the copy you invoke, so a copy that
  predates it carries no check at all — that is how two `2.11.2` publishes got
  through. Target-side validators are the part that does not depend on caller
  age; [RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md).
- Skill loaders build a FRESH module object per import, with no `sys.modules`
  caching. Reading a module global back across a second load silently sees the
  unmutated copy; thread the value through explicitly instead.

## References

- [F9 critique](../charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md) · [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

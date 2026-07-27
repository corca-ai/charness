# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

The backlog is empty on the tracker — zero open issues. This session pushed the
prior run (closing #459) and closed F9: the auto-draft now marks stale citations.
[The F9 critique](../charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md)
holds ten findings, six rejected as over-worry. No decisions pending.

## Current State

- **The chunker reports staleness facts before ranking, and the auto-draft now
  renders them.** Each entry carries `missing_paths` / `closed_issues` /
  `unresolved_issues`; the packet carries a `staleness` block saying which
  checks ran. An empty list means "open" only when the matching check is
  reported as run — markers render from non-empty facts only, so an unmarked
  citation is never a freshness claim.
- **The handoff budget counts CONTENT lines now, not file length.** Blank lines,
  the required `##` headings, and all of `## References` are free. Trimming
  formatting or shortening links buys nothing — cut state instead.
- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.

## Next Session

1. **The drafter cannot see whether a staleness check ran.** The parser's
   top-level `staleness` block dies at `materialize_chunk_proposal_response`
   and the ranker packet — `ChunkCandidate` has no field for it. So the
   auto-draft marks positively-reported staleness (F9, now closed) but cannot
   distinguish "issue states checked, none closed" from "never asked". The
   path check always runs; the residual is issue citations only, because the
   issue check is gated behind `--with-issues`.
2. **`emit_payload_main --write` and scaffold fill guards (D28 remainder).** The
   report-all half is fully resolved; these two never were. Fill guards want an
   observed n-fold rework instance for the family in question before landing.
3. **Suite speed beyond the git-identity fix.** Census: 11756 spawns, git still 68%
   (`rev-parse` 1322, `ls-files` 774, `add` 672). The in-process `run_script` lever
   is unmeasured. Spawn count is the honest metric; 16-worker wall-clock is noise.
4. **Sibling-scan Tier 2 finding D** (operator-scheduled). Two tests snapshot the
   real shared `.charness/usage-episodes/` tree and assert byte-identity after a CLI
   subprocess, so a live SessionStart hook or concurrent `run-quality.sh` fails them
   for unrelated reasons. Needs design; detail in the
   [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md).

## Discuss

- A critique packet's default working-tree binding sweeps the critique artifact
  and the packet files themselves, so writing the artifact stales its own
  binding. Scope it with `--reviewed-path` to the surfaces actually reviewed.
  Same shape for the reviewer-boundary fingerprint: `verify` before applying
  act-before-ship fixes, or the drift it reports is your own.
- Skill loaders build a FRESH module object per import, with no `sys.modules`
  caching. Reading a module global back across a second load silently sees the
  unmutated copy; thread the value through explicitly instead.
- Two files sat exactly at their length cap, so small additions forced a split.
  Check `check_python_lengths.py` before growing a planner or a shared lib.

## References

- [F9 critique](../charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md) · [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

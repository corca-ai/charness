# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

**Push first.** The 2026-07-27 backlog run resolved #459 plus the three
operator-decided items, but its commit is unpushed, so #459 is still OPEN on the
tracker until `Closes #459` lands. [The run critique](../charness-artifacts/critique/2026-07-27-handoff-backlog-1-3-validator-cli-unification-chunker-staleness-facts-content-line-budget.md)
holds the ten findings and their dispositions. No decisions pending.

## Current State

- **The chunker now reports staleness facts before ranking.** Each entry carries
  `missing_paths` / `closed_issues` / `unresolved_issues`, and the packet carries
  a `staleness` block saying which checks ran. Read the block first: an empty
  list means "open" only when the matching check is reported as run.
- **The handoff budget counts CONTENT lines now, not file length.** Blank lines,
  the required `##` headings, and all of `## References` are free. Trimming
  formatting or shortening links buys nothing — cut state instead.
- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.

## Next Session

1. **Auto-draft renders a known-stale citation without a marker.** `_render_boundaries`
   lists a missing path as `- In scope:` and `_render_context_sources` lists a
   closed issue plainly, so the goal artifact asserts a moved path is in scope.
   The facts are correctly not acted on; they are just dropped at the last
   operator-facing surface. Deferred from the run's critique as F9.
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

- Skill loaders build a FRESH module object per import, with no `sys.modules`
  caching. Reading a module global back across a second load silently sees the
  unmutated copy; thread the value through explicitly instead.
- Two files sat exactly at their length cap, so small additions forced a split.
  Check `check_python_lengths.py` before growing a planner or a shared lib.

## References

- [run critique](../charness-artifacts/critique/2026-07-27-handoff-backlog-1-3-validator-cli-unification-chunker-staleness-facts-content-line-budget.md) · [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

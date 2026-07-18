# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.1.3 plugin.

## Current State

- The next operator can start new work without reopening the v2.1.3 release.
  Use the owning artifacts below and route the next task through its matching skill.
- v2.1.3 is public, independently read back over HTTPS, and installed on this
  maintainer machine. The release helper passed release quality, fresh-checkout,
  public-readback, and post-publish update steps. Separate `charness version`
  and `charness doctor` readbacks reported 2.1.3 with no source/cache drift; no
  real-host trigger matched this slice. See the
  [release state](../charness-artifacts/release/latest.md).
- Dead-code advisory review candidates fell from 9 to 2 after provenance-backed
  framework/source-scan classification and confirmed residue deletion. Dynamic
  exports remain visible for judgment. Exact changed lines passed the locked
  producer-to-consumer proof; see the
  [quality review](../charness-artifacts/quality/latest.md).
- Repo Markdown closeout now runs the existing spec-evidence durability check
  before broad pytest, so non-durable reproduction markers fail at their owning
  boundary. Stable manifest fixtures are read once per test module.
- Local release preparation now restores its clean starting commit and
  quarantines newly created non-ignored files when it fails before commit.
  Partial recovery stays explicit. If the release commit exists but the local
  tag does not, resume revalidates and tags that exact commit only before any
  remote/public publication. This shipped in v2.1.3.
- Focused mutation coverage selection now understands split `Path` references
  and nearest same-directory local-loader ancestry. The current unreleased range
  maps to four standing test files instead of requiring manual reconstruction;
  broad pytest and the changed-line consumer remain authoritative. This shipped
  in v2.1.3.

## Next Session

1. If no explicit task is present, run the workflow trigger above and choose the
   smallest coherent backlog slice.
2. For clean-start mutating workflows, enumerate owned mutations before coding
   and make every failure either restore the start state or emit a typed,
   resumable state. For irreversible operations, prove the exact consumed range.
   The checklist is in [recent lessons](../charness-artifacts/retro/recent-lessons.md).
3. Keep D18 ignored unless the operator explicitly reopens it.
4. For mutation-pool changes, ask the selector before widening a producer by
   hand: direct reference, nearest recognized loader ancestor, then broad
   fallback.

## Discuss

- Optional: a future live Codex-host session may record provider-applied
  `gpt-5.6-terra`/`medium` evidence. This is not a release or quality blocker.

## References

- [release state](../charness-artifacts/release/latest.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [release-recovery critique](../charness-artifacts/critique/2026-07-18-release-local-failure-recovery.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept ([release state](../charness-artifacts/release/latest.md)):
  public+installed v2.1.3, exact-range mutation proof, earlier durability
  routing, host-restart condition, and D18 disposition.
- Refresh non-claims ([quality review](../charness-artifacts/quality/latest.md)):
  detailed test/runtime history remains in the owning quality/release artifacts;
  no wall-clock speedup is claimed, no real-host trigger matched, and no
  Cautilus evaluation was run.

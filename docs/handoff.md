# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.1.2 plugin.

## Current State

- The next operator can start new work without reopening the v2.1.2 release or
  reconstructing the local release-recovery change. Use the owning artifacts
  below for proof details and route the next task through its matching skill.
- v2.1.2 is public, independently read back over HTTPS, and installed on this
  maintainer machine. The release helper passed release quality, fresh-checkout,
  public-readback, and post-publish update steps; no real-host trigger matched
  this slice. See the
  [release state](../charness-artifacts/release/latest.md).
- Lint-ignore inventory now separates rule identifiers from human rationales
  and falls back atomically after late Python tokenization errors. The exact
  changed lines passed producer-to-consumer mutation proof; see the
  [quality review](../charness-artifacts/quality/latest.md).
- Repo Markdown closeout now runs the existing spec-evidence durability check
  before broad pytest, so non-durable reproduction markers fail at their owning
  boundary. Stable manifest fixtures are read once per test module.
- Local release preparation now restores its clean starting commit and
  quarantines newly created non-ignored files when it fails before commit.
  Partial recovery stays explicit. If the release commit exists but the local
  tag does not, resume revalidates and tags that exact commit only before any
  remote/public publication. This work remains local and unpushed by request.

## Next Session

1. If no explicit task is present, run the workflow trigger above and choose the
   smallest coherent backlog slice.
2. For clean-start mutating workflows, enumerate owned mutations before coding
   and make every failure either restore the start state or emit a typed,
   resumable state. For irreversible operations, prove the exact consumed range.
   The checklist is in [recent lessons](../charness-artifacts/retro/recent-lessons.md).
3. Keep D18 ignored unless the operator explicitly reopens it.

## Discuss

- Optional: a future live Codex-host session may record provider-applied
  `gpt-5.6-terra`/`medium` evidence. This is not a release or quality blocker.

## References

- [release state](../charness-artifacts/release/latest.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [release-recovery critique](../charness-artifacts/critique/2026-07-18-release-local-failure-recovery.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept ([release state](../charness-artifacts/release/latest.md)):
  public+installed v2.1.2, exact-range mutation proof, earlier durability
  routing, host-restart condition, and D18 disposition.
- Refresh non-claims ([quality review](../charness-artifacts/quality/latest.md)):
  detailed test/runtime history remains in the owning quality/release artifacts;
  no wall-clock speedup is claimed, no real-host trigger matched, and no
  Cautilus evaluation was run.

# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.1.0 plugin.

## Current State

- The next operator can start new work without reopening the v2.1.0 release or
  reconstructing the YAML migration. Use the owning artifacts below for proof
  details and route the next task through its matching skill.
- v2.1.0 is public, independently read back over HTTPS, and installed on this
  maintainer machine. The release helper passed release quality, fresh-checkout,
  real-host, public-readback, and post-publish update steps; see the
  [release state](../charness-artifacts/release/latest.md).
- Every quality `inventory_*.py` producer and canonical inventory-dispatch
  command now offers compact `--summary` YAML and full `--detail` YAML. Hidden
  JSON remains only for programmatic compatibility; see the
  [quality review](../charness-artifacts/quality/latest.md).
- The first publish attempt safely stopped before commit/tag/push on cumulative
  changed-line coverage debt. Behavior-focused in-process tests repaired it,
  and the exact v2.0.0-to-release range passed before publication.
- The ordered-list evidence-continuation bug found during that repair is fixed
  in root and packaged code with positive and negative regression tests.

## Next Session

1. If no explicit task is present, run the workflow trigger above and choose the
   smallest coherent backlog slice.
2. For future cumulative or irreversible operations, prove the exact range the
   boundary consumes; do not assume individually green slices compose. The
   durable checklist is in [recent lessons](../charness-artifacts/retro/recent-lessons.md).
3. Keep D18 ignored unless the operator explicitly reopens it.

## Discuss

- Optional: a future live Codex-host session may record provider-applied
  `gpt-5.6-terra`/`medium` evidence. This is not a release or quality blocker.

## References

- [release state](../charness-artifacts/release/latest.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [release critique](../charness-artifacts/critique/2026-07-18-complete-inventory-yaml-contract-and-v2-1-0-release.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept ([release state](../charness-artifacts/release/latest.md)):
  public+installed v2.1.0, complete YAML-first inventory contract, the
  cumulative-range proof rule, host-restart condition, and D18 disposition.
- Refresh non-claims ([quality review](../charness-artifacts/quality/latest.md)):
  detailed test/runtime history remains in the owning quality/release artifacts;
  no external consumer-repo upgrade was exercised, and no Cautilus evaluation
  was run.

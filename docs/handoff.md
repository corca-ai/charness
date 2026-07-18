# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.1.1 plugin.

## Current State

- The next operator can start new work without reopening the v2.1.1 release or
  reconstructing its quality-infrastructure repair. Use the owning artifacts
  below for proof details and route the next task through its matching skill.
- v2.1.1 is public, independently read back over HTTPS, and installed on this
  maintainer machine. The release helper passed release quality, fresh-checkout,
  public-readback, and post-publish update steps; no real-host trigger matched
  this slice. See the
  [release state](../charness-artifacts/release/latest.md).
- Mutation closeout now executes and validates the authoritative changed-line
  consumer after its producer. Dirty eligible ranges report `NOT CHECKED`
  instead of borrowing a terminal green, while committed-range proof blocks on
  missing, stale, malformed, or uncovered evidence; see the
  [quality review](../charness-artifacts/quality/latest.md).
- The Nose-backed inventories share one transport owner, quality-runner seed
  setup is module-scoped with clone isolation, and mutation-consumer tests have
  a dedicated ownership module. The exact committed release range passed the
  producer-to-consumer proof before publication.

## Next Session

1. If no explicit task is present, run the workflow trigger above and choose the
   smallest coherent backlog slice.
2. For future cumulative or irreversible operations, prove the exact range the
   boundary consumes and execute generated verifier commands; do not treat an
   intermediate producer green as terminal. The durable checklist is in
   [recent lessons](../charness-artifacts/retro/recent-lessons.md).
3. Keep D18 ignored unless the operator explicitly reopens it.

## Discuss

- Optional: a future live Codex-host session may record provider-applied
  `gpt-5.6-terra`/`medium` evidence. This is not a release or quality blocker.

## References

- [release state](../charness-artifacts/release/latest.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [release critique](../charness-artifacts/critique/2026-07-18-quality-infrastructure-correctness-and-v2-1-1-release.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept ([release state](../charness-artifacts/release/latest.md)):
  public+installed v2.1.1, executable consumer proof, explicit dirty-range
  non-claim, host-restart condition, and D18 disposition.
- Refresh non-claims ([quality review](../charness-artifacts/quality/latest.md)):
  detailed test/runtime history remains in the owning quality/release artifacts;
  no wall-clock speedup is claimed, no real-host trigger matched, and no
  Cautilus evaluation was run.

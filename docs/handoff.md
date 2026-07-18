# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.1.5 plugin.

## Current State

- v2.1.5 is the fully verified release candidate and publication is the only
  remaining active step. The exact `v2.1.4..eae81f48` range passed cumulative
  broad pytest, fresh mutation coverage, and the changed-line consumer. Do not
  reopen implementation unless the release helper reports a typed blocker.
- After publication, reconcile this paragraph with the public URL and installed
  `charness version`/`charness doctor` readbacks. The release helper owns push,
  tag, GitHub release, independent HTTPS confirmation, install refresh, and the
  durable observer record. See the [release critique](../charness-artifacts/critique/2026-07-19-gajae-pattern-adoption-v2-1-5-release.md).
- The two recurring dead-code advisory findings are now classified as registered
  dynamic entrypoints only when conservative bidirectional AST evidence proves
  their callers. The live sweep reports two registered entrypoints and zero review
  candidates; wrong-path, wrong-loader, wrong-receiver, and disconnected-loop
  fixtures remain fail-closed. Exact changed lines passed the locked
  producer-to-consumer proof; see the
  [quality review](../charness-artifacts/quality/latest.md).
- The `../gajae-code` comparison is captured and its selected adoption sequence
  is locked in the [adoption plan](../charness-artifacts/spec/2026-07-19-gajae-code-adoption-plan.md).
  The first slice is the current app-server per-message deadline-reset bug.

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
5. When adding a new dynamic-call syntax, add wrong-path, wrong-loader,
   wrong-receiver, and disconnected-control-flow fixtures before recognizing it.
   Finish critique packets before taking reviewer boundary fingerprints, and run
   the focused duplication ratchet before broad validation for large AST helpers.
6. The Gajae-Code plan is implemented and locally locked. If v2.1.5 is not yet
   public, resume only the helper-owned release boundary; otherwise start a new
   smallest coherent backlog slice.

## Discuss

- Optional: a future live Codex-host session may record provider-applied
  `gpt-5.6-terra`/`medium` evidence. This is not a release or quality blocker.

## References

- [release state](../charness-artifacts/release/latest.md)
- [v2.1.5 release critique](../charness-artifacts/critique/2026-07-19-gajae-pattern-adoption-v2-1-5-release.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [release-recovery critique](../charness-artifacts/critique/2026-07-18-release-local-failure-recovery.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept ([release state](../charness-artifacts/release/latest.md)):
  v2.1.5 publication remains helper-owned; exact-range mutation proof, earlier
  durability routing, host-restart condition, and D18 disposition stay current.
- Refresh non-claims ([quality review](../charness-artifacts/quality/latest.md)):
  detailed test/runtime history remains in the owning quality/release artifacts;
  no wall-clock speedup is claimed, no real-host trigger matched, and no
  Cautilus evaluation was run.

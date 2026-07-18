# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.1.6 plugin.

## Current State

- v2.1.6 is public at the [GitHub release](https://github.com/corca-ai/charness/releases/tag/v2.1.6).
  The repo release gate passed, the tag and branch were pushed, and an
  independent HTTPS fetch returned 200. The maintainer install was refreshed;
  `charness version` confirmed 2.1.6 and `charness doctor` returned confirmed
  Codex-host guidance. This release closes no linked issue, so it makes no live
  auto-close timing claim. See the
  [release record](../charness-artifacts/release/latest.md),
  [observer record](../charness-artifacts/probe/2026-07-18-v2.1.6-release-observer.json),
  and [release critique](../charness-artifacts/critique/2026-07-19-v2-1-6-release-critique.md).
- Release publication now separates immutable content from the observer-bound
  issue-close carrier, validates complete restart inputs, and handles ambiguous
  pushes by remote identity. Planner evidence is compact and YAML-first; Git
  delta serialization and closeout artifact commits have cohesive owners.
  Duplicate coupling now fails during ordinary slice closeout, and the focused
  coverage selector recognizes release-local module loaders.
- The Gajae adoption goal is complete. Its exact-range repository proof passed
  cumulative broad pytest, fresh mutation coverage, and the changed-line
  consumer before publication. Do not reopen the bundle unless new evidence
  identifies a regression.
- The two recurring dead-code advisory findings are now classified as registered
  dynamic entrypoints only when conservative bidirectional AST evidence proves
  their callers. The live sweep reports two registered entrypoints and zero review
  candidates; wrong-path, wrong-loader, wrong-receiver, and disconnected-loop
  fixtures remain fail-closed; see the [quality review](../charness-artifacts/quality/latest.md).

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
6. The Gajae-Code plan and v2.1.6 release are closed; start a new smallest
   coherent backlog slice rather than resuming this goal.

## Discuss

- Optional: a future live Codex-host session may record provider-applied
  `gpt-5.6-terra`/`medium` evidence. This is not a release or quality blocker.
- Gate-baseline follow-up: preserve confidence while fixing mutation selector
  and parallelism economics. Broad instrumentation took 141.9-208.3s and the
  serial focused packet 333.8s versus a 120s budget, catching 4 bugs/29 gaps.

## References

- [release state](../charness-artifacts/release/latest.md)
- [v2.1.6 release critique](../charness-artifacts/critique/2026-07-19-v2-1-6-release-critique.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [release-recovery critique](../charness-artifacts/critique/2026-07-18-release-local-failure-recovery.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

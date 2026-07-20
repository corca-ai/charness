# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. Restart the host first
  only when the next task must observe the newly installed v2.3.0 plugin.

## Current State

- v2.3.0 is published and installed-host readback is recorded (distinct-channel
  release-URL fetch + `charness update`/`version`/`doctor`). It makes
  measurement-contract file discovery adapter-owned: a consumer repo declares
  its real test surface via `test_file_discovery` (fixing the `.mjs` undercount,
  issue #447) and its non-default linter directive syntax via
  `lint_ignore_discovery`, instead of the portable body re-deriving discovery and
  diverging from the repo's actual surface.
- A new advisory quality inventory `inventory_hardcoded_discovery` is a tripwire
  for that divergence class: it flags portable constants that hardcode a polyglot
  (2+ code-language-family) discovery list, which must be adapter-owned or carry
  an inline `# discovery-boundary: <reason>` marker. A broad lexical version was
  noise (71 sites); the narrow polyglot-only scope reads 0 unmarked on charness.
- Deferred follow-ups (recorded, not blocking): make the discovery-scan cover
  inline `.rglob`/`git ls-files` pathspec discovery (dropped to avoid the 71-site
  noise), expand `CODE_LANGUAGE_FAMILIES` (php/cs/swift/scala/elixir), and a
  stack-agnostic zero/near-zero test-surface advisory.
- Durable prior context (all closed): the Gajae adoption goal, dead-code review
  distinguishing proven dynamic entrypoints from candidates, and standing-xdist
  focused-proof speedups. Do not reopen without new regression evidence.
- Quality owns a portable proof-path efficiency method (define the current
  consumer envelope before boundary replacement; prove requires representative
  input consumption). Release resume requires exact peeled-tag identity.

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
   fallback; keep its canonical parallel-runner command.
5. When adding a new dynamic-call syntax, add wrong-path, wrong-loader,
   wrong-receiver, and disconnected-control-flow fixtures before recognizing it.
   Finish critique packets before taking reviewer boundary fingerprints, and run
   the focused duplication ratchet before broad validation for large AST helpers.
6. Treat the v2.3.0 release and the adapter-owned-discovery work as closed; start
   a new smallest coherent backlog slice rather than resuming it. The deferred
   discovery follow-ups above are candidates, not commitments.

## Discuss

- Decide an additive migration for issue closeout's terminal-sounding
  `verified` state; do not silently redefine existing artifacts.
- Persist pre-commit rollback outcomes and strengthen post-publication proof
  with an explicitly different observer identity, not only a different channel.

## References

- [release state](../charness-artifacts/release/latest.md)
- [portable proof/release critique](../charness-artifacts/critique/2026-07-19-portable-proof-path-and-release-identity-critique.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)

# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the
  backlog below (the operator-directed affordance convergence closed on
  2026-07-17). Restart hosts first only when testing installed-plugin
  behavior; an explicit user task keeps its own authority.

## Current State

- v2.0.0 is public: affordance convergence `7b20b0ce`, release `586c19e9`,
  tag/https verified. The release battery refused the first publish and the
  root fixes landed in `630bcfce`; see the
  [release state](../charness-artifacts/release/latest.md).
- v1.3.0→v2.0.0 migration note: the first `charness update` from an old
  binary crashes once (`KeyError: 'next_steps'`) after refreshing the
  checkout+binary; the re-run completes and reports `2.0.0`. This is recorded
  in the GitHub release notes and release state.
- The vocabulary and kept exceptions live in the
  [affordance spec](../charness-artifacts/spec/cli-output-affordance-contract.md).
- A local verified correction aligns agent-facing structured-output calls
  with that YAML vocabulary: public skill planners and the governing Cautilus
  preflight use YAML default/`--detail`; hidden legacy `--json` remains actual
  JSON for parser compatibility. Plugin exports and focused contract tests are
  included, but this work is not released or installed.
- The stale historical v0.56.7 round-5 goal is now `Status: complete` on
  immutable evidence, without current remote/install/v2 claims.

## Next Session

1. Decide the next-release scope for the local post-v2.0.0 changes, including
   the update/init self-heal and YAML planner-contract correction; do not infer
   publish authority from this handoff.
2. Restart now only to test the already-installed v2.0.0 surface. Testing the
   local correction requires a later authorized release/update first and is not
   proven by that restart.
3. D18 disposition (passed over 2026-07-17, still pending with the same
   reopen trigger) — see the 2026-07-16
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`.

## Discuss

- DONE 2026-07-17 (same session): the update/init self-heal shipped
  (`maybe_reexec_refreshed_cli`, pid-scoped guard, `cli_reexec` signal); see
  the [slice critique](../charness-artifacts/critique/2026-07-17-cli-reexec-self-heal-slice.md).
  Unreleased at refresh time — fold into the next release. Deferred there:
  the older end-of-init `cli_path` re-exec (F6) and the latent
  stale-standalone-CLI variant in non-refreshing consumers (F7).
- Optional under the 2026-07-17 per-host split: a live Codex-host session can
  still add provider-applied evidence that the Codex-scoped
  `gpt-5.6-terra`/`medium` request is honored; evidence polish, not a blocker.

## References

- [affordance spec](../charness-artifacts/spec/cli-output-affordance-contract.md)
  · [slice critique](../charness-artifacts/critique/2026-07-17-affordance-convergence-slice.md)
  · [release state](../charness-artifacts/release/latest.md) ·
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept (`AGENTS.md`): the published-v2.0.0 restart-to-load state
  (after a release/update), the carried D18 decision, the per-host reviewer
  contract, and the local-unreleased YAML planner correction.
- Refresh non-claims ([release state](../charness-artifacts/release/latest.md)):
  the migration-crash observation is one maintainer machine; no consumer-repo
  upgrade was exercised at refresh time; the convergence's payload renames
  are proven by the test suite and one live doctor/update run, not by
  external-consumer evidence; this session did not push, publish, update an
  installed plugin, or run Cautilus evaluation.

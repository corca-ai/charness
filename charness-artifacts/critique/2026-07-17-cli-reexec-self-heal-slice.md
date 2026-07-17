# CLI self-heal re-exec slice

Date: 2026-07-17

## Decision Under Review

Self-heal for the running-CLI → checkout code skew observed at the v2.0.0
publish: `charness update` from the old v1.3.0 binary refreshed the managed
checkout, then the old in-memory code crashed on the new installer payload
(`KeyError: 'next_steps'`). `maybe_reexec_refreshed_cli` now runs after
`ensure_checkout` in `cmd_update` and `cmd_init`: when the running CLI's
bytes differ from the checkout's `charness`, it re-executes the checkout's
CLI with the same argv; the re-exec child reports
`cli_reexec: {status: reexecuted}` (also copied into the summary
projection); a pid-scoped env guard blocks loops without being spoofable by
inherited environment values.

## Failure Angles

- Re-exec correctness: argv forwarding, exit-code propagation, stdout purity.
- Wrong-fire paths: dev-from-repo runs, in-process test callers, embedded
  bootstrap, tool flows; loop/fork-bomb risk and guard leakage.
- One-shot skip honesty and recoverability.
- Child payload honesty (`cloned: False` after the parent cloned).
- Missed sibling flows with the same skew class.
- Test honesty: do the tests pin what the code guarantees?

## Counterweight Pass

- Reviewer verified the clean angles directly: argv/flags forwarded (pinned
  by unit test), execve replaces the process so exit codes propagate, stdout
  stays one YAML doc (progress goes to stderr), the same-path guard excludes
  dev-from-repo runs, only the two clone/pull flows (`cmd_update`,
  `cmd_init`) can create the skew and both got the guard, and no recursive
  `charness` spawn exists for the guard to suppress. Real blockers: none.
- The one path that could reintroduce the original crash (finding F1) was
  real and cheap to close, so it was fixed in-slice rather than accepted.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness | action: fix | note: a pre-existing/foreign `CHARNESS_CLI_REEXECUTED` value silently defeated the self-heal (skip branch → the original crash class); fixed by pid-scoping the guard value — execve keeps the pid, so only the exec'd continuation matches, and a foreign value cannot suppress a legitimate re-exec (new unit test pins it).
- F2 | bin: act-before-ship | evidence: moderate | ref: charness | action: fix | note: comment and STEP text claimed the checkout is "newer" while the check is direction-less byte inequality; reworded to "code differs / matches its scripts", which also honestly covers the run-the-checkout's-own-code invariant for a stale checkout target.
- F3 | bin: valid-but-defer | evidence: moderate | ref: tests/charness_cli/test_managed_install.py | action: document | note: the re-exec child reports `cloned: False` even when the parent run cloned; `cli_reexec.status=reexecuted` is the paired signal consumers must read alongside `checkout.cloned` — documented in the e2e test comment and here; merging parent clone provenance across exec is deliberately not built.
- F4 | bin: act-before-ship | evidence: moderate | ref: charness | action: fix | note: `os.execve` failure was uncaught (would crash differently than the class being prevented); now falls back to a WARNING plus `cli_reexec: {status: failed}` and continues in-process (unit-tested).
- F5 | bin: over-worry | evidence: weak | ref: charness | action: document | note: an OSError on the child's re-check drops the `reexecuted` self-report (cosmetic, extreme edge); accepted.
- F6 | bin: valid-but-defer | evidence: moderate | ref: charness | action: document | note: the pre-existing end-of-`cmd_init` `os.execv` (cli_path re-exec, `EMBEDDED_REPO_ROOT` guard) now largely overlaps the new checkout re-exec; confirming/retiring it is deferred — pre-existing surface, not introduced here.
- F7 | bin: valid-but-defer | evidence: weak | ref: charness | action: document | note: non-refreshing checkout consumers (tool/goal/session-capture resolvers) cannot produce this slice's skew but carry a latent stale-standalone-CLI variant; explicitly deferred in the handoff Discuss list instead of silently omitted.

## Reviewer Tier Evidence

- Requested tier: high-leverage (crash-class repair on the update path).
- Requested spawn fields: per-host contract (AGENTS.md `Subagent Delegation`,
  split 2026-07-17) — Claude Code host convention applies: typed
  `bounded-reviewer`, session-model inheritance.
- Host exposure state: host-defaulted
- Application state: read-only envelope asserted by agent type (Read/Grep/
  Glob); parent-side boundary fingerprint verify returned `drift: []`.

## Fresh-Eye Satisfaction

parent-delegated — bounded read-only reviewer ran in the shared worktree over
the full working diff plus surrounding CLI flows;
`reviewer_boundary_fingerprint.py` snapshot/verify around the review returned
`ok: true` with empty drift. Reviewer verdict: approve-with-fixes; F1/F2/F4
fixed in-slice, F3/F5/F6/F7 dispositioned above.

## Boundary Ownership

- Producer: the root `charness` CLI update/init flows.
- Consumer: operators and automation running `charness update`/`init` across
  a version-skewed installed binary, including future breaking releases.
- Owning surface: the root `charness` CLI plus its unit/e2e tests; the
  v1.3.0→v2.0.0 one-time re-run note stays in the v2.0.0 GitHub release
  notes (this fix ships in a later release, so it cannot help binaries that
  predate it).
- Verdict: owned-correctly

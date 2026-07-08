# Resolution Critique — issues #424 and #425 (update-output auditability, merged NEXT_ACTION)

- **Target**: pre-commit resolution critique of the uncommitted diff that
  resolves #424 (`charness update all` output hides what changed: no
  from->to versions, one-line-per-run readability) and #425 (four next-step
  markers merged into one `NEXT_ACTION:` list).
- **Execution**: 3 bounded fresh-eye angle reviewers with distinct named
  lenses (data-flow correctness of version-transition capture,
  output-contract/downstream-consumer breakage, verification-channel
  fitness/test-coverage regression) + 1 separate counterweight reviewer;
  all completed their assigned lens directly.
- **Fresh-eye satisfaction**: parent-delegated (repo `Subagent Delegation`
  contract; four real subagent spawns via the host Agent tool).

## Reviewer Tier Evidence

- requested tier: high-leverage
- requested spawn fields: model `gpt-5.5`, reasoning_effort `medium`,
  service_tier `priority` (from `.agents/critique-adapter.yaml`
  `reviewer_tiers.high-leverage`)
- host exposure state: host-defaulted
- application state: not applied — the Claude Code host exposes only a
  per-subagent model override, not the Codex-shaped adapter fields;
  reviewers ran on the host default reviewer model.

## Change

Close #424 + Close #425. `scripts/update_tools.py` now captures a
`version_transition` (`from` read from the prior lock before persist,
`to` from the post-update detect probe) and persists it in the update
lock (`integrations/locks/lock.schema.json` gained the optional
`versionTransition` shape); `print_tool_statuses` and the CLI update
summary render it. The CLI `TOOLS:` summary became one line per tool
(`  - nose: updated 0.17.0 -> 0.18.0 (script)`) with an honest
`updated (version unknown)` fallback, and the package-manager next-step
message carries the transition. `_print_next_actions` merged
`NEXT_ACTION`/`CODEX_NEXT_STEP`/`CLAUDE_NEXT_STEP`/`REPO_NEXT_STEP` into
one prioritized `NEXT_ACTION:` list with exact-message dedupe and a
`repo` label derived from the payload `source` when the primary has no
host. JSON payload fields unchanged.

## Capability at Stake

Auditability of `charness update all` from its own output (an "updated"
that cannot be distinguished from a no-op reinstall hides surprise major
bumps that invalidate version-scoped baselines), and a single prioritized
operator instruction surface instead of four competing marker names.

## Structured Findings

- A | bin: bundle-anyway | evidence: contested | ref: scripts/control_plane_lifecycle_lib.py | action: fix | note: failed update rendering a real observed transition is kept deliberately (diagnostic: binary moved, healthcheck failed) and pinned with a unit test so it cannot drift silently.
- B | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/test_update_output.py | action: fix | note: fixture swap had dropped the only fast-lane coverage of the doctor-status fallback and doctor-sourced healthcheck suffix; restored via a doctor-only tool in the unit fixture.
- C | bin: bundle-anyway | evidence: moderate | ref: tests/charness_cli/test_doctor_next_action.py | action: fix | note: added single-marker count and old-marker absence assertions so the #425 merge outcome is proven, not just the narrow dedupe overlap.
- D | bin: bundle-anyway | evidence: moderate | ref: tests/charness_cli/test_update_output.py | action: fix | note: the CLI copy of the version-suffix logic had an untested from==to branch; pinned with a same-version tool in the unit fixture.
- E | bin: bundle-anyway | evidence: strong | ref: charness | action: fix | note: when repo-onboarding won the primary next_action, dedupe dropped the labeled repo line leaving an unlabeled entry; label now derived from payload source, covered by a fast-lane unit test.
- F | bin: valid-but-defer | evidence: moderate | ref: scripts/update_tools.py | action: document | note: repeated direct `update_tools.py --execute` runs (dev path) can report a phantom transition from a stale doctor observation; the supported CLI flow refreshes doctor locks after update and is immune.
- G | bin: over-worry | evidence: weak | ref: scripts/update_tools.py | action: document | note: `from` is lock-reconstructed, not probed pre-update, so an out-of-band update makes the rendered from stale; honest best-effort limitation recorded as a non-claim, no pre-update probe added.

## Counterweight Triage

- Act Before Ship: none.
- Bundle Anyway: A (keep-and-pin), B, C, D, E — all applied pre-commit.
- Valid but Defer: F (documented caveat, no timestamp logic in this slice).
- Over-Worry: G (non-claim); suppressing the transition on failed status
  (would hide the load-bearing fact an operator debugging a broken
  post-update needs); rewriting the historical
  `charness-artifacts/release/latest.md` captured output (frozen snapshot,
  no live consumer parses the old markers).

## Deliberately Not Doing

- No version-scoped-baseline boundary-crossing advisory line (the issue's
  "consider" item); it needs baseline-scope knowledge that does not belong
  in this rendering slice — recorded in the close comment as deferred.
- No pre-update version probe (G) and no doctor/update timestamp
  freshness arbitration (F) in this slice.
- No dedup of the duplicated version-suffix logic between the standalone
  installed CLI and `scripts/control_plane_lifecycle_lib.py`: the CLI is
  a self-contained installed file by design; both copies are now
  unit-pinned instead.

## Per-Issue Behavioral Verdict

**Behavior #424: verified** — distinct evidence channel: the counterweight
reviewer and this parent independently executed the focused pytest suites
and observed the rendered output: the fast-lane unit render shows
`  - nose: updated 0.17.0 -> 0.18.0 (script)`,
`  - agent-browser: updated (version unknown)`, `  - cautilus: manual`,
one line per tool; the release-lane end-to-end `update all` subprocess run
prints the multi-line `TOOLS:` block from the real installed CLI; and
`test_tool_lifecycle` asserts a real executed update persisted
`version_transition {from: 0.9.2, to: 0.25.3}` read from a genuinely
pre-existing seeded lock. Channel distinct from the GitHub `CLOSED` state
and the carrier body.

**Behavior #425: verified** — distinct evidence channel: executed doctor
subprocess run of the installed CLI shows exactly one `NEXT_ACTION:`
marker (`stdout.count == 1`), the `  - claude:` prefixed entry, the
deduped message appearing exactly once, and zero occurrences of
`CODEX_NEXT_STEP`/`CLAUDE_NEXT_STEP`/`REPO_NEXT_STEP`; the repo-label
edge is covered by a fast-lane unit test of `_print_next_actions`.
Channel distinct from the GitHub `CLOSED` state and the carrier body.

## Boundary Ownership

- Producer: `scripts/update_tools.py` produces the `version_transition`
  fact and persists it in the update lock; `charness` (installed CLI) and
  `scripts/control_plane_lifecycle_lib.py` render it;
  `_print_next_actions` in `charness` owns the merged human next-step
  rendering.
- Consumer: operators and agents reading `charness update all` / `doctor`
  human output; lock readers validating against
  `integrations/locks/lock.schema.json`; JSON consumers (unchanged
  payload fields).
- Owning surface: root CLI + `scripts/` with their `plugins/charness/`
  mirrors (synced and byte-identical); tests under `tests/charness_cli/`.
- Verdict: owned-correctly

## Next Move

Commit the fix + bundles with the `Closes #424` / `Closes #425` carrier,
push, and run `issue_tool.py verify-closeout --expect-state CLOSED`.

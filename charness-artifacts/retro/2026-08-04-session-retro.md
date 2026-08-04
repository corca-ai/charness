# Session Retro

Date: 2026-08-04
Goal: `make-recurring-closeout-cost-actionable`

## Context

This retro covers S1–S7 of the active goal: the #503 telemetry cohort and
decision receipt, the narrow #496 refill repair, final local proof, the v3.2.0
release, and its remote, public, and installed readbacks. The strongest claims
are execution claims with durable evidence; future operator uptake and runtime
relief remain unproven.

## Window

The window runs from the goal's local slices and release preparation through the
release-content commit `2a652b18de280fa50d0f1e46f9caebe41c70755a` and the
post-publish evidence commit `a12b2779`, both on 2026-08-04. It includes the
final public page and install readbacks recorded after publication.

## Evidence Summary

- #503's selected cohort has one `phase=verify`/command key, 16 matching
  entries, 12 completed and 4 failed parent records, 6,257.15 seconds total,
  447.03-second median, 475.46-second peak, a 120-second budget, and
  4,337.15 seconds of paired excess. The decision receipt is opt-in and
  read-only; it changes no emitter schema, gate, or CI behavior. Measured local
  relief is 0 seconds and is not presented as a success claim.
- #496's repair is an exact field-scoped allowlist with configured siblings
  preserved. The final release quality bundle reported 85 checks passed and 0
  failed; the post-repair markdown-preview/miner focused suite reported 36
  passed, and the renderer-specific suite reported 20 passed. Issues #496 and
  #503 remain open.
- The final deterministic lock completed at `2026-08-04T02:25:42Z` in 46.31
  seconds, with the recorded checks passing. No Cautilus evaluation was run.
- Release quality completed with 85 passed and 0 failed in 168.19 seconds.
  The normal pre-push gate completed with 85 passed and 0 failed in about
  162.8 seconds. Clean-checkout startup probes passed before publication.
- The delegated release critique's clean second round recorded the release
  claims conditions and the F9 branch/CI ordering limitation. The markdown
  preview repair had a first bounded reviewer hold on portable `script` flags
  and missing branch coverage (`019fcaaa-ea95-7413-9ef6-f3ebd6927d38`); after
  repair, `019fcaad-ab74-7602-bf11-9e594cd55de1` accepted the source/plugin
  pair and focused proof with a clean boundary verify.
- The release-content SHA was read back through the GitHub branch and commit
  APIs. Actions run `30874005717` read back at the exact SHA with both core and
  changed-line mutation jobs successful. Tag `v3.2.0` resolves to that exact
  release-content SHA. The release helper and an independent HTTPS page read
  both confirmed the public release; the unauthenticated REST API returned 403
  rate limiting and is recorded as unavailable, not as proof.
- `charness update`, `charness version`, and `charness doctor` read back the
  installed/source/cache surfaces at 3.2.0 with no cache drift. Baton reconcile
  was explicitly n/a because `docs/handoff.md` has no release-version claim.
  Full boundary evidence is in
  `charness-artifacts/release/v3.2.0-public-readback.md`.
- The host-log probe is persisted at
  `charness-artifacts/probe/2026-08-04-goal-host-log-probe.md`. It found no
  goal metric window, so its thread-wide signals do not support per-goal
  token, tool, turn, or cost totals.
- Packet consumed: `charness-artifacts/retro/2026-08-04-session-retro-packet.md`.

## Waste

- `truth-surface-rebinding` — the support repair changed reviewed truth
  surfaces after the release critique, so the candidate scope, critique packet,
  packet identity, and release evidence had to be rebound. The extra prep and
  packet refreshes were necessary once the repair was real, but the avoidable
  part was letting the release packet span an unfrozen support surface. Decision:
  same waste, fix now. Proof: the final packet identity and candidate scope were
  regenerated after the last reviewed repair.
- `non-tty-proof-boundary` — the first release preparation exposed that a piped
  `glow` invocation could produce a blank capture. The PTY fallback repair and
  its first fresh-eye hold were real safety work, not cosmetic churn. Decision:
  same waste, fix now. Proof: source/plugin parity, fallback tests, and the
  second bounded review are recorded above.
- `release-boundary-ordering` — the release helper's natural sequence did not
  interpose remote branch CI before tag/public publication. The limitation was
  caught by F9 before it escaped; the publish was manually split into branch
  push, independent CI readback, tag/publication, and independent readback.
  Decision: valid follow-up outside the slice. Proof: the release readback and
  the durable D51 entry in `docs/deferred-decisions.md`.
- `gate-baseline-runtime` — the release and pre-push gates measured about 168.19
  and 162.8 seconds. This is quality debt and an optimization target, not a
  reason to weaken floors or shrink test scope. Decision: valid follow-up
  outside the slice. Proof: D51 records the named owner surface and reopen
  trigger in `docs/deferred-decisions.md`.
- `quality-gate-branch-coverage` — the first release prep found genuine
  uncovered changed lines in the miner and renderer, requiring focused tests
  and another full release gate. Decision: same waste, fix now. Proof: the
  later 85-check release gate and the focused suites passed after those tests.
- Missing host metric window was not treated as waste or backfilled by
  inference. It is a measurement boundary and remains an explicit non-claim.

## Critical Decisions

- Kept #503's receipt opt-in and read-only. The local result is 0 seconds of
  measured relief; no emitter schema, gate, or CI change was invented to make
  the recurring signal look resolved.
- Kept #496's repair field-scoped and allowlisted. The empty-value predicate was
  not generalized to unrelated configured fields.
- Added the PTY path only for the non-TTY capture boundary and retained a
  direct `glow` fallback when `script` is missing or unsupported. This was
  accepted only after a distinct second review read the repaired surface.
- Split release publication around the remote branch/CI observation instead of
  treating the release helper's exit code as CI proof.
- Did not close issues #496 or #503; release/public/install proof does not imply
  issue closure.

## Trends vs Last Retro

The immediately prior checked-in retro is for a different goal and has no
comparable goal-scoped host metric window. The current probe likewise reports
`Host metric window: absent`, so no numeric trend in tokens, turns, tools, or
cost is claimed. Qualitatively, this session repeated the prior positive
pattern that a distinct observer caught a proof-surface gap before publication,
and converted the lesson into a durable follow-up rather than weakening a gate.

## North Star Alignment

- Held P1, P4, and P5 at the release boundary: local proof, remote commit/CI
  readback, public page readback, and installed doctor/version readback were
  treated as separate observations and channels.
- Initially misapplied the capture boundary: a local green release preparation
  did not prove that piped Markdown rendering was trustworthy, and the first
  reviewer correctly held on the portable `script` assumption. The repair added
  fallback behavior and branch proof before publication.
- The failure signature was “terminal green is not remote/public proof.” The
  branch/tag helper ordering issue was caught before publication, and the
  manual sequence preserved the different-observer requirement.
- The #503 and #496 issue boundaries remain honest: local implementation proof
  is recorded, but remote issue closure is not claimed.

## Expert Counterfactuals

- Engelbart's system-improving lens (human method + language + artifact/tool)
  says the critique packet, release helper, and closeout readback should make
  the branch/CI barrier executable and observable, not merely describe it in
  prose. D51 is the durable next owner for that repair.
- An Ousterhout-style lens would have made the release state machine's
  transitions explicit: branch published, CI observed, tag published, public
  release observed, install refreshed. The current helper bundles too much
  ordering, which is why the session had to separate those transitions manually.

## Sibling Search

- same layer: release helper `_publish_and_finalize` and the release quality
  runner | decision: valid follow-up outside the slice | proof: inspected the
  helper ordering and the measured 168.19/162.8-second gates; follow-up:
  `docs/deferred-decisions.md#d51-release-branchci-barrier-and-quality-gate-runtime`
- abstraction up: release adapter and the north-star publication boundary |
  decision: intentional boundary | proof: the adapter remains host-portable and
  the manual distinct-channel sequence is recorded in the public readback.
- specialization down: `markdown_preview_render.py`, its source/plugin mirror,
  and `check_glow_backend` | decision: same waste, fix now | proof: fallback
  branches, source/plugin comparison, focused tests, and second-round review.
- mental-model siblings: #503/#496 carriers, release notes, and final
  disposition | decision: diagnostic-only | proof: each carrier keeps its own
  owner, predicate, and proof channel; no universal semantic policy was added.

## Next Improvements

- Workflow: freeze the release candidate and refresh its critique packet only
  after the final implementation surface is stable.
- Capability: teach the release helper to expose and persist the branch-push,
  remote-CI, tag, public-release, and install-refresh states with explicit
  observers; D51 owns this follow-up.
- Quality: run changed-line coverage immediately after focused branch additions
  and before the broad release gate; this was applied in this session.
- Memory: require a host metric window for any per-goal host-cost claim; when it
  is absent, persist the probe and state the non-claim.
- Artifact: keep release-content proof separate from post-publication remote,
  public, and installed readbacks; this was applied in the two release records.

## Packet Consumed

Packet Consumed: `charness-artifacts/retro/2026-08-04-session-retro-packet.md`

## Host Metrics

Host metric window: absent. See
`charness-artifacts/probe/2026-08-04-goal-host-log-probe.md`; no per-goal host
metric total is claimed.

## Persisted

Persisted: yes: `charness-artifacts/retro/2026-08-04-session-retro.md`

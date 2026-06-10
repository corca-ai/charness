# v0.38.0 release critique

Date: 2026-06-10

## Decision Under Review

Cut charness 0.38.0 (minor bump from 0.37.0) at pushed HEAD ec919d07 via
the repo-owned coupled publish helper (version + tag + GitHub release +
adapter-declared post-publish install refresh). Delta: the 2026-06-10
post-push goal's two capability slices (deleted-checkout settings scan;
F4 e2e via the PR-mirror's first real execution) plus artifact-only
records and an inert next-queue draft goal.

## Failure Angles

- Wrong bump level (operator-visible new exit-1 cause vs additive).
- Consumer repos inheriting new blocking behavior from the settings scan.
- The `toml_command_value` rename stranding an external consumer.
- Stale generated surfaces / version drift / missing mirror in the delta.
- Releasing before required CI proof (post-push run, scheduled mutation
  run) or with a stale release artifact/update_instructions.
- Update notes the next maintainer could misread.

## Counterweight Pass

- Real and folded: the 0.38.0 update_instructions entry was added to the
  release adapter before publish with the degrade contract spelled out
  (status-mode only, foreign hooks never flagged, silence on absent
  settings, init/update unaffected) and the rename named; the delta
  narrative accounts for all 8 commits including the artifact-only
  v0.37.0 verification record (reviewer nit 4).
- Over-worry: bump level (minor precedented by 0.37.0's structurally
  identical hook_liveness exit-1 cause; degrade contract verified
  concretely in code — consumers inherit no blocking behavior); rename
  (underscore-private, zero external references, mirror byte-synced);
  pending scheduled mutation run (post-release verification lane per the
  v0.37.0 precedent — quality-core on the release SHA is already green,
  which was the only CI wait the prior release imposed); the advisory-only
  requested-review warning (pre-existing posture).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml update_instructions | note: the 0.38.0 entry must land before publish (staleness guard) and must spell the new exit-1 cause, the basename-derived scan scope, the degrade contract, and the toml_command_value rename so the next maintainer cannot misread the operator-visible edge. Fixed: entry added and adapter validated pre-publish. | action: fix
- F2 | bin: bundle-anyway | evidence: strong | ref: git log v0.37.0..ec919d07 | note: stated delta said 6 commits; the range holds 8 (includes 3310b28b, the artifact-only v0.37.0 verification record, and the lesson-index refresh) — accounted in the release narrative as artifact-only. | action: document
- F3 | bin: over-worry | evidence: strong | ref: scripts/host_hook_registry.py settings_file_scan; scripts/reconcile_usage_episodes_host_hooks.py | note: consumer-blocking worry refuted concretely — status-mode only, basename-known filter, live entries never flagged, silence on absent/unreadable settings; no gate invokes status mode (run-quality.sh, .githooks, doctor.py all clean). | action: document
- F4 | bin: over-worry | evidence: strong | ref: charness-artifacts/critique/2026-06-10-v0-37-0-release-critique.md F2 precedent | note: the scheduled mutation run over the pushed state is the standing post-release verification lane (the next-queue draft goal's slice 1 consumes it), not a tag precondition; quality-core on ec919d07 is completed success. | action: document

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye subagent reviewer (separate agent context, read-only, prior state via git show/log, read-only gh).
- Requested spawn fields: subagent_type=general-purpose, name=release-critique, bounded release packet (delta, probe/gate state, five review angles, update-notes drafting ask).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned the reviewer verdict (named reviewer release-critique, 15 tool uses, ~185s; independently verified version-surface consistency at 0.37.0, mirror cmp on all four changed scripts, the 8-commit delta, the no-gate-invokes-status grep, and the v0.37.0 critique precedent).

## Fresh-Eye Satisfaction

Verdict: SHIP-WITH-NITS, no blockers (named reviewer release-critique).
The reviewer confirmed the minor bump, the consumer degrade contract, the
rename safety, hygiene (no drift, mirrors byte-identical, tree clean), and
that nothing in the delta blocks the tag; nits F1 (update_instructions
prep) and F2 (delta accounting) folded before publish.

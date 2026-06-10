# Deleted-checkout settings scan slice critique

Date: 2026-06-10

## Decision Under Review

Slice 2 of the post-push goal
(`charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror.md`):
close the documented #343 blind spot by adding `settings_file_scan(home)` to
`scripts/host_hook_registry.py` — a direct read of the host settings files
(claude `settings.json`, codex `hooks.json`, codex `config.toml`) flagging
entries whose command carries a known charness hook-script basename but whose
embedded path no longer exists — wired into `--mode status` as a
`settings_scan` section joining the existing exit-1 drift list.

## Failure Angles

- The scan could flag a foreign hook or mutate consumer settings.
- The known-basename set could fork from the owning modules' constants.
- The exit-1 join could leak into `charness init`/`update` (reconcile mode)
  or a CI surface that calls status.
- The public rename of `toml_command_value` could strand an importer.
- Degrade-to-silence could fail on unreadable/malformed settings shapes.
- The TOML identification (basename, not marker block) could diverge from
  the goal text dishonestly.

## Counterweight Pass

- Real and folded: the dead `intents` parameter on
  `known_hook_script_basenames` is now passed through from
  `settings_file_scan` (reviewer nit 2); the basename-not-marker TOML
  decision and the direct-exec edge are recorded below and in the slice log
  (nits 1, 3).
- Over-worry: foreign-hook flagging (skipped before listing; zero writes;
  per-format silence tested), rename safety (zero stale references repo-wide,
  lib+registry ship as a unit), exit-1 leakage (reconcile mode untouched;
  status already derived exit 1 from `in_sync`; no CI surface calls status),
  payload additivity (explicit key set after the spreads).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: weak | ref: scripts/host_hook_registry.py _command_script_path | note: a hand-written direct-exec entry (`/abs/<known>.py ...`, no interpreter token) whose script EXISTS is reported dangling as "no script path found" — the basename match sees any-position `.py`, the path extractor deliberately skips tokens[0]. Inherited posture from hook_state_liveness (loud over silent on commands charness never wrote); advisory-only. | action: document
- F2 | bin: act-before-ship | evidence: moderate | ref: scripts/host_hook_registry.py settings_file_scan | note: `known_hook_script_basenames()` was called without the intents passthrough, leaving the parameter dead for the only production consumer. | action: fix
- F3 | bin: bundle-anyway | evidence: moderate | ref: scripts/host_hook_registry.py _toml_settings_commands | note: goal text said "config.toml charness-marker blocks"; shipped scan reads every `command = "..."` line and filters by known basename — strictly broader and safe (foreign basenames skipped); docs paragraph claims exactly the shipped behavior. | action: document

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye subagent reviewer (separate agent context, read-only, prior state via git show; uncommitted diff via git diff).
- Requested spawn fields: subagent_type=general-purpose, name=slice2-critique, bounded slice packet (intent, changed files + mirrors, invariants, tests/proof, non-claims, out-of-scope, reviewer questions a-e).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned the reviewer verdict (named reviewer slice2-critique, 28 tool uses, ~290s; independently re-ran the module + family tests 64/64, cmp'd all three mirrors, ruff + length gate, and traced the status/reconcile exit-code paths in the charness CLI).

## Fresh-Eye Satisfaction

Verdict: SHIP-WITH-NITS, no blockers (named reviewer slice2-critique).
The reviewer confirmed the derivation is single-source against the live
constants, foreign hooks cannot be flagged or touched, reconcile/install/
uninstall are unaffected, the rename leaves no stale importer, and the e2e
subprocess test proves the headline deleted-checkout case (empty state +
scratch-home leftover → flagged, exit 1). Nit F2 folded before commit;
F1/F3 recorded here and in the slice log.

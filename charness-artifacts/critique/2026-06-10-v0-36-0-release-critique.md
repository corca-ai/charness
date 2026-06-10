# Critique Review
Date: 2026-06-10

Goal: ship charness v0.36.0 (minor, 0.35.0 →) — push origin/main..HEAD (the
2026-06-10 next-queue goal bundle, 10 commits) and publish via the repo
publish helper.

## Decision Under Review

Whether the v0.36.0 release is safe to push + publish: the bundle ships the
`run_slice_closeout --base` option, the adapter-declared edit-time #N-anchor
PostToolUse hook (installed onto maintainer machines by the next `charness
update`), the first push/tag CI workflow (this push triggers its first-ever
remote run), six commit-time timing pulls, and an additive public-skill
parity-policy keyword (`local-gate-subset-mirror`).

## Failure Angles

- `charness update` on another machine installs a PostToolUse hook whose
  embedded script path does not exist (dangling-path, exit-2 noise on every
  Edit) — the highest-risk install/update seam.
- The first quality-core CI run failing in a way that blocks work (required
  status) rather than just showing red.
- The new parity-policy keyword silently changing consumer gate behavior
  without opt-in.
- A wrong bump level (compatibility break hiding in the plugin exports).
- A stale release record / update_instructions misleading operators.
- Secrets or machine-local paths in the 10 commits.

## Counterweight Pass

- Hook path traced concretely: `charness update` refreshes the source
  checkout BEFORE reconciling, and `build_command` embeds
  `<checkout>/scripts/post_edit_skill_anchor_guard.py` — a committed file
  that exists post-pull; a stale checkout's old adapter lacks the intent and
  takes the uninstall/no-op path; basename dedupe prevents double-install
  against this machine's dev-checkout hook. Safe.
- CI first run: `permissions: contents: read`, no required-status branch
  protection, mutation-mirror job is PR-only — a red first run is a red
  check only; triage is slice 3 of the already-shaped next goal.
- Parity keyword: exemption requires a declared marker; markerless consumers
  see zero change (previously-unknown keyword warned + standard-enforced).
- Bump: everything additive (new scripts, opt-in adapter/schema section,
  `--base` with unchanged default, existence-guarded gate pulls); no
  removed/renamed plugin exports → minor is right.
- Release record: the publish helper regenerates
  `charness-artifacts/release/latest.md` for the target version
  (`write_release_artifact`); update_instructions staleness is guarded by the
  helper's HOLD + the `--prep-update-instructions` step (run before publish).
- Diff scan: no secrets/tokens/machine-local paths in added lines; the
  lesson-selection-index churn is regenerated state per artifact policy.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml | action: fix | note: update_instructions still describes 0.35.0; the publish helper's staleness guard would HOLD — run `publish_release.py --prep-update-instructions --part minor` and commit the stub before `--execute` (the designed flow, executed in this release lane).
- F2 | bin: valid-but-defer | evidence: strong | ref: scripts/reconcile_usage_episodes_host_hooks.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/343 | note: no dedicated uninstall surface for the anchor-guard hook; a deleted checkout leaves a dangling PostToolUse hook (exit-2 on every Edit, louder than the SessionStart class). Already filed as #343 and slice 2 of the shaped next-queue goal — tracked, not a release blocker.
- F3 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/ci_local_gate_parity_lib.py | action: document | note: a consumer who already declared the exact previously-unknown `local-gate-subset-mirror` keyword would silently flip from warned+standard-enforced to exempt — implausible collision; the doc section defines the contract.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: fresh-eye release reviewer (separate subagent context, read-only, bounded packet).
- Requested spawn fields: the 10-commit diff, the six release-critical questions (install/update hook-path trace, CI first-run blast radius, consumer keyword inheritance, bump level, release-record staleness, should-not-ship scan).
- Host exposure state: applied
- Application state: host-confirmed: tool signal: a bounded fresh-eye subagent ran via the Agent tool and returned a structured SHIP-WITH-NITS verdict with the concrete hook-path trace (charness:3311/3344 ensure_checkout-before-reconcile, host_hook_install_lib.py:97-99 build_command, the #245 basename-dedupe check against the live settings file) and the publish-helper record-regeneration trace (publish_release_cli.py:132 → write_release_artifact).

## Fresh-Eye Satisfaction

Reviewer verdict: SHIP-WITH-NITS — no blockers; both nits are tracked (F1 is
the designed prep step, executed in this lane before `--execute`; F2 is
issue #343, slice 2 of the shaped next goal). The highest-risk seam (hook
install path on updated machines) was traced to a committed file in a
freshly-pulled checkout with stale-checkout and double-install edges both
closing safely. Concrete signal: the reviewer's file:line trace chain,
independently spot-checked (build_command resolves repo_root-relative;
`cmd_update` orders ensure_checkout before reconcile).

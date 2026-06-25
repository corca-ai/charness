# v0.56.0 release critique
Date: 2026-06-26

## Decision Under Review

Publish Charness `v0.56.0` from `origin/main..HEAD`, carrying quality-review
efficiency changes, standing pytest runner refinements, and optional headless
`web-fetch` fallback stages.

Success means the release locks the checked-in plugin/export surfaces with
honest operator notes, no release gate blockers, and no claim that optional
headless fallbacks bypass active site blocking.

## Release Scope

- Current version: `0.55.2`.
- Target version: `0.56.0` / tag `v0.56.0`.
- Consumer change: optional `curl_cffi` and headless Patchright web-fetch
  fallbacks, compact quality inventory summaries, standing pytest execution
  refinements, and refreshed quality ratchet baselines.

## Surface-Lock Inventory

- Generated/install surfaces: `plugins/charness/**`, `.claude-plugin/**`,
  `.agents/plugins/**`, `packaging/charness.json`.
- Consumer-visible behavior: `support/web-fetch` route planning,
  HTTP-error classification, optional headless fallback traces, and standing
  pytest worker/default behavior.
- Documentation/operator surfaces: `charness-artifacts/release/v0.56.0-notes.md`,
  `skills/support/web-fetch/SKILL.md`, and web-fetch runtime/routing references.
- Quality artifacts: `charness-artifacts/quality/dup-ratchet-baseline.json`,
  quality summary records, and committed tests for the new behavior.

## Failure Angles

- Gawande operational angle checked release gates, duplicate ratchet state,
  fresh-checkout proof posture, install/update concerns, and manifest/export
  sync.
- Minto communication angle checked whether operators get a clear release story
  instead of a changed-file inventory, and whether the notes overstate proof.
- Raskin interface angle checked installed-user affordance for optional
  `curl_cffi`/Patchright dependencies and whether Patchright behavior is
  portable and trace-visible.

## Counterweight Pass

- The release notes gap was real and is fixed by
  `charness-artifacts/release/v0.56.0-notes.md`, including non-claims for
  blocked-site access, challenge bypass, and quality-summary proof strength.
- Patchright locale/timezone concern was real before release lock-in and is
  fixed: the renderer now uses the browser default context and records
  `locale: browser-default` plus `timezone_id: browser-default` in attempt
  details.
- Duplicate ratchet was a real release blocker. The baseline was regenerated
  after the final source/plugin/test edits, and
  `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
  now reports `status: clean`.
- Optional `curl_cffi` and Patchright dependency management is real but cheap:
  the release notes state that `charness update` does not install them and the
  runtime records `missing-tool` skips when absent.
- Real-host proof is handled by the release helper's fresh-checkout and
  post-publish install-refresh path; no separate Cautilus proof is required for
  this slice.
- Helper length warnings and a human-readable support-helper wrapper are valid
  follow-up concerns, not release blockers.

## Operator Action Required

- Use `charness-artifacts/release/v0.56.0-notes.md` as the release notes file.
- Run the repo-owned release helper with a minor bump and this critique artifact.
- After publish, trust only the helper's public visibility, distinct-channel,
  fresh-checkout, and install-refresh evidence for release-complete claims.

## Upgrade Path

- Operators run `charness update`.
- Active Codex/Claude sessions should restart or refresh after install cache
  rotation.
- Operators who want the new optional fallback routes must install `curl_cffi`
  and/or Patchright separately; absent optional tools are traced as
  `missing-tool` rather than treated as release failures.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/v0.56.0-notes.md | action: fix | note: release notes now state operator story and non-claims before tag publication
- F2 | bin: act-before-ship | evidence: strong | ref: skills/support/web-fetch/scripts/patchright_headless_stage.py:40 | action: fix | note: Patchright context now uses browser defaults and records locale/timezone details
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/quality/dup-ratchet-baseline.json | action: fix | note: duplicate ratchet baseline refreshed after final edits and the gate reports clean
- F4 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/release/v0.56.0-notes.md | action: document | note: optional curl_cffi and Patchright dependencies are noted as not managed by charness update
- F5 | bin: valid-but-defer | evidence: moderate | ref: docs/handoff.md#next-session | action: defer | note: split near-limit web-fetch helper and direct human-readable wrapper later

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: host exposed `spawn_agent` with reasoning/service fields; application beyond submitted fields is not independently confirmed.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated.

Angle reviewers ran as separate subagents for Gawande, Minto, and Raskin
release lenses; a separate counterweight reviewer triaged their findings into
Act Before Ship, Bundle Anyway, Over-Worry, and Valid but Defer. Packet consumed:
`charness-artifacts/critique/2026-06-25-211733-packet.md`.

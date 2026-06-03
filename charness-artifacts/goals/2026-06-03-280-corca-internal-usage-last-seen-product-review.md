# Achieve Goal: Issue 280 Corca internal usage last-seen product review

Status: complete
Created: 2026-06-03
Activation: `/goal @charness-artifacts/goals/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete; release routing remains the next workflow step.
- Next action: commit the completed goal and implementation, then route the
  user-requested push release through `release`.
- Verification cadence: cheap deterministic checks for schema/report/doc changes;
  focused tests for reporter semantics; fresh-eye critique before enabling any
  auto-filing or Corca-internal collection path.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files, expected invariants, privacy boundary, issue/comment examples,
  tests/proof, non-claims, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Design and, if activated, implement the first Corca-internal product-review loop
for Charness usage evidence from #280, building on #184's rule that artifact
creation is not satisfaction proof.

The goal is to support privacy-safe release-window or review-window reporting
that shows when Corca repos/users were last observed using Charness and can
append reporter-only GitHub issue/comment packets for agreed friction or
missed-detection evidence. The system must expose `first_seen_at`,
`last_seen_at`, usage counts, version/update context, and non-claims without
classifying inactivity as churn or prescribing fixes.

## Non-Goals

- Do not classify `stop-using`, churn, dissatisfaction, or satisfaction from
  inactivity, usage drops, update declines, or silence.
- Do not connect update acceptance to satisfaction. Update prompts are a
  distribution/maintenance loop, not product-success proof.
- Do not send public or external-repo telemetry by default.
- Do not store or transmit raw prompts, transcripts, private source bodies, or
  personal content.
- Do not let the reporter script diagnose root cause or recommend fixes. It may
  state observations, thresholds, evidence refs, confidence gaps, and triage
  questions.
- Do not file issues or comments for raw episode count growth, first-value
  artifacts, last-seen staleness, or update prompts alone.
- Do not close #184 as a result of this goal. #184 remains the broader
  product-success synthesis issue.

## Boundaries

- In scope: issue #280, #184 product-success context, usage episode reporting
  docs, usage episode schemas, local reporter scripts, GitHub issue/comment
  formatting, and Corca-internal API seam documentation if implementation
  reaches that layer.
- In scope: a reporter-only packet shape for release-window/review-window
  summaries and threshold-triggered friction/missed-detection evidence.
- In scope: dry-run/report-only behavior before any mutating issue/comment path.
- In scope: enough structured output for a future dashboard to show
  `last_seen_at` and related windows without implying churn.
- Out of scope unless explicitly discussed: hosted analytics infrastructure,
  external customer telemetry, dashboard UI implementation, user outreach
  automation, and automatic update installation.
- Stop if the proposed data model needs raw transcript/prompt content.
- Stop if the implementation would make inactivity a machine-authored negative
  product signal.
- Stop if auto-filing cannot be explained as a reporter packet that leaves
  diagnosis to the repo agent/human.

## User Acceptance

- The user can inspect #280 and product-success docs and see that last-seen is a
  review field, not a churn/satisfaction classifier.
- The user can run a local report/dry-run command that emits a privacy-safe
  release-window or review-window summary with `first_seen_at`, `last_seen_at`,
  usage counts, version/update context, evidence refs, and non-claims.
- The user can see at least one example issue/comment packet that contains
  observations and triage questions but no root-cause diagnosis or recommended
  fix.
- The user can verify that automatic filing/commenting, if implemented, is
  threshold-based only for friction or missed-detection evidence and has a
  dry-run/report-only mode.
- The user can verify update prompt state is reported separately from
  product-success or satisfaction metrics.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/report_usage_episodes.py --repo-root .`
- Focused JSON/report command for any new product-review reporter surface.
- `python3 scripts/validate_usage_episodes.py --repo-root .`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/skills/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`
- `rg -n "stopped_using_candidate|churn|satisfaction proof|last_seen_at" docs scripts tests integrations plugins/charness`

### High-Confidence Checks

- Focused tests for any new reporter packet builder, threshold filter, dry-run
  mode, or issue/comment body rendering.
- Fixture review with at least these cases: usage observed with last-seen only,
  inactivity with no filing, missed-detection threshold filing, friction
  threshold filing, update prompt state reported but not satisfaction-counted.
- Plugin mirror/package validation if root scripts or integration manifests
  change.
- Fresh-eye critique before enabling a mutating issue/comment path or any
  Corca-internal collection seam.

### External Or Live Proof

- Live GitHub proof is required only if the goal implements issue/comment
  creation. Otherwise a dry-run packet and deterministic tests are sufficient.
- Corca-internal API proof is required only if the implementation touches the
  collection seam. If the API is unavailable, record a stubbed contract and an
  explicit non-claim.
- No public/external telemetry proof is required; public telemetry remains a
  non-goal.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Lock the product-review boundary | The user changed the model from stop-using signal to last-seen review field | Updated #280 wording, accepted non-goals, and this shaped goal artifact | completed |
| 1 | Specify the reporter packet and data contract | Implementation needs a stable boundary before code | Docs or spec define fields, non-claims, thresholds, and dry-run/mutating modes | completed |
| 2 | Implement the smallest reporter/dry-run surface | A policy without a runnable reporter will not improve review behavior | Command output or helper emits release-window/review-window packets without filing | completed |
| 3 | Add thresholded issue/comment path if still warranted | Auto mutation is useful only after reporter semantics are proven | Dry-run plus optional mutating path with tests and GitHub proof if enabled | completed |
| 4 | Review privacy/product-readiness | Corca-internal collection changes trust boundaries | Fresh-eye critique, validation, non-claims, and clear keep-open/next-split decision | completed |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.

Gather: n/a — #280 and #184 GitHub issue context is directly reachable through
the issue backend; no private external source is required for this draft. If a
Corca-internal API/source is introduced during implementation, route that source
through `gather` or record why it is unavailable.

Release: pending after goal completion — the user requested "push release" after
this goal completes; route final version/tag/public-release proof through
`release` after this artifact is committed.

Issue closeout: pending release carrier — #280 is the tracked implementation
issue and should be closed by the commit/release carrier. #184 remains open by
design as the broader product-success synthesis issue.

## Discuss before activation

Resolved before activation:

- The activated goal should include specification, dry-run reporting, and an
  explicit mutating GitHub issue/comment path. Mutating behavior still needs an
  explicit flag or consent gate; dry-run/report-only remains available.
- For Corca-internal mode, named user reference plus repo reference is the useful
  default identity level because the product-review use case includes human
  follow-up. This identity is operational contact context, not satisfaction,
  dissatisfaction, or churn classification.
- Public/external telemetry remains disabled by default.

## Slice Log

### 2026-06-03 — Reporter contract and implementation

- Implemented `scripts/report_usage_product_review.py` as the local
  product-review CLI and `scripts/usage_episode_product_review.py` as the
  packet builder.
- Added docs in `docs/product-success-metrics.md` for the Corca-internal
  last-seen review loop, including `first_seen_at`, `last_seen_at`, release
  context, update prompt non-claims, thresholded friction/missed-detection
  packets, dry-run behavior, and default target-ref redaction for mutating
  GitHub comments.
- Synced checked-in plugin exports with
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- Focused proof after implementation: `pytest -q
  tests/test_usage_episodes_report.py tests/test_usage_episodes_schema.py`
  passed, 64 tests after the multi-packet execute proof was added.
- Local reporter proof: `python3 scripts/report_usage_product_review.py
  --repo-root . --release-version local --update-prompt-state unknown
  --friction-threshold 1 --missed-detection-threshold 1 --json` returned
  `status=valid`, `usage_count=409`, `first_seen_at=2026-05-22T23:00:38Z`,
  `last_seen_at=2026-06-03T00:45:08Z`, `actionable_packet_count=0`.

### 2026-06-03 — Fresh-eye critique and fixes

Fresh-eye satisfaction: parent-delegated. Three bounded read-only reviewers ran
privacy/product semantics, CLI failure-mode, and packaging/validation angles.

Act Before Ship findings and dispositions:

- Empty review windows were labeled `usage_observed`. Applied:
  `no_usage_observed` is emitted when the filtered window is empty, and tests
  cover the neutral empty-window packet.
- `repo_ref`/`user_ref` could be posted into mutating GitHub comments. Applied:
  target refs now require `--corca-internal`; mutating comments redact target
  refs by default and require `--include-target-refs-in-comments` to include
  them.
- `classification_skipped` alone could become a missed-detection issue comment.
  Applied: missed-detection threshold records now require friction/non-delivery
  plus `classification_skipped` or `t_status=none`.
- Missing `gh` could traceback under `--execute --json`. Applied:
  `gh_unavailable` structured payload and test.
- Multi-packet execute was non-atomic and could hide partial comments. Applied:
  execute posts one combined comment for all actionable packets and records
  packet count separately.
- Invalid/reversed windows could traceback or silently become empty. Applied:
  `invalid_window` structured payload and tests.
- Attention-state visibility missed the wrapper readiness states. Applied:
  wrapper-visible state constants plus attention-state reference entry; gate
  passed for 67 files.
- Executed comments could carry stale `filing_mode=execute_ready`. Applied:
  executable packet bodies regenerate with `filing_mode=executed`; fake-`gh`
  test asserts the posted body.

Bundle Anyway findings applied in this slice: plugin product-review CLI smoke,
window filtering test, target-ref gating test, and docs note for mutating
comment redaction.

## Context Sources

- GitHub issue #280:
  `https://github.com/corca-ai/charness/issues/280`
- Parent product-success issue #184:
  `https://github.com/corca-ai/charness/issues/184`
- Prior consume-policy goal:
  `charness-artifacts/goals/2026-06-02-184-usage-episode-product-success-consume-policy.md`
- Product-success docs:
  `docs/product-success-metrics.md`
- Usage episode report:
  `scripts/report_usage_episodes.py`
- Usage episode product-evidence helper:
  `scripts/usage_episode_product_evidence.py`

## Interview Decisions

- Stop-using options considered: machine-authored `stopped_using_candidate`,
  dashboard-visible `last_seen_at`, or ignore usage absence entirely. Chosen:
  expose `last_seen_at` and window summaries; humans interpret later. Rejected:
  automatic stop-using/churn labels because silence has many causes.
- Corca-internal identity options considered: repo-only, team aggregate,
  user-hash, or named user reference plus repo reference. Chosen: named user
  reference plus repo reference for Corca-internal mode because the intended
  dashboard/review action is human follow-up. Rejected: repo-only and team
  aggregate are too weak for follow-up; user-hash supports cohort analysis but
  still needs a lookup path before a human can ask the right person.
- Satisfaction options considered: update acceptance as satisfaction,
  continued usage as satisfaction, or keep both separate from satisfaction.
  Chosen: keep update acceptance and continued usage separate. They can support
  distribution/review context but not product-success proof.
- Reporter role options considered: report plus recommended action, report plus
  triage questions, or no issue/comment surface. Chosen: reporter packet plus
  triage questions. Rejected: script-authored recommended actions because they
  would encode weak heuristics and increase FP/FN.
- Filing options considered: auto-file inactivity, auto-file any threshold, or
  auto-file/comment only friction/missed-detection thresholds with dry-run.
  Chosen: friction/missed-detection only, dry-run first. Rejected: inactivity
  filing because last-seen staleness should be a dashboard/human review input.

## Plan Critique Findings

- Risk: last-seen can easily become a hidden churn classifier. Folded into
  Non-Goals, Boundaries, User Acceptance, and Slice Plan.
- Risk: Corca-internal telemetry could normalize public telemetry by accident.
  Folded into Non-Goals and External Proof: no public/external telemetry by
  default.
- Risk: update prompt acceptance could be misread as satisfaction. Folded into
  Non-Goals and User Acceptance.
- Risk: reporter scripts can become product managers by prescribing fixes.
  Folded into Goal, Boundaries, and Slice Plan as reporter-only packets.
- Risk: auto-filing can create noise if thresholds are weak. Folded into Slice
  Plan: dry-run/report-only first; mutating issue/comment path only after
  reporter semantics are proven.

## Off-Goal Findings

- None yet. #280 is the tracked implementation issue; #184 remains the parent
  product-success synthesis issue.

## Final Verification

- Implemented reporter surface:
  `scripts/report_usage_product_review.py` and
  `scripts/usage_episode_product_review.py`.
- Synced checked-in plugin mirror:
  `plugins/charness/scripts/report_usage_product_review.py`,
  `plugins/charness/scripts/usage_episode_product_review.py`, and
  `plugins/charness/skills/quality/references/attention-state-visibility.json`.
- Product-success docs now document the Corca-internal last-seen review loop,
  thresholded reporter packets, dry-run default, update prompt non-claim, and
  default target-ref redaction for mutating comments.
- Focused tests passed: `pytest -q tests/test_usage_episodes_report.py
  tests/test_usage_episodes_schema.py` — 64 tests.
- Local reporter proof passed: `python3 scripts/report_usage_product_review.py
  --repo-root . --release-version local --update-prompt-state unknown
  --friction-threshold 1 --missed-detection-threshold 1 --json` returned
  `status=valid`, `usage_count=409`,
  `first_seen_at=2026-05-22T23:00:38Z`,
  `last_seen_at=2026-06-03T00:45:08Z`, and `actionable_packet_count=0`.
- Plugin reporter smoke passed through the focused test suite.
- Fresh-eye critique completed with parent-delegated reviewers for
  privacy/product semantics, CLI failure modes, and packaging/validation.
  Act Before Ship findings were applied and covered by tests.
- Public-skill dogfood review completed for the touched `quality` reference:
  `python3 scripts/suggest_public_skill_dogfood.py --repo-root .
  --skill-id quality --json`; resulting consumer-contract note was added to
  `docs/public-skill-dogfood.json`.
- Closeout rehearsal passed:
  `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest
  --ack-cautilus-skill-review`.
- Verification-lock closeout passed:
  `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock
  --ack-cautilus-skill-review`, including broad pytest in 277.4s and all
  changed-surface sync/docs/packaging/skill/integration/lint/length/
  attention-state gates.
- Live GitHub mutation proof was not run because no issue/comment was posted;
  the mutating path is tested with fake `gh`, default target-ref redaction, and
  structured missing-`gh` failure.
- Corca-internal API proof was not run because this slice did not implement a
  collection API seam.
- No public/external telemetry proof was required or claimed.

## User Verification Instructions

- Run `python3 scripts/report_usage_product_review.py --repo-root .
  --release-version <version> --update-prompt-state unknown --json` to inspect
  a review-window payload.
- Add `--friction-threshold <n>` or `--missed-detection-threshold <n>` to preview
  reporter-only issue/comment packets in dry-run mode.
- Use `--execute --github-repo <owner/repo> --issue-number <n>` only for an
  approved Corca-internal destination; target refs are redacted in mutating
  comments unless `--include-target-refs-in-comments` is explicitly passed.

## Auto-Retro

- Retro: `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`.
- Host log probe: charness-artifacts/probe/2026-06-03-280-corca-internal-usage-last-seen-host-log-probe.json
- Disposition review: charness-artifacts/critique/2026-06-03-280-corca-internal-usage-disposition-review.md
- Retro: charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md
- Recent lessons refreshed through the retro persistence helper:
  `charness-artifacts/retro/recent-lessons.md` and
  `charness-artifacts/retro/lesson-selection-index.json`.
- Main finding: mutating reporter paths need edge fixtures before broad happy
  paths — empty/no-data windows, missing external binary, multi-action failure,
  and privacy redaction. Disposition: applied in
  `tests/test_usage_episodes_report.py`.
- Dogfood/attention-state finding: public-skill reference edits can trigger
  dogfood review even when routing is unchanged. Disposition: applied in
  `docs/public-skill-dogfood.json`.
- Sibling search: no other thresholded product-review reporter path found; no
  follow-up issue needed.
- Retro dispositions: applied — targeted tests, dogfood registry note, and goal
  slice-log critique dispositions are committed with this work.

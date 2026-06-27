# Achieve Goal: Focused coverage producer UX loop

Status: complete
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-focused-coverage-producer-ux-loop.md`

This file is the living goal scratchpad for the active follow-on quality loop.

## Active Operating Frame

- Current slice: focused mutation coverage producer UX.
- Current slice intent: make `scripts/suggest_mutation_coverage_command.py`
  explain status meanings and fallback action in help/text mode without
  changing the JSON payload or exit-code contract.
- Next action: commit, push, and report that no release publish is warranted for
  this helper-guidance-only slice.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Improve the focused mutation coverage producer operator experience so a maintainer can distinguish recommended, partial, missing, noop, and blocked outcomes without reading source code. Boundaries: keep JSON payload keys and existing exit-code contract stable; do not auto-run closeout from the suggester; do not publish a release unless the final diff materially changes shipped operator behavior beyond helper guidance. User acceptance: run the suggester help and text/JSON tests, complete slice closeout with focused mutation coverage, commit, push, and report whether release work is warranted.

## Non-Goals

- Do not make closeout auto-run this suggester in this slice.
- Do not change the helper's JSON keys, command shape, or success/non-success
  status set.
- Do not publish a release unless the final diff materially changes shipped
  operator behavior beyond helper guidance.

## Boundaries

- External side-effect scope: commit and push the completed slice to
  `origin/main` after local closeout passes. No release publish is pre-approved
  for this slice.
- Portability classification: skill-capability/export surface because the helper
  ships through the Charness plugin mirror; run root plugin sync before
  validators.
- Review scope: small local-risk code/CLI UX slice; fresh-eye review focuses on
  runtime behavior, CLI/operator contract, test adequacy, and generated mirror
  sync.

## User Acceptance

- Run `python3 scripts/suggest_mutation_coverage_command.py --help` and see
  `recommended`, `partial`, `missing`, `noop`, and `blocked` explained with
  closeout/fallback guidance.
- Run the helper without `--json` on a partial fixture and get command stdout
  plus stderr warning for unmapped files and broad fallback.
- Confirm the slice is committed, pushed, and has a release decision.

## Agent Verification Plan

### Low-Cost Checks

- `python3 -m pytest -q tests/quality_gates/test_suggest_mutation_coverage_command.py`
- `python3 -m py_compile scripts/suggest_mutation_coverage_command.py plugins/charness/scripts/suggest_mutation_coverage_command.py`
- `bash .githooks/pre-commit`

### High-Confidence Checks

- Related pytest group:
  `python3 -m pytest -q tests/quality_gates/test_suggest_mutation_coverage_command.py tests/quality_gates/test_changed_line_mutation_coverage.py tests/quality_gates/test_mutation_coverage_producer.py`
- Locked closeout with focused mutation coverage producer returned by
  `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --json`.
- Post-commit changed-line mutation coverage consumer reuses fresh producer
  coverage.

### External Or Live Proof

- `git push origin main` after local closeout. No external release publish unless
  the final release decision changes.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Focused producer UX | Handoff named thin help/status guidance as the first high-value follow-up after v0.56.6 | Help output, focused tests, related pytest, fresh-eye review, closeout with focused producer, push | complete |

## Operator Decision Queue

none — no operator-only decision blocks this local slice.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing: `find-skills` recommended `quality` for the quality-improvement loop;
the implementation phase used `impl`, and this local-risk slice used bounded
fresh-eye review.
Gather: n/a - no external source context.
Release: n/a - no version bump, install manifest change, or release publish is
warranted; this slice only improves helper guidance and tests after v0.56.6.
Issue closeout: n/a - this goal does not close a tracked GitHub issue.

## Slice Log

### Slice 1: Focused Coverage Producer UX

- Objective: make the focused coverage producer helper self-explanatory for
  `recommended`, `partial`, `missing`, `noop`, and `blocked` outcomes.
- Files changed: `scripts/suggest_mutation_coverage_command.py`,
  `plugins/charness/scripts/suggest_mutation_coverage_command.py`,
  `tests/quality_gates/test_suggest_mutation_coverage_command.py`, and this
  goal artifact.
- Alternatives rejected: closeout auto-discovery/auto-run was left deferred so
  proof command selection stays explicit and auditable.
- Targeted verification: focused pytest, related mutation coverage tests,
  py_compile, diff check, pre-commit, fresh-eye review, and locked slice
  closeout with a focused mutation coverage producer.
- Test-pressure: added focused helper tests in an existing test module; file
  headroom after closeout was 664 lines for the test file and 309 lines for the
  helper script.
- Critique: parent-delegated fresh-eye review found partial JSON `reason`
  needed status-aware wording before ship; fixed and retested.
- Post-commit coverage finding: changed-line mutation coverage consumer caught
  that `noop` and `blocked` text diagnostics lines were not executed by focused
  tests. Added direct `main()` tests for both branches before amending the
  commit.

## Context Sources

- `docs/handoff.md` first high-value loop: focused coverage producer UX.
- `docs/conventions/implementation-discipline.md` mutation coverage producer and
  sync-before-verify rules.
- `docs/conventions/operating-contract.md` commit, critique, and push discipline.
- `charness-artifacts/critique/2026-06-27-release-0.56.6-focused-mutation-coverage.md`
  deferred item: richer `--help` status guidance.

## Interview Decisions

- Mode: implementation-continuation, not artifact-only, because the user said to
  start another loop after the previous sustained-quality goal.
- Slice choice: focused coverage producer UX over release planning evidence
  scope because handoff ranked it first and it is a narrow post-release
  follow-up.
- Automation boundary: keep the suggester explicit instead of auto-running from
  closeout in this slice; rejected auto-run because auditability of the proof
  command is still being evaluated.

## Plan Critique Findings

Fresh-eye review by subagent `019f06eb-9db7-7f11-8673-4e0d4390b970` found one
Act Before Ship issue: partial JSON `reason` still implied the focused command
could be trusted even when unmapped files existed. Fixed by making the existing
`reason` value status-aware for partial and extending tests. Bundle-anyway help
test coverage for `missing`/`noop`/`blocked` was also added.

## Off-Goal Findings

none so far.

## Final Verification

- Focused pytest:
  `python3 -m pytest -q tests/quality_gates/test_suggest_mutation_coverage_command.py`
  passed, 10 tests.
- Related pytest:
  `python3 -m pytest -q tests/quality_gates/test_suggest_mutation_coverage_command.py tests/quality_gates/test_changed_line_mutation_coverage.py tests/quality_gates/test_mutation_coverage_producer.py`
  passed, 47 tests.
- Syntax:
  `python3 -m py_compile scripts/suggest_mutation_coverage_command.py plugins/charness/scripts/suggest_mutation_coverage_command.py`
  passed.
- Lint Gate: ran-pass `bash .githooks/pre-commit`.
- Fresh-eye satisfaction: parent-delegated reviewer
  `019f06eb-9db7-7f11-8673-4e0d4390b970`; one Act Before Ship finding fixed.
- Disposition review:
  `charness-artifacts/critique/2026-06-27-focused-coverage-producer-ux-loop-disposition-review.md`.
- Focused producer discovery:
  `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --json`
  returned `status: recommended` and command
  `python3 -m pytest -q -m 'not release_only' tests/quality_gates/test_suggest_mutation_coverage_command.py`.
- Locked closeout:
  `python3 scripts/run_slice_closeout.py --repo-root . --base auto --skip-sync --allow-unmatched --verification-lock --refresh-broad-pytest-proof --produce-mutation-coverage --mutation-coverage-command "python3 -m pytest -q -m 'not release_only' tests/quality_gates/test_suggest_mutation_coverage_command.py" --json`
  passed once before final artifact completion and is the required final proof
  to rerun after this completion edit.
- First locked closeout evidence: broad standing pytest passed 3698 tests in
  21.26s; focused instrumented producer passed 10 tests in 1.44s and wrote
  `reports/mutation/test-coverage.json` with fingerprint
  `0e91fa509cf94cdc2812b26edd1d790c8535abd2b561ab0b9c80e2ef8a823a41`.
- Post-commit changed-line consumer: first run failed on
  `scripts/suggest_mutation_coverage_command.py` lines 157-160 (`noop` and
  `blocked` diagnostics); remediated by adding focused text-mode tests and
  rerunning the producer/consumer before push.
- Release decision: no release. The helper is already shipped in v0.56.6; this
  diff improves guidance/tests only and does not warrant a new public release.
Retro: skipped: host-log-not-exposed: no host session log or metric window is
exposed for this small single-slice run; no transferable workflow waste was
found beyond the bounded fresh-eye fix recorded here.
Host log probe: skipped: host-log-not-exposed: no host token/time/session-log
surface is exposed for this small single-slice run, so no goal-scoped host-log
probe can be bound honestly.
Disposition review: charness-artifacts/critique/2026-06-27-focused-coverage-producer-ux-loop-disposition-review.md

## User Verification Instructions

- Inspect `python3 scripts/suggest_mutation_coverage_command.py --help`.
- Inspect the pushed commit and this goal artifact for verification and release
  decision.

## Auto-Retro

Retro dispositions: none — no new transferable workflow improvement surfaced in
this slice yet.
Structural follow-up: none — no sibling-search trigger surfaced.

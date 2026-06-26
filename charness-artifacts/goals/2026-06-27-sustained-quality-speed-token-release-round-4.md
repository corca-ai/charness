# Achieve Goal: Sustained quality, speed, token, and release round 4

Status: active
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-sustained-quality-speed-token-release-round-4.md`

This file is the living goal scratchpad. The user requested the three-hour goal
and release run directly in chat, so this artifact is active for this session.

## Active Operating Frame

- Current slice: quality slice verified; release and publication remain.
- Current slice intent: reduce a concrete test-maintenance pressure point and
  remove one unnecessary script startup cost without weakening proof.
- Next action: commit the quality slice, then run release planner/publish flow.
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

Run an approximately three-hour quality improvement round for Charness covering bug fixes, deterministic quality posture, test and script runtime, token efficiency, and release readiness. Prefer high-leverage repo-owned changes backed by measured evidence. Finish by syncing generated surfaces, verifying, committing, pushing, and cutting/pushing the next release if release gates allow it.

## Non-Goals

- Do not weaken existing quality gates to create speed.
- Do not add broad prose policy when a helper, test, validator, or deletion can
  own the concern.
- Do not run Cautilus unless the repo planner allows a named log-backed lane.
- Do not close unrelated GitHub issues unless the implemented slice directly
  satisfies their closeout contract.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Push and release are requested by the user for the final bundle, but remain
  publish-boundary work: run release planning and critique before executing.
- Timebox: approximately 3 hours from session activation.
- Activation time: 2026-06-27 session start.
- Closeout reserve: keep the final 30 minutes for sync, verification, critique,
  commit, push, release, and artifact completion.
- Done-early policy: continue_next_improvement while local proof remains cheap
  and release reserve is intact.

## User Acceptance

- Review the final commits and release/tag pushed to the configured remote.
- Run `./scripts/run-quality.sh --read-only`.
- Run the focused tests or helper checks named in `## Final Verification`.
- Inspect the release artifact for version, proof, and non-claims.

## Agent Verification Plan

### Low-Cost Checks

- Quality planner and required primer reads.
- Runtime summary and skill ergonomics inventory interpretation.
- Focused pytest or helper tests for each changed code path.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after mutation.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  for pre-lock slices when changes span gated surfaces.
- Final locked closeout with broad proof when mutation set is fixed.
- Release planner, fresh-checkout probes, and publish helper proof before tag
  push.

### External Or Live Proof

- `git push` and release publish/tag push are final-bundle only.
- No provider/live behavior proof is claimed unless explicitly recorded by the
  release helper or another distinct evidence channel.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Baseline quality and choose cleanup | Avoid guessing about slow or weak surfaces | planner, runtime summary, ergonomics inventory, read-only gate | complete |
| 2 | Implement selected deterministic improvement | User requested aggressive quality gains, not report-only review | focused tests, changed-surface check, slice log | complete |
| 3 | Sync, verify, critique, release | Publish boundary requested explicitly | closeout gate, release artifact, clean push/tag | pending |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

none — no operator-only decision is currently queued; final release follows the
user's explicit push/release request and release planner gates.

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

Routing: `find-skills` recommended `quality` for the improvement slice and
`release` for the publication boundary; both routes were followed.
Gather: n/a — no external URLs or source links were introduced as working
context for this goal.
Release: pending — release planner/publish proof runs after the quality slice
commit, then this line will be updated with the release artifact.
Issue closeout: n/a — this goal did not claim or close tracked GitHub issues.

## Slice Log

- Slice 1/2 evidence:
  - Routing: `find-skills` recommended `quality` first and `release` for the
    publication boundary.
  - Quality planner: required primer reads consumed; runtime summary and skill
    ergonomics inventories run.
  - Runtime interpretation: `run-quality-read-only` remains a real standing
    cost but within budget; only `check-markdown` is CI-backed and too small to
    justify weakening local proof.
  - Structural cleanup: split
    `tests/quality_gates/test_quality_bootstrap.py` into a focused bootstrap
    test file, `tests/quality_gates/test_quality_adapter_gate_design.py`, and
    `tests/quality_gates/quality_bootstrap_support.py`.
  - Length proof: `test_quality_bootstrap.py` moved from 749/800 code lines
    near-limit to 474/800; new files are 215/800 and 73/800.
  - Behavior proof: `pytest -q
    tests/quality_gates/test_quality_bootstrap.py
    tests/quality_gates/test_quality_adapter_gate_design.py` passed 17 tests.
  - Script-speed cleanup: moved `run-quality.sh` standing pytest target
    expansion after help/argument validation; `bash -x scripts/run-quality.sh
    --help` no longer invokes `run_standing_pytest`, while
    `CHARNESS_QUALITY_LABELS=check-test-completeness ./scripts/run-quality.sh
    --read-only` still passed.
  - Prompt-inventory cleanup: refined
    `skills/public/quality/references/find_inline_prompt_bulk.py` so true
    module/class/function docstrings are not reported as inline prompt bulk,
    while control-flow string expressions remain reportable.
  - Prompt-inventory proof: `tests/test_find_inline_prompt_bulk.py` covers the
    docstring exclusion and control-flow preservation regressions; focused
    `pytest -q tests/test_find_inline_prompt_bulk.py` passed 6 tests.
  - Fresh-eye review: bounded reviewer
    `019f05c3-0863-79f0-ba5f-dbabf8a557a5` found one medium docstring
    over-exclusion risk and one low EOF whitespace issue; both were fixed and
    covered before closeout.
  - Quality artifact:
    `charness-artifacts/quality/2026-06-27-round-four-quality-speed-token-review.md`
    records runtime, script-speed, test-maintenance, prompt-inventory, and
    validation evidence for the slice.
  - Broad proof: `./scripts/run-quality.sh --read-only` passed 79 phases with
    zero failures after sync.
  - Locked closeout: `python3 scripts/run_slice_closeout.py --repo-root .
    --verification-lock --refresh-broad-pytest-proof
    --produce-mutation-coverage --mutation-coverage-command "pytest -q
    tests/test_find_inline_prompt_bulk.py" --ack-cautilus-skill-review`
    completed successfully.
  - Low-cost checks: `bash -n scripts/run-quality.sh`, `ruff` on changed Python
    files, `check_changed_surfaces.py`, and boundary-bypass ratchet passed.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request in chat: overall quality improvements across bugs, test speed,
  script speed, token efficiency, then push/release.
- `docs/handoff.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/quality/latest.md`
- `charness-artifacts/release/latest.md`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Scope: broad quality round chosen over single issue because the request named
  several quality dimensions; rejected issue-only routing because no issue
  number was provided and handoff has multiple candidates.
- Proof depth: start report-first with cheap inventories, then run broad gate;
  rejected immediate code churn because prior retros warn against brute-force
  broad pytest and mechanical cleanup.
- Release intent: final push/release is in scope because the user explicitly
  requested it; publication still uses release planner and critique gates.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Same-agent initial critique: broad quality wording can become unfocused
  churn. Folded response: select from measured runtime, handoff, and gate
  evidence only.
- Same-agent initial critique: release is irreversible relative to local edits.
  Folded response: keep push/release to final bundle and route through release.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence. Before marking complete, update the release proof from
pending to the checked-in release artifact and tag/push evidence.

Retro:
`charness-artifacts/retro/2026-06-27-sustained-quality-speed-token-release-round-4-goal-retro.md`
Host log probe: skipped: host-log-not-exposed: Codex host goal-window token and
event metrics are not exposed as a stable checked-in source for this run.
Disposition review:
`charness-artifacts/retro/2026-06-27-sustained-quality-speed-token-release-round-4-goal-retro.md`
Quality proof:
`charness-artifacts/quality/2026-06-27-round-four-quality-speed-token-review.md`
Release proof: pending: release planner and publish proof run after the quality
slice commit.

## User Verification Instructions

- Run `./scripts/run-quality.sh --read-only`.
- Inspect
  `charness-artifacts/quality/2026-06-27-round-four-quality-speed-token-review.md`
  for the focused quality evidence and non-claims.
- After release, verify the pushed tag and release artifact named in the
  updated `Release proof:` line above.

## Auto-Retro

Retro dispositions: applied: quality artifact validators were run immediately
after artifact repair before the final locked closeout rerun; applied:
control-flow string-expression regression coverage was added to
`tests/test_find_inline_prompt_bulk.py`.
Structural follow-up: repo-local guard:
`scripts/validate_quality_artifact.py`,
`scripts/validate_inventory_consumption.py`,
`scripts/check_spec_evidence_durability.py`, and
`scripts/validate_current_pointer_freshness.py` already guard the artifact
contract; no new gate added.

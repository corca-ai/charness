# Achieve Goal: Sustained quality speed token release round 2

Status: active
Created: 2026-06-26
Activation: `/goal @charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-2.md`
Timebox: 3h
Activation time: 2026-06-26T12:30:30+09:00
Closeout reserve: 25m
Done-early policy: continue_next_improvement

This file is the active living goal scratchpad for the current run.

## Active Operating Frame

- Current slice: baseline quality/runtime inventory and first safe local
  improvement candidate.
- Current slice intent: continue aggressive but bounded quality, test-speed,
  script-speed, and token-efficiency work without external push/release until
  the closeout reserve begins at 2026-06-26T15:05:30+09:00.
- Next action: run quality planner/inventories, choose one bounded local slice,
  implement, verify, critique, commit, then continue with the next safe slice.
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

Run another roughly three-hour implementation-continuation goal that improves
Charness quality across bug fixes, test speed, script execution speed, and token
efficiency. Keep safe local improvements moving until the closeout reserve, then
push `main` and publish or verify the release surface only through the release
contract.

## Non-Goals

- Do not push, tag, publish, or refresh installed release surfaces before the
  closeout reserve begins.
- Do not weaken the standing read-only quality gate or remove real CLI boundary
  proof merely to make tests faster.
- Do not add a new deterministic blocking floor without the floor-addition
  restraint call required by implementation discipline.
- Do not claim token efficiency from cached-input or whole-session metrics
  alone; use goal-window host evidence at closeout.
- Do not close tracked GitHub issues unless a slice explicitly routes through
  `issue` and carries the required closeout proof.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- The user's final push/release request authorizes only the final closeout lane.
  Before 2026-06-26T15:05:30+09:00, release/push actions are out of scope unless
  continuing local work becomes unsafe and an early-close report is recorded.
- If the first improvement family finishes early, continue with the next safe
  improvement instead of closing early.
- Generated/plugin/export surfaces must be synced before validators when
  touched; mutation, sync, verification, and publish remain hard phase barriers.
- Cautilus remains eval-only and disabled unless the repo planner explicitly
  allows the wrapper path with a named failing-log source.

## User Acceptance

- Inspect the commits from this run and see concrete changes that improve
  correctness, test speed, script runtime, token efficiency, or quality proof.
- Run `./scripts/run-quality.sh --read-only` successfully after the final bundle.
- Confirm no premature push/release happened before the closeout reserve.
- Confirm `main` is pushed and the release surface is prepared or published
  according to the release contract at closeout.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest or direct script validation for each changed surface.
- `ruff` for changed Python.
- Relevant inventory ratchets such as boundary-bypass, duplicate, length, or
  runtime budget checks when the slice touches their surfaces.
- `git status --short --branch` at slice boundaries.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest` for
  broad multi-surface slices before commit.
- Fresh-eye or scoped critique for substantial risk boundaries.
- `./scripts/run-quality.sh --read-only` for final broad proof.

### External Or Live Proof

- Final `git push origin main` result plus clean local/remote branch status.
- Release helper proof, public release verification through a distinct channel,
  and install refresh/readback when required by the release planner.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Baseline quality/runtime inventory and first local improvement | Avoid repeating low-yield subprocess micro-slices without checking current hot spots | quality planner, targeted inventory, focused proof, critique, commit | in-progress |
| 2 | Next highest signal local quality/runtime/token-efficiency improvement | Timebox mode continues safe work until closeout reserve | focused proof, relevant ratchet, critique, commit | queued |
| 3 | Repeat safe improvement slices until closeout reserve | User asked for sustained three-hour work, not early close | slice logs, commits, cheap gates | queued |
| 4 | Final push/release closeout | User explicitly requested final push/release | read-only quality gate, release planner/helper proof, public verification, clean status | queued |

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

Current queue: none — the user explicitly authorized the final closeout
push/release lane, and no operator-only decision blocks local quality slices.

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

Routing: find-skills recommended quality for quality/runtime posture and release for final publication; implementation slices will record impl routing at closeout after mutation work exists.
Gather: n/a — no external URL/source context was provided for this goal.
Release: pending final closeout — no release/push before 2026-06-26T15:05:30+09:00 unless an early-close report is required.
Issue closeout: n/a — this goal is not currently resolving a tracked GitHub issue.

Discuss before activation: resolved — the user explicitly requested final
push/release, and this artifact scopes that approval to the final closeout lane
only; before the closeout reserve, safe local quality slices continue and
release/push is forbidden unless an early-close report is recorded.

## Slice Log

### Activation: run setup

- Objective: Shape and activate the second sustained quality goal without
  repeating the previous premature-release failure.
- What changed: Created this goal artifact with an explicit closeout reserve and
  release boundary.
- Targeted verification: pending `check_goal_artifact.py --pursue-ready`.
- Lessons carried forward: final push/release waits until closeout reserve;
  host metric window is recorded before closeout probe; prefer shared helpers
  over repeated micro-slice patterns.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request on 2026-06-26: run another three-hour aggressive quality
  improvement goal, then push/release at the end.
- `docs/design-north-star.md`
- `docs/conventions/implementation-discipline.md`
- `docs/conventions/operating-contract.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release.md`
- `charness-artifacts/retro/2026-06-26-sustained-quality-speed-token-release-goal-retro.md`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only draft vs implementation-continuation. Chosen:
  implementation-continuation because the user explicitly asked to create a
  three-hour goal and proceed. Rejected: artifact-only would fail the request.
- Timebox family: exact stop at first macro success vs continue-next-improvement
  until reserve. Chosen: continue-next-improvement with 25m closeout reserve
  because the request is sustained and the prior miss was closing/publishing too
  early. Rejected: early release after first green gate.
- Quality axis: repeat broad fanout micro-slices vs inventory-led next slice.
  Chosen: inventory-led slice selection because the previous run showed repeated
  tiny conversions create artifact churn. Rejected: blindly continuing the same
  conversion pattern without new signal.
- Release axis: publish whenever green vs closeout-only release. Chosen:
  closeout-only release through the `release` skill, after local proof and
  critique. Rejected: direct publish before closeout reserve.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Folded blocker: release/push can happen too early in a timebox. The closeout
  reserve timestamp is explicit and release/push is forbidden before it.
- Folded blocker: speed work can erase real boundary proof. Non-goals and the
  verification plan preserve representative CLI proof.
- Folded blocker: repeated small subprocess conversions can waste tokens and
  artifacts. Slice 1 starts from quality/runtime inventory before choosing work.
- Over-worry not folded: avoid all small improvements. Counterweight: small
  bounded slices are still valid when inventory shows a high-confidence target
  and proof remains cheap.
- Reviewer provenance: same-agent shaping critique; substantial mutation slices
  will use bounded fresh-eye or scoped critique according to risk.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

None yet.

## Slice Log

### Slice 1 — Reuse update-all support sync results

- Objective: Cut release-gate script execution time without weakening the
  `charness update all` boundary proof.
- Finding: `charness update all` ran `scripts/sync_support.py` once during
  install surface refresh and again during tool update flow; fixture timing
  measured the duplicate support sync at about 1.1s in the representative
  temp install.
- Change: `run_tool_update_flow` now accepts precomputed support sync results
  and reuses them only for the unfiltered, non-dry-run `update all` path where
  install surface already synced the same repo/plugin surface.
- Verification:
  - `python3 -m pytest -q tests/charness_cli/test_update_flow_unit.py tests/charness_cli/test_managed_install_extended.py::test_installed_cli_update_all_refreshes_external_tools_and_support_state --durations=20 --durations-min=0.01`
    passed; update-all sentinel call time was 12.63s in this run.
  - `python3 -m pytest -q tests/charness_cli/test_update_output.py::test_installed_cli_update_all_without_json_prints_progress_and_summary --durations=10 --durations-min=0.01`
    passed; non-JSON progress output still includes the support sync step.
  - `python3 scripts/check_python_lengths.py --paths charness tests/charness_cli/test_update_flow_unit.py`
    passed for the Python test file; the extensionless `charness` script is
    outside that checker.

### Slice 2 — Remove redundant control-plane subprocesses

- Objective: Reduce standing test runtime while preserving a real behavior
  check for doctor, support sync, update, and lock state.
- Finding: `tests/control_plane/test_sync_support.py::test_doctor_sync_and_update_work_on_seed_repo`
  spawned `doctor.py`, `sync_support.py`, `doctor.py`, and `update_tools.py`
  even though the scripts expose import-safe functions and separate CLI
  boundary tests still cover command behavior.
- Change: The test now calls `inspect_manifest`, `sync_one`, and `update_one`
  directly against the same seeded repo and asserts the same payload/lock
  contract.
- Verification:
  - `python3 -m pytest -q tests/control_plane/test_sync_support.py --durations=20 --durations-min=0.01`
    passed; the target test call time was 0.54s, down from the 1.12s pre-change
    sample.

### Slice 3 — Lower integration validation doctor checks in-process

- Objective: Continue reducing standing nested-process fanout where a test
  asserts Python payload contracts rather than CLI stdout/stderr behavior.
- Finding: Several `tests/control_plane/test_integrations_validation.py`
  doctor/support assertions spawned import-safe scripts even though the same
  file keeps explicit CLI boundary coverage for human output and blocking
  `charness tool doctor` behavior.
- Change: Internal doctor/support cases now use `inspect_manifest`,
  `sync_one`, and `load_capabilities` directly, while the human-output and
  CLI-return-code tests remain subprocess boundary tests.
- Verification:
  - `python3 -m pytest -q tests/control_plane/test_integrations_validation.py --durations=25 --durations-min=0.01`
    passed; file runtime was 7.15s in the post-change sample, with the converted
    missing-support case down to 0.18s from 0.50s in the earlier sample.

### Slice 4 — Plan compact skill ergonomics packets

- Objective: Reduce token waste in the quality planner without hiding full
  evidence when deeper inspection is needed.
- Finding: The quality planner recommended the full skill ergonomics JSON
  packet, about 97KB on this repo, even though the script already exposes a
  compact `--summary` packet for agent triage.
- Change: The quality reference catalog now recommends
  `inventory_skill_ergonomics.py --summary`; the checked-in plugin copy is kept
  in sync, and the planner test asserts the compact command.
- Verification:
  - `python3 -m pytest -q tests/quality_gates/test_quality_run_planner.py`
    passed.
  - `python3 scripts/validate_quality_reference_catalog.py --repo-root .`
    passed.
  - `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
    now reports the skill ergonomics gate with `--summary`.
  - `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary | wc -c`
    reported 12201 bytes, compared with the earlier full `--json` measurement
    of 96643 bytes.
- Public-skill dogfood decision: `quality` routing, durable artifact behavior,
  required primer reading, structural review packet, and gate-packet contract
  are unchanged; only the planner-recommended evidence packet switches from
  full JSON to the existing compact summary. `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
  confirmed the current `quality` consumer contract already covers planner
  gate-packet behavior, so no dogfood scenario change is needed.

### Slice 5 — Move slice-plan row counting out of goal core

- Objective: Reduce near-limit pressure in the core achieve goal artifact
  helper without changing its public API.
- Finding: `skills/public/achieve/scripts/goal_artifact_lib.py` was in the
  Python length warning band at 346/360 code lines, and its test-only
  `slice_plan_data_row_count` helper belonged with markdown parsing utilities.
- Change: Moved the row-count implementation to `goal_artifact_markdown.py`
  and re-exported it from `goal_artifact_lib.py`; synced the checked-in plugin
  mirror.
- Verification:
  - `python3 -m pytest -q tests/quality_gates/test_goal_artifact_lib.py::test_slice_plan_table_row_count_table_form tests/test_handoff_chunker_auto_draft.py::test_slice_plan_data_row_count_is_zero`
    passed.
  - `python3 scripts/check_python_lengths.py --repo-root . --paths skills/public/achieve/scripts/goal_artifact_lib.py skills/public/achieve/scripts/goal_artifact_markdown.py plugins/charness/skills/achieve/scripts/goal_artifact_lib.py plugins/charness/skills/achieve/scripts/goal_artifact_markdown.py`
    passed.
  - `python3 scripts/check_staged_mirror_drift.py --repo-root .` passed.
  - `python3 scripts/check_python_lengths.py --repo-root . --headroom --paths skills/public/achieve/scripts/goal_artifact_lib.py plugins/charness/skills/achieve/scripts/goal_artifact_lib.py skills/public/achieve/scripts/goal_artifact_markdown.py plugins/charness/skills/achieve/scripts/goal_artifact_markdown.py`
    reported `goal_artifact_lib.py` at 305/360 code lines, 55 lines of
    headroom.

### Slice 6 — Split portability goal tests out of the near-limit file

- Objective: Remove a test-file length warning before the next goal artifact
  change is forced to pay a split tax.
- Finding: `tests/quality_gates/test_goal_artifact_lib.py` was at 792/800 code
  lines. Its portability self-test cluster was cohesive and independent enough
  to own a focused file.
- Change: Moved portability section and slice-plan row-count tests into
  `tests/quality_gates/test_goal_artifact_portability.py`; kept the remaining
  operator-decision queue test inline by removing its cross-fixture dependency.
- Verification:
  - `python3 -m pytest -q tests/quality_gates/test_goal_artifact_portability.py tests/quality_gates/test_goal_artifact_lib.py::test_operator_decision_queue_is_not_global_required_section`
    passed.
  - `python3 scripts/check_python_lengths.py --repo-root . --headroom --paths tests/quality_gates/test_goal_artifact_lib.py tests/quality_gates/test_goal_artifact_portability.py`
    reported `test_goal_artifact_lib.py` at 705/800 code lines, 95 lines of
    headroom.
  - `python3 -m py_compile tests/quality_gates/test_goal_artifact_lib.py tests/quality_gates/test_goal_artifact_portability.py && ruff check tests/quality_gates/test_goal_artifact_lib.py tests/quality_gates/test_goal_artifact_portability.py`
    passed.

### Slice 7 — Split web-fetch route/classify tests

- Objective: Remove another near-limit test-file warning without changing
  web-fetch behavior coverage.
- Finding: `tests/test_web_fetch_support.py` was at 761/800 code lines, with a
  cohesive route/classify/direct-helper cluster independent from the
  acquire/gather integration tests.
- Change: Moved route selection, response classification, and direct helper
  branch tests into `tests/test_web_fetch_route_and_classify.py`; left
  acquire/gather boundary tests in the original file.
- Verification:
  - `python3 -m pytest -q tests/test_web_fetch_route_and_classify.py tests/test_web_fetch_support.py --durations=20 --durations-min=0.01`
    passed, 35 tests.
  - `python3 scripts/check_python_lengths.py --repo-root . --headroom --paths tests/test_web_fetch_support.py tests/test_web_fetch_route_and_classify.py`
    reported `test_web_fetch_support.py` at 530/800 code lines and the new
    file at 250/800.
  - `python3 -m py_compile tests/test_web_fetch_support.py tests/test_web_fetch_route_and_classify.py && ruff check tests/test_web_fetch_support.py tests/test_web_fetch_route_and_classify.py`
    passed.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

- Run `./scripts/run-quality.sh --read-only` after final closeout.
- Inspect the final `git log --oneline --decorate --max-count=12`.
- Inspect the final GitHub release evidence named under `Release:`.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named

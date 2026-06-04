# Achieve Goal: 3h Quality Test Economics

Status: complete
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-3h-quality-test-economics.md`

This file is the completed goal scratchpad for the run.

## Active Operating Frame

- Current slice: complete.
- Next action: none; review final verification and user verification
  instructions.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Run a three-hour post-release quality improvement goal focused on reducing Charness pytest and lifecycle-test cost while preserving behavior proof. Use nose advisory output to find refactoring candidates, but do not chase clone-count reduction when test economics or proof clarity is the higher-value quality move.

Discuss before activation: RESOLVED in-thread on 2026-06-05. The user selected
the three-hour quality goal, clarified that closeout may finish after the
timebox once started, and asked to continue to the next improvement if the
planned goal closes with meaningful time remaining. No live, provider, release,
or external proof is expected unless a selected slice unexpectedly requires it.

## Non-Goals

- Do not mechanically chase nose clone counts, especially bootstrap and plugin
  portability patterns whose duplication may be cheaper than shared coupling.
- Do not remove slow or long tests unless equivalent behavior proof remains at
  a cheaper layer or as one intentionally thin boundary smoke.
- Do not change release versions, publish a release, or edit install manifests.
  Version `0.18.0` was already released before this goal.
- Do not broaden into unrelated product, issue, or documentation cleanup merely
  because quality inventory surfaces it.

## Boundaries

- Timebox active improvement work to three hours from activation. If closeout
  begins before the timebox expires, finish closeout even if that crosses the
  three-hour wall.
- If the planned goal closes early and meaningful time remains, continue with
  the next highest-value quality improvement under the same boundaries.
- Primary quality target: pytest and lifecycle-test economics, especially
  duplicated subprocess, fixture-copy, or source-guard proof.
- Secondary target: nose-surfaced refactoring only when it removes real
  maintenance burden without weakening plugin portability or public support
  independence.
- Proof preservation: every deleted, demoted, or split expensive test must leave
  helper-level, in-process, or representative CLI smoke proof for the same
  user-visible behavior.
- Commit discipline: each meaningful slice ends with focused checks, surface
  sync when relevant, critique when non-trivial, and a clean commit before
  moving to the next slice.
- Broad proof: run broad non-release pytest at final closeout if standing test
  behavior changed; run release-specific quality only if release-only tests or
  release surfaces changed materially.

## User Acceptance

- Inspect the final commit list and see at least one committed quality
  improvement that reduces expensive or duplicated pytest proof while preserving
  representative behavior checks.
- Re-run the listed focused checks and broad/substitute checks from `## Final
  Verification`.
- Review nose and test-economics before/after notes and see why chased or
  rejected candidates were chosen.
- Confirm any skipped broad, release, live, or provider proof is explicitly
  called out as a non-claim.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch` before and after each slice.
- `python3 scripts/check_python_lengths.py --paths <touched python files>` for
  Python edits, plus repo-native formatting/lint on touched files where
  available.
- Focused `pytest` for touched tests and their owning helpers.
- Nose advisory inventory with `NOSE_BIN=/home/hwidong/codes/nose/target/release/nose`
  when selecting or validating duplication refactors.

### High-Confidence Checks

- Broad non-release `pytest` at final closeout when the standing pytest surface
  changes.
- Release quality only if release-only tests or release/install surfaces change.
- `python3 scripts/check_changed_surfaces.py --repo-root .` before committing
  meaningful repo work.
- Fresh-eye critique for any non-trivial test deletion, demotion, public helper
  extraction, or quality-contract change.

### External Or Live Proof

- No external, provider, or live proof is planned. If a candidate unexpectedly
  requires it, stop and record the proof gap instead of substituting local tests.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Refresh the current quality and pytest-economics posture. | The target must come from current runtime, duplicate, and test surface data, not yesterday's intuition. | Runtime summary, standing-test economics, nose advisory sample, selected target rationale. | completed |
| 2 | Convert one duplicated expensive pytest proof cluster into cheaper helper-level proof while keeping one boundary smoke. | This best matches the user's preference for equal confidence with less code and time. | Focused before/after test commands, retained representative boundary proof, critique notes. | completed |
| 3 | Apply one nose-surfaced refactor only if it is clearly extractable and low risk. | Nose should guide real simplification, not become the objective. | Before/after nose excerpt, focused tests, plugin/support sync if relevant. | completed |
| 4 | Use remaining time for the next low-risk pytest structure cleanup. | The user asked to continue when the planned goal closes early with time left. | Focused tests, lint/length proof, committed diff. | completed |
| 5 | Finalize and close out. | The goal must leave audited evidence, committed artifacts, and honest non-claims. | Broad or substitute proof, final artifact status complete, retro dispositions, clean committed tree. | completed |

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

Routing: find-skills routed this goal to achieve for lifecycle work and quality for current gate, test-economics, and nose-advisory decisions.
Gather: n/a — no external URLs, Slack, Notion, Docs, Drive, or other external
source is being used as working context.
Release: n/a — this goal intentionally follows the completed `0.18.0` release
and must not bump or publish.
Issue closeout: n/a — no tracked GitHub issue is being closed by this goal.

## Slice Log

### Slice 1-2: Release Publish Standing Pytest Economics

- Baseline: `render_runtime_summary.py` reported `pytest` 21.4s latest / 27.4s
  median under a 140s budget, and `check-coverage` 41.7s latest / 42.1s median
  near its 45s budget.
- Standing economics inventory: 244 Python test files, 107 nested CLI fanout
  files, and clean pytest temp footprint.
- Nose advisory: `nose 0.4.0` via `/home/hwidong/codes/nose/target/release/nose`
  reported mostly bootstrap/import-loader families plus adapter helper
  duplicates; no nose-only refactor was selected before test-economics cleanup.
- Target selected: release publish tests because
  `tests/quality_gates/test_release_publish.py` took 14 passed in 20.97s and
  `tests/quality_gates/test_release_publish_real_host_delta.py` took 13 passed
  in 11.53s. Before the change, `-m "not release_only"` collected all 27 tests
  from those two files.
- Change: mark full publish subprocess/git/GH boundary tests as
  `release_only`; keep requested-review gate tests, dry-run helper-level
  fail-closed tests, and the no-trigger dry-run CLI check in standing pytest.
- Focused proof so far: `pytest --collect-only -q -m "not release_only"
  tests/quality_gates/test_release_publish.py
  tests/quality_gates/test_release_publish_real_host_delta.py` collected 8/27;
  `pytest -q -m "not release_only" ... --durations=20 --durations-min=0.01`
  passed 8, deselected 19 in 3.27s; `pytest -q -m release_only ...` passed 19,
  deselected 8 in 29.15s.
- Hygiene proof so far: `python3 -m ruff check
  tests/quality_gates/test_release_publish.py
  tests/quality_gates/test_release_publish_real_host_delta.py` passed;
  `check_python_lengths.py --paths ...` passed with an advisory near-limit
  warning for `test_release_publish.py`.
- Delegated Review: executed via bounded fresh-eye subagent Ptolemy. No
  `Act Before Ship` findings. Reviewer agreed the marked tests are full
  `publish_release.py --execute` subprocess/git/GH boundary tests and that
  standing pytest still keeps requested-review gates plus dry-run/helper
  fail-closed sentinels. Reviewer did not recommend a smaller marker boundary.

### Slice 3: Nose Candidate Triage

- Candidate evaluated: achieve `_mask_fences` duplication across
  `goal_artifact_lib.py`, `goal_artifact_coordination_floors.py`,
  `goal_artifact_disposition.py`, `goal_artifact_closeout_evidence.py`,
  `goal_artifact_discussion.py`, and `goal_artifact_phase_routing.py`.
- Decision: defer. The repeated functions are inside one skill, but several
  modules explicitly document self-contained/no-sibling-import reasoning to
  avoid circular imports and keep closeout floor helpers leaf-like. This is a
  real nose advisory finding, but not a clear low-risk extraction during this
  goal.
- Applied action: none. Continue test-economics cleanup instead.

### Slice 4: Quality Runner Test Setup Cleanup

- Change: extracted `_commit_quality_runner_repo` in
  `tests/quality_gates/test_quality_runner.py` and replaced four repeated
  git-init/config/add/commit blocks in check-coverage selection tests.
- Proof: `pytest -q tests/quality_gates/test_quality_runner.py --durations=10
  --durations-min=0.01` passed 32 tests in 13.82s; `python3 -m ruff check
  tests/quality_gates/test_quality_runner.py` passed; `python3
  scripts/check_python_lengths.py --paths
  tests/quality_gates/test_quality_runner.py` passed.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request on 2026-06-05: run a three-hour quality goal after the first
  release, use nose actively but not exclusively, prefer shorter/faster pytest
  when confidence is unchanged, finish closeout even if it crosses the timebox,
  and continue to the next improvement if the primary goal closes early.
- Repository pickup state: `main` clean except for this draft artifact and ahead
  of `origin/main` by two post-release quality commits.
- Recent runtime posture from the prior quality pass: `check-coverage` around
  42s with a 45s budget, pytest around 21-27s median with a 140s budget,
  `check-current-pointer-writes` around 13s, `check-duplicates` around 10s, and
  `check-test-completeness` around 8s.
- Recent standing test economics: 244 Python test files, 107 nested
  CLI/subprocess fanout files, and clean pytest temp footprint.
- Recent nose advisory posture: top candidates included runtime bootstrap,
  adapter init/resolve blocks, `_string`/`optional_string`, `_mask_fences`, and
  `_git_paths`; these are advisory candidates, not automatic refactor orders.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Timebox: chose three hours because the user requested it. Closeout may cross
  the wall if already started; this prevents incomplete artifacts from saving a
  few minutes at the cost of trust.
- Primary target: chose pytest/lifecycle economics over pure clone-count
  reduction because the user wants less code and time when proof strength stays
  equal.
- Nose role: advisory. Nose can identify refactoring candidates, but the win is
  maintainability or cheaper proof, not a lower duplicate score.
- Jscpd role: out of scope for this run. Markdown duplicate gating stays on the
  existing document-only checker; code clone gating is deferred until after
  nose-led refactoring.
- Proof shape: prefer moving proof down to helper/in-process seams while keeping
  one boundary smoke. Rejected wholesale deletion because it can hide CLI,
  adapter, or packaging regressions.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Risk folded: reducing long pytest files can accidentally delete the only CLI
  or mutation-boundary proof. Boundary now requires a retained representative
  smoke or cheaper equivalent proof.
- Risk folded: nose can encourage noisy clone-count chasing. Non-goals and slice
  plan now require real maintenance or test-economics value before refactoring.
- Risk folded: broad pytest can consume a large share of a three-hour window.
  Verification cadence reserves broad proof for final closeout or substantial
  behavior surface changes.
- Over-worry not folded: coverage runtime may be the largest current quality
  hot spot, but the user explicitly prioritized pytest economy and proof design.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- issue #299: optional release-only sentinel coverage inventory. Surfaced by
  final disposition review as the concrete destination for the retro
  `capability:` improvement.

## Final Verification

- Focused release publish standing proof:
  `pytest --collect-only -q -m "not release_only"
  tests/quality_gates/test_release_publish.py
  tests/quality_gates/test_release_publish_real_host_delta.py` collected 8/27
  tests after the marker split. Before the change, the same files collected
  27/27 non-release tests.
- Focused standing release publish run: `pytest -q -m "not release_only"
  tests/quality_gates/test_release_publish.py
  tests/quality_gates/test_release_publish_real_host_delta.py --durations=20
  --durations-min=0.01` passed 8 tests, deselected 19, in 3.27s.
- Focused release-only release publish run: `pytest -q -m release_only
  tests/quality_gates/test_release_publish.py
  tests/quality_gates/test_release_publish_real_host_delta.py --durations=10
  --durations-min=0.01` passed 19 tests, deselected 8, in 29.15s.
- Focused quality-runner run: `pytest -q
  tests/quality_gates/test_quality_runner.py` passed 32 tests in 13.65s.
- Final broad lint: `ruff check charness scripts tests
  skills/public/*/scripts skills/support/*/scripts` passed.
- Final length gate: `python3 scripts/check_python_lengths.py --repo-root .
  --require-git-file-listing` passed for 668 files, with existing advisory
  near-limit warnings for `scripts/check_mutation_score.py`,
  `scripts/setup_agent_docs_lib.py`,
  `skills/public/handoff/scripts/chunked_routing_agentic.py`, and
  `tests/quality_gates/test_release_publish.py`.
- Final attention-state gate: `python3
  scripts/validate_attention_state_visibility.py --repo-root . --scan-root
  scripts --scan-root skills --scan-root-map ../charness-support=skills/support`
  passed for 69 files.
- Final broad non-release pytest: `pytest -q -m 'not release_only'
  tests/quality_gates tests/control_plane tests/test_*.py` passed 2140 tests,
  skipped 4, deselected 25, in 170.70s.
- Final changed-surface check: `python3 scripts/check_changed_surfaces.py
  --repo-root .` reported no unstaged changed paths after the implementation
  commits.
Retro: charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md
Host log probe: skipped: host-log-not-exposed: no `Host metric window:` line was recorded, so the host-log probe reported thread-wide proxy pressure only and no goal-scoped token/time/tool-call total is claimed.
Disposition review: charness-artifacts/critique/2026-06-05-3h-quality-test-economics-disposition-review.md
- Non-claims: no release was published; no release version or install manifest
  was changed; no live/provider proof was run; no jscpd gate was added; no nose
  code refactor was applied after `_mask_fences` was judged intentionally
  self-contained for now.

## User Verification Instructions

- To verify the standing-test split, run: `pytest --collect-only -q -m "not
  release_only" tests/quality_gates/test_release_publish.py
  tests/quality_gates/test_release_publish_real_host_delta.py`.
- To verify the release boundary proof still exists, run: `pytest -q -m
  release_only tests/quality_gates/test_release_publish.py
  tests/quality_gates/test_release_publish_real_host_delta.py`.
- To verify the final local quality proof, rerun the broad non-release pytest
  and lint commands listed in `## Final Verification`.
- Treat release publication, live/provider behavior, jscpd adoption, and
  goal-scoped host-cost totals as explicit non-claims.

## Auto-Retro

Session retro persisted at
`charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md` and
refreshed `charness-artifacts/retro/recent-lessons.md`.

Retro dispositions:

- applied: future quality goals now have a persisted recent lesson to collect
  standing-test economics and focused durations before acting on clone
  inventory.
- issue #299: optional release-only sentinel coverage inventory was filed and
  verified as `https://github.com/corca-ai/charness/issues/299`.
- applied: `_mask_fences` nose finding is explicitly recorded as deferred in
  this goal because the closeout-floor helpers are intentionally self-contained
  leaf modules; no code refactor was applied.

Disposition review: charness-artifacts/critique/2026-06-05-3h-quality-test-economics-disposition-review.md

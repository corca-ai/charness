# Achieve Goal: Testability Quality Skill Ratchet

Status: active
Created: 2026-06-03
Activation: `/goal @charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Discuss before activation: RESOLVED in-thread on 2026-06-03. The user first
asked whether test-quality DSL/testability work belongs in `quality` or a
separate skill. The recommended decision was accepted for goal shaping by the
follow-up "achieve" request: do not create a new public test skill now; keep
portable diagnosis and ratchet policy in `quality`, while Python/layout-specific
DSL and probes stay repo-local. Live/release proof is explicitly a non-claim for
this goal unless later scope changes touch release surfaces.

## Active Operating Frame

- Current slice: Slice 5 — first backlog conversion cluster.
- Next action: convert the first clean import-safe `inventory_*` tests from
  subprocess boundary assertions to in-process calls where the target does not
  shell out internally, preserving one thin real-boundary smoke where needed.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad proof at
  closeout, with live/release proof recorded only if scope changes.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Raise this repo's test quality while making the portable `quality` skill strong
enough to guide similar work in other repos.

This goal completes the next obligation from
[docs/testability-dsl-initiative.md](../../docs/testability-dsl-initiative.md):
turn the boundary-bypass probe from an advisory sensor into a structural
ratchet, and skillify the portable parts without pretending a stack-specific
test DSL is a public Charness skill.

The outcome is three-part:

- This repo has a committed boundary-bypass baseline, no-increase policy,
  documented exemptions, and `run-quality` wiring.
- The existing `quality` testability lens can diagnose repo-local test
  ergonomics helpers or DSLs: whether they are lazy, composable, and simple,
  and whether they are comfort-paving a low-testability boundary.
- A portable boundary-bypass payload/ratchet contract exists so Go, TypeScript,
  Python, or other repos can ship their own stack-specific probes against the
  same quality policy.

## Non-Goals

- Do not create a new public `test` skill in this goal. The public concept is
  still overall quality posture; a future support skill may be justified only
  after the payload/ratchet machinery repeats across repos.
- Do not generalize `tests/dsl.py` into Charness public skill prose or exports.
  It is Python/pytest/repo-layout code and stays repo-local.
- Do not convert the full 134-candidate boundary-bypass backlog in this goal.
  The first conversion cluster may happen only if needed to prove the ratchet;
  broad backlog cleanup is a follow-up slice after the gate exists.
- Do not claim live, release, scheduled CI, or cross-repo proof unless those
  proof levels are explicitly run and recorded during the goal.
- Do not close #283, decide #184, or run the v0.16.0 real-host smoke as part of
  this goal. Those are adjacent handoff items, not this objective.

## Boundaries

- Portable policy belongs in `skills/public/quality/` references and helpers.
  Stack-specific target resolution belongs in repo-local `scripts/` and tests.
- The ratchet must fail only on clear regression over a committed baseline, not
  on advisory detector noise. Exemptions need a rationale and should mirror the
  coverage-floor style.
- Fix ratchet correctness before enforcement: avoid `.read_text(` over-match,
  stabilize candidate counting, clarify "candidate" wording, and distinguish
  targets that spawn internally from clean in-process wins.
- Generated/export/plugin surfaces must be synced before verification if any
  touched file participates in those mirrors.
- Meaningful repo work in this goal should be committed with the goal artifact
  and initiative updates, following the repo's phase barriers.

## User Acceptance

What the user can do to verify completion directly:

- Read `skills/public/quality/references/testability-and-selection.md` and the
  new/updated boundary-bypass reference and confirm they are stack-neutral.
- Read the repo-local boundary-bypass baseline/exemption files and confirm they
  describe this repo rather than public Charness policy.
- Run the quality command or targeted ratchet command and see the current repo
  pass at the committed baseline, then understand what would fail on an
  increase.
- Inspect `tests/dsl.py` and confirm it remains repo test ergonomics, not a
  public skill dependency.

## Agent Verification Plan

### Low-Cost Checks

- Targeted pytest for boundary-bypass probe/ratchet behavior.
- `ruff check` on changed Python files.
- Goal artifact validation:
  `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md`.
- Markdown/reference/link checks for touched skill/docs surfaces.
- `run-quality` targeted or read-only subset that includes the new ratchet path.

### High-Confidence Checks

- Full `./scripts/run-quality.sh --read-only` before final completion unless an
  explicit environment blocker is recorded.
- Fresh-eye bounded critique for the ratchet and skill-boundary change, with a
  packet covering changed files, invariants, proof, and non-claims.
- Dogfood the `quality` recommendation path: a consumer-style prompt should
  route to `quality`, not to a newly invented public test skill.
- Stack-neutral contract proof: validate at least one non-Python-shaped
  boundary-bypass payload or adapter command-slot example against the portable
  reference/schema so the portability claim is not only Python producer text.

### External Or Live Proof

- External/live proof is not planned. No release, scheduled mutation run,
  cross-repo consumer run, or GitHub issue closeout is required for this goal.
  If the implementation unexpectedly touches release surfaces or tracked issue
  closeout, update `## Coordination Cues` and run the owning workflow first.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Shape and validate the achieve goal | Prevent scope drift before code changes | This artifact passes normal and pursue-ready validation | done |
| 1 | Ratchet-correctness fixes in the advisory probe | Enforcement before correctness would freeze noisy counts | Targeted tests for over-match, candidate naming/count stability, internal-spawn classification | done |
| 2 | Baseline, exemptions, and no-increase policy | Converts sensor into a structural ratchet | Committed baseline, rationale-bearing exemptions, failing regression fixture, passing current repo | done |
| 3 | Wire ratchet into `run-quality` | Makes the rule part of standing quality instead of an optional script | `run-quality --read-only` includes the ratchet with visible advisory/fail state | done |
| 4 | Portable `quality` skillification | Lets other repos reproduce the policy without Python/layout coupling | Updated testability lens and boundary-bypass payload/ratchet reference; find-skills routes task to `quality` | done |
| 5 | First backlog conversion cluster | Proves the gate points to real structural cleanup | Import-safe `inventory_*` tests converted subprocess to in-process where targets do not shell out internally | pending |
| 6 | Sync, critique, broad verification, closeout | Finish with honest proof and non-claims | Synced surfaces, fresh-eye critique, green gates or recorded blockers, final artifact complete | pending |

Test-duplication pressure expectation:

- Slices 1-4 should add targeted tests only where they prove detector,
  ratchet, or stack-neutral contract behavior; each slice log must record
  whether tests were added and include `--test-pressure` evidence when they
  were.
- Slice 5 intentionally changes existing tests; it should prefer in-place
  subprocess-to-in-process conversion over adding parallel duplicate coverage.
- Slice 6 must classify any broad duplicate/pressure finding as new-slice-local
  versus accumulated suite debt before closeout.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — Gather: n/a — this goal is shaped from in-repo artifacts and
  skill surfaces, not an external URL, Slack, Notion, Docs, or Drive source.
- **Release step** — Release: n/a — no version bump or install-manifest edit is
  planned.
- **Issue closeout step** — Issue closeout: n/a — #283 and #184 are context only;
  this goal does not resolve tracked GitHub issues unless scope changes.

## Slice Log

### Slice 0: Shape and validate the achieve goal

- Objective: Create the activation artifact and lock the public-skill boundary
  before implementation.
- Why this approach: The user asked to use `achieve` after deciding that
  portable test-quality diagnosis belongs in `quality`, not a new public test
  skill.
- Commits: `afc4d848` Shape testability quality ratchet achieve goal.
- What changed: Added this goal artifact with scope, non-goals, slice plan,
  test-pressure expectations, and fresh-eye critique provenance.
- Alternatives rejected: New public test skill now; stack-specific DSL in
  public skill prose; raw advisory count enforcement before detector fixes.
- Targeted verification: `check_goal_artifact.py` normal and `--pursue-ready`,
  markdown/doc/command/secrets checks, full `check-markdown.sh`.
- Test duplication pressure: no tests added.
- Critique: parent-delegated fresh-eye reviewers plus counterweight; Act
  findings folded before commit.
- Off-goal findings: none.
- Lessons carried forward: keep `quality` diagnostic, not DSL-authoring.
- Metrics: not measured for Slice 0 beyond command outcomes above.

### Slice 1: Ratchet-correctness fixes

- Objective: Fix boundary-bypass detector correctness before any no-increase ratchet freezes its counts.
- Why this approach: The advisory probe had known over-reporting and did not distinguish clean in-process conversions from targets that still spawn internally; enforcing it first would create noisy debt.
- Commits: `0cab1e5c` Fix boundary-bypass inventory classification.
- What changed: Parsed spawn-like calls with ast so script paths mentioned only in assertions no longer count; removed raw .read_text( as a behavior assertion signal; added clean_inprocess_targets/internal_boundary_targets plus internal_boundary_count; updated CLI summary wording; removed the now-active ratchet goal from handoff's non-issue Next Session candidates.
- Alternatives rejected: Regex-only target filtering; keeping convertible_count as candidate_count minus keep-boundary while only adding a note about internal spawns.
- Targeted verification: python3 -m pytest tests/test_boundary_bypass_inventory.py (7 passed); ruff check scripts/inventory_boundary_bypass_lib.py scripts/inventory_boundary_bypass.py tests/test_boundary_bypass_inventory.py; python3 scripts/inventory_boundary_bypass.py --repo-root . => 96 candidates, 54 clean-convertible, 42 internally-spawning, 23 likely keep-boundary across 235 test files; changed-surface validators including packaging, docs/secrets, integration/control-plane dry-runs, and pytest selected surface (2101 passed, 4 skipped).
- Test duplication pressure: Expanded one existing focused test file from 4 to 7 cases; no parallel duplicate test module added; tests cover three new failure modes named by the goal.
- Critique: Slice-level critique deferred to the larger ratchet bundle unless later edits introduce a new risk boundary; Slice 0 fresh-eye already locked the detector-correctness concerns.
- Off-goal findings: Selected pytest initially exposed a stale handoff non-issue candidate for this ratchet work; fixed by moving that pickup to the active goal artifact and keeping `## Next Session` issue-linked.
- Lessons carried forward: Do not enforce advisory counts until target extraction and classification semantics are stable.
- Metrics: Probe line headroom after edits: inventory_boundary_bypass_lib.py 170/480; test file 169/800.

### Slice 2: Baseline and no-increase ratchet

- Objective: Commit a repo-local baseline, rationale-bearing exemption file, and no-increase checker for the corrected boundary-bypass payload.
- Why this approach: The advisory sensor needs a deterministic ratchet before future test code can add new boundary-bypass patterns silently.
- Commits: `43e70e4c` Add boundary-bypass no-increase ratchet.
- What changed: Added boundary_bypass_ratchet_lib.py and check_boundary_bypass_ratchet.py; added scripts/boundary-bypass-baseline.json with current corrected baseline; added empty scripts/boundary-bypass-exemptions.txt requiring '# why:' rationale; added in-process ratchet tests; synced plugin exports.
- Alternatives rejected: A summary-count-only baseline without candidate keys; prose-only exemptions; wiring directly into run-quality before the ratchet command had focused tests.
- Targeted verification: python3 -m pytest tests/test_boundary_bypass_inventory.py tests/test_boundary_bypass_ratchet.py (11 passed); ruff/length/attention checks; validate_packaging/validate_packaging_committed; validate_integrations plus sync_support/update_tools dry-runs; python3 scripts/check_boundary_bypass_ratchet.py --repo-root .; selected pytest surface passed (2105 passed, 4 skipped).
- Test duplication pressure: Added one focused ratchet test module with 4 cases covering matching baseline, new unexempt candidate failure, missing # why: rationale failure, and exemption allowance. This is new behavior, not duplicate inventory-probe coverage.
- Critique: No new fresh-eye pass yet; this is still inside the ratchet bundle that will receive bounded critique before closeout.
- Off-goal findings: None.
- Lessons carried forward: Baseline enforcement should track stable candidate keys as well as counts so new targets in existing test files cannot hide behind unchanged row counts.
- Metrics: Baseline: 96 candidate rows, 159 candidate keys, 54 clean-convertible, 42 internally-spawning, 23 likely keep-boundary.

### Slice 3: Run-quality ratchet wiring

- Objective: Make the boundary-bypass no-increase ratchet part of the standing read-only quality gate.
- Why this approach: A ratchet command outside run-quality still relies on operator memory; standing wiring makes new boundary-bypass tests costly immediately.
- Commits: `130bcd3d` Wire boundary-bypass ratchet into run-quality.
- What changed: Queued check-boundary-bypass-ratchet in scripts/run-quality.sh after test-structure gates; updated the quality-runner test support map; synced plugin run-quality.sh.
- Alternatives rejected: Leaving the ratchet as a manual command until final closeout; wiring it before the baseline checker had its own tests.
- Targeted verification: CHARNESS_QUALITY_LABELS=check-boundary-bypass-ratchet ./scripts/run-quality.sh --read-only => Quality summary: 1 passed, 0 failed; focused pytest test_quality_runner + ratchet/inventory tests passed (43 passed); bash -n/check-shell, ruff, length, attention, packaging, integrations/control-plane dry-runs; selected pytest surface passed (2105 passed, 4 skipped).
- Test duplication pressure: No new tests added in this slice; updated existing test helper metadata so existing quality-runner tests exercise the new label path.
- Critique: No new fresh-eye pass yet; ratchet bundle critique remains scheduled before closeout.
- Off-goal findings: None.
- Lessons carried forward: A no-increase checker only becomes structural when it is queued by the standard read-only quality gate.
- Metrics: New run-quality label runtime: 493ms in the direct label run.

### Slice 4: Portable quality skillification

- Objective: Make the portable `quality` skill strong enough to guide other
  repos toward a boundary-bypass payload and no-increase ratchet without
  exporting this repo's Python detector or pytest DSL.
- Why this approach: The user asked whether the test-quality DSL/testability
  work belongs in `quality` or a separate skill; this slice keeps the public
  concept in `quality` while leaving stack-specific probes and DSLs repo-local.
- Commits: `b2404442` Skillify boundary-bypass ratchet guidance.
- What changed: Added a stack-neutral boundary-bypass payload reference, a
  portable payload example, and a validator script under `quality`; expanded the
  testability reference to separate DSL ergonomics from structural testability
  and boundary-bypass ratchets; added a find-skills testability trigger so
  consumer-style prompts route to `quality`; synced plugin exports.
- Alternatives rejected: A new public test skill now; exporting the Python
  boundary-bypass detector as public policy; treating a lazy/composable DSL as
  sufficient proof of testability without a boundary ratchet.
- Targeted verification: `validate_boundary_bypass_payload.py` accepted the
  non-Python-shaped example payload; targeted pytest for payload validator and
  find-skills recommendation passed; find-skills dogfood prompt returned
  `quality` with matched trigger `testability`; changed-surface validators
  passed for packaging, markdown/docs/secrets, Cautilus proof policy, skills,
  public-skill policy/dogfood, ruff, py_compile, length, and attention-state
  visibility; selected pytest surface passed (2108 passed, 4 skipped).
- Test duplication pressure: Added one focused quality-gate test module with 2
  validator cases and one find-skills recommendation case in an existing module;
  this covers new portable contract and routing behavior rather than duplicating
  the repo-local Python detector tests.
- Critique: No new fresh-eye pass yet; final bounded critique remains scheduled
  for the ratchet plus skill-boundary bundle before closeout.
- Off-goal findings: None.
- Lessons carried forward: `quality` should diagnose test DSL ergonomics and
  boundary bypass pressure, not author stack-specific DSLs.
- Metrics: `skills/public/quality/SKILL.md` is 198 lines after adding the new
  reference, below the 200-line skill cap.

## Context Sources

- [docs/handoff.md](../../docs/handoff.md): names the testability initiative,
  shipped DSL/probe commits, and next ratchet obligation.
- [docs/testability-dsl-initiative.md](../../docs/testability-dsl-initiative.md):
  source of the A/B reframe, three-layer architecture, done/non-claims, and
  remaining sequence.
- [charness-artifacts/quality/latest.md](../quality/latest.md): current quality
  posture and standing test-economics context.
- [charness-artifacts/retro/recent-lessons.md](../retro/recent-lessons.md):
  recent traps relevant to handoff/doc edits, broad gates, and headroom.
- [skills/public/quality/SKILL.md](../../skills/public/quality/SKILL.md) and
  [skills/public/quality/references/testability-and-selection.md](../../skills/public/quality/references/testability-and-selection.md):
  current quality/testability ownership.
- [skills/public/create-skill/SKILL.md](../../skills/public/create-skill/SKILL.md):
  boundary rule for public vs support skills and portable authoring.

## Interview Decisions

- **Skill boundary:** options were (A) new public test skill, (B) support skill
  now, (C) strengthen `quality` and keep DSL repo-local. Chosen: C. Rejected A
  because the public concept would smuggle Python/test-framework specifics;
  rejected B for now because the common machine contract has not repeated across
  multiple repos.
- **DSL role:** options were (A) make DSL the main quality improvement, (B)
  treat DSL as ergonomics only and pair it with testability enforcement.
  Chosen: B. The prior initiative established that DSL improves test-code
  maintainability, not production-code testability.
- **Ratchet timing:** options were (A) enforce the current advisory count as-is,
  (B) fix detector correctness then enforce no-increase. Chosen: B. A noisy
  baseline would tax future cleanup and hide the real boundary smell.
- **Backlog conversion:** options were (A) convert all candidates now, (B)
  convert one import-safe cluster after the gate exists. Chosen: B. The goal is
  first to prevent worsening; broad cleanup is valuable but larger.

## Plan Critique Findings

- Fresh-Eye Satisfaction: parent-delegated. Reviewers:
  `019e8d41-4933-7261-980f-d176fdd8559c` (achieve lifecycle/activation) and
  `019e8d41-62c0-7c43-b4af-462138fa663d` (quality boundary/portability), with
  counterweight pass `019e8d43-0435-7d33-a09a-d6e399900a86`.
- Folded: enforcing a raw advisory count risks freezing detector noise; Slice 1
  must fix correctness before Slice 2 enforcement.
- Folded: a public test skill would be over-broad and stack-coupled; the goal
  keeps the public surface in `quality` and leaves future support extraction as
  a non-goal unless repeated evidence appears.
- Folded: converting subprocess tests through the DSL alone can comfort-pave a
  bad boundary. The plan separates DSL ergonomics from in-process reachability.
- Folded: quality must diagnose repo-local DSL/test-helper ergonomics, not sound
  like it authors stack-specific DSLs.
- Folded: portability proof must include a non-Python-shaped payload or adapter
  example, not only a Python probe and routing text.
- Folded: each slice log must record test-duplication pressure when tests are
  added or expanded.
- Not folded: a full cross-repo proof would be stronger but is too expensive
  for this goal; the final report must name it as a non-claim.

## Off-Goal Findings

None yet.

## Final Verification

Not run yet. The goal is active; final broad proof belongs to Slice 6.

## User Verification Instructions

After completion, inspect the files named in `## Context Sources`, run the final
quality command recorded in `## Final Verification`, and review the non-claims
before treating this as portable across other repos.

## Auto-Retro

Not run yet. Auto-Retro belongs to the After phase.

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

- Current slice: Slice 2 — baseline, exemptions, and no-increase policy.
- Next action: design the committed boundary-bypass baseline/exemption shape and
  the no-increase checker using the corrected Slice 1 payload.
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
| 2 | Baseline, exemptions, and no-increase policy | Converts sensor into a structural ratchet | Committed baseline, rationale-bearing exemptions, failing regression fixture, passing current repo | in progress |
| 3 | Wire ratchet into `run-quality` | Makes the rule part of standing quality instead of an optional script | `run-quality --read-only` includes the ratchet with visible advisory/fail state | pending |
| 4 | Portable `quality` skillification | Lets other repos reproduce the policy without Python/layout coupling | Updated testability lens and boundary-bypass payload/ratchet reference; find-skills routes task to `quality` | pending |
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
- Commits:
- What changed: Parsed spawn-like calls with ast so script paths mentioned only in assertions no longer count; removed raw .read_text( as a behavior assertion signal; added clean_inprocess_targets/internal_boundary_targets plus internal_boundary_count; updated CLI summary wording; removed the now-active ratchet goal from handoff's non-issue Next Session candidates.
- Alternatives rejected: Regex-only target filtering; keeping convertible_count as candidate_count minus keep-boundary while only adding a note about internal spawns.
- Targeted verification: python3 -m pytest tests/test_boundary_bypass_inventory.py (7 passed); ruff check scripts/inventory_boundary_bypass_lib.py scripts/inventory_boundary_bypass.py tests/test_boundary_bypass_inventory.py; python3 scripts/inventory_boundary_bypass.py --repo-root . => 96 candidates, 54 clean-convertible, 42 internally-spawning, 23 likely keep-boundary across 235 test files; changed-surface validators including packaging, docs/secrets, integration/control-plane dry-runs, and pytest selected surface (2101 passed, 4 skipped).
- Test duplication pressure: Expanded one existing focused test file from 4 to 7 cases; no parallel duplicate test module added; tests cover three new failure modes named by the goal.
- Critique: Slice-level critique deferred to the larger ratchet bundle unless later edits introduce a new risk boundary; Slice 0 fresh-eye already locked the detector-correctness concerns.
- Off-goal findings: Selected pytest initially exposed a stale handoff non-issue candidate for this ratchet work; fixed by moving that pickup to the active goal artifact and keeping `## Next Session` issue-linked.
- Lessons carried forward: Do not enforce advisory counts until target extraction and classification semantics are stable.
- Metrics: Probe line headroom after edits: inventory_boundary_bypass_lib.py 170/480; test file 169/800.

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

Not run yet. The goal is draft and inactive.

## User Verification Instructions

After completion, inspect the files named in `## Context Sources`, run the final
quality command recorded in `## Final Verification`, and review the non-claims
before treating this as portable across other repos.

## Auto-Retro

Not run yet. Auto-Retro belongs to the After phase.

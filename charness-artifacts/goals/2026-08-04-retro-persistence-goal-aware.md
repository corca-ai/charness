# Achieve Goal: Make retro persistence goal-aware without breaking session retros

Status: active
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-retro-persistence-goal-aware.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: Slice 1 is implemented and locally proven; final bundle
  proof and closeout records remain.
- Current slice: goal-aware persistence validation and no-write proof.
- Current slice intent: make the owning goal an explicit, opt-in input at the
  retro write boundary and prove mismatches fail before any write. Once active,
  this names the reviewable-intent unit in progress; critique and broad proof
  do not re-fire within one unchanged intent.
- Next action: run the verification-locked closeout bundle, then flip the
  artifact only if its final evidence remains complete.
- Verification cadence: cheap deterministic checks at commit boundaries;
  focused and fresh-eye proof at slice boundaries; strongest applicable proof
  at final closeout.
- Gate cadence: use `run_slice_closeout.py --skip-broad-pytest` before lock;
  use the verification-locked closeout for the final bundle when the changed
  surface requires it.
- Slice review packet: include intent, owner, changed/generated surfaces,
  expected invariants, no-write proof, non-claims, and reviewer questions.
- History boundary: keep this frame current; move completed detail to the
  Slice Log, Final Verification, and Auto-Retro sections.

## Goal

Change the retro persistence boundary so an achieve closeout retro can carry
and validate its owning goal identity before any artifact, summary, lesson
index, or event write, while ordinary session retros remain supported without
a goal. Resolve issue #504 with local proof and an honest closeout record.

## Non-Goals

- Do not force ordinary session retros to name a goal.
- Do not redesign lesson selection, rolling telemetry, or the #496 hollow-refill
  predicate.
- Do not add a semantic meta-gate that judges whether a retro lesson is correct;
  this goal protects evidence identity and write ordering only.
- Do not publish a release, create a PR, or claim provider/live proof.

## Boundaries

- The implementation remains local until the final bundle. A final push is
  allowed only if the current pre-push gate passes; no gate may be weakened.
- #504 may be closed only after the issue closeout floor is satisfied: validated
  carrier, delegated resolution critique, distinct behavior verdict, and
  GitHub state readback.
- Goal-aware mode is opt-in at the persistence boundary. Legacy session mode
  must retain its current behavior.
- A goal mismatch must fail before writing the retro, recent-lessons summary,
  lesson-selection index, related event record, or any newly-created output
  directory.
- The identity contract is exact and field-bound: `--goal-path` resolves to one
  repo-relative POSIX goal path and its canonical filename slug; goal-aware
  input must carry exactly one `Goal:` metadata field whose trimmed value is
  exactly that path or that slug. Text elsewhere cannot satisfy the match;
  malformed, missing, or different fields refuse before write. New goal-aware
  output uses the canonical repo-relative path form.

## User Acceptance

- A goal closeout can invoke persistence with its owning goal path and succeeds
  only when the retro identity matches that goal.
- A different goal path, missing goal identity in goal-aware mode, or malformed
  goal evidence fails before any target output changes.
- A normal session retro still persists without a goal path.
- The closeout record contains commands and artifact paths for reproducing the
  matching, mismatch, and legacy-session cases.

## Agent Verification Plan

### Low-Cost Checks

- Read all persistence callers and the achieve closeout consumer before coding;
  verify the owner instead of treating #504's candidate direction as a plan.
- Run focused retro persistence tests, artifact validators, source/plugin parity
  checks, and `git diff --check` at commit boundaries.
- Run `describe_goal_closeout_shape.py` and `check_goal_artifact.py` before any
  final status or issue-closeout claim.

### High-Confidence Checks

- Add positive, mismatch, missing-identity, and legacy-session tests.
- Test the Python library boundary directly as well as the CLI; the existing
  release retro caller must continue to work with its omitted goal path.
- Use temporary output directories and enabled `.charness/t-events` storage to
  prove mismatch rejection leaves the full side-effect tree byte-identical,
  including absent directories and append/rotation files.
- If the first fresh-eye review finds and drives a verdict-logic repair, run the
  required second review of the repaired surface before the locked mutation
  producer; a clean first review discharges that second-round obligation.
- Freeze the changed surface, then run the strongest applicable standing proof
  and generated plugin mirror/import checks.

### External Or Live Proof

- No provider or production proof is required; the behavior is local file
  identity and write ordering.
- If #504 is closed, use `gh issue view` or the issue adapter for a separate
  final state readback; a commit exit code is not remote proof.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Map persistence callers and choose the identity API | The issue direction is a hypothesis; verify its premise before coding | Caller/consumer map, exact `Goal:` grammar, sibling and generated-surface inventory | completed |
| B | Add optional goal-aware persistence validation | The write boundary is where wrong ownership should stop | Library + CLI input, exact field comparison, pre-write refusal, unchanged session mode | completed |
| C | Prove positive and negative behavior | Shape-valid output is not enough; mismatches must be unable to write silently | Focused direct-library/CLI tests, full side-effect-tree snapshot, source/plugin parity | completed |
| D | Close out the capability and issue | The fix needs durable evidence and separate remote state proof | Locked quality proof, retro, claims review, carrier/readback | in progress |

## Operator Decision Queue

none — the operator confirmed the four activation decisions: use `--goal-path`,
preserve ordinary session retros, fail before any write, and keep #496 separate.
Issue close and push remain conditional on their final gates.

## Coordination Cues

Routing: achieve — own the activation artifact and slice lifecycle.
Routing: debug — establish #504's root cause before changing the helper.
Routing: impl — change the persistence boundary and synchronized surfaces.
Routing: quality — select focused and final verification without inventing live proof.
Routing: critique — challenge the API owner, write ordering, and closeout claims.
Routing: retro — record the next improvement and durable lesson.
Routing: issue — carry #504's problem-first resolution and conditional closeout.
Gather: charness-artifacts/issue/2026-08-04-retro-persistence-goal-binding.md — the external issue body is already captured locally.
Release: n/a — no version or install-manifest surface is in scope.
Issue closeout: #504 — direct-commit carrier only after `validate-closeout-draft` and `verify-closeout` proof.

## Discuss Before Activation

- Discuss before activation: resolved — the user approved an opt-in `--goal-path` contract; ordinary session retros remain goal-free; mismatches fail before any write; #496 stays separate; and #504 closure/push are deferred to the final gated bundle.

## Slice Log

Slice 1 is recorded below; the remaining closeout work is tracked in the
active frame and Slice Plan.

### Slice 1: Goal-aware persistence contract

- Objective: Move achieve goal identity validation to the shared retro write boundary and prove mismatch refusal before every derived write.
- Why this approach: The caller map showed the shared library owns the first artifact, event, summary, and index writes while achieve only checked identity later.
- Commits: `9768f95d` (`fix: bind retro persistence to owning goals`); follow-up
  durable closeout records remain to be committed after final proof.
- What changed: scripts/retro_persistence_lib.py and CLI; achieve closeout token binding; retro/achieve workflow instructions; synchronized plugins/charness mirrors; direct-library/CLI tests; debug and critique records.
- Alternatives rejected: Rejected universal goal requirements because release/session callers are intentionally goal-free; rejected semantic lesson-quality validation and #496 combination.
- Targeted verification: 13-test initial proof, 103-test repair proof, 106-test pre-lock proof, 111 focused tests after the heading-boundary and slug-canonicalization repairs, then 112 tests with the maintained achieve/retro caller-contract regression; source/plugin diffs are identical; reviewer boundary fingerprints were clean for all initial/repair windows and the recorded repair reads.
- Test duplication pressure: Focused persistence and achieve binding coverage expanded by 9 tests; duplicate-pressure sample deferred to the pre-lock aggregate gate.
- Critique: Round 1 found metadata-location, repo-root resolution, workflow-routing, and numeric-consumer blockers. Round 2 found fence-length/trailing-text and Setext-boundary blockers. The final pre-lock repair read found an indented-heading boundary gap and missing slug canonicalization; both were repaired, and the subsequent repair-read found no concrete implementation blocker. The final dogfood-record read remains carried by the critique packet.
- Off-goal findings: #496 remains independent; no provider/live/release proof or issue close was attempted.
- Issue causal review: the local caller contract is now regression-tested, but the
  delegated review found no host-level proof that an agent invocation cannot omit
  `--goal-path`; the durable causal record keeps any remote close claim deferred.
- Lessons carried forward: Keep exact semantic identity at the write owner, mask representations before parsing, and read the repaired verdict surface again before locked proof.
- Metrics: Host tool exposed reviewer findings; no per-goal host timing window was requested.

## Context Sources

1. [design-north-star.md](../../docs/design-north-star.md) — P1/P3 keep
   judgment out of a new blocking gate; P4/P5 require distinct evidence at the
   issue-close boundary.
2. [#504 problem-first carrier](../issue/2026-08-04-retro-persistence-goal-binding.md) — the contemporaneous issue record for the observed mismatch, impact, and candidate direction; its later-dated example is explanatory context, not proof for this goal.
3. [later-added completed goal context](2026-08-08-decide-where-a-recurring-lesson-lives.md) — a later-dated record that explains the concrete failure and repaired goal-bound retro; it is not contemporaneous proof for this August 4 goal.
4. [later-added goal retro context](../retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md) and [recent lessons](../retro/recent-lessons.md) — later-dated explanatory context and next-session guidance, not contemporaneous proof for this goal.
5. `skills/public/retro/scripts/persist_retro_artifact.py`, `scripts/retro_persistence_lib.py`, and `tests/quality_gates/test_retro_persistence.py` — current owner and proof seams inspected while shaping.

## Interview Decisions

1. Identity input: `--goal-path` versus `--goal-slug` versus no goal-aware mode.
   Chose `--goal-path` for closeout mode because the helper can inspect the
   canonical artifact and avoid two independent slug sources. No argument
   remains the ordinary session mode. Axis: none — the owning goal path is a
   repo-local singleton for one invocation.
2. Failure timing: validate after writing versus before writing. Chose
   before-writing refusal because late validation caused the observed closeout
   churn and could leave summary/index state ahead of the retro. Axis: none —
   filesystem mutation ordering is the invariant.
3. Scope: combine #496 or force every retro to be goal-scoped versus keep a
   narrow #504 goal. Chose the narrow goal; #496 has a separate semantic
   predicate owner. Axis: `retro kind` — session and achieve-closeout retros
   are intentionally distinct modes.
4. External boundary: close/push during implementation versus at final bundle.
   Chose final bundle only, with the existing closeout floor and no release,
   tag, or PR. Axis: `publication stage` — local proof and remote readback are
   separate stages.
5. Identity representation: loose token containment versus an exact `Goal:`
   field. Chose exact field matching against the normalized repo-relative goal
   path or its exact filename slug, with new goal-aware output using the path
   form. This preserves existing slug-shaped retros without allowing incidental
   prose to bind. Axis: `evidence representation` — only the metadata field is
   identity-bearing; body prose is not.

## Plan Critique Findings

- Folded blocker: a helper that always requires a goal would break legitimate
  session retros; the boundary is explicitly opt-in.
- Folded blocker: writing before checking identity would repeat the observed
  mismatch; the plan includes no-write assertions over all derived outputs.
- Folded blocker: the no-write proof snapshots the retro output directory and
  enabled `.charness/t-events`, not only four named files; this covers append,
  rotation, deletion, and directory creation.
- Folded blocker: validation lives in `scripts/retro_persistence_lib.py`, with
  a direct-library test; the CLI is only one transport and the release caller's
  omitted-goal path remains a compatibility proof.
- Over-worry not folded: a universal semantic validator for retro lesson quality
  is outside this goal and would violate floor-addition restraint.
- Over-worry not folded: every achieve producer need not be migrated before the
  known persistence boundary is proven; caller inventory decides whether a
  follow-up is real.
- Premise check: the candidate direction was verified against the live
  persistence CLI, library, adapter, and test callers before shaping.
- Fresh-eye provenance: bounded critique of the saved packet is required before
  implementation lock-in, and a distinct closeout-claims review is required
  before completion.
- Counterweight triage: exact identity and complete no-write coverage are
  `Act Before Ship`; concrete side-effect fixtures are `Bundle Anyway`; a
  semantic lesson-quality gate and #496 combination are `Over-Worry`; broad
  producer migration is `Valid but Defer` until caller inventory proves need.
- Repair-read: delegated Huygens review returned Pass with no blockers after the
  exact identity, direct-library, full-tree no-write, and conditional-review
  repairs; boundary fingerprint `retro-goal-design-critique-repair-read-1` was
  clean.
- Slice 1 review record: round 1 delegated reviewers found blockers in
  metadata-location parsing, repo-root resolution, workflow routing, and the
  numeric-only closeout consumer; round 2 found fence-length/trailing-text and
  Setext-heading boundary blockers; the earlier final delegated repair-read
  found no concrete implementation blocker. A later pre-lock repair read found
  that Markdown-valid indented headings and slug-only output needed one more
  repair; the parent added all-width no-write coverage and canonical output,
  then a final delegated repair-read passed. All reviewer boundary fingerprints
  verified clean. The later dogfood-record read is carried by the critique
  packet and remains the bound review record for closeout.

## Off-Goal Findings

#496 remains open and independent; it is not a retro-persistence acceptance
criterion. Publication-state reconciliation belongs at the final push boundary,
not before the read-only caller map in Slice A.

## Final Verification

Pre-lock gate: completed — `run_slice_closeout.py --skip-broad-pytest
--ack-cautilus-skill-review` completed with all structural, sync, and
deterministic verify phases passing; broad pytest was intentionally skipped by
the pre-lock policy.
Retro: charness-artifacts/retro/2026-08-04-retro-persistence-goal-aware-closeout.md
Host log probe: skipped: host-log-not-exposed: no goal-scoped host metric window was requested, so host efficiency is not claimed.
Disposition review: charness-artifacts/critique/2026-08-04-retro-persistence-goal-aware-disposition-review.md

## User Verification Instructions

After activation, follow the Slice Plan. At closeout, run the documented
positive, mismatch, and legacy-session commands from the final verification
record and inspect the no-write proof before accepting #504 as closed.

## Auto-Retro

Retro dispositions: applied: goal-aware persistence validation, canonical output, and full no-write proof.
Structural follow-up: none — host invocation enforcement is unavailable in this local contract, so no additional guard is claimed.

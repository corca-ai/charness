# Achieve Goal: #258: review/critique subagents must not mutate the parent worktree git index at closeout (silent-regression trap)

Status: complete
Created: 2026-05-30
Activation: `/goal @charness-artifacts/goals/2026-05-30-258-subagent-git-index-hygiene.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

#258: review/critique subagents must not mutate the parent worktree git index at closeout (silent-regression trap)

**Source handoff entry #1: #258: Review subagents can corrupt the parent worktree's git index (silent-regression risk at closeout)**

> ## Observed problem
>
> During the #255 `achieve` run, fresh-eye **review/critique subagents** (spawned
> via the Agent tool, running in the *same* working tree) verify "no regression"
> by exercising the pre-change behavior. To do so, a subagent checked out a
> base-commit version of a source file. This left the **parent session's git
> index** holding the stale, pre-change version of
> `skills/public/achieve/scripts/goal_artifact_lib.py` as a *staged reversion*,
> while `HEAD` and the worktree held the correct post-change version.
>
> ## Operator experience / cost
>
> At closeout, a routine `git add -A && git commit` would have **silently
> re-committed the deleted code** — undoing the slice's change — because the
> index had the reversion staged. It was caught only by noticing the unexpected
> `MM` state in `git status` and diffing index-vs-HEAD *before* committing. A less
> careful closeout would have shipped the regression with all gates green (the
> reverted code is internally consistent and passes its own tests).
>
> **JTBD:** "When I delegate a fresh-eye review, I need it to not mutate my
> working state, so my closeout commit reflects exactly what I built."
>
> ## Evidence
>
> - `git status --short` → `MM skills/public/achieve/scripts/goal_artifact_lib.py`
> - `git diff --cached HEAD` → the removed `is_non_trivial_goal` / `_TRIVIAL_GOAL_MARKER` **re-added** in the index.
> - `git diff` (worktree vs index) → the exact inverse (so worktree == HEAD == correct).
> - Recovery: `git add` of the correct worktree version made index == HEAD, and the file dropped out of the closeout commit.
>
> ## Scope / blast radius
>
> Latent **silent-regression trap** for any workflow that spawns review/critique
> subagents in the shared worktree: `achieve` (plan/impl/disposition critiques),
> `issue` causal-review, `critique`.
>
> ## Possible direction (not prescriptive)
>
> A useful outcome might be one or both of:
>
> - **Subagent git hygiene:** instruct review/critique subagents to inspect prior
>   versions **read-only** (`git show <ref>:<path>`) and forbid index/worktree-
>   mutating git ops (`git checkout -- <path>`, `git restore`, `git stash`) in the
>   shared tree. Could live in the critique skill's subagent-spawn guidance or the
>   shared `fresh-eye-subagent-review` reference.
> - **Closeout guard:** a check (e.g. in `run_slice_closeout.py`, the #256 surface)
>   that flags an unexpected *staged reversion* of already-committed files (index↔HEAD
>   divergence on files the run did not intend to re-touch) before the closeout commit.
>
> _Found during the #255 achieve run (goal `charness-artifacts/goals/2026-05-30-255-remove-trivial-goal-exemption.md`); surfaced at the closeout commit, after that run's retro._
>

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk (the rest of
  the "Backlog" bundle stays in the handoff memo).
- **Not a perfect detector.** The gate catches the *unambiguous* phantom only:
  `worktree == HEAD` (file looks done/correct) but `index != HEAD` (a staged
  blob present in neither the commit nor the working copy). The mixed case —
  HEAD=v1, worktree=v2 (real new work), index=v0 (base reversion) — is
  **git-state-indistinguishable** from a legitimate partial stage, so the gate
  does **not** block it; that residual is mitigated by the Slice A prevention
  rule, not by the gate. This rung-1/rung-2 split mirrors the #253 disposition
  gate (deterministic floor catches the clear case; prevention/judgment owns the
  rest) and is stated honestly, not papered over.
- Do not make every reviewer-spawning skill verbatim-duplicate the hygiene rule;
  single canonical owner + citation (repo convention).

## Boundaries

- **Slice A (prevention) in scope:** `skills/shared/references/fresh-eye-subagent-review.md`
  is the canonical owner of the new "Shared-Tree Git Hygiene" rule. Reviewer-spawn
  surfaces inherit by citation: `skills/public/critique/SKILL.md`,
  `skills/public/issue/SKILL.md`, plus verify-then-cite-where-missing for
  `spec`, `quality`, `handoff`, `hitl`, and the repo `AGENTS.md` Subagent
  Delegation contract (plan critique flagged the original list as under-counted).
- **Slice B/C (detection) in scope:** a new detector lib + a **blocking
  pre-commit gate** in the `check_staged_mirror_drift.py` gate family (B1: the
  real teeth, because `run_slice_closeout.py` runs at *verify*, before the
  agent's commit and before post-verify critiques), and an **early advisory**
  call wired into `scripts/run_slice_closeout.py` (honors #258's named surface).
- **Detector algorithm (folds B2/B3/B4):** for each path in
  `git diff --cached --name-only`, compare three blob hashes — `HEAD:<path>`,
  `:<path>` (index), and `git hash-object <worktree>` — and flag iff
  `index_blob != head_blob` **and** `worktree_blob == head_blob`. Using blob
  hashes (not `git diff HEAD`, which ignores the index) makes mode-only staged
  changes pass (equal blobs), and the missing-blob branches define A/D/R edges
  explicitly (new-file add with a present worktree → not flagged; deletion
  reverted into the index → handled per the documented verdict). Recovery message
  branches by case so it never tells the operator to re-corrupt the index.
- **Escape:** `--allow-staged-reversion` (closeout, mirrors `--allow-unmatched`)
  and an env-var bypass for the pre-commit gate (mirrors the existing gate
  family), satisfying the operator's "block + ack" decision.
- **Mirror/surfaces obligations (B5):** any edited or new script under `scripts/`
  has FOUR synced copies (`scripts/`, `plugins/charness/scripts/`,
  `mutants/scripts/`, `mutants/plugins/charness/scripts/`); a new module also
  needs `surfaces.yaml` coverage or closeout self-blocks on unmatched. Re-sync
  the plugin mirror after every source edit (recent-lessons trap).
- Portable per implementation-discipline: pure git plumbing, no host-specific
  assumption; the gate-tier naming stays host-plural.
- Stop conditions: name on first discovery; do not guess.

## User Acceptance

The user can verify completion directly by:

- Reproducing the #258 trap in a scratch state — stage a base-reversion of a file
  whose worktree still matches HEAD, then attempt a commit — and seeing the
  pre-commit gate **block** with a clear staged-reversion message + correct
  recovery, instead of silently committing the regression.
- Confirming the documented escape (`--allow-staged-reversion` / env bypass) lets
  an intentional case through.
- Reading `skills/shared/references/fresh-eye-subagent-review.md` and finding the
  explicit shared-tree git-hygiene rule that bounded reviewers must follow.

## Agent Verification Plan

### Low-Cost Checks

- Targeted pytest for the detector lib: phantom (`worktree==HEAD ∧ index≠HEAD`)
  → flagged; legit full stage (`worktree==index≠HEAD`) → pass; mode-only staged
  → pass; new-file add → pass; clean tree → pass; escape flag/env → pass.
- grep-assert the "Shared-Tree Git Hygiene" section + citations are present in
  the shared reference and the high-traffic reviewer-spawn surfaces.
- `check_goal_artifact.py` green.

### High-Confidence Checks

- Full pre-commit gate aggregate green (the new detector joins the
  `check_staged_mirror_drift.py` family); `check_staged_mirror_drift.py` green
  with all four mirror copies synced; `surfaces.yaml` covers any new module so
  closeout does not self-block on unmatched paths.
- `run_slice_closeout.py` self-run green with the new advisory wiring.
- Broad duplicate/length/pressure gate at the bundle boundary (Slice B adds
  tests) — classify any failure as new-slice-local vs accumulated-suite debt.

### External Or Live Proof

- None applicable: a local harness / git-plumbing change with no provider,
  network, or live surface. Explicitly **not run**; no provider/live/release
  proof will be claimed (honest-proof discipline).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Add "Shared-Tree Git Hygiene" rule to `fresh-eye-subagent-review.md` (canonical owner); verify/add citations on reviewer-spawn surfaces (critique, issue, spec, quality, handoff, hitl, AGENTS) | Root-cause prevention; frames B's rationale; cheapest, lowest-risk | New section present; high-traffic spawn surfaces cite it; grep proof; no contradicting prior guidance | planned |
| B | New `staged_reversion` detector lib + **blocking pre-commit gate** (env-var escape) + unit tests + 4 mirror copies + `surfaces.yaml` coverage + pre-commit registration | Durable teeth at the real pre-commit moment (closeout verify runs too early; post-verify critiques can re-introduce the phantom) | unit tests pass (phantom→block, legit stage→pass, mode-only→pass, edge verdicts, escape→pass); mirror-drift gate green; gate registered | planned |
| C | Wire the same detector into `run_slice_closeout.py` as an early **advisory** (first block call, reads git directly) + 4 mirror copies | #258 explicitly names the closeout surface; early warning before the human commit | closeout self-run surfaces the advisory on a seeded phantom; blocking stays owned by the pre-commit gate | planned |

## Slice Log

## Context Sources

- Source: handoff entry #1 (#258: Review subagents can corrupt the parent worktree's git index (silent-regression risk at closeout)) — see [docs/handoff.md](../../docs/handoff.md).
- Cited path: `scripts/run_slice_closeout.py`
- Cited path: `skills/public/critique/SKILL.md`
- Cited path: `skills/public/issue/SKILL.md`
- Cited path: `skills/shared/references/fresh-eye-subagent-review.md`
- Cited issue: #258
- Design precedent — pre-commit gate family the detector should join:
  `scripts/check_staged_mirror_drift.py` (a commit-time index-inspecting hard gate
  for the structurally identical staged-mirror-drift hazard, #257).
- Design precedent — rung-1 deterministic-floor + rung-2 judgment split:
  `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md` (the honest
  "catch the unambiguous case deterministically, name the residual" pattern this
  detector reuses).
- Trap memory: [recent-lessons](../retro/recent-lessons.md) — re-sync the mirror
  after any source edit; doc/blast-radius is undercounted (fix the *concept*
  across surfaces, not just the pointed-at file).
- Origin run that surfaced #258:
  `charness-artifacts/goals/2026-05-30-255-remove-trivial-goal-exemption.md`.

## Interview Decisions

- **Mode (#239):** shape-then-activate. The operator said "어치브 시작" and chose
  the design forks; this Before-phase shapes and saves at `draft`, and the run
  executes only on explicit `/goal` activation. `single-point` — workflow phase
  boundary, not a system axis.
- **Q1 — scope.** Family {both, gate-only, contract-only}; chose **both**
  (defense-in-depth). Rejected: gate-only leaves a prose gap (reviewers still
  corrupt the index, the gate only refuses the commit); contract-only is decaying
  prose with no teeth (capture-and-hope). `single-point` — a design-scope choice,
  not a host/provider axis.
- **Q2 — gate teeth.** Family {block+ack, warn-only}; chose **block + ack
  escape**. Rejected: warn-only repeats capture-and-hope; the silent regression
  already passed all green gates once, so a missable WARN is insufficient.
  `single-point` — closeout/commit gate policy is repo-wide; the escape flag is
  the per-run accommodation; detector is host-agnostic git plumbing.
- **Derived (from plan critique, not asked) — teeth location.** Family
  {closeout-only, pre-commit-primary+closeout-advisory}; chose
  **pre-commit-primary** because `run_slice_closeout.py` runs at *verify*, before
  the agent's commit and before post-verify critique subagents that can
  re-introduce the phantom (B1). Honors decision Q2 (block) at the moment it
  actually bites; still wires the closeout surface #258 named, as advisory.

## Plan Critique Findings

Bounded fresh-eye plan critique ran before save (reviewer provenance:
`parent-delegated` — a bounded Plan reviewer completed the lens directly,
read-only, dogfooding the very git-hygiene rule under review).

**Folded blockers (into Boundaries / Verification / Slice Plan):**

- **B1 — gate ran too early.** Closeout is the `verify` step; the commit (and
  post-verify critiques) come after. Folded: teeth move to a blocking
  **pre-commit gate**; closeout becomes advisory (Slices B + C).
- **B2/B3/B4 — `git diff HEAD` probe ignores the index.** It would both miss the
  mixed-case reversion and, if naively widened, false-positive legitimate partial
  stages — and the mixed case is fundamentally git-state-ambiguous. Folded: scope
  the detector to the **unambiguous** `worktree==HEAD ∧ index≠HEAD` fingerprint via
  three-way **blob-hash** comparison (handles mode-only / new / delete / rename
  edges); record the mixed case as an honest documented limit (Non-Goals) covered
  by Slice A prevention.
- **B5 — mirror blast radius.** Four synced copies, not two; a new module needs
  `surfaces.yaml` coverage or closeout self-blocks. Folded into Boundaries.
- **B6 — ordering/noop.** Place the closeout advisory as the first block call,
  reading git directly (not the deduped `changed_paths` string list). Folded into
  Slice C evidence.
- **Missing scope — citation surfaces under-counted.** Original list named only
  critique + AGENTS; `issue`, `spec`, `quality`, `handoff`, `hitl` reviewer
  surfaces also run in the shared tree. Folded into Slice A.

**Over-worry (raised, not folded):** submodules (none in this repo; skip gitlinks
defensively); extra git-call cost at closeout (negligible vs the gate subprocess
set); the `--allow-*` escape mirroring `--allow-unmatched` (a real, clean
existing pattern — correct to reuse). The reviewer affirmed the "no intent-model
needed" instinct: the blob fingerprint is self-selecting once B2/B3 are fixed.

**Verdict:** reshape-then-sound. Blockers folded above; the two operator
decisions (both / block) are preserved and strengthened.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro

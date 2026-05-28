# Achieve Goal: Reduce achieve/issue/release self-substitution and commit-hook waste (#230 + #229)

Status: draft
Created: 2026-05-28
Activation: `/goal @charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

Eliminate the lighter self-substitution pattern across achieve/issue/release closeouts (#230 Waste 1) and the same pattern's Before-phase anti-anchoring half (#229), quiet the markdown commit/push hook context-flooding (#230 Waste 2), and remove the redundant broad-gate push repetition (#230 Waste 3) so future agent runs cost less time/tokens and produce more honest closeouts.

## Non-Goals

- Not a release: no plugin version bump expected; v0.10.0 real-host proof stays an
  independent track.
- Do not absorb #227 (survey-reliability retro) or #184/#185 (deferred product/AI-ML).
- Do not redesign or weaken the broad pre-push quality gate's correctness
  guarantees; quieting hooks and batching pushes must not suppress real failures.
- Do not file, debug, or close #231 (new mutation regression) inside this goal;
  track only as Off-Goal context.
- Do not modify the `/goal` host runtime; this goal targets repo-owned skill
  contracts, not the host activation entrypoint.

## Boundaries

- In scope: `achieve` lifecycle (Before/After phase prose + helper scripts),
  `critique` skill (potential new angle), `issue` closeout, `release` closeout,
  the markdown lint pre-commit/pre-push hook config, the broad-gate push
  routing/batching policy, and tests under `tests/`.
- Closeout-guard helper must be portable (no host-specific assumption) per
  [implementation-discipline](../../docs/conventions/implementation-discipline.md);
  shared helper lives in a single canonical location and is reused by all three
  skills.
- No `achieve`-only branches in coordinated skills (per the coordination
  guardrail); each coordinated skill must stay useful standalone.
- Stop conditions (active triggerable signals; flip to `blocked` and ask, do
  not guess):
  - **Portability fallback, not full block**: if slice 1's spec doc records the
    shared closeout guard as infeasible across all three surfaces without
    violating standalone usefulness, do NOT flip the goal to `blocked` — instead
    fall back to three standalone guards (slices 3-5 become independent rather
    than blocked) and re-run plan critique on the revised slice plan.
  - If slice 6's markdown hook change removes any failing-file name from stdout
    (verified by running the hook against a known-failing fixture), stop and ask.
  - If slice 7's push-gate router skips the broad gate when the pushed diff
    touches any file under `plugins/`, `.claude-plugin/`, or
    `.agents/plugins/` (any generated export surface), stop and ask — these
    paths unconditionally trigger the full gate regardless of any
    docs/artifact-only classification.
  - If a slice's `--test-pressure` sample reports a duplicate/length figure
    within 0.5 percentage points of the gate threshold, stop and ask before
    adding more tests in that slice.

## User Acceptance

- A future `achieve` After-phase run cannot flip status to `complete` without
  an executed `retro` artifact + host-log probe (or an explicit "skipped because
  X" record); a guard or checklist proves this, not prose alone.
- A future `issue` resolution closeout actually invokes the resolution critique
  sub-skill (or records the explicit skipped-because reason), gated the same way.
- A future `release` closeout actually invokes the standalone critique (or
  records the explicit skipped-because reason), gated the same way.
- `git commit` / `git push` no longer emits the full per-file markdownlint
  enumeration into agent stdout by default; failing files are still named on
  failure, and the lint correctness contract is unchanged.
- A near-identical second push (closeout/bookkeeping-only) does not re-run the
  full ~100-120s broad gate redundantly, while correctness guarantees stay
  intact; the batching policy is documented and gate-tested.
- A new `critique` angle (or `achieve` Before-phase probe) tests whether a
  user-confirmed or issue-inherited value is one of a known system axis
  (host/provider/environment) before locking the design; demonstrable via spec
  example and a test that fails when the probe is removed.

## Agent Verification Plan

### Low-Cost Checks

- Targeted `pytest` of new guard / probe tests for the slice under change.
- Before editing any `SKILL.md`, run `wc -l skills/public/<skill>/SKILL.md` and
  refuse to grow a body that is within 10 lines of the 200-line `MAX_SKILL_MD_LINES`
  budget; route new content into a `references/*.md` file instead (recent-lessons
  repeat trap).
- `validate_skills` after any SKILL.md or skill reference edit.
- `check_doc_links` on any docs edit.
- `ruff` + `mypy` on changed Python.
- For each slice that adds or expands tests: cheap duplicate-pressure sample
  (`--test-pressure` on `append_slice_log.py`) so the broad-gate threshold does
  not surface only at final closeout.

### High-Confidence Checks

- Full pre-push broad gate green at bundle boundaries and at final.
- Mutation gate green on HEAD (scheduled), or a documented changed-surface
  sample-mode run when the slice touches mutation-relevant code.
- Full duplicate/length/pressure gate at final; if it fails, classify as
  new-slice-local vs accumulated-suite debt per After-phase contract.

### External Or Live Proof

- Real-host smoke: trigger the new `achieve` After-phase guard in a small dummy
  goal closeout to confirm it actually blocks an incomplete `complete` flip,
  in at least one host context (Claude Code is the active host this session,
  so default there; record explicitly if Codex coverage was deferred).
- The shared closeout helper's exit code is exercised in tests, but a real-host
  invocation is the honest "did it actually fire under the harness" proof.
- Skipped-proof note: this goal is not a release, so no clean-machine
  Cautilus install/doctor proof is required from this run.

### Critique Cadence

- Plan-level critique (standard tier per shared fresh-eye reference) against
  this artifact before user activates.
- Slice-level critique on slices 1 (spec), 6 (markdown hook — suppression
  risk), 7 (push-gate routing — correctness risk).
- Final critique on the closeout slice.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1. Spec | Carve the shared closeout-guard contract + Before-phase anti-anchoring probe contract across `achieve` / `issue` / `release` / `critique`; resolve cross-cutting trade-offs before code | Cross-cutting design must converge once before three skill surfaces drift | Spec doc under `docs/`, revised Slice Plan, plan critique pass | planned |
| 2. Anti-anchoring probe (#229) | Add Before-phase anti-anchoring probe to `achieve` lifecycle + new `critique` "confirmed-input over-anchoring" angle | Smallest standalone slice; informs how closeout guards record skipped-proof reasons | Lifecycle update, critique angle ref, focused tests | planned |
| 3. achieve After-phase guard (#230 Waste 1a) | Closeout guard preventing `complete` flip without executed retro + host-log probe; integrate with `check_goal_artifact.py` | Highest stated priority half of #230; primary surface | Helper update, guard test, achieve doc edit | planned |
| 4. issue closeout guard (#230 Waste 1b) | Extend shared guard to `issue` resolution closeout — refuse closeout without resolution-critique artifact reference or explicit skip record | Sibling surface per user scope | Issue skill doc edit, shared-helper reuse, test, **documented interaction with existing `issue_tool.py verify-closeout` (no duplication)** | planned |
| 5. release closeout guard (#230 Waste 1c) | Extend shared guard to `release` standalone critique closeout | Sibling surface per user scope | Release skill doc edit, shared-helper reuse, test | planned |
| 6. Markdown hook quieting (#230 Waste 2) | Pre-commit/pre-push markdown hook prints file count + failing files only, not the full 485-path enumeration | Pure recurring context noise; one-shot fix | Hook config edit, demo log diff in slice report | planned |
| 7. Push-gate batching (#230 Waste 3) | Smarter broad-gate routing so docs/artifact-only repushes skip redundant repetition without weakening correctness | User chose full-fix scope; correctness risk demands explicit design + critique | Gate-router change, decision matrix doc, test | planned |
| 8. Closeout | Broad gates, full `retro` invocation, host-log probe metrics, final verification, non-claims, user verification instructions | Final-stage proof per After-phase contract | `check_goal_artifact.py` pass, retro artifact, broad gate green, real-host guard smoke | planned |

## Slice Log

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

## User Verification Instructions

## Auto-Retro

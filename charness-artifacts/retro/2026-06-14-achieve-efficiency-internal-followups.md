# Session Retro: achieve-efficiency internal follow-ups (A2 + floor-addition restraint nudge)

Mode: session

## Context

Goal `charness-artifacts/goals/2026-06-14-achieve-efficiency-internal-followups.md`
shipped two additive, charness-internal refinements to the `achieve` closeout
contract (no floor removed, no blocking gate added):

- **S1 (A2, `e6d1a59a`)** — made `describe_goal_closeout_shape.py` goal-aware via
  `--goal-path`: it reads the in-progress goal and emits only the floors *that*
  goal triggers (and which are missing), folding the dry `check_goal_artifact.py`
  preview into one call. Closes the residual Problem-1 churn the D closeout-floor
  audit named on the runtime-conditional `keep` floors a static catalog cannot.
- **S2 (`c75de40f`)** — gave the prose Floor-Addition Restraint checklist
  non-blocking teeth: `advise_floor_addition_restraint` flags a new blocking floor
  (new `report["ok"] = False` site / new `REQUIRED_*` member) added without a
  recorded restraint call. Resolves `follow-up:floor-addition-restraint-nudge`.

## Evidence Summary

- Two fresh-eye bounded slice critiques (separate agent contexts), one per slice:
  both returned **zero Act-Before-Ship**; S1 folded B1/B2, S2 folded B1/B2.
- Bundle-boundary `run_slice_closeout.py --verification-lock
  --produce-mutation-coverage --base 3abb20d1`: **status completed, 0 failures**,
  broad pytest green (446s), mutation coverage produced.
- 16 new unit tests (6 A2 + 10 nudge) green; `validate_skills`,
  `validate_skill_ergonomics`, `check_doc_links` pass.
- A2 dogfood on this very goal: the `--goal-path` describe surfaced the goal's
  exact conditional missing set (Retro / Host log probe / Disposition review rung
  1b / Routing / Auto-Retro placeholder) and omitted 11 non-triggered floors —
  first-try, no serial rejection.
- Host-log probe (`2026-06-14-...-host-log.md`): thread-wide claude scope,
  127 function calls, 30 patch applications, 2 subagent spawns; not goal-scoped
  (no metric window requested) — proxy activity shape, not a per-goal cost total.

## Waste

1. **`git add -A` swept in off-goal concurrent WIP.** An untracked
   `integrations/tools/pry.json` plus a tracked edit to
   `tests/charness_cli/test_tool_lifecycle.py` — a *separate* pry-integration
   effort's in-flight work — were not present at session start but appeared in the
   worktree mid-run. `git add -A` staged them; the packaging/mirror gate then
   blocked my commit twice before I traced it to the stray files and stashed them
   to isolate a clean closeout. Cost: ~2 blocked commit rounds + investigation.
2. **Mirror/headroom blind spots cost rejected-commit rounds.** (a) S2 edited
   repo-root `scripts/*.py`, which mirror into `plugins/charness/scripts/` — I
   initially treated only skill surfaces as mirrored, so the staged-mirror-drift
   gate rejected the first S2 commit. (b) S1's SKILL.md After-bullet grew the core
   below its headroom buffer, rejecting the first S1 commit until compressed.
   Both gates *worked*; the waste was the extra round, not a gap.
3. **Minor commit-boundary catches:** ruff flagged unused `sys`/`pytest` imports
   in the first S1 test commit. Cheap, caught locally.
4. **Gate-baseline runtime:** the broad pytest ran 446s, over the 120s
   gate-runtime budget — the C advisory fired correctly. This is pre-existing
   slow-by-design suite cost (gate-baseline/code-quality debt), not new debt
   introduced by these slices.

## Critical Decisions

1. **A2 reuses the live `check_complete_evidence` + `check_timebox_closeout`
   reports** rather than re-deriving any floor trigger/satisfy logic — the whole
   point is that the goal-conditional view *cannot drift* from the gate. This was
   the highest-leverage design call.
2. **A2 surfaces the form rungs (1c/1d/1f) only when actively refusing** (read
   from the report's refusal fields), giving an honest, drift-free "missing-line
   set" instead of a re-implemented content trigger.
3. **A2 omits the proof-mismatch + mutable-HEAD floors** (loader-heavy
   `from scripts.` module; not D-audit `keep` floors) — stated as an explicit
   non-claim; `check_goal_artifact.py` stays the authoritative gate.
4. **S2 ships a conservative line-anchored detector**, not AST tokenization: the
   line-anchored `report["ok"] = False` regex and the line-anchored marker both
   removed self-reference traps (own prose counting as a floor; prose paraphrasing
   the marker silencing it). Dogfood confirmed `detect_new_floors` returns `[]` on
   its own changed source.
5. **S2 stays a non-blocking advisory** — a blocking gate here is the exact reflex
   the rule names; recording the call is the intended teeth level. (Dogfooded the
   restraint mindset on the goal's own dispositions.)
6. **Stashed the off-goal pry WIP** rather than committing or deleting it —
   preserved a concurrent effort's work while isolating a clean closeout.

## Expert Counterfactuals

- **Michael Feathers (seams / characterization):** would have predicted the S2
  self-reference trap earlier — a detector that scans source for a pattern its own
  source contains needs a characterization test over *itself* before wiring. The
  line-anchor fix landed via the fresh-eye critique + a deliberate dogfood; doing
  the self-scan up front (it is now a permanent test assumption) would have saved
  the post-hoc fix. Changed action: when a scanner's match pattern can appear in
  its own module, write the "no self-match" assertion in the same commit as the regex.
- **Gary Klein (pre-mortem):** a 30-second pre-mortem on "what in the worktree is
  *not mine*?" before the first `git add -A` would have caught the pry WIP
  immediately instead of via two blocked-commit rounds. Changed action: a clean
  `git status` scan for unexpected untracked/modified paths is a cheap pre-stage
  ritual when a session spans hours in a shared repo.

## Next Improvements

- **workflow — stage explicit paths, not `git add -A`, when untracked/off-goal
  files may be present.** The closeout proof and commit should cover only the
  goal's own changed set; `git add -A` couples in concurrent WIP. (Transferable —
  see Sibling Search.)
- **memory — repo-root `scripts/*.py` mirror into `plugins/charness/scripts/`**,
  not just skill surfaces; sync before the commit gate, not after a rejection.
  (The staged-mirror-drift gate already enforces this deterministically; the
  lesson is to sync proactively.)
- **workflow — the A2 `--goal-path` describe is now the right first closeout
  step**; it surfaced this goal's exact missing set first-try. Use it instead of
  the static catalog + separate dry check going forward (the SKILL.md/lifecycle
  wiring now points there).

## Sibling Search

The `git add -A`-sweeps-off-goal-WIP waste is transferable: any long session in a
shared repo where a concurrent effort leaves untracked/modified files can stage
foreign changes into a "clean" closeout commit.

- Four-axis scan: (skill) no charness skill does a blanket `git add -A` in a
  helper — staging is operator-driven; (script) the closeout/commit helpers stage
  explicit `plugins/`/`.claude-plugin/`/`.agents/plugins/` paths, not `-A`;
  (doc/workflow) no convention forbids `git add -A` at closeout; (gate) the
  staged-mirror-drift + unmatched-path gates *did* catch the symptom downstream.
- decision: **none — first occurrence; restraint applies.** Per the
  Floor-Addition Restraint checklist this very goal shipped, a new closeout guard
  on first sight is the reflex the rule names — prefer the recorded memory lesson
  (stage explicit paths; pre-stage `git status` sanity) and revisit a deterministic
  "untracked off-goal files present at closeout" advisory only if this recurs. The
  existing downstream gates already block the worst outcome (a polluted mirror).

## Persisted

yes — persisted via persist_retro_artifact.py to charness-artifacts/retro/.

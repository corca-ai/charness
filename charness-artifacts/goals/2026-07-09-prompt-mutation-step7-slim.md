# Achieve Goal: Prompt mutation follow-up: parentless blinding, rewrite operator, step-7 slim experiment

Status: active
Created: 2026-07-09
Activation: `/goal @charness-artifacts/goals/2026-07-09-prompt-mutation-step7-slim.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: T3/T4 closeout complete locally; final verification and commit
  are in progress.
- Current slice intent: T3 proved the rewrite/sentinel machinery works but the
  refreshed captures are tainted for the blinding claim; T4 therefore does not
  apply the slim prose.
- Next action: run sync/verification, commit the negative experiment report and
  policy update, and keep the duplicate-pressure hard-block signal in view for
  final broad closeout.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof
  at closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Extend the prompt-mutation pipeline from section-deletion to **sub-section
rewrite** mutation, harden the blinding that the pilot proved insufficient,
and run the first precisely-motivated rewrite experiment: slim handoff
Workflow step 7's verbatim re-spelling of the refresh tokens down to a
pointer at `## Closeout Vocabulary` (the convention-mandated token home per
create-skill's Closeout Vocabulary Rule), and prove the slim variant holds
both the deterministic floors and the baton-pass output quality.

1. **T1 — #426 blinding fix.** All experiment arms (baseline included) run
   from **symmetric parentless snapshot commits** (`git commit-tree` with no
   parent): every arm's worktree has a single root commit of identical shape
   and no diffable *history* — removing the parent-diff channel 4/6 pilot
   mutant runs used. Residual shared-refs channels are enumerated in
   Boundaries (red-team-the-observer floor) and mitigated structurally: raw
   snapshot SHAs are passed as arm refs and **no `refs/prompt-mutants/*`
   refs exist while captures run**; the post-hoc transcript sweep covers
   what remains (e.g. `git diff main`). T1 produces the **close-ready**
   commit for #426 (`Close #426` body + `issue_tool.py
   validate-closeout-draft` in-goal); live CLOSED-state verification needs
   the commit on origin/main, which this goal's no-push boundary forbids —
   it is queued as an operator post-push step, not claimed in-goal
   (plan-critique B1).
2. **T2 — rewrite operator.** `generate_prompt_mutants.py` gains a
   replace-unit mode (unit content substituted with provided text) alongside
   removal, same plumbing/blinding/manifest contract.
3. **T3 — step-7-slim experiment.** One hand-authored rewrite mutant (step
   7's token re-spelling replaced by a pointer to `## Closeout Vocabulary`;
   the rest of step 7 untouched) vs baseline, refresh scenario, N=2 each.
   The slim text is **frozen and fresh-eye critiqued BEFORE captures**
   (public-skill prose risk boundary), so the tree that runs is the tree
   that would ship (plan-critique F3). Detection channels: the pilot's
   deterministic witnesses must ALL fire in every run of BOTH arms — the
   scorer's per-unit witness scoping cannot see this, so T2 adds a
   **sentinel-witness mechanism** (non-causal canary checks evaluated for
   all arms: RSF tokens, RCF spill-targets.md, planner trace marker;
   distinct from causal witness-map entries — plan-critique F2) — **plus a
   new blinded output-quality comparison**: a bounded subagent judge
   receives per-run produced `docs/handoff.md` + closing summary as
   randomized **pairwise A/B per run index** (arm identity hidden;
   pre-registered decision rule in Boundaries). Post-hoc transcript sweep
   for unblinding probes is part of the evidence.
4. **T4 — conditional application.** If T3 is green (all sentinel witnesses
   fire in all runs of both arms AND the pre-registered judge rule finds no
   material regression), apply the **frozen** slim text to
   `skills/public/handoff/SKILL.md` + plugin mirror as a normal reviewed
   commit. **The T3 mutant run is itself the ship-configuration proof**
   only while the applied text is byte-identical to the captured mutant
   and the handoff surfaces are still f84eb223-identical — both re-checked
   at apply time; any wording change demanded by review triggers a capture
   re-run from headroom, never a silent divergence (plan-critique F3).
   Any-red → no edit; record the finding and stop. Green path also updates
   `docs/prompt-mutation-policy.md` to model the rewrite operator class
   (what evidence ships a rewrite, ratchet accounting) so the governing
   surface does not go stale (plan-critique F7). This is the pipeline's
   first shipped prose change and stays within the ratchet (1 change ≤ k=2).

Success = a close-ready #426 fix with capture-provable symmetric blinding
(live close queued post-push), the rewrite operator + sentinel mechanism
tested, one clean experiment with the new judge channel, and either an
applied one-commit slim (evidence-green path) or an honest negative report
(any-red path).

## Non-Goals

- No deletion of any prompt prose; T4 is a rewrite that preserves the
  step-7 instruction and the `## Closeout Vocabulary` section (the
  convention home) — the demotion proposal from the pilot stays rejected.
- No cautilus judge spend: the new quality channel is a bounded subagent
  comparison (repo standing delegation), not `cautilus evaluate`; the
  cautilus contract is untouched.
- No new scenarios, skills, or granularity sweep — exactly one hand-authored
  rewrite mutant on one scenario.
- No release/version bump; if T4 applies, the release rides the operator's
  normal release cadence.
- #427 (mention-vs-execution scorer scope) is NOT fixed here unless T3
  scoring is blocked by it — trace markers score from trace-digest which was
  sufficient in the pilot.

## Boundaries

- External side-effect scope: **#426 close-ready commit only** (`Close #426`
  body per the direct-commit carrier + `issue_tool.py
  validate-closeout-draft` in-goal). A GitHub close keyword fires only when
  the commit reaches the default branch on the remote, so the live
  `--expect-state CLOSED` verification is **queued as an operator post-push
  step** (Operator Decision Queue), never claimed in-goal (plan-critique
  B1); no improvised `gh issue close` manual fallback. No push, no release,
  no other issue closes. Commits stay local; the operator pushes.
- Live capture spend: **≤ 8 captures** (planned 4: parentless baseline N=2 +
  slim mutant N=2; headroom 4 for flakes/a critique-forced re-run). Same
  1200s timeout, failures consume budget, N=1 arms INVALID-FOR-VERDICT.
- Blinded subagent judge — **pre-registered decision rule (plan-critique
  F5)**: comparison is pairwise A/B per run index (never pooled ranking of
  all 4 packets — pooled invites clustering runs into arms via shared
  snapshot-SHA/style artifacts); the judge scores each packet against the
  handoff contract, not free-form preference; **material regression = the
  judge prefers baseline in BOTH pairings with a stated contract-anchored
  reason**; a split or ties = no material regression, recorded as advisory
  noise. Arm identity hidden; the packet-builder test also covers grouping
  leaks (shared SHAs, dates, paths). Advisory quality evidence, never a
  deterministic-witness substitute.
- Snapshot tree definition (plan-critique F6): the **wholesale `f84eb223`
  tree** for both arms (mutant = that tree + the frozen slim edit) — never
  a hybrid with current main, which would re-import the experiment
  blueprint (witness map, goal artifacts, policy doc, pilot report). The
  capture chain needs only `plugins/charness/**`, `docs/handoff.md`, and
  normal repo shape in the worktree; specs, witness map, and tooling are
  read from the main checkout. T1/T2 must not touch
  `skills/public/handoff/**` or `plugins/charness/skills/handoff/**`, and
  T4 re-verifies the surfaces are still f84eb223-identical before apply.
- Residual observation channels (enumerated per the red-team floor,
  plan-critique F4): the worktree shares the main repo's ref store, so
  `git diff main HEAD -- <skill path>`, `git log --all` (pilot commit
  subjects on main name "prompt-mutation"), and cross-arm ref diffs remain
  possible. Mitigations: no `refs/prompt-mutants/*` refs exist during
  captures (raw SHAs as arm refs; manifest holds the SHAs), and the
  post-hoc transcript sweep marks any run that probed these channels as
  tainted evidence.
- Mutant construction: plumbing only, neutral messages, digest-only refs,
  baseline committer date (pilot floors), plus parentless (T1). Refs cleaned
  post-experiment; SHAs in the manifest.
- The T4 edit touches public skill prose: it requires its own fresh-eye
  critique (public-skill risk boundary) before commit, and the
  `## Closeout Vocabulary` section is NOT edited.
- Coding slices in lower-power-model subagents; main loop authors the slim
  step-7 text (judgment content) and the judge packet design.

## User Acceptance

- Read the experiment report
  `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-experiment.md`:
  per-witness + sentinel fire table for both arms, blinded judge verdicts
  with the unblinded mapping revealed only in the report, transcript-sweep
  result for unblinding probes, and the applied/not-applied outcome with
  reason.
- #426 has a close-ready T1 commit (validate-closeout-draft evidence in the
  goal) and a test proving mutant AND baseline snapshot commits are
  parentless with identical commit-shape metadata; the live CLOSED state
  lands when the operator pushes (queued decision).
- If applied: `git show` of the T4 commit is exactly the step-7 slim (a few
  lines in two mirrored files), with `## Closeout Vocabulary` untouched.

## Agent Verification Plan

### Low-Cost Checks

- T1 tests: snapshot commits have zero parents; baseline and mutant snapshot
  metadata (author/committer/date/message) byte-identical; `git log`/`show`
  inside a fixture worktree reveals no diffable history or unit identity.
- T2 tests: replace-unit mode round-trip (unit content substituted exactly,
  rest of file byte-identical), manifest records operator kind
  (removal/rewrite) + content hash of the replacement, plumbing/no-shared-
  state invariants inherited from the pilot tests.
- Judge-packet builder test: arm identity absent from the packet content
  (no arm names, refs, SHAs, or paths that encode them).
- `run_slice_closeout.py --skip-broad-pytest` at slice boundaries.

### High-Confidence Checks

- T3 experiment itself (4 captures) with baseline-validity refusal active.
- Post-hoc transcript sweep: any `git log`/`show`/`for-each-ref`/`reflog`
  probe in any arm's transcript is reported; a probe that could reveal arm
  identity marks that run's evidence as tainted in the report.
- Full broad gate + verification lock at closeout.

### External Or Live Proof

- #426 closeout verification through the issue tool (external write:
  approved above). No other external claims. Non-claims: results hold for
  the refresh scenario on this host; the blinded judge is advisory
  small-N evidence, not a general quality proof.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| T1 | Parentless symmetric snapshot blinding in generate_prompt_mutants + capture config path; close #426 | Pilot proved the diff channel is the dominant leak; rewrite diffs read even better than deletion diffs | pytest green (parentless + shape-identity tests); issue_tool closeout draft/verify for #426; low test pressure (extends existing test file) | complete |
| T2 | Replace-unit rewrite operator + manifest operator kind + **sentinel-witness scoring** (all-arm canary checks, distinct from causal witnesses) | T3's mutant is a rewrite, and its green condition is unscoreable without sentinels (F2) | pytest green (round-trip, manifest, sentinel evaluation incl. a sentinel-fails fixture); low test pressure | complete |
| T3 | Freeze + pre-critique the slim text, then the experiment: 4 captures, sentinel witnesses + blinded pairwise judge + unblinding transcript sweep | The precisely-motivated compaction the pilot surfaced but could not test at section granularity; pre-critique keeps the captured tree shippable (F3) | frozen-text critique verdict; scorer + sentinel tables; judge verdicts under the pre-registered rule; sweep result; ≤8 budget | complete — scorer/judge passed, sweep tainted all runs |
| T4 | Conditional application of the frozen slim (green path, byte-identity + f84eb223-identity re-checked) or honest negative report (red path); policy-doc rewrite-class update | The experiment doubles as the ship-config proof only under byte-identity; the governing policy surface must model the new operator class (F7) | Applied: reviewed 2-file commit + equality check + policy update; Not applied: report section naming the failed channel | complete — no edit; policy updated for T1/T2 operator semantics |

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
- Routing: find-skills -> impl + issue — task-text recommendation matched
  `issue` because T1 resolves #426; interpretation check routed code mutation
  through `impl` and keeps `issue` for source-of-truth read plus close-ready
  carrier proof.
- **Gather step** — when `## Context Sources` names an external source, add a
  `Gather:` line here, or write `Gather: n/a — <reason>`.
- **Release step** — when this run touches a release surface, add a `Release:`
  line, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier,
  and `issue_tool.py validate-closeout-draft` / `verify-closeout` proof.

Routing step line form (record on ONE physical line):

- `Routing: find-skills -> <skill> — <why this phase needs it>`
- Gather: n/a — no external source links were introduced during execution.
- Release: n/a — no release/version surface changed.
- Issue closeout: #426 close-ready carrier only; `validate-closeout-draft`
  passed in T1, live close remains queued for the operator after push.

## Discuss Before Activation

- Discuss before activation: resolved — **first shipped prose mutation
  (T4)**: the operator reviewed the full decision packet in-session
  (closeout-vocabulary section verbatim, step-7 duplication, pilot
  survival evidence, the create-skill Closeout Vocabulary Rule), rejected
  the section demotion, and explicitly asked for this step-7-slim follow-up
  goal ("네 후속 goal 잡아주세요") knowing T4 applies a public-skill prose
  edit on green evidence. The edit is a reversible local commit gated by
  T3 evidence plus its own fresh-eye critique; any-red means no edit.
- Discuss before activation: resolved — **issue close (#426)**: the T1
  deliverable is a close-ready direct-commit-carrier commit with
  validate-closeout-draft proof; the live CLOSED verification requires the
  push the operator owns, so it is queued rather than claimed (plan-critique
  B1 fold); no manual `gh issue close` fallback, no other issue closes.
- Discuss before activation: resolved — **capture spend**: ≤ 8 real
  captures on this machine, same bound semantics as the pilot (operator's
  standing in-conversation approval; overage re-asks).
- Discuss before activation: resolved — **judge channel**: bounded blinded
  subagent comparison (repo standing subagent delegation), explicitly not
  cautilus; advisory evidence only.

## Slice Log

### Slice 1: T1 parentless snapshot blinding

- Objective: Remove the parent-diff unblinding channel for prompt-mutation captures and make #426 close-ready.
- Why this approach: The pilot observed 4/6 mutant runs reading the removed prose through parented snapshot diffs; fixing the generator producer boundary is the smallest prevention surface.
- Commits: this T1 commit; #426 carrier draft validated ready_to_commit_push before commit
- What changed: scripts/prompt_mutant_lib.py and generate_prompt_mutants.py now emit parentless baseline_snapshot_sha + per-unit mutant_sha and no normal mutant_ref; scorer doc/fixture and plugin mirrors synced; critique artifact added.
- Alternatives rejected: Rejected keeping live refs as capture handles; rejected rewriting completed pilot artifacts because they are historical evidence, not the new contract.
- Targeted verification: PASS python3 -m ruff check scripts/prompt_mutant_lib.py scripts/generate_prompt_mutants.py scripts/score_prompt_mutation_survival.py tests/test_generate_prompt_mutants.py tests/test_score_prompt_mutation_survival.py; PASS python3 -m pytest -q tests/test_generate_prompt_mutants.py tests/test_score_prompt_mutation_survival.py (44 passed); PASS real handoff generate probe at f84eb223: 35 units, parentless baseline/mutant SHAs, no refs; PASS issue_tool.py validate-closeout-draft for #426 direct-commit carrier; PASS run_slice_closeout.py --skip-broad-pytest.
- Test duplication pressure: check_dup_ratchet.py --json hard-block vs origin/main: 6 new code families, 0 doc families; classified as accumulated local prompt-mutation-tool debt across the ahead-of-origin bundle, to resolve/classify before final broad closeout.
- Critique: Causal review parent-delegated; code critique artifact charness-artifacts/critique/2026-07-09-t1-parentless-prompt-mutant-snapshot-fix.md; counterweight: no remaining Act Before Ship.
- Off-goal findings: none
- Lessons carried forward: Keep baseline_sha as provenance only; baseline_snapshot_sha is the capture-facing baseline. Do not use refs/prompt-mutants during captures.
- Metrics: subagent coding worker + causal/code critique reviewers used; live capture spend 0/8.

### Slice 2: T2 rewrite operator and sentinel scoring

- Objective: Add replace-unit mutation and all-arm sentinel witnesses for the T3 rewrite experiment.
- Why this approach: Step-7 slim is a rewrite, not a deletion; its green condition requires non-causal canaries to fire in both baseline and mutant arms, which per-unit causal witnesses cannot express.
- Commits: this T2 commit.
- What changed: generator CLI/API supports `--replacement-text`; manifest unit records include `operator_kind` plus applied replacement hash for rewrites; generator emits top-level `sentinels` from repeatable `--sentinel`; scorer validates and reports sentinels, returns nonzero on sentinel failure, and preserves in-band invalid reports for missing bundles; rewrite splicing and sentinel scoring were split into cohesive helper modules; plugin script exports synced.
- Alternatives rejected: Rejected hand-editing sentinels into manifests because that would make T3's proof non-reproducible; rejected substring public-sibling rewrites because duplicated prose can select the wrong section; rejected treating sentinel failures as green CLI exits.
- Targeted verification: PASS `python3 -m ruff check scripts/prompt_mutant_rewrite_lib.py scripts/prompt_mutant_lib.py scripts/generate_prompt_mutants.py scripts/score_prompt_mutation_sentinel_lib.py scripts/score_prompt_mutation_survival_lib.py scripts/score_prompt_mutation_survival.py tests/test_generate_prompt_mutants.py tests/test_score_prompt_mutation_survival.py`; PASS `python3 -m pytest -q tests/test_generate_prompt_mutants.py tests/test_score_prompt_mutation_survival.py` (58 passed); PASS real handoff rewrite+sentinel generate probe at f84eb223: 35 units, top-level sentinels, rewrite operator hash, parentless baseline/mutant SHAs, no refs; PASS `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`.
- Critique: Fresh-eye reviewers found sentinel missing-bundle hard-raise, producer reachability gap, zero-run vacuous success, trace-marker caveat loss, newline-free rewrite boundary risk, ambiguous public duplicate risk, and green sentinel-failure CLI exit; all were fixed. Critique artifact: `charness-artifacts/critique/2026-07-09-t2-rewrite-sentinel-operator.md`.
- Test duplication pressure: check_dup_ratchet.py --json hard-block vs origin/main: 8 new code families, 0 doc families; classified as accumulated local prompt-mutation-tool debt across the ahead-of-origin bundle, to resolve/classify before final broad closeout.
- Off-goal findings: `docs/prompt-mutation-policy.md` still needs rewrite/sentinel operator semantics; deferred to T4 as already scoped because the policy should describe the applied/not-applied outcome after the experiment.
- Lessons carried forward: T3 manifests must be generated with producer-backed `--sentinel` entries; sentinel failures are closeout-red even when causal unit verdicts remain valid.
- Metrics: one coding worker and three fresh-eye reviewers used (one lower-power reviewer spawn hit model capacity and was replaced); live capture spend 0/8.

### Slice 3: T3 frozen text and refreshed step-7-slim experiment

- Objective: Generate the frozen step-7 slim rewrite mutant, run the refresh
  scenario N=2 per arm, score deterministic witnesses/sentinels, judge output
  quality blind, and sweep for unblinding probes.
- Why this approach: The pilot identified a precise duplication candidate; T3
  tests that exact rewrite without changing the shipping skill first.
- Commits: this T3/T4 closeout commit.
- What changed: frozen replacement artifact, generated rewrite manifest, AB
  config, refreshed capture bundles, survival report, blinded judge packets,
  judge results, unblinding sweep, experiment report, and frozen-text critique
  artifact.
- Alternatives rejected: The first four captures used the default chunked
  scenario and were discarded after fresh-eye review because they did not
  preserve the produced `docs/handoff.md`; the final proof attempt used
  `refresh.spec.json`.
- Targeted verification: PASS scorer returned `experiment_valid: true`; PASS
  baseline fragments `Refresh kept:` and `Refresh non-claims:` fired in both
  baseline runs; PASS all sentinels (`Refresh kept:`,
  `Refresh non-claims:`, `spill-targets.md`, planner trace marker) fired in
  every baseline and slim run; PASS blinded judge rule found no material
  regression after unblinding (split: one slim preference, one baseline
  preference).
- Taint result: FAIL clean-blinding proof. The transcript sweep found
  executed git history/ref probes in every refreshed capture, including direct
  slim snapshot probes in slim runs; all four runs are tainted for the
  blinding claim.
- Critique: Frozen-text critique parent-delegated; T4 taint adjudicator
  returned `BLOCK`, so the slim prose is not applied. Artifacts:
  `charness-artifacts/critique/2026-07-09-t3-step7-slim-frozen-text.md`,
  `charness-artifacts/critique/2026-07-09-t4-step7-slim-no-apply.md`.
- Test duplication pressure: still a final broad-closeout concern from the
  accumulated ahead-of-origin bundle; not resolved by T3/T4.
- Off-goal findings: Parentless snapshots remove the parent diff, but the
  refresh task's legitimate git-history behavior still exposes enough
  identity surface to taint output captures; future clean proof needs a
  stronger blind workspace or task-level probe controls.
- Lessons carried forward: The scorer/sentinel channel can pass while the
  experiment still fails as a ship proof; the sweep is a first-class gate, not
  report-only decoration.
- Metrics: live capture spend 8/8 used; 4 discarded chunked captures plus 4
  refreshed captures.

### Slice 4: T4 no-apply closeout and policy update

- Objective: Apply the frozen slim prose only if T3 was clean; otherwise record
  an honest negative report and keep the governing policy current for the
  T1/T2 pipeline changes.
- Why this approach: The goal's green path requires clean capture evidence; the
  taint sweep made the slim change non-shippable even though the deterministic
  and judge channels passed.
- Commits: this T3/T4 closeout commit.
- What changed: `plugins/charness/skills/handoff/SKILL.md` and
  `skills/public/handoff/SKILL.md` remain at the original step-7 wording;
  `docs/prompt-mutation-policy.md` now documents rewrite operator byte
  identity, parentless capture snapshots, and sentinel-vs-invalid outcomes.
- Alternatives rejected: Rejected shipping the slim prose with only a caveat;
  fresh-eye adjudication found that T4 does not apply when all captures are
  tainted for blinding.
- Targeted verification: PASS handoff mirrors have no diff after backing out
  the slim prose; final sync/verification recorded below.
- Critique: T4 no-apply critique artifact records the `BLOCK` decision.
- Metrics: one bounded taint adjudicator used; live capture spend remains 8/8.

## Context Sources

- Pilot goal + report (read first):
  `charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md`,
  `charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md`
  — verdicts, unblinding disclosure, and the mutual-redundancy finding this
  goal acts on.
- `docs/prompt-mutation-policy.md` — verdict semantics, ship-config rerun,
  ratchet, red-team-the-observer floor (T1 implements its blinding
  direction).
- Issue #426 (to close in T1), #427 (context only; recurs #415).
- `skills/public/create-skill/references/portable-authoring.md` — the
  Closeout Vocabulary Rule that rejected the demotion and shapes the slim
  edit (tokens stay in core; step 7 points at them).
- This session's operator decision (2026-07-09): demotion rejected,
  step-7-slim follow-up requested.
- Pilot tooling: `scripts/prompt_mutant_lib.py`,
  `scripts/generate_prompt_mutants.py`,
  `scripts/score_prompt_mutation_survival.py`,
  `evals/cautilus/handoff-claim-fidelity/witness-map.json`.

## Interview Decisions

- Mode — implementation-continuation on activation (the operator asked to
  formalize the follow-up; execution starts only at `/goal` per the
  Before-phase contract). single-point: operator instruction this session.
- Mutation operator — family: deletion-only / rewrite / paraphrase-sweep;
  chosen: **hand-authored rewrite** for one unit (T2 operator + T3
  experiment). Rejected paraphrase sweeps (generative fan-out, unbounded
  cost) and deletion (the compaction target is a re-spelling inside a
  load-bearing step). axis: operator-kind is a manifest field so future
  operators extend, not fork, the schema.
- Quality channel — family: cautilus judge / bounded subagent blinded
  comparison / output-diff heuristics; chosen: **blinded subagent
  comparison** (respects the cautilus ask-before-run contract, adds the
  judgment dimension deterministic floors miss; randomized A/B hides arm
  identity). Rejected raw output-diff heuristics as too brittle for prose
  quality. axis: detection-channel, already a witness-map schema axis.
- Blinding — family: keep parented mutants + disclose / parentless
  symmetric snapshots / separate blind repos; chosen: **parentless
  symmetric snapshots for all arms** (#426 direction; cheapest change that
  removes the diffable-history channel while keeping ref-armed capture
  reuse). Rejected separate blind repos (breaks worktree/plugin resolution
  machinery). single-point until a counterexample: if a run can still
  reconstruct identity another way, the transcript sweep catches it.
- Baseline content — pinned to the pilot's `f84eb223` handoff surfaces
  (blueprint decontamination), re-verified at T3 time. axis: baseline-ref
  is a config field per experiment.

## Plan Critique Findings

Bounded fresh-eye plan critique executed 2026-07-09 (delegated read-only
subagent `ac58bcc981c6c7d94`). Verdict: ACTIVATE-AFTER-FIXES; all folds
applied before this draft was reported ready:

- **B1 BLOCKER (folded → Goal T1, Boundaries, User Acceptance, Discuss):**
  a `Close #426` keyword fires only when the commit reaches the remote
  default branch; under the no-push boundary an in-goal "closed" claim is
  unsatisfiable, and `issue_tool.py verify-closeout --expect-state CLOSED`
  would fail. T1 is now scoped to a close-ready commit +
  validate-closeout-draft; live verification queued post-push.
- **F2 (folded → Goal T3, T2/T3 slice rows):** the survival scorer
  evaluates only the mutated unit's witnesses, so "ALL pilot witnesses must
  fire" had no mechanism; T2 adds sentinel (all-arm canary) scoring,
  deliberately distinct from causal witness-map entries.
- **F3 (folded → Goal T3/T4, Boundaries, slice rows):** a post-capture
  prose critique could change the slim text and void the
  experiment-as-ship-config proof; the text is frozen and critiqued before
  captures, and T4 is equality-gated with an f84eb223-identity re-check.
- **F4 (folded → Goal T1, Boundaries):** parentless snapshots remove the
  parent-diff channel but not shared-refs channels (`git diff main`,
  `git log --all`, cross-arm ref diffs); enumerated per the red-team floor,
  mitigated by ref-less capture (raw SHAs as arm refs) + the taint sweep.
- **F5 (folded → Boundaries):** the judge gate needed a pre-registered
  decision rule; pairwise per run index, regression = baseline preferred in
  BOTH pairings with contract-anchored reasons, split/ties = advisory noise.
- **F6 (folded → Boundaries):** snapshot tree pinned to the wholesale
  `f84eb223` tree (a hybrid with current main silently re-imports the
  experiment blueprint); capture-chain sufficiency of that tree verified by
  the reviewer against capture-skill-run.sh and the harness.
- **F7 (folded → Goal T4, slice row):** shipping a rewrite while the policy
  doc models only demote/delete leaves the governing surface stale; the
  green path updates the policy's operator classes.
- **Over-worries (raised, not folded):** parentless capture-chain mechanics
  verified safe (no ancestry assumptions in worktree add, base-commit
  recording, or output extractors); witness-map prefix resolution never
  touches the mutant tree; ratchet (1 ≤ k=2) and cautilus non-use clean.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Retro: `charness-artifacts/retro/2026-07-09-session-retro.md`
Host log probe: `charness-artifacts/probe/2026-07-09-prompt-mutation-step7-slim-host-log.json`
Disposition review: `charness-artifacts/retro/2026-07-09-step7-slim-disposition-review.md`

- PASS `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
- PASS `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`
- PASS `python3 scripts/check_doc_authoring_preflight.py --path docs/prompt-mutation-policy.md`
- PASS `python3 scripts/validate_skills.py --repo-root .`
- PASS `python3 scripts/validate_retro_artifact.py --repo-root . --paths charness-artifacts/retro/2026-07-09-session-retro.md`
- PASS `python3 -m json.tool charness-artifacts/probe/2026-07-09-prompt-mutation-step7-slim-host-log.json`
- BLOCK `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`: hard-block, 8 new code families, 0 doc families, accumulated across the ahead-of-origin prompt-mutation bundle.
- Outcome sufficiency check: local slice artifacts, policy update, and negative experiment report are verified and commit-ready; the whole activated goal is not marked complete because the duplicate-ratchet hard block and #426 post-push live close remain open operator/final-bundle work.

## User Verification Instructions

## Auto-Retro

Retro dispositions: `charness-artifacts/retro/2026-07-09-step7-slim-disposition-review.md` PASS — blind-workspace guard and clean-proof preflight are dispositioned as repo-local guards; sweep-as-ship-gate memory is applied.
Structural follow-up: repo-local guard: prompt-mutation blind-workspace guard; repo-local guard: prompt-mutation clean-proof preflight; applied: T3/T4 report + retro record sweep-as-first-class ship gate.

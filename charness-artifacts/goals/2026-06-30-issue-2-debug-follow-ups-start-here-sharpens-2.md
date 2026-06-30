# Achieve Goal: debug follow-ups — land the outcome-assertion pattern + fix the planner mis-fire

Status: active
Created: 2026-06-30
Activation: `/goal @charness-artifacts/goals/2026-06-30-issue-2-debug-follow-ups-start-here-sharpens-2.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: CLOSEOUT — all three legs (a+c+d) executed; recording
  Final Verification + retro before flip to complete.
- Current slice: Slice 3 DONE (live re-capture + judge grade ran). Honest result:
  FLOOR miss (debug stays HYPOTHESIS), SUBSTANCE grade pass_rate 0.8 (the outcome
  set discriminated), planner fix proven live (fresh artifact + Resolution set).
- Next action: fill Final Verification / User Verification / Auto-Retro, run the
  quality gate + retro, then flip status to complete.
- Verification cadence: cheap deterministic checks (validators, pytest) at commit
  boundaries; fresh-eye slice critique at slice boundaries; the live cautilus
  re-capture + outcome grading is the final external proof — operator-gated.
- Slice review packet: before fresh-eye slice critique, hand the reviewer intent,
  changed files + owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and
  `## Auto-Retro`.

Discuss before activation: CONFIRMED — leg (d) is a live cautilus eval with token
spend (ask-before-run per CLAUDE.md). The operator confirmed full a+c+d scope and
that the run pauses at the actual `cautilus evaluate` boundary for an explicit go
(consult `plan_cautilus_proof.py`, invoke via `scripts/run_cautilus_eval.py`,
never bare `cautilus evaluate`). The exact capture params (planted failing
fixture, HEAD ref, timeout) are a runtime confirmation tracked in the Operator
Decision Queue, not an unresolved activation blocker.

## Goal

Land the reusable debug **outcome-assertion** pattern on one worked skill, remove
the `continue-existing-artifact` planner mis-fire that buries the debug required
reads for fresh bugs, then attempt a live re-capture PASS so `debug` moves from
HYPOTHESIS toward PROVEN.

**Source handoff entry #1: debug follow-ups — START HERE (sharpens #2)**

> Author a debug OUTCOME-ASSERTION set (protect the structural intent by
> SUBSTANCE — real Detection Gap / Sibling Search / Prevention content, not
> doc-opening, a weak proxy); fix `continue-existing-artifact` mis-fire for fresh
> bugs; re-capture debug to attempt a PASS. Why first: landing the
> outcome-assertion pattern on one worked skill lets the #2 sweep REUSE it
> per-eval instead of reinventing it skill-by-skill.

The 2026-06-30 capture was a MISS (informative): the run nailed the structural
SUBSTANCE (exemplary Detection Gap + Sibling Search) but skipped its planner-
required `five-steps.md` + `debug-memory.md`, aggravated by the planner
mis-moding to `continue-existing-artifact` (a mature repo always has a current
pointer from a prior, possibly closed, incident). This goal protects the
substance by assertion and fixes the mis-fire, so a competent run can PASS.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not soften the cautilus matcher or planner-ize mechanically to force a PASS
  (a miss is a skill-shape signal). The floor stays `[five-steps.md, debug-memory.md]`.
- Do not encode deterministic assertions keyed on literal phrases from the
  2026-06-30 capture (e.g. "0 vs 14 findings", "~15 sibling scanners"); substance
  assertions stay judge-kind so the set discriminates beyond n=1 (over-fit guard).
- Do not broaden the planner mode-decision ladder beyond the single
  resolved-vs-open guard (operator chose the minimal change; a broader redesign
  was explicitly rejected). Adding a minimal debug-artifact `Resolution:` field to
  MECHANIZE that single guard is within "targeted" — it is not a ladder redesign.
- Do not re-author outcome-assertion sets for other skills speculatively; this
  goal lands the pattern on debug only (the #2 sweep reuses it per-eval).
- Do not absorb adjacent handoff entries (#408, #404, #371) beyond the selected chunk.

## Boundaries

- In scope: `evals/cautilus/debug-claim-fidelity/outcome-assertions.json` (new);
  `skills/public/debug/scripts/plan_debug_run.py` (the mode-decision ladder +
  `_required_reads`/`_next_action` exists-branch); `tests/test_debug_plan.py`
  (extend); any debug-artifact resolved/closed-state signal the fix depends on;
  the live re-capture bundle under `charness-artifacts/cautilus/`.
- Portable per implementation-discipline: no host-specific assumption; the
  planner stays deterministic; the assertion set keys on portable evidence
  (bundle outputs, summary, transcript), not host paths.
- The resolved-state signal for leg (c) — VERIFIED GAP (plan critique): the
  debug-artifact schema carries NO resolved/closed field today (checked
  `scaffold_debug_artifact.py`, `validate_debug_artifact.py`, and the live
  `latest.md` = a long-closed #365 incident still serving as current pointer);
  `Next Step: impl|spec` cannot distinguish resolved from open. So the targeted
  guard needs ONE of: (i) a minimal new artifact field (e.g.
  `Resolution: resolved|open`), with the scaffold + template + validator edits IN
  Slice 2 scope; or (ii) a content-independent signal that already exists (e.g.
  `latest.md` mtime/age vs the incoming bug, or treating the current pointer as
  prior memory once it is itself an archived dated incident). Slice 2 RCA decides
  which; this is still the single resolved-vs-open distinction (the locked
  "targeted" intent), NOT a broader mode-ladder redesign.
- Stop conditions: pause at the `cautilus evaluate` boundary for explicit go;
  stop if `plan_cautilus_proof.py` returns `next_action: none` without a named
  failing-log path; name any new surface on first discovery, do not guess.

## User Acceptance

What the user can do to verify completion directly.

- Open `evals/cautilus/debug-claim-fidelity/outcome-assertions.json` and confirm
  it mirrors the hitl set's shape and that its assertions key on SUBSTANCE — real
  Detection Gap (which gate failed + proof), Sibling Search (mental-model
  abstraction + per-sibling decisions), and Prevention (smallest concrete move) —
  with at most a couple of deterministic sanity floors (ran-debug, wrote-artifact),
  i.e. doc-opening is NOT used as a proxy for the structural intent.
- Run `python3 scripts/validate_outcome_assertions.py` and see the debug set pass.
- Run `python3 -m pytest tests/test_debug_plan.py` and see a test proving a fresh
  bug whose only on-disk artifact is a resolved/closed prior incident routes to a
  fresh-investigation mode (not `continue-existing-artifact`), with `five-steps.md`
  + `debug-memory.md` surfaced unburied at the top of required reads.
- Confirm the SAME test file also proves the genuine OPEN case is preserved: an
  in-progress (unresolved) current artifact still routes to
  `continue-existing-artifact` with its current-artifact read first — so the guard
  flips only the resolved case, not all existing-artifact cases (regression floor).
- Read `## Final Verification` for the live re-capture result: an honest PASS, or a
  MISS recorded as a skill-shape signal — never a softened matcher or a green that
  was not actually produced by a graded run.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/validate_outcome_assertions.py` (new debug set validates).
- `python3 -m pytest tests/test_debug_plan.py` (mode-decision regression test).
- `python3 skills/public/debug/scripts/plan_debug_run.py --repo-root <fixture>`
  JSON diff on a fresh-bug-with-resolved-prior fixture vs the old behavior.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock commit boundaries.

### High-Confidence Checks

- Fresh-eye bounded slice critique on the planner fix (different agent context):
  does the resolved-state guard correctly distinguish open continuation from
  closed prior memory without regressing the genuine continue case?
- Fresh-eye review of the outcome-assertion set for substance-not-proxy: would a
  contaminated or doc-opening-only run legitimately score low?
- `quality` validation recommendation before HITL/manual closeout review.

### External Or Live Proof

- Operator-gated live re-capture: plant a deliberately non-gitignore-aware
  scanner fixture (per the debug spec `_comment`), consult
  `python3 scripts/plan_cautilus_proof.py --repo-root . --json`, run the capture
  via `scripts/capture-skill-run.sh` + `scripts/run_cautilus_eval.py`, then grade
  the outcome-assertion set via `scripts/grade_skill_outcome.py` (deterministic
  offline; judge-kind via `--judge-cmd`, ask-before-run). Record PASS/MISS and the
  graded evidence bundle path honestly.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Author `debug-claim-fidelity/outcome-assertions.json` keyed on SUBSTANCE | Lands the reusable pattern the #2 sweep needs; independent of the planner fix | `validate_outcome_assertions.py` passes; set mirrors hitl shape; judge assertions cover Detection Gap / Sibling Search / Prevention substance | planned |
| 2 | RCA the resolved-vs-open mechanism (no field exists today), then implement the single guard incl. any minimal artifact `Resolution:` field + scaffold/template/validator edits | Removes the fidelity blocker so a competent fresh-bug run surfaces five-steps/debug-memory unburied | debug artifact recording the RCA + chosen mechanism; planner mode flips on a resolved-prior fixture AND still continues an OPEN artifact (both tests green); `tests/test_debug_plan.py` extended; fresh-eye critique | planned |
| 3 | Operator-gated live re-capture + outcome grading | Turns debug HYPOTHESIS → PROVEN (or records an honest MISS) once a+c land | graded bundle under `charness-artifacts/cautilus/`; PASS/MISS recorded in Final Verification | planned (gated) |

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

Open items:

- Decision: approve the live cautilus re-capture (leg d) and its capture params.
  | Owner: operator (bae.hwidong@corca.ai) | Why deferred: legs a+c are fully
  local and provable without it; the live eval spends tokens. | Unblock action:
  explicit "run the re-capture" go, after I surface the planted fixture, HEAD ref,
  and timeout from `plan_cautilus_proof.py`. | Revisit trigger: slices 1+2 proven
  green and committed.
- Decision (checkpoint, not a blocker): a minimal `Resolution:` artifact field is
  pre-approved as within the targeted guard (Slice 2 scope). Stop to confirm ONLY
  if Slice 2 RCA finds the resolved-vs-open guard needs MORE than a single field +
  its scaffold/template/validator edits (i.e. it grows toward the rejected broad
  redesign). | Owner: operator (bae.hwidong@corca.ai) | Why deferred: the
  single-field path is the expected minimal mechanism. | Unblock action: confirm
  whether the larger change is in scope or should be re-scoped to a new goal. |
  Revisit trigger: slice 2 RCA shows the guard cannot be expressed as a single
  distinction.

## Coordination Cues

Phase routing defers to `find-skills` (no inline phase→skill map): query it when
a leg names a capability (debug RCA, quality validation, issue filing, critique).
Closeout floors to satisfy when triggered:

- Routing: recorded phase work routes through `find-skills` (this goal entered via
  the find-skills → handoff chunked-routing pickup).
- Gather: n/a — no external source feeds this goal (the originating context is the
  in-repo debug finding, already cited).
- Release: n/a — no release surface; no plugin version bump (see Non-Goals).
- Issue closeout: n/a — no GitHub issue is in scope (the handoff "#2" is an
  internal Next Session cross-reference, not GitHub issue #2).

## Slice Log

### Slice 1: Author the debug outcome-assertion set

- Objective: Author evals/cautilus/debug-claim-fidelity/outcome-assertions.json keyed on SUBSTANCE (Detection Gap / Sibling Search / Prevention + falsifiable-hypothesis-before-fix as judge-kind) plus minimal deterministic sanity floors (ran-debug, wrote-debug-artifact), mirroring the only prior set (hitl). Leg (a); independent of the Slice 2 planner fix.
- Why this approach: The 2026-06-30 capture nailed the structural SUBSTANCE but missed doc-opening; protecting substance directly (judge-kind) — not doc-opening, which spec.json already scores — is what the finding's disposition called for. Deterministic floors stay minimal and NOT over-fit to that capture's numbers.
- Commits: (this slice's commit)
- What changed: NEW evals/cautilus/debug-claim-fidelity/outcome-assertions.json (6 assertions: 2 deterministic + 4 judge).
- Alternatives rejected: Rejected a doc-opening 'missing required fragment' negate assertion (the hitl pattern) as a substance proxy — the finding proved doc-opening is a weak proxy here; the spec.json floor already scores it.
- Targeted verification: validate_outcome_assertions.py OK (2 sets). No-spend deterministic dry-grade vs the prior bundle: ran-debug PASS (summary 'Execution of /debug'), wrote-debug-artifact FAIL-honest ('no outputs/ dir' = not preserved, not unwritten), 4 judge SKIPPED (no --judge-cmd, ask-before-run respected), grader self-test PASSED.
- Test duplication pressure:
- Critique:
- Off-goal findings: Slice 3 dependency surfaced: substance judging reads the debug artifact via the bundle PRODUCED OUTPUTS excerpt, so the live re-capture must preserve it (--keep-untracked-outputs) or judge rows can't see the substance.
- Lessons carried forward:
- Metrics:

### Slice 2: Targeted resolved-state planner guard

- Objective: Fix the continue-existing-artifact mis-fire (leg c): a current-pointer artifact from a closed prior incident forced continue-existing-artifact, burying five-steps/debug-memory for a fresh bug. Add a Resolution: open|resolved lifecycle field; planner continues only when resolution != resolved.
- Why this approach: RCA confirmed no resolved/closed signal existed in the schema (only Next Step: impl|spec, which cannot distinguish). Chose missing->open (smallest behavior change: legacy/in-progress keep continuing; only explicit resolved flips) + scaffold writes open + closeout sets resolved + one-time migrate the live latest.md (#365, concluded). Rejected missing->resolved (larger behavior change, breaks fieldless resume).
- Commits: (this slice's commit)
- What changed: plan_debug_run.py (_artifact_summary resolution parse; mode ladder; _required_reads exists-branch surfaces resolved pointer as prior memory; _next_action); scaffold_debug_artifact.py (template emits Resolution: open); validate_debug_artifact.py (OPTIONAL Resolution enum, case-folded for planner parity); SKILL.md (closeout sets Resolution: resolved); migrated charness-artifacts/debug/2026-06-14-issue-365...md to resolved; tests/test_debug_plan.py (+3 tests); synced plugins/charness mirror (4 files, byte-identical).
- Alternatives rejected:
- Targeted verification: pytest debug suite green (plan+artifact+scaffold); validate_debug_artifact OK over all 20 live artifacts; live planner now routes the migrated #365 pointer to fresh-investigation-with-prior-memory (was continue). Fresh-eye slice critique (separate agent): SAFE TO COMMIT, no blockers, mirror byte-identical, both directions tested; folded its 2 over-worries (validator case-parity + a fail-safe test).
- Test duplication pressure: tests/test_debug_plan.py +3 small fixtures (explicit-open, resolved-flips, unknown-value fail-safe); no duplication vs existing suite — each asserts a distinct mode/resolution branch the old suite did not cover.
- Critique: Fresh-eye bounded reviewer verdict: safe to commit as-is. Public-skill validation: the debug DOGFOOD consumer contract (routes to debug, names latest.md, preserves artifact) is UNCHANGED — Resolution is an internal planner-lifecycle refinement, so no docs/public-skill-dogfood.json freeze needed. Scenario decision: resolved-pointer-routes-fresh is now covered by deterministic tests; the live scenario re-capture is Slice 3 (operator-gated), so scenarios.json is not mutated now.
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Live re-capture + judge grade (operator-gated)

- Objective: Leg (d): operator-approved live cautilus re-capture of /charness:debug at HEAD (with the fix), build observed packet, run cautilus evaluate observation, grade the outcome set with the LLM judge. Attempt debug HYPOTHESIS->PROVEN.
- Why this approach: The fix should let a competent run honor the floor reads. Outcome judge tests whether the substance set discriminates a faithful run independent of doc-opening.
- Commits: (this slice's commit)
- What changed: NEW bundle charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/ (justification, observed.v1.json, trace-digest, cautilus-report, outcome-grade, finding, outputs/). FIX grade_skill_outcome.py _output_excerpts per_file 500->8000 +40KB total budget (synced mirror).
- Alternatives rejected:
- Targeted verification: Capture exit 0 (full run, not the cap). FLOOR: cautilus failed/reject, coverage 3/11, still skipped five-steps.md+debug-memory.md. SUBSTANCE (after the excerpt fix): pass_rate 0.8 — detection-gap/sibling-search/prevention PASS, falsifiable-hypothesis FAIL (static-only, no repro/disconfirmer before fix). Planner fix proven live: run scaffolded a FRESH artifact + set Resolution: resolved at closeout.
- Test duplication pressure:
- Critique: Honest MISS on the FLOOR (debug stays HYPOTHESIS; do NOT soften — the mis-fire was aggravating, not causal for the doc-skip). The outcome set is VALIDATED: it discriminated real substance (3 PASS) and caught a real discipline gap (falsifiable FAIL) the floor + prior prose both missed. The first grade false-negatived two substance rows via a 500-char judge excerpt truncation; fixed and re-graded.
- Off-goal findings: FLOOR doc-skip is a debug skill-shape question (run reaches structural outcome via the scaffold without the docs) — out of this goal's scope; candidate follow-up. falsifiable-hypothesis FAIL (static-only RCA) is the most actionable substance signal for a future debug emphasis.
- Lessons carried forward: A 'fixable' mis-fire can be only an aggravating factor — proving the fix changed behavior (fresh artifact, Resolution set) is separate from proving it fixes the downstream symptom (floor reads). Substance grading needs the judge to see the FULL artifact, not its head.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct the
originating context by following them in order.

- Source: handoff entry #1 (debug follow-ups — START HERE) — see [docs/handoff.md](../../docs/handoff.md).
- Note: "#2"/"#3" in the entry are the handoff's own Next Session item numbers
  (correctness sweep / outcome-assertion pattern), not GitHub issues — no GitHub
  issue is in scope for this goal.
- Prior debug capture finding (the MISS this goal addresses): [charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30/finding.md](../cautilus/debug-claim-fidelity-2026-06-30/finding.md).
- Pattern to reuse (the only existing outcome-assertion set): [evals/cautilus/hitl-claim-fidelity/outcome-assertions.json](../../evals/cautilus/hitl-claim-fidelity/outcome-assertions.json).
- Grader + valid check types: [scripts/grade_skill_outcome.py](../../scripts/grade_skill_outcome.py); validator [scripts/validate_outcome_assertions.py](../../scripts/validate_outcome_assertions.py).
- Planner under change: [skills/public/debug/scripts/plan_debug_run.py](../../skills/public/debug/scripts/plan_debug_run.py) (mode ladder lines ~303–310; `_required_reads`/`_next_action` exists-branch); debug eval spec [evals/cautilus/debug-claim-fidelity/spec.json](../../evals/cautilus/debug-claim-fidelity/spec.json).
- Capture/eval contract: CLAUDE.md cautilus eval-only/ask-before-run; [scripts/plan_cautilus_proof.py](../../scripts/plan_cautilus_proof.py), [scripts/run_cautilus_eval.py](../../scripts/run_cautilus_eval.py).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- Scope of the goal (which legs). Options: a only / a+c (recapture gated) /
  a+c+d full. Chosen: **a+c+d (full, incl. live re-capture)**. Rejected: a-only
  (leaves debug a HYPOTHESIS and the mis-fire unfixed); a+c-gated (the operator
  wanted the PASS attempt this run). The live leg pauses at the cautilus boundary
  for an explicit go (recorded in Operator Decision Queue + Discuss-before-activation).
- Aggressiveness of the planner fix (leg c). Options: targeted resolved-state
  guard / broader mode redesign. Chosen: **targeted resolved-state guard**.
  Rejected: broader redesign — larger blast radius on a shipped skill surface and
  higher review cost for no proven need; the miss is explained by the single
  resolved-vs-open distinction.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but not
folded, and reviewer provenance.

Reviewer: fresh-eye bounded plan critique (separate general-purpose agent context,
read-only), 2026-06-30.

Folded (BLOCKERs):

- B1 — No resolved/closed field exists in the debug-artifact schema today
  (verified across scaffold/validator + the live closed-#365 `latest.md`);
  `Next Step: impl|spec` cannot distinguish resolved from open, so the "prefer
  existing field" framing was misleading. Folded: Boundaries now states the
  verified gap and names the two candidate mechanisms; Slice 2 explicitly owns the
  mechanism RCA + any minimal `Resolution:` field + scaffold/template/validator
  edits (not hidden in a conditional queue item); Non-Goals/Interview Decisions
  clarify a single-field mechanism is within "targeted", not a ladder redesign;
  the queue item is downgraded to a checkpoint.
- B2 — The acceptance test only proved the resolved case FLIPS, risking a silent
  regression of the genuine OPEN continuation. Folded: User Acceptance + Slice 2
  evidence now require a companion test proving an OPEN artifact still routes to
  `continue-existing-artifact` with its current-artifact read first.

Raised, not folded as blockers (over-worry / already sound):

- Substance-not-proxy governance is adequate (substance assertions must be
  judge-kind; doc-opening already forbidden) — added a Non-Goals guard against
  over-fitting deterministic assertions to n=1 capture phrases.
- Slice independence + dependency ordering correct (Slice 1 offline-validatable,
  independent of Slice 2; Slice 3 depends on both). Note: Slice 1 judge-kind
  assertions are only GRADED at Slice 3's live judge — honestly scoped already.
- Live-capture acceptance is honest about PASS-vs-MISS; not pre-committed to green.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro

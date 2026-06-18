# Achieve Goal: North-star overhaul: Track 1a (per-unit verdict framing) + Track 2 (slim)

Status: complete
Created: 2026-06-18
Activation: `/goal @charness-artifacts/goals/2026-06-18-north-star-overhaul.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **COMPLETE.** S1–S6 all done; `Status: complete` flipped via the
  `check_goal_artifact` gate. Four slice critiques (S2, S3, S3-reloc, S5) + a
  rung-2 disposition review all PASS; broad pytest **3275 passed, 0 failed**.
- Current disposition: DONE. All Done criteria met — every audited irreversible
  boundary mandates a per-unit behavioral verdict via a distinct channel (issue/PR
  close, release publish, release-linked close, deletion; HOTL + achieve seed
  pre-existing); the standing surface shrank (retro core 160→146 off cap + Cautilus
  always-on text pulled) without losing a safeguard; gate suite green; fresh-eye
  confirmed framing-not-gate; no terminal-green gate added.
- Follow-ups (in `docs/handoff.md` Next Session): the spun-out remaining-13-body
  SRP sweep, the deferred AGENTS.md Skill-Routing collapse (needs a lockstep
  `render_skill_routing.py` change), and any future push (no external side effect
  taken this run).
- Verification cadence: cheap deterministic checks at commit boundaries;
  fresh-eye critique + higher-cost proof at slice-intent boundaries; broad proof
  at the closeout bundle.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Bring the charness harness into line with `docs/design-north-star.md`, using the
**RESOLVED Step 0 finding** that the #386-class failure is driven by task
**FRAMING** (an aggregate-disposition sign-off after all-green + CLOSED suppresses
a fresh reviewer's present proxy-skepticism), and that the lever which flips catch
0.00 → 1.00 is a **per-unit behavioral verdict mandate** at the boundary — *not*
context-load, *not* raw-vs-summary channel, and **not** a new gate.

Two tracks:

- **Track 1a (LIGHT) — generalize the framing.** The #386 fix already lands this
  lever, but scoped narrowly to the achieve issue-bundle disposition review
  (`achieve/references/lifecycle.md` Rung-2). Generalize the *same* per-unit
  behavioral-verdict framing to every other irreversible boundary that still
  rubber-stamps on a proxy (PR **merge**/close, release-linked issue close,
  external state writes, deletions; PR irreversibility triggers at
  merge-to-shared-history, not the tracker flip). This is a framing/task-structure prose change at the
  decision point; it adds **no new gate, no script, no verdict token** (the
  plan-v2 gate/token/PULL-raw-state/load-cap machinery is empirically dead).

- **Track 2 (SLIM) — less standing prose.** PUSH→PULL the always-on surface
  (AGENTS.md / CLAUDE.md → minimal stable entry + skills index; detail pulled on
  demand) and own-concept SRP-compress the overlong skill bodies. Cut
  intrinsic-judgment restatement (agents already have the judgment — the Step 0
  general finding); keep non-intrinsic repo-specific info. Compression = concept
  separation/deletion, never line-shaving to dodge a cap (north-star P2).

Done = every irreversible boundary demands a per-unit behavioral verdict via a
distinct channel (not an aggregate sign-off), the standing prose surface shrinks
measurably without losing a boundary safeguard, the existing gate suite stays
green, a fresh-eye reviewer confirms the change is framing (not a smuggled gate),
and no terminal-green gate was added.

**Design lens (added 2026-06-18 — *capabilities over features*, gathered).** Frame
both tracks as capabilities-over-features, not subtraction: the target is maximum
**orthogonal, composable, learnable-by-use** capability from a minimal surface —
not fewer lines. Track 2's success metric is **learnability/discoverability** (can a
fresh agent find the right capability by invoking it?), not line count. A candidate
north-star addition this overhaul should weigh: an **orthogonality / "one obvious
way" lens** for any new or existing gate/skill — *is this the Nth redundant way to
do X, or is it orthogonal and composable?* (a judgment **lens, not a gate**: a
non-orthogonal answer is a reason to *ask*, not a license to delete) — since
non-orthogonal surface forces "which path?" overhead and wrong choices (the page's
core critique; charness's own overlapping closeout paths are the symptom). The
operator's breaking-change permission is what lets the overhaul *delete*
non-orthogonal surface, not only slim prose — **except** a gate that guards an
irreversible boundary, which is never deleted on non-orthogonality grounds alone
(see Non-Goals and north-star P5). (Source:
`../gather/2026-06-18-capabilities-over-features.md`.)

## Non-Goals

- **No new deterministic gate, validator, or verdict token at any boundary.**
  North-star P5 + the #386 commit's "why no gate": an 8th floor would re-grant a
  terminal green on the agent's own self-classification — the exact
  "all-green + CLOSED = behavior proven" equivalence that caused #386.
- **Not re-running Step 0.** Mechanism is RESOLVED. The single-fixture limit is
  named; an optional 2nd-defect-class hardening is explicitly out of scope here
  (non-blocking).
- **Not reviving plan-v2's Track-1a machinery** (reviewer-PULLs-raw-state,
  doer-can't-author-brief, per-reviewer load caps, ref-token gate) — empirically
  not load-bearing (C3b summary+mandate = 1.00; C3c-heavy ≈ lean).
- **Not closing or coupling #387** (closeout-validator one-pass UX — a separate
  issue the handoff mislabeled as this pilot) **or #371** (browser teardown).
- **Not line-shaving to dodge a length cap** (P2 violation) and **not deleting a
  gate that guards an irreversible boundary and replacing it with nothing**
  (P5 failure signature). Slimming touches reversible prose, never a cliff fence.

## Boundaries

- Prose / skill-surface edits only; reversible session-internal state until
  commit. No code-behavior or runtime surface change expected for Track 1a.
- `mutate → sync → verify → publish` is a hard phase barrier: sync generated /
  `plugins/` mirror surfaces before validators (`check_staged_mirror_drift`).
- Track 2 edits **always-on host instruction surfaces** (AGENTS.md / CLAUDE.md) —
  high blast radius on every future session. Treat as its own fresh-eye critique
  boundary; the reviewer question is "was any boundary safeguard lost or made
  unread?", not "are there fewer lines?".
- External side-effect scope: **none approved at shaping.** No push / publish /
  tag. Any external action (including pushing the pending Step-0 archive commit
  `4da92874`) is a separate operator decision, phase-scoped, not carried forward.

## User Acceptance

What the user can do to verify completion directly:

- Read the **S1 boundary-audit artifact**: each irreversible boundary classified
  *mandates-per-unit-verdict* vs *rubber-stamps-proxy*, with an explicit gap list.
- For each closed gap, read the diff: the boundary's closeout prose now demands a
  **per-unit behavioral verdict through a channel distinct from the proxy**,
  citing north-star P4 — and the bound fresh-eye critique confirms it is framing,
  not a new gate.
- Track 2: read the before/after of the always-on surface (line counts + what
  moved from PUSH to PULL) and the SRP-split skill bodies, plus the critique
  confirming no boundary safeguard was lost.
- Confirm the gate suite is green: `validate_skills`, `check_doc_links`,
  `check-markdown`, length gates, and the closeout/achieve gate suite.

## Agent Verification Plan

### Low-Cost Checks

- `run_slice_closeout.py --skip-broad-pytest` at every commit boundary
  (ruff, length, mirror-drift, `validate_skills`, `check_doc_links`,
  `check-markdown`, attention-state).
- For any `achieve/references/lifecycle.md` or closeout-contract edit, the
  targeted closeout/achieve gate suite (the ~127-test set the #386 fix ran).
- Length-headroom advisory on any changed gated file near its cap (choose a new
  module over appending — directly relevant to Track 2).

### High-Confidence Checks

- Full broad pytest + markdown gate + skill-ergonomics sweep at each bundle
  boundary and at final closeout.
- **Fresh-eye critique per slice-intent boundary** (the substantive proof a gate
  cannot give): Track 1a reviews "is this framing, or a smuggled gate / terminal
  green?" — concretely, **per changed boundary** the reviewer must answer: *does
  the sharpened prose DECLARE a completion condition* (BLOCKER — "all units
  confirmed = close" re-creates the exact #386 terminal-green) *or only MANDATE
  the per-unit question* (pass)? Track 2 reviews "was a boundary safeguard lost or
  pushed into unread overflow?".

### External Or Live Proof

- None required — prose/skill-surface change, no runtime/provider roundtrip.
- **Optional, non-blocking:** behaviorally re-validate a generalized framing fix
  with the Step-0 C3b/C3c subagent harness (authentic Sonnet, in-prompt fixture)
  to confirm the lever still flips at the new boundary. If skipped, name it a
  non-claim ("framing validated by reasoning + reviewer, not re-run behaviorally").

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 — boundary audit | Read-only: classify each irreversible boundary (issue close, PR **merge**/close, release-linked close, external write, deletion — PR trigger = merge-to-shared-history, not the tracker flip) as mandates-per-unit-verdict vs rubber-stamps-proxy; produce the gap list | Grounds Track 1a in evidence; mirrors #386 pilot-first; stops me guessing the gap | audit artifact under `charness-artifacts/critique/` | **done** — `charness-artifacts/critique/2026-06-18-s1-boundary-audit.md` (`c6c0cc56`); models = achieve seed + HOTL; gaps G1 issue/PR close, G2 PR merge, G3 release publish, G4 release-linked close, G5 deletions; worst = G1+G2 |
| S2 — Track 1a pilot | Close the single worst gap from S1 in-place (sharpen closeout framing → per-unit behavioral verdict, cite P4, no gate) + fresh-eye critique (framing-not-gate) | Validate the LIGHT pattern on one real gap before any sweep | diff + bound critique artifact; the critique must answer per boundary: *declares a completion condition (blocker) or only mandates the per-unit question (pass)?* | **done** — closeout-discipline.md new mandate + SKILL.md guardrail + resolve-flow.md pointer; critique `charness-artifacts/critique/2026-06-18-s2-issue-close-framing-critique.md` = PASS (declares-vs-mandates: mandates, all 3 surfaces; safeguard strengthened) |
| S3 — Track 1a sweep | Generalize the validated framing to the remaining real gaps from S1 | Pattern proven by S2; one critique covers the coherent bundle | diffs + critique (same per-boundary declares-vs-mandates check) | **done** — G3 release publish (step-7 P4 per-surface verdict, 3 bullets consolidated), G4 release-linked close (guardrail pointer), G5 deletion (rename-critique Per-Removed-Concept Verdict); critique `charness-artifacts/critique/2026-06-18-s3-sweep-framing-critique.md` = PASS (declares-vs-mandates: mandates all 3; in-place justified; safeguard intact) |
| S4 — Track 2 audit | Measure the always-on surface (AGENTS.md / CLAUDE.md / skill bodies at cap) + own-concept bloat; plan PUSH→PULL + SRP splits | Track 2 is Step-0-independent; needs its own measurement before cutting | audit + plan (decide spin-out — see Operator Decision Queue) | **done** — `charness-artifacts/critique/2026-06-18-s4-track2-audit.md`; AGENTS.md 70L (2 PUSH→PULL targets: Cautilus block, Skill-Routing dup); 14 bodies near 160 core cap; S5 = AGENTS.md PUSH→PULL + retro SRP pilot; recommend spin out the remaining-13-body sweep |
| S5 — Track 2 slim | Execute PUSH→PULL + SRP compression on the highest-bloat surfaces + fresh-eye critique (no safeguard lost) | After 1a lands the framing, the docs should reflect the smaller standing surface | diffs + before/after counts + critique | **done** — AGENTS.md PUSH→PULL 70→58 (Cautilus block → pointer; Skill-Routing dup collapsed) + retro SRP-split core 160→144 (Auto-Retro Trigger + Expert Counterfactual Rule → existing references); critique `charness-artifacts/critique/2026-06-18-s5-track2-slim-critique.md` = PASS (no safeguard lost/unread; P2 concept-separation) |
| S6 — closeout | Broad proof + retro + per-improvement disposition + handoff update | Bundle boundary | gate suite green + retro + bound disposition review | planned |

## Operator Decision Queue

Closeout state: all three queue items below are RESOLVED; no operator action
blocks completion. The only forward-looking operator decisions are the
recommended **spin-out of the remaining-13-body SRP sweep** and the deferred
**AGENTS.md Skill-Routing collapse** (both recorded in `docs/handoff.md` Next
Session), plus any future **push** of the pending local commits (no external
side effect was taken this run).

- Decision: Split **Track 2 (SLIM)** into its own goal? | Owner: operator |
  Status: **SIZED at S4 (2026-06-18) — recommend PARTIAL spin-out.** Keep the
  **AGENTS.md PUSH→PULL + one `retro` SRP pilot** in this goal (S5) — that is the
  contained core Track-2 deliverable satisfying the goal's "standing surface
  shrinks measurably" Done criterion. **Spin out the remaining-13-capped-body SRP
  sweep** as its own follow-up goal: it is a high-volume, mechanical, repeatable
  program where each body is prompt-affecting (own dogfood review) — a clean
  spin-out shape, not safe to rush in one session. Operator-overturnable. |
  Revisit trigger: S5 closeout, or an explicit operator instruction.
- Decision: File a tracking GitHub **issue** for this overhaul? | Owner: operator
  | Status: **RESOLVED 2026-06-18 — skip** (operator approved); the overhaul is
  tracked by this goal artifact | Revisit trigger: if scope outgrows one goal.
- Decision: Push pending local commits **`4da92874` / `8a92985f`** to
  `origin/main`? | Owner: operator | Status: **RESOLVED 2026-06-18 — not in
  scope** (operator approved "no external side effects"); a push needs a separate
  explicit instruction | Revisit trigger: the next explicit push request.

## Discuss before activation

Discuss before activation: RESOLVED 2026-06-18 — operator approved all four
defaults ("모두 승인"): (1) Track-1a **in-place** method (no new shared
reference), (2) Track-2 **bundled** for now (revisit spin-out at S3), (3) **no
external side effects in scope** — no push/publish/tag, including pending commits
`4da92874` / `8a92985f` (a push needs a separate explicit later instruction),
(4) **no tracked issue** filed. Goal is now activation-ready.

1. **Track 1a method = in-place sharpening (cite P4), not a new shared
   reference.** APPROVED. Overturn only if S1 shows ≥3 boundaries would duplicate
   the same paragraph.
2. **Track 2 bundled, spin-out-able.** APPROVED to keep bundled; decide spin-out
   at S3.
3. **No external side effects in scope** (no push/publish/tag). APPROVED. Pushing
   the pending commits requires a separate explicit instruction.
4. **No tracked issue for the overhaul.** APPROVED skip.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- Routing: find-skills recommended the phase route followed across S1–S6 — `quality` for validation cadence, `critique` for fresh-eye reviews, `impl` for surface/prose edits, and `achieve` for the goal lifecycle (queried read-only at activation via `--recommend-for-task`).
- **Gather** — `Gather: n/a — all context is repo-internal artifacts; no external URL/Slack/Notion/Docs source to gather.`
- **Release** — `Release: n/a — prose/skill-surface change only; no version bump or install-manifest edit planned (a later operator decision could ship it as a release).`
- **Issue closeout** — `Issue closeout: n/a — closes no tracked issue; #386 is already CLOSED (context only), #387/#371 are explicitly out of scope and not closed by this goal.`

## Slice Log

- **S5 — Track 2 slim — done (with an S6 correction, see below).** Two
  concept-separations (P2), not line-shaving. **A — AGENTS.md always-on
  PUSH→PULL (Cautilus):** the Cautilus Start-Here bullet compressed to a 1-line
  pointer (full eval-only/disabled-surface contract already in + tooling-enforced
  by `quality/references/cautilus-on-demand.md`) — always-on *text/concept load*
  reduced (the learnability metric), line count unchanged (it was always one
  bullet). Safeguard sections (Subagent Delegation, Phase Rules) untouched.
  **B — retro own-concept SRP-split (core 160 → 146, off the cap):**
  `## Auto-Retro Trigger` + `## Expert Counterfactual Rule` compressed to their
  load-bearing rule + the repo-specific `check_auto_trigger.py` command,
  delegating taxonomy/examples to the pre-existing references
  `trigger-and-persistence.md` / `expert-lens.md` (zero content lost; verbatim
  contract-snippet phrases preserved). This is the **measurable standing-surface
  shrink**. Synced mirror; froze the `retro` scenario-review decision (scenarios
  unchanged). **Bound fresh-eye critique = PASS**
  (`charness-artifacts/critique/2026-06-18-s5-track2-slim-critique.md`).
  **S6 correction:** the S5 *Skill-Routing collapse* was REVERTED — the
  S6 broad pytest caught that `AGENTS.md`'s `## Skill Routing` is a
  **setup-generated surface** bound verbatim by `setup/scripts/render_skill_routing.py`
  (`matches_compact_block`), so collapsing it flipped `charness doctor`'s
  `repo_onboarding` status `ready → required` (`test_charness_doctor_reports_managed_surface`).
  Restored the canonical block verbatim; collapsing it needs a lockstep
  `render_skill_routing.py` change → deferred to the spun-out Track-2 work.
  Remaining-13-body SRP sweep → spin-out (recommended).
- **S4 — Track 2 audit (read-only) — done.** Artifact:
  `charness-artifacts/critique/2026-06-18-s4-track2-audit.md`. Always-on surface =
  `AGENTS.md` 70 lines (`CLAUDE.md` symlink). Two PUSH→PULL / orthogonality
  targets: the Cautilus block (L11, ~10 lines whose detail already lives in
  `quality/references/cautilus-on-demand.md` + is tooling-enforced → 1-line
  pointer) and the Skill-Routing section (L17–31, which duplicates Start Here:
  find-skills/gather/quality routing). 14 public skill bodies sit within 8 core
  lines of the 160 `MAX_CORE_NONEMPTY_LINES` cap (retro at 160, issue 159, impl
  158, …) — own-concept bloat, ~68% per the Phase-0 finding. Cut target =
  intrinsic-judgment restatement; keep = repo-specific commands/paths/observables.
  **S5 plan:** AGENTS.md PUSH→PULL (always-on shrink) + one `retro` SRP-split
  pilot, each its own fresh-eye critique boundary. **Spin-out sized:** keep the
  AGENTS.md PUSH→PULL + retro pilot in this goal; recommend spinning out the
  remaining-13-body SRP sweep as a follow-up goal.
- **S3 — Track 1a sweep (release publish G3, release-linked close G4, deletion
  G5) — done.** Generalized the S2-validated framing in-place. **G3:**
  `release/references/install-surface.md` (Publication Closure Boundary) now
  renders `public release surface verified` as a P4 per-surface behavioral
  verdict (channels: Real-Host Proof checklist, `fresh_checkout_probes`/
  `startup_probes`, `install_refresh` readback); `release/SKILL.md` step 7 carries
  a terse salient in-body pointer (the verdict detail was relocated out of the
  capped body after the `check-skill-core-headroom` ratchet fired — a P2
  concept-relocation that improved core-headroom 199 → 193; three redundant
  step-7 state-distinction bullets + a duplicate step-6 line consolidated).
  **G4:** the release-linked-issue guardrail now also requires the per-issue
  behavioral verdict from `issue/closeout-discipline.md`.
  **G5:** `critique/references/rename-critique.md` gained a "Per-Removed-Concept
  Verdict" section. Synced mirror; froze the `critique` + `release` scenario-review
  decisions in `docs/public-skill-dogfood.json` (hitl-recommended tier;
  scenarios unchanged; acked). **Bound fresh-eye critique = PASS, no folds**
  (`charness-artifacts/critique/2026-06-18-s3-sweep-framing-critique.md`):
  declares-vs-mandates = mandates on all three; no smuggled gate/token; the
  four-state guardrail (release L158-159) intact; consolidation is concept-merge
  not a cap-dodge (net +2 lines); **Q5 orthogonality = in-place justified** (each
  instantiation differs on unit/proxy/channel/disposition/observer — not a
  duplicated paragraph; ≥3-boundary overturn rule not triggered). Track 1a
  complete. **Track-2 candidates surfaced:** release/SKILL.md at 199/200 (slim in
  S5); optional shared-ref cross-link naming the per-unit-verdict pattern if a
  4th–5th boundary lands.
- **S2 — Track 1a pilot (issue/PR close, G1+G2) — done.** Closed the single
  worst gap in-place: added "## Per-Issue Behavioral Verdict At Close (the
  irreversible-boundary mandate)" to `issue/references/closeout-discipline.md`
  (full home, cites P4, names distinct channel + the resolution critique as
  distinct observer, forbids same-proxy re-read, bakes the
  mandate-not-declare guardrail, states no-new-gate); rewrote the
  `issue/SKILL.md` `carrier_verified`/`CLOSED` guardrail in place to
  "necessary-not-sufficient" (no net lines, held at 199/200 cap); added a salient
  pointer in `issue/references/resolve-flow.md`. Covers both carriers
  (direct-to-default commit + PR merge-to-shared-history). Synced the `plugins/`
  mirror (byte-match). Recorded the public-skill scenario-review decision as a
  freeze in `docs/public-skill-dogfood.json` (scenarios unchanged; rationale +
  non-claim) and acked the slice closeout (`--ack-cautilus-skill-review`;
  planner `next_action: none` → no Cautilus eval per the on-demand contract).
  **Bound fresh-eye critique = PASS, no folds**
  (`charness-artifacts/critique/2026-06-18-s2-issue-close-framing-critique.md`):
  declares-vs-mandates = mandates on all three surfaces; no smuggled gate/token;
  safeguard strengthened (carrier_verified prohibition retained + extended);
  P4 distinct-channel+observer present. Cheap deterministic gate green.
- **S1 — boundary audit (read-only) — done, `c6c0cc56`.** Artifact:
  `charness-artifacts/critique/2026-06-18-s1-boundary-audit.md`. Classified the
  four north-star irreversible families. **Models (already mandate per-unit
  verdict):** achieve issue-bundle disposition (the #386 seed, scoped to
  `achieve`+HOTL-touching bundles) and the HOTL ledger (per-entry provider
  readback, cites P4). **Gaps (rubber-stamp proxy):** G1 standalone `issue
  resolve` close (`verify-closeout CLOSED` + recurrence critique), G2 PR
  merge-to-shared-history (keyword-survival + `CLOSED`), G3 release publish
  (critique-ran + state-distinguished + adapter host-proof checklist), G4
  release-linked issue close, G5 deletions (rename-critique = aggregate
  coherence, slug-drift partially covers). Announcement delivery = mostly-covered
  (per-post readback), not a primary gap. **Recommended S2 target = G1+G2** (the
  issue/PR-close boundary in every carrier outside the seed). Carried the B2
  guardrail: sharpened prose must MANDATE the per-unit question, never DECLARE a
  completion condition. Cheap deterministic gate green (doc-links, markdown,
  secrets, critique-artifact validator). Routing recorded below.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `charness-artifacts/retro/2026-06-18-step0-experiment-program-archive.md` —
  the RESOLVED mechanism, the resolved matrix, the carry-forward general findings,
  and the reusable method. **Read first.**
- `charness-artifacts/critique/2026-06-18-step0-instrument3-c3-results.md` — the
  single-variable isolation (per-unit mandate is the lever; load/channel ruled out).
- `charness-artifacts/critique/2026-06-18-overhaul-plan-v2.md` — the plan;
  **note** its Track-1a machinery is superseded by the resolved findings (see
  Non-Goals).
- `docs/design-north-star.md` — the governing standard; **P4** (provisional
  success, distinct channel + distinct observer) and **P5** (no terminal green)
  are the contract Track 1a generalizes.
- `skills/public/achieve/references/lifecycle.md` (Rung-2 disposition review, the
  irreversible-boundary mandate ~L666–687) — the #386 pilot = the seed to
  generalize. Sibling principle homes: `skills/public/hotl/references/ledger-and-dispositions.md`,
  `skills/public/issue/references/closeout-discipline.md`.
- Commit `6e795f61` (#386 fix, prose-only). Issues: #386 CLOSED (context only);
  #387 (closeout-validator UX) and #371 (browser teardown) OPEN, out of scope.
- `docs/handoff.md` — Next Session pickup that routed here.
- `charness-artifacts/gather/2026-06-18-capabilities-over-features.md` — the
  *capabilities over features* page (orthogonality, composability,
  learnability-by-use; "features are promises, removal is hard"); the positive
  framing behind the Design lens above and Track 2's success metric.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **First bite** (operator-asked). Family: {audit-then-pilot,
  foundational-refactor, full-sweep, shape-as-achieve-goal}. Chosen:
  *shape-as-achieve-goal*. Rejected: direct-implementation paths deferred to
  post-activation slices — the operator wanted a reviewable plan before any prompt
  surface mutates. `single-point: explicit operator choice`.
- **Track 1a method** — new shared reference vs in-place sharpening. Family:
  {new `skills/shared/references/` doc that each boundary cites, in-place
  per-surface sharpening citing north-star P4}. Chosen (default, foldable into
  S2): *in-place sharpening + cite P4*. Rejected: a new shared reference adds a
  prose surface Track 2 wants to cut (P2: displaced overflow goes unread), and the
  resolved finding says the lever is what is SALIENT **at the decision point**, not
  a referenced doc. `single-point: north-star P2 + Step 0 finding`. Surfaced for
  S2 critique — overturn if the audit shows ≥3 boundaries would duplicate the same
  paragraph.
- **Goal scope** — 1a-only vs 1a+2. Family: {1a-only-goal, 1a+2 bundled,
  two-separate-goals}. Chosen: *1a+2 bundled in one draft, Track 2 as a
  spin-out-able later block*. Rejected: splitting now is premature (the handoff
  sequences them) and bundling does not commit to executing Track 2 (operator
  reviews before activating; spin-out is an Operator Decision Queue item).
  `single-point: handoff sequencing + reversibility`.
- **Mode** — artifact-only vs implementation-continuation. Settled by the request
  ("shape … save as draft" + the operator chose shape-as-goal). Assumed:
  *artifact-only Before-phase; do not execute slices*. `single-point: explicit
  operator instruction`.
- **Anti-anchoring on inherited values.** "No new gate" =
  `single-point: north-star P1/P5 governing standard`. "Per-unit verdict is the
  lever" = `single-point: Step 0 resolved finding (Δ≈0.9)`. The irreversible-
  boundary set = `single-point: north-star blast-radius definition`. External-
  write providers vary on a `axis: provider` (Slack/Notion/provider) but that is
  within-boundary, not a goal-scope anchor.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Reviewer provenance: one bounded fresh-eye plan premortem (authentic Sonnet,
read-only, shared parent worktree), 2026-06-18.

**Blockers folded:**

- **B1 — PR *merge* was under-scoped.** A merged PR propagates to shared history
  others build on (north-star "Reopenable ≠ reversible" logic applies to merge,
  not only the tracker flip), so "PR close" alone would let the S1 audit skip the
  merge-to-shared-history trigger. Folded into the Goal Track-1a set and the S1
  audit scope ("PR merge/close; trigger = merge-to-shared-history").
- **B2 — the "cite P4" formula could relapse into a terminal-green floor.** A
  future executor could write "confirm each unit via a distinct channel; when all
  units are confirmed, close" — the second clause re-creates the exact
  "all-green + CLOSED = behavior proven" equivalence #386 named as root cause.
  Folded a concrete per-boundary reviewer question into S2/S3 expected-evidence
  and the High-Confidence critique line: *does the prose DECLARE a completion
  condition (blocker) or only MANDATE the per-unit question (pass)?* This keeps
  the catch as a reviewer judgment, not a new gate.

**Over-worries raised, not folded** (reviewer agreed each was already covered):
in-place-vs-shared-ref default is well-grounded with the ≥3-boundary overturn
guard; Track-2 safeguard-loss already has the "lost or made unread?" critique
question + spin-out gate; S1-first ordering is correct; P2 line-shaving is named
in Non-Goals; optional behavioral re-validation is defensible given Δ≈0.9.

**Verdict:** yes-with-folds — sound to save as a reviewable draft; highest-leverage
fix was B2, now folded.

## Off-Goal Findings

- The handoff (`docs/handoff.md`) mislabels #387 as the "overhaul Phase-1 pilot";
  #387 is actually a closeout-validator one-pass UX issue. **RESOLVED** — the
  handoff already carried the correction (L33–34 "**not** the overhaul pilot");
  the S6 handoff refresh keeps #387 correctly scoped.
- **New (S6):** `AGENTS.md`'s `## Skill Routing` is a setup-generated surface
  pinned by `setup/scripts/render_skill_routing.py` — editing it freely flips
  `charness doctor` `repo_onboarding`. Recorded in the retro + handoff as a
  deferred Track-2 slice (needs a lockstep `render_skill_routing.py` change).

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md
Host log probe: charness-artifacts/probe/2026-06-18-north-star-overhaul.json
Disposition review: charness-artifacts/critique/2026-06-18-north-star-overhaul-disposition-review.md

Broad proof: `python3 -m pytest -q` = **3275 passed, 0 failed** (482s, 2026-06-19)
after the S6 fixes (3 pinned-phrase/generated-surface regressions the per-slice
gates missed, caught at this bundle-boundary broad run and fixed). Targeted gates
green: `validate_skills`, `check_doc_links`, `check-markdown`,
`check_skill_contracts`, `check-skill-core-headroom`. One CLI install/uninstall
test (`test_session_capture_cli_install_and_uninstall_round_trip`) flaked once
under heavier `-n auto` parallelism but passes in isolation and under the default
run — a known parallelism flake, unrelated to this prose-only change.

## User Verification Instructions

**Re-run the gate suite:**

```bash
python3 scripts/validate_skills.py --repo-root .
python3 scripts/check_doc_links.py --repo-root .
./scripts/check-markdown.sh
python3 scripts/check_skill_contracts.py --repo-root .
python3 -m pytest -q            # full broad proof (3272+ tests; ~8 min)
```

**Read the audit + diffs (Track 1a — every irreversible boundary now demands a
per-unit behavioral verdict):**

- S1 boundary audit: `charness-artifacts/critique/2026-06-18-s1-boundary-audit.md`
  (the gap list, models vs gaps).
- The per-boundary mandates (each cites P4, names a distinct channel, adds no
  gate): `git show 8b3e38e9` (issue/PR close) · `git show 439c4112` (release
  publish + release-linked close + deletion). Grep the live surfaces:
  `grep -n "Per-Issue Behavioral Verdict" skills/public/issue/references/closeout-discipline.md`,
  `grep -n "per-surface behavioral verdict" skills/public/release/references/install-surface.md`,
  `grep -n "Per-Removed-Concept Verdict" skills/public/critique/references/rename-critique.md`.
- The framing-not-gate critiques: `charness-artifacts/critique/2026-06-18-s2-issue-close-framing-critique.md`,
  `...-s3-sweep-framing-critique.md` (each answers per boundary: *mandates the
  per-unit question, never declares a completion condition*).

**Read the before/after (Track 2 — standing surface shrank without losing a
safeguard):**

- `git show 142329b2` (S5 slim) and the S6 closeout commit; the measurable shrink
  is `retro/SKILL.md` core 160 → 146 (off the 160 cap) via concept-separation to
  pre-existing references, plus the Cautilus always-on text pulled to
  `quality/references/cautilus-on-demand.md`. The S5 critique
  (`...-s5-track2-slim-critique.md`, with the S6 generated-surface correction)
  confirms no safeguard lost/unread.
- Confirm no terminal-green gate was added:
  `git diff 1f10df0b..HEAD -- scripts/ tests/` is empty for behavior code (the
  whole overhaul is prose/skill-surface + artifacts).

## Auto-Retro

Cited retro: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`.
Per-improvement disposition of its `## Next Improvements`:

Retro dispositions: none — workflow (pre-edit near-cap SKILL.md headroom+snippet check): both traps are already caught at commit by existing gates (check-skill-core-headroom, check_skill_contracts); the fix is a workflow pre-check habit, not a missing structural guard.

Retro dispositions: none — capability (a pre-edit affordance that prints a SKILL.md's core-headroom margin + pinned contract snippets): convenience-only; the two existing commit gates already enforce both constraints, so this is nice-to-have and is deferred to the spun-out 13-body SRP goal if the manual pre-check proves costly.

Retro dispositions: applied: memory — captured the staged-blob-headroom-ratchet and contract-snippet-slim traps in the durable retro (charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md) Waste + Sibling Search, the canonical home the recent-lessons digest selects from on its next persist cycle.

Structural follow-up: none — the transferable waste (a body-slim drops a pinned contract phrase / ignores the staged-blob core-headroom ratchet) is already caught post-hoc by the existing commit gates check_skill_contracts and check-skill-core-headroom; the durable retro memory note is the pre-check for the spun-out 13-body SRP sweep, so no new gate/guard is warranted.

# Achieve Goal: North-star overhaul: Track 1a (per-unit verdict framing) + Track 2 (slim)

Status: draft
Created: 2026-06-18
Activation: `/goal @charness-artifacts/goals/2026-06-18-north-star-overhaul.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: draft awaiting operator review + activation.
- Current disposition: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary changed.
- Current slice intent: shape-only. First real slice on activation is **S1 —
  boundary audit** (read-only): classify every irreversible boundary as
  *mandates-a-per-unit-behavioral-verdict* vs *rubber-stamps-a-proxy*. Once
  active, the slice intent names the reviewable-intent unit in progress and the
  commits it spans; critique and broad proof do not re-fire within one unchanged
  intent (meaningful-slice-cadence).
- Next action: operator resolves the `Discuss before activation` items, then
  activate with
  `/goal @charness-artifacts/goals/2026-06-18-north-star-overhaul.md`.
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
| S1 — boundary audit | Read-only: classify each irreversible boundary (issue close, PR **merge**/close, release-linked close, external write, deletion — PR trigger = merge-to-shared-history, not the tracker flip) as mandates-per-unit-verdict vs rubber-stamps-proxy; produce the gap list | Grounds Track 1a in evidence; mirrors #386 pilot-first; stops me guessing the gap | audit artifact under `charness-artifacts/critique/` | planned |
| S2 — Track 1a pilot | Close the single worst gap from S1 in-place (sharpen closeout framing → per-unit behavioral verdict, cite P4, no gate) + fresh-eye critique (framing-not-gate) | Validate the LIGHT pattern on one real gap before any sweep | diff + bound critique artifact; the critique must answer per boundary: *declares a completion condition (blocker) or only mandates the per-unit question (pass)?* | planned |
| S3 — Track 1a sweep | Generalize the validated framing to the remaining real gaps from S1 | Pattern proven by S2; one critique covers the coherent bundle | diffs + critique (same per-boundary declares-vs-mandates check) | planned |
| S4 — Track 2 audit | Measure the always-on surface (AGENTS.md / CLAUDE.md / skill bodies at cap) + own-concept bloat; plan PUSH→PULL + SRP splits | Track 2 is Step-0-independent; needs its own measurement before cutting | audit + plan (decide spin-out — see Operator Decision Queue) | planned |
| S5 — Track 2 slim | Execute PUSH→PULL + SRP compression on the highest-bloat surfaces + fresh-eye critique (no safeguard lost) | After 1a lands the framing, the docs should reflect the smaller standing surface | diffs + before/after counts + critique | planned |
| S6 — closeout | Broad proof + retro + per-improvement disposition + handoff update | Bundle boundary | gate suite green + retro + bound disposition review | planned |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

- Decision: Split **Track 2 (SLIM)** into its own goal? | Owner: operator |
  Why deferred: Track 1a is the priority and independently shippable; Track 2 is
  Step-0-independent and high-blast-radius (always-on surfaces) | Unblock action:
  operator says split vs keep-bundled | Revisit trigger: after S3 lands Track 1a.
- Decision: File a tracking GitHub **issue** for this overhaul? | Owner: operator
  | Why deferred: the handoff mislabeled #387 as the tracker; the overhaul has no
  tracked issue today | Unblock action: operator says file vs skip | Revisit
  trigger: at activation.
- Decision: Push pending local commit **`4da92874`** (Step 0 archive) to
  `origin/main`? | Owner: operator | Why deferred: external action, awaiting
  confirmation since the prior session | Unblock action: operator approves push |
  Revisit trigger: at activation or the next push boundary.

## Discuss before activation

Discuss before activation: four consequential defaults are surfaced for the
operator — (1) Track-1a in-place method, (2) Track-2 bundling/spin-out,
(3) no external side effects in scope, (4) no tracked issue filed. **SURFACED,
NOT YET RESOLVED** — the operator resolves these before activating; until then
`--pursue-ready` is correctly false.

These consequential defaults are **surfaced, not yet resolved** — the operator
resolves them before activating (until then `--pursue-ready` is correctly false):

1. **Track 1a method default = in-place sharpening (cite P4), not a new shared
   reference.** Chosen to honor north-star P2 and the "salient at the decision
   point" finding; overturned only if S1 shows ≥3 boundaries would duplicate the
   paragraph. Confirm or override.
2. **Track 2 is bundled but spin-out-able.** It edits always-on surfaces
   (high blast radius). Decide at S3 whether it stays in this goal or becomes its
   own. Confirm the bundling is acceptable for now.
3. **No external side effects are in scope** (no push/publish/tag), including the
   pending `4da92874` archive commit. Confirm, or approve a specific push.
4. **No tracked issue is filed for the overhaul.** Confirm skip, or ask to file
   one before activation.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — at activation, ask `find-skills` to recommend the skill per phase
  (expected: surface edits → `impl`; fresh-eye reviews → `critique`; validation
  cadence → `quality`) and record the route returned. [fill during run]
- **Gather** — `Gather: n/a — all context is repo-internal artifacts; no external URL/Slack/Notion/Docs source to gather.`
- **Release** — `Release: n/a — prose/skill-surface change only; no version bump or install-manifest edit planned (a later operator decision could ship it as a release).`
- **Issue closeout** — `Issue closeout: n/a — closes no tracked issue; #386 is already CLOSED (context only), #387/#371 are explicitly out of scope and not closed by this goal.`

## Slice Log

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
  #387 is actually a closeout-validator one-pass UX issue. Correct the handoff at
  closeout (S6) so the next session is not misrouted.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

_Filled at closeout: the exact commands to re-run the gate suite, and the audit /
diff / before-after artifacts to read, so the operator can confirm each
irreversible boundary now demands a per-unit verdict and the standing surface
shrank without losing a safeguard._

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out

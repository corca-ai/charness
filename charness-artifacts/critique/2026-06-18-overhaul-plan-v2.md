# North-Star Overhaul Plan v2 (post-critique) — PROVISIONAL, gated on Step 0

Reflects the 4-lens fresh-Opus critique of v1 (2026-06-18-overhaul-plan-v1-for-critique.md).
Status: PROVISIONAL. Everything structural is gated on the Step 0 experiment. Execution
is post-compaction. The Step 0 experiment design must itself be critiqued and operator-
approved before it runs.

## What changed from v1 (the critique, accepted)

All four critics converged:
- **The keystone inference over-reached.** "Agents have the judgment; failure is
  structural not informational" rests on NON-reproduction of #386 + a confounded test
  (sole-task, code-readable bug, priming brief). The contradiction v1 footnoted is
  load-bearing: **#386's reviewer was fresh and failed; the 50 trials say fresh agents
  don't fail.** Unresolved variable = **context load / decision salience**. The tests
  maximized salience + minimized load; #386 was the opposite.
- **Real open frame:** judgment may be PRESENT but not reliably RETRIEVED under
  load/low-salience — a retrieval/attention problem, neither prose nor structural-routing.
  This is UNRESOLVED and Step 0 exists to test it.
- **D1 demoted** from a universal law ("the lever is structural") — which repeats the
  "just add a gate" over-rotation — to: *for the families tested, a prose brief was
  redundant; derive the lever per problem-family.*
- **Cuts (all critics):** 1b typed trust-class label (the gate-reflex re-skinned as data,
  dead by our own evidence, unowned maintenance, new sync surface); 3a classification
  ceremony (→ one heuristic sentence); per-doc retrospective cadence (charness already has
  event-driven rca-ledger); migration tripwire machinery (→ git revert + one-line watch).
- **Behavioral-GREEN is not auto-proof either** (flaky/asserts-nothing/tests-the-mock).
  Only behavioral-RED (a real observed failure) is reliable. Carry this sharper form.

## Step 0 — the gating experiment (FIRST action; design TBD-and-critiqued)

Hypothesis under test: **the #386 rubber-stamp is driven by context-load / low decision
salience, and a fresh sole-task reviewer (context reset) restores the judgment agents
already possess.**

- Must be designed to genuinely VERIFY *or* FALSIFY — not ceiling like rounds 1-5.
- Reproduce a rubber-stamp under: long/loaded context + the verification buried as a
  non-salient sub-step + NO priming brief.
- If it reproduces → test whether a fresh sole-task reviewer fixes it, AND separate
  "context-reset" from "engagement-framing" as the mechanism (e.g., long-context reviewer
  vs short-context reviewer).
- If it does NOT reproduce even under load → we do not understand #386; STOP and reconsider
  before any structural change.
- The experiment design itself gets a fresh-critique + operator approval before running.

## Track 1a — fresh-eye routing at irreversible boundaries (ONLY if Step 0 supports it)

Re-specified structurally per the operational critique (freshness alone is necessary, not
sufficient; #386's fresh reviewer failed):
- **Deterministic trigger:** the irreversible-action script (issue/PR close, release
  publish, external write, deletion) refuses to proceed without a reviewer-verdict token
  that NAMES the raw artifact's immutable ref/SHA (identity only — the script verifies a
  verdict exists for this exact ref; it must NOT test any content predicate, or it
  relapses into the content-gate reflex). Code enforces the *routing/state-transition*;
  the reviewer (intelligence) owns every judgment about what the ref contains. (Fix from
  the bounded v2 critique, Q1.)
- **Reviewer PULLs raw state** from canonical sources (re-run the gate, re-read the issue
  via `gh`, re-execute the behavioral check). The doer does NOT author the reviewer's
  brief — the pre-digested "it's done" summary is excluded (that is how #386's reviewer
  was fed).
- **Reviewer must RUN the behavioral check** and read red/green; route onto the
  behavioral-RED channel. Freshness + independent behavioral execution, not freshness alone.
- **One reviewer + raw multi-unit manifest + per-unit verdicts** (not N serial spawns;
  per-unit-not-bundle as an absolute is operationally untenable). **Step-0-gated open
  question (Q3 from the bounded v2 critique):** a single reviewer pulling N units' raw
  state recreates the very load/low-salience condition Step 0 is testing — so if Step 0
  confirms load-induced rubber-stamping, cap per-reviewer unit count or require per-unit
  context reset so each verdict is rendered under comparable salience. NOT a settled
  compromise.

## Track 2a — slim docs (independent of Step 0; the genuine less-is-more)

- AGENTS.md/CLAUDE.md → minimal stable entry + skills index; detail loaded on demand
  (PUSH→PULL). Directly attacks the diagnosed own-concept bloat.
- Concept-separate the ~200-line skill bodies (own-concept compression, SRP). Cut
  intrinsic-judgment restatement; keep non-intrinsic repo-specific info.
- Carry two one-line heuristics: "prefer structural fixes over prose"; "name proxy
  evidence as proxy."

## Phase-0 corrections (carried)

Cluster membership fix (coherent family = lifecycle-state misclassification; the hand-
picked cluster was cherry-picked); mutation-CI a first-class track; behavioral-RED reliable
/ any-GREEN not auto-proof replaces vague "non-terminality."

## Rollback / preconditions

git revert per change; one-line watch for the first close-on-proxy after a phase ships.
The honest limitations are GATING preconditions, not footnotes: nothing structural ships
until Step 0 resolves the load/salience question.

## Deferred (not in v2 core)

- "Gate exit-behavior carries trust" (proxy gate exits soft, behavioral exits
  authoritative) — a smaller structural alternative to the cut 1b label; revisit only if
  Step 0 shows agents need a trust signal at all.

# North-Star Phase 0 — Validated-Diagnosis Back-Test (2026-06-20)

**Verdict: PARTIALLY CONFIRMED — the diagnosis is not contradicted (0/7), is
supported by the irreversible-boundary cases, and is sharpened on two
load-bearing points. Action: proceed to Phase 1 — after landing the corrections
below in the roadmap + design north star (done with this note).**

Method: a dynamic workflow ran 7 parallel per-issue back-tests (one agent each)
classifying how the *original* failure was caught (deterministic gate /
fresh-eye review / escaped-to-operator / self-caught), whether it sat at an
irreversible boundary, and whether it supports the diagnosis — plus a
bloat-driver test on the 5 capped SKILL.md bodies, a synthesis, and an
**adversarial verify pass that refuted the synthesis's overclaims**. This note is
the verify-corrected reading; the raw synthesis over-reached (see "Corrections").

## Per-issue catcher table

| Issue | Catcher (of the *original* failure) | Irreversible boundary? | Conf | Diagnosis |
|---|---|---|---|---|
| #359 closeout flips `Status` while a placeholder section is pending | escaped → operator (incidental retro pass; local gates + fresh-eye review + push/CI + apply-readback **all green**) | yes — external-write | high | **supports** |
| #363 premature issue close via close-keyword leak in a non-fix commit | escaped → operator (downstream `gh issue view` found a dishonest `CLOSED`) | yes — issue-close | high | **supports** |
| #386 per-issue HOTL matrix before issue-bundle close | escaped → operator (a standing fresh-eye review **ran, re-read the same proxy, and rubber-stamped**) | yes — issue-close | high | **supports** |
| #381 operator decision queue at closeout | escaped → operator (operator "had to say again") | yes — issue-close | med | **supports** |
| #385 boundary matrix before achieve marks a goal `blocked` | escaped → operator (false-`blocked` over-classification; human caught) | no — reversible (mirror image) | high | **supports** |
| #376 re-judgment after a deterministic helper output | escaped → operator (live observation in ceal, filed as an issue) | no — reversible | med | neutral |
| #382 HOTL proving-surface staleness needs adjudication | escaped → operator (live operator pushback) | no — reversible | high | neutral |

**Tally: 0 contradicts. 5 supports / 2 neutral.** Firm base = the **3
high-confidence irreversible-boundary cases (#359, #363, #386)**; #381 supports at
medium confidence; #385 supports as the *reversible mirror-image*. The 2 neutral
cases are reversible contract/teaching defects — neither demonstrations of the
diagnosed failure nor counter-examples. All 4 of these refs that carry an
`rca-ledger.jsonl` entry log `caught_by: human`.

## What the back-test confirms

1. **At the irreversible boundaries, the standing teeth were green when the
   wrong answer escaped.** On #359 the local gates, a fresh-eye review, push/CI,
   and apply-readback all passed; the contradiction (a `completed` goal whose own
   `## Auto-Retro` still held a pending stub) was noticed only post-push,
   incidentally, by a retro pass reading a *different* channel (the artifact
   body). #363's dishonest `CLOSED` surfaced only when a downstream pickup ran
   `gh issue view`. This is the diagnosis's core — one green channel trusted as
   proof an irreversible action was done right.
2. **The bespoke-gate-as-bloat mechanism is live.** 4 of the fixes (#359, #363,
   #385, #386) added a new gate/floor in response to a human-caught failure
   (`rca-ledger` `durable_kind: gate`, `converted: true`). The accretion the
   diagnosis names is real and ongoing.

## Two corrections the adversarial pass forced (load-bearing)

**A. It is NOT "review beats gates" and NOT "stop adding gates."** The synthesis's
"7/7 escaped every gate AND every review at the boundary" over-reached: only ~4
issues sit at an irreversible boundary, and the "a standing fresh-eye review ran
and still rubber-stamped" finding rests on **2 issues (#359, #386)**, not the
whole cluster. More decisively, **the fixes that worked were gates** (#359's
section-placeholder complete-state check; #385's pre-`blocked` boundary matrix).
The honest lesson is not anti-gate; it is **anti-same-channel-terminal-trust**:
the failure is trusting one green *channel*, and the working remediation is
forcing a check on a **distinct evidence channel** — which P5 explicitly permits
a gate to do (*a gate may force a question; it may not declare completion*).
#359 and #386 prove a distinct *observer alone is insufficient*: on both, a
fresh-eye review existed, ran, re-read the **same triggering proxy**, and passed.
The operative variable is the **evidence channel**, not whether the checker is a
gate or a human.

→ Phase 2's "distinct observer per unit" must read as "distinct observer
**consulting a distinct evidence channel** per unit, before the boundary" — this
is already P4's wording; keep it explicit so it cannot degrade into "a fresh
agent re-reads the same proxy."

**B. #385 is the mirror image.** Its failure was a *false-`blocked`
over-classification* of a reversible internal state, not a wrong-completion. The
Phase-2 per-unit-disposition floor must guard **both** wrong-completion and
wrong-block — single-context over-generalization runs in both directions.

## Bloat finding (floors vs cap)

"Boilerplate dominates the capped bodies" is **false as written.** Floor share:
impl ~32%, debug ~31% (the mixed pair), gather 16%, quality 15%, find-skills 11%.
The 200-line pin is driven mainly by **genuine concept size** (quality's ~25
inventory-dispatch anchors, debug's RCA lens stack, find-skills' routing surface,
gather's provider ladder), not stacked closeout ritual. **But the floor is real
and near-verbatim duplicated:** the critique/fresh-eye-subagent floor recurs
across ~8 public skills, closeout-discipline across ~6,
external-capability-proof-ladder across ~6, rca-ledger-append across ~3.

→ Phase 3 does **both, in priority order:** (a) **fix the floors for impl +
debug** — replace inlined 5–15-line restatements with one-line cites to the
existing shared references (`skills/shared/references/fresh-eye-subagent-review.md`,
`closeout-discipline.md`, rca-ledger-append) — reclaims ~50–64 lines each and
kills the duplication signal; (b) **quality + find-skills are genuine-concept cap
pressure → concept-separation, not floor surgery** (quality's inventory anchors;
find-skills' decision-frame-vs-discovery split). Floor cleanup alone will not
de-pin them. Measure concept clarity, not line count.

## Residual risks / caveats (carry into Phase 1+)

1. **Survivorship.** The corpus is the 7-issue recurrence cluster — they became
   issues *because* a human caught them. Gate-silent successes leave no issue,
   and `rca-ledger` shows many `caught_by: gate` entries elsewhere. Read the
   finding as "the standing teeth were green at *these* escapes," **not** "gates
   never catch."
2. **Catcher classification is "escaped → operator" on all 7, but 2 are
   coin-flips** (#363, #376 each self-note borderline self-caught-same-agent),
   and only 4/7 have a direct `rca-ledger` entry. Don't treat the operator-catcher
   label as instrumented certainty.
3. **Phase 1 (#387) must not add an 8th floor.** The win is making the existing
   closeout stack *legible in one pass*, not growing it.
4. **The distinct-channel prescription is grounded by counterfactual (#359) + one
   realized fix (#386), not by a demonstrated prevention.** Treat it as the
   best-supported direction, to be proven by Phase 2's first consumer.
5. **Phase 3 measures concept clarity, not line count.**

## Disposition of the conflicting workflow verdicts

Synthesis returned `proceed_to_phase_1`; the adversarial verify returned
`revise_roadmap_first` while affirming `verdict_sound: true`. **Owner
resolution:** the diagnosis is not contradicted, so the roadmap's *phase plan*
stands and Phase 1 proceeds. The verify's objections are real and are
dispositioned into corrections A/B + this note, plus minimal honesty edits to the
roadmap (mark Phase 0 done; carry A/B into the Phase 2/3 framing) and the design
north star (drop the "provisional, pending back-test" marker; cite this note).
That is "revise the doctrine surfaces before propagating," not "halt the plan."

Source run: dynamic workflow `wf_8bf4fdb7-04a` (10 agents; 7 back-tests + bloat +
synthesis + adversarial verify).

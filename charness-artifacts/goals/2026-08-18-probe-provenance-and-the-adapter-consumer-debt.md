# Achieve Goal: A verdict may not claim more than its probe measured

Status: draft
Created: 2026-08-18
Activation: `/goal @charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md`

This file is the living goal scratchpad. It is activated by the user's request after
the pre-implementation critique passes.

## Goal

Make a behavioral probe unable to claim more than it measured, at the two boundaries where
a wrong claim escapes — an issue close and a release publish — and then pay down the
adapter-consumer debt using that mechanism as the way each row is proven. The debt is not
the point; it is the corpus that proves the mechanism works on 45 real rows instead of on
one worked example.

## Problem

On 2026-08-18 three of one session's own measurements were refuted, each by a reviewer with
no execution capability. All three share one generator: the probe's stimulus came from the
agent's model of the mechanism rather than from the source that defines the claim, and
nothing established that the run entered the path under judgment. "The fix is absent" and
"the fixed branch was never entered" render identically, so a probe that measured nothing
reads exactly like a probe that measured a failure — and in one case that produced a wrong
report to the operator, in another a "verified" that preceded any distinct observer.

This repo already enforces the countermeasure on its TEST surface: a behavior test carries a
mutation that must be killed, and the reconciliation census carries a liveness control so a
row cannot pass by sharing no field with its probe. It does not enforce it on the PROBE
surface, and the probe surface is what closes issues and publishes releases.

Meanwhile the adapter-consumer census counts 45 rows of unpaid debt — 37
`accepted-risk-unguarded` plus 8 `no-version-validation` — and the count is compared to
nothing, so a 46th row lands green. Paying those rows down without the probe discipline
first would reproduce the 2026-08-18 error 45 times.

## Fixed Decisions

- The probe record is a POPULATED EVIDENCE RECORD, not a new gate that renders a verdict
  about other gates. The north star names a gate-that-checks-gates as the anti-pattern; the
  teeth here are the same ones it does license — a populated record and a distinct observer.
- Base-vs-HEAD disagreement is the minimum bar for a probe to be readable as evidence. When
  base and HEAD agree, the honest output is "this probe measured nothing", never the result.
- Stimulus provenance is quoted, not summarized: an issue body line, a spec docstring, or a
  shipped test fixture, reproduced verbatim.
- The consumer census gains a pre-change query before it gains any new teeth. Enumeration is
  cheap and prevents; refusal is expensive and only detects.
- A census row may carry more than one defect class. The 2026-08-18 seeding assumed one and
  mis-filed at least one row, which would have been repaid under the wrong remedy.

## Probe Questions

- Does the base-vs-HEAD rule survive contact with probes whose base does not build, or whose
  fix is a new file with no base at all? Slice 1 answers before the rule is wired anywhere.
- Is `safe-checks-errors` decidable by AST — does this file branch on `errors`/`valid`
  between the loader call and the first consequential read — or does it collapse into the
  same judgment the prose reason already carries? Slice 3 answers with a measurement over
  the 55 existing rows, not with an opinion.
- Is quality's same-day scaffold overwrite the defect `#628` reports, or the designed
  continue-in-place its debug sibling documents? This is an operator design call and Slice 5
  brings it to the queue rather than deciding it.

## Non-Goals

- Do not build a gate that inspects other gates' verdicts. If the probe record cannot be
  populated with captured observables, that is the finding; a meta-verdict is not.
- Do not convert the two-round review obligation's JUDGMENT half into automation. Whether a
  finding is the class under repair, whether a channel is genuinely distinct, and whether an
  accepted-risk reason is honest all stay human-language judgment.
- Do not pay the census debt down by editing verdict strings. Four of five verdicts are
  editable by the party reporting them, and a debt that falls without a behavior change is
  the failure this goal exists to make visible.
- Do not close `#628` inside this goal on a design call the operator has not made.

## Boundaries

- **Precondition, not scope**: the standing lane is red on a load-dependent flake in
  `tests/test_web_fetch_cleanup.py` that blocks pre-push. It is
  [handoff](../../docs/handoff.md) Next Session item 1 and must clear before this goal's
  first push, but fixing it is not this goal's work.
- Issue close, release publish, and proof-surface authoring are irreversible boundaries.
  Each needs its own phase-scoped grant; none is inferred from a green gate.
- Every slice that changes verdict logic on a proof surface owes the second bounded review
  round over the repaired surface, capped at two rounds.
- The census manifest is the row-level contract. A row's disposition changes only with a
  behavioral probe attached.

## User Acceptance

- A probe supporting a close or a publish carries its stimulus verbatim with provenance and
  its base/HEAD pair, and a probe whose base and HEAD agree is reported as measuring nothing
  — demonstrated on at least one real close, not only in a fixture.
- `check_adapter_consumer_classification.py --impact <loader-symbol>` answers "who reads this
  producer" before a shared output contract changes, and the implementation-discipline order
  names that step.
- The accepted-risk count cannot rise silently: an increase requires a named reason, in the
  same scoped-accept shape the dup ratchet already uses.
- The `no-version-validation` rows are wired onto the shared resolver, or each carries a
  recorded reason it cannot be.
- Every row paid down flips a behavioral assertion, not a string.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/check_adapter_consumer_classification.py --repo-root .` at every commit
  boundary; the per-verdict counts are the running measure.
- `python3 -m ruff check --no-cache scripts skills tests` and the standing pytest lane.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  immediately after each slice commit and BEFORE the broad lane.

### Behavioral Proof

- Each debt row paid down is proven by running the real CLI in a temp repo under the
  conditions the row's `reason` names — not by reading the diff, and not under conditions
  chosen for convenience.
- Every such probe records its stimulus provenance and its base/HEAD pair. A probe that
  cannot show base and HEAD disagreeing does not count as evidence for the row.

### Distinct-Observer Review

- Bounded read-only reviewers, briefed from PRIMARY sources — the issue body, the shipped
  spec, the row's own `reason` — and deliberately NOT given the agent's probe transcript.
  The 2026-08-18 evidence is that a reviewer handed the agent's summary reviews the summary;
  the two refutations came from reviewers that went to the code instead.

## Slice Plan

| # | Slice | Proves |
| --- | --- | --- |
| 1 | Probe record: stimulus provenance + base/HEAD pair, with the no-base and no-build arms answered | A probe that measured nothing says so |
| 2 | `--impact <loader-symbol>` pre-change query; `enumerate-consumers` enters the discipline order | The preventing tool runs before the change, not after |
| 3 | Census: multi-class rows, no-increase seam, AST witness trial for `safe-checks-errors` | The debt count can only fall silently |
| 4 | Pay down the debt in severity order, starting with gates that report the opposite of truth | 45 rows, each with a behavioral flip |
| 5 | Two-round bookkeeping as typed critique fields; `#628`'s design call to the operator queue | The obligation is recorded, not remembered |

## Slice Log

Not started.

## Backlog Recount

- 37 `accepted-risk-unguarded` and 8 `no-version-validation` rows at goal creation; the
  live figures come from the census command, not from this line.
- `#628` remains open with a re-measurement comment and an unmade design call.
- `#668` (runtime bar) and `#546` sit in one file and are an operator ruling, not this goal.

## Operator Decision Queue

- Does quality's same-day scaffold overwrite stay (continue-in-place, as debug documents) or
  go (the defect `#628` reports)? The families currently disagree.
- Should the 14 per-skill `adapter-contract.md` files carry the version-containment rule, or
  is the runtime refusal — which names the file and the line to fix — the better channel?

## Discuss Before Activation

- Slice 4 is the long pole and is the one that could turn into mechanical grinding. If the
  Slice 1 mechanism does not make a row's proof cheap, stop and re-shape rather than paying
  45 rows by hand.

## Context Sources

- [The session retro](../retro/2026-08-18-adapter-version-containment-and-the-consumer-census.md) — the three refuted measurements and their shared generator.
- [The closes critique](../critique/2026-08-18-closing-four-verified-resolved-issues.md) — the round that refuted two of them.
- [The design north star](../../docs/design-north-star.md) — P4, P5, and the proof-surface reading of the irreversible boundary.
- [The census manifest](../../scripts/adapter-consumer-classification.json) — the row-level debt this goal pays down.

## Interview Decisions

- Rejected: a goal that only pays down the 45 rows. The retro's evidence is that paying them
  down without the probe discipline reproduces the error once per row.
- Rejected: a goal that only ships the probe discipline. A mechanism with one worked example
  is how this repo has repeatedly shipped rules that did not survive their second case.
- Chosen: the discipline first, the debt as its forcing corpus, in one goal so the mechanism
  is judged by whether it made 45 real proofs cheap.

## Plan Critique Findings

Not yet run — this goal is `draft` and owes its pre-implementation critique before
activation. The two expert counterfactuals in the source retro are inputs to that critique,
not a substitute for it.

## Closeout Binding Plan

- Reviewed inputs: the census manifest, the probe records produced by slices 1 and 4, and
  every issue or release carrier this goal touches.
- Frozen target: the commit that lands the final debt row or its recorded refusal.
- Fresh-eye: bounded read-only reviewers briefed from primary sources, without the agent's
  probe transcript; two rounds on any slice that changed verdict logic.
- Verification lock: the census command's per-verdict counts plus the changed-line proof at
  the frozen target.
- Complete flip: only after a retro bound to this goal records that no row was paid down by
  editing a verdict string.

## Off-Goal Findings

None yet.

## Final Verification

Not started.

## User Verification Instructions

Not started.

## Auto-Retro

Owed at completion, bound to this goal by its `Goal:` field.

# Can-This-Rule-Fire Sweep

Date: 2026-08-02

Four instances of one class surfaced by accident, every one found by a person
and never by a gate: **a rule that cannot fire in the situation it was written
for**. It emits no failure, no log line, no ticket. Four accidents is not a
measurement. This is the measurement.

Known members before the sweep: [#471](https://github.com/corca-ai/charness/issues/471)
(a literal compared against prose this repo writes bolded, so the gate it
guarded had never executed), [#473](https://github.com/corca-ai/charness/issues/473)
(`--fail-on-pre-rule-refusal` reports 0 for every possible corpus, because the
predicates it compares are mutually exclusive by control flow), and
[#475](https://github.com/corca-ai/charness/issues/475) (bounded fresh-eye
review MANDATED by several skills, inert in any repo that never ran `setup`).
A fourth, unnumbered, was a population statement that hid a third intake bucket.

## The Predicate

**Written down BEFORE the population was read**, so "can this rule fire?" is
answered the same way every time and the count means something. Committed in
this file ahead of any finding.

> **Q: Is there a concrete, constructible input, in the situation this rule was
> written for, that makes it fire?**

A rule is **`cannot-fire`** when at least one of these holds:

1. **Unreachable by construction** — its guard is mutually exclusive with the
   situation it targets, so control flow makes it dead. (#473's shape.)
2. **Population empty by construction** — the set it inspects is always empty in
   its target situation. Structurally empty, not merely empty today; "0 findings
   this run" is not this.
3. **Literal-vs-reality mismatch** — it matches a literal, format, or phrase
   against a surface whose real content never takes that form. (#471's shape.)
4. **No reachable precondition** — it mandates an action requiring a precondition
   that its target situation cannot supply. (#475's shape.)
5. **Verdict computed and discarded** — it renders a decision that nothing
   consumes at the surface which acts on it.

A rule is **`can-fire`** only when a concrete input in its target situation is
named that makes it fire. "It looks reachable" is not an answer; the input is.

Every rule read gets exactly one classification:

| value | meaning |
| --- | --- |
| `can-fire` | a firing input in the target situation is named |
| `cannot-fire` | one or more of criteria 1–5, with the criterion named |
| `not-a-rule` | inspected and renders no verdict about other code or artifacts |
| `unread` | in the population, not read — counted, never silently dropped |

Every `cannot-fire` gets exactly one disposition: `repaired` / `issue #N` /
`accepted: <reason>`.

**A reader must be able to tell "checked and live" from "not checked."** The
absence of that distinction is what made four findings look like bad luck.

## Population And Denominator

Measured **2026-08-02, after Lane A's fold** — so the corpus includes this run's
own artifacts. The prior run shipped a denominator measured before its own
artifacts landed in the corpus it was measuring; this one states the timing.

| stratum | population | how counted |
| --- | --- | --- |
| S1 `*_RULE_DATE` constants | 17 across 12 files | `grep -rn "_RULE_DATE\s*=\s*date(" scripts/ skills/` excluding `plugins/` mirrors |
| S2 `validate_*` / `check_*` scripts | 107 (91 repo + 16 skill-package) | `ls scripts/validate_*.py scripts/check_*.py` plus `skills/*/*/scripts/` |
| S3 contract/reference surfaces an agent reads | 202 (18 shared references + 178 public-skill references + 6 convention docs) | `ls` over those three roots |

**S3 is the stratum an earlier draft of this sweep did not have.** That draft
enumerated only code, and #475 — the instance that prompted the sweep — lives in
a contract surface an agent reads. A sweep that only reads code cannot find the
instance that started it.

`plugins/` mirrors are excluded throughout: they are generated copies of the
same rules, not independent ones. Counting them would double every finding.

## Scope Call On S3

S3 at 202 documents is materially larger than the whole population the earlier
draft counted. Per this goal's stop condition (2), that is re-scoped explicitly
rather than silently sampled:

- the S3 predicate is narrow — a reference is in scope only when it states a
  rule an agent must OBEY (a mandate, a precondition, a refusal), not when it
  merely describes or explains;
- the reduced S3 set and its own denominator are recorded below;
- the 202 stays stated as the unfiltered stratum, so the reduction is visible as
  a reduction and not as the original population.

## Findings

<!-- populated by the sweep; each row carries its classification, the criterion
     when `cannot-fire`, and its disposition -->

## Counts

<!-- read / can-fire / cannot-fire / not-a-rule / unread, per stratum, each
     against the denominator above -->

## Non-Claims

- This sweep does not claim the population is exhaustively READ. Whatever is not
  read is counted as `unread` against the stated denominator rather than omitted.
- This sweep is a one-off MEASUREMENT plus targeted repairs and dispositions. It
  is deliberately **not** a permanent meta-validator in CI: the north star names
  a validator that audits validators as the anti-pattern applied to itself.
- A `can-fire` verdict says a firing input exists. It does not say the rule is
  correct, well-scoped, or worth keeping.

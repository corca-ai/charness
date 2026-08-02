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
- the mandate filter (>=5 occurrences of must / never / do not / forbidden /
  required / refuse / blocked / mandat) reduces the 202 to **71**;
- of those, **79 units were assigned** across the two S3 slices (all 24 shared
  references and convention docs, plus 55 public-skill references) and **54 were
  read** — the 25 unread are counted in `## Counts`, never dropped;
- the 202 stays stated as the unfiltered stratum, so the reduction is visible as
  a reduction and not as the original population.

## Findings

### Confirmed `cannot-fire` (survived adversarial verification)

| rule | file:line | criterion | disposition |
| --- | --- | --- | --- |
| `validate_quality_runtime_signal_claims` | `scripts/validate_current_pointer_freshness.py:187` (pre-repair) | 1 + 5 — the entire body was `_ = repo_root`; a registered check rendering no verdict | **repaired** — deleted from the check list, with the reason recorded at the call site |

One confirmed instance, and it is the class exactly: seven checks were registered
in `validate_current_pointer_freshness`, a reader saw seven, and six ran. Its own
comment explained why it was empty, which makes the emptiness deliberate and the
REGISTRATION the defect.

### Known members carried into the sweep

| rule | disposition |
| --- | --- |
| #471 `has_repo_delegation_contract` | **repaired** before this sweep; re-read here and now also walks the authorization ladder |
| #475 the delegation authorization rule | **repaired** in Lane A of this goal |
| #473 `--fail-on-pre-rule-refusal` | **repaired** — resolved as a TRIPWIRE with a forced-scope probe, not deleted (below) |
| #476 the compact `AGENTS.md` template markers | **issue #476** — filed this run, measured, not repaired: both repair directions newly APPLY floors to repos previously outside them |

**#473 resolved.** `pre_rule_rung1a_refusals` is 0 for every possible corpus
because pre-rule and rung-1a-refused are mutually exclusive by control flow, so
`--fail-on-pre-rule-refusal` had never returned 1. The predicate's own wording
decided the disposition: the situation the flag was written for is **the
grandfather leaking**, not the current corpus, and in that situation it does
fire. Deleting it would remove a guard for a real regression because the
regression has not happened yet. the forced-scope probe
([test_pre_rule_refusal_tripwire.py](../../tests/quality_gates/test_pre_rule_refusal_tripwire.py))
forces the mutually-exclusive pair through `summarize` — reachable because
`summarize` is a pure function of the audited rows — and pins that the count
reaches 1 AND that the flag's exit path returns 1. The module docstring now says
the flag cannot return 1 *while that ordering holds*, and names the probe.

### Refuted `cannot-fire` claims

**11 of 14 `cannot-fire` claims were refuted by adversarial verification.** That
is the headline result of the verify stage and it is reported as such rather than
buried: a sweep whose surveyors' claims were taken at face value would have
reported roughly 14 findings, and 11 of them would have been wrong.

The refutations cluster into one shape worth recording. Most were rules in
shipped skill references citing `<repo-root>/scripts/<name>.py` paths that exist
only in the authoring repo, claimed `cannot-fire` (criterion 4) *in a consuming
repo*. Each verifier refuted by exhibiting a firing input **in the authoring
repo**. Both readings are defensible, and the verify stage was deliberately tuned
to refute on uncertainty, so the count resolves toward `can-fire`. **This is a
stated limitation of the measurement, not a hidden one** — see `## Non-Claims`.

## Counts

Denominator: the population table above, measured 2026-08-02 after Lane A's fold.
Assignment differs from the raw stratum counts because S2 was sliced by family
and S3 was reduced by the mandate filter recorded in `## Scope Call On S3`.

| stratum | assigned | read | unread | rules classified | `can-fire` | `not-a-rule` | `cannot-fire` claimed | confirmed after verify |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 rule-date constants | 12 files (17 constants) | 12 | 0 | 19 | 17 | 2 | 0 | 0 |
| S2a artifact validators | 37 | 37 | 0 | 32 | 28 | 1 | 3 | 1 |
| S2b `check_*` scripts | 53 | 53 | 0 | 58 | 55 | 2 | 1 | 0 |
| S2c skill-package scripts | 16 | 16 | 0 | 16 | 16 | 0 | 0 | 0 |
| S3a shared refs + conventions | 24 | 24 | 0 | 51 | 46 | 3 | 2 | 0 |
| S3b public-skill references | 55 | 30 | **25** | 25 | 13 | 4 | 8 | 0 |
| **total** | **197** | **172** | **25** | **201** | **175** | **12** | **14** | **1** |

- **172 of 197 assigned units were read (87%).** The 25 unread are all in S3b and
  are counted, never dropped — a reader can tell "checked and live" from "not
  checked", which is the distinction whose absence made four findings look like
  bad luck.
- "rules classified" exceeds "read" in several strata because one file carries
  several rules, and falls below it in S3b because unread files yield no rules.
- **`cannot-fire` after verification: 1 of 201 classified rules.** The honest
  reading is not "the codebase is clean" — it is that this predicate, applied at
  this depth, finds roughly one instance per two hundred rules, and that four
  previously-known instances were all found by people rather than by this method.

## Non-Claims

- This sweep does not claim the population is exhaustively READ. Whatever is not
  read is counted as `unread` against the stated denominator rather than omitted.
- This sweep is a one-off MEASUREMENT plus targeted repairs and dispositions. It
  is deliberately **not** a permanent meta-validator in CI: the north star names
  a validator that audits validators as the anti-pattern applied to itself.
- A `can-fire` verdict says a firing input exists. It does not say the rule is
  correct, well-scoped, or worth keeping.
- **The consuming-repo reading is under-measured.** The verify stage was tuned to
  refute on uncertainty, and most refuted claims were "inert in a consuming repo"
  claims refuted by a firing input in the AUTHORING repo. Those rules may still
  be inert where the skill is installed. This sweep does not settle them, and the
  count leans toward `can-fire` because of that tuning. Measuring it properly
  needs a consuming repo, which is not reachable from this tree.
- 25 S3b files are `unread`. Nothing is claimed about them.
- The counts come from surveyor agents plus adversarial verifiers, not from a
  deterministic tool. The one CONFIRMED finding was independently re-read by the
  parent before it was repaired; the refutations were not each re-read.

# Umbrella class disposition plan — #582, #583, #584, #585

Date: 2026-08-10. **REVISED 2026-08-11 after critique; still not executed.** This
document existed to be attacked before any deletion happened, and it was: five of the six
proposed deletions were refuted or mis-scoped. Read `## Dispositions — REVISED` as the
live plan; the sections above it are kept because the corrections are only legible
against what they correct.

## What this decides

The four umbrellas were verified on 2026-08-10 to be the only durable home of ten
defects, all of which read `CLOSED`/`NOT_PLANNED` — the `consolidated` disposition,
which claims nothing about the defect. Evidence:
[class-survival review](../audit/2026-08-10-umbrella-class-survival-review.md).

This plan disposes of each CLASS (not only each member instance), operator-directed,
with a deletion bias. The first draft claimed 13 items resolving 12 delete-or-rule to 1
build, and offered that ratio as a finding to distrust. **The critique found the ratio was
a labelling artifact and that the deletions it counted did not survive a grep.** Corrected
count and dispositions: `## Dispositions — REVISED`.

## The measure

`docs/design-north-star.md` governs. The load-bearing lines for this plan:

- **P1** — reversible work defaults to judgment; a gate/validator/rule there "bears
  the burden of showing why judgment alone fails."
- **P5** — "Teeth only for irreversibility and form. A gate may *force a question*; it
  may not *declare completion*."
- **The anti-pattern (`:100-103`)** — "What this does **not** license is a gate that
  checks gates. That is the anti-pattern named in the diagnosis above — meeting a
  gate-quality problem with another bespoke gate — applied to itself. The teeth here
  are a distinct observer and a scope a verdict must name, not another green."
- **The failure signature (`:122-124`)** — "you cited 'fewer lines / fewer gates' — or,
  inverted, *more* code / *more* gates as 'thoroughness' — as success; count is not the
  metric in either direction (escape-closed + concept-clearer is)."

So the test applied to every deletion below is **not** "is it less code" but: **does a
wrong pass here escape somewhere we do not control?** If yes, teeth stay (P5). If no,
teeth are friction on reversible work (P1) and go.

**The critique's verdict on this measure, which stands:** the first draft ran it on 5 of
13 items and silently used three different tests. Worse, the test as stated is arguably a
category error — it comes from the north star's *closeout-boundary* definition, and a
probe's job is not to stop an escape but to make a silent change observable. A probe with
no downstream actor still converts silence into a message; deleting it produces the
unbounded silence the same document calls the worst failure mode (`:84-90`). Any future
disposition pass must fix the stated test before applying it.

## Proposed north-star amendment — RESOLVED: adopted as TASTE, not as a facet

**Landed 2026-08-11 in `docs/design-north-star.md` under `## Taste`.** The operator
overruled the counterweight's rejection on a category argument that holds: the ladder is
**taste**, and a taste needs no observable predicate because it renders no verdicts — it
orders preferences among options that already pass the five facets. The source
([Tasteful software](https://wiki.g15e.com/pages/Tasteful%20software.md), gathered at
`../gather/2026-08-10-wiki-g15e-com-pages-tasteful-software-md-536ebc23.md`) frames it
exactly that way: taste is not innate, not finished, kept useful by unlearning, and its
job is choosing among many possibilities.

Three of the counterweight's four objections were therefore aimed at a gate that was
never proposed. The FOURTH survives and is written into the north star as the rule's own
guardrail: **the `at equal —` precondition is the rule.** This plan asserted equal
capability four times and was wrong four times, and those four failures are cited in the
north star by name so the next reader inherits the failure mode with the taste. Placement
is beside P1-P5, never as P6, because a preference order is a different kind of statement
than a principle with a measured failure behind it.

The text below is the input as the operator wrote it.

The current document says count is not the metric *in either direction* but gives no
tiebreak when two designs close the same escapes. The operator proposes this ladder.
It does not overturn the existing line — it applies only **at equal capability**, so
count never justifies itself; it only breaks a tie.

> **Capability, not count, is the metric — but at equal capability, prefer less.**
>
> 1. At equal **capabilities** (what can be done), fewer **features** is better.
>    Capability is possibility; a feature is one shipped path to it. More features at
>    the same capability is surface without reach.
> 2. At equal features, **less code** is better.
> 3. At equal code, a **higher share of open source** is better.
> 4. At equal code, **declarative** beats **procedural**.

Open questions this amendment leaves, which the critique should press:

- Rule 1 needs a worked example or it reads as a slogan; P3 demands "one sharp worked
  example plus the principle behind it." Which pair in this repo is the example?
- Rules 3 and 4 introduce axes the north star has never carried (dependency posture and
  code style). Are they facets of the one idea, or a second idea that belongs in a
  different document? A north star that accumulates axes stops being a north star.
- Rule 3 has an unstated cost: a dependency is an external surface whose failure is
  outside this repo's control — which the same document classes as *irreversible*.
  "Higher open-source share is better" and "an external write is irreversible" are in
  tension and the amendment does not resolve it.

## Dispositions — REVISED after critique

**Four angle reviewers plus a counterweight pass ran on the first draft
(`../critique/2026-08-11-umbrella-class-disposition-plan.md`). Five of the six proposed
deletions were refuted or mis-scoped.** The counterweight's summary is the honest
headline: "five of the six were checkable against source in minutes and four failed."
The original dispositions are kept as strikethrough context only where the reason
matters; everything below is the corrected disposition.

### The corrected count

Not 12 delete-or-rule against 1 build. **One clean deletion, one partial, four
rework-or-refuse, two builds, five rulings, one omitted item.** The first draft's
headline ratio was a labelling artifact: "delete-or-rule" absorbed IGNORE, RETIRE, and a
decision made before this plan existed, and one item carried no verb at all.

### REFUSED — the deletion premise was false

**`Premise-residue:` seam — KEEP.** `recount_residue_lib.py:63-67` says the marker is
human-authored *by design*: "a marker with no reason records a ritual, and the whole
point is that a human wrote down WHY." Zero markers means nothing was declared, not an
empty-input verdict. And the fail-open the draft cited was already repaired —
`recount_premise_lib.py:80-87` enumerates the four missing-evidence channels and states
that missing evidence resolves toward refusal. **This was the plan's highest-risk item:
a proof surface, deleted on a refuted premise, where the round-2 review safeguard
structurally cannot catch the error because a deleted surface presents nothing to
repair.**

**dup-ratchet identity arm — REFUSE.** There is no property arm to keep.
`dup_ratchet_lib.py:305` is `hard_block = bool(new_code or new_doc)`, both pure
set-differences at `:279-280`; `classify_reductions` at `:93-131` is the shrink
tolerance, not a blocking arm. The only count-shaped arm is `_boy_scout_arm`, keyed on a
hand-maintained `dup-review.json` ceiling and advisory unless stagnation ≥ K. Deleting
the identity arm would delete the ratchet and leave an advisory keyed on a hand-edited
number — verbatim the north-star failure signature at `:113-115`. Verified directly by
the parent.

### REWORK — right target, wrong operation

**boundary-bypass identity arm — RE-KEY, do not delete.** `count_increases` fires only
when a count *exceeds* baseline (`:132-139`), so removing one bypass and adding another
leaves every count identical and `ok: True`. `new_keys` is the only substitution
detector. The false block is real (a `git mv` changes `test_file` in `candidate_key()`
at `:25-26`), and the repo has a worked precedent for fixing exactly this without
deleting anything: `nose_fingerprint_lib.py:20` re-keyed on content, path-independent.
Also touches `build_baseline:93-99`, `load_baseline:114` (which *requires*
`candidate_keys`), `tests/test_boundary_bypass_ratchet.py:71`, and a
`plugins/charness/` baseline mirror.

**#561 equality pins — BLOCKED as written.** The escape test was not just unverified,
it was false. `tests/test_inventory_marker_rule_measurement.py:135` — "D47 now cites
these numbers, so they must not drift silently" — and `docs/deferred-decisions.md:685-703`
publishes 196/188/153/35/4-across-3 plus the full recursive set. D47 is an **open**
operator decision and the pin is what forces its refresh. Under north star `:69-71`
("it ships to an operator") this is on the irreversible side of the plan's own test.
Two further corrections: the draft said "3 refreshes recorded" when `:715` and `:721`
record a fourth and fifth, and the standing tax is tracked as **#536**, not D47's
question (`:711-714`) — so the draft also routed the decision to the wrong node.
Executable only paired with D47: either date-stamp or de-pin D47's published figures, or
keep the pins. Narrowing to the fields D47 does not quote is the most that is available
without an operator ruling on #536.

**#568 eval pair — PARTIAL, and the draft's premise was factually wrong.**
`pickup-ambiguous.spec.json` carries `requiredCommandFragments:
["continuation-sequence.md"]` — **not empty** — and is the ONLY `engage-always` forcer of
that reference. `claim_fidelity_lib.py:390-403` raises on any unwaived planner-forceable
ref, gate queued at `run-quality.sh:747`, and
`tests/quality_gates/test_scenario_conditional_reads.py:136` `unlink()`s that exact file
as its incident fixture, so the deletion would make that test *error*. Corrected
disposition: delete `pickup.spec.json` only (its floors genuinely are both empty), keep
`pickup-ambiguous.spec.json` as the forcing scenario, update the registry entry and the
fixture registry in the same commit. Separately, the draft's claim that the property is
"already held" by `tests/test_handoff_plan.py:442-472` conflates two observables: those
tests assert what the PLANNER emits; the eval asserted whether an agent actually opened
the reference. A unit test is not an eval.

**#531 — BUILD with corrected scope, and it is irreversible.** The draft's fix would
have shipped a new defect: the handoff artifact path is adapter-configurable
(`plan_handoff_run.py:108` reads `adapter["artifact_path"]`), so a hardcoded
`is_file("docs/handoff.md")` probe would silently suppress branch (1) in any consumer
repo with a non-default path — trading a harmless over-emission for a silent
under-emission. It must resolve the adapter path. And it is not P1 reversible work: the
hook is installed at user level against the released plugin copy
(`session_start_routing.py:10-16`), so it ships to operators and owes the
distinct-observer treatment.

### PROCEED

**`render_skill_routing.py` — delete the unused PARAMETER only.** The `listed_skill_ids`
payload key stays: `scripts/eval_setup.py:220-224` raises unless it is `[]`, and
`tests/quality_gates/test_setup_render_skill_routing.py:40` asserts it. The draft
conflated the dead argument with the live key. This is the one clean deletion in the
plan.

**`plan_quality_run.py:327` — constant `next_action` over branches already computed.**
Low stakes, agreed by every reviewer. Needs an actual verb, which the draft never gave it.

**#525 residual — BUILD.** Unchanged and unchallenged: external claims ship to operators,
the drift is silent, and a live instance already sits in the file
(`docs/readme-proof.md:36-42` forbids claim discovery while `:80-82` instructs running
it, and the gate passes either way). The build must ship its own acceptance check —
`specs/readme-proof.spec.md` is presence/row-shape only.

### RULINGS — each needs a named durable destination, or this repeats the laundering

**#569 — no new gate, but the justification is rewritten.** The draft's citation pointed
the wrong way: north star `:100-103` ends "the teeth here are a distinct observer **and a
scope a verdict must name**", and a fixture requirement is exactly a scope a verdict must
name. The honest ruling is *declined for cost*, not *the north star forbids it*. And the
fallback is misdescribed — `check_quality_tool_fixtures.py:112-115` returns 0 on an empty
fixture set and is not queued in `run-quality.sh`, so "leave it as the tamper-evidence
check it already is" describes a check that does not run. **File that fail-open;** the
two-line repair (empty set is a refusal) is cheaper than the rule that was declined.

**#524 — IGNORE, and the reason is cost, not unreality.** The draft's dismissal used
survivorship reasoning. One reviewer also noted a deletion was *available* here and not
taken — the repo owns a schema'd ladder beside the prose one — which is the sharpest
evidence that the draft's real bias was toward zero effort rather than toward deletion.
Recorded rather than acted on.

**#535 — IGNORE with a reopen trigger.** **#514 — record as already declined; not this
plan's item to dispose.** **#582 umbrella — RETIRE by ruling**, per its own body.

**#532 — do both.** The draft's reframe was convenient: a cost signal and a smaller read
set are not exclusive, and `_validate_gate_packets` mandating `cost_tier` while
`_validate_reads` requires only `path`/`why` means the repo already decided a cost signal
is worth mandating for the other packet type. "Unearned" is contradicted by the file's
own precedent.

### OMITTED from the first draft

**`.agents/quality-adapter.yaml:123-652`** — ~530 lines of hand-maintained prose sizing
~120 machine-checked numbers, named by the audit as #582's largest class instance. It is
the one instance where no deletion is available, and it did not survive the transfer into
a deletion-biased plan. Recorded; not sliced now.

## Sequencing — REVISED

0. **Establish a green baseline** before any edit, so a later red is attributable.
1. Record dispositions and their durable destinations. Every ruling names the file or
   issue it lands in — five of them had none in the first draft, which re-creates the
   laundering the audit diagnoses. #561's record routes to **#536**, not D47.
2. Re-split or re-state each member on GitHub. Open count will RISE.
3. The one clean deletion + `plan_quality_run.py:327`. Coverage substitution for the
   `pickup.spec.json` deletion lands in the SAME commit as the deletion.
4. Rework slice: re-key the boundary-bypass arm; #531 with the adapter path.
5. Build slice: #525 evidence-path resolution, with its own acceptance check.

**Mirror sync is mandatory** and the first draft omitted it: `session_start_routing`,
`boundary_bypass_ratchet_lib` + its baseline JSON, `recount_*_lib`, `render_skill_routing`,
and `dup_ratchet_lib` all have `plugins/charness/**` mirrors. This is
`mutate -> sync -> verify` from the implementation discipline, and skipping it blocks the
commit.

**Proof-surface second round:** the boundary-bypass re-key, #531, and the
`pickup.spec.json` deletion all change what a live gate decides. The first draft
mis-scoped this — it listed the seam and the probes (now not being touched) and omitted
the spec deletion, which it had classed as "removing a green that says nothing."

## Where this may be serving a preference rather than the evidence

The operator asked for a deletion bias and stated it as a principle. This plan returned
12 delete-or-rule against 1 build. A ratio that closely matched what was asked for is
the first thing a critique should distrust. Specific admissions:

1. **#569 is the weakest link.** I invoked "a gate that checks gates" to avoid building
   the rule. But P5 explicitly permits teeth "for irreversibility **and form**", and a
   fixture-presence check is arguably a *form* check — it does not adjudicate whether a
   test is correct, only whether it captured its input. If that reading holds, #569 is a
   legitimate ask and I dismissed it with a citation that does not reach it.
2. **#532's reframe is convenient.** "Delete the requirement, don't price it" is
   deletion-flavored and pleasing. But a cost signal has value independent of whether
   the read set shrinks, and the two are not exclusive. I may have converted a cheap
   additive fix into an open-ended refactor in order to report a deletion.
3. **#561's "nothing escapes" is asserted, not verified.** I did not check what consumes
   those probe counters. If anything downstream reads them as a drift detector, the
   claim is wrong and the pins are load-bearing.
4. **#524's dismissal uses survivorship reasoning.** "The consumer hand-mapped it and it
   worked" is evidence that the workaround was survivable, not that the problem is
   unreal. The 15-classes-collapsing-into-one datum arguably says the opposite.
5. **The north-star amendment was drafted by the party it favors.** I rendered the
   operator's four rules and then used a deletion bias to grade my own plan. The
   amendment should be judged on its own, by someone who is not spending it.

## Non-claims

Nothing here has been executed. No deletion has happened, no issue has been re-split, no
gate has been run against a proposed change. The class-survival evidence this plan rests
on came from four bounded reviewers with `Read`/`Grep`/`Glob` only — no gate execution,
no `git log`, no `gh` — so every "was reverted" or "predates" claim is read from in-repo
records rather than from history. The two live defect texts (#531, #532) were confirmed
directly by the parent against the files.

## What the critique should attack

1. Each deletion's escape test, individually. Which one closes an escape I claimed it
   does not?
2. The five admissions above — is each as bad as stated, worse, or actually fine?
3. The north-star amendment: does rule 1 have a worked example, do rules 3-4 belong in
   this document, and is the dependency/irreversibility tension real?
4. The plan's shape: is "delete or rule" the honest reading of the evidence, or the
   reading the operator asked for?
5. What this plan does not mention at all. An omitted item is invisible to every check
   above.

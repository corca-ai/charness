# Umbrella class disposition plan — #582, #583, #584, #585

Date: 2026-08-10. **PARTIALLY EXECUTED — see `## Execution status` below before
reading any section as pending.** Originally revised 2026-08-11 after critique. This
document existed to be attacked before any deletion happened, and it was: five of the six
proposed deletions were refuted or mis-scoped. Read `## Dispositions — REVISED` as the
live plan; the sections above it are kept because the corrections are only legible
against what they correct.

## Execution status

A blanket "still not executed" line sat at the top of this file for two commits after
part of it shipped, and on 2026-08-11 it cost a session a wrong claim to the operator:
the agent reported the pickup ruling as pending, having confirmed it against the
INSTALLED plugin copy (`~/.agents/src/charness`, release 4.2.0) instead of this repo's
source. Per-section status, not one banner:

| Section | Status |
| --- | --- |
| `# Operator ruling 2026-08-11: delete the pickup ambiguity heuristic and its evals` | **EXECUTED at `a24b0155`.** The planner heuristic, `next_session_entry_count`, `--pickup-target`, the `continuation-sequence.md` literal, both pickup eval specs, their registry entries, and the test-fixture re-key are all gone from source. The `workflow-trigger.md` classTag move landed with them. |
| `# Deletable-surfaces sweep`, `## Deletions that survive` items 1 and 3 | **EXECUTED at `c9b9e243`, `322664d5`, `50975458`** — the dead-code wrapper and the `candidate_key_count` enforcement drop. The second went through two bounded review rounds; round 1 found the subsumption proof rested on a generator property rather than the field's own definition. |
| `## Deletions that survive` item 2 | **HALF EXECUTED at `c9b9e243`.** The dead `refused_citation_count` branch is gone. The NARROW is deliberately NOT done: `#596` reserves it for the operator, and landing it here would execute an operator-reserved call under cover of a dead-code removal. |
| `## Candidates that died on inspection` | Re-verified 2026-08-11 by a nine-agent triage. All still dead, and now with the consumer greps that establish it rather than the reasons that were merely asserted. |
| `## Teeth without a cliff` | **NOT executed, and two of its premises were false.** It describes three candidates as `review-needed` rows in the 2026-07-04 gate-reclassification audit; all three are disposition **keep** there. That audit has exactly two `review-needed` rows: `check-links-external` and `inventory-ubiquitous-language` (the latter is `#598`). |
| Everything under `## Dispositions — REVISED` | Unchanged; still the live plan for what it covers. |

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

Not 12 delete-or-rule against 1 build. **ONE clean deletion (shipped), zero partials,
five rework-or-refuse, two builds, five rulings, one omitted item.** Six of six proposed
deletions were refuted; the survivor was an unused function parameter. The first draft's
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

**#568 eval pair — RETRACTED 2026-08-11. Do not delete either spec.**
The plan first proposed deleting both, then narrowed to `pickup.spec.json` after the
critique showed `pickup-ambiguous.spec.json` is the only `engage-always` forcer of
`continuation-sequence.md` (`claim_fidelity_lib.py:390-403`, gate at `run-quality.sh:747`,
and `tests/quality_gates/test_scenario_conditional_reads.py:136` `unlink()`s that exact
file as its incident fixture). Reading one more file before executing killed the
remainder: `evals/cautilus/handoff-claim-fidelity/outcome-assertions.json` records the
empty floor as a deliberate, capture-verified **floor MOVE**, not a collapse — "the
pickup.spec.json deterministic floor move (RCF `[workflow-trigger.md]` -> `[]` on this
substance floor) ... rides a fresh ask-before-run capture that VERIFIES this instrument
grades correctly." That judge set resolves as the sibling of the whole directory and is
written to hold for all four intents, so deleting the pickup scenario removes the only
registered pickup-intent vehicle for `pickup-starts-named-workflow` and
`trigger-fidelity-no-invention`.

So `#568`'s real residue is neither spec: it is that **no collapse detector exists**, and
that `pickup-ambiguous.spec.json:2` still carries an uncorrected draft comment while its
sibling carries the correction. Both are edits, not deletions.

**Six of six proposed deletions were refuted, and every one was answerable by reading a
file the plan had not opened.** That is the plan's single most durable finding.

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


---

# Deletable-surfaces sweep — 2026-08-11

Four bounded angle reviewers (zero-consumer hunt / duplicate-surface hunt / teeth-without-
a-cliff / re-examine-the-refutations). **No separate counterweight pass ran this round**,
so the classification below is the parent's, not a triangulated four-bin triage. Reviewer
boundary snapshot/verify: `clean`.

Every candidate below carries the grep that establishes its consumer set, because the
absence of that grep is what produced six wrong deletions.

## The refutation that was itself wrong

**`pickup.spec.json` — my refutation was wrong; the deletion is available.** Verified by
the parent, not taken on the reviewer's word:

- `scripts/claim_fidelity_lib.py:151` resolves the substance judge as
  `(repo_root / spec_path).parent / "outcome-assertions.json"` — **per DIRECTORY**, so it
  survives as long as any sibling spec remains.
- `pickup-ambiguous.spec.json` is also a pickup-intent scenario (`"resume from the current
  state and start the next workflow"`), and `outcome-assertions.json:15` keys the judge on
  *"resume/pickup wording"*, never on a filename.
- `pickup.spec.json` contributes **nothing** to the conditional-reads gate: its
  `engage-always` set is empty, and its lone `classTag: INLINE` on `workflow-trigger.md` is
  duplicated by `pickup-ambiguous.spec.json`.

**It is still not an at-equal-capability deletion, and so it is NOT recommended on the
taste rung.** Deleting it removes the CLEAR prompt variant
(`"resume the pinned task ... start the named workflow"`), leaving the judge assertions
gradable only through the AMBIGUOUS phrasing — which is the less common real-world case.
The trade is one lost observation against one fewer ask-before-run Cautilus scenario.
**Operator decision, recorded as open.**

The general lesson, in the reviewer's words: a refutation that proves *the proposer's
stated reason was wrong* is not a refutation that proves *the surface is load-bearing*.
Only the second blocks a deletion. Four of my six refutations were the second kind; this
one was the first.

## Deletions that survive (execute next session)

1. **`scripts/boundary_bypass_ratchet_lib.py:17` — drop `"candidate_key_count"` from
   `COUNT_FIELDS`.** `filtered_summary:80,87` computes it as exactly the number of
   non-exempt candidate keys, from the same filtered pass that `build_baseline:93,98-99`
   writes `candidate_keys` from. So `current > baseline` on that field implies
   `|current_keys| > |baseline_keys|` implies `new_keys` is non-empty: the arm **cannot
   fire without `new_keys` firing first**. Strictly subsumed, contributes nothing to `ok`
   at `:139`. Caveat to state in the commit: the implication holds only while the baseline
   `summary` is generated rather than hand-edited. The other four count fields are
   row-shaped, not key-shaped, and are NOT subsumed.
2. **`tests/test_inventory_marker_rule_measurement.py:189-195` — narrow the recursive pin
   to the fields D47 publishes, and delete the dead branch at `:190`.** Parent-verified:
   `recursive_variant` has no `refused_citation_count` key, so the count-only comparison
   the author wrote never executes and a full-list deep-equality on
   `citations_refused_by_the_marker_rule` runs instead — the exact opposite of what the
   shallow test does to the same field, for a reason the shallow test states at `:166-168`
   ("D47's headline figure is the CITATION count, not the artifact list"). The loop also
   deep-compares `rows` (~60 per-artifact entries), `pre_contract_citations_skipped`,
   `corpus`, and `recursive`, **none of which D47 publishes**. Narrowing therefore does
   NOT touch the open operator decision and does not wait on `#596`; it removes the
   largest slice of the standing corpus-write tax.
3. **`skills/public/quality/scripts/run_dead_code_advisory.py:100-101` —
   `_dataclass_field_locations` is a pass-through wrapper.** Production reaches dataclass
   fields via `_source_roles.source_role_locations` at `:167`, never through this. Only
   consumer is `tests/quality_gates/test_quality_dead_code_advisory.py:762-764`, whose
   three assertions repoint at `source_role_evidence.dataclass_field_locations` without
   loss. **CORRECTED 2026-08-11:** that repoint target was itself a pass-through with no
   production caller, so following this instruction would have moved the same defect down
   one module. As executed, BOTH pass-throughs are deleted and the assertions repoint at
   `source_role_locations`, where production reads it, checking the whole returned dict
   instead of one of its three keys. Mirror sync required.

## Candidates that died on inspection (do not re-propose)

- **The two proof ladders are not the same ladder.** The prose one has zero machine
  readers but **eight live skill-prose consumers**; the schema'd one
  (`scripts/proof_semantics_adapter_lib.py:1-31`) is domain-blind by design and has no
  levels of its own to give. `#524` is "the prose ladder has no schema", not "there are
  two ladders".
- **`resolve_adapter.py` copies are schemas, not copies** (30 to 389 lines), and the
  extractable half was already extracted — `charness-artifacts/quality/2026-06-30-dup-portability-falsification-audit.md:29-32`
  records the CLI tail moving into `SKILL_RUNTIME.run_adapter_cli` across 16 skills with
  byte-identical proof.
- **`check_title_slug_drift` shim** — parent checked `git show v4.0.0`: the shim IS present
  at that tag, so the installed-caller compatibility argument transfers and the candidate
  dies honestly.
- **`boundary-bypass-baseline.json`** — all 59 candidate-key subjects exist; no stale
  entries. **`validate_scenario_conditional_reads.allowlist.txt`** — its one entry's
  subject exists.
- **`dup-review.json`** — a ~60-entry sample of the `intentional` classifications found
  none worth overturning.

## Teeth without a cliff — and a five-week-old unaddressed audit

The repo already has `charness-artifacts/audit/2026-07-04-gate-reclassification.md`, which
classifies every wired gate irreversible / reversible / form. **Two of the findings below
are that audit's own `review-needed` rows, still unaddressed.**

- **`inventory-ubiquitous-language` blocks unconditionally**
  (`skills/public/quality/scripts/inventory_ubiquitous_language.py:431`, queued at
  `scripts/run-quality.sh:985`). Every sibling `inventory-*` gate is advisory or blocks
  only behind an explicit caller flag; this is the sole exception. A wrong pass leaks a
  word preference in markdown prose. **Split the arms:** `findings` should move behind a
  `--require-empty`-style opt-in like its six siblings; `scope_findings` (`:313-320` —
  declared globs matched no file, so a clean result establishes nothing) is a fail-open
  detector for the gate's own scope and **keeps its teeth**.
- **`check-references-link-inventory`** (`scripts/check_references_link_inventory.py:143-154`,
  and in the pre-push docs-only subset at `.githooks/pre-push:66`, so it can block a push
  alone) enforces bullet SHAPE inside `## References` sections. Nothing consumes the
  section; `check-doc-links` / `check-plugin-doc-links` / `check-markdown` already hold
  everything that resolves or renders. Recorded cost:
  `charness-artifacts/retro/2026-08-06-session-retro.md:263` records it firing on a
  wrapped bullet.
- **`check-timing-layer-completeness`, `missing` arm only**
  (`scripts/check_timing_layer_completeness.py:161-174`): a gate label lacking a row in a
  docs table. This is the closest thing in the tree to the shape the north star does not
  license (`:100-103`, a gate that checks gates). Its `stale` arm (`:176-186`) catches a
  docs-only push reporting a clean pass while queueing one fewer gate — **real teeth,
  keep**.
- **`check-markdown` at the commit boundary** (`scripts/staged_commit_gate_plan.py:346-347`)
  lints every tracked markdown file in the repo on any staged `.md`, and the identical
  whole-repo command runs again at pre-push and again in CI. The same file already demoted
  its `check_markdown_inline_code` half to WARN citing P1 by name.
- **Two more exact-count pins of the `#561` shape:**
  `tests/quality_gates/test_adapter_key_warn_tier.py:292-294` (`== 16`, `== 3`, `== 37` over
  a live corpus — adding one `adapter.example.yaml` reds all three) and
  `tests/quality_gates/test_quality_run_planner.py:387` (`== 35` derived straight from
  `catalog.yaml`). For the first, a prior `>= 15` threshold was already refuted in review
  because dropping a whole glob still left 16 — so the invariant wanted is per-family
  NON-EMPTINESS, not a threshold and not a total.

## What none of this establishes

No gate was executed by a reviewer and no reviewer could read history; every claim above
is a reading of the current worktree. The parent separately verified, through channels the
reviewers lacked: the pickup spec engagement sets, `claim_fidelity_lib.py:151`, the absent
`refused_citation_count` key, and `git show v4.0.0` for the shim. Nothing in this sweep has
been executed.


---

# Operator ruling 2026-08-11: delete the pickup ambiguity heuristic and its evals

**Ruling:** the pickup ambiguity decision is skill BEHAVIOR. Prose governs it and Cautilus
verifies it. A planner heuristic that guesses it from artifact text is the wrong shape and
comes out.

## Why the ruling is stronger than the argument that produced it

The operator objected to "an ambiguous regex doing FP/FN". The current mechanism is one
step past a regex and the objection lands harder for it:
`plan_handoff_run.py:161-170` decides ambiguity from `pickup_target.strip()` plus
`next_session_entry_count >= 2`, and that count comes from
`chunked_routing_lib.parse_handoff_entries(raw)` (`:129`) — **a prose parser counting
markdown entries under `## Next Session`.** Renumber the handoff, wrap a bullet, or split
one item into two, and the planner's verdict about the OPERATOR's intent changes.

**The repo already accepted this reasoning and stopped one step short.** The regex
classifier `should_fire_chunker` was deleted for exactly this, and `_resolve_intent`'s
docstring (`:172-175`) states the principle: *"Resolve routing from what the caller
DECLARED, never from the invocation text. Python is not in the conversation, so a
classifier here could only ever read..."*. Intent got the treatment; ambiguity did not,
because it counts prose instead of matching it.

## Scope — verified consumer sets, so the next session does not rediscover them

Delete:

- `_pickup_needs_continuation_sequence` (`:161-170`) and its call at `:278`, plus the
  `pickup_skip_continuation` branch at `:284-287`.
- `next_session_entry_count` (`:126-131`, `:157`). **Verified: its only functional consumer
  is that predicate**; the sole other reference is one edge-case assertion at
  `tests/test_handoff_plan.py:490`.
- `--pickup-target` (`:234`, `:369`, `:383`, `:425`, `:434`). **Verified: its only consumer
  is the same predicate**, plus `skills/public/handoff/SKILL.md:39` prose and two tests.
- The four discriminating tests, `tests/test_handoff_plan.py:442-472`.
- Both eval specs, their `evals/cautilus/claim-fidelity-registry.json` entries, and the
  fixture registration in `tests/quality_gates/test_scenario_conditional_reads.py:139-159`.

**The load-bearing edge, and the reason both specs become deletable as a CONSEQUENCE
rather than as a separate argument:** `_handoff_planner_forceable`
(`scripts/claim_fidelity_lib.py:283-301`) AST-scans the planner for **any** string literal
matching `references/<name>.md`, *regardless of branch*. So deleting the branch is not
enough — `continuation-sequence.md` stays in the forceable set while the literal survives
at `plan_handoff_run.py:28`. **That literal must go too.** Once it does,
`continuation-sequence.md` leaves the forceable set, `would_need_waiver` shrinks, and
`pickup-ambiguous.spec.json`'s `engage-always` coverage stops being load-bearing — which
dissolves the single refutation that has blocked this cluster all session, without
appealing to any of the six.

`references/continuation-sequence.md` itself STAYS. It becomes ordinary skill prose the
agent opens by judgment, which is the ruling.

## What must be preserved

The substance judge. `evals/cautilus/handoff-claim-fidelity/outcome-assertions.json`
resolves per directory and its assertions grade the behavior that actually matters —
started the artifact-named workflow, verified live state through a channel other than the
handoff text, did not invent a trigger. Deleting the two spec files must not orphan it:
either `spec.json` / `refresh.spec.json` remain as its vehicles (they do), or the ruling
loses the only thing verifying the behavior it says Cautilus should verify.

## The class this points at — the larger prize

The operator's stronger claim is that there are many of these. Three same-shape candidates,
recorded for a later sweep and NOT yet checked for consumers:

- `skills/public/setup/scripts/setup_skill_routing_lib.py` —
  `agents_skill_routing_semantically_complete` decides by regex whether a **consumer's**
  AGENTS.md prose means the right thing. Same shape, and its wrong answer ships outward.
- `skills/public/handoff/scripts/chunked_routing_parser.py` — 11 regexes parsing handoff
  prose into entries; the source of the count above, so the same family.
- `scripts/classify_push_diff_lib.py` — 11 regexes classifying a diff into a category that
  drives behavior.

The discriminator for the sweep is NOT "does it use a regex". Form validators
(`validate_skills.py`, `check_doc_links.py`) legitimately match shape. The question is
**does a pattern-match decide what an agent or operator MEANT** — and if so, the declared
route should replace it, exactly as `--intent` replaced `should_fire_chunker`.


---

# Observation run 2026-08-11 — the next session was actually run, headless

`claude -p "handoff"`, Opus 5 / medium effort, in an isolated `git worktree` at `369f6d7b`
so nothing could touch the real tree. 82 turns, 7m18s, $5.40. Full diff preserved at
`charness-artifacts/audit/2026-08-11-pickup-deletion-experiment.patch`.

The question was whether this session's lessons transfer through the harness without the
operator restating them. Two hypotheses, both measured from the tool-call trace.

**H1 — does it read `recent-lessons.md` before acting? YES.** Tool calls 4-5, before
touching item 1 and before any edit.

**H2 — does it propose a removal without searching for what reads it? NO — it searched.**
It read `claim_fidelity_lib.py:270-310` (the AST-scan extractor), all four eval specs, the
allowlist, the registry, and `test_scenario_conditional_reads.py`, and ran a combined grep
over `pickup-ambiguous` / `pickup.spec.json` / `pickup_target` before editing. It VERIFIED
the recorded consumer sets rather than trusting them, which is the behavior the seven
failures were about.

**It also found a hole in the consumer sets this plan calls "verified".**
`workflow-trigger.md` carried `classTag: INLINE` in the two specs being deleted **and
nowhere else**, while remaining planner-forceable through the `judge_from_user_request`
intent (`plan_handoff_run.py:48`). Deleting both specs without moving the tag reddens the
conditional-reads cross-check. My scope check saw both specs carrying the tag and concluded
the sibling covered it — but both siblings were on the delete list. The run moved the tag
onto `spec.json` and `refresh.spec.json` with the reason recorded inline, and flagged it as
"a consequence the deletion ruling did not name."

**It stopped honestly instead of claiming done.** `python3` and most `git` invocations
returned "This command requires approval" under `--permission-mode acceptEdits`, so it
could not run `sync_root_plugin_manifests.py`, pytest, or the gate. It reported the tree as
inconsistent and unverified, refused to hand-mirror ("unverifiable hand-mirroring is how
drift gets committed"), and named what it still owed: the mirror sync, the gates, and the
two-round bounded review this proof-surface change carries.

## What this settles about the harness thesis

The lessons transferred — **but not through the surface built for them.**
`recent-lessons.md`'s four trap slots dropped this session's two sharpest lessons on a
recency+recurrence ranking, and the run's correct behavior traces instead to the handoff's
explicit first line and to the consumer greps recorded in THIS artifact. So the memory
digest is lossy and the handoff plus the spec artifact did the work. That is a narrow,
actionable result: invest in the handoff/spec channel, and either give the digest a way for
a session to mark a lesson decisive or stop treating it as the memory surface.

One genuine harness defect the run exposed on its own: **a headless pickup cannot reach its
own stop gate.** The repo's contract says code written is not a stop state, and the default
permission posture blocks the very commands the contract requires. Any autonomous run of
this repo hits that wall.

## Consequence for the next session

The `workflow-trigger.md` classTag move is now a NAMED part of item 1's scope rather than a
discovery. The patch is evidence, not a shortcut: it was produced without a mirror sync,
without a test run, and without the review the change owes, so the next session re-does the
work under verification rather than applying it.

# Achieve Goal: Gate by property, not by enumeration

Status: active
Created: 2026-08-23
Activation: `/goal @charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: slice 4 complete. All four slices are done; the goal is ready
  for closeout (retro, then the granted push and CI observation). Slices 1 and 2 are complete (`3a5da4a59`,
  `0552d40b1`, `332077310`). Slice 3's two-round cap is consumed; its round-2
  repairs are recorded as accepted-unreviewed.
- Next action: slice 4 (make the remaining surfaces name their uncovered set),
  plus two open operator decisions — whether the approval covered EXECUTING a
  `recommend-removal`, and the standing CI re-verification item.
- **Standing correction carried out of slice 3: `## User Acceptance` bullet 3 is
  OPEN.** No `derive` has landed in this goal. Do not read slice 3 as having
  discharged it.
- Slice 3 objective and expected evidence, stated before the work: replace the
  consumer-validator catalog's POSITIONAL discovery predicate with a structural
  one, and make the catalog report what its predicate did not admit.
  - Measured first, before designing: 833 packaged `.py`; 135 match the
    `check_*`/`validate_*` PREFIX; 377 carry a `__main__` guard. So the
    reviewer-proposed property "packaged Python with a validator entry point"
    does NOT separate the population — it would nearly triple the decision count.
    Rejected on that measurement rather than on taste.
  - The defect is POSITIONAL, not the token set: matching the same two tokens
    ANYWHERE in the basename instead of only at the front adds exactly ONE
    candidate, and it is the live miss
    (`skills/issue/scripts/issue_validate_closeout_draft.py`). This is the same
    shape as the frozen `bar-recorded-as-prose` lesson: prefer a structural,
    positional property over a longer token list.
  - Correction, caught by the gate itself during implementation: the
    reconnaissance above was measured with the regex `(check|validate)` while the
    predicate uses the tokens `check_`/`validate_`. Under the implemented
    predicate `scripts/worktree_doctor_checks.py` ("checks", no underscore) is NOT
    a candidate, so the delta is one file rather than two. The catalog header
    check refused the entry I had added for it. Recorded because measuring with a
    looser pattern than the one being shipped is exactly how a scope claim drifts
    from the code that implements it.
  - What this deliberately does NOT solve, and why the second half exists: a
    validator named with none of these tokens still escapes. Measured exposure if
    the token list were widened instead — `audit` 11, `guard` 9, `lint` 4,
    `verify` 3, `assert` 1, `enforce` 1. Growing the list is the disease. So the
    catalog will instead REPORT its predicate and the count it did not admit, and
    a green stops meaning "everything was checked".
  - Expected evidence: a capability-equality replay proving every currently
    discovered path is still discovered; a negative control; a wired-path test;
    and the uncovered count present in the report.
  - **Public-skill validation decision (recorded so the closeout ack is
    grounded, not waved through).** The slice edits
    `skills/public/quality/references/consumer-validator-catalog.yaml`, a
    prompt-affecting surface of the `quality` skill, so `run_slice_closeout.py`
    blocked for a validation review. Decision: **no dogfood freeze and no
    Cautilus run.** Evidence — the diff adds exactly one entry, and it is
    `consumer_facing: false`; no `consumer_facing: true` entry is touched; the
    consumer-facing set stays at 14 with the same ids and paths. The `quality`
    skill's consumer contract is therefore unchanged. What changed is an INTERNAL
    discovery predicate plus three additive report fields, and the checker itself
    is a declared scanner exclusion rather than a shipped consumer validator.
    Cautilus stays unrun per repo policy (eval-only, ask-before-run); this slice
    makes no live-behaviour claim that would need it.
- Current slice intent: both slices 1 and 2 are discharged. Slice 1 made an
  unmeasured mutation run say so on all three routes into that state and repaired
  the red baseline's cause; slice 2 produced the disposition record and had its
  first cut falsified. Once a new slice starts, this names the reviewable-intent
  unit in progress and the commits it spans; critique and broad proof do not
  re-fire within one unchanged intent — update it when the intent changes, not
  per commit (meaningful-slice-cadence).
- **Method note, now carrying two lessons and worth reading before slice 3.**
  Classify what a surface does IN THE TREE, not what a summary says it does — and
  that applies to the surface's OWN comments, not only to the predecessor retro.
  Slice 2's first cut graded seven gates on their self-description and was
  falsified twice over; this repo's comments are rich and self-critical enough
  that reading them feels like review when it is not. Run the surface.
- Frozen target at activation: `5bd571166d0f3b8c84b9a758b246b1d811e6adbe`.
- Next action: operator decision on slice 2's plan redirect (queued). Slice 3's
  conversion target moved to the consumer-validator catalog's discovery
  predicate; slice 4 is reinstated. Neither starts before that decision.
- Standing non-claim for this goal: no CI run has been observed after slice 1.
  The mutation lane is NOT known to be green, and slice 1's repair is necessary
  but not proven sufficient — a second, uncharacterized failure mode (the
  08-19/08-20 cancellations) is still live.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Stop gating by enumeration. Every gate in this repo that asks to be extended
with a new list entry is a gate that will silently stop covering something, and
this repo has at least seven of them.

The evidence is one session. Six times, the answer to a red gate was "add your
new thing to a hand-maintained list": a skill-ownership allowlist, a
consumer-validator catalog entry, a validator-count pin, three duplicate-family
classifications, a link-only-line bar, and a runtime budget. Each cost a round
trip and none made the next instance safer. In the same session a fresh-eye
round charged the same disease on a classifier written that day: a hand-kept
prefix list plus "`.md` means narrative" put a rolling gate-input pointer in the
advisory scope. The repair that held was a PROPERTY -- a dated filename stem --
not a longer list.

The clearest specimen is the validator-count pin. The assertion above it already
states the real property, that every packaged validator carries a decision. The
count proves nothing further and summons a human every time the population
changes.

This is the same root as the issues already filed about verification that stops
verifying. A whitelist is the most common way a gate stops covering, because
nothing fails when the list falls behind -- the gate stays green and the new
instance is simply outside it.

**North-star reading (the design frame for this goal).** This is not a cleanup
preference; it is two facets of the standard, and the standard also says where
to stop.

- P3, *principle over rulebook*: "an enumerated `do not X` list rots and still
  misses the case it never listed." That is a verbatim description of the six
  round trips. So the default disposition for an enumeration is: name the
  property it approximates.
- P3's own **exception** is load-bearing here and is why this goal is not a
  delete sweep: "at an irreversible boundary, the list of irreducible
  observables **is** the contract." Some of the seven are that list. Converting
  one of those would be the failure, not the fix.
- P5, *no terminal green*: "A gate may force a question; it may not declare
  completion." An enumerated gate whose list has fallen behind declares
  completion over a population it never read. That is the defect, stated in the
  standard's own words, and it is why the acceptance below is about **removing
  the ambiguity of green**, not about shortening lists.
- P5's named anti-pattern bounds the remedy: "What this does not license is a
  gate that checks gates." A meta-gate enumerating this repo's enumerations
  would be this goal's own disease, one level up. Every disposition here lands
  inside the gate that owns the list, or nowhere.

Three anchors, in order of what they buy:

- The mutation harness has not produced a verdict on `main` since 2026-08-19.
  Confirmed on the latest scheduled run (2026-08-22, `f5211700a`, run
  `32573073322`): `Select mutation sample` **failure**, `Run mutation`
  **skipped**, `Summarize mutation report` **failure**. So the honest reading of
  every green since then is "unmeasured", not "passed". Coverage of the mutation
  surface is the floor other proofs stand on.

  **Corrected at activation, twice, and the second correction matters more than
  the first.** This draft said the sampler "times out"; the 08-22 run shows it
  completing the standing suite in 1184.59s and refusing on `8 failed`. But
  narrowing the cause to that was ALSO wrong: a fresh-eye round pointed out that
  `scripts/command_plan_preflight.py` — whose eight failures those are — did not
  exist before 2026-08-21 (`365aa4b21`), so it cannot explain the 08-19 or 08-20
  runs. Checked: those were **cancelled** at `Select mutation sample` (the 08-19
  run after 28 minutes, under a 180-minute job timeout and with
  `cancel-in-progress: false`, so neither the job timeout nor concurrency
  explains it). There are therefore at least TWO failure modes in the window, and
  the one this goal repairs is the later one. The earlier cancellations are
  uncharacterized and still live. Necessary, not proven sufficient — recorded so
  a later session does not read a green mutation run as proof that both were
  fixed.
- A check that passes its own direct-call test while never firing on the wired
  path (issue #586). Hit three times in one session, twice in the same file.
  This one is not only an anchor, it is a constraint on every conversion below:
  a derived property tested only by direct call reproduces the exact defect.
- A budgeted runtime label with no sample reads as an enforced bar when it is
  unenforceable.

The goal is not to delete the lists. It is to make each one either derive its
scope, or fail closed when it falls behind, or say out loud what it is not
covering -- so that "green" stops being ambiguous between "checked" and "not
looked at".

## Non-Goals

- NOT deleting the lists. Some enumerations are the honest shape — a refusal
  vocabulary, an enum of allowed skip reasons. The target is the ones that
  approximate a property nobody wrote down.
- NOT converting a list that IS the irreducible-observable contract at an
  irreversible boundary. That is P3's stated exception, and the `contract`
  disposition below exists to record it as a decision rather than an oversight.
- NOT building a gate that checks gates. P5 names that as the anti-pattern this
  repo already paid for. No new surface may take "the repo's enumerations" as
  its input; a disposition that can only be enforced that way is downgraded, not
  built.
- NOT deleting a gate on P1 grounds during this run. Where an enumeration guards
  a reversible surface and judgment would carry it, this goal RECOMMENDS removal
  through `## Operator Decision Queue` and does not execute it. Removal
  contradicts the first non-goal above, and the taste ladder's `at equal
  capability` precondition is exactly what an agent asserting it gets wrong.
- NOT a sweep of all seven's implementations at once. Each is a proof surface;
  the point is a demonstrated pattern plus the two or three that buy the most,
  not a mass rewrite reviewed by nobody. Slice 2 classifies all seven on paper —
  that is a decision record, not a rewrite, and it is what keeps slice 3 from
  converting a `contract` list by accident.
- NOT closing the open issues this touches. Fixing a defect is not the per-issue
  closeout floor.
- NOT pushing, and NOT claiming that any change here WORKS on CI. The operator
  scoped this activation to local reproduction and honest signal only. Narrowed
  after a round-2 reviewer found the earlier wording ("NOT claiming anything
  about CI behaviour from an observed run") in tension with the slice's own
  shipped comments, which cite five run IDs. Reading CI history as DIAGNOSTIC
  INPUT is in scope and is how slice 1's premise was corrected twice; asserting
  post-change CI behaviour is not, and is asserted nowhere.

## Boundaries

### The disposition taxonomy (the decision procedure this goal adds)

Every enumeration this goal touches gets exactly ONE recorded disposition. The
taxonomy is derived from the north star, not invented: `contract` is P3's
exception, `derive` is P3's default, `declare-uncovered` is P5's "force a
question, do not declare completion", and `recommend-removal` is P1 held back to
an operator call.

- `derive` — the list approximates a property that is machine-derivable from the
  tree. Convert. Owes a capability-equality replay, a negative control, and a
  wired-path test.
- `contract` — the list IS the set of irreducible observables at an irreversible
  boundary. Keep verbatim. Owes only the classification record and its reason.
- `fail-closed` — the property is contested or not derivable, but the list
  falling behind IS detectable. Keep the list; add the refusal that fires when
  the population it covers moves.
- `declare-uncovered` — neither derivable nor detectable-when-stale. Keep the
  list; make the gate name its uncovered set, as a number, in its OWN output, so
  its green stops meaning "checked".
- `recommend-removal` — a P1 reversible-surface gate judgment could carry.
  Recorded to `## Operator Decision Queue`; not executed here **unless the
  operator explicitly approves that instance, which must then be recorded as an
  exception with the approval text quoted.** The escape hatch is written down
  because slice 3 used one before it existed: it removed the
  `packaged_validator_count == 134` pin, and a round-2 reviewer correctly charged
  that against this rule and against the matching Non-Goal. The one contested
  instance is queued in `## Operator Decision Queue`; a reader should treat an
  unrecorded execution as a violation, not as precedent.

### Constraints on the conversions

- **Capability equality is proven by replay, not asserted.** Before a `derive`
  lands, every entry currently in the list must be replayed against the property
  and produce the same verdict, and any divergence must be named as a deliberate
  scope change with its reason. A `derive` that cannot replay its current
  population is downgraded to `fail-closed`. This is the taste ladder's `at
  equal —` precondition, which the north star records being asserted wrongly
  four times in a row on 2026-08-11, each time reading as a tie while reducing
  capability.
- **Reachability, not just coverage** (issue #586). Every converted property is
  tested through the wired surface an operator invokes, never only by direct
  call. The changed-line mutation gate does not catch this class: those lines
  were covered — by the direct-call test.
- Changing a gate's scope changes what it refuses. Every change here needs a
  negative control — removing the defect must flip the verdict — because a gate
  that stops refusing is exactly the failure under study.
- **P4 needs two things, and one does not substitute for the other.** The
  negative control is the distinct *evidence channel* (behavioural: the verdict
  flips when the defect is planted). The bounded reviewer is the distinct
  *observer*. The north star is explicit that a proof surface's own author and
  its own tests are one observer, and that a large suite is not many independent
  observations along this axis.
- Two-round bounded review applies to every slice here: all of them change
  verdict logic on a proof surface, so round 2 reads the REPAIRS. Cap is two;
  round-2 repairs are recorded as accepted-unreviewed.
- Reviewers are spawned unnamed and read-only, in the shared parent worktree,
  with `reviewer_boundary_fingerprint.py` snapshot/verify around each round. A
  failed verify quarantines that round's approvals.

### Stop conditions

- Stop and report if the mutation sampler's slow phase cannot be identified from
  two local runs; the honest-signal half of slice 1 does not depend on finding it
  and ships regardless.
- Stop before converting any enumeration whose slice-2 disposition is `contract`
  or that fails its capability-equality replay.
- Stop at `blocked` rather than pushing, opening a PR, or reading a CI run: this
  activation's external-boundary grant covers neither.

### Proof cost and duplication pressure

- Slice 1: one or two local sampler runs, each in the multi-minute range. This is
  the most expensive proof in the goal and it is bounded to two runs.
- Slices 3 and 4 add tests (replay, negative control, wired-path, staleness
  detection) and will push the broad duplicate/length/pressure gates toward their
  thresholds. Each of those slices takes a cheap `test-pressure` duplicate sample
  when it adds tests, and classifies any broad-gate failure as new-slice-local
  versus accumulated suite debt before repairing it.

## User Acceptance

- A green from the mutation harness can no longer be confused with an unrun one:
  either the local reproduction produces a verdict, or the harness reports
  UNMEASURED coverage distinguishably from both "passed" and "step failed". The
  operator can read this from the harness's own output without inspecting CI.
- Every one of the seven named enumerations carries a recorded disposition from
  the taxonomy, with the reason and the property (or the observable contract) it
  encodes — so a later session can see which were considered and kept, not just
  which were changed.
- At least one enumeration is converted to a derived property, with its
  capability-equality replay, its negative control, and a test through the wired
  surface. **STATUS: OPEN. Slice 3 did not discharge this and must not be read as
  having done so.** Slice 3 dropped a positional constraint from an enumeration
  over an unchanged token pair; no property replaced a list. A round-2 reviewer
  named the overclaim and it is adopted here rather than argued with. Slice 3's
  real contribution is a bug fix (a live validator was outside the catalog) plus
  the `declare-uncovered` half. Whether any of the seven admits a genuine
  `derive` is now itself open — row 6 is the only one that already did, and it
  was built that way before this goal existed.
- Every enumeration left in place is either fail-closed when its list falls
  behind, or names in its own output what it is not covering — so a green from it
  is no longer ambiguous between "checked" and "never looked".
- No new surface was added that takes other gates' VERDICTS, or the repo's
  enumerations, as its input. The wording is deliberate and was tightened after a
  round-2 reviewer showed the earlier phrasing ("takes other gates as its input")
  was literally violated by this goal's own slice 1: a test that reads workflow
  FILES and asserts a binary is installed before the step that needs it. The
  worked boundary example, recorded so a later session does not have to re-derive
  it — reading a gate's *provisioning precondition* out of the only file that
  states it is a fact about the environment; reading a gate's *green* and
  re-certifying it is the P5 anti-pattern. The first is allowed, the second is
  not.

## Agent Verification Plan

### Low-Cost Checks

- Per commit: the focused tests for the changed surface, plus the repo's
  changed-line proof before any broad gate (a passing broad suite cannot prove
  changed-line ownership).
- Per conversion: the capability-equality replay, run as a test, enumerating the
  list's current population and asserting the property agrees on every entry.
- Per conversion: a negative control test that plants the defect and asserts the
  verdict flips.
- Per conversion: a wired-path test that reaches the check through the operator
  entry point, not by direct call.
- Per unconverted gate: a test that an entry falling behind is DETECTED, not
  silently tolerated.

### High-Confidence Checks

- Two bounded fresh-eye rounds per slice, unnamed and read-only, with a boundary
  fingerprint around each; round 2 reads the repairs.
- Broad proof at the slice boundary, not per commit.
- The final quality gate or a documented substitute at closeout.

### External Or Live Proof

- Out of scope by operator grant. The mutation harness runs in CI; this goal's
  evidence is a local reproduction only. Any statement about CI behaviour is
  recorded as inference, and re-verifying on CI is deferred to
  `## Operator Decision Queue`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Make the mutation harness distinguish unmeasured from passed, and reproduce the sampler failure locally | Every other proof stands on it, and it has produced no verdict since 2026-08-19 | A local run naming the failing/slow phase; a harness change so a skipped `Run mutation` reports unmeasured coverage rather than reading as a step failure; a negative control; two bounded rounds | done — `3a5da4a59` plus round-2 repairs; evidence in `## Slice Log` |
| 2 | Classify all seven enumerations with the disposition taxonomy | Converting before classifying is how a `contract` list gets destroyed; P3's exception is real | A per-enumeration record: file and line, current list, the property it approximates or the observable contract it IS, disposition, reason | done — record in `## Enumeration Dispositions`; first cut falsified by two reviewers and rewritten; plan redirect queued for the operator |
| 3 | Convert the `derive` set — target redirected by slice 2 and approved | Slice 2 showed the original two targets had no derivable property; the catalog's scan predicate had a live miss | Predicate widened, live miss brought into scope, `uncovered_module_count` published, capability replay + four negative controls + wired-path test, two bounded rounds | done — **but NOT a `derive`**; see `## User Acceptance`, which stays OPEN |
| 4 | Give the `fail-closed` and `declare-uncovered` remainder their uncovered-set report | A green that cannot distinguish checked from unlooked is the root defect | Each remaining gate reports its uncovered set as a number in its own output | done — four surfaces; one blocker and ~a dozen should-fixes folded from three bounded reviewers |

## Enumeration Dispositions

Slice 2's decision record. Each of the seven read in the tree as it stands, not
from the predecessor retro's one-line description of it.

**This section's first cut claimed "ZERO of the seven silently under-cover, all
seven fail closed", and two bounded reviewers falsified it. The claim is
WITHDRAWN.** It is kept visible here rather than quietly rewritten, because how
it failed is the most useful thing slice 2 produced.

**The corrected finding, which is sharper than the thesis it was meant to test:
the enumeration that rots is not the allowlist — it is the SCAN.** All seven do
fail closed *over the population their scan admits*. But four of the seven reach
their list through a discovery predicate that is itself a hand-shaped
enumeration, and none of those four names its unscanned set. A new instance the
scan never reaches never becomes a candidate, the list is never consulted, and
the gate is green with nothing said. That is the goal's original thesis, holding
exactly one level below where the first cut looked.

Three live instances in the tree today, each verified by running the surface, not
by reading it:

- `skills/public/setup/scripts/templates/t_events_adapter.yaml:7` carries a
  `charness-artifacts/spec/` mention — a `setup:artifact:spec` cross-namespace
  overlap with no allowlist entry. `check_skill_ownership_overlap.py` reports
  `findings: []`, `status: ok`, `scanned_skills: 20`. Its scan reads `SKILL.md`
  plus a NON-recursive `iterdir()` over `scripts/` and `references/`, filtered to
  `.py`/`.md`, so this file is doubly invisible: nested, and `.yaml`.
- `plugins/charness/skills/issue/scripts/issue_validate_closeout_draft.py` is a
  packaged, operator-facing validator — CLAUDE.md's own issue-closeout floor
  names it — and it is absent from the catalog. `discover_packaged_validators`
  admits a file only if its basename starts with `check_` or `validate_`, so
  this one is never discovered, never needs a decision, and `missing` is empty.
- `charness-artifacts/quality/dup-review.json` moved aside makes the duplicate
  ratchet exit **0** with `ok: true`, `status: degraded`. `dup_ratchet_lib.py:298`
  returns before `hard_block` is ever computed. Observed directly, then restored
  and the restore verified.

**How the first cut got it wrong, recorded because it is a repeatable trap.**
Every row's reason in the first cut cited or paraphrased the surface's OWN
docstring or comment. This repo's comments are unusually rich and self-critical,
so reading them feels like adversarial review when it is not. The two facts that
falsify the headline — the `if degraded:` early return and the non-recursive
`iterdir` — are exactly the two things the self-descriptions do not mention. The
slice's stated method note ("classify what the surface does in the tree, never
what the retro's one-line summary said") was applied against the RETRO and never
against the SURFACES. And the strongest sentence in the section was the only
claim in it with no file and line behind it — and it was the sentence that
dissolved the remaining work.

**What survives from the first cut.** Churn is real and is a second, distinct
cost: several of these surfaces demand a round trip per correct change. But churn
is now an ADDITIONAL finding, not a replacement for the thesis.

| # | Enumeration | Where | What it does TODAY | Disposition (corrected) | Reason |
| --- | --- | --- | --- | --- | --- |
| 1 | Skill-ownership allowlist | `scripts/check_skill_ownership_overlap.py` `scan()`, list at `scripts/check_skill_ownership_overlap.allowlist.txt` (31 entries) | An unlisted overlap becomes a finding; a waiver nobody consumed is a stale advisory. But the SCAN reads only `SKILL.md` plus a non-recursive `iterdir()` over `scripts/`+`references/`, `.py`/`.md` only | `fail-closed` (list) + **`declare-uncovered`** (scan) | The list direction is right and `derive` is correctly rejected: the derivable population IS the finding set, so an allowlist derived from it would make the gate a permanent no-op. But the scan is a silent enumeration with a live miss, and no run ever emits a scanned-file count or the skipped suffix/depth set. The scope caveat exists only inside the stale-waiver advisory, which is emitted CONDITIONALLY — a clean run says nothing about partial coverage. Owes: a number. |
| 2 | Consumer-validator catalog | `discover_packaged_validators` at `scripts/check_consumer_validator_catalog.py`; catalog at `skills/public/quality/references/consumer-validator-catalog.yaml` | Raises on any discovered validator without a decision, and on any declared path not discovered — but `discovered` admits a file only by a two-token basename test | **`declare-uncovered`** + a scope widening. **NOT `derive`** — corrected after slice 3 | Classified `derive` and slice 3 attempted it; a round-2 reviewer showed no property landed. What shipped drops a POSITIONAL constraint (`startswith` → `token in name`) over the SAME two tokens: `CANDIDATE_TOKENS` is still a two-item list and the shipped comment says so outright. Nothing is derived from the tree. The candidate property that would have been — "packaged Python with a validator entry point" — was measured (377 of 833 carry a `__main__` guard) and correctly rejected as not separating the population. So this surface's honest disposition is the one slice 4 was going to give it: the widening is a real bug fix, and `uncovered_module_count` is the real remedy. |
| 3 | Validator-count pin | `tests/test_consumer_validator_catalog.py:94`, `:95`, `:96` | Three assertions with three different answers | **Split three ways** — see below | The first cut treated these as one row and got all three wrong. |
| 3a | — line 94 | `packaged_validator_count == decision_count` | Cannot fail | **dead assertion — remove or annotate** | Verified: line 186 raises when a declared path is not discovered, line 406 raises on `discovered - declared`, line 184 rejects duplicates. So equality is a THEOREM given `status == "pass"`. Confirmed live (134 == 134). The goal's own prose called this "the assertion above it already states the real property" — the property is stated and enforced by the production gate; this restatement can never bite. A test assertion that cannot fail is this goal's own defect class, inside the test it calls its clearest specimen. |
| 3b | — line 95 | `packaged_validator_count == 134` | Fires only on a complete, self-consistent, correct change | **`recommend-removal`** | Every INCOMPLETE change is already refused by production: added-without-decision (line 406), deleted-with-entry-kept (line 186), truncated mirror (line 186). What is left is exactly "someone did the work correctly", and the comment on the line is the receipt for the last time the chore was paid. Classifying it `fail-closed` preserved the very chore the record had just identified as the measured cost. |
| 3c | — line 96 | `consumer_facing_count == 14` | Guards the exported consumer surface | **`contract`** | This one is P3's exception. It pins what every consuming repo must wire or explicitly opt out of. A complete addition or removal of a consumer-facing validator changes an exported contract at an irreversible boundary, and lines 97-99 pinning specific consumer paths and ids reinforce the reading. |
| 4 | Duplicate-family classifications | `charness-artifacts/quality/dup-review.json` (781 entries); `dup_ratchet_lib.py:298`; scope at `.agents/quality-adapter.yaml:867` | Hard-blocks on a new family **when armed** — but returns `ok=True, block=False` before computing `hard_block` on ANY degrade, and never echoes its scope | **`declare-uncovered`**, NOT `fail-closed` | Observed, not reasoned: hiding the overlay yields exit 0. `tests/` and `skills/shared/` are outside `scope_paths` entirely and no family is ever formed there. Unlike two siblings in this same repo — `check_docs_graph.py` emits `did_not_judge`, `check_runtime_budget_universe.py` emits `NOT_JUDGED` — this gate emits neither its scope nor its uncovered set. The first cut's "never once passed over something it had not looked at" generalised three observed runs into a property the code contradicts. |
| 5 | Link-only-line bar | `scripts/check_docs_graph.py:56`, `resolve_link_only_lines_bar` at `:277` | A monotone ratchet: refuses when the count moves UP, silently tolerates slack when it moves DOWN | **`bound`** — a SIXTH category this taxonomy lacked | Every failure mode falls to the strict default, and pages outside `docs/` are named in `did_not_judge`, so this surface is genuinely well-built. But `fail-closed` does not describe it: it fails open in the slack direction, and the gate's own comment concedes a genuine bare link can hide under the wrapping residual. Not `derive` (the residual is not machine-separable from a real finding — that is why the bar exists), not `contract`, not `recommend-removal`. Owed remedy is to report the slack as a number, not to convert anything. |
| 6 | Runtime budget | `scripts/check_runtime_budget_universe.py` (#546) | Derives membership over the UNION of profile blocks and rides `NOT_JUDGED` on every armed verdict | `derive` (done) + `declare-uncovered` (**partial**) | Still the strongest of the seven, and the `derive` half is genuinely complete. But the first cut used it to argue slice 4 was discharged, and on the taxonomy's own wording — "name its uncovered set, AS A NUMBER, in its own output" — it is not: `NOT_JUDGED` names the CLASSES, and no count of budgeted-but-never-run labels exists. The gate structurally cannot produce that count, which is the open half of #546. |
| 7 | Claims-review scope prefixes | `skills/public/release/scripts/claims_review_scope.py:100-126`, lists at `:44` and `:61` | Unrecognised paths return `blocking`; `_is_dated_narrative` discriminates by dated filename stem | `fail-closed` holds, **reason rewritten** | The first cut called both prefix lists "an optimisation over a fail-closed default." True of `BLOCKING_PREFIXES` only. `ADVISORY_PREFIXES` is CONSTITUTIVE — the sole source of `advisory` in the module, i.e. a permission list where every entry widens what a release may waive. The module's comment guards only the omission direction; the commission direction is what launders findings. Separately, the date-stem property has a known-false premise for one class: `charness-artifacts/goals/<date>-<slug>.md` classifies advisory while `describe_goal_closeout_shape.py` parses that same file as gate input. Blast radius is bounded (the achieve complete gate owns goal-artifact correctness independently), so this is a reason defect, not a disposition change. |

**The taxonomy itself gained a category.** `bound` — a monotone ratchet that
refuses in one direction and accumulates slack in the other — is not any of the
original five, and row 5 is a real instance. Recorded as a finding about the
taxonomy rather than by forcing row 5 into `fail-closed`.

**Consequence for the plan, corrected.**

- **Slice 3 is NOT dead, and its target moves.** The first cut killed it on the
  grounds that neither named target had a derivable property. Both named targets
  were misjudged, and a better one exists: row 2's `check_`/`validate_` prefix
  predicate is a genuine two-item enumeration standing in for "packaged Python
  with a validator entry point", with a live miss to prove it. That is one real
  conversion, which is what `## User Acceptance` requires.
- **Slice 4 is NOT discharged; it is the slice this evidence most supports.**
  Rows 1, 4, 5 and 6 each owe a number in their own output: unscanned-file count,
  scope plus `did_not_judge`, ratchet slack, and budgeted-but-never-run count.
  Each lands inside the gate that owns the list, so none of them trips P5's
  gate-checking-gates anti-pattern.
- **Row 3 splits into a removal, a contract, and a dead line** rather than a
  conversion.
- **A boundary claim of this goal's own is false and is corrected here.**
  `## Boundaries` says slices 3 and 4 will "push the broad duplicate/length/
  pressure gates toward their thresholds" because they add tests. `tests/` is
  outside the duplicate ratchet's `scope_paths` entirely, so test scaffolding
  registers nothing on its code arm. Reading that silence as a clean result would
  be this goal's own defect.

## Backlog Recount

Recount the tracker before scope; see the `achieve` skill's
`references/lifecycle-before.md`. That path is SKILL-relative — resolve it from
`$SKILL_DIR`, not from this artifact's own directory, where it does not exist.

- Counted: 34 open issues at activation, from
  `gh issue list --repo corca-ai/charness --state open --limit 300 --json number --jq 'length'`.
  They fall into three groups: verification that stops verifying, skill contracts
  that have drifted from their code, and this session's own residue.
- Claims: this goal takes the first group, and only the three instances its
  slices name. Two of those three are already-filed issues (#586, #612); the
  third is the enumeration pattern itself, which has no issue and is the
  operator's framing.
- Premise check on the claimed issues: #586's premise HOLDS unchanged. #612's
  premise holds — the harness is still producing no verdict — but its BODY is
  stale: it describes `Select mutation sample: success` / `Run mutation: success`
  with only the summary failing, while the current failure is `Select mutation
  sample: failure` / `Run mutation: skipped`. An open issue is not a description
  of today's defect; slice 1 works from the observed run, not from the body.
- Not claimed: the skill-contract-drift group, the release/host-boundary group,
  and every individual item outside the three slices. Nothing here asserts those
  are lower value — only that this goal does not touch them, so a later session
  reading this artifact does not infer they were considered and dismissed.

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

Seeded at activation:

- Decision: whether the slice-1 harness repair actually restores a verdict on CI
- Owner: operator
- Why deferred: this activation's grant is local reproduction and honest signal
  only; no push, no CI observation
- Unblock action: land the slice-1 change and read one scheduled `Mutation Tests`
  run, or grant CI observation to a later phase
- Revisit trigger: the first scheduled mutation run after slice 1 lands
- **Resolved 2026-08-23: operator GRANTED push and CI observation.** This lifts
  the activation-time local-only scope for this phase only. `## Non-Goals` keeps
  its narrowed form — reading CI is in scope, and post-change CI behaviour may
  now be claimed ONLY from an observed run, never inferred.

- Decision: what to do about the SECOND, uncharacterized mutation failure mode
- Owner: operator
- Why deferred: it has no repair in this goal and no reproduction. The 08-19 and
  08-20 scheduled runs (`32201476295`, `32369077640`) were cancelled at
  `Select mutation sample` — the 08-19 one after 28 minutes, under a 180-minute
  job timeout and with `cancel-in-progress: false`, so neither the job timeout
  nor concurrency explains it. Slice 1's rg repair does not touch this. A
  round-2 reviewer noted this mode was called "still live" in the goal prose
  while having no queue item, issue, or off-goal entry — a goal whose thesis is
  "say out loud what you are not covering" leaving its own gap untracked. This
  entry is that repair.
- Unblock action: decide whether to file it as a tracked issue now or wait for
  the next scheduled run to characterize it with fresh step timings
- Revisit trigger: the next cancelled `Select mutation sample`, or the first
  scheduled run after slice 1 that still produces no verdict

- Decision: approve slice 2's redirect of the remaining plan
- Owner: operator
- Why deferred: it changes what slices 3 and 4 do, which is a scope decision, and
  local work can continue on either reading. Slice 2's classification moves
  slice 3's conversion target from the count pin and an allowlist to the
  consumer-validator catalog's `check_`/`validate_` discovery predicate, splits
  the count pin into a removal plus a `contract` plus a dead assertion, and
  reinstates slice 4 as the slice this evidence most supports (four surfaces owe
  a number in their own output). It also proposes a sixth taxonomy category,
  `bound`.
- Why this entry exists at all: an earlier draft of `## Enumeration Dispositions`
  ended "That decision is the operator's and is queued" while this queue held
  nothing of the kind. A bounded reviewer caught it and named it correctly as the
  same defect recorded two entries above — a goal whose thesis is "say out loud
  what you are not covering" leaving its own gap untracked, one slice later, on
  the sentence that cancelled two slices.
- Unblock action: approve the redirect, or direct slices 3 and 4 to run as
  originally written
- Revisit trigger: before slice 3 starts
- **Resolved 2026-08-23: operator replied `승인` (approved).**

- Decision: confirm that the approval above covered EXECUTING a
  `recommend-removal`, or direct the pin restored
- Owner: operator
- Why deferred: the removal is already made and is cheap to reverse either way;
  no further work depends on which answer comes back.
- The exact facts, so the answer is not made on my summary. The taxonomy defined
  `recommend-removal` as "recorded to the queue; not executed here", and
  `## Non-Goals` repeated it as "does not execute it". Slice 3 removed the
  `packaged_validator_count == 134` assertion. The approved text said the
  redirect "splits the count pin into a removal plus a `contract` plus a dead
  assertion" — which names a removal as the outcome — but the queue entry's own
  Unblock action asked a SCOPE question ("approve the redirect, or direct slices
  3 and 4 to run as originally written"), not for permission to delete an
  assertion, and no queue entry for the pin itself was ever written. A round-2
  reviewer charged this as the same shape already caught once in this goal: a
  decision treated as settled whose record does not carry it.
- What the removal costs if it was wrong: the pin's one unique detection was a
  scanner-exclusion list growing while a catalog entry was deleted. That is now
  held on purpose by
  `test_the_scanner_exclusion_list_is_exactly_the_checker_itself`, so the
  capability is not lost either way; the open question is procedural.
- Unblock action: confirm the approval covered execution, or say "restore the
  pin" and it goes back with a proper queue entry
- Revisit trigger: before this goal reaches `complete`
- **Resolved 2026-08-23: operator confirmed the approval covered EXECUTION.** The
  removal stands, recorded here as the one approved `recommend-removal` exception
  the taxonomy now allows. The pin's unique detection is independently held by
  `test_the_scanner_exclusion_list_is_exactly_the_checker_itself`, so no
  capability rests on this ruling.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Phases** — name the phases this run's recorded work crossed, e.g.
  `Phases: debug, quality`, or `Phases: n/a — <reason>` when it crossed none. YOU
  say this; the floor used to infer it by matching words in your prose and was
  wrong in both directions — plain-English debug work did not register, while the
  word "gate" in an unrelated sentence demanded a quality route.
- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / issue work (both detected from records you wrote) and every
  phase you declared above need this `Routing:` evidence or a
  `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.
- **Successor goal step** — required at EVERY completion, not conditionally. Add
  a `Successor goal:` line naming the next goal artifact this run's lessons
  designed, or write `Successor goal: n/a — <reason>` to say out loud that none
  is wanted. The closing goal is the only place that still holds what the session
  measured about this repo's real shape; a completion that does not spend it
  throws that away, and the next session re-derives it.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Phases: <declared phases, or n/a — why none were crossed>`
- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: approved — every slice changes verdict logic on a
  proof surface, which the north star classifies as irreversible and which needs
  a distinct observer. The session's higher-priority instruction was not to spawn
  subagents unrequested, so fresh-eye review was unavailable and a same-agent
  substitute is contract-forbidden. The operator was asked before activation and
  granted bounded-reviewer spawning for this goal (2026-08-23), so the two-round
  floor is satisfiable rather than waived.
- Discuss before activation: resolved — slice 1's original acceptance ("the
  harness produces a verdict on `main` again") required push and CI observation,
  both of which need a phase-scoped grant. The operator scoped this activation to
  local reproduction plus honest signal only. Acceptance was rewritten to the
  ambiguity-removal outcome, which is the north-star point of the slice and does
  not depend on a performance fix landing; CI re-verification is seeded into
  `## Operator Decision Queue` instead of claimed here.

## Slice Log

### Slice 1: Slice 1 — make an unmeasured mutation run say so, and unblock the baseline

- Objective: Give the mutation harness a verdict vocabulary that distinguishes 'nothing was measured' from 'measured and failed', and remove the cause of the red coverage baseline. Scoped by operator grant to local reproduction plus honest signal: no push, no CI observation.
- Why this approach: Every other proof in this repo stands on the mutation surface, and it had produced no verdict since 2026-08-19 while its summary still rendered a score verdict. That is the north star's P5 defect exactly -- a gate declaring completion over a population it never read.
- Commits: 3a5da4a59 (slice), fd07fb9d7 (goal shaping and activation)
- What changed: scripts/check_mutation_score.py, scripts/check_js_mutation_score.py, scripts/mutation_baseline_abort_lib.py, .github/workflows/mutation-tests.yml, .github/workflows/quality-core.yml, tests/quality_gates/test_mutation_baseline_abort.py, tests/quality_gates/test_quality_mutation_testing.py, tests/quality_gates/test_js_mutation_tooling.py, charness-artifacts/quality/dup-review.json, and the generated plugins/charness/ mirror.
- Alternatives rejected: Rejected: skipping the rg-dependent tests when rg is absent -- that is issue #586's class, a green suite over an inert surface. Rejected: removing the rg dependency from the shipped script in this slice -- it is a dependency change on an exported proof surface and a naive `git ls-files` swap breaks seven tests that build non-git roots, so it owes its own slice. Rejected: special-casing the two extra zero-score render sites a reviewer found -- the single condition over the denominator covers every route into them, which is this goal's own thesis. Rejected: reverting the shared `verdict_token` to satisfy the duplicate detector, which had begun flagging the import lists that sharing created -- letting the gate dictate a worse design is the failure under study.
- Targeted verification: Local reproduction of the cause in both directions: with rg present the preflight suite passes 25/25 in 2.10s; with rg removed from PATH the same 8 tests fail in 1.71s, matching the CI log's 8 verbatim. Independently corroborated on a second workflow: quality-core run 32536921987 (2026-08-21) went red with the identical 8. Negative controls, each run by planting the defect and observing the flip, then restoring: the UNMEASURED rename (test fails, restored passes), the rg workflow ordering pin (fails, restored passes), and the zero-denominator property -- which FIRST showed no coverage at all when planted, proving the property had shipped untested, and now bites. run_slice_closeout.py --skip-broad-pytest completed clean. NOT claimed: any CI behaviour after this change; no run was observed.
- Test duplication pressure: Predicted in the goal's Boundaries and it fired twice. The duplicate ratchet hard-blocked on a pre-existing byte-identical pair in check_js_mutation_score.py that an unrelated comment shifted into one detector window -- removed by extracting _append_summary_section rather than recorded as a ledger entry. It then blocked again on four families that were all boilerplate or structurally parallel: a one-line ternary, the repo's sys.path bootstrap preamble, the two import lists that the shared-rule extraction had made identical, and the two engines' inherently parallel metrics functions. Those four were classified intentional with reasons. Classification: the first was new-slice-local and fixable; the four are accumulated detector noise on boilerplate, and the fact that its remedy menu asked for a ledger entry each time is direct evidence for slice 2's disposition of dup-review.json.
- Critique: Two rounds, five bounded read-only reviewers, unnamed, with reviewer_boundary_fingerprint snapshot/verify around round 1 (verdict parent-attributed, no unattributed drift). Round 1 ran three angles -- correctness/reachability, proof integrity, and root-cause premise -- and every one of them landed something that changed the slice. Proof integrity showed the negative control tested a pure function while the token it guarded was emitted by a different renderer. Correctness showed the shipped invariant was false: two more reachable paths still rendered FAIL with nothing scored. Root-cause premise broke the claim's time scope by noticing command_plan_preflight.py did not exist before 2026-08-21, and broke the 'only CI surface runs the standing suite' premise. Both premise corrections were verified against CI records and folded. Round 2 read the repairs.
- Off-goal findings: Four findings recorded in the artifact's Off-Goal Findings: the missing-binary legibility gap, the adapter-owned issue title that misnames a baseline abort, #612's stale body, and the shipped script's hard rg dependency with the non-git-root caveat that makes a naive git ls-files swap unsafe.
- Lessons carried forward: Reproduce before repairing, and then reproduce the REPAIR's premise too. This slice's stated cause was wrong twice: the draft said the sampler times out (it completed and refused on a red baseline), and the first correction over-scoped rg to a window in which the offending file did not yet exist. Both were caught by reading records -- CI step outcomes, git log --diff-filter=A -- not by re-reading prose. Second: a property added without a test is not a property. Planting the zero-denominator defect showed nothing failed, which is the only reason it now has a control.
- Metrics:

### Slice 2: Slice 1, round-2 repairs — the fix carried the class it fixed

- Objective: Fold two round-2 bounded reviews of the repaired surface. The operating contract requires this round for a slice that changes verdict logic on a proof surface, and it earned its keep: it found a blocker in the code and a blocker in the record.
- Why this approach: One round would have shipped a summary that contradicted itself and a written record claiming the opposite of what the diff did.
- Commits: follows 3a5da4a59; round-2 repairs committed separately
- What changed: scripts/check_mutation_score_summary_lib.py, scripts/check_js_mutation_score.py, scripts/check_mutation_score.py, scripts/mutation_baseline_abort_lib.py, tests/quality_gates/test_mutation_baseline_abort.py, tests/quality_gates/test_js_mutation_tooling.py, tests/quality_gates/test_quality_mutation_score_validity.py, tests/quality_gates/test_quality_mutation_testing.py, charness-artifacts/quality/dup-review.json, this artifact, and the generated mirror.
- Alternatives rejected: Rejected the blunt `"**FAIL**" not in rendered` assertion that exposed the code blocker: it also forbids `- Blocking signals: **FAIL**`, which is a DIFFERENT predicate and is true and needed. Suppressing a correct line to satisfy a test would have been the same defect in the other direction, so the property is stated over the rows that render a verdict about the code, and the blocking-signal row is asserted PRESENT. Rejected keeping the rg pin as a hand-listed pair of workflow paths: that is a two-entry enumeration inside the goal that exists to stop them, so the population is now globbed from `.github/workflows/` and each job that runs the standing suite must install rg.
- Targeted verification: 124 focused tests pass. Three negative controls run by planting the defect and observing the flip, then restoring: the self-contradicting summary, the cross-job rg install (moved into the job that does NOT run the suite -- the old whole-file assertion passed, the derived per-job one fails), and the zero-denominator property. Both engines now have a WIRED-PATH test driving a zero-denominator run through the real CLI by subprocess, which the property shipped without. run_slice_closeout.py --skip-broad-pytest completed clean; broad standing suite run separately. NOT claimed: any CI behaviour after this change.
- Test duplication pressure: The duplicate ratchet fired a third time, and this occurrence is the slice's sharpest measurement about it: three of the four families were re-reported under NEW fingerprints because the repairs added one name to an import list. The ids are content fingerprints, so an edit near the members orphans a reviewed entry and demands a fresh one for an unchanged human judgement. Entries were re-keyed in place rather than accumulated. Classification: churn, not stale-list under-coverage -- the opposite failure from the one this goal set out to find.
- Critique: Two bounded read-only reviewers on the repaired surface. Findings folded: a THIRD spelling of the rule in check_mutation_score_summary_lib rendering `Mutation score: **FAIL** (0.0%)` directly under `Status: **UNMEASURED**` -- the #612 misdiagnosis reproduced by its own repair; a `passed` verdict rule computed twice in check_js_mutation_score, once for the renderer and once for the exit code, in different orders so no detector could ever flag them; the `status reflects partial completion` sentence that is false when the status is UNMEASURED; the untested `reachable == 0` precedence over the timeout and pending arms; the `one owner` claim overstated while a fourth inline ternary survived; UNMEASURED_STATUS referenced only inside its own definition; the missing wired-path tests; and a BLOCKER on the record -- the Off-Goal Findings bullet said the ratchet's request was answered by removing duplication while the diff extended the ledger four times, three of them describing this slice's own fix.
- Off-goal findings: The second, uncharacterized mutation failure mode (the 08-19/08-20 cancellations) now has an Operator Decision Queue entry; it had been called `still live` in prose with no tracked destination, which is this goal's own thesis one level up. The public reference skills/public/quality/references/mutation-testing.md still teaches the two-token vocabulary and has no UNMEASURED entry.
- Lessons carried forward: The two-round floor is not ceremony on a proof surface. Round 1 produced a repair that carried the class it fixed -- a status token corrected on two paths while a third spelling contradicted it on the adjacent line -- and only a round reading the REPAIRS could see it. Second: an assertion narrowed to make a test pass is how the blocker hid. The first cut asserted `- Status: **FAIL**` where the sibling assertion used the bare token; the anchored form steps around the contradicting line, and the version that would have caught it was already in the same file, one function away.
- Metrics:

### Slice 3: Slice 2 — classify the seven, and get falsified

- Objective: Record one disposition per enumeration from the five-way taxonomy, so slice 3 does not convert a list that is the contract. No code change; the deliverable is a decision record.
- Why this approach: The predecessor retro named the seven in one line each. Converting on those descriptions is how a contract list gets destroyed, and slice 1 had already shown two of them were nearer the target shape than the summary implied.
- Commits: this slice is artifact-only; recorded in `## Enumeration Dispositions`
- What changed: charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md — new `## Enumeration Dispositions` section, a corrected `## Boundaries` claim, and a new Operator Decision Queue entry.
- Alternatives rejected: Rejected forcing all seven into the goal's stated thesis. Rejected the reverse too: an earlier cut concluded the thesis was unsupported and the remaining slices were dead, and that conclusion did not survive review either.
- Targeted verification: Every corrected claim re-derived by RUNNING the surface rather than reading it. The ownership gate reports findings [] / status ok / scanned_skills 20 while an unallowlisted setup->spec mention sits in a nested .yaml. The catalog reports 134 == 134 == decision_count, and issue_validate_closeout_draft.py — a packaged operator-facing validator — is absent from it because the discovery predicate admits only check_/validate_ basenames. Moving dup-review.json aside makes the duplicate ratchet exit 0 with ok true and status degraded; restored, and the restore verified by diff. Line 94's tautology confirmed against the two subset-enforcing raises at :186 and :406. Goal artifact, referent gate, and markdown lint all clean.
- Test duplication pressure: None — no tests added or changed. Worth recording that the goal's own `## Boundaries` predicted duplicate-gate pressure from later slices adding tests, and that prediction is FALSE: tests/ is outside the ratchet's scope_paths entirely, so test scaffolding registers nothing on its code arm. Corrected in place.
- Critique: Two bounded read-only reviewers, one told to falsify the headline and one to attack each disposition. Both falsified it, independently and by different routes. The headline `ZERO of the seven silently under-cover` is withdrawn. Corrected finding: all seven fail closed over the population their SCAN admits, and four reach their list through a discovery predicate that is itself a silent enumeration naming no unscanned set. Three live instances in the tree. Further folded: line 94 is a dead assertion that cannot fail; line 95 fires only on correct work and is recommend-removal; line 96 is contract; dup-review.json is declare-uncovered because of an explicit fail-open degrade branch; the link-only ratchet needs a sixth taxonomy category because it fails open in the slack direction; and ADVISORY_PREFIXES is constitutive rather than an optimisation. A reviewer also caught a record blocker: the section claimed a decision was queued while the queue held nothing of the kind.
- Off-goal findings: The three live instances are defects in the tree, not just classification inputs: an unallowlisted cross-namespace mention, an undeclared packaged validator, and a duplicate gate that exits 0 when its overlay is absent. None is repaired in this slice; each belongs to the redirected slice 3 or 4 and is queued with them.
- Lessons carried forward: I graded seven surfaces on their own self-description. This repo's comments are unusually rich and self-critical, so reading them feels like adversarial review when it is not — and the two facts that falsified my headline, an `if degraded:` early return and a non-recursive iterdir, are exactly the two things the self-descriptions do not mention. The slice's own method note said to read the tree rather than the retro's summary; I applied it against the retro and never against the surfaces. The structural tell was available at the time: the strongest sentence in the section was the only claim in it with no file and line behind it, and it was the sentence that dissolved the remaining work.
- Metrics:

### Slice 4: Slice 3 — widen the catalog's discovery predicate, and stop calling it a derive

- Objective: Repair the consumer-validator catalog's positional discovery predicate, which silently excluded a packaged operator-facing validator, and make the gate report what its predicate does not admit.
- Why this approach: Slice 2 found the enumeration that rots is the SCAN, not the list. This is the scan with a live miss and the cheapest honest repair.
- Commits: committed with this entry; follows 332077310
- What changed: scripts/check_consumer_validator_catalog.py, scripts/staged_commit_gate_plan.py, skills/public/quality/references/consumer-validator-catalog.yaml, docs/conventions/validator-timing-layers.md, tests/test_consumer_validator_catalog.py, tests/quality_gates/test_staged_commit_gate_plan.py, charness-artifacts/quality/dup-review.json, and the generated plugins/charness mirror.
- Alternatives rejected: Rejected the reviewer-proposed property `packaged Python with a validator entry point` ON MEASUREMENT, not taste: 377 of 833 packaged modules carry a `__main__` guard, so it would nearly triple the decision count without separating the population. Rejected widening the token list, which is the disease this goal names -- measured exposure if it were widened: audit 11, guard 9, lint 4, verify 3. Rejected keeping the population pin's chore in exchange for its one real detection; that detection is now held on purpose by a positive test on the scanner-exclusion list.
- Targeted verification: Capability-equality replay committed as a test: zero paths lost, exactly one gained, and it is the live miss. Four negative controls, each run by planting the defect and observing the flip, then restoring: reverting the predicate (3 tests fail), zeroing the uncovered count (1 fails), the INFIX-named undeclared validator (the control that actually distinguishes the two predicates -- added only after round 2 showed every existing fixture used a prefix-form name the OLD predicate already caught), and reverting the dispatcher to its own positional copy. Wired-path assertions on the CLI. Standing suite 11182 passed / 0 failed. Slice closeout green. NOT claimed: any CI behaviour.
- Test duplication pressure: One new duplicate family, classified intentional: a one-line `sum(1 for path in <root>.rglob(...) if path.is_file())` counting idiom matched across three unrelated modules. Shape, not shared logic.
- Critique: Two bounded read-only reviewers, and both landed findings that changed the slice. The load-bearing one: the commit-time dispatcher in staged_commit_gate_plan.py kept its OWN positional copy of the predicate, so the single validator this widening exists to bring into scope was the single file whose edit did not fire the catalog gate at commit time -- #586's class, produced by the repair itself. The dispatcher now imports the checker's predicate and a test pins the identity. Also folded: a shipped docstring still carried a retracted measurement (137 / `the two added`) that the goal artifact had already corrected, exported to consumers through the mirror; `candidate_predicate == list(EXPECTED_CANDIDATE_PATTERNS)` was a tautology -- this slice deleted one dead assertion and added another, replaced now by an executable tie between the token constant and the published globs; `uncovered_module_count` counted the deliberate scanner exclusion as unseen; `count_packaged_modules` filtered `__pycache__` where discovery did not, so the subtraction spanned two populations; the refusal message still taught the prefix rule; and one added test was a near-duplicate of an existing control and was dropped.
- Off-goal findings: The catalog's own operator-facing refusal text and the timing-layer doc both stated the prefix rule and were corrected here. The installed-layout residual (a consumer invoking the packaged checker from their repo root would scan their own tree, and the widened predicate admits strictly more of it) is pre-existing and unchanged by this slice; recorded, not repaired.
- Lessons carried forward: Two, both about claiming more than was done. First: NO DERIVE LANDED. Dropping a positional constraint from an enumeration over an unchanged token pair is a bug fix plus a declare-uncovered, and calling it a conversion overclaims the goal's own acceptance criterion -- which is now recorded OPEN rather than discharged. Second: a negative control must plant the defect the change is ABOUT. Every planted-defect fixture in the file used a prefix-form name that the old predicate already refused, so none of them could tell the two predicates apart; the control that could was written only after a reviewer pointed at the gap.
- Metrics:

### Slice 5: Slice 4 — make four gates name their uncovered set as a number

- Objective: Each of the four surfaces slice 2 said owed a number now emits one, in its own output, without changing any verdict.
- Why this approach: Slice 2's corrected finding: all seven fail closed over the population their SCAN admits, and four never said what the scan did not reach. A green that cannot distinguish `checked` from `never looked` is this goal's root defect.
- Commits: committed with this entry; follows 009a894e2
- What changed: scripts/check_skill_ownership_overlap.py, scripts/check_docs_graph.py, scripts/check_runtime_budget_universe.py, skills/public/quality/scripts/{check_dup_ratchet,dup_ratchet_lib,dup_ratchet_git,runtime_profile_lib}.py, four test files including a new tests/quality_gates/test_dup_ratchet_scope_coverage.py, charness-artifacts/quality/dup-review.json, and the generated mirror.
- Alternatives rejected: Rejected forcing a number where the gate structurally cannot know one: the runtime-budget surface still declines to count `a budgeted label the runner names but never RUNS`, which is the open half of #546, and says so in did_not_judge instead. Rejected running this slice in my own context: it was delegated to a Sonnet workflow (4 read-only analysts, one sequential implementer, one verifier) precisely to keep 1098 lines of reading out of the parent.
- Targeted verification: Every number re-derived by RUNNING the gate rather than trusting the workflow's self-report. ownership: scanned_files 533 / excluded_build_artifacts 362 / uncovered.total 45. dup ratchet: scope admits 1095/7785 tracked files by path. docs graph: link_only_lines_slack 0 against a recorded bar of 167. runtime budget: checked 37, universe_size 109, plus second_direction_status and malformed_budget_profile_blocks. Standing suite 11202 passed / 0 failed. Dup ratchet clean, mirror synced, lint clean, slice closeout green. NOT claimed: any CI behaviour.
- Test duplication pressure: One new duplicate family classified intentional (a one-line rglob counting idiom across three unrelated modules). Separately, and more usefully: the slice's OWN new test file had copied four helpers verbatim from its sibling -- into `tests/`, which is exactly the scope this slice made the ratchet report as never judged. The ratchet cannot see it, so the discipline had to; the helpers are now imported.
- Critique: Three bounded read-only reviewers, one BLOCKER and roughly a dozen should-fixes, all folded. The blocker: dup ratchet's new did_not_judge asserted that no family is formed from files outside scope_paths -- false, because the doc arm reads DEFAULT_SCAN_PATH='.' and a new doc family sets hard_block. A false non-claim in the direction that gets a REAL block dismissed, shipped by the code written to make claims honest. Two siblings of it: an empty scope_paths made the gate report the whole tree as uncovered while the scanner had in fact fallen back to its defaults and scanned, and a degraded run printed coverage numbers for a run that formed no families. Also folded: the ownership walk excluded ~362 build-artifact files from BOTH walks while its docstring claimed the buckets summed to the whole unreachable population; that gate had no unconditional did_not_judge; two docs-graph assertions were f(x) == f(x) and would pass against a collapsed bar resolver; and two ownership mutants survived (dropping `references` from the bucket condition counts SCANNED files as uncovered).
- Off-goal findings: check_skill_ownership_overlap.py is not queued by run-quality.sh at all -- only tests exercise it -- so its new number is visible only on a manual invocation. Recorded rather than repaired: wiring a gate into the routine lane is a scope decision, not a slice-4 deliverable. Two of the new numbers (the dup-ratchet SCOPE line, unreachable_by_selected_profile) also carry no WARN marker, so run-quality.sh's passing-phase filter hides them on green runs.
- Lessons carried forward: Verify a reviewer before acting on it. Three findings across the three reviewers were WRONG and I checked each against HEAD before repairing: the exception-narrowing and the budgeted_labels delegation both predate this slice, and the env-dependent test is already handled by a session-wide conftest scrub. I applied the third fix before checking, then reverted it as redundant -- the one place this round I acted on a report instead of on evidence.
- Metrics:

## Context Sources

- [The design north star](../../docs/design-north-star.md) — the governing
  standard this goal was shaped against. P3 and its irreversible-boundary
  exception, P5's no-terminal-green and its gate-checking-gates anti-pattern, P4's
  distinct observer and distinct evidence channel, and the taste ladder's
  `at equal —` precondition are each load-bearing in the design above.
- This repo's open issues on verification that stops verifying: #586 (a check
  that passes its direct-call test while never firing on the wired path) and #612
  (the mutation regression on `main`).
- `charness-artifacts/retro/2026-08-22-claims-convergence-and-ship-retro.md`,
  whose Waste section names the six enumerations extended in one session and
  whose Sibling Search names all seven.
- The predecessor goal's slice-1 critique rounds, where a hand-kept prefix list
  put a gate-input pointer in the wrong scope and a property fixed it.
- The CI runs read as diagnostic input for slice 1, listed in full because a
  round-2 reviewer found the frozen list named only the first while the shipped
  comments cite five: `Mutation Tests` `32573073322` (2026-08-22, `f5211700a`,
  the sampler failure); `quality-core` `32536921987` (2026-08-21, the same eight
  preflight failures on a different workflow); `quality-core` `32544789186`
  (2026-08-22, clean in 0.5s on a release-artifact-only range, which is why that
  lane's green is range-scoped rather than suite-wide); and the cancelled
  `Mutation Tests` runs `32201476295` (2026-08-19) and `32369077640`
  (2026-08-20). Read at activation and during slice 1, not the stale text in
  #612.
- Local reproduction of slice 1's cause, recorded here rather than only in a
  workflow comment: with `rg` present `tests/quality_gates/test_command_plan_preflight.py`
  passes 25/25 in 2.10s; with `rg` removed from `PATH` the same eight tests fail
  in 1.71s — the eight tests in isolation, not a reproduction of the 20-minute
  sampler path.

## Interview Decisions

- Decision: the operator named the target as "gate more intelligently instead of
  extending a whitelist one at a time". That framing is the goal, not the issue
  list; the issues are instances.
- Decision: mutation harness first. It is the only one where the current state
  is "no coverage at all" rather than "coverage with a stale edge".
- Decision: prefer fail-closed over clever derivation where the property is
  genuinely contested. An enumeration that refuses when it falls behind is
  already better than one that silently passes.
- Decision (asked at activation): fresh-eye channel. Family considered — spawn
  bounded reviewers / proceed and record the review unproven / route the packet
  to the operator as the human observer. Chosen: spawn bounded reviewers, granted
  explicitly by the operator. Rejected the unproven option because every slice
  here changes verdict logic and the whole goal is about surfaces that fail
  silently; rejected the operator-as-reviewer option because it blocks each slice
  boundary on a human turn. `axis: host` — subagent availability is a host
  capability, so this grant is recorded as a per-session host fact and is not a
  portable default for consumer repos.
- Decision (asked at activation): external-boundary scope for slice 1. Family
  considered — local reproduction and honest signal only / push plus CI
  observation / push without observation. Chosen: local only. Rejected the push
  options because the slice's north-star value is removing an ambiguous green,
  which is provable locally, and a performance fix on CI is a separate, larger
  bet. `axis: environment` — the harness runs local and in CI, and this goal
  binds itself to the local instance deliberately.
- Decision: the disposition taxonomy replaces "convert or not" as the unit of
  work. `single-point: this repo's seven named enumerations` — the taxonomy is
  authored here for this goal's decision record and is not proposed as a portable
  skill contract in this run.

## Plan Critique Findings

No Before-phase plan critique subagent round yet; the design was shaped at the
predecessor's closeout from that run's measured waste, then reworked against the
north star at activation. Folded at activation, and stated so a reviewer can
attack each:

- Folded into Non-Goals and Boundaries: the original plan had no test for P3's
  irreversible-boundary exception, so a `contract` list could have been converted
  as if it were an approximation. Slice 2 and the `contract` disposition exist
  for that.
- Folded into Non-Goals: slice 4's original wording ("make the remaining
  enumerations say what they do not cover") could be implemented as one gate
  reading all the others, which is P5's named anti-pattern. It is now constrained
  to each gate's own output.
- Folded into Boundaries: the original plan asserted conversions preserve
  behaviour without a way to establish it. The capability-equality replay is now
  the precondition, and a failed replay downgrades the disposition.
- Folded into Boundaries and the verification plan: #586's class applies to this
  goal's own repairs, so a converted property needs a wired-path test.
- Weakest remaining point, stated for a reviewer to attack: slice 2 assumes the
  seven are separable and individually classifiable. If two of them are the same
  property observed at different surfaces, classifying them independently
  produces two different dispositions for one rule — the exact contradiction this
  repo has paid for before under `one rule, one owner`.
- Second weakest: the taxonomy itself is a five-item enumeration authored inside
  a goal whose thesis is that enumerations rot. It is defended as a decision
  vocabulary rather than a coverage list (P3's refusal-vocabulary exception), but
  that defence is exactly what every rotting list's author believed.

## Closeout Binding Plan

- Reviewed inputs: issues #586 and #612, the predecessor retro's Waste and
  Sibling Search sections, and the observed mutation run `32573073322`, frozen at
  activation so a later edit cannot retroactively change what was reviewed.
- Frozen target: `5bd571166d0f3b8c84b9a758b246b1d811e6adbe`, the SHA at
  activation, also recorded in `## Active Operating Frame`.
- Fresh-eye: bounded reviewer subagents, operator-granted at activation, two
  rounds per verdict-surface slice, spawned unnamed and read-only with a
  `reviewer_boundary_fingerprint.py` snapshot/verify around each round.
- Verification lock: changed-line proof over each slice before any broad gate,
  and the broad gate at the bundle boundary — not per commit.
- Complete flip: the terminal-record rule is `describe_goal_closeout_shape.py` FIRST to get the whole
  conditional missing set in one pass, then verify once. The predecessor flipped
  serially and paid six round trips for it.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- **The operator caught this goal committing its own defect, in the surface the
  goal had just repaired.** Slice 3 removed the `packaged_validator_count == 134`
  pin as a chore — a count a TEST enforced — and then wrote the same measurement
  into the module's docstring, where nothing enforces it. That is a checked count
  converted into an unchecked one: strictly worse than the chore it replaced, and
  the frozen lesson for it is named `bar-recorded-as-prose`. It survived two
  bounded reviewers, both of whom read that comment; one of them even flagged an
  EARLIER stale number in the same block without noting that the replacement was
  the same species.
  - Repair: the docstring now states the METHOD for judging the token pair and
    carries no population counts at all. The counts live where they are computed
    — `packaged_validator_count`, `packaged_module_count`,
    `scanner_excluded_count`, `uncovered_module_count` are in every report the
    module emits, so a reader gets today's number by running it. This is the
    idiom `check_docs_graph.py` already uses for its ratchet ("HOW TO SIZE ONE,
    stated as the method rather than as anyone's answer"), which slice 2 had
    already read and praised and then did not apply.
  - The same fix was applied to a second instance in the same slice: the
    capability-replay test pinned the gained set to one literal path, which would
    demand a chore edit the next time someone correctly adds an infix-named
    validator. It now characterises the SHAPE of the widening instead.
  - **Measured before generalising: this is not a repo-wide pattern.** A sweep of
    `scripts/` and the packaged skill scripts for population counts frozen in
    comments returns nothing else. So the remedy is the authoring discipline
    above, NOT a new gate — building one would be meeting a prose problem with
    another bespoke gate, which is the cost the north star's diagnosis names.
    Recorded as a lesson rather than a slice.

- **A missing required binary is reported as N opaque assertion diffs.** The
  standing suite's answer to "ripgrep is not installed" was eight failures
  asserting error codes they never reached, twenty minutes into the sampler's
  baseline run. The property is one legible refusal — "declared required binary
  `rg` absent; N tests depend on it" — checked once, instead of discovered
  through the enumeration of downstream failures. This is this goal's own pattern
  and belongs to a later slice or a tracked issue; it is deliberately NOT folded
  into slice 1, because a suite-wide precondition has a far wider blast radius
  than the slice under review and owes its own review round. It must FAIL, never
  skip: a skip would make the suite green while the surface is inert (#586's
  class).
- **The auto-filed mutation issue's title misnames a baseline abort.** The title
  is adapter-owned (`.mutation_testing.auto_issue.title` =
  "Mutation test regression on main") and is applied to every filed instance,
  including runs where no mutant executed. The summary body now says
  `UNMEASURED`, so the title and the body disagree. Left unchanged deliberately:
  the title is shared with genuine regressions and changing it is a separate
  decision about the adapter's vocabulary.
- **#612's body describes a failure that is not the current one.** It records
  `Select mutation sample: success` / `Run mutation: success` with only the
  summary failing; run `32573073322` shows the sampler failing and the run
  skipped. The auto-filer updates an existing issue by marker token, so the body
  reflects whichever run first opened it. An open issue is not a description of
  today's defect.
- **The duplicate ratchet asked to be extended during slice 1, and the slice
  answered BOTH ways — it removed duplication once and extended the list four
  times.** An earlier version of this bullet recorded only the removal, which
  read as though the slice had declined to extend the ledger. It did not. A
  round-2 reviewer caught the omission; the full record follows, because the
  measurement is the most useful input slice 2 has.
  - Removed: a pre-existing byte-identical pair in `check_js_mutation_score.py`
    that an unrelated comment had shifted into one detector window. Extracted as
    `_append_summary_section`. The ledger entry would have recorded the copies
    instead of removing them, so removal was correct here.
    - Extended: four entries in `charness-artifacts/quality/dup-review.json`,
    all classified `intentional` — a one-line ternary matched across unrelated
    domains; the two engines' metrics functions, which share no input schema;
    the two import lists; and the repo's `sys.path` bootstrap preamble. The
    family fingerprints are deliberately NOT restated here: they are volatile
    (see the re-keying note below), and a value copied into prose drifts from its
    source, which is a small instance of this goal's own subject. The ledger is
    the one place they live.
  - **Three of the four were created or surfaced by this slice's own
    refactor.** The import-list family exists *because* the shared rule was given
    one owner: the detector reported the fix as the defect. That is a measured
    fact about how this ratchet behaves on refactors, not a complaint.
  - **Re-keyed within the same slice, which is the sharpest measurement this
    slice produced about the ledger.** The four ids above are the SECOND set. The
    round-2 repairs added one name to an import list, and three of the four
    families were immediately re-reported under new fingerprints, requiring their
    reviewed entries to be re-keyed in place. The ids are
    content fingerprints, so an edit ANYWHERE NEAR the members orphans the
    reviewed entry and demands a fresh one — the human judgement is unchanged and
    has to be re-recorded anyway. That is a maintenance treadmill, not a stale
    list: the failure mode here is churn rather than silent under-coverage, which
    is the opposite of the failure this goal set out to find. Slice 2 should
    classify on THIS evidence, not on the predecessor retro's one-line summary.
  - **Disposition correction.** An earlier reading of this ledger as the
    `contract` case was wrong, and the reviewer's correction is adopted:
    `dup-review.json` is **`fail-closed`**. Its gate already refuses when a new
    family appears, so the list falling behind IS detectable — which is the
    fail-closed definition in `## Boundaries`, not the irreducible-observable
    contract. Under that classification, extending it is the correct operation of
    a healthy enumeration rather than an instance of the disease. Slice 2
    inherits this classification, not the earlier one.
- **The shipped `command_plan_preflight.py` hard-requires a non-baseline binary,
  and CI provisioning does not fix that for consumers.**
  `skills/shared/references/binary-preflight.md` names `rg` as explicitly
  non-baseline, with a declaration-and-consent protocol for skills that call it.
  That script is not a skill bootstrap fence — it is Python that shells out to rg
  with no declaration, no sentinel, and no fallback, and it is the only non-skill
  code path in the repo that does. It ships to consumer repos, where charness
  cannot add an apt step. Installing rg in this repo's CI fixes this repo's
  signal and leaves the exported defect untouched. The measured swap target is
  `git ls-files -c -o --exclude-standard` (a strict superset here, and git is
  already a hard dependency of the same script for `git rev-parse --verify`), but
  a naive swap is NOT safe: seven of the eight affected tests build their repo
  with a bare `mkdir` and never `git init`, and `git ls-files` exits 128 in a
  non-git directory where `rg --files` succeeds. So the swap owes either an
  explicit git-repo contract with its own distinct error code or a walk fallback.
  Deferred to its own slice with its own two rounds rather than folded here: it
  is a dependency change on a shipped proof surface, and slice 1 is already
  carrying more than it planned.
- **Slice 2 inventory anchors located** (recorded here so slice 2 does not
  re-derive them): the ownership allowlist is a literal file,
  `scripts/check_skill_ownership_overlap.allowlist.txt` (41 lines, and its own
  header already describes a stale-entry advisory); the validator-count pin is
  `tests/test_consumer_validator_catalog.py:94-96`, where line 94 asserts the
  real property (`packaged_validator_count == decision_count`) and line 95 pins
  the population at a literal whose comment records the last chore. Note for
  slice 2's classification: line 95 is not purely redundant — line 94 alone stays
  green if validators are deleted in step with their decisions — so its
  disposition is a real judgement between `derive` and `fail-closed`, not the
  obvious `derive` the predecessor retro implied.
- **At least two of the seven are already nearer the target shape than the
  predecessor retro's one-line descriptions suggested**, which is the first
  evidence that slice 2 (classify before converting) was the right sequence
  rather than overhead. The `link_only_lines` bar in
  `scripts/check_docs_graph.py` is not a flat list but a RATCHET that may only
  decrease (line 56), which is already a fail-closed shape. The runtime budget
  has `scripts/check_runtime_budget_universe.py` (#546) sitting over it, whose
  own docstring states the property — "is this budgeted label still a name the
  runner knows?" — so the enumeration there is already partly derived. Slice 2
  must classify what these surfaces DO today, not what the retro's summary said
  they do; converting either on the retro's description alone would have been
  the `contract`-list mistake in its other direction.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named

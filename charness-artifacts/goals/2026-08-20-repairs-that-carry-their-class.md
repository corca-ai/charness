# Achieve Goal: Make a repair prove it does not carry the class it repairs, then finish the corpus

Status: draft
Created: 2026-08-20
Activation: `/goal @charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: shaped draft awaiting activation; slice 1 is the first to run.
- Current slice intent: Before-phase shaping is complete as of 2026-08-19 against
  `dd671ec1e` — scope, acceptance, slice plan, backlog recount and the four
  operator rulings are recorded; reshape before activating if the acceptance
  boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md` after confirming the draft is
  still intended.
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

This run's predecessor measured the same failure SIX times across three unrelated surfaces in one goal: a probe-record detector whose variant generator emitted the exact malformed shape it was built to catch; an adapter loader whose unregister repair reproduced the second-error-hides-the-first shape its own comment names; a census gate that forbade a legitimate chain and so produced a manifest quietly omitting a real caller. Every one was found by the SECOND bounded round, which is the most expensive detector this repo owns.

The thesis is the predecessor's own retro conclusion, one level up from where it left it. The predecessor built the tool that thirteen review rounds had paid for by hand, and the tool worked -- it found a fifth dead control no round had. But the ROUNDS were still what caught the repairs, and six rounds across three slices is roughly the same bill the predecessor set out to stop paying.

Slice 1 is the affordance: when a slice's diff adds a REFUSAL, name the input class it refuses and ask, mechanically, whether the repair's own new code contains that class. Slice 2 spends it on the two known instances that are still open -- `covering_rows` is an enumerated set whose named rows are never checked to CALL what they cover (the gate refuses four OTHER shapes already; see `## User Acceptance` item 7, which retracts this paragraph's original "verified in neither direction"), and 55 `safe-checks-errors` rows carry one token over materially different coverage exactly as `guarded` did before it was split.

The predecessor's unfinished remainder is deliberately NOT in this goal. The seventeen adapter-consumer rows (recounted with `check_adapter_consumer_classification.py`, never read off prose — that is the predecessor's own recorded lesson) and its slice 6 (two-round bookkeeping as typed critique fields, `#628` to the operator queue) are handed forward again. The operator ruled the scope at detector-plus-its-two-spends on 2026-08-19, for the reason the predecessor stopped at its own rule: paying seventeen rows in the same run that builds the mechanism meant to check the payment is how a goal ends at three of five slices twice in a row. See `## Non-Goals`.

The two spends are the instances that are still open and that the detector can be TRIED on: `covering_rows` is enumerated and the gate never checks that a named row actually CALLS the covered symbol or that the list is complete (its own docstring says so, `scripts/check_adapter_consumer_classification.py:167-169`), and the `safe-checks-errors` rows reading through `cautilus_adapter_lib` / `proof_semantics_adapter_lib` are structurally blind on two of three doors because both libraries still call `load_yaml_file` bare (`scripts/cautilus_adapter_lib.py:205`, `scripts/proof_semantics_adapter_lib.py:241`, verified at `dd671ec1e`).

There are FIVE such rows, not the four the gate's own prose comment claims at lines 115-116 — `validate_adapters.py` is the fifth, and it calls `load_yaml_file` bare a second time at line 292. A wrong count sitting in a comment inside the very gate whose rule is "never read a count off prose" is this goal's thesis appearing before the goal starts, and slice 2b corrects it. The doors themselves come from two functions, not one: `read_declared_adapter` (`scripts/adapter_lib.py:146`) supplies the refused parse and the silently dropped line, while the refused version comes from `declared_fields_after_version_check` (line 309), which both libraries already call. `resolve_declared_adapter` (line 188) is a combined form with exactly ONE caller in the repo (`resolve_adapter_payload`, line 241) — it is NOT what the sixteen resolvers call, and a round-2 reviewer refuted this sentence's first repair for saying so. What `#673` established is stated by `scripts/adapter_version_verdict.py:134-137`: five resolvers used to call `load_yaml_file` bare, `#673` routed all five through `read_declared_adapter`, and the door is REACHABLE for all sixteen. Reachable is not called-by.

Slice 2 is therefore also slice 1's first live trial: the detector reads slice 2's own diff, and a detector that says nothing about a diff adding refusals must classify its own silence — `blind-class`, `not-established`, or `genuine-absence`. An unclassified silence is not a recorded result.

## Non-Goals

- **The seventeen remaining adapter-consumer rows.** Handed to the successor of
  this goal. Recount them; do not inherit a number from prose.
- **A BLOCKING verdict for the slice-1 detector.** Operator ruling 2026-08-19:
  reporting-only first, then decide from measured findings.
  `conservative-static-verdicts` is the standing lesson that a baseline is
  trialled before a rule blocks. `#587` is NOT a measurement of what a false
  blocker costs and must not be cited as one — the execution ledger
  (`2026-08-12-open-backlog-execution-ledger.md:22,138`) records its
  serial-aggregate remedy as refuted and the false-blocker question itself as
  `unproven-defer`, pending the unavailable original session record. It is the
  OPEN question, which is a reason for caution, not evidence.
- **A no-increase baseline for the detector.** A baseline over an unmeasured
  detector freezes its mis-seeding; the same objection already sits in the
  inherited queue for `reconcile_usage_episodes_host_hooks.py` /
  `quality_label_universe.py`.
- **Splitting the `safe-checks-errors` 55-row class into coverage levels.**
  Operator ruling 2026-08-19: route the two libraries instead, which removes the
  FIVE structurally-blind rows; whether the remaining 50 still need a split is a
  question re-asked AFTER slice 2 — and NOT from the census recount, which cannot
  answer it (see `## User Acceptance` item 8). Not a claim made now.
- **Folding `--replay-stimulus` into `check_probe_record.py --require-evaluated`.**
  Operator ruling 2026-08-19: do not fold; correct the predecessor's acceptance
  wording instead. The close/release floors call that CLI, and folding it makes
  every close boundary execute a record's own declarations through up to sixteen
  resolver subprocesses.
- **`#628`, and typed two-round critique bookkeeping.** Still the operator's
  design call and still only staged, not decided, here.
- **Any push, release, tag, version bump, or issue CLOSE.** Filing is
  standing-approved; closing `#676` is not, and this goal does not request it.

## Boundaries

- Scope is slice 1 (the affordance) and slice 2 (its two spends). If slice 1
  overruns, the honest stop is BEFORE slice 2, and slice 2's two spends are
  independent of each other — either may ship without the other.
- **Stop condition, stated as evidence not vibes:** if `#676`'s table cannot
  establish a six-instance corpus with commit SHAs, stop at slice 0. If the
  slice-1 detector flags fewer than three of the six, stop and REPORT THE NUMBER
  rather than lowering the floor or tuning the detector against its own corpus
  until the output looks right. The floor is three, chosen before implementation,
  and it also lives in `## User Acceptance` — a stop rule that exists only in
  this section is not what a goal is reported complete against, which a bounded
  reviewer named as the escape hatch in the first draft. Fitting a verdict
  surface to its own test set is the defect `recount_premise_state.py` exists to
  have removed.
- **Second review round is owed by contract.** Slice 1 IS a proof surface — it
  renders a verdict about other code — and slice 2 changes census verdict inputs.
  Round 2 reads the REPAIRS. A first round producing no repairs discharges it.
- Local-only by default. External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

1. **The corpus is checked in before the detector is written, and it carries
   NEGATIVE controls.**
   `charness-artifacts/probe/repairs-carrying-their-class.json` (or an equivalent
   checked-in path) enumerates the six positive instances from `#676`, each with
   its commit SHA and the class it carried, PLUS at least three negative
   controls: diffs that add a refusal and do NOT carry its class. Precondition,
   not evidence: if `#676`'s table does not carry six per-instance SHAs, slice 1
   stops and reports rather than inventing a corpus — nothing below is runnable
   without it.
2. **The detector FLAGS at least three of the six positives AND flags none of
   the negative controls.** A detector that flags every added refusal satisfies a
   recall floor and is worthless; round 1 closed the 0/6-recall hole and a
   round-2 reviewer found the mirror image still open. Both directions are the
   bar. The per-instance verdict is asserted by a checked-in test that RUNS THE
   DETECTOR over the corpus — a test asserting a hand-authored results file is
   the session's say-so relocated into a file, which is not a different evidence
   channel. `tests/quality_gates/test_probe_record_corpus_replays.py` is the
   precedent for the shape.
   **Fewer than three positives, or any negative flagged, is a FAILED item and
   the stop condition firing** — not a finding the goal reports on its way to
   green. The report replaces the completion; it does not accompany it.
3. **Every verdict is three-valued: `flagged`, `named-miss`, or
   `not-established`.** A miss is only a `named-miss` when the reason it is
   invisible is recorded; a base ref that did not resolve, an unreadable file, or
   a failed diff subprocess is `not-established` and is NEVER counted toward
   item 2's floor. This mirrors `SCOPE_NOT_ESTABLISHED`
   (`scripts/new_proof_surface_advisory.py:89`); the reason it exists is recorded
   in `new_surface_candidates`' docstring at lines 112-119, which says the first
   cut of that surface shipped the `[]`-means-two-things defect and names it
   class (a)/(d).
4. **The detector's blind class is written in its module docstring, in its own
   commit, before any test file for it lands.** `git log --follow` over the two
   paths shows that order. An ordering claim nobody can check after the fact is
   the anti-post-hoc device defeating itself.
5. **The finding is durable and non-blocking.** It attaches to the slice-closeout
   PAYLOAD (the `attach_new_proof_surface_advisory` shape at
   `scripts/run_slice_closeout.py:370`), not stderr only, so a read-only reviewer
   can read it; and `run_slice_closeout.py --skip-broad-pytest` on a flagged diff
   exits zero.
6. **The detector was tried on slice 2's own diff and the trial has an outcome.**
   Either it named at least one added refusal and stated whether the class
   recurs, or it was silent and the silence is classified `blind-class`,
   `not-established`, or `genuine-absence` with the evidence for that
   classification. A recorded silence with no classification does not satisfy
   this item.
7. **`covering_rows` gains the check the census gate says it lacks.** Not "both
   directions" — the gate ALREADY refuses an empty list, a non-string entry, a
   named row with no census row, and a named row that is not itself guarded
   (`scripts/check_adapter_consumer_classification.py:250-282`). The unverified
   gap is the one its own docstring names at lines 167-169: the named row is
   never checked to actually CALL the covered symbol, and the list is never
   checked for COMPLETENESS. At least the CALLS half gains a witness, with a
   mutation proof in both directions.
   **Non-claims this item ships with, stated because they ARE the class this goal
   detects.** The witness is buildable from `_call_names` and is therefore CALL
   PRESENCE, not load-bearing-ness — the same module already records at lines
   146-153 that a witness called in dead code, inside a never-called helper, with
   the wrong argument, with its result discarded, or shadowed by a same-named
   local all read as present, and that it is ALIAS-BLIND. Lines 170-172 add that
   coverage is call-site-granular while `guarded` is file-granular. So slice 2a
   ships a repair carrying a documented instance of the class it repairs, and
   this artifact says so out loud rather than discovering it in round 2 of the
   implementation. COMPLETENESS stays entirely open.
8. **The five consumers behind `cautilus_adapter_lib` /
   `proof_semantics_adapter_lib` reach all three doors.** FIVE, not four:
   `cautilus_scenarios_lib`, `control_plane_lifecycle_lib`, `plan_cautilus_proof`,
   `proof_mismatch`, and `validate_adapters` — the last one missing from the
   gate's own prose comment at
   `scripts/check_adapter_consumer_classification.py:115-116`, which slice 2b
   also corrects. `validate_adapters.py:292` calls `load_yaml_file` bare in
   `_require_declared_version` as well, so it needs both call sites. Evidence is
   a test asserting the three signals are reachable for each of the five, NOT the
   census recount: `safe-checks-errors` is absent from `GUARDED_LEVELS`
   (line 135), so no level is measured for these rows and the printed vector is
   unchanged by this slice. Any row that does change verdict carries a
   measurement, never an upgrade-by-assertion. The three doors have directly
   assertable predicates — `version_refused`, `parse_refused`,
   `declarations_dropped` (`scripts/adapter_version_verdict.py:119,124,129`) —
   and `tests/quality_gates/test_every_resolver_answers_a_refused_document.py`
   is the shipped precedent that asks them directly rather than matching text.
   **The five rows are not one uniform proof:** four are payload consumers, but
   `validate_adapters._require_declared_version` RAISES `ValidationError` and its
   bare `load_yaml_file` at line 292 raises before any payload exists, so "the
   signals are reachable" means something different there. A green on this item
   must not be read as five identical proofs.

What the user can do to verify completion directly — the OUTCOMES, not the
verification cadence. Whichever line of `## Active Operating Frame` states when
broad or expensive proof runs (`Gate cadence:` in the charness default frame; a
consumer adapter may seed its own) is the one owner of that answer. Restating it
here creates a second owner, and an agent reading its own acceptance criteria
obeys the acceptance criteria: one measured session paid roughly two and a half
hours re-running a 12-minute suite that way. Name what is true when the goal is
done, and point at `## Active Operating Frame` for when it is proven.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`
  at every commit boundary.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  AFTER the slice commit and BEFORE the broad lane. `no-verdict` is not a pass,
  and a green test is not a covered line — read the named lines.
- `python3 scripts/check_adapter_consumer_classification.py --repo-root .` for the
  slice-2 recount. Never read a count off prose, including this file's.
- `python3 -m ruff check --no-cache scripts skills tests`.

### High-Confidence Checks

- `python3 scripts/run_standing_pytest.py` at slice boundaries, after
  `python3 scripts/sync_root_plugin_manifests.py`.
- `python3 -m pytest -q -m release_only` at the bundle boundary.
- Bounded `bounded-reviewer` rounds per the floor `## Boundaries` states (round 2
  is owed where a slice changes verdict logic on a proof surface, and a first
  round producing no repairs discharges it) — that section is the one owner of
  this rule; this line does not restate a stricter version of it, because an
  agent reading its own verification plan obeys the verification plan. Spawned
  UNNAMED and read-only,
  with `reviewer_boundary_fingerprint.py` snapshot/verify around each. No
  repairing inside an open review window — that drifted twelve paths in one
  measured session and quarantined the reviewers' own verdicts.
- Mutation proof for each new refusal: delete the guard, name the test that
  fails, revert.
- **The corpus test** — a checked-in test asserting the per-instance verdict
  (`flagged` / `named-miss` / `not-established`) for all six, so acceptance items
  2 and 3 are reproducible by anyone and reviewable as a diff.
- `git log --follow` over the detector module and its test files, to establish
  acceptance item 4's ordering claim.
- **The detector's own trial:** run slice 1's detector over slice 2's diff,
  record what it said, and CLASSIFY any silence — unclassified silence does not
  satisfy acceptance item 6.

### External Or Live Proof

- None requested. No push, no release, no issue close in this goal's scope.
  `#676` stays open; closing it needs the `issue` floor and a phase-scoped grant
  the operator has not given.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Check in the corpus: `#676`'s six instances with per-instance commit SHA and the class each carried, as a data file, BEFORE the detector exists | Acceptance items 2 and 3 are unrunnable without it, and a corpus authored after the detector is a corpus fitted to it | The file, plus a stated stop if `#676`'s table does not carry six SHAs | not started |
| 1 | The affordance: read a slice diff, name the input class each ADDED refusal refuses, and report whether the repair's own new code contains an instance. Reporting-only, attached to the closeout PAYLOAD | Six instances, three surfaces, one goal — all caught by the second bounded round, the most expensive detector the repo owns, and none by a gate | ≥3 of 6 FLAGGED asserted by a checked-in test over the slice-0 corpus; every other instance `named-miss` or `not-established`, never conflated; blind class in the module docstring in its own commit ahead of any test file | not started |
| 2a | A `covering_rows` witness for the CALLS half: a named covering row must actually call the covered symbol | The gate already refuses four `covering_rows` shapes (`check_adapter_consumer_classification.py:250-282`); the hole its own docstring names is that a named row is never checked to CALL the symbol, and two of the first five lists shipped wrong | Mutation proof in both directions on the CALLS property; COMPLETENESS explicitly left open as a recorded non-claim | not started |
| 2b | Route the two libraries through the reporting loader, fix both bare `load_yaml_file` sites in `validate_adapters.py`, and correct the gate's own `four consumers` comment to five | Both libraries still call `load_yaml_file` bare at `dd671ec1e`, so two of three doors are structurally dead for the FIVE rows behind them | A test asserting all three signals reachable for each of the five named rows. NOT the census recount — `safe-checks-errors` is absent from `GUARDED_LEVELS` (line 135), so no level is measured for these rows and the printed vector cannot move | not started |
| 2c | Record the `--replay-stimulus` ruling where the next author reads it, and correct the predecessor's acceptance wording | The predecessor shipped acceptance item 1 naming a command that does not refuse; leaving it uncorrected re-teaches the wrong command | Entry in `docs/deferred-decisions.md` in its `## Record Shape` form; predecessor artifact's stale command AND its non-refusing worked example (that file's line 498) annotated, not silently rewritten | not started |

Slice 1 is an EXTENSION, not a build from zero. The diff-reading half already
exists in the same lane: `detect_new_floors` and `advise_floor_addition_restraint`
(`scripts/slice_closeout_advisories.py:385,458`) already find added refusals, and
`scripts/new_proof_surface_advisory.py` already supplies the reporting-only
stance, the payload attachment, the `evaluated` / `not-established` scope, and a
`DEFECT_CLASSES` vocabulary. The genuinely new capability is naming the refused
input class and re-scanning the repair's own added lines for it. Related but
distinct: `advise_repair_parity` (same file, 517-586) compares repaired functions
against a reviewer snapshot — different input, different question. It is NOT
silent when no snapshot exists: lines 555-568 are a repair that removed exactly
that silence and print the reason by name ("no reviewer snapshot for this HEAD…
That is UNEXAMINED, not clean"). This artifact's first repair said "silent with
no snapshot" because it read the function's stale DOCSTRING (lines 529-530) over
the code beneath it — a fact read off prose, inside the goal whose thesis is that
counts and facts must not be read off prose. Slice 1 should reuse that
distinguish-the-silences shape rather than reinvent it.

Slice 2 is also slice 1's first live trial. **If slice 0 cannot establish the
corpus, or slice 1 flags fewer than three of the six, stop BEFORE slice 2** and
report the number — do not lower the floor and do not tune the detector against
its own corpus.

## Backlog Recount

Recount the tracker before scope; see
[`skills/public/achieve/references/lifecycle-before.md`](../../skills/public/achieve/references/lifecycle-before.md)
(the template's bare `references/lifecycle-before.md` does not resolve from a
goal artifact's own directory).

- Counted: 25 open issues on 2026-08-19 via
  `gh issue list --repo corca-ai/charness --state open`, cross-checked by
  `recount_premise_state.py --with-bodies` (`counted: 25`, list not truncated,
  this artifact excluded from the residue scan).
- Claims: `#676` for RESOLUTION only. Premise state: `premise-holds`, judged
  against the tree at `dd671ec1e` — no script or test asks whether a slice's new
  refusal class appears in the repair's own new code, and both libraries the
  issue's spend names still call `load_yaml_file` bare. No residue marker
  declines it. CLOSING it is out of scope and needs its own grant.
- Not claimed: the remaining 24, every one `unverifiable-by-machine` because no
  premise judgement was supplied for it. That is the honest state, not a clean
  bill: counting is not re-verifying. Named adjacents, each deliberately left —
  `#550` (resolver bodies near-identical) may have MOVED under `#673`'s
  five-resolver reroute and slice 2b touches the same family, so re-read its
  premise before claiming it, never assume it; `#672` (a consumer that ASSERTS
  reports the same kind as a passing mention) sits one step from slice 2a's
  witness; `#628`, `#668`, `#546` are operator design calls this goal only
  carries; `#582`/`#583`/`#584` are umbrellas whose premises nobody re-read here.

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

RESOLVED AT SHAPING (2026-08-19), recorded so a fresh session does not re-ask:

- Decision: detector teeth. Ruled REPORTING-ONLY first; blocking is reconsidered
  only from measured findings. Revisit trigger: the first slice where a
  reporting-only finding is ignored and the class ships anyway.
- Decision: the `safe-checks-errors` 55-row class. Ruled ROUTE THE TWO LIBRARIES
  (slice 2b) rather than split the class; whether the remaining 50 need a level
  split is re-asked after slice 2 from the per-row door reachability, NOT from
  the census recount — `safe-checks-errors` is absent from `GUARDED_LEVELS`, so
  the recount's printed vector cannot move on this slice and is blind to the
  question. Revisit trigger: slice 2b landing, or any change to either library.
- Decision: `--replay-stimulus` folding into `--require-evaluated`. Ruled DO NOT
  FOLD; correct the predecessor's acceptance wording instead (slice 2c). The
  corpus sweep gate stays the standing-lane substitute that keeps the detector
  from being inert. Revisit trigger: any change to the issue-close floor.
- Decision: goal scope. Ruled DETECTOR PLUS ITS TWO SPENDS; the seventeen rows
  and `#628` hand forward again. Revisit trigger: this goal's closeout.

INHERITED, still the operator's, and deliberately NOT re-decided here:

- Decision: should `plan_retro_run` / `plan_debug_run` keep their diagnostic plan
  under an unhonored declaration, or is the one-line refusal right for that input
  class? Owner: repo operator. Why deferred: design call, and the current shape is
  pinned by test so it cannot drift silently. Unblock action: rule keep-refusal or
  restore-plan. Revisit trigger: any slice touching either planner.
- Decision: `#628` — does quality's same-day scaffold overwrite stay or go?
  Owner: repo operator. Why deferred: design call, and closing `#628` either way
  is irreversible. Unblock action: rule stay or go. Revisit trigger: the
  successor goal that claims `#628`.
- Decision: the contestable seeded verdict pair
  (`reconcile_usage_episodes_host_hooks.py` vs `quality_label_universe.py`).
  Owner: repo operator. Why deferred: ratcheting over a mis-seeded row freezes the
  mis-seeding. Unblock action: rule which verdict is correct. Revisit trigger: any
  attempt to build the no-increase ratchet — which this goal does NOT attempt.

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

- Discuss before activation: resolved — four consequential defaults were raised in the transcript on 2026-08-19, settled by the operator, and then re-shaped by two bounded plan reviews before this artifact was reported ready. (1) Detector teeth: reporting-only, not blocking, because the mechanism has no measured hit rate; `#587` is NOT the evidence for that and the first draft's citation of it was refuted. (2) The 55-row `safe-checks-errors` class: route `cautilus_adapter_lib` / `proof_semantics_adapter_lib` through the reporting loader rather than split the class — and note the affected consumer count is FIVE, not the four the gate's own prose says, so the remainder question is re-asked from a corrected count, not from the census recount vector (which this slice cannot move). (3) `--replay-stimulus`: not folded into `--require-evaluated`; the predecessor's acceptance wording is corrected instead, because folding puts up to sixteen resolver subprocesses per record inside every close boundary. (4) Scope: detector plus its two spends; the seventeen rows and `#628` hand forward. Proof-level non-claims, stated here because they are consequential: a green on this goal claims the detector FLAGS at least three of six recorded historical instances and that its misses are classified — it does NOT claim the detector catches this class generally, and it does not claim `covering_rows` is completely verified (only the CALLS half gains a witness; COMPLETENESS stays open). No live, prod, push, release, or issue-close boundary is crossed by this goal, and none is requested.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [design north star](../../docs/design-north-star.md) — read while SHAPING.
   Its rule is: brief a capable judge, and keep TEETH only where a wrong answer
   escapes. That is what settled slice 1's teeth question. A repair carrying its
   own class does not escape today — the second bounded round catches it, every
   time, six for six. What is expensive is the ROUND, not the escape. So the
   affordance's job is to make the round cheaper, and a blocking gate over a
   mechanism with no measured hit rate would add a new false-verdict surface
   where nothing is currently escaping. This goal crosses NO irreversible
   boundary: no push, no release, no issue close.
2. [`#676`](https://github.com/corca-ai/charness/issues/676) — the six-instance
   table is this goal's regression corpus and its acceptance-item-1 input.
3. [predecessor goal](./2026-08-19-adapter-debt-tooling-and-remainder.md) — its
   `## User Acceptance` items 4 and 5 (one partial, one unmet), its operator
   queue, and its stop-before-slice-4 rule this goal re-applies.
4. [predecessor retro](../retro/2026-08-19-adapter-debt-tooling-and-remainder.md)
   `## Sibling Search` / `## Persisted` — where `#676` was recorded from.
5. [census manifest](../../scripts/adapter-consumer-classification.json) plus
   `python3 scripts/check_adapter_consumer_classification.py --repo-root .` —
   the live per-verdict counts. At `dd671ec1e`: 6 accepted-risk-unguarded,
   3 guarded-errors-only, 5 guarded-upstream, 55 safe-checks-errors,
   32 guarded-all-doors (independently recounted from the manifest by a bounded
   reviewer, not read off this file).
6. Lessons, cited to where the SLUGS actually live —
   [lesson ledger](../retro/lesson-ledger.json) and
   [selection index](../retro/lesson-selection-index.json).
   `detector-blind-class-unstated` is folded into acceptance item 4,
   `changed-line-proof-before-broad-quality` and `green-test-is-not-covered-line`
   into the low-cost checks, and `conservative-static-verdicts` into the teeth
   non-goal. [recent-lessons.md](../retro/recent-lessons.md) carries three of
   these as untagged prose (its lines 17-19) and carries
   `green-test-is-not-covered-line` not at all — the digest is a rendering, not
   the slug surface, and citing it for slug identifiers was a first-draft error a
   bounded reviewer caught.
7. [operating contract](../../docs/conventions/operating-contract.md) Critique
   Discipline — why slice 1 owes a second review round: it renders a verdict
   about other code.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

**Mode:** artifact-only. The operator asked for the Before phase to be filled and
the goal prepared for activation, not for slices to run. Nothing executes until
`/goal`.

1. **Detector teeth.** Family: blocking gate / reporting-only / reporting plus a
   no-increase baseline. Chosen: reporting-only. Rejected: a blocking gate,
   because this mechanism has no measured hit rate yet — NOT because `#587`
   measured a false blocker's cost. That citation was in the first draft and a
   bounded reviewer refuted it against the execution ledger, where the
   false-blocker question stands as `unproven-defer`. The reason is the missing
   measurement, not a precedent; rejected the baseline, because a baseline over an unmeasured detector
   freezes its mis-seeding, which is the exact objection already sitting in the
   inherited queue for a contestable seeded verdict pair.
   `axis: validator-timing-layer` — this repo already varies strictness by
   boundary (`docs/conventions/validator-timing-layers.md`), so "reporting-only"
   is a value at the slice-closeout layer, NOT a global stance on teeth. A later
   pre-push or standing-lane instance of the same detector is a separate
   decision, and reading this line as "the detector is advisory everywhere"
   would be the over-anchoring error.
2. **The `safe-checks-errors` 55-row class.** Family: split into coverage levels
   as `guarded` was split / route the two blind libraries / both / defer.
   Chosen: route. Rejected the split as the first move because it is a slice of
   its own and would rebuild the scope that stopped the predecessor at three of
   five; rejected defer because FIVE rows are structurally blind on two doors
   TODAY (the decision was taken believing it was four — the count came from the
   census gate's own prose comment and a bounded reviewer corrected it; the
   choice does not change, but a fresh session should inherit the real number).
   `single-point: <two named modules>` — `cautilus_adapter_lib` and
   `proof_semantics_adapter_lib` are the only two readers still calling
   `load_yaml_file` bare after `#673`; this is a concrete pair, not a policy.
3. **`--replay-stimulus` folding.** Family: fold into `--require-evaluated` /
   do not fold and correct the wording / fold for records authored after this
   goal. Chosen: do not fold. Rejected folding because the issue-close and
   release floors call that CLI and folding puts up to sixteen resolver
   subprocesses per record inside every close boundary; rejected the
   new-records-only variant because it creates two paths through one command,
   which is the `one-engine-per-pattern` shape.
   `axis: validator-timing-layer` — the replay lives in the standing lane
   (`tests/quality_gates/test_probe_record_corpus_replays.py`), and the ruling is
   about the CLOSE boundary specifically, not about the replay being optional.
4. **Scope.** Family: detector only / detector plus its two spends / the full
   four-to-five-slice draft. Chosen: detector plus its two spends. Rejected
   detector-only because a detector never tried on a live diff is the
   `green-test-is-not-covered-line` shape one level up; rejected the full draft
   because two consecutive goals have now stopped at their own scope rule.
   `single-point: this goal` — a scope choice, re-decided per goal.
5. **Timebox.** No work budget was given, so no timebox fields are recorded.
   `single-point: <no budget supplied>`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Round 1, 2026-08-19, two unnamed read-only `bounded-reviewer` spawns against the
first shaped draft at base `dd671ec1e`, angles held disjoint (acceptance rigor /
factual premises). Parent proved the window with
`reviewer_boundary_fingerprint.py`: `verdict: clean`, no drift, so neither
review is quarantined. Both reviewers recorded `envelope-unbound` as
inapplicable — each held Read/Grep/Glob only.

**Blockers folded (acceptance rigor).** Five, all folded into
`## User Acceptance` and `## Slice Plan`. **Item numbers in this round-1 list are
the FIRST DRAFT's five-item numbering**, which the repairs replaced with eight
items; the round-2 list below uses the CURRENT numbering, and each entry says
which:

1. `NAMED MISS` made item 1 unfalsifiable — zero-flagged/six-named-miss passed
   as written, and the reviewer named a concrete implementation that scores 5/5
   green with 0/6 recall. The stop rule lived in `## Boundaries`, which is not
   what a goal is reported complete against. Folded: a numeric floor (≥3 of 6)
   promoted INTO acceptance, chosen before implementation.
2. Item 1's evidence was reachable only by the implementing agent's say-so, while
   `## Closeout Binding Plan` claimed the reviewer supplies a different evidence
   channel. Read-only reviewers cannot run the detector. Folded: the corpus is a
   checked-in file and the per-instance verdict is a checked-in test, so the
   verdict is a diff anyone can read.
3. The two-valued vocabulary had no value for "did not run", and the advisory
   channel it plugs into degrades to `[]` on an unresolved base ref. This repo
   already shipped and repaired that exact defect on a sibling surface
   (`new_proof_surface_advisory.py:112-119`, class (d): "PASS reported for a
   check that silently did not run"). The parent verified that quotation in the
   source. Folded: three-valued, with `not-established` excluded from the floor.
4. Slice 2's "first live trial" bound nothing — no outcome of it could change the
   goal's verdict, which is the very shape interview decision 4 rejected
   detector-only for. Folded as acceptance item 6, with a classified-silence
   requirement.
5. Item 2's "written before the first acceptance test" was unprovable after the
   fact. Folded: the docstring lands in its own commit ahead of any test file, so
   `git log --follow` decides it.

**Blockers folded (factual premises).** Four wrong or overstated claims, each
re-verified by the parent before folding rather than taken on the reviewer's
word:

- The affected consumer count is FIVE, not four — `validate_adapters.py:302`
  was missing, and it calls `load_yaml_file` bare a second time at line 292. The
  four came from the census gate's own prose comment (lines 115-116). Parent
  confirmed all five carry `safe-checks-errors` in the manifest.
- `covering_rows` is not unverified "in both directions": the gate already
  refuses four shapes. The real hole is the CALLS check and completeness. Item 7
  and slice 2a were rescoped, and completeness is now an explicit non-claim.
- `#587` did not measure a false blocker's cost; it is `unproven-defer`. The
  citation was load-bearing in two places and both were corrected.
- The census recount cannot evidence slice 2b: `safe-checks-errors` is absent
  from `GUARDED_LEVELS`, so those rows are never level-measured and the printed
  vector cannot move. Item 8's evidence channel was replaced with a test.

Also folded: slice 1 is an EXTENSION of existing diff-reading advisories, not a
build from zero (slice-1 row); the lesson slugs were cited to the digest that
does not contain them (Context Sources item 6); and the template's
`references/lifecycle-before.md` path does not resolve from a goal's directory.

**Over-worry raised and NOT folded.** The reporting-only, exit-zero channel
already exists and is mature (`run_slice_closeout.py:89-110` computes the
effective exit code from `status`, which advisories never set), so item 5's
exit-zero half costs nothing to satisfy — recorded, but the item stays because
its payload-attachment half is the part that does work. `advise_repair_parity`
is adjacent but asks a different question; a pointer was added to the slice-1
row instead of a scope change. And the closeout-exit-zero check can go red for
reasons unrelated to the detector; loud and self-explaining, no plan change.

**Carried as unverifiable, not as satisfied.** The reviewers had no network and
no shell: `#676`'s six-instance table, the 25-issue recount, and cleanliness
against `dd671ec1e` were checked by the parent, not by fresh eyes. Slice 0 exists
because of the first of those.

---

Round 2, 2026-08-19, one unnamed read-only `bounded-reviewer` against the
REPAIRED artifact, briefed to read the repairs rather than the original.
Fingerprint window `clean` again. **This round found nine blockers, and the
sharpest three are this goal's own thesis landing on its own planning artifact**
— a repair carrying the class it repaired. Numbers below are the CURRENT
eight-item acceptance list.

Folded, and the three that are the thesis first:

- **The four→five correction did not propagate.** `## Non-Goals`,
  `## Operator Decision Queue`, and `## Interview Decisions` still said four, and
  two carried the dependent arithmetic (51 residue, now 50). The repair for a
  wrong count left the wrong count in the two sections written specifically so a
  fresh session inherits the design space. Fixed in all three.
- **A wrong citation was repaired with a second wrong citation.** The repair
  added "`resolve_declared_adapter` is the combined form the sixteen resolvers
  use". It has ONE caller. `adapter_version_verdict.py:134-137` says the door is
  REACHABLE for sixteen; reachable is not called-by. Parent re-verified by grep
  before folding.
- **A fact was read off prose inside the goal that forbids it.** The repair said
  `advise_repair_parity` is "silent with no snapshot", copied from that
  function's stale docstring; the code twenty lines below is a repair that
  removed that silence and prints the reason by name. Parent re-verified in
  source. Fixed, and slice 1 now points at that shape as prior art.
- **Item 2 reopened the hole it was promoted to close.** "if the honest result is
  fewer, that is a real finding and the goal reports it" let 1/6 read as
  satisfied. Now: fewer than three is a FAILED item and the stop firing; the
  report REPLACES the completion.
- **Nothing constrained the false-positive direction.** A detector that flags
  every added refusal satisfied every item. Item 1 now requires negative controls
  in the corpus and item 2 requires none of them flagged.
- **Item 7's witness ships the class it repairs, undeclared.** A `_call_names`
  witness is call-presence, alias-blind, and file-granular — all three recorded
  by the census module itself. Now an explicit non-claim on item 7 and slice 2a.
- **`## Goal` still asserted what item 7 retracts** ("verified in neither
  direction"). Fixed with a pointer to the retraction.
- **Two sections still routed the remainder question through the census
  recount** that item 8 proves blind to it. Fixed.
- **This section mixed first-draft and current acceptance numbering.** Fixed by
  labelling both lists.

Over-worry folded anyway because each was cheap and correctness-shaped: the
`SCOPE_NOT_ESTABLISHED` citation now names both the constant and the docstring
that explains it; the verification plan no longer restates a stricter review
floor than `## Boundaries` owns; item 2 now requires the test to RUN the
detector; the predecessor's items are cited as one partial and one unmet rather
than two unmet; and item 8 records that `validate_adapters` raises rather than
returning a payload, so its proof is not the same shape as the other four.

**Accepted unreviewed.** The two-round cap applies: these round-2 repairs have
not themselves been read by a third round. The `## Goal` and
`## Interview Decisions` rewrites and the negative-control requirement are the
largest of them and are the most likely place for a third instance of this class.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: this goal artifact, `#676` (semantic issue input), the
  predecessor goal `2026-08-19-adapter-debt-tooling-and-remainder.md` (its
  acceptance item 4 PARTIALLY MET at that file's line 510, item 5 NOT MET at
  line 517 — not two unmet items), and the census manifest
  `scripts/adapter-consumer-classification.json`. Retro, packet, reviewer, and
  lock records are terminal evidence, not semantic inputs.
- Frozen target: commit slice 2's last semantic change, then bind the closeout
  packet to that exact SHA. Do not bind to a dirty tree; the changed-line proof
  reads `base..HEAD` and proves nothing over an uncommitted pool.
- Fresh-eye: unnamed read-only `bounded-reviewer` spawns, distinct from the
  implementing context, with `reviewer_boundary_fingerprint.py` snapshot/verify
  around each round. Different evidence channel, and it must be a channel a
  READ-ONLY reviewer can actually reach: the committed corpus file, the
  committed corpus test and its assertions, and the payload-attached detector
  finding. A reviewer with Read/Grep/Glob cannot run the detector, so any
  "recorded output" that is only session prose is the implementing session's
  account of itself wearing a different label — the first draft claimed exactly
  that and a bounded reviewer refused it.
- Verification lock: `python3 scripts/run_slice_closeout.py --verification-lock`
  at the bundle boundary; evidence under `charness-artifacts/` per the closeout
  script's own receipt. Any edit to a semantic input above requires rebinding.
- Complete flip: record packet, reviewer, and lock evidence first; write terminal
  status and evidence bookkeeping outside the reviewed identity, and only then
  flip `Status:` to `complete` after `check_goal_artifact.py` passes.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

Found while SHAPING (2026-08-19), before activation:

- **The census gate's own comment carries a wrong count.**
  `scripts/check_adapter_consumer_classification.py:115-116` says "four consumers
  read through them"; there are five (`validate_adapters.py` is missing). The
  file whose stated rule is that a count must never be read off prose is itself
  the prose someone read a count off — this artifact's first draft did exactly
  that. In scope: slice 2b corrects it. Recorded here because the finding is
  about the gate, not about this goal's work.
- **`validate_adapters.py:292` (`_require_declared_version`) calls
  `load_yaml_file` bare**, so an unparsable adapter raises out of it uncaught —
  a second call site in a file already counted once. In scope: slice 2b.
- **The predecessor's own worked example is non-refusing.**
  `2026-08-19-adapter-debt-tooling-and-remainder.md:498` shows
  `--replay-stimulus` without `--require-evaluated`, which reports and exits 0.
  In scope: slice 2c annotates it.
- **The goal-artifact template's `references/lifecycle-before.md` pointer does
  not resolve** from `charness-artifacts/goals/`. NOT in this goal's scope — it
  is a defect in the packaged `achieve` scaffold, and every goal artifact
  scaffolded from it carries the same dead link. Candidate for an `issue` filing
  by whoever next touches that skill; this artifact only annotates its own copy.

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

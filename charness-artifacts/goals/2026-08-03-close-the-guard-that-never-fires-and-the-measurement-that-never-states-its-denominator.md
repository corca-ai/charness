# Achieve Goal: Close the guard that never fires, and the measurement that never states its denominator

Status: complete
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: C (closeout) — complete. Lanes A and B shipped and reviewed.
- Current slice intent: make two dormant/underspecified proof surfaces state the
  truth — wake `has_repo_delegation_contract` (Lane A) and make
  `audit_disposition_corpus.py` state its dated denominator (Lane B). Both are
  read-and-report repairs to EXISTING surfaces; neither adds a floor. One
  reviewable intent spanning both lanes, because they are the same defect at two
  scales and a reviewer reading one benefits from the other.
- Next action: none — the goal is closed. Follow-ups live as
  [#472](https://github.com/corca-ai/charness/issues/472),
  [#473](https://github.com/corca-ai/charness/issues/473), and
  [#474](https://github.com/corca-ai/charness/issues/474), and the next session's
  entry point is `docs/handoff.md`.
- Measurement standing (Lane A). **0 refused**, at every point it was taken:
  before the repair, after the repair, and again at closeout. The DENOMINATOR
  moves, because this run writes critique artifacts into the corpus it measures —
  so each figure is stated as-of. **Pre-repair and post-repair: 0 of 686**
  (986 `critique/*.md` minus 300 `charness.critique_prepare_packet` documents
  excluded by content kind; 587 of the 686 carried a `Fresh-eye satisfaction`
  value). **At closeout, after this run's own resolution critique landed: 0 of
  687** (987 minus 300; 588 with a value). The closeout-claims review re-derived
  both and caught that the shipped tree was 687, not 686. Recount at any time
  with `python3 scripts/validate_critique_artifacts.py --repo-root . --all`.
  The check reads only the `Fresh-eye satisfaction` value and has no date
  grandfather. Disposition: **ship the repair unchanged** — no grandfather, no
  narrowing, no operator toll, because the woken gate refuses nothing at any
  denominator. Stop condition (1) did not fire.
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

Close two defects the 2026-08-02 run FOUND but deliberately did not fix, both of
the same shape the north star names as the hardest to see: **a proof surface
whose wrong pass is silent by construction.**

1. **A guard that has never fired.**
   `validate_critique_artifacts.has_repo_delegation_contract` substring-tests an
   unbolded marker against an `AGENTS.md` that writes `**already delegated**`, so
   it returns `False` in this repo and everything it gates
   (`_check_forbidden_blocker_phrases`) has never run. Tracked as
   [#471](https://github.com/corca-ai/charness/issues/471). The repair is one
   line; the WORK is measuring what goes red when a dormant gate wakes up across
   400+ checked-in artifacts.
2. **A corpus measurement that omits its own denominator.**
   `skills/public/achieve/scripts/audit_disposition_corpus.py` globs the goal
   corpus and reports `pre_rule_grandfathered` / `in_scope` — where `in_scope`
   is the fail-closed population that includes every UNDATABLE artifact — and
   never states the dated denominator. That is the exact defect #470's
   follow-up (a) described, alive in the one corpus-measurement surface the
   `achieve` skill ships. Found by the pre-close review on 2026-08-02, after the
   plan critique had cut the lane that would have covered it.

Both are P4 applications: a claim confirmed by a distinct observer rather than by
re-reading the same proxy. Neither adds a gate — one repairs a gate's activation
condition, the other makes an existing report state its scope.
## Non-Goals

- **Not arming anything on an unmeasured population.** #471's repair makes a
  dormant gate live. If the measurement shows it refuses honest artifacts, the
  answer is a grandfather or a narrowed rule, NOT shipping the repair and letting
  authors discover it. Arming on a corpus that could not object is a mistake this
  repo has made twice; the second time is recorded in D49.
- **Not a sweep of every `*_RULE_DATE` floor.** Whether the other nine carry
  unstated denominators was named as a non-claim on 2026-08-02 and stays one
  unless a slice explicitly takes it.
- **Not answering D40.** Whether the pre-push lane should refuse on a partial
  denominator is the operator's toll and inherited #469's residual. Reading D40
  is in scope; arming it is not.
- **Not a release**, no version bump, no `cautilus evaluate`.
- **Not a new blocking floor.** Both repairs are to surfaces that already exist.
  If a slice starts wanting a validator that audits validators, stop — the north
  star names that as the anti-pattern applied to itself.
## Boundaries

- **External side-effect scope, enumerated in full.** (1) `git push` to `main` of
  work this goal creates, plus the `quality-core` runs those pushes trigger.
  (2) Closing [#471](https://github.com/corca-ai/charness/issues/471) if a lane
  resolves it, through the close path's own floor — which now requires a
  DELEGATED resolution critique, so the fresh-eye round runs BEFORE the close.
  (3) Filing new issues for anything a lane surfaces and does not fix.
  NOT approved and NOT carrying forward: a publish, a tag, a version bump, or any
  `cautilus evaluate` run. **Enumerated in full because the last three runs each
  found a write their non-claims block had omitted.**
- **Phase-scoped approval.** Push approval covers the phase that requests it and
  does not carry to a later phase; batch local proof and run remote CI once over
  the bundled state.
- In scope (Lane A — the dormant guard):
  [validate_critique_artifacts.py](../../scripts/validate_critique_artifacts.py)
  `has_repo_delegation_contract` / `DELEGATION_CONTRACT_MARKERS`, and whatever
  `repo_has_delegation` gates.
- In scope (Lane B — the corpus report):
  [audit_disposition_corpus.py](../../skills/public/achieve/scripts/audit_disposition_corpus.py).
- Also in scope: regression tests for each change, and the generated
  `plugins/charness/` mirror of every touched file. Sync mirrors before
  validators (`mutate -> sync -> verify`).
- Stop conditions: (1) if Lane A's measurement shows the woken gate refuses
  artifacts that are honest, STOP and bring the number to the operator before
  shipping the repair — that decision is a toll, not an implementation detail.
  (2) If either repair would require editing a frozen artifact, record instead.
  (3) If Lane B's fix starts growing into the floor-family sweep the Non-Goals
  exclude, cut it back to the one shipping surface.
## User Acceptance

- **Lane A:** `has_repo_delegation_contract(REPO_ROOT)` returns `True` against
  this repo's REAL checked-in `AGENTS.md`, pinned by a test that reads the real
  file rather than a synthetic fixture — the absence of exactly that test is why
  this stayed invisible. AND the number of checked-in critique artifacts the
  newly-live `_check_forbidden_blocker_phrases` would refuse is **measured and
  stated with its denominator** before the repair ships. If that number is
  non-zero, the disposition (grandfather / narrow / accept) is an explicit,
  defended decision recorded in the goal, not a silent consequence.
- **Lane B:** `audit_disposition_corpus.py`'s summary states the DATED
  denominator alongside `in_scope`, so a reader can tell how much of the
  in-scope population is in scope only because it is undatable. Pinned by a test
  over the real corpus that fails if the dated count collapses.
- **Global:** every figure in `## Final Verification` carries
  `<value> — <source>` or `<value> — unbacked: <why>`, and every corpus
  measurement states its denominator AND what population that denominator
  actually selects (the 2026-08-02 run got the number right and the LABEL wrong,
  and its closeout review caught it).
## Agent Verification Plan

### Low-Cost Checks

- **verify a named remedy's premise BEFORE shaping a slice around it.** Both
  lanes here were NAMED by a reviewer, not verified by me; treat each as a
  hypothesis and re-read the surface first.
- **run the measurement BEFORE the fold, and again after** — the 2026-08-02 run
  shipped three successive over-blocks and caught the third only by re-measuring.
- the dup-ratchet at the FIRST edit to a gated file in each slice, never at the
  closeout aggregate.
- `check_python_lengths.py --headroom` before a large addition; when it refuses,
  SPLIT the concept rather than shaving lines (P2).
- targeted `pytest` AND `ruff check` in the same breath.
- after any scripted string edit, assert the superseded text is absent; when a
  number replaces a number, grep for the old value.
- never edit a markdown artifact by `text.index("## Heading")` — match at line start.

### High-Confidence Checks

- one bounded fresh-eye round per slice; **TWO for Lane A**, which changes what a
  validator refuses on a proof surface.
- `reviewer_boundary_fingerprint.py snapshot` around each review, **and a
  `verify --before` run the MOMENT the reviewer returns, before any parent
  write** — verifying late downgrades the attestation to parent testimony, which
  happened twice on 2026-08-02.
- a closeout-claims review by a DISTINCT observer before the complete flip. It
  found 8 blockers last run, all in claims, including a blocker count written
  before the reviewer that would produce it had reported.
- a slice packet's NON-CLAIMS get the same premise check as its claims.

### External Or Live Proof

- `git push` to `main` and the remote CI it triggers, confirmed per P4 by a
  different observer AND a different evidence channel than the push exit code.
- Closing #471 if Lane A resolves it — through the close path's floor, with a
  DELEGATED resolution critique whose round runs BEFORE the close call.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.
## Slice Plan

Two lanes plus closeout. Each independently closable; stopping between lanes is
clean. Lane A is ordered first because its measurement may hand the operator a
decision, and that decision wants the most session left.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Measure what wakes up when `has_repo_delegation_contract` starts returning `True`, then repair it with that number in hand | A guard that has never fired is a proof surface failing open — silent by construction, shipped to every consuming repo, and every session since has trusted it. The repair is one line; the measurement is the work, and doing it in the other order is how D49 happened | The refused-artifact count with its denominator, stated BEFORE the repair lands; a test pinning the contract live against the REAL `AGENTS.md`; an explicit disposition if the count is non-zero; two bounded rounds | done |
| B | Make `audit_disposition_corpus.py` state its dated denominator beside `in_scope` | It is the one corpus-measurement surface the `achieve` skill ships, and it reports a fail-closed population that silently includes every undatable artifact — the exact defect #470's follow-up (a) named, which that issue closed as not-built | The summary carrying the dated count; a test over the real corpus that fails if the dated count collapses; the numbers stated with what population they select | done |
| C | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run (a `completed` gate is NOT broad proof); `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | done |
## Operator Decision Queue

One item, non-blocking, recorded below. The decision this goal was WRITTEN to hand
back — the disposition if the woken guard refused honest artifacts — never arose:
the measurement was 0 at every denominator, so stop condition (1) did not fire and
that toll was never owed. The item below is a different, smaller one the run
surfaced and deliberately declined to decide for the operator. The three
external side effects were approved in-transcript at activation before any of
them ran, and the operator then delegated remaining judgment calls to this run.
The two decisions that DID need a defended call — not widening the phrase list,
and not repairing #473's structural guard — were both resolved by filing rather
than by acting, which is the conservative direction and needs no confirmation.

- Decision: whether to widen `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES`, given that the
  now-live gate refuses 0 only because of how the list is spelled
- Owner: operator
- Why deferred: widening refuses at least 3 checked-in artifacts; arming teeth on
  a corpus that could not object is a mistake recorded twice in this repo (D49),
  and the goal's Non-Goals fence it out explicitly
- Unblock action: decide grandfather-by-date / narrow the rule / accept the churn,
  after re-measuring with a widened matcher and stating the count with its
  denominator
- Revisit trigger: [#472](https://github.com/corca-ai/charness/issues/472) being
  picked up, or the next critique artifact that trips the near-miss spelling

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
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

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- Routing: quality — selected from installed skill metadata for the validation-posture boundary: the closeout gate blocked on a public-skill validation review and on the duplicate ratchet, and `quality` owns repo-local gate design and the dup-review classification contract that resolved both.
- Routing: issue — selected from installed skill metadata for the tracked-issue boundary: filing #472/#473/#474 and closing #471 through the close path's floor, with the delegated resolution critique running before the close call.
- Routing: achieve — goal lifecycle owner for this run; selected from installed skill metadata, with impl-shaped slice work and critique-shaped bounded review rounds run inside it rather than as separate goals.
- Gather: n/a — every source in ## Context Sources is a checked-in repo file or a GitHub issue in this repo's own tracker, read directly with gh/Read; no external page or exported document became working context, so there is nothing for gather to durably capture.
- Release: n/a — no version bump, no install-manifest edit, no publish or tag; the plugins/charness mirror was regenerated by sync_root_plugin_manifests.py as a generated surface, which is not a release surface.
- Issue closeout: #471 — carrier direct-commit; delegated resolution critique ran BEFORE the close (charness-artifacts/critique/2026-08-02-issue-471-resolution-critique.md); #472 and #473 were FILED by this run and are left open, not closed.
- Public-skill validation decision: achieve + issue changed, both below the consumer contract. achieve's change is audit_disposition_corpus.py, a read-only audit runner that no acceptance-evidence line in docs/public-skill-dogfood.json references; issue's change is comment-only in issue_critique_observer.py with no behavior delta. No SKILL.md, adapter, or dogfood contract moved, so maintained scenario coverage in evals/cautilus/scenarios.json is unchanged and no cautilus evaluate run was requested or performed. Recorded, then acked with --ack-cautilus-skill-review.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision that must be
resolved before `/goal`.

- Discuss before activation: APPROVED / RESOLVED 2026-08-03 at activation. (1) APPROVED by the operator in-transcript for this run, all three enumerated writes: `git push` to `main` plus the CI each push triggers; closing #471 if Lane A resolves it (through the close path's floor, delegated resolution critique BEFORE the close call); and filing new issues for anything a lane surfaces and does not fix. Still NOT approved and NOT carrying forward: publish, tag, version bump, `cautilus evaluate`. (2) RESOLVED by design — the goal stops and hands the disposition to the operator rather than picking one; the stop condition is written into `## Boundaries`. (3) RESOLVED by design — two bounded rounds on Lane A, and arming decisions are fenced out of `## User Acceptance`.
- Original discussion text, preserved: THREE items, none blocking local progress. (1) IRREVERSIBLE SIDE EFFECTS — `git push` to `main` plus the CI each push triggers, and closing #471 if Lane A resolves it. Both need explicit operator approval at activation; the 2026-08-02 approval was scoped to that goal and does NOT carry forward. (2) A DECISION LANE A MAY HAND BACK — if the woken guard would refuse honest checked-in artifacts, the disposition (grandfather / narrow the rule / accept the churn) is an operator toll, not an implementation detail, and the goal will stop and ask rather than pick one. This is the one item most likely to end the run early, and that is the intended behaviour. (3) PROOF-SURFACE AUTHORING — both lanes change surfaces that render verdicts about other artifacts, which the north star classifies as an irreversible boundary in its own right; resolved by requiring TWO bounded rounds on Lane A and by fencing arming decisions out of acceptance.
## Slice Log

### Slice A+B — both repairs, one reviewable intent

- Objective: wake `has_repo_delegation_contract` with the refused-artifact count
  in hand BEFORE the repair (Lane A), and make `audit_disposition_corpus.py`
  state the dated denominator beside `in_scope` (Lane B).
- Why now: both are proof surfaces whose wrong pass emits nothing. Run together
  because they are the same defect at two scales and one reviewer reading both
  sees the pattern; they were still measured and repaired independently.
- Premise check first (the plan's own Low-Cost Check): both lanes were named by a
  reviewer, not verified by me. Lane A's premise held — the marker is absent from
  the flattened text because `AGENTS.md` writes `**already delegated**`, confirmed
  by running the function. Lane B's premise held — `disposition_gate_applies` is
  fail-closed on an unparseable `Created:`. The premise check also found the
  remedy already existed in the sibling `issue_critique_observer`, which changed
  the repair from "invent a matcher" to "restore parity", and produced the parity
  test that would otherwise not have been written.
- Files: `scripts/validate_critique_artifacts.py`,
  `skills/public/achieve/scripts/audit_disposition_corpus.py`,
  `skills/public/issue/scripts/issue_critique_observer.py` (comment only),
  `tests/test_critique_artifact_validation.py`,
  `tests/quality_gates/test_goal_disposition_gate.py`,
  `tests/quality_gates/test_critique_skill.py`, `docs/handoff.md`,
  `charness-artifacts/quality/dup-review.json`, and the generated
  `plugins/charness/` mirror of every exported source file.
- Alternatives rejected: (a) ship Lane A's one-line fix and see what breaks —
  rejected because a dormant gate waking across the corpus makes every author who
  trips it the discoverer of a decision nobody recorded; (b) widen
  `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES` once round 1 showed it under-fires —
  rejected as an arming decision on a corpus that cannot object, filed as #472;
  (c) repair #473's structural guard — rejected as a design change, annotated and
  filed instead.
- Targeted verification: `pytest` over the three touched test files (83 passed)
  with `ruff check` in the same breath; `validate_critique_artifacts.py --all`
  re-run with the gate LIVE (686 validated, exit 0); the audit re-run and its
  summary read field by field.
- Test duplication pressure: `check_dup_ratchet.py --summary` hard-blocked on 2
  new code families at the closeout aggregate. Both were classified `intentional`
  with recorded reasoning rather than deduplicated: `09af11c87038f373` is the
  deliberate cross-package restatement of the delegation contract (the parity
  round 1 asked me to pin), and `9f2acd76a3a85b84` is a two-line `is None` guard
  idiom with 30 untouched members. Lesson recorded: the plan said run this at the
  FIRST edit to a gated file, and running it at the aggregate is what made it a
  blocker instead of a note.
- Critique: two bounded rounds, fingerprinted, `verify --before` run the moment
  each reviewer returned and before any parent write — `clean` both times. Round 1
  (two reviewers, one per lane) produced the phrase-list finding, the OSError
  divergence, the test-that-pins-nothing, and Lane B's structural-zero blocker.
  Round 2 read only the repairs and found a BLOCKER neither round-1 reviewer could
  see, plus two overstated sentences of mine. Details in `## Plan Critique
  Findings`.
- Off-goal findings: #472 and #473, both filed, neither fixed.
- Lesson into the next slice: the round that reads the REPAIRS found the most
  serious defect in this run. It was not a re-check of round 1's list.

## Context Sources

Follow these in order; a fresh session can reconstruct the whole originating
context without this session's memory.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — read "The
   boundary (load-bearing)". Both lanes are proof surfaces, which the north star
   classifies as an irreversible boundary in its own right, and it explains why:
   a fail-open proof surface emits no failure, no log line, no ticket.
2. [issue #471](https://github.com/corca-ai/charness/issues/471) — Lane A's
   subject, with the premise-check order written into its body.
3. [The 2026-08-02 goal](./2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md)
   and its
   [closeout-claims review](../critique/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary-closeout-claims-review.md)
   — where both defects were found, and what its own claims got wrong.
4. [The #469/#470 resolution critique](../critique/2026-08-02-issues-469-470-resolution-critique.md)
   — F0 and F3. F3 IS Lane B's subject. F0 is the worked example of a residual
   nearly filed against the wrong decision record.
5. [D40](../../docs/deferred-decisions.md) — now carries #469's residual. Read it
   before touching the changed-line lane; do not arm it.
6. [That run's retro](../retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md)
   — the waste analysis whose three lessons are this plan's Low-Cost Checks.
## Interview Decisions

Shaped from the previous run's findings rather than a fresh interview, so the
decisions below record the design space a fresh session should see.

1. **Which of the surfaced-but-unfixed items to take?** Family considered: {the
   dormant guard (#471); the corpus report; the `*_RULE_DATE` floor sweep; D40's
   toll}. **Chosen: the first two.** They are the same defect at two scales — a
   surface that reports something it never established — and both were found by a
   reviewer rather than a gate, which is the signature the north star says to
   treat as an irreversible-boundary problem. Rejected: the floor sweep, because
   it is unbounded and was already recorded as a non-claim; rejected: D40,
   because arming it is an operator toll, not an agent's call.
   Anti-anchoring: `axis: repair register` — Lane A could be framed as "fix a
   typo" and is not; the one-line fix is the trivial part and the measurement is
   the deliverable.
2. **Repair first and measure after, or measure first?** Family considered:
   {ship the one-line fix and see what breaks; measure then ship; measure, ship,
   and grandfather}. **Chosen: measure first, with the disposition explicit.**
   Rejected: ship-then-see, because a dormant gate waking across 400+ artifacts
   makes every author who trips it the discoverer of a decision nobody recorded —
   and because the repo has twice armed teeth on a population that could not
   object. Anti-anchoring: `single-point: this repo's corpus` — the refusal may
   be entirely right; that is a property of these artifacts, not of the rule.
## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Reviewer provenance: three bounded read-only `bounded-reviewer` spawns — round 1
Lane A, round 1 Lane B, round 2 over the repairs of both. Unnamed one-shot spawns
per the repo's spawn-shape rule; all three returned findings inline.

Round 1, folded: the `OSError` divergence from the sibling reader; a Lane A test
that passed identically before and after the repair; Lane B's `in_scope_population`
omitting the `Status: complete` filter and 20 silently-dropped non-goal files;
`disposition_rule_date` rendering `[]` on an empty corpus with a str-vs-list type;
a majority threshold that tolerated 56 undatable goals; a tautological assertion.

Round 1, raised and NOT folded: widening `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES`
(filed #472 — an arming decision needing its own measured disposition) and
repairing the structurally-unfireable `--fail-on-pre-rule-refusal` (filed #473 —
a design change; annotated only).

Round 1, judged over-worry: that flattening `` ` * _ `` could widen the population
so a non-adopting repo reads as adopted. Flattening removes characters without
inserting spaces, so it can destroy a match across a word gap but never fabricate
one, and `all()` still requires a 62-character verbatim sentence. Not folded as a
guard; folded as a near-miss test instead.

Round 2, folded — the round that read only the REPAIRS: a BLOCKER neither round-1
reviewer could see, that `summarize` filtered `status == "complete"`
case-sensitively and so dropped
[2026-06-08-preflight-gate-phase-coverage.md](./2026-06-08-preflight-gate-phase-coverage.md)
(`Status: COMPLETE (2026-06-07)`) out of EVERY reported bucket — a completed,
in-scope goal the audit never examined, and a population statement hiding part of
its own intake, which is precisely this slice's thesis failing on the slice.
Also folded: two sentences of MINE that asserted more than was established (an
"and no other shape" closure claim about what the guard would catch, and a 0
described as "confirms the control flow" when it is merely unable to be
non-zero); the `main()` restructure shipping with no test over `main()`; R8's
motivating empty-corpus branch left untested while its apparent pin became a
tautology; a `--completed-only` help string contradicting the code; and a
near-miss test whose comment claimed to witness flattening that a negative
assertion cannot witness.

Round 2, judged correct as shipped: the strict-zero undatable pin (checked against
`parse_created_date`'s real `None` paths), and the `main()` restructure's
behaviour-equivalence for every pre-existing summary key.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- [#472](https://github.com/corca-ai/charness/issues/472) — `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES`
  under-fires. The 0-of-686 measurement is arithmetically right but reports how
  narrowly the list is spelled, not corpus health: 2 checked-in artifacts name a
  delegation policy as the canonical blocker in a real `Fresh-Eye Satisfaction`
  value and pass (`active delegation policy`). A third artifact cited alongside
  them is a separate defect — `2026-05-16-mutation-validity-fix.md:5` writes
  `Fresh-eye status:`, a field-name variant the reader never reaches, so widening
  the phrase list would not catch it; the issue now says so. NOT fixed here —
  widening refuses checked-in artifacts, which is an arming decision on a corpus
  that cannot object and needs its own measured disposition (the Non-Goals fence).
- [#473](https://github.com/corca-ai/charness/issues/473) — `audit_disposition_corpus.py`'s
  `--fail-on-pre-rule-refusal` is 0 by construction and cannot fire, because
  `apply_disposition_rungs` returns at `if not in_scope` before any
  `disposition_blank` is set. The same defect class as #471, found inside the very
  surface Lane B was repairing. Annotated so the number states what produced it;
  NOT repaired, because making the audit able to detect a real grandfather leak is
  a design change, not a labelling fix.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md
Host log probe: skipped: host-log-not-exposed: this Claude Code session exposes no per-turn token, wall-clock, or tool-call log to this agent, so any efficiency figure here would be fabricated rather than measured; the goal window is recorded only as the commit range in `## Auto-Retro`.
Disposition review: charness-artifacts/critique/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator-closeout-claims-review.md

Every figure, with its source:

- **0 refused, at three separate points** — before the repair, after it, and at
  closeout — by iterating `candidate_paths(root, [], all_artifacts=True)` and
  testing each artifact's `fresh_eye_satisfaction_status` value against
  `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES`; corroborated on a different channel by
  `python3 scripts/validate_critique_artifacts.py --repo-root . --all` exiting 0
  with the guard live.
- **Denominator, as-of pre-repair and post-repair: 686 = 986 − 300.** **As-of
  closeout: 687 = 987 − 300**, because this run's own resolution critique landed
  in the measured corpus. `charness-artifacts/critique/*.md` total minus the
  `charness.critique_prepare_packet` documents `candidate_paths` excludes by
  content kind. What this denominator selects: every artifact the `--all` run
  actually judges, which is the population the check can reach. It will move
  again as artifacts are added — the stable claim is the 0, not the 687.
- **587 of 686 (pre-repair) / 588 of 687 (closeout) carry a `Fresh-eye
  satisfaction` value** — the sub-population the check can even read, since it
  inspects only that value. The remaining ~99 are vacuously unrefusable by it.
- **Round-1 reviewer's independent corroboration, as-of that round** — a
  case-insensitive grep for all six phrases across ALL 986 files, including the
  300 excluded ones, returned no matches, so the 0 did not depend on the
  denominator being right. **Superseded at closeout:** the claims reviewer found
  one prose occurrence in this run's own resolution critique, which quotes a
  forbidden phrase while discussing it. The conclusion survives on the stronger
  ground — the phrase is not in any artifact's `Fresh-eye satisfaction` VALUE,
  which is the only text the check reads — but the "no matches anywhere"
  formulation is false for the shipped tree and is corrected here rather than
  carried.
- **audited_files 149 = rows_without_status 20 + rows_with_other_status 7 +
  completed_goals 122, as measured BEFORE this goal's own flip to `complete`** —
  `python3 skills/public/achieve/scripts/audit_disposition_corpus.py --repo-root .`.
  The flip moves this goal from `active` to `complete`, so the same command run
  after it reports 149 = 20 + 6 + 123. The TEST pins the identity, not the
  values (`test_live_corpus_summary_states_the_dated_denominator`), which is why
  the flip does not break it.
- **in_scope 115 = in_scope_dated 115 + in_scope_undatable 0, same as-of** —
  `python3 skills/public/achieve/scripts/audit_disposition_corpus.py --repo-root .`;
  116 after this goal's flip to `complete`, for the same reason.
  What this denominator selects: goals whose NORMALIZED status is `complete`,
  then fail-closed by `Created` against the 2026-05-30 rule date. It is not "all
  goals" and not "all completed files".
- **completed_goals moved 121 → 122** — caused by this run's status
  normalization, not by corpus growth; the recovered goal is
  `2026-06-08-preflight-gate-phase-coverage.md` (`Status: COMPLETE (2026-06-07)`),
  identified by listing every non-canonical first status token in the corpus.
- **83 tests passing** across `tests/test_critique_artifact_validation.py`,
  `tests/quality_gates/test_goal_disposition_gate.py`, and
  `tests/quality_gates/test_critique_skill.py` — targeted `pytest` run.
- **2 new duplicate families, both classified `intentional`** —
  `check_dup_ratchet.py --detail`, then `--summary` returning `ok: true,
  status: clean, new_code_family_count: 0`.
- **2 near-miss artifacts for #472, not 3** — the round-1 reviewer cited three;
  the closeout-claims reviewer split them.
  `2026-05-21-copy-heavy-release-only-critique.md:7` and
  `2026-05-21-usage-episodes-disabled-handoff-critique.md:7` are genuine
  phrase-spelling misses (`active delegation policy` in a real
  `Fresh-Eye Satisfaction` value). `2026-05-16-mutation-validity-fix.md:5` writes
  `Fresh-eye status:`, a FIELD-NAME variant `fresh_eye_satisfaction_status` never
  reads — so widening the phrase list would not catch it. It is a different
  defect wearing the same evidence, now stated as such in #472. Unbacked:
  whether 2 is the complete set of spelling misses. It is a floor from
  inspection, not a swept count.
- **Broad pytest: 6612 passed in 31.32s** — `python3 scripts/run_standing_pytest.py
  --repo-root . --mode read-only`, exit 0, run over the final bundled state. A
  `completed` closeout gate is NOT this evidence; this is the explicit run the
  Slice Plan's row C required, and its absence from an earlier draft of this
  section was the closeout-claims review's first blocker.
- **83 tests across the three touched test files** — `python3 -m pytest
  tests/test_critique_artifact_validation.py tests/quality_gates/test_goal_disposition_gate.py
  tests/quality_gates/test_critique_skill.py -q`.
- **Push and remote CI: confirmed, P4-style** — the push's own exit code is NOT
  the evidence. Server-side ref read back with `git ls-remote origin main`
  (a different observer than the local client), and the run it triggered —
  `gh run view 30730812074` — reports `completed / success` for `Quality Core` on
  `main`. The pre-push local suite (`82 passed, 0 failed`) is a third, separate
  channel and is not what this line claims.
- **#471 closed by the carrier, verified remotely** — `gh issue view 471` reports
  `CLOSED`; #472, #473 and #474 report `OPEN`, which is the intended end state.
  The close was carried by this commit's `Resolves #471` ledger, rehearsed before
  the commit with `issue_tool.py validate-closeout-draft` (`draft_verified`), and
  the delegated resolution critique ran BEFORE the close call.
- **Slice closeout gate: `completed`** — `python3 scripts/run_slice_closeout.py
  --repo-root . --skip-broad-pytest --ack-cautilus-skill-review`, after the two
  duplicate families were classified. Recorded as a gate result, not as broad
  proof.

## User Verification Instructions

1. **The guard is live and refuses nothing.**
   `python3 -c "import sys; sys.path.insert(0,'scripts'); from pathlib import Path; import validate_critique_artifacts as v; print(v.has_repo_delegation_contract(Path('.')))"`
   prints `True`, and
   `python3 scripts/validate_critique_artifacts.py --repo-root . --all` exits 0.
2. **The pin is against the real file, not a fixture.**
   `python3 -m pytest tests/test_critique_artifact_validation.py -q` — the test
   named `..._against_this_repos_real_agents_md` reads the checked-in `AGENTS.md`.
   To see it bite, bold the marker differently in `AGENTS.md` and re-run.
3. **The audit states its denominator.**
   `python3 skills/public/achieve/scripts/audit_disposition_corpus.py --repo-root . | head -30`
   — check that `audited_files` equals the sum of the three buckets and that
   `in_scope_population` names the status filter.
4. **The strict pin bites.** Break a completed goal's `Created:` line (or add a
   stray ` ``` `) and run
   `python3 -m pytest tests/quality_gates/test_goal_disposition_gate.py -q`; the
   dated-denominator test fails and names the offending file. Revert after.
5. **What was NOT done:** #472 and #473 are open by design. `gh issue view 472`
   and `gh issue view 473` carry the reasoning and the suggested approach.

## Auto-Retro

Goal window: `698a5d8f` (the shaping commit this goal was activated from) through
the single commit that follows it — `git log 698a5d8f..HEAD` resolves it, and no
SHA is transcribed here on purpose: the commit that CONTAINS this line cannot
name its own hash, and an earlier draft did, went stale on the next amend, and
had to be corrected. Both lanes, both reviews' folded repairs,
and the closeout landed together because the first commit attempt was refused by
the handoff-artifact gate, and the right response was rewriting the handoff for
the next session rather than patching it — by which point the closeout was ready.
No
provider-safe metrics block is rendered: the host exposes no per-turn token/time
log to this agent, per the `Host log probe:` skip.

Verification lock: the mutation set was locked after the closeout-claims review's
findings were folded; broad proof over that locked state is **6612 passed in
31.32s** (`run_standing_pytest.py --mode read-only`, exit 0), with the slice
closeout gate reporting `completed` separately. The gate result is not the broad
proof; both are recorded in `## Final Verification` with their commands.

Retro dispositions: issue #474 (recurs: the length-headroom advisory already exists for the sibling trap, and this run hit the dup ratchet at the closeout aggregate despite its own plan naming the first-edit rule — prose-resident checklists fire when nobody reads them) — surface duplicate-ratchet pressure at the first edit to a gated file; applied: `tests/test_critique_artifact_validation.py::test_delegation_contract_is_live_against_this_repos_real_agents_md` — pin a contract that gates behaviour against the REAL checked-in file, never only a synthetic fixture, because a fixture spells the marker the way the code does and cannot fail this class; applied: `tests/test_critique_artifact_validation.py::test_both_readers_of_the_delegation_contract_agree_on_this_repo` — when one contract is deliberately restated across a portability boundary, pin the parity rather than trusting a comment, since the comment asserting the divergence was itself stale; applied: `skills/public/achieve/scripts/audit_disposition_corpus.py` `pre_rule_refusal_detectability` + `in_scope_population` — a reported count states the population it selects and, when it is structurally fixed, says so; applied: `skills/public/achieve/scripts/audit_disposition_corpus.py:8-17` module docstring + `pre_rule_refusal_detectability` string — the retro improvement "treat `explain why this number is 0` as a claim needing the same premise check" lands HERE, and it was not theoretical: round 2 found that this run's first attempt at explaining the structural zero contained a false closure clause ("and no other shape") and an overstatement ("confirms the control flow" for a count that merely cannot be non-zero), both of which were corrected in the shipped text; accepted-risk: preserving key order when editing a checked-in JSON policy file is not guarded — the `sort_keys` reformat was caught by reading the diff's line count against the expected insert size, and a guard for a once-per-several-runs authoring slip would cost more than it saves; none — filing an issue before writing its number into prose, and running `validate_handoff_artifact.py` before composing a commit message, are single-step ordering habits with no structural destination that would not be more ceremony than the slip they prevent (both are recorded in the retro's waste analysis for the next session to inherit)
Structural follow-up: issue #474 (recurs: same advisory-shaped gap the length-headroom signal already closed for the sibling trap) — the retro's `## Sibling Search` names the transferable pattern as *a count whose value is determined by structure rather than by the thing it purports to measure*, with three instances this run (#471's guard, #473's flag, Lane B's unstated `in_scope`); its generalized trigger is carried by issue #473, and the workflow-affordance half is carried by #474.

# Achieve Goal: Close the guard that never fires, and the measurement that never states its denominator

Status: draft
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md` after confirming the draft is
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
| A | Measure what wakes up when `has_repo_delegation_contract` starts returning `True`, then repair it with that number in hand | A guard that has never fired is a proof surface failing open — silent by construction, shipped to every consuming repo, and every session since has trusted it. The repair is one line; the measurement is the work, and doing it in the other order is how D49 happened | The refused-artifact count with its denominator, stated BEFORE the repair lands; a test pinning the contract live against the REAL `AGENTS.md`; an explicit disposition if the count is non-zero; two bounded rounds | pending |
| B | Make `audit_disposition_corpus.py` state its dated denominator beside `in_scope` | It is the one corpus-measurement surface the `achieve` skill ships, and it reports a fail-closed population that silently includes every undatable artifact — the exact defect #470's follow-up (a) named, which that issue closed as not-built | The summary carrying the dated count; a test over the real corpus that fails if the dated count collapses; the numbers stated with what population they select | pending |
| C | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run (a `completed` gate is NOT broad proof); `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | pending |
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

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  boundary, and record the route it returns. At completion, recorded
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

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision that must be
resolved before `/goal`.

- Discuss before activation: THREE items, none blocking local progress. (1) IRREVERSIBLE SIDE EFFECTS — `git push` to `main` plus the CI each push triggers, and closing #471 if Lane A resolves it. Both need explicit operator approval at activation; the 2026-08-02 approval was scoped to that goal and does NOT carry forward. (2) A DECISION LANE A MAY HAND BACK — if the woken guard would refuse honest checked-in artifacts, the disposition (grandfather / narrow the rule / accept the churn) is an operator toll, not an implementation detail, and the goal will stop and ask rather than pick one. This is the one item most likely to end the run early, and that is the intended behaviour. (3) PROOF-SURFACE AUTHORING — both lanes change surfaces that render verdicts about other artifacts, which the north star classifies as an irreversible boundary in its own right; resolved by requiring TWO bounded rounds on Lane A and by fencing arming decisions out of acceptance.
## Slice Log

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

## Off-Goal Findings

Issues or deferred findings discovered during the run.

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

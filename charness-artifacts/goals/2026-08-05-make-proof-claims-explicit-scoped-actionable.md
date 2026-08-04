# Achieve Goal: Make proof claims explicit, scoped, and actionable

Status: active
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: active local-first planning/evidence-coordination goal;
  the five selected issues remain independent tracks with separate proof and
  closure boundaries.
- Current slice: C — re-verify and disposition the existing #496 semantic
  repair.
- Current slice intent: independently prove the policy-aware intent-loss
  behavior and carry an honest issue disposition without reopening the settled
  generic-empty predicate.
- Next action: read the current #496 carrier and implementation, run its
  focused positive/negative controls and source/plugin parity checks, then
  prepare its independent closeout or durable blocker.
- Slice B acceptance envelope: one semantic owner; quality maps
  `pass`/`fail`/`unestablished`, closeout preserves
  `completed`/`failed`/`blocked`/`planned`/`noop`; each adverse subject carries
  its own recovery disposition; `effective_exit_code` is the real entrypoint
  result; a closeout block has a recorded cause even with zero failed commands;
  structured output is explicit opt-in and per-run only; human renderers stay
  thin and keep one terminal compatibility assertion each.
- Verification cadence: cheap contract and artifact checks at commit
  boundaries; focused behavior and bounded fresh-eye review at each proof
  surface slice; broad proof at the final local bundle and live proof at each
  track's own publication boundary.
- Gate cadence: pre-lock slices use
  `run_slice_closeout.py --skip-broad-pytest`; final proof records the locked
  diff and uses `--verification-lock`.
- Slice review packet: name the claim, measured scope, evidence identity,
  owner, reader-facing next action, tests, non-claims, and all source/derived
  surfaces. A verdict-rendering change owes a second bounded review round after
  repairs, capped at two rounds.
- History boundary: Slices A and B are recorded and the goal is active. No push,
  release, or remote issue close is implied by the local matrix or by saving
  this artifact. Slice B's implementation and repaired-surface review are
  recorded locally; broad/final proof and each external track remain separately
  gated.

## Goal

Turn the recurring proof-boundary failures behind #491, #496, #502, #504, and
#506 into one bounded maintenance outcome: the Charness maintainer can inspect
each selected evidence surface and tell what it claims, which scope or identity
it binds, who owns the meaning, and what action follows. The surfaces do not
share one runtime protocol or first reader. Each track gets only the dimensions
that its own reader and producer need, retains domain-specific vocabulary, and
is proved independently. The goal is complete only when a fresh observer can
distinguish what each track established, what it did not establish, and what the
operator should do next.

Capability failure: a human or agent currently has to infer meaning from prose,
shape, stale paths, or a remembered relationship between producer and consumer.
That makes a technical truth look operationally useful when it is not, lets a
reference contradict the behavior it describes, and makes a valid local proof
look like a final claim without a bound identity or distinct observer.

Current workaround: hand-edit consumers, rely on bounded reviewers to discover
semantic drift after implementation, rerun broad gates, and manually decide
which artifact or snapshot belongs to which goal or review window. The cost is
rework and delayed discovery, not only line count.

## Non-Goals

- Do not create one universal status enum, output schema, or renderer for every
  Charness surface. Shared facts may be normalized, while quality, closeout,
  documentation, and reviewer tools retain domain-owned adapters.
- Do not include #503 or #505 in this goal. Their primary problem is recurring
  verification cost and proof-preserving runtime choice, not semantic claim
  ownership. Their existing evidence remains a separate cost track.
- Do not include #480, #482, #483, or #484. Those form a coherent but separate
  reference reachability, packaging, and corpus-denominator family. This goal
  may record their relationship but will not repair their path/export rules.
- Do not absorb #468's deferred-remedy premise verification. It is a related
  durable-record discipline and remains a follow-up unless Slice A proves a
  small shared seam with a named consumer.
- Do not add a new blocking gate merely because a semantic concern was found.
  Prefer an existing owner, a structured receipt, a source/consumer inventory,
  or an explicit reviewer question; add a floor only with a recorded recurrence
  and a separate false-fire decision.
- Do not perform live production/provider proof, release publication, tag or
  version mutation, or remote issue closure per slice. Remote state is a final
  boundary and is not implied by local green.

## Boundaries

- Review matrix only: record `semantic_claim`, `measured_scope`,
  `evidence_identity`, `owner`, `next_action`, and `non_claims` for comparison;
  do not require every surface to implement every field. The matrix is a
  planning and closeout aid, not a universal runtime protocol.
- Domain boundary: `run-quality.sh` and slice-closeout keep producer-owned
  status mappings; #496 keeps policy-aware semantics; #491 keeps a reference
  claim inventory or reviewer-owned decision; #504 keeps session retros
  separate from goal-bound closeout retros; #506 keeps parent/reviewer drift
  attribution while making the snapshot window identity explicit. #496 and
  #504 enter as already-locally-repaired closeout tracks unless live evidence
  shows their behavior has regressed.
- Initial track scope map (review-only; Slice A may revise it):

  | Issue | First reader / consumer | Producer and owner | Observable / falsifier | Closure dependency |
  | --- | --- | --- | --- | --- |
  | #491 | Behavior-changing maintainer reading shipped references | Reference author plus reviewer-owned quality decision | Stale behavior claim or copy-paste command; alternatively an explicit intentional-non-coupling disposition | Independent |
  | #496 | Policy/config author reading intent-loss warning | `_mark_subkey_refills` and `describe_intent_loss` under quality policy | Inert default is handled without hiding an intent-bearing empty policy value | Independent |
  | #502 | Terminal operator or CI reader | Quality and slice-closeout receipt producers | Failed subject, measured scope, recovery available/unavailable, and blocked/no-command cause are actionable | Independent |
  | #504 | Goal operator reading closeout evidence | `retro_persistence_lib.py` and achieve closeout | Wrong `Goal:` identity refuses before writes; session mode remains distinct | Independent |
  | #506 | Review parent verifying a boundary window | Reviewer fingerprint helper and its invocation contract | Stale/different/default window refuses with the window identity and re-snapshot action | Independent |

  The matrix is not a runtime schema. Its `first reader`, `producer`, and
  `observable / falsifier` columns prevent a superficially complete owner list
  from hiding the different causal boundaries.

### Locked Slice A Matrix (2026-08-05)

This matrix is locked from the live issue reads and current-tree inventory. The
issue reads were performed through the selected `gh` adapter with
`comments_read: true`; all five issues were `OPEN`. Evidence identities below
bind the row to the reader-facing source and its current proof record, not only
to the issue number.

| Issue | Semantic claim | Measured scope | Evidence identity | Owner / first reader | Observable / falsifier | Next action | Non-claims | Closure dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #491 | A shipped reference must not describe behavior, status vocabulary, or a copy-paste command that the implementation no longer has. | Three concrete claim families from the issue: `lifecycle-before.md` readiness scope/refusal, `bootstrap-posture.md` status and `refilled_subkeys`, and `goal-artifact.md` `--fields-file` invocation; this is not a full reference corpus. | Live #491 read plus the three current source references at `HEAD` `abf6c508`; the current texts carry the repaired claims but no source-to-reference manifest. | Reference author owns the claim; bounded reviewer is the first independent reader of the semantic question. | Falsifier: shipped reference contradicts the behavior or gives a command that cannot preserve the stated contract. | Keep the existing reviewer-owned semantic question as the contract; do not add a manifest or literal-set gate without a new mapped recurrence. Carry an explicit claim disposition to independent #491 closeout. | No mechanical proof of all reference correctness, no full-corpus census, and no universal reference schema. | Independent carrier, delegated resolution critique, distinct claim-read behavior verdict, and adapter readback. |
| #496 | An intent-loss warning must distinguish inert omitted defaults from intent-bearing policy values and preserve configured siblings. | `mutation_testing.commands` inert-leaf allowlist, missing-real-command negative case, sibling preservation, `prompt_asset_policy.exemption_globs` axis control, and source/plugin payload parity. | Live #496 read plus `charness-artifacts/issue/2026-08-04-issue-496-local-closeout.md`, `scripts/quality_bootstrap_lib.py`, `scripts/quality_bootstrap_absence.py`, and their identical plugin mirrors. | Quality/bootstrap maintainer owns `_mark_subkey_refills` and `describe_intent_loss`; policy/config author is the first reader. | Falsifier: a hollow refill is reported as lost intent, a meaningful empty value is suppressed, or the warning recommends deleting a configured block. | Re-run the existing focused semantic controls and prepare an independent closeout disposition; do not reopen the settled generic-empty predicate. | No remote issue closure, provider/host proof, or future-consumer guarantee; no universal empty-value taxonomy. | Independent carrier, delegated resolution critique, distinct behavior verdict, and adapter readback or durable blocker. |
| #502 | A terminal proof receipt must state the outcome, adverse subject, recovery evidence, unproven scope when relevant, and actual process exit behavior. | `scripts/run-quality.sh` quality summary with 21 literal summary assertions across three test files, plus `scripts/slice_closeout_reporting.py` final verdict with one literal pin; quality and closeout keep domain-specific states. | Live #502 read plus `scripts/run-quality.sh`, `scripts/slice_closeout_reporting.py`, `tests/quality_gates/test_quality_runner.py`, `test_quality_runner_runtime_aggregate.py`, and `test_gate_summary_names_failures.py`. | Shared per-run receipt owner with producer-owned quality/closeout adapters; terminal operator or CI reader is first reader. | Falsifier: a failed subject has no trustworthy recovery disposition, `unproven` renders as pass, a closeout block with no failed command loses its cause, or the final line and subprocess exit disagree. | Slice B: implement the thinnest shared receipt/test seam, then migrate consumer assertions to semantic fields while retaining one renderer compatibility pin per surface. | No universal status schema, no rolling telemetry store, no remote CI or issue-close claim from local receipt proof. | Independent carrier, delegated resolution critique, distinct behavior verdict, and adapter readback. |
| #504 | Goal-bound retro evidence must bind to the owning goal before persistence writes; session retros remain goal-free. | Goal-aware `--goal-path` success, wrong/malformed/outside/missing identity no-write refusal, exact slug canonicalization, legacy session mode, and achieve/retro caller contract. | Live #504 read plus `charness-artifacts/issue/2026-08-04-issue-504-causal-review.md`, `2026-08-04-retro-persistence-goal-binding.md`, `scripts/retro_persistence_lib.py`, `skills/public/retro/scripts/persist_retro_artifact.py`, and `tests/quality_gates/test_retro_persistence.py`; source/plugin mirrors are identical. | Retro persistence helper and achieve closeout own the binding; goal operator is first reader. | Falsifier: a wrong-owner or malformed goal retro writes an artifact/summary/event, or legacy session mode is forced into goal scope. | Keep implementation closeout-only; re-run its local behavior proof and independently prepare the remote issue disposition. | No host invocation proof that every caller supplies `--goal-path`, no remote issue state, and no claim that session retros become goal-scoped. | Independent carrier, delegated resolution critique, distinct local behavior verdict, and adapter readback or durable blocker. |
| #506 | Reviewer-boundary verification must certify the requested review window and refuse stale/default snapshots that belong to another window. | Snapshot/verify window binding, explicit `--before` path, canonical default behavior, legacy snapshot compatibility, parent-attribution exit distinction, and no-write boundary semantics. | Live #506 read plus `skills/shared/scripts/reviewer_boundary_fingerprint.py`, `tests/quality_gates/test_reviewer_boundary_fingerprint.py`, and identical plugin mirror; current tests cover explicit `round-1`/`round-2` refusal. | Reviewer-boundary helper owns snapshot identity; review parent is first reader. | Falsifier: a snapshot from another window is accepted, the default silently selects stale evidence, or parent-attributed drift is rendered as an undeclared clean proof. | Keep this helper-owned and separate from #502; verify default invocation/readback behavior during its independent disposition. | No proof of host reviewer spawning, no universal receipt, and no replacement of the distinct-observer requirement with a same-agent reread. | Independent carrier, delegated resolution critique, distinct boundary behavior verdict, and adapter readback or durable blocker. |

**Slice A lock:** #502 is the only new implementation slice. #496 and #504
remain closeout-only unless fresh behavior proof contradicts their existing
local carriers. #491 remains a reviewer-owned claim decision, and #506 remains
helper-owned; neither is absorbed into the #502 receipt or a universal gate.
- Reader-position axis: a reference may be authored in the source tree and read
  in an exported consumer tree. The first slice must decide whether any claim
  is checked at the author, consumer, or evidence-reader position before a
  validator is proposed.
- Lifetime axis: #502's structured receipt is a per-run contract/test seam
  with explicit machine-readable opt-in, not a rolling telemetry store. A
  durable store requires a separate consumer, retention, run identity, and
  stale-state contract.
- Source/derived boundary: if a selected surface has a checked-in plugin mirror,
  mutate source, sync the mirror, then verify both before broad gates. The
  selected issue contract is read through the issue adapter at activation;
  local artifacts do not replace GitHub state.
- Irreversible boundary: any push, remote CI claim, release, or issue close is
  a separately verified boundary. A final bundle may group the local changes
  administratively, but it is not an all-or-nothing transaction: one track's
  incompleteness must not block another track's honest disposition. Each issue
  closure requires its own carrier floor, delegated resolution critique,
  distinct behavior verdict, and adapter readback.

## User Acceptance

- A user reading only a failed quality receipt can identify the adverse subject,
  the scope that was measured, whether its recovery evidence is available or
  unavailable, and the next action. The terminal line remains useful under log
  truncation, while detailed tests assert semantic fields rather than 17 prose
  copies.
- A user seeing a #496 warning can tell whether the report found real intent
  loss or only an inert default difference. The existing local repair remains
  intact; the goal re-verifies its semantic controls and closes or honestly
  dispositions the issue without reopening the settled predicate.
- A maintainer changing behavior can locate the reference claim that must be
  updated, or see an explicit reviewer-owned disposition when mechanical
  coupling is not justified. A shipped reference is not allowed to silently
  describe the old behavior as current.
- A goal closeout cannot bind a valid-looking session retro to the wrong goal,
  and a reviewer-boundary verify cannot silently compare against a stale default
  snapshot. The intended goal/window identity and the refusal or readback are
  visible; these are separate evidence-boundary checks, not one receipt schema.
- Each selected issue is independently carried to a verified closeout or an
  honest durable open disposition. A single broad green run is never presented
  as proof of all five behaviors.

## Agent Verification Plan

### Low-Cost Checks

- At activation, run the issue planner and adapter read for #491, #496, #502,
  #504, and #506; confirm current title/body/state and `comments_read: true`.
- Inventory each producer, consumer, evidence artifact, generated mirror, and
  current test assertion before choosing an implementation owner. For #502,
  classify every current summary consumer; for #491, enumerate the actual
  reference claims rather than assuming a manifest is the answer.
- Run artifact validators, `git diff --check`, source/plugin drift checks, and
  focused contract tests at each commit boundary. Use describe-first helpers
  before drafting goal or issue closeout evidence.
- For every proposed blocking floor, record the floor-addition restraint call:
  existing advisory/owner/consumer first, recurrence basis second.

### High-Confidence Checks

- Run a delegated decision pre-mortem with distinct framing, diagnostic,
  first-reader/operational, and counterweight lenses before activation or
  implementation lock. The completed pre-mortem already recommends separate
  tracks rather than one shared schema; the goal carries that correction.
- Slice A produces a per-issue claim/scope/identity/owner/action matrix and an
  inclusion decision. Every later slice cites the matrix rather than inventing
  a local interpretation; a row may be routed to closeout-only or follow-up.
- Focused proof covers #502 clean/failure/unproven, mixed recovery evidence,
  blocked/no-command closeout, and actual subprocess exit behavior; #496's
  existing positive/negative semantic controls; #491 stale-reference and
  intentional non-coupling cases; #504 wrong-goal and session-retro controls;
  and #506 canonical/stale/explicit-window snapshot controls. These are
  independent proofs with independent readers and owners.
- Any change to what a gate, validator, or evidence renderer decides receives a
  second bounded fresh-eye round reading the repaired surface. Run broad quality,
  changed-line mutation coverage, and plugin parity only after the final repair
  round and synchronization.

### External Or Live Proof

- Local tests and a green push do not establish remote CI. For each track that
  publishes, read back the exact pushed SHA and its checks through a different
  observer/channel before that track's issue close or release claim. Grouping
  several tracks in one push does not merge their behavior verdicts.
- For each issue close, validate that issue's carrier, run its delegated
  resolution critique before the close call, render its distinct behavior
  verdict, and verify its tracker state through the adapter. If one closeout
  floor cannot be met, leave only that issue open and record its blocker; do not
  claim the umbrella complete until every selected track is independently
  closed or dispositioned.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Reconcile the five live issues and lock the shared claim dimensions | The common pattern is plausible, but scope and reader position must be proven before five fixes become five new contracts | Live reads, producer/consumer/evidence map, issue inclusion matrix, owner decision, false-unification risks, bounded pre-mortem | completed |
| B | Implement the substantive terminal-receipt owner (#502) | This is the only selected track with a new shared implementation need: duplicated verdict prose and ambiguous recovery evidence | Per-run semantic receipt/producer adapters, focused last-line and subprocess exit tests, second repaired-surface review | completed |
| C | Re-verify and disposition the existing #496 semantic repair | The local behavior is already repaired; reopening its predicate would repeat settled work | Existing positive/negative controls, current source/plugin parity, distinct behavior evidence, issue carrier or durable blocker | in_progress |
| D | Resolve the independent claim/binding tracks (#491, #504, #506) | Reference claims, goal-bound retros, and reviewer snapshots have different readers and owners | #491 corpus/claim decision, #504 closeout proof, #506 explicit-window/default refusal proof; no universal schema | pending |
| E | Cross-track proof and independent issue disposition | Shared vocabulary is not shared behavior; each issue needs its own boundary evidence | Broad locked quality/mutation proof, per-issue behavior verdicts, delegated critiques, adapter readbacks or durable blockers | pending |

## Operator Decision Queue

- Decision: confirm the five-issue bundle (#491, #496, #502, #504, #506) as one
  goal, or reduce it before activation.
  Owner: user/operator.
  Why deferred: the bundle is coherent at the capability level but crosses
  quality, achieve, and reviewer tooling, so activation should not silently
  convert a recommendation into authorization.
  Resolution: CONFIRMED by the operator; retain the bundle as one
  planning/evidence-coordination goal with independent tracks, local-first
  execution, and separately verified external boundaries.
  Revisit trigger: only if Slice A finds that a selected issue has no honest
  capability relationship or its own owner cannot be identified.
- Decision: choose whether #491 receives a mechanical claim manifest, a narrow
  literal-set check, or an explicit reviewer-owned contract after Slice A reads
  the real corpus; do not let the matrix preselect a gate.
  Owner: agent, with operator review if the choice adds a blocking floor.
  Why deferred: the live issue lists all three directions and current evidence
  only proves that memory alone failed.
  Resolution: reviewer-owned semantic question. The live corpus has three
  concrete claim families but no stable source-to-reference mapping; a
  manifest or literal-set gate would either overreach or miss the actual
  behavior claim. The existing bounded reviewer packet already carries the
  invariant, owner, recorded instance, axis-varying counterexample, and
  reject/repair/defer comparison.
  Revisit trigger: a new recurrence with a mechanically observable mapping and
  a separately reviewed false-fire decision.
- Decision: treat push, remote CI, release, and issue-close actions as
  independently verified track boundaries, even when a final local bundle
  contains several tracks.
  Owner: user/operator under the repository's standing conditional approval.
  Why deferred: no remote mutation is needed to shape this draft, and grouping
  is an administrative convenience rather than a shared proof claim.
  Unblock action: each publishing track must pass its local gates and boundary
  critiques; read back its own SHA/checks before its issue close or release.
  Revisit trigger: each track's publication boundary.

## Coordination Cues

Routing: ideation — establish the shared concept and reject over-bundling before
activation.
Routing: achieve — operate one auditable multi-slice goal after confirmation.
Routing: critique — run the decision pre-mortem and repaired proof-surface
reviews.
Routing: quality — own validation cadence, proof-surface risk, and local/remote
proof separation.
Routing: impl — implement only the smallest owner/binding slice after the
contract matrix is locked.
Routing: issue — read and independently carry the selected issue closeouts.
Routing: retro — review waste and disposition any recurring pattern after the
goal.
Gather: n/a — issue identity is read through the repo's GitHub adapter and all
other context is repo-local.
Release: n/a — no release surface is intended during shaping.
Issue closeout: #491, #496, #502, #504, #506 — final carrier, delegated critique,
distinct behavior verdict, and adapter readback are pending activation and must
be completed independently per issue.

## Discuss Before Activation

Discuss before activation: CONFIRMED — the operator accepted the five-issue
bundle as one planning/evidence-coordination goal, explicitly not one shared
implementation or release/issue-close transaction; accepted the local-first
boundary; and accepted that #491's implementation shape remains a Slice A
decision rather than a preselected manifest or new gate.

## Slice Log

Slice A is complete; the following report is the execution archive. The active
frame above is the control panel for Slice B.

### Slice 1: Lock the five-track proof matrix

- Objective: Reconcile the five live issue records with the current producer, first-reader, evidence, and test surfaces, then lock the independent-track boundary before implementation.
- Why this approach: The user-confirmed umbrella is only honest if the shared capability does not erase different readers or owners. Live reads and source inventory were the cheapest way to test that premise before changing code.
- Commits: No implementation commit; the active goal artifact is the only changed surface in this slice.
- What changed: Updated the goal artifact with the locked Slice A matrix, evidence identities, the #491 reviewer-owned decision, and the #502-only implementation boundary.
- Alternatives rejected: Rejected a universal receipt/status schema, a reference-claim manifest, a generic empty-default predicate, and a shared closure transaction. Kept #496/#504 closeout-only and #491/#506 independent because their first readers and falsifiers differ.
- Targeted verification: Issue planners for #491/#496/#502/#504/#506 passed with the adapter selected as gh; all five adapter reads returned comments_read=true and state OPEN. Current-tree inventory found 21 literal Quality summary assertions across three test files and one Closeout verdict pin. Source/plugin cmp was identical for the #496, #504, #506, and referenced #491 surfaces. The existing #496 local carrier, #504 causal/local carrier, and #506 window tests were read as evidence; no remote close or implementation proof is claimed by this slice.
- Test duplication pressure: No tests added or expanded in Slice A; duplicate-pressure sample not applicable.
- Critique: The activated pre-mortem was already completed with four bounded fresh-eye lenses and a repaired-surface round. Its independent-track correction is carried into the locked matrix; no new proof-surface code was changed in Slice A.
- Off-goal findings: #491 mechanical coupling remains a reviewer-owned disposition unless a new mapped recurrence justifies a gate. #496/#504 local carriers and #506 helper proof remain independent closeout tracks; #503/#505 and packaging/reference families remain out of scope.
- Lessons carried forward: A durable issue body is a hypothesis until the current producer and first reader are read. Keep semantic facts, observed spelling, and external issue state separate; do not treat source/plugin parity or a local green as remote behavior proof.
- Metrics: Host token/time/tool metrics are not exposed in a goal-scoped session file; no such metrics are claimed. Five issue planner reads and five issue adapter reads were run in parallel; all were read-only.

### Slice 2: Implement and repair the shared terminal receipt owner

- Objective: Implement the smallest #502 semantic owner for quality and closeout, preserve their domain-specific statuses, and make terminal output carry actionable subjects, recovery evidence, causes, and the actual entrypoint exit code.
- Why this approach: The live issue's duplicated prose was a consumer-ownership problem, not a reason to unify unrelated verdict vocabularies. One shared model with producer-owned adapters keeps semantics centralized while leaving quality and closeout state decisions local.
- Commits: Pending Slice B closeout commit; source/plugin generated export is synchronized in the worktree.
- What changed: Added `scripts/proof_receipt.py` and its plugin export; routed `run-quality.sh` through the quality adapter with explicit `CHARNESS_QUALITY_RECEIPT_JSON` / `--receipt-json=PATH` opt-in; attached closeout receipts in `--json`; routed the closeout final line through the shared renderer; added semantic and subprocess-focused tests.
- Targeted verification: The exact focused command over `test_proof_receipt.py`, `test_quality_runner.py`, `test_quality_runner_runtime_aggregate.py`, `test_run_slice_closeout_surface_obligations.py`, and `test_slice_closeout_broad_gate.py` passed 92 tests after moving explicit-filter no-match detection after all queue declarations and counting only actual explicit selections, including forced-opt-in counterexamples. `bash -n`, `py_compile`, `git diff --check`, and source/plugin parity passed for the changed runtime files. The durable review record is `charness-artifacts/critique/2026-08-05-slice-b-proof-receipt.md`.
- Fresh-eye review: Round 1 used three unnamed Codex bounded reviewers with distinct semantic, shell/runtime, and closeout/export lenses; all boundary verifies were clean. Round 2 read the repaired surface with the same three lenses and found three real issues (closeout cause precedence visibility, blank error fallback, and an explicit filter that could pass with zero scope); all were repaired. A later claims review found the zero-match check was placed before later queue declarations; that placement repair is recorded as accepted-unreviewed under the two-round cap. The durable artifact records each reviewer identity and the clean boundary checks; it does not claim a third proof-surface round.
- Alternatives rejected: Rejected a universal status enum, durable telemetry store, swallowed JSON-write failure, and a zero-scope green for an explicit label filter. Kept optional receipt-write failure separate from the gate's actual exit code while reporting it before the terminal human line.
- Non-claims: No broad quality gate, changed-line mutation proof, remote CI, plugin installation readback, issue carrier validation, delegated issue-resolution critique, issue close, push, or release is claimed by this slice.
- Next step: run the pre-lock closeout, commit the local implementation, and continue with Slice C's independent #496 re-verification.

## Context Sources

Durable references this goal was shaped from, in the order a fresh session
should read them:

1. `docs/design-north-star.md` — explicit scope, different observer/channel,
   and no terminal green at proof/irreversible boundaries.
2. `docs/handoff.md` — the previous narrower #502 draft and the already-noted
   relationship to #491, #496, and #504.
3. `charness-artifacts/retro/recent-lessons.md` — recurring wrong-boundary,
   semantic-review, and evidence-binding waste.
4. `docs/conventions/implementation-discipline.md` — premise verification,
   sync-before-verify, proof-surface review cadence, and floor restraint.
5. Live issue reads through `skills/public/issue/scripts/issue_tool.py` for
   #491, #496, #502, #503, #504, #505, #506, #468, and #480–#484 — the
   inclusion/exclusion evidence; GitHub remains the issue source of truth.
6. `charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md`
   — the superseded #502-only draft; its receipt details remain candidate
   acceptance for Slice B, not a pre-accepted whole-goal contract.
7. `charness-artifacts/issue/2026-08-04-issue-496-local-closeout.md` and
   `charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`
   — prior #496/#503 separation and the warning that a cost/report decision must
   not preselect a semantic predicate.

## Interview Decisions

1. Concept: chose “proof claims explicit, scoped, and actionable” as the single
   capability, not “one shared renderer.” Axis: semantic domain and reader
   position; different surfaces may need different adapters. Rejected the
   renderer-first framing because it would force unrelated status vocabularies
   together.
2. Bundle: included #491, #496, #502, #504, and #506. Axis: claim/evidence
   identity; each has a concrete recorded instance where shape or transport
   passed while meaning, scope, or binding failed. Rejected #503/#505 as cost
   tracks and #480/#482/#483/#484 as a packaging/reachability family.
3. Execution: chose local-first sequential slices with one shared matrix and
   independent issue proof. Axis: external boundary; push, remote CI, release,
   and issue close may occur after a final local bundle, but each remains a
   separately verified track boundary. Rejected parallel issue fixes because
   they would obscure which owner and evidence channel each repair proves.
4. Contract: chose normalized claim dimensions plus producer-owned adapters,
   not a universal protocol. Axis: surface lifetime and host/export boundary.
   Rejected a durable telemetry store and identical prose because neither is
   required to remove the observed failure.

## Plan Critique Findings

Delegated pre-mortem result: all four fresh-eye reviewers agreed that the five
issues do not share one first reader, implementation owner, or runtime receipt.
Act-before-ship findings were folded by changing the goal from a shared
capability contract to an umbrella maintenance outcome with independent tracks;
the review matrix is explicitly non-runtime, and #496/#504 are closeout-only
unless live evidence reopens implementation. Bundle-anyway: retain #502's two
terminal surfaces together and keep the matrix. Over-worry: universal schema,
universal reference manifest, and a new semantic meta-gate. Valid-but-defer:
#491 reviewer/literal-set decision, #504 remote closeout, and #506 helper
hardening remain independent tracks. Fresh-eye satisfaction is
`parent-delegated`; four unnamed one-shot reviewers returned findings. The
boundary verify was `verdict: parent-attributed` with no undeclared drift; the
only declared drift was the parent edit to this draft after the snapshot.

## Off-Goal Findings

- #503/#505: related trust/cost signals, but separate runtime and proof-cost
  decision surfaces; do not silently reopen them here.
- #480/#482/#483/#484: related reference integrity, but their decisive axis is
  package/export reader position and corpus coverage; retain as a separate
  follow-up family.
- #468: related durable assumption verification; retain as a follow-up unless a
  concrete shared consumer emerges during Slice A.
- #499 is closed and remains a precedent for wrong-boundary review, not active
  work.

## Final Verification

This draft has not run implementation or closeout proof. No push, release,
remote CI claim, issue close, or Cautilus evaluation is claimed. Activation and
execution remain the operator's explicit next decision.

## User Verification Instructions

Read the issue inclusion/exclusion table and `## Discuss Before Activation`.
Confirm the five-issue bundle, or name the issue(s) to remove, before running:

`/goal @charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md`

Nothing runs merely because this draft exists.

## Auto-Retro

No goal slices have run, so no waste or improvement disposition exists yet.
Any future retro must classify each improvement as applied, a tracked issue, or
an explicit no-improvement disposition.

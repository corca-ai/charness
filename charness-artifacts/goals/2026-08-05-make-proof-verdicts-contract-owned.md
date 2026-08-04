# Achieve Goal: Make proof verdicts contract-owned and actionable

Status: draft
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: substantial draft/backlog awaiting activation; the
  proposed next goal is #502, not the smaller #504 remote-only closeout.
- Current slice: A — fix the receipt contract and ownership decision before
  implementation begins.
- Current slice intent: make the terminal proof receipt self-sufficient and
  honest about outcome, actionable subjects, recovery evidence, and exit
  status, while preserving quality-only and closeout-only states.
- Next action: confirm the #502 scope and activate with `/goal @charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md`.
- Verification cadence: cheap contract checks at commit boundaries; focused
  behavior and fresh-eye review at slice boundaries; broad quality and issue
  closeout proof only at the bundle boundary.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final proof records the verification lock and uses `--verification-lock`.
- Slice review packet: include changed files and owning/generated surfaces,
  normalized receipt invariants, state matrix, tests/proof, non-claims, and
  reviewer questions. A proof-surface change owes a second bounded review round
  after repairs, capped at two rounds.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and
  `## Auto-Retro`.

## Goal

Resolve issue #502 by giving `run-quality.sh` and slice-closeout terminal
receipts a named structured semantic owner, producer-owned normalizers, thin
human renderers, and tests that assert semantic fields instead of scattering the
prose contract across 17 hand-written consumers. Preserve the operator-visible
last-line and process exit behavior, then close #502 only after implementation
proof, distinct behavior evidence, and the issue closeout floors pass.

## Non-Goals

- Do not reactivate the completed #504 implementation goal or perform its
  remote closeout here; #504 remains a separate issue-boundary task.
- Do not implement #491's reference-claim synchronization problem, #496's
  hollow-refill predicate choice, or unrelated open issues.
- Do not add a new blocking gate, repo-wide telemetry redesign, or universal
  verdict protocol for every runtime surface.
- Do not require byte-identical full output or one identical status vocabulary
  across quality and closeout. Their domain-specific statuses remain explicit.
- Do not make all human wording immutable. Keep one compatibility assertion per
  renderer and move the rest of the contract to structured fields.

## Boundaries

- Semantic owner: a small shared proof-receipt model/renderer is the leading
  implementation shape. Quality and closeout keep producer-owned adapters for
  their own status and evidence; no producer reconstructs the other's domain.
- Common receipt facts: terminal outcome, actionable adverse subjects,
  recovery evidence (`available` with a verified path, `unavailable`, or
  `not-applicable`), unproven subjects where applicable, and process exit
  status. The normalized contract must distinguish a real failure from an
  unestablished scope and distinguish a closeout block from a failed command.
- Quality mapping: `pass` means all selected scope was established with no
  failure; `fail` remains nonzero and carries failed labels plus verified or
  unavailable log receipt; `unproven` remains visibly non-pass even when the
  existing runner exit contract is zero.
- Closeout mapping: preserve its existing `completed`, `failed`, `blocked`,
  `planned`, and `noop` domain states. A `blocked` or non-command failure must
  carry its recorded cause; it must not be inferred from an empty failed-command
  list.
- Structured output boundary: the receipt is a per-run contract and test seam;
  any machine-readable opt-in must be explicit and must not create an
  unowned durable telemetry store. The default human output remains compatible
  except for the issue-approved actionable details.
- Source/export boundary: if a source surface or shared module is mirrored in
  `plugins/charness`, synchronize and verify the mirror before quality gates.
- Issue boundary: GitHub issue #502 is selected and re-read through the
  adapter at activation. Require `comments_read: true`; local artifacts are
  context, not remote state.
- External side-effect scope: any push, remote CI, or issue-close action is
  scoped to the final bundle that contains this goal's carrier and requires the
  existing repository gates. No per-slice remote publication is implied.
- Close boundary: do not close #502 until the carrier passes
  `validate-closeout-draft`, a delegated resolution critique is persisted, a
  distinct behavior verdict is recorded, and
  `verify-closeout --expect-state CLOSED` reads the state back.

## User Acceptance

- A user can read only the final line of a failed quality run and learn which
  check failed and whether its recovery log is trustworthy, without rerunning
  the full gate.
- A user can distinguish clean, failed, and unproven quality outcomes from the
  terminal receipt and process exit code; no unproven run is rendered as PASS.
- A user can see a closeout failure or block's recorded reason even when no
  command failed, and a stale/unavailable log path is never advertised as
  usable.
- The focused tests assert the structured receipt contract and only the small
  per-renderer last-line compatibility surface; the 17 prose consumers no
  longer independently define the format.
- Source and shipped plugin behavior are proven in parity when either surface
  is exported, broad quality proof passes, and #502 is either verified CLOSED
  under the issue floor or honestly remains open with a durable blocker.

## Agent Verification Plan

### Low-Cost Checks

- At activation, run the issue planner and live read for #502; confirm
  `comments_read: true`, current title/body, and open state.
- Recount and classify current summary consumers, inspect the actual producer
  and closeout paths, and write the state/exit/recovery matrix before code.
- Run `git diff --check`, source/plugin export-drift checks, focused contract
  tests, and the relevant artifact validators at each commit boundary.
- Use the existing quality and closeout packet/shape helpers; do not invent a
  parallel gate to judge semantic ownership.

### High-Confidence Checks

- First review round: a delegated fresh-eye critique reads the proposed owner,
  state mapping, and initial implementation packet.
- Focused proof covers clean, ordinary failure, unproven/partial, durable log
  available, log-copy unavailable, closeout blocked before commands, and
  non-command closeout failure. It checks final-line-only reads and preserves
  process exit status.
- If the changed surface renders a verdict, run the required second bounded
  review round after repairs; record accepted-unreviewed round-2 repairs under
  the repository cap rather than claiming a third review.
- Run the broad quality gate, changed-line mutation coverage, source/plugin
  parity proof, and final locked slice closeout. Interpret warnings as
  advisories and do not weaken a refusing gate.

### External Or Live Proof

- A push, remote CI run, and issue close are separate evidence channels. A
  green local gate does not establish remote CI, and a `CLOSED` readback does
  not establish behavior.
- Before any issue close, validate the carrier, run the delegated resolution
  critique, publish only within the approved final bundle, render the behavior
  verdict from the receipt behavior channel, and verify the issue through the
  adapter with `--expect-state CLOSED`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Reconcile #502, inspect all consumers, and lock the semantic receipt/mapping contract | The existing format has many consumers and two domain-specific verdict surfaces; implementation before ownership would repeat the issue | Live issue read, consumer inventory, producer/consumer brief, state/exit/recovery matrix, and resolved owner decision | pending |
| B | Implement the thinnest shared receipt owner and producer adapters | A single semantic owner removes hand-sanded prose while preserving quality/closeout-specific state | Shared model/renderer, quality and closeout adapters, source/plugin sync, focused unit/contract tests | pending |
| C | Migrate consumers and prove terminal behavior | The value is operational only if truncation, stale-log prevention, unproven scope, and blocked/no-command paths remain honest | Semantic-field tests, one black-box last-line test per renderer, real-shell exit tests, broad gate, mutation proof, second repaired-surface review | pending |
| D | Publish the final carrier and close or honestly disposition #502 | Issue state is an irreversible boundary and must not be inferred from local green | Validated carrier, delegated resolution critique, distinct behavior verdict, adapter readback, or durable blocker with issue open | pending |

## Operator Decision Queue

- Decision: confirm #502 as the next activated goal rather than #504 remote
  closeout, #496, or #491.
  Owner: user/operator.
  Why deferred: the user asked for a larger next goal and #502 is the strongest
  structural candidate, but goal activation is an explicit operator action.
  Unblock action: confirm the #502 focus or name a different larger objective.
  Revisit trigger: before `/goal` activation.
- Evidence check: choose the final publication carrier only after branch scope
  and generated/plugin surfaces are known.
  Owner: agent, with user input only if the scope is unsafe.
  Why deferred: publication can bundle unrelated history and cannot be decided
  honestly from the draft alone.
  Unblock action: inspect branch scope in Slice A; stop and ask only if no safe
  carrier exists.
  Revisit trigger: before any push or issue close.

## Coordination Cues

Routing: achieve — shape and operate one auditable multi-slice goal.
Routing: quality — own validation cadence, proof-surface risks, and local-vs-remote proof separation.
Routing: impl — implement the shared receipt owner and smallest meaningful slices.
Routing: critique — run pre-implementation and repaired-surface fresh-eye reviews.
Routing: issue — read, carry, and verify #502 through the adapter-selected backend.
Routing: retro — measure waste and turn repeatable improvements into applied changes or tracked issues.
Gather: n/a — GitHub issue identity is read through the selected issue adapter; no public-source gather is needed.
Release: n/a — no version or install-manifest change is intended.
Issue closeout: #502 — carrier and `validate-closeout-draft`/`verify-closeout` proof are pending Slice D.

## Discuss Before Activation

- Discuss before activation: unresolved — confirm #502 as the larger next goal.
  The default is selected from the live issue and handoff evidence; #504's
  remote-only closeout, #496's already-local implementation, and #491's
  documentation-sync problem remain separate. Also confirm that the goal may
  touch both terminal verdict surfaces because #502 explicitly names slice
  closeout as the scope question; do not activate until this scope is accepted.

## Slice Log

## Context Sources

1. `docs/design-north-star.md` — judgment on reversible contract design; a
   different observer and channel at remote issue-close and CI boundaries.
2. `docs/handoff.md` — current open issues and the reason #504 closeout is a
   smaller boundary than the next structural work.
3. `charness-artifacts/issue/2026-08-04-issue-496-local-closeout.md` — #496 is
   independently implemented/locally carried and should not be conflated with
   this goal.
4. Live GitHub issue #502, read with comments through
   `issue_tool.py read --repo corca-ai/charness --number 502` — 17 hand-written
   summary consumers, two candidate ownership shapes, and the closeout-scope
   question.
5. `charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md`
   — four-lens before-the-fact critique, semantic boundary brief, and
   counterweight disposition.
6. `charness-artifacts/retro/recent-lessons.md` — recurring wrong-boundary and
   verdict-surface lessons to carry into implementation.

## Interview Decisions

1. Next-goal family: chose a substantive implementation/proof goal centered on
   #502 rather than a remote-only #504 closeout; rejected reopening completed
   implementation goals because their local evidence is already complete.
   Axis: proof surface / issue boundary; both remain explicit rather than
   collapsing into one irreversible claim.
2. Scope: chose `run-quality.sh` plus slice-closeout because #502 itself names
   the closeout verdict as the adjacent scope question; rejected absorbing #491
   because reference synchronization has a different producer/consumer
   invariant. Axis: verdict surface; not a repo-wide runtime singleton.
3. Owner: chose a small shared structured receipt/renderer with producer-owned
   normalizers as the leading fixed shape; rejected a schema-only arrangement
   where two consumers reconstruct semantics independently. Axis: source vs
   derived surface; host-specific rendering remains adapter-owned.
4. Output: chose a per-run contract/test seam with explicit machine-readable
   opt-in if needed; rejected an unowned durable telemetry store. Axis: runtime
   output lifetime; no global persistence is implied.
5. Proof: chose semantic field tests plus one terminal black-box test per
   renderer and real-shell exit tests; rejected 17 prose pins as the contract.
   Axis: proof channel; remote issue state remains a separate channel.

## Plan Critique Findings

- Folded: “one owner” alone was too vague. The goal now names outcome,
  actionable subjects, recovery evidence, unproven subjects, exit status, and
  producer-owned status mapping before implementation.
- Folded: identical cross-surface status/prose would be a false proxy. Quality
  keeps `pass`/`fail`/`unproven`; closeout keeps `completed`/`failed`/`blocked`/
  `planned`/`noop`; parity is tested at normalized semantic facts.
- Folded: closeout can be blocked with zero failed commands and can fail after
  commands succeed; acceptance therefore requires a recorded cause, not just a
  failed-command list.
- Folded: failed-log copy availability is an axis. A failed copy must yield
  `unavailable`, never a stale path, and that distinction belongs in the
  receipt.
- Folded: plugin mirror synchronization is conditional but explicit whenever a
  shared/exported source changes.
- Rejected as over-worry: a universal verdict protocol, a new meta-gate, a
  telemetry redesign, and byte-identical output across different surfaces.
- Fresh-eye provenance: four unnamed, bounded Codex reviewers ran under the
  repo-delegated critique contract; findings were received in the parent and
  all four reviewer-boundary verifications returned `clean`. Durable record:
  `charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md`
  and its boundary receipt JSON.

## Off-Goal Findings

- #504 remote closeout remains a separate small issue-boundary goal; do not
  activate its draft merely because it appears first in the handoff.
- #496's local carrier says its predicate choice is independent; revisit only
  through its own goal.
- #491's reference-claim synchronization could become a later structural goal;
  it is not a cheap side effect of this contract change.

## Final Verification

This is an unactivated draft. No implementation, remote publication, issue
mutation, or completion claim has been made. At closeout, replace the following
with bound evidence or an explicit allowed non-claim:

Retro: pending — create a goal-bound retro after activation, or record the allowed opt-out if no meaningful work runs.
Host log probe: pending — record a goal-scoped host window if the activated run exposes one; otherwise state the host limitation.
Disposition review: pending — obtain the required resolution/claims review before any issue close or complete status.

## User Verification Instructions

Before activation, confirm the goal's #502 focus and two-surface scope. During
the run, inspect the state/exit/recovery matrix before implementation, the
semantic contract tests after implementation, and the final-line-only tests
for both renderers. At closeout, independently inspect the broad gate, plugin
parity, delegated resolution critique, distinct behavior verdict, and issue
adapter readback; any missing item means #502 remains open.

## Auto-Retro

Retro dispositions: pending — after activation, disposition every improvement as an applied change or tracked issue; no prose-only memory.
Structural follow-up: pending — after activation, classify transferable waste with the retro's sibling search and record its destination.

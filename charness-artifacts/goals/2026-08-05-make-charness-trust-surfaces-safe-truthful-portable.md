# Achieve Goal: Make Charness trust surfaces safe, truthful, and portable

Status: draft
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-make-charness-trust-surfaces-safe-truthful-portable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-05-make-charness-trust-surfaces-safe-truthful-portable.md`; begin with #507 after confirming the draft is still intended.
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

Make the next open trust-surface work converge as one auditable improvement program: preserve operator intent, keep acquisition and references truthful, make runtime ownership visible, and leave every selected backlog track fixed, explicitly deferred with evidence and owner, or blocked at a named boundary. Start with #507 quality-adapter preservation, then complete the remaining tracks without weakening proof floors or pretending local proof is remote proof.

## Non-Goals

- Do not invent a universal adapter schema or rewrite every consumer before the
  affected contract is proven.
- Do not weaken proof floors, replace distinct-observer review with a same-agent
  reread, or turn local checks into remote/live claims.
- Do not automatically close issues, push, publish a release, or run Cautilus;
  each external boundary stays per-track and separately authorized.
- Do not absorb unrelated backlog that is not listed in the selected tracks.

## Boundaries

- This is one umbrella goal with independent tracks. `#507` is the first
  implementation slice; later tracks may be fixed, explicitly deferred with an
  evidence/owner, or blocked at a named boundary without blocking unrelated
  tracks.
- Track A: `#507` quality-adapter bootstrap has three discriminating outcomes:
  matching normalized intent is a no-op with no advisory; a conflict preserves
  the existing value/comment and advises the exact surface, requested change,
  reason, and next action; explicit migration mode names every intended rewrite
  and retains comments. It must not add absent/disabled surfaces by default.
- Track B: `#508`, `#509`, `#510` make gather acquisition and classification
  truthful, including content-negotiated Markdown before login-wall fallback
  and safe URL slug derivation.
- Track C: `#480`, `#482`, `#483`, `#484`, `#491` make reference discovery,
  package/export surfaces, non-Markdown assets, and claim links portable.
- Track D: `#503`, `#505` make recurring closeout telemetry and mutation/quality
  runtime ownership actionable without weakening proof floors.
- Track E: independently disposition `#496`, `#502`, `#504`, `#506`; use `#468`
  as a cross-cutting premise-verification rule rather than a forced standalone
  implementation slice.
- Completion requires Track A/#507's user-visible preservation outcome to be
  delivered with behavior evidence. Every other selected issue must have a fix
  with evidence, an explicit deferral with owner/evidence, or a named blocker;
  the final report must label delivered versus unmet outcomes and does not
  require every issue to be remotely closed.

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- The #507 bootstrap path proves the matching-no-op, conflict-preserve/advisory,
  and explicit-migration outcomes against the observed consumer failure.
- Gather does not claim a login wall before trying the supported Markdown or
  content-negotiated acquisition path, and derived slugs/classifiers are safe.
- Reference/package tracks state which paths are actually shipped and portable.
- Runtime tracks expose an owner, useful signal, and proof-safe cost boundary.
- Every selected issue has a fix, evidence-backed deferral, or named blocker;
  the final report separates local proof from remote/live non-claims.

## Agent Verification Plan

### Low-Cost Checks

- Read each selected issue and owning source before shaping its slice; run the
  targeted tests, source/plugin mirror checks, and goal validation.
- Run focused quality/advisory inventories after each track and record their
  actual output in the slice log.

### High-Confidence Checks

- Run behavioral tests for #507, gather acquisition/classifier fixtures for B,
  and package/reference consumer checks for C.
- Use a distinct bounded fresh-eye reviewer for proof-surface changes; a
  verdict-logic repair owes a second review round over the repaired surface.
- Run the broad quality gate at the final bundle and bind the result to the
  final commit/packet identity.

### External Or Live Proof

- No external/live proof is planned by default. If a track needs remote CI,
  consumer checkout, issue closeout, push, or release proof, record the exact
  boundary and run its owning workflow before claiming it.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Startup contract check | New achieve binding plan must be inherited before activation | `--pursue-ready` report and resolved decision summary | prerequisite |
| 1 | Fix #507 quality-adapter preservation | It is the first concrete trust failure and defines preserve-vs-migrate semantics | focused bootstrap/advisory tests, readback, and fresh-eye review | planned |
| 2 | Fix #508/#509/#510 gather truthfulness | Acquisition and classification errors share a user-facing trust boundary | targeted gather tests and explicit acquisition/classifier evidence | planned |
| 3 | Fix #480/#482/#483/#484/#491 reference/package integrity | Shipped claims are only portable when their real consumer surfaces agree | reference inventory, package/export checks, and claim readback | planned |
| 4 | Fix #503/#505 runtime ownership and economics | Recurring proof/runtime signals must be actionable without floor erosion | telemetry/runtime evidence, owner/budget record, and quality proof | planned |
| 5 | Disposition #496/#502/#504/#506 and apply #468 | Keep local proof and remote issue state honest while clearing the remaining backlog | per-track fix/deferral/blocker carrier with evidence and owner | planned |
| 6 | Bundle proof and closeout | The umbrella claim needs one fixed target and independent review | final packet, fresh-eye, verification lock, retro, and disposition ledger | planned |

## Issue Disposition Ledger

Every selected issue gets its own terminal row; the track table is only the
execution summary. `planned` and `not yet delivered` are the honest draft
state, not completion claims.

| Issue | Track | Intended user outcome | State | Evidence/carrier | Owner | Delivered / unmet |
| --- | --- | --- | --- | --- | --- | --- |
| #507 | A | Preserve adapter intent/comments and explain migration | planned | issue #507 + consumer reproduction | next active session | unmet |
| #508 | B | Classifier does not misread ordinary prose as login wall | planned | issue #508 + targeted fixture | next active session | unmet |
| #509 | B | URL-derived slug is safe and stable | planned | issue #509 + targeted fixture | next active session | unmet |
| #510 | B | Try supported Markdown acquisition before fallback | planned | issue #510 + acquisition evidence | next active session | unmet |
| #480 | C | Script-only references are discovered when shipped | planned | issue #480 + inventory | next active session | unmet |
| #482 | C | Shipped command docs point at a real consumer path | planned | issue #482 + package check | next active session | unmet |
| #483 | C | Non-Markdown assets participate in reachability checks | planned | issue #483 + inventory | next active session | unmet |
| #484 | C | Shared docs behave as a portable package | planned | issue #484 + consumer readback | next active session | unmet |
| #491 | C | Reference claims stay aligned with source truth | planned | issue #491 + claim readback | next active session | unmet |
| #503 | D | Recurring closeout telemetry has an owner and signal | planned | issue #503 + runtime record | next active session | unmet |
| #505 | D | Runtime is actionable without weakening proof floors | planned | issue #505 + quality evidence | next active session | unmet |
| #496 | E | Hollow refill class has an explicit disposition | planned | issue #496 + sibling search | next active session | unmet |
| #502 | E | Quality summary has a clear consumer/owner | planned | issue #502 + consumer inventory | next active session | unmet |
| #504 | E | Retro persistence carries goal-bound evidence | planned | issue #504 + artifact proof | next active session | unmet |
| #506 | E | Reviewer boundary default window stays current | planned | issue #506 + boundary test | next active session | unmet |
| #468 | E/cross-cutting | Remedy premises are verified before shaping | planned | issue #468 + per-track records | next active session | unmet |

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

- `Routing: achieve — umbrella lifecycle and activation contract`
- `Gather: planned for Track B — external source acquisition routes through gather before decisions`
- `Release: n/a — no release surface is in scope unless a selected track proves it necessary`
- `Issue closeout: n/a — issues are context and work carriers; close only after each track meets its own floor`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: CONFIRMED — use the broad umbrella with #507 first; #507 must deliver the three preservation/migration outcomes, while every later issue gets its own fix, evidence-backed deferral, or named blocker row. Preserve #507's existing values and comments, and make each advisory state the exact requested change and reason. No external side effect or issue close is implied by activation.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `docs/design-north-star.md` — reversible work is judged by capability;
   issue close, release, external write, and deletion boundaries require a
   different observer and evidence channel.
2. `docs/handoff.md` — current pickup, open backlog, and the prior session's
   remaining work.
3. `charness-artifacts/retro/recent-lessons.md` — repeated closeout drift,
   premise verification, and waste lessons to carry into this goal.
4. GitHub issues `#507`, `#508`, `#509`, `#510`, `#480`, `#482`, `#483`, `#484`,
   `#491`, `#503`, `#505`, `#496`, `#502`, `#504`, `#506`, and `#468`, read on
   2026-08-05 as the selected work and disposition inventory.
   In particular, #507 reports a consumer-owned `.agents/quality-adapter.yaml`
   whose bootstrap returned `adapter_status: updated`, dropped 14 comments,
   added absent CI/lefthook/public-spec/runtime/current-pointer surfaces, and
   overwrote customized intent; it is the bounded first reproduction, not a
   claim about every consumer.
5. `docs/conventions/implementation-discipline.md` and
   `docs/conventions/operating-contract.md` — sync/verify/publish barriers,
   premise verification, fresh-eye review, and artifact/commit discipline.

## Interview Decisions

- Scope: narrow single-issue goal vs umbrella — chose umbrella because the
  trust failures are connected and the user explicitly asked for a larger goal;
  rejected narrow scope because it would preserve the same backlog fragmentation.
- Order: #507 first vs gather first — chose #507 because preservation semantics
  are the clearest immediate trust failure; rejected gather-first because it
  would postpone the agreed carrier.
- Completion: close every issue vs disposition every issue — chose per-issue
  disposition, with #507 required to deliver its user-visible outcome, so
  remote state is not mistaken for local completion; rejected an all-or-nothing
  close condition because independent later tracks can be evidenced separately.
- #507 behavior: preserve values/comments by default vs normalize-and-rewrite
  automatically — chose matching no-op, conflict preservation plus explanatory
  advisory, and explicit migration because operator intent is the existing
  value; rejected silent rewrite because it loses information and revives absent
  surfaces.

## Plan Critique Findings

 - The broad bundle is bounded by six tracks and an explicit per-track
   disposition, so it is not an all-or-nothing implementation transaction.
 - Before shaping #507's remedy, verify the bootstrap/advisory premise from the
   consumer evidence; the issue's suggested remedy is not proof by itself.
 - The achieve change adds minimum binding-field shape at activation, not a
   semantic packet validator or second closeout-time proof floor. This is the
   smallest structural repair for the repeated packet/status/lock drift; final
   values and lock evidence still belong to the existing closeout workflow.
 - Fresh-eye review is required for the final umbrella claim and twice for any
   verdict-logic repair; same-agent reread is not a substitute.
- Floor-addition restraint: keep the five-field shape because the same closeout
  drift recurred; do not add a full content classifier until actual misses prove
  this structural contract is insufficient.

## Closeout Binding Plan

This is the concrete closeout contract for this umbrella goal:

- Reviewed inputs: this goal's semantic sections, each selected issue carrier,
  and per-track quality/behavior records; retro, packet, reviewer, lock, and
  terminal status/evidence are derived terminal records, not semantic inputs.
- Frozen target: finish semantic inputs, commit the baseline, and generate the
  packet against that exact commit SHA; never bind final proof to moving `HEAD`.
- Fresh-eye: use a distinct bounded reviewer and a different evidence channel;
  any proof-surface verdict-logic repair gets a second round over the repair.
- Verification lock: run `python3 scripts/run_slice_closeout.py --repo-root . --base --verification-lock` only after the semantic baseline and packet are final; a later semantic-input edit requires rebinding.
- Complete flip: after #507 and every issue ledger row have their evidence or
  explicit unmet disposition, record packet/fresh-eye/lock evidence in the
  terminal closeout record and then write status/evidence bookkeeping outside
  the reviewed identity.

## Off-Goal Findings

- `#468` remains a cross-cutting premise-verification rule; it is applied while
  shaping each remedy, not silently lost as an unrelated note.
- If #496/#502/#504/#506 remain unchanged after their disposition pass, retain
  their explicit state and owner rather than manufacturing a fix.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: not applicable before activation — create the bound retro during final closeout
Host log probe: not planned before activation — record measured host evidence or an allowed skip at closeout
Disposition review: not applicable before activation — create the final independent disposition review at closeout

## User Verification Instructions

At the next session, run the activation line at the top of this file. Start by
reading `## Closeout Binding Plan`, then verify #507's current consumer evidence
before changing bootstrap behavior. Review each later track independently; do
not close an issue or claim remote proof merely because local tests pass.

## Auto-Retro

Retro dispositions: not applicable before activation — at closeout, disposition each surfaced improvement as applied or tracked issue.
Structural follow-up: not applicable before activation — at closeout, classify any transferable waste as an applied guard, tracked issue, repo-local guard, or explicit none.

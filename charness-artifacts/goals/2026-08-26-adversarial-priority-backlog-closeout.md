# Achieve Goal: Design and dogfood issue-native backlog closeout

Status: approved-frozen
Created: 2026-08-26
Intended activation after approval: `/goal #724`
Authorization state: approved for the exact #724 reconciliation and child
implementation described by the briefing; push, release, tag, remote CI,
installed-host mutation, and issue close remain unauthorized

This is the full local goal draft. It accumulates research and design until the
operator approves the final briefing. After approval it is retained as the
frozen planning snapshot; GitHub owns routine execution progress.

## Goal

Design an issue-native `achieve` lifecycle that researches the existing system,
builds and reviews a full local goal draft, explains the intended to-be system,
and waits for explicit approval before creating a GitHub parent/sub-issue graph
or implementing. Dogfood that lifecycle on the existing P0–P2 backlog, then—only
after approval—resolve the cohort with independently executable and verifiable
sub-issues while leaving the resulting domain model, architecture, design,
code, and `docs/` more coherent than the starting system.

## Why This Goal Exists

The original goal coordinated 26 P0–P2 issues, but the first issue-native
`achieve` attempt skipped the planning/implementation boundary: it replaced the
full draft with a receipt, created GitHub tracker state, and began local
implementation before an implementation briefing was approved. That premature
work is evidence for this design, not an approved implementation.

This dogfood run must prove that `achieve` can help a capable agent and operator
design the right system before optimizing execution tracking.

## Planning Contract

The detailed, operator-approved lifecycle is
[Phase 0 planning contract](../specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/planning-contract.md).
Its order is load-bearing:

1. research the existing system
2. accumulate the full local draft
3. run the bounded decision interview
4. run critique round 1
5. write to-be docs and executable sub-issue drafts
6. run critique/adversarial-verification round 2
7. perform the meticulous final alignment audit
8. brief the operator on purpose, target structure, execution, and proof
9. wait for explicit approval
10. only then freeze the draft, reconcile GitHub, and implement

## Current Planning State

- Current stage: 9 — operator approved the exact implementation briefing; this
  complete Goal Draft is now frozen planning evidence.
- Completed stage: 1 — researched the pre-prototype `achieve`/`issue` model from
  `HEAD`, current docs, adapters, tests, historical contracts, provider
  readback, and the unapproved prototype as a separate evidence set.
- Current action: begin only the approved #726 minimum-provider bootstrap slice,
  then reconcile #724 through the verified provider boundary.
- Prototype boundary: uncommitted issue-native code and its tests are proposal
  evidence only; they do not define the current system or an approved to-be.
- GitHub boundary: `corca-ai/charness#724` and #725–#727 already exist because
  of the premature attempt. They are provisional external facts and remain
  untouched until the final briefing is approved.
- Stop condition for planning: a reviewed full draft, conditional to-be docs,
  executable sub-issue drafts, two critique rounds, final alignment audit, and
  an operator-facing implementation briefing.

## Approval Record

- Decision: approved.
- Exact operator response: `승인`.
- Observed date: 2026-08-26 Asia/Seoul.
- Session identity: `01a03c37-b39b-7541-9dc2-95459b1d7479`.
- Approved briefing:
  [Implementation Briefing: Issue-Native Achieve And First Dogfood](../specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/implementation-briefing.md).
- Authorized boundary: freeze this full draft; reconcile #724/#725–#727;
  create the two missing system children; implement the minimum #726 bootstrap
  slice and then execute the approved child graph.
- Still unauthorized: push, release, tag, remote CI mutation, installed-host
  mutation, and issue closure.
- Freeze rule: after this approval record, this file's complete bytes are the
  planning snapshot and must not change. Execution observations and progress
  belong to separate Goal Run evidence and GitHub.

## Confirmed Decisions

- GitHub parent authority: after approval, one parent issue is the execution
  tracker; the full local goal remains the frozen planning source and is not
  replaced by a receipt.
- GitHub unavailable: default to a typed stop. A local provisional fallback is
  allowed only when an adapter explicitly opts in and must not claim GitHub
  authority.
- Provisional fallback scope: planning may proceed through the reviewed briefing,
  but `/goal` activation, implementation, child progress, and completion remain
  blocked until the GitHub parent/child graph is created and read back.
- Update model: assume one agent updates the parent. Routine progress is child
  state; parent-body updates are sparse and reserved for shared contract changes.
- Child creation: prepare every known independently closable child at graph
  creation; add later concrete discoveries lazily.
- Existing cohort: attach all 26 original P0–P2 issues, including already-closed
  #721, #694, and #628. A parent cannot close while a linked child remains open;
  a deferred child moves to a successor parent with a recorded reason.
- Provisional graph disposition: after briefing approval, reuse #724 as the
  authoritative parent, record the premature bootstrap and planning reset,
  reconcile its body and child specs to the approved contract, and verify the
  complete provider graph rather than creating a replacement parent.
- Local draft: grow a full draft through planning and preserve it after approval;
  do not use it as a routine progress mirror.
- Draft-to-run binding: use a checked-in structured sidecar. The frozen Markdown
  draft owns planning intent; the wholly immutable sidecar owns approval,
  draft hash, GitHub parent identity, and initial approved graph identity. It
  contains no establishment/terminal references or mutable provider state.
- Binding path: derive it deterministically beside the draft by replacing `.md`
  with `.binding.json`. For this goal the exact proposed path is
  `charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.binding.json`.
- Legacy goal scope: ignore every local goal artifact except this goal. Leave
  those files untouched, but do not migrate them, preserve their runtime path,
  or use them as compatibility/acceptance constraints for the target system.
- Child quality: every child must be immediately executable and verifiable by a
  fresh agent without rediscovering the design.
- Review: run two `critique`/adversarial-verification iterations. Apply obvious
  findings directly; ask the operator about consequential choices.
- Architecture criterion: success is not a small delta. The final domain model,
  architecture, design, and code must be more coherent and less makeshift.
- Documentation criterion: conditional to-be structure must be designed in
  `docs/` before implementation approval and reconciled to honest current-state
  documentation before goal completion.
- Approval boundary: after final alignment, brief “what purpose, what target
  structure, what execution and proof”; no implementation begins without an
  explicit yes to that briefing.

## Decision Interview Ledger

- Adapter default ceiling: 15 substantive operator questions; any positive
  integer override is valid.
- Interview status: initial interview complete.
- Questions asked and answered: 9.
- Remaining shared capacity for non-obvious critique decisions: 6.
- Operator-provided principles do not consume the count, but are recorded as
  decisions.
- Initial interview and both critique rounds share the same ceiling.
- Every question includes options, per-option tradeoffs, a recommendation, and
  the recommendation reason.
- Facts discoverable from code, docs, tracker, or durable history are researched
  rather than asked.
- If the ceiling is exhausted with consequential ambiguity remaining, planning
  stops without a briefing or parent finalization until the ceiling or scope is
  changed.

### Question 1 — Planning And Execution Authority (Answered: A)

After approval, which surface should own mutable goal execution while retaining
the planning record?

- **A. Frozen full Goal Draft plus authoritative GitHub parent — recommended.**
  Preserve the complete local draft as the approved design snapshot and use one
  parent/sub-issue graph for mutable execution. Tradeoff: requires an explicit
  integrity binding, but gives planning and execution one owner each.
- **B. Dual-write the full local goal and GitHub.** Keep both current throughout
  execution. Tradeoff: strongest offline readability, but every child close,
  deferral, and scope change creates reconciliation and stale-mirror risk.
- **C. Keep the local goal authoritative and use GitHub as a summary.** Tradeoff:
  smallest change to the current implementation, but collaborators and provider
  automation cannot trust the actual parent/sub-issue graph.

Recommendation reason: A preserves the rich design record without retaining two
mutable trackers.

Operator decision: A confirmed. The full Goal Draft is frozen after approval;
GitHub owns execution.

### Question 2 — GitHub Unavailable (Answered: A)

What should happen when the selected GitHub capability is unavailable?

- **A. Typed stop by default; adapter-explicit planning-only fallback —
  recommended.** Tradeoff: execution waits for GitHub, but no false authority or
  later state merge is created.
- **B. Automatically execute against local state and reconcile later.**
  Tradeoff: maximum availability, but recreates a second tracker and ambiguous
  conflict/partial-migration semantics.
- **C. Always stop all work, including planning.** Tradeoff: simplest authority
  rule, but wastes safe research, critique, docs, and briefing work.

Recommendation reason: A preserves useful planning while refusing to split
execution truth.

Operator decision: A confirmed. Default is a typed stop; only an explicit
adapter policy permits planning-only fallback.

### Question 3 — Parent Update Protocol (Answered: A)

How should routine progress update the parent?

- **A. One agent; child state is progress; sparse parent changes — recommended.**
  Parent updates are limited to shared intent, scope, policy, dependency, graph,
  or completion changes. Tradeoff: no activity diary in the parent, but the
  provider graph remains the direct progress view.
- **B. Add optimistic concurrency for agents and human editors.** Tradeoff:
  protects multi-writer edits, but adds conflict machinery for a scenario the
  operator says does not exist.
- **C. Append every child event to the parent.** Tradeoff: one chronological
  page, but duplicates provider state and makes routine closeout noisy.

Recommendation reason: A matches the single-agent operating assumption and
keeps the parent focused on durable shared contract changes.

Operator decision: A confirmed. Concurrent human editing is out of contract.

### Question 4 — Initial Child Creation (Answered: A)

When should known independently closable work become sub-issues?

- **A. Establish every known independent child initially — recommended.** Add
  genuinely new in-scope discoveries later. Tradeoff: a larger initial graph,
  but dependencies and completion are visible before implementation.
- **B. Create children only when selected.** Tradeoff: smaller graph at first,
  but hidden work and late dependency discovery weaken the briefing.
- **C. Keep one implementation child and split only if blocked.** Tradeoff:
  minimal issue count, but creates the catch-all unit the target architecture is
  intended to remove.

Recommendation reason: A makes the approved decomposition inspectable and lets
each child close independently.

Operator decision: A confirmed. Initial establishment includes all known work;
later concrete in-scope discoveries are added lazily to the Goal Run.

### Question 5 — Existing Cohort And Parent Completion (Answered: A)

How should the 26 existing P0–P2 issues participate in the Goal Run?

- **A. Link all 26, including already-closed issues — recommended.** Parent
  closure requires every linked child closed; a genuine deferral moves to a
  verified successor parent with reason. Tradeoff: the graph includes historical
  completions, but it exactly represents the approved cohort.
- **B. Link only currently open issues.** Tradeoff: a cleaner progress view, but
  loses the cohort's completed evidence and makes the initial baseline
  irreproducible.
- **C. Recreate all work as new managed child issues.** Tradeoff: uniform bodies,
  but duplicates identity/history and disconnects prior discussion and proof.

Recommendation reason: A preserves provider identity and makes parent completion
an exact graph property without duplicating work.

Operator decision: A confirmed. Closed #721, #694, and #628 remain linked;
deferral is a verified move, not a silent unlink.

### Question 6 — Durable Draft-To-Run Binding (Answered: A)

How should the frozen full draft bind to the authoritative GitHub run after
approval?

- **A. Checked-in structured sidecar binding — recommended.** Keep the Markdown
  draft body immutable after approval. A small repo-visible structured record
  owns draft identity/hash, parent `(repo, number, URL)`, approved child-manifest
  digest, and provider-observation references. Tradeoff: one additional artifact
  type, in exchange for explicit domain boundaries, portable recovery, and
  machine validation without parsing planning prose as runtime state.
- **B. Mutable metadata envelope in the full Markdown draft.** Freeze the body
  but continue changing a narrow header for parent identity and lifecycle
  status. Tradeoff: fewer files and easier compatibility with current
  `goal_path` consumers, but the planning snapshot still has two owners and
  local status can be mistaken for authoritative execution state.
- **C. Activate and recover directly from the GitHub parent.** Remove the local
  runtime binding and teach the host `/goal` boundary to accept a GitHub issue
  identity. Tradeoff: the cleanest single execution authority, but it requires a
  host-runtime contract change outside this repository and weakens clone-local
  portability/offline fallback.

Recommendation reason: A names the real cross-boundary relationship as its own
domain object. It preserves the operator's frozen full draft, leaves mutable
execution truth on GitHub, and retains a small portable integrity/recovery
record without rebuilding the old local progress tracker.

Operator decision: A confirmed. The target model therefore has four distinct
objects: frozen `Goal Draft`, structured `Goal Binding`, authoritative GitHub
`Goal Run`, and independently closable `Work Item`.

### Question 7 — Legacy Nonterminal Goal Migration (Answered: Ignore All)

How should the new lifecycle treat existing nonterminal full-artifact goals?
The current repository has 2 `active`, 1 `blocked`, and 12 `draft` legacy goal
artifacts; 163 completed artifacts remain historical evidence.

- **A. Bounded cutover by state — recommended.** Historical terminal artifacts
  remain read-only. Existing `active`/`blocked` runs may finish through the old
  contract, while existing `draft` artifacts must be reshaped into the new
  draft+binding+GitHub model before activation. No newly created goal may use
  the legacy runtime path, and compatibility code has an explicit removal
  trigger when the grandfathered active/blocked inventory reaches zero.
  Tradeoff: a temporary dual reader remains, but it is finite, measurable, and
  cannot create new legacy debt.
- **B. Migrate every nonterminal artifact before any further pursuit.** Convert
  all 15 active/blocked/draft artifacts and establish GitHub parents/bindings
  before they can continue. Tradeoff: immediate architectural convergence, but
  it mutates unrelated live or stale plans, requires operator decisions for
  each, and makes this rollout depend on a broad one-time migration.
- **C. Permanently support both lifecycles through an adapter choice.** Each
  repository chooses local-full-artifact or issue-native execution indefinitely.
  Tradeoff: maximum compatibility for non-GitHub consumers, but two domain
  models, validators, docs paths, and coordination contracts remain permanent.

Recommendation reason: A keeps migration reversible at the live-work boundary
without making the undesirable dual architecture permanent. It protects the
three runs that may contain real in-flight evidence, forces every unactivated
draft through the better model, and gives legacy removal an executable census
condition.

Operator decision: ignore all goal artifacts except this goal. Existing files
remain untouched as historical repository contents, but none is a migration
input, supported execution mode, or acceptance constraint. The target therefore
owes no legacy dual reader or grandfathered runtime path.

### Question 8 — Provisional Local Fallback Semantics (Answered: A)

When the adapter explicitly permits provisional local fallback but the selected
GitHub capability is unavailable, how far may the goal proceed?

- **A. Planning-only provisional state — recommended.** The full draft,
  interview, both critique rounds, to-be docs, child specs, final alignment, and
  briefing may complete. A separate typed planning observation records the
  missing capability; no Goal Binding or parent placeholder exists. `/goal`
  activation and implementation remain blocked until the parent/child graph is
  created and read back. Tradeoff: no autonomous execution while GitHub is
  unavailable, but execution authority never splits and no local progress
  tracker or later state merge is needed.
- **B. Local execution with later GitHub reconciliation.** The sidecar and local
  child records temporarily own execution/progress, then migrate to GitHub when
  available. Tradeoff: offline execution continues, but this recreates the
  second tracker the redesign is meant to remove and requires conflict/partial
  migration semantics.
- **C. Execute only already-existing GitHub children from cached identity.** If
  a verified graph existed before the outage, implementation may continue and
  queue provider mutations locally; a never-published goal remains blocked.
  Tradeoff: better outage tolerance, but child state can become stale and queued
  close/update operations create reconciliation and false-completion risks.

Recommendation reason: A makes `provisional` an honest planning capability, not
a disguised second execution backend. It preserves useful work during an outage
while keeping activation, child progress, and completion dependent on verified
GitHub authority.

Operator decision: A confirmed. Provisional fallback is planning-only. It may
reach a reviewed operator briefing, but it cannot activate, implement, advance
child execution state, or complete before verified GitHub authority exists.
Round-2 integrity refinement: planning-only fallback creates no Goal Binding or
placeholder parent identity. Its typed planning observation is separate; this
preserves the operator's chosen authority boundary without a fake sidecar.

### Question 9 — Disposition Of Provisional GitHub Parent #724 (Answered: A)

After the final briefing is approved, should the already-created #724 graph be
reconciled into the authoritative first dogfood run, or replaced?

- **A. Reuse and explicitly reconcile #724 — recommended.** Preserve its issue
  identity and the 29 verified relationships, replace the superseded body with
  the approved contract, mark the premature bootstrap and planning reset
  explicitly, rewrite #725–#727 into approved executable specs or supersede
  them when the final decomposition differs, and read the entire graph back.
  Tradeoff: the issue timeline retains the premature attempt, but that history
  is honest and the graph is not needlessly recreated.
- **B. Close #724 as superseded and create a new approved parent.** Preserve
  #724 as the failed bootstrap record, create a clean parent after approval, and
  move/relink every retained child. Tradeoff: the authoritative issue begins
  cleanly, but it adds many external mutations, creates duplicate tracker
  identity, and makes recovery distinguish failed versus current parents.
- **C. Keep #724 as a historical umbrella and create the approved run beneath
  it.** The new parent becomes another child or linked successor while #724
  records the broader history. Tradeoff: preserves both narratives but creates
  two parent-like authorities and makes completion semantics needlessly nested.

Recommendation reason: A treats the mistake as auditable history rather than a
reason to duplicate state. Since one agent owns updates and the provider has
already verified all 29 relationships, explicit reconciliation gives one stable
identity and the smallest chance of graph drift.

Operator decision: A confirmed. #724 remains the stable first-dogfood identity.
It is not authoritative while planning is unapproved; after approval its body,
children, and relationships are reconciled and read back as one external
transition.

## Reviewed To-Be Domain Model

This section is the planning target after both critique rounds. It remains
conditional design—not current behavior—until implementation and live dogfood
prove it.

### Domain Objects

1. **Goal Draft** — the complete local Markdown planning record. It accumulates
   research, decisions, critique dispositions, target architecture, child
   drafts, alignment results, and the operator briefing. Approval freezes its
   semantic body and binds its content hash. It never owns routine execution
   progress.
2. **Goal Binding** — a small checked-in structured sidecar keyed to one Goal
   Draft. It is wholly immutable and owns the approval identity, exact draft
   path/byte hash, GitHub parent identity, and exact initial approved child
   manifest. It carries no observation references, host activation identity,
   lifecycle state, child progress, percentage, slice log, or parent-body
   mirror. Its canonical path is the draft path with `.md` replaced by
   `.binding.json`.
3. **Goal Run** — one GitHub parent issue. After approval and exact readback it
   is authoritative for shared execution scope, dependency ordering, completion
   semantics, and sparse contract changes. Its provider state, not the binding,
   decides whether the run is open or closed.
4. **Work Item** — one real GitHub sub-issue whose body is an immediately
   executable and verifiable capability contract. Its provider state is routine
   progress. A Markdown mention is never relationship or completion proof.
5. **Provider Observation** — a typed result produced by the issue backend for
   preflight, mutation, or readback. It distinguishes no mutation, verified
   mutation, unverified mutation, and partial graph mutation so retry logic does
   not guess.

### Goal Binding V1

The checked-in sidecar is a wholly immutable integrity record with schema id
`charness.goal-binding/v1`. Its canonical path is the frozen Goal Draft path
with `.md` replaced by `.binding.json`. Canonical UTF-8 JSON key ordering makes
the complete binding byte hash stable. Version 1 contains only:

- `approval`: final briefing SHA-256, approval response identity, and approved-at
  observation supplied by the host/session record
- `goal_draft`: repository-relative path and SHA-256 of the complete frozen file
  bytes after Q1–Q9, both critique dispositions, alignment, and briefing are
  present
- `goal_run`: exact repository, issue number, and canonical URL, established or
  reused before binding creation
- `approved_work_items`: a canonical key-sorted initial manifest whose entries
  declare stable key, create/reuse intent, exact existing identity when known,
  body ownership/fingerprint, dependency keys, and deterministic execution rank
- `approved_graph_sha256`: SHA-256 of the canonical JSON representation of
  `approved_work_items`

The complete binding SHA-256 is the immutable approval anchor. It contains no
observation attachment, `status`, active/blocked flag, progress, current child,
host goal identity, cached provider state, or copied parent body. Provider-less
planning fallback creates neither a Goal Run identity nor a Goal Binding; it
emits a typed planning-only observation and resumes establishment after provider
readiness.

Changing draft bytes, approval identity, parent identity, or the initial
manifest requires a new explicit approval and a new binding. Missing files,
byte-hash mismatch, parent metadata mismatch, initial-graph mismatch, unknown
schema, and changed binding bytes are typed refusals.

Establishment, mutation, deferral, and terminal evidence are separate immutable
`charness.goal-run-observation/v1` receipts under
`charness-artifacts/goal-runs/<repo>-<number>/observations/`. Each receipt binds
operation/attempt id, binding/draft/parent identity, target manifest or Work Item
key, before state, submitted digest, returned provider identity, readback,
outcome, and next action. The issue backend serializes observations; `achieve`
consumes them and decides lifecycle progression.

The parent body contains exactly one versioned managed block delimited by
`<!-- charness-goal-run:v1` and `-->`; its interior is canonical JSON. Duplicate,
malformed, foreign-version, or stripped blocks refuse before any update/close.
The block names binding path/hash, draft path/hash, initial graph hash, current
membership hash/revision, establishment and optional terminal observation
path/hash, and the premature-bootstrap planning-reset note. Human-readable intent
remains ordinary Markdown. Parent readback must agree with immutable local
identities; neither side silently repairs the other.

### Authority And State Transitions

1. `shaping`: Goal Draft is mutable; no Goal Binding or GitHub authority is
   claimed.
2. `reviewed`: interview and two critique rounds are complete; conditional
   to-be docs, child drafts, and final alignment support the briefing.
3. `approved`: operator approves the briefing; the complete Goal Draft is
   frozen and hashed. If the provider is unavailable, a planning-only
   observation records why establishment cannot proceed; no binding exists.
4. `binding`: provider readiness and exact parent identity are known; the
   immutable V1 binding is created over the frozen draft and initial manifest.
5. `bound`: parent body, every initially approved child, and exact relationships
   have been reconciled and read back. A separate verified establishment
   observation is referenced by the parent; the binding remains unchanged.
6. `active`: the user invokes `/goal #<issue-number>`. `achieve` resolves that
   shorthand against the current repository, reads the parent, follows its
   Goal Draft/Goal Binding pointers, validates the identity chain, and reads the
   real child graph before choosing work. Active state is observed from the
   host goal plus provider state; it is not cached in the binding.
7. `closing`: a dedicated goal-run close operation reads every linked child,
   refuses any open child, verifies approved deferrals were moved to a successor
   with reason, closes the parent, and reads the parent state back through a
   distinct provider observation.
8. `complete`: the parent is provider-verified closed and its managed metadata
   references the immutable terminal observation. The binding remains the
   initial approved baseline and never declares GitHub completion.

There is no legacy full-artifact execution branch. Other local goal artifacts
are ignored and untouched.

This first #724 dogfood has one explicit self-hosting exception, not a generic
state: after approval, already-linked #726 may implement and locally prove only
the minimum provider graph primitives. Those primitives reconcile the exact
approved graph and mark the parent `pending-target-roundtrip`, allowing GitHub
child state to own progress while target `/goal` pickup remains blocked. After
all four system capabilities are built, the target commands independently
re-prove the same graph and replace the marker with verified establishment. No
later Goal Run, adapter, fallback, or second session inherits this bootstrap.

### Ownership

- `achieve` produces Goal Draft/Binding and owns lifecycle semantics, interview
  budgeting, approval, graph policy/order, executable-child selection, and final
  consumption of provider observations.
- Work Item capability owners produce executable/verifiable issue bodies;
  GitHub owns their mutable state and relationships; implementing agents and the
  guarded parent close are their final consumers.
- `issue` owns provider/backend mechanics and Provider Observation
  serialization: readiness, exact identity, file-backed bodies, parent update,
  relationship mutation/listing, guarded issue close, and post-mutation readback.
- `achieve`, not `issue`, composes provider primitives into initial graph
  establishment or later graph-policy decisions.
- adapters own environment policy only: question ceiling, selected issue
  backend, and whether planning-only provisional fallback is allowed.
- `docs/` owns the evergreen domain model and authority transitions.
- GitHub owns mutable execution state; the repository owns the frozen design and
  the narrow identity binding.

### Mutation And Recovery Rules

- Every provider mutation performs exact preflight at its mutation ingress and
  returns a typed observation. A failed readback is never reported as success.
- Multi-child reconciliation is resumable rather than transactional. Before
  invoking each mutation, `issue` persists a bounded `started` attempt. An
  invoked command without conclusive readback is `unverified` or `partial`,
  never `no-write`. Returned identities and verified results are retained; a
  retry re-reads before mutating and never blindly recreates an ambiguous child.
- `create-or-reuse` uses a stable Work Item key in managed body metadata and
  read-only discovery. If an invoked create has no discoverable exact identity,
  reconciliation stops for operator disposition instead of retrying create.
- Parent close has one dedicated operation. Generic issue close cannot close a
  Goal Run without the all-children-closed observation and distinct post-close
  readback. This places teeth at the irreversible boundary without adding
  concurrency machinery for a single-agent updater.
- Parent-body updates are byte-read-back and sparse. Generic update refuses to
  remove or alter Goal Run metadata without the binding-aware operation. Child
  state supplies routine progress; neither Goal Draft nor Goal Binding
  duplicates it.
- Exact binding manifest equality is required for initial establishment. After
  binding, GitHub owns execution graph evolution: in-scope additive discoveries
  and verified deferrals update parent membership metadata and carry exact
  reason/identity/readback observations. Changes to objective, non-goals,
  success criteria, or proof policy require explicit operator approval.

### Transition And Interface Matrix

| Transition | Semantic owner | Required input | Provider evidence | Binding effect | Retry/refusal |
| --- | --- | --- | --- | --- | --- |
| research → reviewed draft | `achieve` | repo/docs/tracker facts, bounded answers, two critiques | read-only issue observations when used | none | stop on consequential ambiguity or question-cap exhaustion |
| reviewed → approved | `achieve` | final briefing plus explicit operator yes | none | freeze complete draft; no binding until exact parent exists | changed draft requires re-approval |
| approved → planning-only unavailable | `achieve` | adapter-explicit fallback and failed provider readiness | typed no-write planning observation | none | activation/implementation/progress/completion refuse; retry readiness later |
| approved → binding | `achieve` | ready backend, exact reused/created parent, frozen draft, initial manifest | verified parent identity readback | create immutable V1 binding | changed core requires re-approval; no auto-rebind |
| binding → bound | `achieve` orchestrates; `issue` mutates/observes | valid binding and complete provider capability closure | typed started/no-write/verified/unverified/partial establishment receipt | none | clean retry re-reads parent, bodies, children, and relationships before any write |
| bound → active pickup | host stores `#N`; `achieve` resolves through `issue` | exact repository plus parent number | fresh parent, managed metadata, membership, and child state readback | none | refuse unresolved repo, non-parent, missing/mismatched pointers, closed parent, or invalid membership revision |
| active → child progress | selected Work Item workflow | one open child contract | provider child state plus child-owned behavioral proof | none | child remains open/blocked; no parent progress rewrite |
| active → in-scope child amendment | `achieve` policy; `issue` primitives | executable child body, stable key/rank/dependencies, reason | create/reuse/link/body/parent membership readbacks | none; parent current graph revision changes | semantic goal change requires operator approval; ambiguous create stops |
| active → deferred child | `achieve` policy; `issue` primitives | successor Goal Run, durable reason, exact child | successor add, current remove, both parent readbacks | none; both parents record transition | parent remains unclosable until successor mapping is verified |
| active → semantic goal change | operator plus `achieve` | proposed objective/non-goal/success/proof change | parent contract update readback | initial binding remains historical baseline | explicit approval required before applying change |
| active → complete | `issue` dedicated guarded close | each child's closeout evidence/comment or verified deferral plus whole-system proof | distinct pre-close, mutation, and post-close observations | none; parent references terminal receipt | generic close refuses before comment/write; failed post-readback is unverified, not complete |

### Host Activation Contract

The user surface is deliberately small:

`/goal #724`

Issue-native pickup accepts exactly one trimmed objective matching
`^/goal[ ]+#[1-9][0-9]*$`; malformed or compound text returns
`goal-objective-invalid`. Repository resolution precedence is: an explicit
achieve/issue adapter repository, then one canonical provider-compatible Git
remote. No remote, multiple conflicting remotes, or the current basename guess
returns `repository-unresolved` or `repository-ambiguous` before a provider
call. `achieve` passes the normalized exact `(repository, number)` to the
adapter-resolved `issue` backend.

The parent managed block identifies binding/draft paths and hashes, immutable
initial graph hash, current membership revision/hash, and establishment
observation. The workflow validates parent ↔ binding ↔ draft ↔ establishment,
then compares the stored current membership hash with fresh real relationships.

The sidecar is therefore internal integrity evidence, not a user-facing input
or a special host parser format. Official Codex documentation confirms that
`/goal <objective>` accepts ordinary objective text; the `#<issue-number>`
interpretation is Charness lifecycle semantics owned by `achieve`/`issue`, not
an OpenAI host-runtime claim.

An executable child is open, has valid Work Item metadata/body, and has every
declared prerequisite closed or explicitly satisfied. Selection is lowest
execution rank, then stable Work Item key, then exact repository/number. The
initial manifest puts the independent binding/provider roots first, then
orchestration, evidence-lineage cutover, dogfood establishment, and finally the
ranked P0–P2 cohort. Strategic priority changes are parent contract changes, not
implicit model judgment.

Typed pickup failures name the next action:
`goal-objective-invalid`, `repository-unresolved`, `not-a-goal-run`,
`metadata-invalid`, `binding-missing`, identity/hash mismatch,
`graph-not-established`, `graph-invalid`, `dependency-cycle`,
`dependency-blocked`, `stale-child`, `no-executable-child`,
`all-children-closed`, and `parent-closed`. None falls back to the old local
active-goal path. `all-children-closed` routes to final proof/guarded close;
`no-executable-child` reports the exact blocking keys.

### Final Capability Decomposition

The five independently closable system capabilities are specified in the
[proposed child graph](../specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/index.md):

1. `goal-binding-v1` — one canonical Goal Draft producer plus immutable
   binding validation, including handoff production.
2. `goal-run-provider` — complete issue-backend preflight, exact graph
   primitives, typed observations, retry semantics, and non-bypassable close.
3. `achieve-orchestration` — researched planning, bounded questions, two
   critiques, approval, graph policy, active coordination, and exact
   `/goal #N` pickup.
4. `goal-evidence-lineage` — premise/slice/critique/prove/retro/closeout/
   host/release evidence bound to one run and child, plus the final consumer
   classifier. It is deliberately not a broad migration owner.
5. `dogfood-724-establishment` — use the bounded provider bootstrap to reconcile
   #724, then after all four system capabilities independently re-prove it and
   the 26 audited backlog identities as the first live run.

The existing 26 Work Items have a separate
[readiness contract](../specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md):
23 open issues require managed executable addenda and fresh premise readback;
closed #721, #694, and #628 preserve their issue-owned behavioral evidence.

### Critique Round 1 Disposition

Round 1 consumed packet
`charness-artifacts/critique/issue-native-achieve-planning-r1-packet.json`
(packet SHA-256
`59425e174344798ed0ed1d3bcfd90e05f2040e3808ba9103a6f2a97de769a06a`;
input identity
`284146b7316146be3b1adfc6b4117903658f4f1372a75a5506c77cda9ea0a53b`)
through framing, ownership, operability, and counterweight passes. Boundary
fingerprints verified clean for all four parent-delegated reviews.

Applied findings: quarantine the prototype; define the exact binding/hash and
mismatch refusals; establish `/goal #N`; require exact desired-graph equality
and typed partial reconciliation; add this transition matrix and a dedicated
issue-owned close; inventory every local-goal consumer; strengthen child specs;
and replace legacy migration with removal/non-support.

Deliberately not doing: a second local ledger, transactions, optimistic
concurrency, a host-runtime redesign, legacy migration/grandfathering, or a
generic cross-host activation abstraction without evidence. No consequential
operator question emerged, so the ledger remains 9 used and 6 available.

### Critique Round 2 Disposition

Round 2 consumed
`charness-artifacts/critique/issue-native-achieve-planning-r2-packet.json`
(packet SHA-256
`eb26b80d98df588225b9de83238eca9c9183e46e7cdb70efa2e56638a02a4135`;
input identity
`b45f76ee24ceb6c988ab03e66dfa01abd02b22a94bdf3171e8d5578b742149c7`)
through architecture, operator-readiness, provider-failure/close, and
counterweight passes. All four file-backed fresh-eye workers delivered
schema-valid findings. Reviewer boundary verification classified worker-output
files as parent-attributed changes during the windows; no tracked target-design
drift was attributed to a reviewer, but this is not claimed as an empty
worktree window.

Applied findings: make the entire binding immutable and move observations out;
create no binding in provider-less fallback; separate immutable initial graph
from verified parent-owned graph evolution; fully specify preflight, ambiguous
create, partial result, metadata protection, and guarded close; parse
`/goal #N` and repository identity exactly; bind child-owned evidence rather
than creating a second ledger; split the broad consumer child by ownership;
restore the complete nine-question ledger; audit all 26 reused issue bodies;
and replace aspirational proof prose with explicit target commands and fixtures.

Rejected as over-design: signatures/authentication machinery, event sourcing,
transactions, optimistic concurrency, a local acceptance database, extra
user-facing binding paths, and rewriting historical prototype evidence. Live
GitHub and alternate-backend behavior remain deferred proof obligations, not
planning claims. The counterweight found no consequential new choice: all
repairs follow already-confirmed single-authority, planning-only-fallback, and
evidence-bound-preservation decisions. Nine questions remain used and six
remain unused. The user requested exactly two critique iterations, so these
round-2 repairs are accepted under that cap and receive no claimed third
fresh-eye review; the final alignment audit is a direct synthesis check.

## To-Be Documentation Requirement

Before the approval briefing, `docs/` must contain an explicitly conditional
description of the intended system:

- domain concepts and vocabulary
- state transitions and authority boundaries
- ownership of goal draft, parent issue, sub-issue specs, and provider readback
- public-skill versus adapter versus backend responsibilities
- planning, approval, execution, recovery, deferral, and closeout flows
- removal and documented non-support of legacy full-goal execution behavior
- concepts and paths to remove rather than preserve as permanent seams

These docs must not claim unimplemented behavior is current. Completion later
requires reconciling them with the implementation and removing conditional or
to-be labels only when the built system proves the claim.

## Executable Sub-Issue Contract

Every proposed child must state:

- purpose and user/system capability
- current state and target state
- owning surface and explicit boundaries
- inputs, dependencies, and non-goals
- implementation contract and relevant to-be docs
- acceptance criteria
- deterministic tests and any runtime/provider proof
- documentation impact
- closeout evidence and residual non-claims

Children are capability slices, not file buckets. Completing all children must
compose into the intended system without a final catch-all integration issue
that hides architectural seams.

## Final Alignment Audit

Before briefing, inspect the full goal, to-be docs, proposed children, current
system, and cutover/removal path together. The audit must answer:

- Are domain concepts minimal, stable, and named consistently?
- Does each fact, state, and policy have one clear producer/owner?
- Are dependency directions and public/internal boundaries natural?
- Does the design remove accidental seams instead of institutionalizing them?
- Can every child execute and prove one independently closable capability?
- Does the child graph cover every required transition into the to-be system?
- Will completing the graph actually produce the documented architecture?
- Can a future maintainer understand the result without this conversation?

Any consequential ambiguity returns to the bounded question queue. The audit is
not complete merely because validators or both critique rounds are green.

The completed [final alignment audit](../specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/final-alignment-audit.md)
passes the model, authority, ownership, transition, child-executability,
cutover, and documentation checks. It found and repaired one final structural
cycle: the first Goal Run could not depend on its own not-yet-built provider and
pickup. The bounded #724-only bootstrap now makes that dependency explicit
without adding a generic fallback or second tracker. No consequential question
remains; question use stays 9 of 15.

## Required Operator Briefing

The briefing following final alignment must explain:

- the problem, purpose, and reason to act now
- the current system and its structural failure
- the target domain model and architecture
- why the target is more coherent
- what remains, changes, migrates, or is removed
- the proposed child graph and implementation order
- verification, provider proof, and closeout strategy
- risks, rollback/cutover posture, non-goals, and non-claims
- question-budget use and any remaining decisions

The briefing ends by asking whether to finalize/reconcile GitHub and begin
implementation. Without explicit approval, the run stops in reviewed-planning
state.

The exact briefing presented for approval is
[Implementation Briefing: Issue-Native Achieve And First Dogfood](../specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/implementation-briefing.md).

## Backlog Scope

The original cohort remains the 26 P0–P2 issues: #723, #722, #721, #717, #715,
#710, #708, #706, #704, #703, #701, #700, #699, #698, #697, #695, #694,
#693, #692, #669, #668, #667, #637, #634, #628, and #546.

P3 issues #711, #709, #705, #702, #688, #612, #599, #584, #583, and #582
remain outside this goal unless a later operator decision changes scope.

## Non-Goals And Boundaries

- Do not continue or legitimize the prototype implementation during planning.
- Do not mutate the provisional GitHub graph before briefing approval.
- Do not close issues, push, tag, publish, run remote CI, or mutate installed
  surfaces without the separately required authorization and proof.
- Do not turn the local goal into a progress log after approval.
- Do not ask the operator for facts the repository can establish.
- Do not equate fewer lines, smaller diff, more validators, or green tests with
  a better target system.
- Do not preserve a flawed compatibility path merely because it already exists
  in the prototype.

## Completion Conditions

Planning completes only after the two critique rounds, final alignment audit,
and approved briefing. The overall goal completes only when:

- the approved GitHub graph has exact provider readback
- every child is closed with its own behavioral evidence or moved to a successor
  parent with reason
- the parent has no linked open children and its close is independently verified
- the implementation matches the target domain model and architecture
- `docs/` honestly describes the built current system
- legacy/provisional seams are removed or explicitly dispositioned
- final whole-system proof and fresh-eye closeout review are bound to the result

## Sources

- [Design north star](../../docs/design-north-star.md)
- [Current handoff](../../docs/handoff.md)
- [Recent lessons](../retro/recent-lessons.md)
- [Cortex #702 gathered reference](../gather/2026-08-26-cortex-702-achieve-tracker-reference.md)
- [Premature Phase 0 prototype record](../specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/spec.md)
- [Official Codex goal-objective contract](../gather/2026-08-26-codex-goal-objective-contract.md)
- Provisional GitHub parent: `corca-ai/charness#724`

## Research Notes

### Verified Current System At `HEAD`

- `achieve` currently has one central domain object: a mutable Markdown goal
  artifact under `charness-artifacts/goals/`. It is not merely a plan. Across
  Before/During/After it owns draft shaping, `draft`/`active`/`blocked`/
  `complete`/`superseded` status, `/goal` activation identity, current frame,
  slice history, verification, closeout evidence, retro, and non-claims.
- `goal_artifact_lib.py` and its sibling modules implement that state machine.
  `upsert_goal` creates once and thereafter changes only status;
  `append_slice_log.py` mutates the same artifact; `check_goal_artifact.py` and
  `charness goal check` validate local shape and pursue readiness. Host-level
  completion is explicitly downstream of a locally complete artifact.
- `handoff` is a second producer of the same nominal goal type. Its
  `draft_goal_from_chunk.py` uses a separate copied template and refuses
  overwrite independently of `upsert_goal.py`. Current docs acknowledge the
  auto-draft as an unshaped artifact that later routes through `achieve`. This
  is already a producer-drift seam that the cutover must eliminate rather
  than preserve as a third lifecycle.
- Active-goal coordination is presence-gated on a local file whose status is
  `active`. `impl`, `quality`, `critique`, and `issue` are instructed to read or
  append that file. Premise, retro, slice-manifest, release claims-review, docs
  checks, and other support scripts also bind durable evidence to `goal_path`.
- The coupling is broad, not incidental: at `HEAD`, 74 tracked source/doc/test
  files contain the canonical goal-directory path, 46 contain `goal_path`, 30
  contain `Status: active`, and 11 contain `append_slice_log.py`. The achieve
  package has 50 script files, the issue package 40, and at least 75 tests
  mention goal-artifact or issue-tool behavior. Counts describe cutover
  topology, not design quality.
- The achieve adapter currently owns repo/language/artifact location,
  scaffolding, closeout publication, and retro defaults. It has no interview
  ceiling or tracker-fallback policy at `HEAD`.
- `issue` currently owns generic issue creation, reading, selection, closeout,
  and adapter-resolved provider commands. Its backend already has the useful
  hard parts for the proposed lifecycle: binary/auth preflight, exact
  `(repository, number)` identity, repository-qualified command templates,
  file-backed body safety, create readback, and explicit handling of
  unverified writes. It does not own parent-body updates or real sub-issue
  relationship operations at `HEAD`.
- The existing documentation truth says the local artifact is the single
  durable/running-memory surface. This claim is owned at least by
  `docs/workflow-routes.md`, `docs/readme-proof.md`, `docs/cli-reference.md`,
  `docs/artifact-policy.md`, `docs/prescribed-skill-closeout-contract.md`, and
  the handoff chunked-routing contract. No evergreen page currently owns a
  distinct goal-lifecycle architecture or a draft-versus-execution authority
  model.

### Verified Provider And Provisional Graph Facts

- GitHub parent `corca-ai/charness#724` is open and currently has 29 real
  sub-issues: all 26 original cohort issues plus provisional #725–#727.
- Provider readback reports 29 total, 3 closed, and 10 percent complete. Each
  listed child payload includes repository identity and `parent_issue_url`, so
  real relationship proof is available independently of Markdown links.
- #724–#727 were created before the newly confirmed planning, two-critique,
  to-be-docs, final-alignment, briefing, and approval boundaries. Their current
  bodies therefore record a superseded proposal, not an approved contract.
- In particular, #724 and #727 say the full draft will be replaced by a minimal
  receipt. The operator has since decided the full local planning draft is
  preserved and frozen after approval. None of #725–#727 yet satisfies the new
  immediately-executable-and-verifiable child contract: they omit concrete
  dependencies, acceptance/proof commands, cutover boundaries, docs impact,
  and residual non-claims.

### Unapproved Prototype Observations

- The prototype changes 18 tracked contract/source/test surfaces by roughly
  544 added and 120 removed lines and introduces three source scripts plus
  three test files. It adds an adapter interview ceiling, a structured
  interview validator, a minimal receipt type, parent-update/sub-issue backend
  operations, and tracker-oriented skill prose.
- The prototype hard-codes the now-rejected transition from full draft to
  minimal receipt and splits current versus legacy behavior inside the public
  skill. That is proposal evidence, not an accepted compatibility model.
- Earlier bounded review found concrete proof and ownership gaps: local receipt
  validation could pass without live parent/child readback; tracker preflight
  did not compose binary/auth/capability readiness; generic mutation was not
  bound to the active goal identity; the parent-close guard was not enforced at
  irreversible mutation ingress; provisional fallback state was not fully
  representable; one bootstrap example contained a literal invalid path;
  exported recovery proof omitted lane/dependency/child-progress/closing-rule
  behavior; and post-mutation readback failure lacked a typed partial-success
  result. These findings remain inputs to the planned critique rounds, not
  implementation tasks yet.

### Structural Tensions The Target Must Resolve

- Preserve the rich local draft without letting it remain a competing execution
  tracker after approval.
- Separate stable planning intent, host objective text, mutable execution state,
  and terminal proof so each has one owner and evidence channel.
- Cut over all local-file presence/status consumers coherently; adding an
  issue-native branch beside the full-artifact branch indefinitely would make
  the public model more tangled.
- Extend the existing `issue` backend for provider operations rather than
  inventing a second GitHub readiness/identity stack in `achieve`.
- Keep adapter policy about environment/capability defaults in adapters while
  keeping lifecycle semantics and state transitions in the public skill/domain
  contract.
- Reconcile the handoff auto-draft producer with the canonical draft model so
  there is one creation path or one shared schema, not copied templates that
  drift.
- Define recovery after partial external mutation explicitly: the durable state
  must distinguish no write, verified write, unverified write, and partially
  completed graph mutation without repeating mutations blindly.

### To-Be Documentation Surface Identified By Research

- Add one evergreen owner for the goal lifecycle domain model and authority
  transitions.
- Update workflow routing and README proof claims from “one local running-memory
  artifact” to the approved draft/execution split.
- Update CLI reference for any new inspect/preflight/readback surface.
- Reclassify the full draft and provider-backed execution state in artifact
  policy.
- Reconcile handoff chunked routing and its auto-draft producer with the single
  canonical planning model.
- Update the prescribed closeout contract and shared active-goal coordination
  only after the target state/identity model is settled.

### Remaining Planning Work, Not Operator Decisions

- Finalize independently executable capability children so every local-goal
  consumer moves without a catch-all integration seam.
- Verify round 2 against the conditional docs, child graph, clean-process
  reconciliation, and irreversible parent-close boundary.
- Run the meticulous final alignment audit and prepare the approval briefing.

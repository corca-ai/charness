# Phase 0: Make issue-native achieve tracking real and dogfood it here

Status: provisional prototype evidence — implementation was not approved; retained for planning review
Goal: [adversarial-priority-backlog-closeout](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)

## Supersession Map

This file is historical proposal evidence, not an implementation contract. The
[full goal draft](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)
and [planning contract](./planning-contract.md) are the only normative planning
sources for this run.

| Prototype clause | Disposition | Normative replacement |
| --- | --- | --- |
| Repository research before questions and adapter ceiling default 15 | retained as evidence | bounded interview in the planning contract |
| Backend-routed parent update and real sub-issue operations | retained as candidate evidence | issue-owned Goal Run operations in the full draft |
| Create the parent immediately after the initial interview | rejected | two critique rounds, to-be docs, alignment, briefing, and approval precede reconciliation |
| Replace the full draft with a minimal receipt | rejected | preserve and freeze the full draft; use a narrow integrity binding |
| Activate through a local file/receipt identity | rejected | user invokes `/goal #<parent-number>`; `achieve` resolves the parent and follows its internal pointers |
| Permanent current-versus-legacy compatibility branches | rejected | other goal artifacts are ignored; the old execution path is removed or explicitly unsupported |
| #725–#727 as already executable child specs | rejected | rewrite or supersede them against the final capability graph after approval |
| Prototype code and tests as the implementation target | rejected | they may inform implementation only after an approved child contract selects a behavior |

Do not implement from the remainder of this file. Where it conflicts with the
normative sources above, this map makes the conflict explicit rather than
silently editing historical proposal text.

## Tracker Identity

- Parent: `corca-ai/charness#724`
- URL: https://github.com/corca-ai/charness/issues/724
- New Phase 0 children: #725 migration/dogfood, #726 issue backend, #727
  achieve interview and compatibility lifecycle
- Existing children: all 26 claimed issues, including already-closed #721,
  #694, and #628
- Relationship readback: 29 exact children, 26 open and 3 closed; no missing,
  unexpected, or wrong-parent entries on 2026-08-26
- Authority: none established for implementation. The GitHub objects are
  provisional external facts, the restored full goal owns planning, and the
  final briefing approval decides whether and how to reconcile the graph.

> Planning correction: this spec records the premature first implementation
> attempt. It does not authorize further code, tracker mutation, or closeout.
> The operator-approved lifecycle now lives in
> [planning-contract.md](./planning-contract.md).

## Objective

Change `achieve` so it researches the repository, drafts the goal, asks only the
remaining consequential questions (at most an adapter-controlled limit, default
15), then creates a GitHub parent issue and manages independently closable work
through real GitHub sub-issue relationships. Use this active backlog-closeout
goal as the first end-to-end case.

## Capability Contract

An operator can give `achieve` an under-specified long-running outcome and receive
a researched, reviewable interview with options, per-option tradeoffs, and one
reasoned recommendation. After the answers settle the contract, collaborators can
inspect the parent issue to understand current intent, acceptance, dependencies,
progress, and child state without needing a separate full goal file as the
tracking source of truth.

## Public-Skill Capability Brief

- Artifact class: improvements to two public skills with one canonical source
  implementation each (`achieve` owns the goal lifecycle; `issue` owns GitHub
  tracker mutations). Generated plugin placements mirror those implementations;
  they are not intentional forks.
- Audience: an agent operating a long-running goal and collaborators recovering
  that goal from GitHub.
- Trigger: `$achieve <outcome>` or continuation of an active issue-native goal;
  ordinary one-off issue filing/resolution remains `issue` behavior.
- Current failure: `achieve` asks an unbounded prose interview, saves a full local
  tracker, and cannot establish or operate a real parent/sub-issue graph through
  the selected issue backend.
- Portable intake: preserve the existing Before/During/After lifecycle and host
  goal-slot boundary; change the shared tracker and question contract without
  hardcoding Charness repository identity or the `gh` binary.
- External dependency: GitHub operations route through the issue adapter. The
  default authenticated backend is `gh`; alternate backends must declare every
  tracker operation. Provider-roundtrip proof is required only for this live
  dogfood case; fake-backend tests remain local proof.
- Accumulated state: before activation, a reviewable draft and interview answers;
  after verified parent creation, the GitHub parent and child graph plus a minimal
  local activation/compatibility receipt.
- Proof boundary: adapter validation and fake-backend tests cannot claim live
  GitHub operation; exact relationship and body readback from #724 is the live
  channel. Child CLOSED state is progress, not behavioral proof of its fix.
- Cold start: research first, draft, ask no more than the configured ceiling,
  create/read back the parent, create/reuse/read back known children, then reduce
  local state to the receipt.
- Warm start: resolve the receipt to the frozen parent, read current body and real
  child states, and continue the owning open child without replaying the interview.
- Error recovery: default activation refuses unavailable tracker capability;
  explicit adapter fallback is provisional, preserves successful identities, and
  reconciles rather than duplicating issues.
- Concrete failure cases: asking facts discoverable from the repo; treating 15 as
  a target; creating the parent before answers settle; duplicating an existing
  child; treating a checklist as a relationship; rewriting routine progress into
  local Markdown; closing a parent with linked open children.

## Verified Facts

- The current `achieve` contract asks a small number of high-leverage questions,
  but has no explicit maximum, no adapter field for that maximum, and no
  structured option/tradeoff/recommendation requirement.
- `.agents/achieve-adapter.yaml` is valid and currently owns publication,
  Auto-Retro, and scaffold policy; it is the natural owner for an interview cap.
- Baseline: `issue_tool.py` could plan, create, verify, read, comment-close, and
  verify closeout, but could not update a body or manage sub-issues. The current
  implementation adds backend-routed tracker preflight, update, list, add, and
  remove commands; focused and live readback proof are in progress.
- Authenticated GitHub REST reads return the real sub-issues of
  `corca-ai/cortex#702`. The current claimed Charness issues sampled (#723 and
  #721) have no parent issue and no children.
- [Cortex #702 gathered reference](../../../gather/2026-08-26-cortex-702-achieve-tracker-reference.md)
  demonstrates the desired parent shape: shared principles and completion in the
  parent; narrow executable work in real sub-issues; dependency-aware ordering;
  no duplicate umbrella implementation unit.

## Scope In

- Before-phase repository research and question selection
- `interview.max_questions`-style adapter policy with default 15
- structured question records: decision, options, tradeoffs, recommendation,
  recommendation reason, answer, and rejected-alternative reason
- parent-issue creation after the interview completes
- real GitHub sub-issue create/reuse/link/readback operations
- sparse parent-body updates when goal scope, policy, dependencies, or completion
  semantics change; routine progress comes from GitHub sub-issue state
- current-goal migration: create one Charness parent tracker, reuse the existing
  claimed issues as children where appropriate, add only genuinely new child work,
  and keep the parent current while this goal proceeds
- compatibility and migration behavior for historical/current goal artifacts,
  host goal slots, closeout validators, retro binding, and non-GitHub repos

## Scope Out

- duplicating an existing issue merely to make it a child
- treating a Markdown checklist as proof of a GitHub sub-issue relationship
- adding a concurrency protocol for a tracker that is contractually owned by one
  updating agent
- making issue creation imply push, release, tag, remote CI, or installed-host
  mutation authority
- migrating historical completed goal artifacts unless a compatibility reader
  needs an explicit pointer

## Open Decisions

None. The interview stopped after five consequential questions; the default cap
of 15 remained a ceiling rather than a target.

Derived implementation constraints from success-criteria review are settled,
not operator choices: `max_questions` accepts any positive integer (booleans,
zero, negatives, strings, and fractions are invalid). Reaching the configured
ceiling with consequential decisions still unresolved produces typed
`interview-cap-reached`, refuses parent creation, and asks the operator to raise
the adapter ceiling or narrow the goal; it never silently drops a question.

## Interview Decisions

### Canonical state

- Chosen: the GitHub parent issue is authoritative. Keep only a minimal local
  activation/compatibility receipt containing the parent repository, number,
  URL, host activation identity, frozen target, and closeout-evidence pointers;
  do not mirror progress locally.
- Recommended because: it gives collaborators one current tracker while retaining
  the minimum local identity needed by host goal slots, compatibility readers,
  validators, and recovery after context loss.
- Rejected — full dual-write: maximizes offline readability but creates
  reconciliation and stale-mirror failure modes on every progress update.
- Rejected — pure GitHub with no local receipt: has the cleanest single source of
  truth but strands local activation identity and existing artifact consumers.
- Answered by operator: `A` on 2026-08-26.

### GitHub unavailable or incapable

- Chosen: fail activation by default when the selected GitHub backend is
  unavailable or lacks parent/update/sub-issue capabilities. Permit a temporary
  local fallback only when the achieve adapter explicitly enables it.
- Recommended because: failure is visible and the authoritative tracker cannot
  silently split, while an explicit adapter policy still supports offline or
  non-GitHub environments that knowingly accept reconciliation work.
- Rejected — automatic local continuation: maximizes availability but can create
  two competing progress histories without an operator choosing that risk.
- Rejected — never permit fallback: has the simplest authority rule but excludes
  intentional offline and non-GitHub host deployments.
- Fallback obligation: mark the activation as provisional, create no GitHub
  identity claims, and reconcile into a verified parent before authority moves.
- Answered by operator: recommended policy accepted on 2026-08-26.

### Parent update protocol

- Chosen assumption: one agent owns parent-issue updates; concurrent human edits
  are out of contract for the default workflow.
- Chosen behavior: use real child state for routine completion/progress. Update
  the parent body only when shared goal intent, scope, policy, dependencies, or
  completion semantics change; record exceptional decisions only when they add
  durable context not represented by a child issue.
- Recommended because: most lifecycle mutations are child close/link operations,
  and GitHub already renders that state. Re-rendering progress into the body or
  comments would duplicate the source of truth.
- Rejected — managed sections plus optimistic concurrency: protects an edit
  pattern the operator says does not exist and adds hashes, conflict recovery,
  and tests without improving the normal case.
- Rejected — transition comment for every child event: preserves an explicit log
  but duplicates GitHub's issue history and produces noise.
- Answered by operator: single-agent ownership and sub-issue-state-first tracking
  on 2026-08-26.

### Child lifecycle

- Chosen: immediately after the interview, create or reuse and link every known,
  independently closable work item. Prefer an existing issue identity and refuse
  duplicates. Add newly discovered children lazily only when investigation makes
  them concrete and independently closable.
- Recommended because: the parent exposes the real initial execution scope at
  activation while avoiding speculative future issues. Later discoveries remain
  visible without pretending they were known during planning.
- Rejected — create every anticipated child up front: maximizes apparent
  visibility but turns hypotheses and possible splits into noisy issue inventory.
- Rejected — create all children lazily: keeps activation small but leaves the
  parent unable to show the already-known executable scope.
- Split/defer rule: link a new child only for a genuinely independent outcome;
  preserve the original issue and record the split or deferral in the parent only
  when it changes shared scope or completion semantics.
- Answered by operator: recommended policy accepted on 2026-08-26.

### Current-goal migration membership

- Chosen: link all 26 existing claimed issues as real children, including #721,
  #694, and #628, which closed before the parent existed. Create new children
  only for independently closable Phase 0 work that has no existing issue.
- Recommended because: this first-case migration preserves the goal's original
  scope, completed work, and truthful denominator instead of rewriting history at
  the moment the tracking mechanism changes.
- Rejected — link only the 23 still-open issues: produces a cleaner current queue
  but erases completed work from the parent graph and understates progress.
- Rejected — link open issues and mention the closed three only in the body:
  preserves prose history but makes the real sub-issue graph incomplete.
- Answered by operator: recommended policy accepted on 2026-08-26.

### Parent completion semantics

- Chosen: close a parent only when every issue still linked as its child is
  closed. A genuinely deferred open child moves to a successor goal parent with
  a recorded reason before the current parent closes.
- Recommended because: parent completion remains equivalent to 100% completion
  of its actual graph, while deferred work stays visibly open under the outcome
  that now owns it.
- Rejected — close with optional children open: preserves the relationship but
  makes the closed parent and incomplete progress indicator disagree.
- Rejected — close deferred children as completed: produces a clean percentage
  by hiding work that still exists.
- Answered by operator: recommended policy accepted on 2026-08-26.

## Completion Criteria

- The adapter defaults to a maximum of 15 questions and validates an override;
  normal interviews stop earlier when no consequential ambiguity remains.
- Question output and durable answer records include options, tradeoffs,
  recommendation, recommendation reason, chosen answer, and rejected reasons.
- No question asks for a fact that repository/code/tracker inspection could have
  established first.
- Parent creation is refused with `interview-cap-reached` when the ceiling is
  exhausted before consequential ambiguity is resolved; the ceiling never pads
  an otherwise-complete interview.
- Before the full draft is reduced, the parent body preserves each structured
  interview decision's options, tradeoffs, recommendation/reason, and answer so
  recovery does not depend on the transitional spec.
- Parent creation occurs only after the interview is complete, through the
  adapter-selected issue backend with create readback.
- Real sub-issue relationships are created/reused and read back; duplicates are
  refused.
- Parent updates are sparse and read back after mutation; routine progress is
  derived from real sub-issue state rather than duplicated into parent text.
- This goal has a verified Charness parent issue, linked/reused child issues, and
  a readback of the parent contract plus child-derived progress before the
  backlog lanes resume.
- Compatibility behavior for goal artifacts, host slots, retro, and non-GitHub
  repos is explicit and tested.

## Verification

- Focused adapter tests for default, override, malformed, and boundary values
- Before-phase fixtures proving repository-resolved questions are omitted and the
  maximum is a ceiling; cover zero/few, exact-cap, over-cap candidate, positive
  override, and malformed/non-positive override cases
- fake-backend tests for create/update/link/readback, duplicate refusal, partial
  failure, and sparse parent update behavior
- authenticated GitHub readback for this goal's parent and sub-issue relations
- clean-consumer recovery with the full goal draft unavailable: resolve the
  receipt, read the parent and children, and identify objective, settled policy,
  current executable lane, dependencies, progress, and closing rule
- source/plugin mirror synchronization and consumer-layout checks
- changed-line proof before broad quality
- bounded fresh-eye review of the issue/goal verdict and mutation surfaces; a
  second round reads repairs when the first round changes verdict logic

## Non-Claims

- The cortex tracker is a design reference, not evidence that Charness already
  implements the pattern.
- A local fake-backend pass does not prove GitHub mutation until this goal's
  parent/sub-issue readback succeeds.
- The manually established #724 graph proves the live relationship pattern, not
  that the new `issue_tool.py` path can create it; the implemented command owes a
  separate fake-backend path plus authenticated readback.
- Issue tracking does not authorize code publication or release.
- Until the interview settles the remaining decisions and the parent is created,
  the current goal artifact remains the active compatibility tracker. After
  verified parent creation it is reduced to the minimal receipt defined above.

## Failure Handling

If verification fails, use `debug` and a 5-whys root-cause pass. Preserve any
successfully created GitHub identities, classify partial parent/child linkage,
and resume idempotently; never create replacement issues to hide a failed link or
stale update.

## Success-Criteria Review

- Fresh-eye satisfaction: parent-delegated; findings-received.
- Reviewer tier: medium requested through the host default; concrete model
  application metadata was not exposed.
- Boundary verdict: `parent-attributed`; only this spec path changed by the
  parent during the window, explicitly declared, with no undeclared drift.
- Folded findings: define positive-integer override semantics and cap exhaustion;
  preserve full structured decisions in the parent; name current lane and
  dependencies; test exact identities/parents rather than child count; update
  public-skill dogfood and prove recovery without the full goal draft.
- Rejected expansion: no progress mirror, concurrency machinery, historical-goal
  migration, or new publication authority.

<!-- charness-goal-run:v1
{
  "binding_path": "charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.binding.json",
  "binding_schema": "charness.goal-binding/v1",
  "binding_sha256": "32ead8148ccfbfbbe0b9b6af1ad5ec1038a9c424c0766f45c1fbc9e54f54516d",
  "bootstrap_verification": "verified-target-roundtrip",
  "draft_path": "charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md",
  "draft_sha256": "ced8410bd896844bf6bb75bff807438cb6f40cb6a3c3b8489ddcd05a662212c2",
  "initial_graph_sha256": "3aeef936962f97fb2ddebc4d93cd37a79f6d684e0565ff3c8ccecd02253ab9b2",
  "current_membership_sha256": "c5895ca6cf9eaccf739cb444a3a51c24149b9314b1e0f89061eb34041b7e8d6b",
  "progress": {
    "completed": 13,
    "membership_sha256": "c5895ca6cf9eaccf739cb444a3a51c24149b9314b1e0f89061eb34041b7e8d6b",
    "next": {
      "key": "backlog-698",
      "number": 698,
      "repo": "corca-ai/charness",
      "state": "OPEN",
      "url": "https://github.com/corca-ai/charness/issues/698"
    },
    "open": 18,
    "revision": 1,
    "schema": "charness.goal-progress/v1",
    "total": 31
  },
  "parent_identity": {
    "number": 724,
    "repo": "corca-ai/charness",
    "url": "https://github.com/corca-ai/charness/issues/724"
  }
}
-->
## Situation

The active P0–P2 backlog-closeout goal coordinates 26 existing GitHub issues,
but its shared intent, completion contract, and progress currently live in a
local goal artifact. The `achieve` skill also stops at that local artifact: it
has no bounded structured interview contract, no authoritative GitHub parent,
and no real sub-issue lifecycle.

## Experience

A collaborator must recover the goal from repository-local Markdown and then
reconcile it with unrelated issue states. Existing work has no common parent,
and changing routine child status risks being restated into another progress
surface.

## Evidence

- `skills/public/achieve/SKILL.md` asks a small number of questions but defines
  neither a numeric ceiling nor option/tradeoff/recommendation records.
- `.agents/achieve-adapter.yaml` has no interview cap.
- `skills/public/issue/scripts/issue_tool.py` cannot update a tracker or manage
  GitHub sub-issue relationships.
- The active cohort is #723, #722, #721, #717, #715, #710, #708, #706, #704,
  #703, #701, #700, #699, #698, #697, #695, #694, #693, #692, #669, #668,
  #667, #637, #634, #628, and #546. The already-completed #721, #694, and #628
  remain part of the original goal scope.
- corca-ai/cortex#702 demonstrates a parent that owns shared principles and
  completion while real sub-issues own independently closable work.

## Impact

The current model makes local files a second tracker, weakens cross-session and
cross-collaborator recovery, and cannot use GitHub's own child-state progress as
the source of truth.

## Goal

Make this issue the authoritative tracker for the active goal and the first live
case of issue-native `achieve`: research first, draft the goal, ask at most an
adapter-controlled number of consequential questions (default 15), then create a
GitHub parent and manage independently closable work as real sub-issues.

## Interview decisions

1. **Canonical state**
   - GitHub parent + minimal local receipt: one current tracker while retaining
     host activation and compatibility identity. **Recommended and chosen.**
   - Full dual-write: better offline readability, but every update creates
     reconciliation and stale-mirror risk. Rejected.
   - Pure GitHub with no local receipt: cleanest authority, but strands host goal
     slots, recovery identity, and existing readers. Rejected.
2. **Unavailable GitHub capability**
   - Fail by default; permit provisional local fallback only by explicit adapter
     opt-in. Visible failure avoids silent split authority while supporting
     intentional offline/non-GitHub hosts. **Recommended and chosen.**
   - Automatic local continuation: higher availability, but silently creates two
     histories. Rejected.
   - Never permit fallback: simplest rule, but excludes intentional offline
     deployments. Rejected.
3. **Parent updates**
   - One agent updates the parent sparsely; routine progress comes from child
     state. This matches the real operating model and avoids duplicate logs.
     **Recommended and chosen.**
   - Managed sections plus optimistic concurrency: protects a concurrent-human
     edit pattern that is out of contract and adds unnecessary recovery logic.
     Rejected.
   - Comment on every transition: preserves a second log but duplicates GitHub
     history and adds noise. Rejected.
4. **Child creation timing**
   - After interview, create/reuse every known independent work item; add later
     discoveries only when concrete. Shows the real initial scope without
     speculative issues. **Recommended and chosen.**
   - Create every anticipated child: maximum apparent visibility, but noisy
     hypotheses. Rejected.
   - Create all children lazily: small activation, but hides already-known scope.
     Rejected.
5. **Migration and completion**
   - Link all 26 original issues, including the three already closed; add only
     genuinely new Phase 0 children. Close the parent only when every still-linked
     child is closed; move deferred work to a successor parent with a reason.
     Preserves history and makes parent completion equal 100% graph completion.
     **Recommended and chosen.**
   - Link only open work or mention completed work only in prose: cleaner queue,
     but rewrites original scope or leaves the graph incomplete. Rejected.
   - Close with optional children open or close deferred work as done: makes
     completion/progress disagree or hides live work. Rejected.

The interview ended after five questions; 15 was a ceiling, not a target.

## Current execution and dependencies

- Current executable lanes: #726 implements backend-routed tracker operations;
  #727 implements the bounded interview and minimal-receipt lifecycle. They may
  proceed in parallel where their source ownership is disjoint.
- #725 depends on #726 and #727 for the clean-consumer migration/readback and
  final removal of the full local goal tracker.
- The remaining original children resume after Phase 0 so their progress is
  managed under this graph.

## Settled operating contract

- Keep only a minimal local activation/compatibility receipt after verified
  parent creation; do not mirror progress locally.
- Fail activation when required GitHub capabilities are unavailable unless the
  adapter explicitly permits a provisional local fallback.
- One agent owns the parent progress cursor. Routine child transitions advance
  this body; child state and child-owned evidence remain the behavioral record.
- After interview, create or reuse every known independently closable child;
  add later discoveries only when concrete.
- Preserve all 26 existing issues in this graph, including work completed before
  parent creation. Add new Phase 0 children only where no issue already owns the
  outcome.
- Close this parent only when every still-linked child is closed. Move genuinely
  deferred open work to a successor parent with a recorded reason.

## Completion

- The issue-native interview and minimal-receipt lifecycle are implemented and
  verified in source and generated consumer layout.
- The selected issue backend can create/read/update parents and create/read real
  sub-issue relationships with duplicate and partial-failure handling.
- This parent has verified real relationships to all known children, and no
  Markdown checklist is treated as relation proof.
- Every still-linked child is closed, with issue-specific behavioral evidence or
  an explicit typed disposition.
- Final goal proof, fresh-eye review obligations, retro, and tracker readback are
  complete. Push, release, tag, and installed-host mutation remain separately
  authorized boundaries.

## Source preservation

Source origin: user-requested workflow change referencing corca-ai/cortex#702.

Source identity: https://github.com/corca-ai/cortex/issues/702, gathered through
authenticated GitHub CLI on 2026-08-26 and preserved locally at
`charness-artifacts/gather/2026-08-26-cortex-702-achieve-tracker-reference.md`.

Source text: achieve should research and draft first, ask at most an
adapter-configurable number of questions with options, tradeoffs, a recommendation
and its reason, then create a GitHub parent, manage work as sub-issues, and keep
the issue current instead of using a goal file; this goal is the first case.

Re-read obligation: re-read the source issue and this settled contract before
resolving or closing this tracker.

AI-provenance: drafted and filed by an AI agent from the operator-confirmed
five-question interview.

## Approved Goal Run Cutover

This parent is the authoritative execution tracker for the approved issue-native `achieve` Goal Run. The earlier issue-native bootstrap was provisional planning evidence; the final reviewed Goal Draft and immutable Goal Binding now govern this one-time reconciliation.

- Goal Binding: `charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.binding.json`
- Initial graph: five system Work Items plus the 26 existing backlog issue identities.
- Bootstrap status: `verified-target-roundtrip`; the target provider and clean `/goal #724` pickup re-read this graph, the frozen binding/draft identities, and selected `backlog-546` without mutation.
- Current progress cursor: revision `1`, `13` completed, `18` open, next `backlog-698` (`#698`). The cursor is the routine navigation record; pickup reads this parent block and does not rescan every child.
- Full graph reconciliation remains an explicit bootstrap/sync/closeout action. The one updater advances this cursor whenever a child transition is published.

The parent remains open until every still-linked child is closed with issue-owned behavioral evidence or a verified successor deferral. Push, release, tag, remote CI, installed-host mutation, and issue closure remain separately authorized boundaries for this run.

## 2026-08-27 Efficiency-first scope reset

The operator approved a redesign of this run because the original graph mixed
issue-native `achieve` dogfooding with an unrelated 26-issue backlog closeout.
The current goal now prioritizes the smallest consumer-speed path: explicit
provider selection, one parent-cursor pickup, external runtime isolation, one
representative child proof, and truthful issue/parent progress readback.

Live classification is recorded in
`charness-artifacts/goal-runs/724/goal-redesign-20260827.md`:

- 13 linked children are already CLOSED and remain historical evidence.
- #698, #708, #710, #722, #723, #726 have local implementation/proof; their
  next action is synchronization, not another implementation pass.
- #725 and #727 have establishment/readback evidence; #733 and #734 have
  existing repository code but still need issue-specific evidence sync.
- #699, #700, #701, #703, #704, #706, #715, and #717 have no current
  implementation receipt and are ordinary independent backlog work, not
  blockers for this dogfood path.

The original binding and initial graph stay immutable historical inputs. No
child is silently removed or declared complete by this addendum. Relationship
amendment, issue close, and parent close still require their own provider
operation, exact readback, and authorization boundary. Routine pickup continues
to consume the existing parent cursor; it does not rescan this classification.
The earlier all-linked-child completion sentence remains historical bootstrap
policy; it is not an instruction to implement the eight unstarted backlog rows
in this run. Any future parent close must first amend and read back that policy
through the provider boundary.

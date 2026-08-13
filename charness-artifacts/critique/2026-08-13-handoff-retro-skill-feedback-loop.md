# Handoff / Retro Skill Feedback-Loop Critique

Date: 2026-08-13

Fresh-eye satisfaction: parent-delegated — three pre-implementation reviewers
and one final customer readback returned findings to the parent.

## Target

- Capability brief: `charness-artifacts/create-skill/2026-08-13-handoff-retro-feedback-loop-brief.md`
- Customer surfaces: public `handoff` and `retro` skills, their planners, the
  Charness retro adapter, and current handoff/lesson memory.
- Review timing: before implementation.

## Angles

### Customer First Touch And Portability

The first reviewer found two risks:

- merely reading lesson evidence at retro time cannot prove that a selected
  list was presented before work;
- the existing target preflight recognizes literal regenerable facts, not every
  semantic proof receipt.

Disposition: accepted. The repair does not claim either inference. Charness's
ordered handoff now owns the next session's declaration/presentation
prerequisite. The public retro boundary treats presentation as a
contemporaneous agent-authored action and resolves uncertainty to no score. The
handoff target preflight is scoped to its deterministic classes and followed by
an agent-owned receipt/owner audit.

The review proposed a typed evaluator adapter object. Counterweight disposition:
deferred. One repo-local evaluator does not yet justify a second public adapter
schema; ordered `evidence_paths` plus an explicit repo-owned procedure are the
smaller portable seam. Generic discovery failure should be demonstrated in more
than one evaluator before hardening that schema.

### Failure Simulation And Verification

The second reviewer found:

- `not evaluated` had no durable owner;
- evidence paths did not distinguish files, directories, and missing optional
  sources;
- two pre-edit handoff checks and their order needed exact regression coverage;
- snapshot inspection could be mislabeled as presentation.

Disposition: accepted. `not evaluated` is an explicit retro line and never a
ledger mutation; the planner discloses evidence path kind/availability; tests
pin artifact → rules preflight → target preflight; and the lesson-evaluation
reference defines contemporaneous presentation and no-backfill behavior.

## Counterweight Pass

- Act before ship: define the negative disposition's owner, exercise realistic
  public-skill consumers, move both handoff preflights before editing, route
  adapter evidence, and preserve the snapshot/presentation distinction.
- Bundle anyway: classify semantic receipts through agent judgment after the
  deterministic target check.
- Defer: a typed lesson-evaluator adapter capability and additional lifecycle
  automation until generic evidence discovery is shown insufficient.
- Over-worry: no score-weight tuning, digest-ranking change, ledger schema
  change, new validator verdict, or Cautilus run without permission.

## Reviewer Tier Evidence

- Requested tier: inherited session reviewer tier
- Requested spawn fields: n/a — reused active bounded reviewer contexts
- Host exposure state: metadata-hidden
- Application state: host exposed no applied model or effort metadata
- Delivery state: findings-received

## Decision

Proceed with the smallest ship set above. The implementation must keep
Charness commands and ledger identity in `.agents/retro-adapter.yaml` and
`docs/development.md`, while the public skill owns only the generic judgment
boundary.

## Review Integrity

The parent fingerprint window `handoff-retro-skill-contract` verified clean:
HEAD, worktree, and index were unchanged by the three bounded read-only
reviewers. Findings were returned to the parent and dispositioned before code
edits.

After implementation, a bounded customer readback returned `PASS`: both
pre-edit handoff checks and the semantic owner audit are visible; retro exposes
ordered adapter evidence and preserves the presentation/no-backfill boundary;
repo-local commands remain outside the portable core; and the current handoff
contains no stale claim. The second fingerprint verified with only the parent's
declared update to the earlier handoff critique record; no reviewer-authored
worktree or index drift was present.

## Boundary Ownership

- Producer: handoff/retro planners expose pre-edit checks and adapter evidence;
  repo-local docs and adapters produce the concrete lesson procedure.
- Consumer: the next handoff author and retro operator.
- Owning surface: public skills own portable judgment boundaries; the Charness
  adapter and development guide own repo-local identity and commands.
- Verdict: owned-correctly

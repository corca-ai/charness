# Goal Run #724 — Efficiency-first scope reset

Status: operator-approved redesign, 2026-08-27 Asia/Seoul

## Why the original shape was wrong

The approved run combined two different jobs: proving the issue-native
`achieve` execution path and closing an existing 26-issue P0–P2 backlog. That
made unrelated release, diagnostic, installed-host, and proof-maintenance work
block the feature that was being dogfooded. It also left locally implemented
children OPEN while the run kept treating them as implementation work.

The run is therefore narrowed to the smallest path that reduces future
consumer rework: resolve one provider, recover one parent cursor, isolate the
runtime, execute one representative child, and publish truthful progress.

## Macro JTBD

Charness exists to accelerate correct, effective development. Any route, hook,
artifact, gate, or review that makes a capable operator rediscover state, wait
on redundant checks, or follow stale authority is a defect in this goal. The
handoff artifact/skill and Charness-provided SessionStart routing are therefore
in scope for removal: the active Goal Run parent cursor plus the progressive
documentation path (`AGENTS.md` → `docs/index.md` → owning page) is sufficient
resume context. The retro lesson ledger remains available for explicit retro or
contract-change work, but is not injected into every session.

## Fact split from the live 31-child graph

This is a dated classification, not a replacement for GitHub state.

- `CLOSED` (13): #546, #628, #634, #637, #667, #668, #669, #692, #693,
  #694, #695, #697, #721. These remain historical evidence and require no new
  implementation.
- `OPEN` with local implementation and focused proof (6): #698, #708, #710,
  #722, #723, #726. Their next action is issue-body/closeout synchronization,
  not another implementation pass.
- `OPEN` with establishment or contract readback already recorded (2): #725,
  #727. Their next action is the same synchronization boundary.
- `OPEN` whose repository code exists from the bootstrap work but whose
  issue-specific evidence is not synchronized (2): #733, #734. Verify the
  existing tests and record the narrow issue evidence; do not rebuild them.
- `OPEN` without a current implementation receipt (8): #699, #700, #701,
  #703, #704, #706, #715, #717. These are independent backlog work, not
  blockers for the issue-native dogfood path.

Live graph read on this date: 31 direct children, 13 CLOSED, 18 OPEN. The
parent cursor selected #698 without reading child issues. The old local #726
receipt saying `3 completed / 28 open` is stale; the live graph and current
parent read are authoritative.

## Revised completion contract

This goal completes the issue-native execution cutover when the following are
true:

1. provider selection is explicit and target-repository scoped;
2. `/goal #724` performs one parent read and selects the parent cursor without
   a routine full graph scan or duplicate capability probe;
3. Python, pytest, coverage, and temporary output are kept outside the
   implementation/proof worktree;
4. one representative child has focused behavioral proof and a truthful
   issue-owned progress update;
5. the parent cursor and the issue readback expose the same next action;
6. session resumption has no dependency on a handoff artifact or a Charness
   SessionStart hook.

Ordinary reversible implementation uses focused tests and the relevant
combined gate. A separate observer, boundary fingerprint, changed-line proof,
session baton, or micro-slice record is conditional on the actual authority,
durability, external-write, security, compatibility, release, or proof-surface
risk. `charness task` is an optional scope/result carrier; it does not create an
observer or a new gate.

## Generative sequence

1. Runtime isolation and provider identity (implemented).
2. Parent-cursor pickup and duplicate-probe removal (implemented).
3. Retire the Charness SessionStart hooks and the standalone handoff
   artifact/skill; keep the retro lesson ledger explicit and targeted
   (implemented in this slice).
4. Review-boundary simplification: typed read-only or isolated execution needs
   no parent fingerprint; only an untyped reviewer sharing the parent uses the
   fallback git-state check (implemented).
5. Synchronize the remaining implementation/establishment-ready issue records and
   run the representative #698 closeout only at the authorized external
   boundary.
6. Stop this goal. Leave #699, #700, #701, #703, #704, #706, #715, and #717 as
   ordinary independently owned backlog issues. Create a successor only when a
   future change has no existing issue owner; do not create an umbrella merely
   to make the parent percentage reach 100%.

## 2026-08-27 representative closeout progress

The cursor-selected representative #698 was closed after the local carrier
validator, resolution critique, provider close, final state verifier, and
separate issue readback all passed. Immediately after that closeout, the live
graph was 31 direct children, 14 CLOSED, and 17 OPEN; the parent cursor
advanced to #708. This is a dated progress observation, while the fact split
above remains the historical classification taken before the closeout.

## 2026-08-27 Cursor advancement after #708

A targeted readback found #708 `CLOSED`. The parent #724 body was then updated
once through the `gh` provider and its byte-identical readback passed. Current
navigation state is revision `3`: `15` completed, `16` open, next `#710`.
This does not claim that #710 or any other open child is complete.

## Explicit non-claims

This reset does not claim that the eight unstarted issues are fixed, that
#733/#734 are issue-closed, or that #724 is CLOSED. It does not claim push,
release, tag, remote CI, installed-host adoption, scheduler changes,
conditional trigger execution, consumer-repository enforcement, or
marketplace/export migration, or automatic cleanup of foreign consumer hooks.
The original binding and initial graph remain immutable historical inputs; any
provider relationship change requires its own readback and operation receipt.

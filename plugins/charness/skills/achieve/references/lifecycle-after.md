# Achieve Lifecycle — After

## After

## Closeout

An implementation slice is complete only when its owning child has behavioral
proof, exact evidence identity, and a truthful list of non-claims. A child
being closed is provider state, not proof by itself. The issue-owned closeout
must name the selected Work Item and shared `goal_lineage`.

Before closing a Goal Run parent, the guarded provider close:

1. reads the parent and every linked child again;
2. refuses any open child or missing child-owned evidence;
3. verifies every deferral on its exact successor parent;
4. checks the whole-system proof and documentation reconciliation;
5. records a terminal observation bound to the draft, binding, parent, and
   operation attempt;
6. invokes the provider close once; and
7. performs a distinct post-close readback.

Generic issue close is not a substitute for this operation. Comment/close
failure, unknown post-close state, and closed/readback failure remain distinct
unverified outcomes. Retry begins with a fresh read and never claims completion
from a missing readback.

Issue-resolution carrier publication and lifecycle-artifact publication are
separate surfaces. Later goal, retro, or handoff records do not require a
second docs-only issue-closeout push once the carrier has been verified.

The legacy delegated-closeout vocabulary remains explicit when that optional
mode is used: `impl-local`, `carrier`, `pushed-ci`, `instance-synced`, `live`,
and `issue-closed`. A provider-backed Goal Run is authoritative for the current
parent/child lifecycle and does not infer these states from local prose.

## Evidence

Every closeout artifact either embeds or references a validated
`goal_lineage` record. It must identify:

- the immutable Goal Draft path and SHA-256;
- the immutable Goal Binding path and SHA-256;
- the exact Goal Run repository, issue number, and URL; and
- the selected Work Item key and exact child identity when the evidence is
  child-scoped.

Planning-only and not-goal-bound evidence must carry an explicit disposition.
It is valid planning evidence but cannot satisfy implementation, child, or
parent completion proof.

## Final report

Separate self-verification, user/provider verification, residual risk, and
non-claims. Report local/fake checks separately from live provider readback.
Do not claim push, hosted CI, installed-host behavior, release, tag, or issue
closure unless its distinct boundary was actually exercised and read back.

The complete frozen Goal Draft remains unchanged at closeout. Routine progress,
child acceptance, and terminal provider state live in their owning evidence and
provider observations.

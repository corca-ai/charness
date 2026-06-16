---
name: hotl
description: "Use when applied live behavior needs human-on-the-loop closure: inventory what needs proof, write a proof packet before execution, run or record roundtrip/readback evidence through repo-owned commands, and keep every loop entry verified or explicitly dispositioned so unproven behavior is never closed as working."
---

# HOTL

Use this when behavior has already been applied to a live surface and the user
wants evidence-based closeout: roundtrip verification, provider readback, or an
explicit disposition for anything that cannot be proven now.

`hotl` is one public concept:

- the human supervises applied autonomous behavior; proof, not assertion,
  closes the loop
- a proof packet precedes any live execution
- every loop entry ends `verified` or explicitly dispositioned, never silently
  closed
- repo specifics (proof commands, surfaces, ledger schema and paths) are
  adapter-owned; this skill ships the discipline, statuses, and proof rules

Relationship to `hitl`: `hitl` inserts human judgment inside a bounded review
loop before changes land; `hotl` supervises and verifies behavior that is
already applied or live. Route bounded pre-apply review to `hitl`.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then
resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Default durable artifact: `<repo-root>/charness-artifacts/hotl/latest.md`
(current loop state); proof packets and closeout records live under the
adapter's `output_dir`.

Missing-adapter posture is `visible`: inventory, proof packets, and
dispositions may continue while the inferred defaults are named, but live proof
must never be improvised — a loop whose proof needs a repo-owned command the
adapter does not declare is recorded `blocked-needs-capability`, not executed
ad hoc. Scaffold the adapter when the repo should own its proof surface:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

## Workflow

1. Inventory the loop.
   - identify the user-facing behavior, its applied/live state, related
     issues, goals, commits, and prior proof artifacts
   - group regression siblings that share one acceptance surface
   - mark the surface class using the adapter's `surfaces` vocabulary (for
     example chat, scheduled workflow, table or sheet, public tools,
     control/action, local guard)
2. Write a proof packet before execution.
   - success criteria: the exact observable result that counts as verified
   - pre-roundtrip failure checks: config, credentials, listener
     reachability, command support, disposable target, artifact path, and
     known policy suppressions that can fail before live proof
   - feasibility: an adapter-declared command exists, a repo-owned command
     must be implemented, or the proof needs a manual or operator action
   - human intervention: the exact action, timing, disposable target,
     screenshot or UI judgment, or approval needed
   - non-claims: what this proof will not establish
3. Implement missing proof methods when needed.
   - prefer extending adapter-declared repo-owned commands over ad hoc manual
     steps; resolve instances and targets from repo config, not env-only state
   - live or mutating commands require a boundary reason where the command
     surface supports one
   - add deterministic tests for target resolution, missing-config failure,
     and proof-result classification
4. Execute or record the proof.
   - run readiness checks before spending live roundtrip budget
   - for external mutations, capture before/after provider readback and
     cleanup or restoration evidence
   - for human actions, provide an exact action packet, then read back the
     provider or runtime evidence
5. Update the ledger and close out per `references/ledger-and-dispositions.md`.
   - record exactly one status per entry: `verified`,
     `blocked-needs-operator`, `blocked-needs-capability`,
     `deferred-by-operator`, `issue`, `accepted-risk`, or `out-of-scope`
   - `verified` carries `verified_at` and `verified_against` (source commit,
     proof artifact, proving-surface refs); a stale proving-surface ref
     demands re-proof, narrower refs, or an explicit disposition
   - final non-verified statuses carry disposition owner, reason, decided-at,
     and revisit trigger
   - queue deferrable operator-only decisions in the active goal's
     `## Operator Decision Queue`; stop only when they block all safe next work
   - completion audits block while a linked entry is neither verified nor
     explicitly dispositioned

## Proof Rules

Apply `references/proof-rules.md`; the load-bearing rules:

- a normalized text match is not exact rendering proof
- a direct post is not scheduled-workflow proof
- bot-authored smoke is not human-ingress proof
- external mutation proof needs before/after provider readback
- if a proof depends on one provider identity being heard by another
  listener, prove or fix that sender/listener relationship first
- local deterministic tests prove guards and command behavior; they do not
  prove live provider behavior unless the acceptance class is local-only

## Output Shape

The result should usually include Loop Inventory, Surface Class, Proof Packet
(Success Criteria, Pre-Roundtrip Failure Checks, Feasibility, Human
Intervention, Non-Claims), Executed Proof or Recorded Disposition, Ledger
Status, Verified-Against or Disposition fields, Staleness Findings, and Next
Action.

## Guardrails

- Do not close an issue, goal, or feature as verified while proof is missing;
  record an explicit disposition instead.
- Do not spend live roundtrip budget before the proof packet and readiness
  checks exist.
- Do not improvise provider execution around the adapter's declared command
  surface; a missing capability becomes `blocked-needs-capability` or a new
  repo-owned command, never an undeclared manual ritual.
- Do not grant a normalized match, direct post, bot smoke, or local test more
  proof weight than the proof rules allow.
- Do not rely on a `verified` entry whose proving-surface refs are stale;
  re-prove, narrow the refs, or disposition it explicitly.
- Do not copy repo or host facts (commands, channels, schema paths) into this
  skill's text; they belong in the adapter.
- Do not run this loop for bounded pre-apply review; that is `hitl`.

## References

- `references/adapter-contract.md`
- `references/ledger-and-dispositions.md`
- `references/proof-rules.md`
- `../../shared/references/external-capability-proof-ladder.md`
- `scripts/resolve_adapter.py`
- `scripts/init_adapter.py`

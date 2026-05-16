# Agent Runtime Evidence Fourth Critique

## Execution

- Fresh-Eye Satisfaction: `parent-delegated`
- Target: `code-critique`
- Change under review: `0efa557 Require runtime evidence for agent docs triggers`
- Packet Consumed:
  `charness-artifacts/critique/2026-05-17-agent-runtime-evidence-fourth-critique-packet.md`

## Change

The prior commit required product docs and runbooks to be paired with runtime
evidence before triggering the production LLM/agent runtime quality lens. This
critique checked whether that correction overfit earlier findings, whether the
tests became too brittle, and whether durable critique artifacts remained
accurate.

## Angles

- Problem framing: ensure the lens is neither docs-driven nor too hard to apply
  to real runtime seams.
- Structure: make the trigger boundary readable and testable without one broad
  phrase-assertion cluster.
- Operational checklist: check artifact durability, packet targeting, export
  sync, and validation coverage.
- Counterweight: separate this corrective slice from broader validator hardening.

## Findings

### Act In This Slice

- The third critique artifact still ended with a pre-closeout next move even
  though commit `0efa557` had already closed the slice.

Resolution: replaced that stale next move with a closeout status naming
`0efa557`.

- The fourth critique packet was a valid review input but not yet durable.

Resolution: keep the fourth packet and this result artifact together under
`charness-artifacts/critique/`.

### Bundle In This Slice

- The trigger wording was slightly overfit for operator runbooks. Product docs
  should require paired runtime evidence, but an operator runbook that describes
  an actual incident or runtime procedure can itself be runtime evidence.

Resolution: split product-doc and operator-runbook wording. Conceptual
runbooks or docs that merely name a provider, serving path, or procedure still
do not trigger the lens without corroborating runtime evidence.

- The dispatch summary duplicated the canonical trigger boundary without saying
  it was a mirror.

Resolution: added an explicit mirror note in `inventory-dispatch.md`.

- The quality docs test had become a broad phrase cluster.

Resolution: split it into focused tests for core anchoring, positive runtime
triggers, docs/runtime evidence boundary, proof-mode vocabulary, and dispatch
mirror behavior.

### Separate Validator-Hardening Slice

- `scripts/validate_critique_artifacts.py` still points at the historical
  `charness-artifacts/premortem/` path even though `.agents/surfaces.json`
  maps `charness-artifacts/critique/**` to that validator.
- Packet JSON shape validation exists in `scripts/validate_critique_packet.py`
  but is not wired into the critique-artifact surface.

Decision: defer these as a separate validator-hardening slice because changing
artifact validation path semantics affects historical premortem artifacts,
checked-in critique packets, and closeout gates beyond this runtime-lens
correction.

### Over-Worry

- Export sync was not actionable. Source and plugin copies are synchronized by
  `sync_root_plugin_manifests.py` and packaging validation owns that surface.

### Valid But Defer

- A retention/index policy for repeated critique packets would reduce workflow
  noise, but it should follow validator hardening.

## Proof

- `pytest -q tests/quality_gates/test_quality_skill_docs.py`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`

## Next Move

Run full slice closeout, commit this fourth-critique corrective slice, then
take the critique-artifact validator bug as the next separate hardening slice.

# Closeout Bundle Execution Contract

Date: 2026-08-06
Source: [closeout-bundle goal](../goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md)

## Problem

The repository already has separate owners for frozen manifests, surface
selection, generated-plugin parity, authoring preflight, critique packets,
current pointers, and verification-locked closeout. The operator still has to
reconstruct their order manually, so the pre-review authoring check and the
identity that a reviewer reads can drift from the later closeout proof.

## Capability Contract

Given a valid frozen slice manifest and explicit critique/behavior inputs, an
operator can run one repo-owned command in dry-run mode to inspect the complete
bundle plan, then rerun it with `--execute` to perform the bounded local steps
in order and persist one bundle receipt. The command refuses before mutation
when the manifest, surface ownership, generated mirror, or critique binding is
invalid. It never treats a mutable `HEAD` or a terminal local green as release
proof.

## Current Slice

Implement the local bundle orchestrator around the existing final-bundle
preflight. It will validate and sync selected surfaces, run authoring
preflight before creating the fresh-eye packet, capture a worktree identity
bound to the packet, run the verification lock, and persist structured phase
receipts. Pointer refresh and release publication remain explicit owner steps;
the orchestrator may verify pointer freshness but does not invent a second
pointer writer or publish externally.

## Fixed Decisions

- The existing `final_bundle_preflight.py` remains the dry-run planner and owns
  cross-owner refusal; the new command consumes its structured plan.
- `--execute` is the only mutation switch. No command supplied through
  `--behavior-channel` is executed automatically; behavior remains an explicit
  operator/fresh-eye proof channel.
- Only repo-owned planned commands with argv-safe syntax are executable. Shell
  operators, absolute paths, and commands outside the selected repo are
  refused rather than interpreted through a shell.
- The packet identity is captured after sync and authoring preflight, includes
  the immutable `HEAD` SHA plus reviewed file bytes and worktree state, and is
  rechecked immediately before verification-lock execution.
- A bundle receipt is written only after successful `--execute` phases and is
  itself bound to the captured identity; dry-run emits no repository state.
- Current-pointer freshness is a validator-owned check. Pointer writes and
  release/push remain separate final-boundary operations.
- Generated `charness-artifacts/**/*-packet.md` renders are packet outputs, not
  hand-authored documents; the bundle leaves their shape to the artifact owner
  while still running artifact-surface preflight over changed artifact paths.
- Retro-to-handoff wiring is an explicit closeout check, not a mid-session
  handoff rewrite. `validate_retro_handoff_wiring.py` requires explicit goal and
  retro paths, normalizes markdown-link citations relative to the handoff file,
  and checks only exact `recurrence-class: <slug>` marker coverage in
  `## Next Session`.

## Probe Questions

- Can the existing surface command vocabulary be executed safely without a
  shell, or must a surface be recorded as plan-only? The first implementation
  must answer this with refusal tests for shell operators and absolute paths.
- Does the existing critique packet generator produce a current binding after
  sync and authoring checks? The integration test must verify the packet's
  identity becomes stale after a reviewed-file edit.

## Deferred Decisions

- Automatic current-pointer record selection and writing; continue using the
  existing pointer owner until a closeout record shape is fixed.
- Natural-language retro disposition quality; the wiring validator proves path
  and marker presence only, while the bounded disposition reviewer judges
  whether each improvement was actually applied or filed.
- Push, remote CI observation, release publication, and release readback; these
  are the final separately gated phase after the local bundle lock.
- Provider, installed-consumer, cross-host, live-agent, and Cautilus proof.

## Non-Goals

- Do not replace `run_slice_closeout.py`, the surface manifest, the packaging
  exporter, or the critique binding validator.
- Do not execute arbitrary behavior commands, provider calls, or release tools.
- Do not make this a standing gate for ordinary reversible work.

## Constraints

- Source and checked-in plugin script copies must remain byte-identical.
- Dry-run and execute output use one structured schema and preserve explicit
  non-claims.
- The receipt and packet are checked-in durable evidence under
  `charness-artifacts/`; ignored `.charness/` output is reproduction detail.

## Success Criteria

- Dry-run reports the full ordered plan and writes nothing.
- Invalid baseline, unmatched path, stale mirror, unbound critique, unsafe
  command, or stale identity returns a structured refusal before mutation.
- Execute performs sync, authoring preflight, packet generation, identity
  freeze/recheck, and verification lock in that order, then writes one receipt.
- The receipt names the immutable target, packet path/SHA, identity SHA, phase
  results, verification-lock result, and non-claims.
- A fresh identity check refuses after a reviewed input changes, even if
  mutable `HEAD` is unchanged.
- A retro-to-handoff wiring check refuses a wrong goal binding, an absent
  goal-bound retro citation, or a missing exact recurrence marker, and passes a
  retro that has no recurrence markers while making that zero-obligation state
  explicit.

## Acceptance Checks

- `python3 -m pytest -q tests/quality_gates/test_closeout_bundle.py` (unit/integration: dry-run, refusal matrix, ordering, identity drift, and receipt shape)
- `python3 scripts/closeout_bundle.py --help` (manual: discoverable no-side-effect command surface)
- `cmp -s scripts/closeout_bundle.py plugins/charness/scripts/closeout_bundle.py` (integration: generated mirror parity)
- `python3 scripts/check_doc_authoring_preflight.py --repo-root . --path charness-artifacts/spec/2026-08-06-closeout-bundle-execution-contract.md --json` (integration: authoring preflight before review packet)
- `python3 scripts/validate_current_pointer_freshness.py --repo-root .` (integration: pointer owner remains authoritative)
- `python3 scripts/validate_retro_handoff_wiring.py --repo-root . --goal-path <goal> --retro-path <retro> --handoff-path docs/handoff.md` (integration: deterministic retro-to-handoff binding only)

## Operator Workflow

1. Run the command with the required manifest, bundle id, critique path, and
   behavior channel arguments but without `--execute`; inspect the complete
   ordered plan and its explicit non-claims.
2. Confirm that the manifest and critique path are the intended frozen inputs.
3. Rerun the same command with `--execute`. `ready` means plan readiness;
   `completed` means only that the local sync, authoring, packet, identity, and
   verification-lock phases completed. It does not claim fresh-eye approval,
   provider, installed-consumer, remote CI, release, or push proof.

Example:

```text
python3 scripts/closeout_bundle.py --manifest <slice-manifest.json> \
  --bundle-id <bundle-id> --critique-path <critique.md> \
  --behavior-channel 'behavior=<operator proof command>'
```

## Boundary Ownership

- `final_bundle_preflight.py` owns baseline/surface/critique refusal and plan
  expansion.
- `check_doc_authoring_preflight.py` owns authoring readiness.
- `prepare_packet.py` and `reviewed_input_identity.py` own packet and input
  binding.
- `run_slice_closeout.py` owns verification-lock execution.
- The new orchestrator owns only ordering, phase receipts, and the explicit
  bundle evidence record.

## Critique

- Fresh-eye review is required before the first executable slice; because this
  command renders verdicts about other artifacts, a repair round is required
  when its refusal/identity logic changes.
- The generated packet is an immutable-input record for the verification lock,
  not a fresh-eye verdict. Consuming that packet through a separate delegated
  critique and claims-review boundary remains a later closeout slice; this
  command does not silently promote packet generation to reviewer approval.
- The issue-510 external-seam interrupt is explicitly carried forward in the
  named issue-510 spec; this contract does not touch that seam.

## Canonical Artifact

- [Closeout Bundle Execution Contract](./2026-08-06-closeout-bundle-execution-contract.md)

## First Implementation Slice

Add the source/plugin orchestrator and focused tests for the dry-run and
refusal/identity boundaries; keep execute phase behavior behind explicit
argv-safe owner calls and persist the receipt only after the verification lock.

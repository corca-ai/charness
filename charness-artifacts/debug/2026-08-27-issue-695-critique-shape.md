# Debug Review
Date: 2026-08-27

## Problem

Issue #695 reports that critique producers omit `Execution mode`, while the
issue closeout observer requires it for typed-subagent evidence.

## Correct Behavior

The critique shape has one owner for reviewer-tier field names and execution
mode values. The scaffold and prepare packet emit a valid execution mode, and
the typed-subagent closeout consumer refuses any incomplete or non-typed
record instead of accepting prose as a substitute.

## Observed Facts

- `issue_resolution_observer.py` already required six typed tier fields,
  including `execution mode`, and rejected its absence.
- `scaffold_critique_artifact.py` emitted the tier block without that field.
- `critique_packet_lib.py` carried `reviewer_runner.mode` in JSON but did not
  render a canonical `Execution mode` field in its Markdown evidence block.
- The source and plugin trees each repeated portions of this shape.

## Reproduction

The executable probe generated the pre-change scaffold and supplied a typed
tier block without `Execution mode`. The scaffold output contained no such
field, and the closeout observer returned `typed-subagent reviewer evidence is
missing fields: ['execution mode']`.

## Candidate Causes

- The closeout consumer gained the field in a later repair than the critique
  producers, leaving an unowned interface seam.
- Packet JSON and Markdown used different names and did not share a field
  renderer.
- Source/plugin mirrors allowed the shape to be copied without a single
  executable owner.

## Hypothesis

The failure is a producer/consumer shape split, not a typed-carrier failure:
centralizing the field names and valid modes, then deriving scaffold and packet
output from that owner, will make the producer outputs satisfy the consumer
without weakening the refusal. disconfirmer: run the focused scaffold/packet
round trips and typed closeout missing/malformed-mode controls.

## Verification

Confirmed by the pre-change reproduction. The scaffold omitted the field and
the closeout observer refused it; the worker carrier itself already carried an
execution mode, so the missing link is the critique artifact shape.

Post-change, the combined focused standing gate passed 134 tests, and the
issue-mandated `tests/quality_gates/test_describe_goal_closeout_shape.py` target
passed 19 tests. Ruff, `py_compile`, the explicit Python length gate, and
source/plugin parity passed. The length gate reports the validator's warn band
at 479 code lines but no hard failure. Python cache output was kept under an
external `PYTHONPYCACHEPREFIX`, and the implementation worktree has no
`__pycache__` directories. The closeout-bundle readiness test was kept out of
this slice gate because its repo-wide fixture reports an unrelated unbound
packet and treats the new debug receipt as unmatched while the worktree is
dirty.

The first clean-target changed-line run then exposed a standalone import
regression: the issue observer could not load the canonical shape because its
`runtime_bootstrap` dependency was not on `sys.path`. The same three preflight
tests passed on base, isolating this to the new loader. The loader now adds the
repository root before importing the canonical module; the preflight and
changed-line runs must be repeated after this repair.

## Root Cause

`Execution mode` was added as a closeout-consumer requirement in the issue
resolution observer, but the critique shape producers retained an older,
duplicated four-field tier block. No shared owner forced the scaffold, packet
renderer, and closeout consumer to agree.
The standalone consumer loader also lacked the repository-root import path
needed by the canonical module, so a direct closeout-shape invocation failed
before it could render the contract.

## Invariant Proof

- Invariant: a typed-subagent closeout's reviewer-tier record names the same
  execution mode vocabulary that critique producers emit.
- Producer Proof: the scaffold and packet renderer derive the field and its
  valid modes from `scripts/critique_reviewer_evidence.py`.
- Final-Consumer Proof: `issue_resolution_observer._typed_delegation_error`
  remains fail-closed for missing, placeholder, wrong-mode, invalid-host, and
  invalid-delivery evidence.
- Standalone-Consumer Proof: the issue observer prepares the repository-root
  import path before loading the canonical shape, preserving direct script
  execution as well as in-process imports.
- Interface-Shape Sibling Scan: source/plugin critique and issue copies are
  compared after export; packet JSON and Markdown carry the same mode.
- Non-Claims: this proves local shape and typed-carrier refusal, not a live
  host process identity or installed consumer adoption.

## Detection Gap

The existing closeout tests covered the typed observer's refusal, but no test
asked the scaffold or packet producer to emit the required field. The smallest
detector is a shared-constant parity assertion plus scaffold and Markdown/JSON
producer assertions and missing/wrong-mode closeout controls.

## Sibling Search

- Mental model: a closeout field is an interface owned by the final consumer
  and every producer, not prose copied into one template.
- same-layer: `scripts/critique_packet_lib.py` | decision: repair now by
  rendering the canonical mode | proof: packet producer test.
- abstraction-up: `scripts/critique_reviewer_evidence.py` | decision: make the
  common field and value vocabulary executable there | proof: producer imports
  and source/plugin parity.
- cross-file: `skills/public/issue/scripts/issue_resolution_observer.py`;
  it is the existing final consumer whose refusal remains intact.

## Seam Risk

- Interrupt ID: issue-695-critique-shape-2026-08-27
- Risk Class: contract-freeze-risk
- Seam: critique producer shape -> typed-subagent closeout observer
- Disproving Observation: a produced scaffold or packet lacks a valid mode, or
  a malformed typed closeout passes the observer.
- What Local Reasoning Cannot Prove: host-attested process distinctness,
  installed-plugin behavior, or external consumer adoption.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Critique Boundary: explicit operator direction omits forced fresh-eye review;
  this host exposes no Agent/subagent capability.
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep reviewer-tier field names and execution-mode values in one executable
shape owner. Producers import it; closeout consumers use the same field list;
tests assert both positive emission and typed refusal. Do not solve this by
mass-editing historical critique artifacts; preserve legacy records and make
new output complete.

## Evidence Disposition

- Report Identity: goal-run:724#sha256:e44cf96713396d4cdca2f6d820b39eb7ddb6b7af37fa64e54377f0c5771c0219
- Reported Findings: 1
- Dispositioned Findings: DBG-695-F1
- Missing Findings: none
- Evidence Digest: sha256:2023fc9c5ffc865c9c305fb82779b3d0912fddfae88b1a0cd80b0e35dc78f64d
- Report Source: charness-artifacts/goal-runs/724/bodies/backlog-695.md
- Report Source SHA256: e44cf96713396d4cdca2f6d820b39eb7ddb6b7af37fa64e54377f0c5771c0219

## Adversarial Verification

- Finding: DBG-695-F1 | source: charness-artifacts/goal-runs/724/bodies/backlog-695.md | expected: critique producers emit Execution mode and an incomplete typed-subagent closeout is refused | stimulus: generate the critique scaffold, then pass a typed-subagent tier block without Execution mode to the closeout observer | disposition: reproduced | observed: the scaffold and packet shape omitted Execution mode while the closeout observer returned the missing field refusal | proof: executable fixture | handoff: charness-artifacts/impl/2026-08-27-issue-695-critique-shape.md | next move: make the shared critique shape owner emit and expose the field in every producer | receipt: charness-artifacts/debug/receipts/issue-695-execution-mode-missing.json | receipt sha256: efb5918ef4fffcba4e309dafbced15d8edf361ebf30ac9e66142367baf790a19

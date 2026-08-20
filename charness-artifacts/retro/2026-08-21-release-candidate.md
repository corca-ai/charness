# Release Candidate Session Retro

Date: 2026-08-21
Goal: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md

## Context

This work unit prepared the semantic candidate for the planned 6.3.0 release
and began the distinct release-candidate boundary. The next move is a release
critique bound to 6.3.0, followed by version mutation only after that boundary
is proven.

## Window

The window covers the semantic-candidate lock, release planner/probe checks,
the rejected dry-run with a semantic-only critique, and the opening and
reconciliation of lesson session `2026-08-21-release-candidate`.

## Evidence Summary

- Semantic candidate endpoint `0784bb041` has the v9 fresh-eye PASS, focused
  receipt, broad quality proof, and verification-lock receipt.
- Release planner selected current `6.2.0` -> target `6.3.0`; current version
  surfaces have no drift and fresh-checkout probes passed 5/5.
- The dry-run refused because
  `semantic-candidate-release-critique.md` did not bind to `6.3.0`; this is a
  target-selection failure, not evidence that release critique passed.
- The lesson gate reported `unclaimed-emission` for the newly opened session.
  The retro planner routed the same frozen bundle and the shared helper proves
  this is the intended lifecycle boundary, not a reason to weaken the gate.
- Sparse score events were recorded for the two lessons that changed concrete
  actions; all other selected lessons remain unscored.

## Waste

- Two helper calls used flattened root paths instead of the skill-resolved
  `$SKILL_DIR/scripts/...` path: `prepare_critique_packet.py` and
  `scripts/scaffold_debug_artifact.py`. Both failed immediately. The structural
  smell is a missing path-existence preflight before copyable skill commands.
- The first release dry-run supplied a semantic candidate critique to a release
  gate. Its refusal correctly exposed that a valid artifact for one boundary is
  not a valid artifact for another. The pattern is target identity being left
  to filename/context rather than bound by the caller.
- Read-only audits ran in parallel; append-only lesson ledger writes ran
  serially. This kept useful fan-out while preserving the shared-writer rule.

## Critical Decisions

- Keep the continuity failure red until this session has a retro disposition;
  do not invent an in-progress exemption or delete the append-only receipt.
- Treat the release critique as a separate irreversible boundary with its own
  target token, packet, reviewer findings, and counterweight pass.
- Record only anchored observed lesson effects, rather than scoring the whole
  emitted list ceremonially.

## Trends vs Last Retro

The prior retro correctly identified the recurring unclaimed-session boundary
under #639. This run reproduced the same class, and the gate/router agreement
held; the remaining improvement is earlier operator visibility and a reliable
end-of-work retro handoff, not a weaker gate.

## North Star Alignment

The north star requires a capable judge and a different observer at irreversible
boundaries. The release planner and dry-run were useful observers because they
refused a critique bound to the wrong target. The continuity gate likewise
preserved its teeth and the retro planner supplied the distinct consumer that
explains how to clear the state. Version mutation, tag, publication, host
readback, and issue closeout remain unproven and are not claimed here.

## Expert Counterfactuals

- Engelbart's system-improving lens would treat skill path resolution, packet
  identity, reviewer delegation, and release gating as one H+LAM+T system. A
  canonical command resolver plus an existence check would have prevented both
  wrong-path helper calls before execution.
- A direct boundary question — “what exact target does this artifact prove, and
  which consumer will reject a mismatch?” — would have selected a release-bound
  critique before the first dry-run.

## Sibling Search

- same layer: `skills/public/critique/SKILL.md` and
  `skills/public/debug/SKILL.md` both require `$SKILL_DIR` resolution before
  helper calls | decision: same class, diagnostic-only for this slice | proof:
  static scan plus two reproduced wrong-root failures; the next release-bound
  work will use resolver-emitted paths.
- abstraction up: release planner, critique packet, and retro planner all bind
  an input identity before consuming it | decision: same class, diagnostic-only
  for this slice | proof: release dry-run and retro packet show distinct target
  contracts; no source code mutation is justified by this operator-side miss.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":2,"session_id":"2026-08-21-release-candidate","status":"effect-recorded"}

The harmful question was considered first. Two selected lessons changed concrete
actions and carry anchors with counterfactuals; the remaining selected lessons
have no honest encounter evidence in this window and remain unscored.

## Next Improvements

- workflow: resolve the skill root and verify every helper path exists before
  running a copyable command; bind every release artifact to the release target
  before dry-run. recurrence-class: wrong-path-and-target-binding remains a
  diagnostic class for this workflow.
- capability: keep the release planner, critique packet, and publish gate on one
  structured target-identity contract; do not infer release scope from a
  semantic-candidate filename.
- memory: preserve #639 as the owner of the recurring session lifecycle gap;
  this retro demonstrates the gate/router contract and is not an issue-close
  claim. recurs: unclaimed-session-disposition.

## Packet Consumed

`charness-artifacts/retro/2026-08-21-release-candidate-retro-packet.md`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-21-release-candidate.md

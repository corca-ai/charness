# Issue 713 Implementation Critique

Date: 2026-08-24

## Decision Under Review

Ship the #713 repair that binds `impl` bootstrap to planned slice paths while
making final risk authorization depend on Git-observed paths before and after
closeout mutations. Preserve `--paths` for focused planning, keep the existing
planner, and export the same behavior in the plugin.

## Failure Angles

- Scope provenance: a caller-selected `--paths` value could hide actual
  interrupt-affine changes from final authorization.
- State interpretation: malformed, incomplete, blocked, or non-impl planner
  tuples could proceed or raise rather than fail closed.
- Timing: sync/verify/coverage commands could create generated or artifact paths
  after the only risk snapshot.
- Ownership and drift: planner interpretation could become a second classifier,
  or source/plugin copies could disagree.
- Proof shape: a private-function test or an earlier unrelated gate could make
  the CLI regression look protective without reaching the risk decision.

## Counterweight Pass

- Retaining `--paths` is valid because it still scopes surface planning; removing
  it would be an unnecessary API break once authorization uses separate Git facts.
- `slice_closeout_risk_interrupt.py` is not a second planner. It interprets the
  existing planner's typed result and owns no discovery or overlap semantics.
- The remaining 479-line closeout orchestrator warning is a genuine accretion
  smell, but this slice moved the new verdict vocabulary out. A broader
  orchestrator decomposition is not required to close #713.
- The second review round found the post-sync timing bypass. The repository's
  two-round cap forbids presenting the resulting repair as independently
  approved; focused proof supports the candidate but does not replace review.
- Post-commit changed-line proof then exposed a second observation-contract
  conflation: `changed_paths is None` means global discovery, while an explicit
  empty list means the authoritative Git observer found no slice paths. Treating
  both as falsey reintroduced a global unrelated interrupt. The planner now
  distinguishes those states directly, rather than teaching the caller to
  retry or fabricate a path.
- Broad pytest exposed the same class at the next boundary: Git observation can
  be unavailable in a valid minimal consumer/fixture, which is different from
  observing no paths. Closeout now records `observed` versus `unavailable`; an
  unavailable observation invokes pathless/global interrupt planning, so no
  current interrupt proceeds while a current interrupt fails closed.
- Fresh-eye pass: scripts/slice_closeout_risk_interrupt.py — round 2 found no
  duplicate-planner or tuple-interpreter blocker; its timing finding belonged
  to the caller, whose repair is accepted unreviewed under the round cap.
- Fresh-eye pass: scripts/risk_interrupt_lib.py — the post-commit `None` versus
  explicit-empty repair changes planner verdict logic after round 2 and is
  accepted unreviewed under the two-round cap; focused None/empty regression,
  source/plugin parity, and changed-line proof are required before closeout.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run_slice_closeout.py:_maybe_block_on_risk_interrupt | action: fix | note: separate caller-selected planning paths from Git-derived risk authorization paths.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run_slice_closeout.py:final_risk_interrupt_paths | action: fix | note: union committed campaign paths with the final live Git set and re-run the same fail-closed decision after closeout commands.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_run_slice_closeout_review_obligations.py | action: fix | note: exercise both source and plugin CLIs for omitted actual paths and sync-created interrupt paths.
- F4 | bin: over-worry | evidence: strong | ref: scripts/slice_closeout_risk_interrupt.py | action: document | note: the extracted policy is an output interpreter, not a duplicate planner.
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/run_slice_closeout.py | action: defer | note: the orchestrator remains in the length warning band, but #713 no longer adds its verdict vocabulary there.
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/risk_interrupt_lib.py:plan_risk_interrupt | action: fix | note: preserve the semantic distinction between omitted/global discovery (`None`) and an explicit Git-observed empty scope (`[]`).
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/slice_closeout_risk_interrupt.py:observe_initial_paths | action: fix | note: represent Git observation as typed `observed`/`unavailable` state; unavailable must use global fail-closed planning rather than crash or caller-selected scope.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: unsupported
- Application state: n/a — the canonical file-backed runner selected backend and timeout but exposed no tier-field application signal.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

accepted-unreviewed-under-round-cap — round 1 found the caller-path bypass;
round 2 read the repaired surface and found the post-sync timing bypass. The
round-2 repair and the later None/empty/unavailable observation-contract repairs
are covered by focused tests and parity checks but deliberately receive no
third-round approval.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.json
- Packet path: charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.json
- Packet SHA256: 99a66ccec2bedfa5229fd6cd0cc8831f0df3e4fa948804fdfde6873d073283ea
- Identity SHA256: 1d24f9bf0c12742e1bfb9406a9e7477312de3f632d8b1db1a7b6b18710f1b3ac

## Boundary Ownership

- Producer: Git-derived committed-range and live-worktree path collectors.
- Consumer: closeout risk authorization immediately before a successful receipt.
- Owning surface: `run_slice_closeout.py` orchestration plus the cohesive `slice_closeout_risk_interrupt.py` tuple interpreter.
- Verdict: moved-to-owner — planning remains caller-scoped, while authorization and final re-observation live at the closeout owner.

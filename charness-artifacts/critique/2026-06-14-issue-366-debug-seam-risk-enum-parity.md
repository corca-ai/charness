# Critique Review: #366 debug Seam Risk enum parity

Date: 2026-06-14

Resolution critique (bounded fresh-eye, high-leverage tier, separate agent
context — subagent `ad37e12145c34f64b`) of the fix for corca-ai/charness#366.
Recurrence framing: "what would let this class of issue, and the siblings
surfaced in the causal review, come back?"

## Decision Under Review

Fix for #366 (`bug`): `scripts/validate_debug_artifact.py` (+ plugin mirror)
imports the Seam Risk enums from `risk_interrupt_lib` (deleting the hand copy)
and adds `validate_dated_seam_risk_enums`, wired into the dated-artifact (`else`)
branch, so off-taxonomy `Risk Class` / `Generalization Pressure` fail at author
time — matching the `run_slice_closeout.py` consumer. Tests in
`tests/test_debug_artifact.py` cover dated off-taxonomy rejection, dated
in-taxonomy acceptance, and a single-source-of-truth guard.

Prior causal-review context (not redone): missing single-source-of-truth
invariant — hand-copied enums + the author-time enum check gated to `latest.md`;
the dated `else` branch (fed into `latest.md` by the current-pointer) omitted it.

## Failure Angles

- Recurrence of the producer-weaker-than-consumer enum gap: a third copy, a new
  author-time validator, or the forced-interrupt-completeness gap left out of
  scope.
- Over-reach of the fix: requiring both Seam Risk lines when the section is
  present could break a legitimate dated shape; the import could cycle; the SST
  guard might not actually pin reuse.
- Sibling disposition: deferred siblings that should have been bundled.

## Counterweight Pass

- Required-both-lines: refuted — every dated record carrying `## Seam Risk`
  already has both bullets; sectionless legacy records short-circuit. No
  retro-regression (whole corpus scanned).
- Import cycle: `risk_interrupt_lib` imports only `artifact_validator`; acyclic.
- SST guard: the `is`-identity assertion pins object identity, so any re-copy of
  the frozensets breaks the test.
- Deferred siblings are genuinely out of this slice's JTBD boundary.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: git working tree | action: fix | note: ship #366 and #361 as separate commits, staging selectively so #361's test-only changes do not ride the #366 carrier (resolved)
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/risk_interrupt_lib.py:217 | action: defer | note: spec-handoff Chosen Next Step/Impl Status have no author-time validate_spec_* gate (only parse_spec_interrupt_resolution); same producer-weaker-than-consumer class, recorded in close comment
- F3 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_issue_closeout_commit_msg.py:93 | action: defer | note: commit-msg ledger under-constraint vs verify-closeout; recurrence of the 2026-06-01 release-issue-closeout-miss lesson, recorded in close comment
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_debug_artifact.py:234 | action: defer | note: forced-interrupt completeness still diverges dated-vs-latest; this slice fixed the enum subset only, recorded in close comment so "fixed" does not imply full parity
- F5 | bin: over-worry | evidence: strong | ref: tests/test_debug_artifact.py | action: document | note: required-both-lines / import-cycle / SST-guard concerns all refuted in the counterweight pass

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model gpt-5.5, reasoning_effort medium, service_tier priority (from .agents/critique-adapter.yaml reviewer_tiers.high-leverage)
- Host exposure state: host-defaulted
- Application state: not host-confirmed; the adapter mapping is a Codex-host field, so this Claude Code host spawned its strongest reviewer (Opus 4.8) instead of sending the gpt-5.5 fields

## Fresh-Eye Satisfaction

parent-delegated — the parent spawned this bounded reviewer in a separate agent
context and it completed the angles + counterweight directly.

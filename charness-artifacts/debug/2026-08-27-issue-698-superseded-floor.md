# Debug Review
Date: 2026-08-27

## Problem

Issue #698 reports that a goal can become `superseded` while a bound retro's
surfaced improvements remain undisposed. The terminal status records only a
successor/remainder pointer, so the run can look honestly non-complete while
still dropping its operational learning.

## Correct Behavior

A superseded transition must preserve two identities: where the remainder was
handed off (`Superseded by:`) and what happened to the retro's surfaced
improvements (`Auto-Retro` disposition). It must not require complete-only
host/evaluator evidence or claim that the goal completed.

## Observed Facts

- GitHub issue #698 is open, labelled `bug`, and its comments were read.
- `check_goal_artifact.py:193-205` checks only `superseded_record`; the
  `check_complete_evidence` branch begins at line 206.
- `goal_artifact_closeout_evidence.py:295-349` is the existing owner of the
  disposition rungs, but its wrapper is named and called only for `complete`.
- `goal_artifact_superseded.py:33-88` validates the handoff pointer/value, not
  retro evidence or disposition.
- The generated artifact makes the Auto-Retro obligation visible with a TODO,
  but the baseline checker does not grade that section for `superseded`.

## Reproduction

- A temporary generated goal had a bound retro with `## Next Improvements`, a
  seeded `Retro dispositions: TODO`, and a substantive `Superseded by:` line.
  The real checker returned `checker_exit=0`, `ok: true`, and emitted only
  `superseded_record`; no disposition verdict was present. The reproduction
  used an external `PYTHONPYCACHEPREFIX` and a temporary fixture root.

## Candidate Causes

- The superseded branch was deliberately scoped to the handoff pointer when
  the lifecycle status was first added, leaving disposition outside its cost.
- The existing disposition wrapper is coupled to complete-only evidence, so
  reusing it wholesale would add host-log and fresh-eye requirements that a
  non-complete terminal record does not claim.
- The focused superseded tests cover pointer/status/refusal behavior but do not
  provide a surfaced-improvement fixture through the production checker.

## Hypothesis

The final checker branches on the exact terminal status and never invokes the
shared disposition rungs for `superseded`. `disconfirmer:` a superseded-only
checker path with an improving retro must return a disposition refusal after a
small shared-floor repair; if it still returns `ok: true`, the branch remains
unwired.

## Verification

Confirmed by the executable temporary fixture above: the baseline path returned
zero with a TODO disposition and an improving retro. The code inspection also
shows the only call to `check_complete_evidence` is under the `complete` branch.

## Root Cause

The lifecycle added a separate `superseded` validator branch but modeled its
contract as only a handoff pointer. The disposition floor was implemented as a
side effect of complete-evidence assembly rather than as a reusable terminal
transition floor. Consequently the superseded branch bypassed the existing
Auto-Retro producer/consumer check and could discard surfaced improvements.

## Invariant Proof

- Invariant: when a bound retro emits surfaced improvements, the superseded
  transition must preserve an explicit disposition and a substantive handoff
  identity before the final checker or writer can accept it.
- Producer Proof: the retro fixture contains `## Next Improvements`; the goal
  template emits `Retro dispositions: TODO` and `Superseded by:` is parsed by
  `goal_artifact_superseded.py`.
- Final-Consumer Proof: the baseline real consumer accepted that fixture with
  exit 0; this is the reproduced detection gap the repair must close.
- Interface-Shape Sibling Scan: `goal_artifact_closeout_evidence.py:295-349`
  owns disposition verdicts; `goal_artifact_superseded.py:33-88` owns terminal
  handoff identity; `goal_artifact_lib.py:219-225` owns write-time refusal.
- Non-Claims: no host activation, fresh-eye review, provider roundtrip, issue
  closure, release, installed export, or complete-status evidence is claimed.

## Detection Gap

- `tests/quality_gates/test_goal_superseded_status.py` | pointer and terminal
  status cases fired, but no production-path improving-retro case existed |
  add positive disposition and missing-field refusal fixtures through both the
  checker and status writer.
- `check_goal_artifact.py` | its `superseded` branch stopped before the shared
  disposition consumer | compose a superseded-specific floor without invoking
  complete-only evidence.

## Sibling Search

- Mental model: a terminal lifecycle branch can preserve its identity field but
  skip a neighboring finalization invariant owned by another branch.
- same-layer: `check_goal_artifact.py:193-225` | decision: same bug, fix now |
  proof: executable baseline fixture.
- abstraction-up: `goal_artifact_closeout_evidence.py:295-349` | decision: same
  class, diagnostic-only for this slice until the reusable terminal wrapper is
  selected | proof: static scan only.
- specialization-down: `goal_artifact_superseded.py:33-88` | decision:
  same bug, fix now by retaining the handoff check beside disposition |
  proof: existing pointer tests plus the new transition fixture.
- cross-file: `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py` |
  decision: same class, diagnostic-only for this slice where complete-only
  evidence is intentionally excluded | proof: static scan only.

## Seam Risk

- Interrupt ID: issue-698-superseded-floor-2026-08-27
- Risk Class: contract-freeze-risk
- Seam: terminal status writer/checker -> Auto-Retro disposition and handoff identity
- Disproving Observation: a superseded fixture with an undisposed improving
  retro is refused by both the checker and the write path.
- What Local Reasoning Cannot Prove: host execution, fresh-eye approval, or
  provider/issue state beyond the local reproduction.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: no
- Next Step: impl
- Handoff Artifact: charness-artifacts/impl/2026-08-27-issue-698-superseded-floor.md

## Prevention

Give non-complete terminal transitions an explicit, shared disposition floor
whose input is the bound retro and whose other output is the existing
`Superseded by:` identity. Keep complete-only host/evaluator requirements out of
that floor, and test the production checker plus writer refusal with both an
improving retro and an explicit no-improvement opt-out.

## Evidence Disposition

- Report Identity: goal-run:724#sha256:3ce10c30a99c88363f1a06e4f9ba08a9aedb7d27c80d8dd6c343e90961972432
- Reported Findings: 1
- Dispositioned Findings: DBG-698-F1
- Missing Findings: none
- Evidence Digest: sha256:760180f7c4b353da611709783eeafc6ccf8776366bd976d063586eb54a7af5bc
- Report Source: charness-artifacts/goal-runs/724/bodies/backlog-698.md
- Report Source SHA256: 3ce10c30a99c88363f1a06e4f9ba08a9aedb7d27c80d8dd6c343e90961972432

## Adversarial Verification

- Finding: DBG-698-F1 | source: charness-artifacts/goal-runs/724/bodies/backlog-698.md | expected: a superseded goal must not bypass the Auto-Retro disposition floor when its bound retro surfaces improvements | stimulus: create a valid goal artifact with a bound retro containing ## Next Improvements, leave Auto-Retro at its seeded unresolved placeholder disposition, add Superseded by: none — an explicit abandonment reason, and run the real check_goal_artifact.py | disposition: reproduced | observed: the superseded validator returned exit 0 and ok: true while the surfaced improvement remained undisposed; its payload contained only superseded_record and no disposition verdict | proof: executable fixture | handoff: charness-artifacts/impl/2026-08-27-issue-698-superseded-floor.md | next move: apply the existing deterministic Auto-Retro disposition floor to superseded transitions without importing complete-only evidence requirements, and require the transition's handoff identity | receipt: charness-artifacts/debug/receipts/issue-698-superseded-bypass.json | receipt sha256: 6a805718ee46e21bb03e5d5c93a083ccef8f32021be9f58dfc0ecfbd26248dd0

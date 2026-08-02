# Issue 471 resolution critique
Date: 2026-08-02

## Decision Under Review

Closing [#471](https://github.com/corca-ai/charness/issues/471) on the repair that
makes `validate_critique_artifacts.has_repo_delegation_contract` flatten inline
markdown emphasis before matching `DELEGATION_CONTRACT_MARKERS`, so the guard
returns `True` against this repo's real `AGENTS.md` and the check it gates
(`_check_forbidden_blocker_phrases`) executes for the first time. Reviewed
together with the measurement offered as the safety argument for closing without
a grandfather: 0 refusals over a stated denominator of 686 candidate artifacts.

## Failure Angles

- **The measurement is right and means less than it reads as.** 0 refusals
  measures how narrowly `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES` is spelled, not that
  the corpus is free of the defect the list exists to catch. Two checked-in
  artifacts name a delegation POLICY as the canonical blocker in a real
  `Fresh-Eye Satisfaction` value and pass on spelling alone (`active delegation
  policy`) against a list carrying `current session delegation policy`. A third
  artifact raised alongside them —
  `charness-artifacts/critique/2026-05-16-mutation-validity-fix.md:5` — is a
  DIFFERENT defect: it writes `Fresh-eye status:`, a field-name variant
  `fresh_eye_satisfaction_status` never reads, so the check has no value to
  inspect and widening the phrase list would not catch it. Closing #471 on "the
  gate is live and refuses nothing" would quietly convert a spelling accident
  into evidence of corpus health.
- **The two readers of one contract could silently diverge again.** The markers
  are restated in `issue_critique_observer` rather than imported, deliberately —
  it is a portable public skill. That duplication is exactly how they drifted:
  the observer carried this repair while the validator did not, and for that
  window one reader said the repo had adopted the contract and the other said it
  had not. Closing the issue without pinning the parity leaves the same drift
  available.
- **The regression tests could pin nothing.** Every pre-existing test around this
  contract built a synthetic `AGENTS.md`, and a synthetic fixture spells the
  marker the way the CODE spells it — which is why a guard that never fired
  looked tested. A repair proven only by more fixtures would reproduce the defect
  class it fixes.
- **Widening MATCHING could widen the POPULATION.** Flattening `` ` * _ ``
  everywhere could in principle let a repo that never adopted the contract read
  as adopted, arming the gate for consuming repos as a side effect of a local fix.
- **An unreadable `AGENTS.md` diverges from the sibling.** `is_file()` can pass on
  a file the process cannot read; the observer returns `False`, the validator
  raised `OSError` — which is not a `ValidationError`, so the run's handler would
  not render it as a validation failure at all.

## Counterweight Pass

Real blockers, folded before the close: the parity pin, the real-file test, and
the `OSError` divergence. Each is a concrete way the resolution could be wrong or
could rot, and each was cheap.

Over-worry, raised and NOT folded: the population-widening angle. `all()` requires
both markers, and marker 2 is a 62-character verbatim sentence; flattening removes
characters without inserting spaces, so `subagent_delegation` becomes
`subagentdelegation`, which does NOT contain `subagent delegation`. Flattening can
destroy a match across a word gap, never fabricate one. A non-adopting repo still
reads `False`, and that is now pinned by a near-miss test rather than by argument.

The phrase-list angle is real but is NOT a blocker to closing #471. #471's subject
is a guard whose activation condition was broken; the list's content is a separate
decision whose repair would refuse checked-in artifacts — an arming decision on a
corpus that cannot object, which this repo has got wrong twice (D49). Filed as
[#472](https://github.com/corca-ai/charness/issues/472) with its own measured
disposition rather than folded here. What the close claims was narrowed to match:
the gate is live and refuses nothing AS SPELLED.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_critique_artifact_validation.py | action: fix | note: pin the contract against the REAL AGENTS.md, not a fixture; a synthetic marker spells itself and is why this was invisible
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/validate_critique_artifacts.py:175 | action: fix | note: unreadable AGENTS.md raised OSError, not ValidationError, diverging from the sibling reader; return False like it does
- F3 | bin: act-before-ship | evidence: strong | ref: tests/test_critique_artifact_validation.py | action: fix | note: pin the two readers' parity on this repo, since the markers are duplicated by design and drift is what caused the defect
- F4 | bin: act-before-ship | evidence: moderate | ref: tests/test_critique_artifact_validation.py | action: fix | note: the absent-repo test passed identically before and after the repair; add the near-miss and a positive markup case that actually witness the flattening
- F5 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/critique/2026-05-21-copy-heavy-release-only-critique.md:7 | action: file-issue | note: the phrase list under-fires; 0 refusals reflects its spelling, not corpus health | follow-up: https://github.com/corca-ai/charness/issues/472
- F6 | bin: over-worry | evidence: strong | ref: scripts/validate_critique_artifacts.py:186 | action: document | note: flattening cannot fabricate a marker match across a word gap, so the population is unchanged; recorded rather than guarded

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer` typed agent), two rounds.
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, session-model inheritance per the Claude Code host arm of the per-host subagent contract.
- Host exposure state: applied
- Application state: host-confirmed: both rounds returned findings inline to the parent; `reviewer_boundary_fingerprint.py verify --before` returned `ok: true, verdict: clean` immediately on each return, before any parent write.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Two bounded rounds ran BEFORE the close call, as the close
path's floor requires. Round 1 read the repair and its measurement and produced
F1–F6; round 2 read only the REPAIRS and found further defects in them, including
two sentences in the parent's own prose that asserted more than had been
established. The parent verified worktree+index integrity around each round.

## Reviewed Input Identity

<!-- No prepare-packet was consumed; each round received an inline bounded slice packet (intent, changed files, claimed measurement with its denominator, expected invariants, reviewer questions, non-claims, out-of-scope lines). -->

## Boundary Ownership

- Producer: `scripts/validate_critique_artifacts.py` — decides whether a consuming repo adopted the bounded-review delegation contract.
- Consumer: `_check_forbidden_blocker_phrases`, the only gated check, plus the issue-close floor's sibling reader in `skills/public/issue/scripts/issue_critique_observer.py`.
- Owning surface: the authoring repo's critique validator, with the portable skill deliberately restating the markers it cannot import.
- Verdict: owned-correctly

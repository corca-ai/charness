# #261 Mutation-Standard Policy Decision Carrier

Date: 2026-06-02
Repo: corca-ai/charness
Goal:
`charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`
Classification: decision-needed

## Resolution Brief

**Classification**: decision-needed

**Reporter JTBD**: decide whether the residual coordination-cues mutation
survivors need more hardening, a global equivalent-mutant exclusion rule, or an
explicit policy disposition.

**Proposed boundary**:

- in scope: close #261 by recording the mutation-standard decision for the
  remaining equivalent/low-value survivors.
- out of scope: new global equivalent-mutant filtering, mutation threshold
  changes, another full survivor-hardening campaign, or live CI proof.

**Non-goals**:

- Do not change mutation score floors, changed-line floors, sampling budgets, or
  scheduled workflow behavior.
- Do not add a broad equivalent-mutant exclusion for regex-flag arithmetic,
  string identity comparisons, release-span blanking, or current-contract
  ordering survivors.
- Do not claim fresh scheduled GitHub Actions proof or a new live mutation run.

**Acceptance checks**:

- #261 has a direct decision carrier with `Close #261`.
- Prior mechanical survivor hardening remains present on `HEAD` and
  `origin/main`.
- The focused coordination-cues tests still pass.
- The carrier draft validates through the issue closeout verifier for
  `decision-needed`.

**Open decisions**:

- none after activation. The selected policy is no-code closure: accepted
  equivalent/low-value residue under the current mutation standard, with no new
  global exclusion rule.

**Autonomous vs pause**: continuing because the active achieve goal surfaced the
close/split/proof decision before activation and the selected boundary changes
no future gate behavior.

## Evidence

- Live issue read: `gh issue view 261` on 2026-06-02 reported state `OPEN` and
  no comments newer than the 2026-06-01 leave-open comments.
- Live #265 read: `gh issue view 265` on 2026-06-02 reported state `CLOSED`;
  its body records the residual exhaustive-triage pickup and the proven
  equivalent classes.
- Mechanical hardening commit `765f5d4 Harden coordination survivor tests` is
  an ancestor of both `HEAD` and `origin/main`.
- Prior scoped proof remains 514/514 executed, 467 killed, 47 survived, 90.9%
  reachable score against an 80% threshold.
- Historical summary re-render from
  `reports/mutation/coordination-cues-dump.jsonl` still reports mutation score
  PASS at 90.9%; its non-zero exit is expected because the proof command uses an
  intentionally nonexistent sample manifest and therefore surfaces blocking
  signal rows for sample-manifest/scope-gap context.
- Focused tests passed:
  `python3 -m pytest -q tests/quality_gates/test_goal_coordination_floors.py tests/quality_gates/test_goal_disposition_gate.py tests/quality_gates/test_goal_head_freshness.py tests/quality_gates/test_achieve_before_activation.py`
  (101 passed).
- Prior fresh-eye critique:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`
  found no blockers and classified the remaining survivors as defensibly
  equivalent or low-value.

## Decision

Close #261 as policy-resolved with no code change.

The current Charness mutation standard remains:

- reachable-score gate stays at the configured threshold;
- changed-line and sample-manifest blocking signals stay separate from the
  reachable score;
- known portable equivalent classes may be filtered when they are structural and
  runner-observable, such as the existing annotation-union filter in
  `scripts/filter_cosmic_ray_mutants.py`;
- target-local implementation-detail survivors are named and accepted when
  fresh-eye review finds that chasing them would add brittle tests without
  improving user-visible behavior.

#261's remaining survivors fit the final category. They are regex flag
arithmetic on equal/disjoint constants, string identity comparisons on interned
single-character strings, release-span blank-count mutations that preserve the
Coordination Cues exclusion, and current-contract ordering comparisons. Adding a
global filter for those would be broader than the evidence supports and would
risk hiding real future mutants. Adding more tests for them would mainly encode
Python or implementation-detail behavior, not operator contract value.
Accepted low-value survivors remain report-visible and countable residue; this
decision creates no hidden exclusion class.

## Close Comment

Resolved in the #261 mutation-standard policy decision carrier.

JTBD: decide whether the residual coordination-cues mutation survivors require
more hardening, a gate-design exclusion, or an explicit policy disposition.

Decision: close as policy-resolved with no code change. The mechanical
survivor-hardening path is complete through #265 and commit `765f5d4`; the
remaining #261 survivors are accepted as equivalent/low-value residue under the
current mutation standard rather than becoming a new global exclusion rule. They
remain report-visible and countable residue, not a hidden filter precedent.

Boundary: no mutation thresholds, sampling budgets, changed-line floors,
scheduled workflow behavior, or equivalent-mutant filters changed in this
carrier.

Evidence:

- Goal artifact:
  `charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`
- Carrier artifact:
  `charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md`
- Gathered issue snapshot:
  `charness-artifacts/gather/2026-06-02-github-issue-261-mutation-standard-policy.md`
- Prior survivor critique:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`

Close #261.

## Non-Claims

- No code, tests, thresholds, filters, release surface, or workflow behavior were
  changed by this carrier.
- No fresh scheduled GitHub Actions mutation run was observed.
- The historical `check_mutation_score.py` re-render intentionally preserves its
  non-zero blocking-signal shape because it uses a nonexistent sample manifest;
  it is cited only for the reachable-score and survivor-count evidence.
- GitHub issue state is still `OPEN` until this carrier is published to the
  default branch and GitHub auto-closes the issue.

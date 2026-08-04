# Goal Disposition Review — Decide Where a Recurring Lesson Lives
Date: 2026-08-04

## Decision Under Review

The repaired closeout record for goal
`charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md`.
The review audits the goal's claims, evidence identity, six-issue acceptance,
retro dispositions, remote readback, and non-claims; it is not a second code
review.

## Acceptance Bar Audit

Pass on the substantive record. One selector weighs all three answers: a gate
only for an observable predicate with a recorded escape and measured false-fire
cost; a reviewer question for judgment-bound facts; and a surface fix when the
owning surface can carry the fact. The six findings are dispositioned under that
selector: #499/#491 use the semantic reviewer question, #500/#502/#501/#497 use
surface ownership and proof. The five #499 instances remain historical evidence,
not a new implementation requirement.

## Slice F Repair Audit

The original closeout cited a retro owned by another goal. The repaired retro
contains the exact goal slug, the closeout validator reports no binding failure,
and the lesson-selection digest is regenerated from it. The issue #504 follow-up
records the general goal-aware persistence capability separately instead of
pretending this concrete repair generalized the helper.

The remote readback is an audit record for the already-published carrier, not a
second closeout carrier. Its carrier sentence names the prior commit and issue
numbers without repeating close keywords, so the commit boundary does not
mistake the readback for a new issue-resolution publication.

The 12 `## Next Improvements` are dispositioned one-for-one in the goal's
`## Auto-Retro`: nine applied workflow/quality/memory improvements, two explicit
out-of-scope capabilities, and the #504 follow-up. The structural follow-up
remains #503 for the separate recurring closeout-runtime class.

## Claims And Channels

- #497 behavior: freshly generated exported-plugin subprocess with
  `CHARNESS_REPO_ROOT` removed.
- #500 behavior: hostile producer inputs refuse unsafe values before writing and
  leave no artifact.
- #501 behavior: direct export-gate execution covers supported literals and
  negative controls for unsupported dynamic forms.
- Remote tracker state: the separate authenticated `gh issue view` readback at
  `charness-artifacts/issue/2026-08-08-decide-where-a-recurring-lesson-lives-remote-readback.md`
  records #497/#500/#501 CLOSED at the observed timestamp; it is not treated as
  behavior proof.

## Counterweight Triage

- **Act Before Ship:** commit the fully validated evidence bundle. The host
  completion call is downstream bookkeeping after the checked-in record exists.
- **Bundle Anyway:** retain the goal-bound retro, regenerated lesson index,
  handoff refresh, issue #504 body, and remote readback as one audit bundle.
- **Over-Worry:** rerun the broad production suite solely for this markdown and
  evidence-binding repair; no production code or tests changed in Slice F.
- **Valid but Defer:** general goal-aware retro persistence belongs to #504.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: goal Slice F and complete-state validator | action: document | note: commit the repaired evidence bundle before downstream host bookkeeping
- F2 | bin: bundle-anyway | evidence: strong | ref: goal Auto-Retro and retro Next Improvements | action: document | note: retain all 12 explicit improvement dispositions and the #504 destination
- F3 | bin: over-worry | evidence: strong | ref: Slice F changed-path set | action: defer | note: no broad code suite rerun is needed for an artifact-only repair
- F4 | bin: valid-but-defer | evidence: moderate | ref: issue #504 | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/504 | note: helper-level goal identity should be designed separately

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none.
- Host exposure state: requested_fields_sent
- Application state: host application not independently confirmed; no applied claim made.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — the final claims review first found the incomplete Slice F
state and missing improvement disposition; the repair-read round read those
repairs and found only the remaining commit boundary. Boundary fingerprints were
clean for the repair-read round. A later repair-read round caught that this
record still named the superseded packet after the readback wording changed; the
record is rebound below to the regenerated packet, and the canonical verifier
is the authority for its sha256-v2 content identity. Final repair-read reviewer
Hume (`019fcb4a-d9cb-7473-9415-16fc19daa16b`) returned Pass with no blockers;
boundary window `slice-f-final-repair-read-6` verified clean before this record
was updated.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-04-053842-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-04-053842-packet.json`
- Packet SHA256: `4bf8f3dfe7aeeb56ebb02d6edc5e3ba2be254cd58e5add6af8fe92979ade6ef0`
- Identity SHA256: `adc57fc1f4947c337372103d822bd42194bd31054f33d0ca3bbb7c84676d981f`

## Boundary Ownership

- Producer: the goal artifact, goal-bound retro, issue carrier/readback, and
  critique review each produce a different closeout fact.
- Consumer: the next operator, closeout validator, issue tracker reader, and
  host completion surface.
- Owning surface: the goal artifact owns the decision and completion claim;
  each cited artifact owns its evidence detail.
- Verdict: owned-correctly

## Verification

- `check_goal_artifact.py --goal-path charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md` returned `ok: true` with no binding or disposition failures.
- `validate_retro_artifact.py` validated the goal-bound retro; handoff and lesson-selection-index validators pass.
- Canonical binding for the supplied JSON packet returned `current` under the
  packet's recorded sha256-v2 algorithm.
- The prior locked bundle proof recorded 7048 standing tests passed in 44.52s; no production code changed in this repair, so broad rerun is not required.

## Deliberately Not Doing

No claim is made for host rendering, future reviewer uptake, per-goal host
metrics, arbitrary dynamic imports, or general retro-persistence behavior.

## Next Move

Commit the evidence bundle and rerun the complete-state validator against the
committed bytes. The commit is the remaining procedural closeout step, not an
unproven behavioral claim; host bookkeeping follows the checked-in record.

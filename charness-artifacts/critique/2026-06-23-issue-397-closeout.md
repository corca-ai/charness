# issue 397 closeout
Date: 2026-06-23

## Decision Under Review

Close #397 after the quality runtime-reference defect was fixed and proven by a
neutral `/charness:quality` capture, while deferring the separate diagnostic
Cautilus artifact-home gap to #398.

## Failure Angles

- Jackson problem framing: the carrier could overstate the decision as "resolved
  #397" even though #397 included the diagnostic artifact-contract sub-gap.
  Finding: bundle the cheap wording fix. The carrier now says it resolved
  "#397's quality runtime-reference defect" and points the sub-gap to #398.
- Weinberg diagnostic: the closeout could accept a weak proxy instead of the
  issue's actual behavior. Finding: the post-fix evidence uses the same behavior
  surface as the original report: a neutral `/charness:quality` invocation, no
  hints about planner or references, `9/39` coverage, and `quality-lenses.md`
  observed. A separate fresh Cautilus accept recommendation was not produced;
  that is valid to defer because the runtime predicate is directly observed.
- Gawande operational checklist: the draft initially failed closeout validation
  because the critique artifact did not exist and the manual fallback reason was
  not rendered with the recognized field name. Finding: act before ship. This
  artifact was added and the carrier now uses `Manual Fallback Reason:`.

## Counterweight Pass

- Act before ship: satisfy validator-visible closeout shape before publishing:
  checked-in critique artifact, recognized manual fallback reason, draft
  validation, durable evidence commit, then GitHub close verification.
- Bundle anyway: keep #398 as the concrete follow-up for the diagnostic negative
  verdict artifact-home gap; it is already created and read back as open.
- Valid but defer: do not require a broad cross-skill rollout or a fresh
  evaluator accept recommendation for #397. The proof is scoped to the quality
  runtime-reference predicate and says so.
- Over-worry: requiring the original negative diagnostic to become a passing
  `latest` proof would blur the distinction that #398 exists to preserve.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/issue-397-closeout/closeout-comment.md:1 | action: fix | note: narrowed opening line from broad #397 resolution to the quality runtime-reference defect
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue-397-closeout/closeout-comment.md:44 | action: fix | note: render validator-visible Manual Fallback Reason before publishing the manual close carrier
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-06-23-issue-397-closeout.md | action: fix | note: provide checked-in resolution critique bound to #397 before closeout validation
- F4 | bin: valid-but-defer | evidence: strong | ref: https://github.com/corca-ai/charness/issues/398 | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/398 | note: diagnostic Cautilus negative-verdict artifact home is real but separate from #397's runtime-reference defect
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/cautilus/quality-claim-fidelity-2026-06-23-planner-capture/finding.md:47 | action: defer | note: no full repository quality closeout or cross-skill rollout is claimed in this slice

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none; parent used `multi_agent_v1.spawn_agent` with
  default inherited model/effort per host tool guidance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: `multi_agent_v1.spawn_agent` returned
  agents `019ef2e2-3895-79c3-a522-e5f203873e66`,
  `019ef2e2-54e3-7483-985f-3ac7351c6802`, and
  `019ef2e2-6f46-7f33-90c7-c5497deb52ac`; all completed via `wait_agent`.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Three bounded reviewers completed
distinct angles:

- Jackson problem framing: no Act Before Ship; bundle the wording precision now
  applied to the carrier.
- Weinberg diagnostic: behavior evidence directly matches #397's runtime
  predicate; do not claim external closeout until the GitHub state is verified.
- Gawande operational checklist: Act Before Ship until this critique artifact,
  recognized manual fallback reason, draft validation, durable commit, and
  final close verification are complete.

# Achieve Goal: #261 mutation-standard policy decision

Status: complete
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 3 - final critique, verification, and closeout.
- Next action: flip the goal to complete after deterministic artifact validation,
  then commit with direct-commit closeout evidence.
- Verification cadence: decision brief and focused issue/source reads first;
  cheap deterministic checks at commit boundaries if implementation becomes
  necessary; fresh-eye critique at the policy decision and final closeout
  boundary; broad proof only after the policy slice is stable.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files or decision artifacts, expected invariants, tests/proof, non-claims, and
  reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve GitHub issue #261 as a bounded mutation-standard policy decision: decide
whether the remaining coordination-cues mutation survivors should be closed as
accepted equivalent/low-value residue, require a repo-owned equivalent-mutant
exclusion rule, or become a smaller follow-up with explicit proof. This
Before-phase artifact is draft-only; execution starts only after `/goal`
activation.

## Non-Goals

- Do not re-run the full #261 coordination-cues survivor campaign by default.
  Prior proof already records 514/514 executed, 467 killed, 47 survived, and a
  90.9% reachable score.
- Do not lower the mutation score floor, changed-line floor, sampling budgets,
  or workflow thresholds to make the issue closable.
- Do not chase survivors already classified by prior fresh-eye critique as
  equivalent or low-value unless a new proof contradicts that classification.
- Do not fold #184 product-success work, #273/#274 regression recovery, or a
  release/version bump into this goal.
- Do not close #261 silently. If it closes, the carrier must make the policy
  decision explicit and use the `issue` closeout path.

## Boundaries

- Treat GitHub issue #261 as the live source of truth for state and current
  comments. Local handoff and older goal artifacts are context, not issue state.
- The residual question is policy/decision-needed after mechanical survivor
  hardening, not another broad coverage-fix campaign unless the first slice
  proves a real, user-visible contract gap.
- In scope: existing #261 body data, prior survivor triage artifacts, prior
  fresh-eye critique, mutation policy references, and focused implementation
  only if the decision requires a repo-owned filter/rule/test.
- Out of scope without user confirmation: new global equivalent-mutant exclusion
  policy, any threshold change, any irreversible issue close that lacks an
  explicit policy rationale, or filing broad follow-up issues.
- Stop and ask before choosing a new policy rule that changes what future
  mutation runs count or exclude. Closing #261 as "accepted equivalent/low-value
  residue" is also a policy decision and must be named in the carrier.

Discuss before activation: this goal is shaped to decide and possibly close
#261, but it must not auto-close the issue merely because prior mechanical
hardening exists. Activation should confirm that a policy decision, a narrow
follow-up, or an explicit leave-open comment are all acceptable outcomes; broad
live mutation proof and remote GitHub issue closure are non-claims until run and
verified.

## User Acceptance

- Read the final #261 carrier/comment and see one explicit disposition:
  `close as policy-resolved`, `leave open with a narrower policy question`, or
  `split/file a focused follow-up`.
- Inspect the goal artifact and issue carrier to see why the chosen disposition
  follows from current #261 evidence, prior scoped proof, and fresh-eye critique.
- If code/tests change, run the named focused tests or validators and see they
  cover the changed rule. If no code changes, see the no-change rationale and
  policy proof instead.
- After publication, verify GitHub issue #261 is in the expected state and has
  the expected close/comment text.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- `gh issue view 261 --json number,title,state,body,comments,labels,url,updatedAt`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/skills/find-skills/scripts/list_capabilities.py --repo-root . --read-only --recommend-for-task "<current boundary>"`
- Re-read prior proof anchors:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`,
  `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`,
  and `charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`.
- If artifacts or docs change, run `python3 scripts/check_changed_surfaces.py --repo-root .`.
- If tests are added or expanded, include a cheap duplicate/length pressure
  sample before slice closeout.

### High-Confidence Checks

- A decision brief that classifies #261 as `decision-needed` unless the first
  slice finds a concrete bug-class behavior divergence.
- Fresh-eye critique of the decision packet before final closeout, focused on
  whether the chosen disposition confuses equivalent mutants, low-value
  survivors, and untested real contracts.
- If implementation is needed, focused tests for the exact changed helper/rule
  plus `ruff` or pycompile for touched Python.
- Final closeout gate after the mutation set is stable:
  `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`, or
  a documented substitute if no code/test surface changed and the repo-local
  contract makes the full gate disproportionate.

### External Or Live Proof

- GitHub issue reads through the selected issue backend (`gh`) before and after
  closeout.
- If #261 is closed, stage the close through `issue` with an explicit close
  keyword in the carrier body or an issue-verified manual fallback.
- Do not claim a fresh scheduled mutation workflow, live GitHub Actions proof,
  or remote issue closure unless observed after publication.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Shape #261-only goal | User invoked `charness:achieve #261` after handoff named #261 as the live mutation-standard policy question | Goal artifact passes `check_goal_artifact.py --pursue-ready`; gathered issue snapshot exists; activation discussion names close/split/proof non-claims | done |
| 1 | Build #261 decision brief | The issue is decision-needed; decide before mutating code or re-running broad mutation proof | Brief classifies accepted residue vs rule/filter vs focused follow-up; open policy decisions are surfaced before design | done |
| 2 | Implement only the chosen narrow outcome | Avoid another survivor-hardening campaign unless the brief proves code/tests are required | Either no-change carrier with policy proof, or focused code/tests and deterministic verification for the selected rule | done |
| 3 | Critique, verify, and stage issue disposition | Repo closeout requires fresh-eye review, proof, and issue discipline | Fresh-eye critique; final validation or documented substitute; issue carrier/comment draft validated; goal closeout evidence bound | done |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.

Routing: startup `find-skills` recommended public `achieve`, with `issue` and
`gh` as the supporting route for the tracked GitHub issue. During activation,
ask `find-skills` again at policy/validation boundaries rather than baking a
phase-to-skill map into this artifact.

Gather: charness-artifacts/gather/2026-06-02-github-issue-261-mutation-standard-policy.md

Release: n/a - this goal does not plan a version bump, install-manifest edit,
or release surface.

Issue closeout: charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md

Retro: charness-artifacts/retro/2026-06-02-261-mutation-standard-policy-decision.md

Host log probe: charness-artifacts/probe/2026-06-02-261-mutation-standard-policy-decision.json

Disposition review: charness-artifacts/critique/2026-06-02-261-mutation-standard-policy-decision-disposition.md

## Slice Log

### Slice 1: Build #261 decision brief

- Objective: Classify #261 after #265 and decide whether the remaining mutation survivors require code, a global filter, a focused follow-up, or policy closure.
- Why this approach: The issue is decision-needed; deciding from current issue/proof state prevents another broad survivor-hardening campaign.
- Commits:
- What changed: No code changed. Read live #261 and #265, prior #265/#261 proof artifacts, existing mutation-filter code, and the mutation score contract. Drafted the decision boundary in charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md.
- Alternatives rejected: Rejected a new global equivalent-mutant exclusion rule because the residual classes are target-local implementation details or low-value current-contract mutants, not portable runner semantics. Rejected another full survivor campaign because #265 is closed and prior proof already moved the score to 90.9%.
- Targeted verification: PASS: gh issue view 261 showed OPEN with no newer comments; PASS: gh issue view 265 showed CLOSED; PASS: git merge-base proves 765f5d4 is ancestor of HEAD and origin/main; PASS: historical mutation score re-render shows 467 killed / 47 survived / 90.9% reachable score, with expected non-zero blocking-signal shape from nonexistent sample manifest; PASS: focused pytest for coordination-cues goal surfaces returned 101 passed.
- Test duplication pressure: No tests added or expanded in this slice.
- Critique: Fresh-eye review accepted no-code policy closure and requested
  explicit report-visible/countable residue wording; the carrier now includes
  it.
- Off-goal findings: N/A - no off-goal findings.
- Lessons carried forward: For #261, policy closure is narrower and safer than creating a broad equivalent-mutant filter for target-local residuals.
- Metrics: No host goal-window metrics available for this slice.

### Slice 2: Stage no-code #261 issue disposition

- Objective: Stage the selected no-code policy outcome through the issue closeout workflow.
- Why this approach: The decision brief concludes #261 should close as policy-resolved without changing gate behavior.
- Commits:
- What changed: Added charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md with a decision-needed resolution brief, explicit policy decision, close comment, Close #261 keyword, evidence, and non-claims.
- Alternatives rejected: Did not close GitHub manually; achieve does not push and issue closeout prefers default-branch auto-close. Did not use a manual-fallback close because auto-close remains available after publication.
- Targeted verification: PASS: issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 261 --classification decision-needed --body-file charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md --repo-root . returned status draft_verified with no missing fields or close keywords.
- Test duplication pressure: No tests added or expanded in this slice.
- Critique: Fresh-eye review accepted the decision-needed classification and
  draft carrier; it required filling goal closeout sections before complete
  flip and preserving `Close #261` in the final direct-commit body.
- Off-goal findings: N/A - no off-goal findings.
- Lessons carried forward: For decision-needed issues, the carrier still needs JTBD, Decision, and close keyword evidence even when no code changed.
- Metrics: No host goal-window metrics available for this slice.

## Context Sources

- Gathered live issue snapshot:
  `charness-artifacts/gather/2026-06-02-github-issue-261-mutation-standard-policy.md`
- GitHub issue: https://github.com/corca-ai/charness/issues/261
- Handoff route: `docs/handoff.md`
- Quality posture: `charness-artifacts/quality/latest.md`
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`
- Prior #261 policy critique:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`
- Prior bounded goals:
  `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`
  and
  `charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`
- Prior issue carriers:
  `charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md`
  and
  `charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md`

## Interview Decisions

- Mode: user invoked `charness:achieve #261`, so this is the Before-phase draft
  for a later implementation-continuation run. Rejected alternative:
  immediately pursuing slices in this turn, because `/goal` activation is the
  explicit execution boundary. Axis note: single-point per-goal lifecycle mode,
  not a host/provider axis.
- Scope: choose #261-only mutation-standard policy decision. Rejected
  alternatives: re-bundling #273/#274, because their goals are complete and left
  #261 open intentionally; broad survivor hardening, because prior proof and
  critique already narrowed the remaining question to equivalent/low-value
  policy. Axis note: issue tracker is GitHub for this repo run, but issue-source
  handling is host-variable; use `issue` rather than hardcoding GitHub-only
  closeout behavior into reusable surfaces.
- Acceptable outcomes: close #261 only with explicit policy proof, leave it open
  with a sharper decision question, or file/split a narrow follow-up after user
  confirmation. Rejected alternative: treating prior mechanical hardening as
  sufficient to close #261 without a policy statement. Axis note: single-point
  policy disposition for this issue, not a profile/env default.
- Proof cost: start with issue/source rereads and a decision brief; run focused
  validators if code/tests change; reserve broad closeout until the slice is
  stable. Rejected alternative: full mutation/broad pytest as readiness
  discovery, which recent retros identify as waste.

## Plan Critique Findings

- Prior fresh-eye provenance:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`
  found no blockers in the bounded survivor triage and said the remaining
  survivors are defensibly equivalent or low-value. This finding is folded into
  Non-Goals and the Slice Plan by making policy disposition the first real
  slice, not broad survivor hardening.
- Same-session Before-phase critique: the main failure risk is accidental issue
  closure by inertia. Folded response: `Discuss before activation:` explicitly
  names close/split/leave-open outcomes and the issue closeout cue starts as
  planned, not satisfied.
- Over-worry not folded: a fresh full scoped mutation run could give newer
  numbers, but it is not required before the policy brief because the issue's
  current comments already define the open question as policy residue. Run it
  only if the brief identifies a concrete contradiction in existing proof.

## Off-Goal Findings

N/A - none during shaping.

## Final Verification

PASS:
`python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/skills/issue/scripts/issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 261 --classification decision-needed --body-file charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md --repo-root .`
returned `ok: true`, `status: draft_verified`, no missing fields, and no missing
close keywords.

PASS:
`python3 -m pytest -q tests/quality_gates/test_goal_coordination_floors.py tests/quality_gates/test_goal_disposition_gate.py tests/quality_gates/test_goal_head_freshness.py tests/quality_gates/test_achieve_before_activation.py`
returned `101 passed in 3.13s`.

PASS: changed-surface scan mapped this no-code artifact change to markdown,
critique-artifact, probe-JSON, and retro-index gates:
`python3 scripts/check_changed_surfaces.py --repo-root .`.

PASS:
`python3 scripts/check_doc_links.py --repo-root .`,
`python3 scripts/check_command_docs.py --repo-root .`,
`./scripts/check-markdown.sh`, and `./scripts/check-secrets.sh`.

PASS:
`python3 scripts/validate_critique_artifacts.py --repo-root . --all`
validated 181 critique artifacts.

PASS:
`python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write`
then
`python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check`
wrote and validated the retro lesson selection index.

PASS:
`for probe_json in charness-artifacts/probe/*.json; do python3 -m json.tool "$probe_json" >/dev/null || exit $?; done`
validated probe JSON syntax.

PASS:
`python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/skills/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`
passed after the complete flip with `closeout_evidence.ok: true`.

Corrected command-form failure:
`for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done`
failed in `zsh` because `path` mutates command search state. Re-run with
`probe_json` passed.

Non-claims:

- No production code, tests, mutation thresholds, mutation filters, or workflow
  behavior changed in this goal.
- No fresh live mutation workflow, broad CI run, or full scheduled mutation proof
  was executed for #261.
- The historical mutation-score re-render reproduced the existing 467 killed /
  47 survived / 90.9% reachable context and intentionally retained the old
  missing-sample-manifest blocking-signal shape; it is not a new pass claim.
- GitHub issue #261 remains open locally until the closeout commit reaches the
  repository's default branch and GitHub processes `Close #261`.

## User Verification Instructions

Inspect
`charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md`
to verify the selected disposition is explicit: close #261 as policy-resolved
with no code change, while accepted survivors remain report-visible and
countable residue.

Inspect the final direct-commit body and confirm it includes `Close #261` plus a
decision-needed ledger. After that commit reaches the default branch, verify
GitHub issue #261 closes through the auto-close mechanism; until then, remote
closure is not claimed.

## Auto-Retro

Retro artifact evidence:
`charness-artifacts/retro/2026-06-02-261-mutation-standard-policy-decision.md`

Host log probe evidence:
`charness-artifacts/probe/2026-06-02-261-mutation-standard-policy-decision.json`

Disposition review evidence:
`charness-artifacts/critique/2026-06-02-261-mutation-standard-policy-decision-disposition.md`

Retro dispositions:

- applied: The issue carrier now states that accepted low-value survivors remain
  report-visible and countable residue, not a hidden filter precedent.
- applied: The active goal's draft-only closeout placeholders are replaced with
  final verification, user verification, and retro evidence before the complete
  flip.
- applied: The closeout path preserves the carrier/commit distinction:
  `issue_tool.py validate-closeout-draft` verified the local draft, and the
  final commit body must carry `Close #261` for default-branch auto-close.

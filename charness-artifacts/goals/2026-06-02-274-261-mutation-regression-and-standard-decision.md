# Achieve Goal: #274 + #261 mutation regression and standard decision

Status: complete
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete - #274 is fixed locally and staged for closeout; #261
  is left open with a precise mutation-standard disposition.
- Next action: publish the local carrier when ready, then verify GitHub issue
  state and any post-fix mutation workflow run before claiming remote proof.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files, expected invariants, tests/proof, non-claims, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve the live #274 mutation regression first, then use the recovered
evidence to make a bounded #261 mutation-standard disposition. The sequence is:
restore the mutation gate's changed-line/selection trust on `main`, then decide
whether #261 can close as policy-resolved, should remain open as a narrow
mutation-standard decision, or needs a smaller follow-up issue.

## Non-Goals

- Do not lower mutation score, changed-line, mutation-line, or selection
  thresholds to make #274 pass.
- Do not absorb all historical #261 survivor hardening into this run. #261 scope
  is triage and policy/disposition after #274, not an exhaustive campaign to kill
  every remaining survivor.
- Do not chase mutants already proven equivalent or low-value in prior #261
  artifacts unless the new #274 evidence contradicts that classification.
- Do not include #184 product-success metric synthesis.
- Do not cut a release or bump plugin/install surfaces unless the actual fix
  unexpectedly touches a release-owned surface.

## Boundaries

- #274 comes first. Treat the latest GitHub issue comments as the source of
  truth. Earlier comments named Python changed-line blockers and
  `scripts/portable_artifact_lib.py` survivors; the latest comments on
  2026-06-02 report `StrykerJS JSON report missing` and no mutation sample
  manifest for runs on `56e9ac59` and `4c3dcbe1`.
- #261 comes second and stays bounded to mutation-standard disposition:
  classify remaining coordination-cues survivors as implemented, equivalent,
  low-value policy residue, or deferred follow-up with evidence.
- Because #274 is bug-class, run a debug/root-cause step before the fix slice;
  do not jump directly from the CI report to tests without naming the failing
  invariant.
- Treat GitHub issue state as the source of truth for closeout. Handoff text and
  prior goals are context, not live issue state.
- Stop and ask before closing #261 if the evidence would require a broad policy
  change, threshold change, new equivalent-mutant exclusion rule, or more than a
  narrow follow-up.
- Stop and ask before filing new issues unless the #261 disposition needs a
  specific follow-up issue to avoid leaving vague policy residue.

### Discuss before activation

- The goal intentionally bundles `#274 + #261`, but #261 is not an exhaustive
  survivor-hardening campaign. It is a bounded post-#274 disposition decision.
- Final proof may close #274 while leaving #261 open with a precise policy
  comment. That is an acceptable completion outcome if the evidence supports it.
- Live GitHub Actions proof is not claimed unless it is actually observed after
  publication; local deterministic proof can be the pre-push proof floor.

## User Acceptance

- #274 is fixed locally and staged for closeout with evidence that the latest
  changed-line blockers are covered or no longer blocking.
- #274 has a closeout path: close keyword in the carrier commit/PR body or a
  verified manual fallback after push.
- #261 has a concrete disposition: closed with implemented proof/policy, or left
  open with a narrow verified comment naming the remaining mutation-standard
  decision.
- Any surviving mutants left in the selected scope are named as equivalent,
  low-value policy residue, advisory JS pass-slice residue, or deferred follow-up
  with evidence.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- `gh issue view 274 --json number,title,labels,body,url,state`
- `gh issue view 261 --json number,title,labels,body,url,state`
- Focused pytest for touched helpers and tests.
- `python3 -m py_compile` or `ruff check` for touched Python scripts when
  applicable.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after edits.
- Cheap duplicate/length pressure sample if tests are added or expanded.

### High-Confidence Checks

- Debug/root-cause artifact for #274 that names the failing invariant and why the
  existing tests missed it.
- Targeted changed-line coverage or mutation-selection proof for the #274
  blocker files named by the issue.
- Targeted survivor proof or focused tests for `scripts/portable_artifact_lib.py`
  if the sampled survivor shape is still live.
- Bounded #261 disposition proof against prior survivor-hardening artifacts and
  any new evidence from this run.
- Slice-level fresh-eye critique before final closeout, scaled to the changed
  surface and issue-disposition risk.
- Final `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`
  or documented substitute that satisfies the repo's closeout contract without
  premature broad pytest reruns.

### External Or Live Proof

- GitHub issue reads through `gh` before and after closeout.
- If pushed during the run, verify #274 closeout state and #261 comment/close
  state on GitHub.
- Do not claim scheduled mutation workflow proof unless a fresh run is observed
  after the fix.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Shape #274 + #261 goal | User selected the merged order and invoked achieve | Goal artifact passes `check_goal_artifact.py --pursue-ready`; consequential defaults are visible before activation | done |
| 1 | Debug and fix #274 live mutation regression | Mainline mutation gate trust is the first blocker and unlocks cleaner #261 policy judgment | Root-cause artifact; focused tests; proof that the StrykerJS report path produces or honestly classifies its JSON report before Python mutation sampling proceeds | done locally |
| 2 | Decide bounded #261 mutation-standard disposition | User asked to bundle #261 after #274, but not as an exhaustive survivor campaign | Evidence-backed close/defer decision; comment or closeout text names remaining equivalent/low-value/policy residue | in progress |
| 3 | Verify, critique, and stage issue closeout | Repo closeout requires synchronized surfaces, critique, proof, and issue discipline | Changed-surface obligations; final validation; fresh-eye critique; carrier commit/PR text with #274 closeout and #261 disposition | done locally |

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

Gather: n/a - source context is GitHub issue content read through `gh` plus
checked-in repo artifacts; no external document needs durable gathering.

Release: n/a - no release surface is planned.

Retro:
charness-artifacts/retro/2026-06-02-274-261-mutation-regression-and-standard-decision.md

Host log probe:
charness-artifacts/probe/2026-06-02-274-261-mutation-regression-and-standard-decision.json

Disposition review:
charness-artifacts/critique/2026-06-02-274-261-mutation-regression-and-standard-decision-disposition.md

## Slice Log

### Slice 0: Shape and activate #274 + #261 goal

- Objective: Convert the selected chunk bundle into an auditable active goal.
- Verification: `check_goal_artifact.py --pursue-ready` passed; goal artifact
  committed in `69a1762d`.
- Live source update: `gh issue view 274` on 2026-06-02 shows newer comments
  than the drafted #274 boundary. Latest failure symptom is `StrykerJS JSON
  report missing` for runs on `56e9ac59` and `4c3dcbe1`; Slice 1 pivots to that
  current issue state instead of the older Python changed-line blocker text.
- Non-claims: no code fix has been implemented yet; #261 disposition has not
  started.

### Slice 1: #274 workflow validation dependency

- Objective: Diagnose and fix the latest #274 scheduled mutation failure.
- Why this approach: The latest issue comments showed StrykerJS JSON missing, but live workflow logs proved the run failed earlier in Select mutation sample because tokei was absent on the GitHub runner.
- Commits: `ff5591eb Install mutation workflow length gate dependency`
- What changed: Added an Install validation binaries step to .github/workflows/mutation-tests.yml that installs tokei before mutation sampling; added test_quality_mutation_testing coverage pinning the ordering; recorded debug evidence in charness-artifacts/debug/latest.md and 2026-06-02-274-mutation-workflow-tokei-dependency.md; regenerated seam-risk index.
- Alternatives rejected: Did not change StrykerJS config because local Stryker already writes the configured JSON report when executed. Did not change mutation thresholds or skip length-gate tests. Did not fix the secondary misleading summary behavior in this slice; it is now monitored after the dependency fix.
- Targeted verification: PASS: pytest -q tests/quality_gates/test_quality_mutation_testing.py (39 passed). PASS: check_github_actions, validate_debug_artifact, build_debug_seam_risk_index --check, doc links, command docs, markdown, secrets, adapters, packaging, packaging_committed, ruff, check_python_lengths, attention-state visibility. PASS: run_slice_closeout.py --skip-broad-pytest completed; broad pytest intentionally skipped pre-lock per recent lessons.
- Test duplication pressure: Added one focused workflow-ordering test; check_duplicates.py --fail-on-match --require-git-file-listing reported no duplicates at threshold 0.98.
- Critique: Debug artifact sibling scan found the root cause was workflow validation dependency setup, not StrykerJS reporter config. Required slice/final critique still pending before goal closeout.
- Off-goal findings: Potential diagnostic-reporting follow-up: summary can report missing JS JSON after an upstream sample failure; deferred unless the dependency fix does not recover #274.
- Lessons carried forward: Latest issue comments can contain downstream symptoms; use workflow job step state to find the earliest failing component before implementing.
- Metrics: No host goal-window metrics recorded for this slice.

### Slice 2: #261 bounded disposition

- Objective: Decide whether #261 can close after the #274 workflow dependency
  fix, without expanding into an exhaustive survivor-hardening campaign.
- Live source update: `gh issue view 261` on 2026-06-02 shows #261 is still open
  and already carries leave-open comments after the open-issue closeout carrier
  and the #273 mutation gate recovery carrier.
- Decision: leave #261 open intentionally. The current #274 evidence proves a
  workflow dependency/setup failure (`tokei` missing before mutation sampling),
  not missing coordination-cues survivor hardening or a mutation-standard policy
  resolution.
- Carrier: drafted
  `charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md`
  with #274 closeout text and a #261 leave-open comment.
- Remaining #261 residue: prior scoped proof remains 514/514 executed, 467
  killed, 47 survived, 90.9% reachable score; prior critique classifies the
  remaining survivors as equivalent/low-value mutation-standard policy residue.
- Non-claims: #261 is not closed by this goal; no new equivalent-mutant exclusion
  rule or gate threshold change was implemented.

### Slice 3: Verify, critique, and stage closeout

- Objective: Prove the local fix and stage an honest #274/#261 issue carrier.
- Critique: parent-delegated fresh-eye causal review plus resolution critique
  recorded in
  `charness-artifacts/critique/2026-06-02-274-261-mutation-workflow-recovery-resolution.md`.
- Closeout draft: `issue_tool.py validate-closeout-draft --repo
  corca-ai/charness --number 274 --classification bug --body-file
  charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md
  --repo-root .` returned `status: draft_verified`.
- Final validation: `python3 scripts/run_slice_closeout.py --repo-root .
  --verification-lock` returned `Closeout status: completed`; broad pytest
  passed 2027 tests with 4 skipped.
- Carrier: final commit body should carry `Close #274`; #261 remains open with
  the drafted leave-open comment.
- Non-claims: remote GitHub issue state is still open before publication; no
  post-fix scheduled or manual mutation workflow success has been observed.

## Context Sources

- GitHub issue: https://github.com/corca-ai/charness/issues/274
- GitHub issue: https://github.com/corca-ai/charness/issues/261
- Handoff route: `docs/handoff.md`
- Quality posture: `charness-artifacts/quality/latest.md`
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`
- Prior related goal:
  `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`

## Interview Decisions

- Scope bundle: user asked whether `#274 + #261` is possible and then confirmed
  "that order"; chosen bundle is #274 first, then bounded #261 disposition.
  Rejected alternatives: `#274` alone would ignore the user's requested bundle;
  exhaustive #261 survivor hardening would delay live regression recovery.
- #261 outcome: accepted completion includes "leave open with precise policy
  comment" when evidence supports it. Rejected alternative: silently close #261
  by treating prior hardening as a broad policy decision.
- Proof level: use focused proof before broad closeout and avoid premature full
  pytest reruns. Rejected alternative: rerun broad gates as readiness discovery,
  which recent lessons identify as waste.
- Axis check: issue provider is GitHub for this repo run, but issue-source
  handling is host-variable in Charness; closeout should use the issue workflow
  surface rather than hardcoding GitHub-only assumptions into reusable docs or
  skills.

## Plan Critique Findings

- Folded blocker: bundling #261 with #274 can balloon into another survivor
  campaign. Boundary now limits #261 to evidence-backed disposition unless new
  #274 proof creates a narrow must-fix target.
- Folded blocker: #274 is bug-class; the plan requires debug/root-cause before
  implementation.
- Folded blocker: broad proof can be wasted if run before the slice is stable.
  Verification plan uses focused checks first and final broad proof only after
  the mutation set is locked.
- Over-worry not folded: automatic merge proposal did not include #261 with
  #274. The user explicitly selected the bundle, and the plan carries the
  boundary that makes it tractable.
- Provenance: same-agent Before-phase critique from the selected chunk, live
  issue reads, prior #273/#261 goal, quality latest, and recent-lessons artifact.

## Off-Goal Findings

- The mutation summary can still report a missing JS JSON artifact after an
  upstream sample failure. This is deferred unless the post-fix workflow still
  fails or keeps producing misleading comments.
- A broader pre-sample validation-binary setup hook for generated mutation
  workflow templates may be useful, but it is not required for #274.

## Final Verification

- PASS: `python3 -m pytest -q
  tests/quality_gates/test_quality_mutation_testing.py` (39 passed).
- PASS: `python3 scripts/check_spec_evidence_durability.py --repo-root .`.
- PASS: `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/scripts/validate_debug_artifact.py --repo-root .`.
- PASS: `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/skills/issue/scripts/issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 274 --classification bug --body-file charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md --repo-root .`.
- PASS: `python3 scripts/run_slice_closeout.py --repo-root .
  --verification-lock` completed after sync, docs, markdown, secrets, workflow,
  adapter, packaging, critique, seam-risk, ruff, length, attention visibility,
  broad pytest, and agent-browser orphan checks.
- Advisory warnings: `check_python_lengths.py` reported four pre-existing
  advisory file-length warnings and exited 0.
- NOT RUN: post-fix GitHub Actions mutation workflow; remote proof remains
  pending until publication.

## User Verification Instructions

Inspect the final carrier commit/PR body or issue closeout artifact for the
#274 closeout language and #261 disposition. After publication, verify #274
closes on GitHub and watch the next mutation workflow before claiming remote
recovery.

## Auto-Retro

- Latest issue comments can be downstream symptoms; use workflow job step state
  to find the earliest failing component before changing reporters or thresholds.
- Durable debug artifacts must mark gitignored reproduction paths with
  `<!-- reproduction-source -->` on the same line as the path.
- Fresh-eye review was useful for distinguishing must-fix closeout integrity
  from valid-but-deferred workflow template generalization.

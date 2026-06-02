# Achieve Goal: #274 + #261 mutation regression and standard decision

Status: draft
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`.
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

- #274 comes first. Treat the latest GitHub issue body as the source of truth:
  changed-line blockers are in
  `skills/public/handoff/scripts/chunked_routing_parser.py` and
  `skills/public/handoff/scripts/parse_handoff_entries.py`; sampled survivors
  are in `scripts/portable_artifact_lib.py`; StrykerJS survivors are advisory
  because that slice already passes.
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
| 0 | Shape #274 + #261 goal | User selected the merged order and invoked achieve | Goal artifact passes `check_goal_artifact.py --pursue-ready`; consequential defaults are visible before activation | in progress |
| 1 | Debug and fix #274 live mutation regression | Mainline mutation gate trust is the first blocker and unlocks cleaner #261 policy judgment | Root-cause artifact; focused tests; changed-line proof for handoff parser/CLI wrapper files; survivor proof for portable artifact helper if still live | planned |
| 2 | Decide bounded #261 mutation-standard disposition | User asked to bundle #261 after #274, but not as an exhaustive survivor campaign | Evidence-backed close/defer decision; comment or closeout text names remaining equivalent/low-value/policy residue | planned |
| 3 | Verify, critique, and stage issue closeout | Repo closeout requires synchronized surfaces, critique, proof, and issue discipline | Changed-surface obligations; final validation; fresh-eye critique; carrier commit/PR text with #274 closeout and #261 disposition | planned |

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

## Slice Log

No slices executed yet - this goal is a `draft` pending `/goal` activation.

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

N/A - none yet.

## Final Verification

N/A - not run yet; goal is in draft before activation.

## User Verification Instructions

After activation and completion, inspect the final carrier commit/PR body or
issue closeout artifact for the #274 closeout language and #261 disposition.
Before activation, verify this plan matches the intended scope.

## Auto-Retro

N/A - not run yet; goal is in draft before activation.

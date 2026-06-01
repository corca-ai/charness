# Achieve Goal: #273 + #261 mutation gate recovery

Status: complete
Created: 2026-06-01
Activation: `/goal @charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 3 closeout active.
- Next action: run final validation and resolution critique, then publish a
  carrier that closes #273 and comments the #261 leave-open disposition.
- Verification cadence: cheap focused tests before commits; targeted mutation or
  mutation-selection proof at slice boundaries; broad read-only quality and
  issue closeout verification at final.
- Slice review packet: intent, changed files, expected mutation/coverage
  invariant, tests/proof, non-claims, and reviewer questions before critique.
- History boundary: keep this frame current; move completed detail to `## Slice
  Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve the live mutation-test regression tracked by #273 and handle #261 in the
same mutation-gate recovery run: restore changed-line/mutation-selection proof on
`main`, kill or explicitly classify the relevant sampled survivors, and close or
leave #261 with a concrete policy disposition rather than a vague carry-forward.

## Non-Goals

- Do not lower mutation score, changed-line, or selection thresholds.
- Do not chase known equivalent mutants already named in #261 as if they were
  killable product defects.
- Do not redesign the whole mutation framework unless local proof shows the gate
  itself is misreporting.
- Do not include #184 or product-success metric work.
- Do not cut a release or bump plugin versions.

## Boundaries

- In scope for #273: current GitHub issue state, latest mutation failure comment,
  changed-line proof targets, selected survivor samples, and the tests/scripts
  needed to make those targets honest.
- In scope for #261: coordination-cues survivor triage and the equivalent or
  low-value survivor policy boundary needed to make the issue closable or
  explicitly deferred.
- Treat GitHub as source of truth for issue state; local handoff text is only the
  pickup route.
- Stop before filing new sibling issues or reducing required proof without user
  approval.

## User Acceptance

- `#273` is no longer a live mutation-regression issue after the carrier is
  pushed, either via auto-close keywords or verified manual fallback.
- `#261` has a concrete disposition: closed with implemented proof/policy, or
  left open with a narrow verified comment naming the remaining policy decision.
- Changed-line blockers named by the latest #273 failure are covered or
  otherwise no longer selected as blocking misses.
- Any surviving mutants left in scope are named as equivalent, low-value policy
  residue, or deferred with evidence.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- Focused pytest for touched helpers and issue-targeted tests.
- `python3 -m py_compile` or `ruff check` for touched Python scripts when
  applicable.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after implementation.

### High-Confidence Checks

- Targeted mutation-selection or mutation-sample proof for the changed files
  involved in #273 and the #261 coordination-cues surfaces.
- `python3 scripts/run_slice_closeout.py --repo-root .` if the slice spans
  scripts, skills, tests, and artifacts.
- Final `./scripts/run-quality.sh --read-only`, unless an equivalent documented
  substitute is required by runtime cost.
- Fresh-eye resolution critique before closeout.

### External Or Live Proof

- Read #273 and #261 through `gh` before closeout.
- Publish a carrier commit with `Close #273` and the correct #261 close/defer
  language.
- Verify GitHub closeout state after push or manual fallback.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Shape combined goal and source context | User selected chunks 4 and 5 together; stale handoff goal text must not steer implementation | Goal passes pursue-ready; #273/#261 current GitHub state read; causal review running | done |
| 1 | Fix #273 live mutation regression | Mainline mutation gate trust is the first blocker | Focused tests cover changed-line targets; targeted mutation-selection proof no longer reports #273 blockers | done |
| 2 | Disposition #261 survivor/policy boundary | The user explicitly asked to bundle it with #273 | Non-equivalent survivor triage or explicit policy artifact/comment; issue state decision recorded | done |
| 3 | Sync, verify, critique, and publish | Repo closeout requires synchronized surfaces, critique, commit, and issue verification | Changed-surface obligations satisfied; quality proof; critique; carrier commit and GitHub verification | in progress |

## Coordination Cues

- Routing: `find-skills` recommended `issue`; combined execution uses `achieve`
  as the goal scratchpad and `issue` for GitHub source/closeout.
- Gather: n/a - source context is GitHub issues read through the issue backend,
  not an external document imported into the repo.
- Release: n/a - no release surface is planned.

## Slice Log

### Slice 0: Shape combined mutation goal

- Objective: Convert the selected `chunk-4 + chunk-5` pickup into one auditable
  goal.
- Current evidence: `gh issue view 273` and `gh issue view 261` were read on
  2026-06-01; latest #273 comment reports failure on `aff563f` with
  `scripts/host_log_probe_lib.py` changed-line blockers and
  `scripts/portable_artifact_lib.py` survivors.
- Verification: pending pursue-ready check after this shaping edit.
- Non-claims: no code fix has been designed or implemented yet.

### Slice 1: #273 latest blocker and survivor fix

- Objective: Cover the latest #273 changed-line blockers and remove the sampled
  `portable_artifact_lib.py` survivor shape.
- What changed so far: `scripts/portable_artifact_lib.py` no longer carries the
  redundant exact-`path` branch, avoids an `and` guard for path lists, and uses a
  length guard for root-home handling. Tests now assert path-key detection,
  non-path list preservation, root-home behavior, relative goal-path missing and
  absent states, malformed host metric window fields, and non-string Codex
  session paths.
- Verification so far: `python3 -m pytest -q tests/test_portable_artifact_lib.py
  tests/quality_gates/test_retro_host_log_probe.py` passed, 17 tests;
  `python3 -m py_compile scripts/portable_artifact_lib.py
  scripts/host_log_probe_lib.py` passed; `ruff check
  scripts/portable_artifact_lib.py tests/test_portable_artifact_lib.py
  tests/quality_gates/test_retro_host_log_probe.py` passed;
  `python3 scripts/check_python_lengths.py --repo-root . --paths ...` passed;
  packaging validators and doc-link check passed after plugin sync.
- Changed-line proof: `python3 scripts/check_changed_line_mutation_coverage.py
  --repo-root . --base-sha 36b2c7880331a4942dbd7521dc9cdfbc1d5f95c3
  --head-sha 8dbfdae` passed after a full mutation-gate coverage probe:
  `blocking: []`, changed pool file `scripts/portable_artifact_lib.py`.
- Latest #273 scheduled-range proof: reusing the generated coverage report,
  `python3 scripts/check_changed_line_mutation_coverage.py --repo-root .
  --base-sha dbd9f8a449119451df6e30c201811ef6ce940551 --head-sha
  aff563f17b204ee120bde875cec9a0524d0ba27a --reuse-coverage` passed with
  `blocking: []`, including `scripts/host_log_probe_lib.py` in the changed
  pool.
- Commit: `8dbfdae Harden mutation gate helper coverage`.

### Slice 2: #261 survivor and policy disposition

- Objective: Resolve the selected chunk's #261 portion without re-paying an
  already-run survivor campaign or silently deciding a broader mutation policy.
- What changed: No code changed in this slice. The existing scoped survivor
  proof and critique were re-read; #261 remains open specifically for the
  equivalent/low-value mutation-standard policy boundary.
- Verification: `git merge-base --is-ancestor 765f5d4 HEAD` and
  `git merge-base --is-ancestor 765f5d4 origin/main` both passed, proving the
  mechanical survivor-hardening commit is already present locally and upstream.
  `python3 scripts/check_mutation_score.py --repo-root . --stats
  reports/mutation/coordination-cues-dump.jsonl --sample-manifest
  reports/mutation/nonexistent-sample.json` re-rendered 514/514 executed, 467
  killed, 47 survived, 90.9% reachable score versus 80% threshold; command exit
  was non-zero only because the intentionally nonexistent sample manifest and
  uncovered sampled mutants are blocking signals in that archived proof context.
  `python3 -m pytest -q tests/quality_gates/test_goal_coordination_floors.py
  tests/quality_gates/test_goal_disposition_gate.py
  tests/quality_gates/test_goal_head_freshness.py
  tests/quality_gates/test_achieve_before_activation.py` passed, 85 tests.
- Critique/provenance: prior fresh-eye critique
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`
  says the remaining survivors are defensibly equivalent or low-value and the
  policy decision should stay open.
- Disposition: close #273 after publication; leave #261 open with a verified
  comment that points to the existing mechanical hardening and this goal's
  policy non-claim.

### Slice 3: Final validation and carrier preparation

- Objective: Prove the bundled fix, satisfy issue closeout contracts, and
  prepare publication.
- What changed: Added debug, critique, retro, probe, and issue-carrier
  artifacts; regenerated `charness-artifacts/debug/seam-risk-index.json`.
- Verification: `issue_tool.py validate-closeout-draft` passed for #273 as
  bug-class with carrier `pr-body`; `validate_debug_artifact.py` passed;
  `build_debug_seam_risk_index.py --check` passed;
  `validate_critique_artifacts.py --all` passed; doc links, command docs,
  markdown, and secret checks passed; final `./scripts/run-quality.sh
  --read-only` passed 69/69 in 48.0s.
- Critique: resolution critique is persisted at
  `charness-artifacts/critique/2026-06-01-273-261-mutation-gate-recovery-resolution.md`
  and its Act Before Ship findings were fixed before completion.

## Context Sources

- GitHub issue: https://github.com/corca-ai/charness/issues/273
- GitHub issue: https://github.com/corca-ai/charness/issues/261
- Handoff route: `docs/handoff.md`
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`
- Quality posture: `charness-artifacts/quality/latest.md`

## Interview Decisions

- Combined scope: user selected chunks 4 and 5 together; chosen as one mutation
  recovery goal rather than separate #273 then #261 sessions.
- #261 policy handling: include disposition in this goal, but do not silently
  invent a new equivalent-mutant gate policy or file new issues without approval.
- Proof cost: use focused tests and targeted mutation proof before broad quality;
  reserve the broad gate for final closeout.

## Plan Critique Findings

- Causal review: fresh-eye read-only subagent completed. Classification: #273 is
  bug-class; #261 is mixed bug/decision-needed after #265. Root model: support
  helper branches were treated as sufficiently covered by feature tests and
  broad quality, while mutation/changed-line proof observes exact branch and
  mutant boundaries. Bundled now: #273 latest `host_log_probe_lib.py` blockers
  and `portable_artifact_lib.py` survivors. Defer/decide explicitly: broad
  equivalent-mutant exclusion policy.
- Known risk folded into plan: #261 is partly a policy boundary, so closing it
  may require an explicit defer comment rather than only more tests.

## Off-Goal Findings

N/A - none yet.

## Final Verification

- PASS: focused pytest for `tests/test_portable_artifact_lib.py` and
  `tests/quality_gates/test_retro_host_log_probe.py` (17 passed).
- PASS: changed-line classifier for new commit range reported `blocking: []`.
- PASS: changed-line classifier for latest #273 scheduled failure range,
  reusing refreshed coverage, reported `blocking: []`.
- PASS: #261 coordination/disposition focused tests passed (85 passed) and
  prior scoped survivor proof remains 90.9% reachable score.
- PASS: final `./scripts/run-quality.sh --read-only` reported 69 passed, 0
  failed, total 48.0s.
- PASS: issue closeout draft validation for #273.
- PASS: debug artifact, debug seam-risk index, critique artifacts, markdown,
  command docs, docs links, and secrets validators.
- Retro: charness-artifacts/retro/2026-06-01-273-261-mutation-gate-recovery.md
- Host log probe: charness-artifacts/probe/2026-06-01-273-261-mutation-gate-recovery.json
- Disposition review: charness-artifacts/critique/2026-06-01-273-261-mutation-gate-recovery-resolution.md
- Non-claims: remote CI is not proven until after push; #261 remains open; no
  release was cut.

## User Verification Instructions

- Inspect the carrier:
  `charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md`.
- After push, verify #273 is closed and #261 has the leave-open comment.
- Optionally re-run `./scripts/run-quality.sh --read-only`.

## Auto-Retro

- Waste: closeout-shape iteration around issue carrier fields and debug artifact
  shape. Existing validators caught it before publication.
- Critical decisions: fixed #273 with focused branch proof; left #261 open as a
  policy boundary; used the mutation gate's changed-line classifier for proof.
- Next improvements: validate carrier/debug evidence immediately after adding
  required fields, before expanding final prose.
- Retro dispositions: applied - issue closeout validation, debug validation,
  seam-risk index validation, and resolution critique were all run before goal
  completion; no new gate is needed.

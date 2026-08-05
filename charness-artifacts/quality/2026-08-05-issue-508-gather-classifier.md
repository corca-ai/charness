# Quality Review
Date: 2026-08-05
Title: Issue #508 gather classifier token-boundary repair

## Scope

Target boundary: the support web-fetch classifier's login-marker precision,
its checked-in plugin mirror, and the public gather persistence/no-write seam.

Ambient repo findings: standing skill ergonomics reports 16 heuristic findings
across 22 skills, mostly host-surface references; those are advisory and not a
target finding for this classifier slice.

## Current Gates

Focused classifier/gather proof passed 39 tests. The final verification-locked
closeout passed the standing read-only suite with 0 failures, and its fresh
changed-line mutation consumer passed against base
`05726f15c1fc9effd2e06e72ca9429d57f26f1ee` and head `2f3fe398`; one changed
mutation-pool file was analyzed with no blocking files. Ruff, dup-ratchet,
source/plugin parity, critique validators, debug/risk validators, probe
validators, and `git diff --check` passed. No Cautilus evaluation was run.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: `run-quality-read-only` latest 50.6s / recent median 54.1s, within its 420s budget; this is a measured signal, not a performance claim about the classifier.
- coverage gate: final verification-locked closeout passed the standing read-only suite and the fresh changed-line mutation consumer; base `05726f15c1fc9effd2e06e72ca9429d57f26f1ee`, head `2f3fe398`, one changed pool file, zero blocking files.
- evaluator depth: deterministic-gates-only; no Cautilus grant, live provider, or installed-host behavior claim is in scope.

## Healthy

- Normalized visible-text matching prevents `design intent` and title prose from
  becoming login blockers while preserving markup-split and standalone markers.
- The complete marker matrix covers single-hyphen/whitespace forms, embedded
  English/Korean negatives, canonical `matched_signals`, and precedence.
- Gather persistence is proven with an explicit extracted-content request, and
  a genuine login blocker remains no-write. Source/plugin mirrors are identical.

## Weak

- All behavior evidence is local source-tree fixture proof, not live or
  installed-host behavior.

## Missing

- Remote CI, provider roundtrip, installed plugin behavior, live named-URL
  acquisition, and Cautilus behavior remain unproven.

## Deferred

- Page-level authentication signals, provider-specific vocabularies, browser
  fallback, and a broad public-web auth corpus require a recorded recurrence or
  operator need before expansion.

## Advisory

- structural review result: artifact=`charness-artifacts/critique/2026-08-05-issue-508-resolution-critique.md`; existing focused tests, standing quality, and the two-round proof-surface critique are sufficient; no new universal classifier gate is justified by this one recurrence.
- prose review result: scope_status=scanned; finding_status=heuristics_present; prose_review_status=required; checked_skill_count=22; heuristic_finding_count=16; host_surface_reference_count=93; support/gather trigger boundaries and progressive disclosure were unchanged, and the ergonomics inventory's host-surface hits are ambient portability prompts rather than this target's defect (command: `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`).
- dup-ratchet result (command: `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary`): reported `status: clean`,
  `new_code_family_count: 0`, and no hard or boy-scout block.

## Delegated Review

- Delegated Review: executed — two unnamed bounded fresh-eye code rounds ran
  with distinct reviewer contexts; round 1 found matrix/packet gaps, round 2
  found separator overreach, and the final repair is explicitly accepted-
  unreviewed under the two-round cap. A separate closeout-claims review then
  returned PASS for the local carrier/goal/handoff record; remote publish and
  GitHub CLOSED readback remain pending.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): executed through quality planning; the only new duplicate
  family was removed and the dirty mutation warning remains explicit.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- `pytest -q tests/test_web_fetch_route_and_classify.py tests/test_web_fetch_support.py` — 39 passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --base --verification-lock --refresh-broad-pytest-proof --produce-mutation-coverage --mutation-coverage-command "pytest -q tests/test_web_fetch_route_and_classify.py tests/test_web_fetch_trace_quality.py"` — completed; standing suite passed and changed-line mutation consumer passed.
- `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha 05726f15c1fc9effd2e06e72ca9429d57f26f1ee --head-sha HEAD --coverage-json reports/mutation/test-coverage.json --reuse-coverage --require-fresh-coverage` — `ok: true`, 1 changed pool file, 0 blocking files.
- `ruff check skills/support/web-fetch/scripts/classify_fetch_response.py tests/test_web_fetch_route_and_classify.py tests/test_web_fetch_support.py` — passed.
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary` — clean, 0 new code families.
- source/plugin classifier and gather `cmp -s`, `python3 scripts/validate_critique_artifacts.py`, `python3 scripts/validate_debug_artifact.py`, risk planner, and `git diff --check` — passed.

## Recommended Next Quality Moves

- active — capability_needed=remote CI and GitHub readback; next_center=the final publish boundary; transformation=run the gated publish when authorized, read remote CI through a distinct observer, and verify the issue carrier through the adapter; proof_boundary=remote CI plus `verify-closeout --expect-state CLOSED`; enforcement_posture=existing-gate-reuse.
- passive — because changed-line mutation proof is complete; capability_needed=fresh focused coverage only if the source mutation pool changes; next_center=the current proof head `2f3fe398`; transformation=preserve the locked producer/consumer evidence; proof_boundary=post-commit mutation consumer; enforcement_posture=existing-gate.
- passive — capability_needed=live provider recurrence; next_center=recorded public response; transformation=expand marker vocabulary only when a real recurrence justifies it; proof_boundary=provider roundtrip; enforcement_posture=no-gate because local fixtures cannot establish that need.

## History

- [prior proof-path learning review](history/2026-07-19-portable-proof-path-learning-review.md)

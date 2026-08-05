# Quality Review
Date: 2026-08-05
Title: Issue #491 semantic-reference decision quality record

## Scope

Target boundary: the #491 semantic-reference decision, its first-reader
references, source/plugin mirrors, and the narrow regression tests.

Ambient repo findings: the skill ergonomics inventory reports 16 heuristic
packages and 93 host-surface hits; those are advisory and outside this slice.

## Current Gates

Focused input-channel and achieve-reference proof passed 37 tests, and the D47
measurement/consumption suite passed 73 tests. Source/plugin parity passed for
both references and `upsert_goal.py`; `git diff --check` is clean. The broad
read-only quality gate passed 85 checks with 0 failures; the verification-locked
closeout passed the changed-line mutation consumer locally. Independent remote
Quality Core run `31008443698` passed both Core deterministic gates and
changed-line mutation coverage for carrier commit
`05726f15c1fc9effd2e06e72ca9429d57f26f1ee`. The prepared critique packet and
resolution critique are present.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`;
  timing capture is missing for this docs-and-focused-tests slice. <!-- reproduction-source -->
- runtime hot spots: not applicable; no standing gate or runtime policy changed.
- coverage gate: broad read-only quality passed 85/0; verification-locked local
  and independent remote changed-line mutation coverage both passed for the
  carrier commit.
- evaluator depth: deterministic-gates-only; no Cautilus grant or live agent
  behavior claim is in scope.

## Healthy

- The actual first-reader `append_slice_log.py` example now routes prose through
  a quoted JSON heredoc and `--fields-file`.
- The semantic question records invariant, owner, instance, counterexample,
  bounded candidate scope, and honest non-applicability/defer outcomes.
- The current bootstrap report contract is kept separate from historical
  `refilled_subkeys` wording superseded by #507.

## Weak

- The reviewer-owned question does not prove whole-repository reference
  synchronization or reviewer uptake; its scope and non-claims are explicit.
- The focused test intentionally protects one reader-facing command shape, not
  every semantic relationship in the repository.

## Missing

- Installed-host readback, provider roundtrip, and live-agent behavior remain
  unproven and outside this slice's contract.
- No mechanical full-corpus reference manifest or literal semantic matcher;
  current evidence does not justify one.

## Deferred

- A future recurrence with a stable owner-to-reference mapping may justify a
  narrow mechanical control and a measured false-fire review.
- Host rendering and future reviewer uptake require separate observation.

## Advisory

- structural review result: existing gate reuse is sufficient; the issue is judgment-bound across heterogeneous claim families, so no new universal gate is justified (command: `plan_quality_run.py --repo-root . --detail`).
- prose review result: `inventory_skill_ergonomics.py --summary` reports
  `scope_status: scanned`, `finding_status: heuristics_present`,
  `prose_review_status: required`, `checked_skill_count: 22`,
  `heuristic_finding_count: 16`, and `host_surface_reference_count: 93`; these
  are ambient portability prompts, not this slice's repair target.
- quality posture (artifact: `charness-artifacts/critique/2026-08-05-issue-491-resolution-critique.md`): keep the reviewer-owned question and narrow reader test; do not promote local literal assertions into a semantic meta-gate.

## Delegated Review

- Delegated Review: executed — four unnamed bounded reviewers ran in each of
  two rounds. Round one found the stale append example; round two approved the
  repaired example but found the slug-coercion contradiction and overbroad
  wording. Parent repairs after round two are explicitly accepted-unreviewed
  under the two-round cap. Full record:
  `charness-artifacts/critique/2026-08-05-issue-491-resolution-critique.md`.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not_applicable — no slow-gate policy or runtime scope is
  changed.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- python3 -m pytest -q tests/quality_gates/test_achieve_before_activation.py tests/quality_gates/test_append_slice_log_input_channel.py tests/quality_gates/test_upsert_goal_input_channel.py — 37 passed.
- python3 -m pytest -q -n 0 tests/quality_gates/test_inventory_consumption.py tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py tests/test_inventory_marker_rule_measurement.py — 73 passed.
- `./scripts/run-quality.sh --read-only` — 85 passed, 0 failed after the quality-record closeout update; the earlier pre-closeout run was 84 passed, 0 failed with the changed-line mutation consumer UNPROVEN.
- source/plugin `cmp -s` parity for repaired references and helper.
- `git diff --check`.

## Recommended Next Quality Moves

- active — capability_needed=issue-closeout; next_center=#508 live read and
  gather-classifier decision; transformation=bind the login-wall JTBD to the
  current goal; proof_boundary=issue adapter readback plus issue-specific
  behavior channel; enforcement_posture=advisory.
- passive until recurrence evidence exists — capability_needed=recurrence evidence; next_center=stable
  owner-to-reference mapping; transformation=measure false-fire cost before
  proposing a narrow matcher; proof_boundary=another real semantic escape;
  enforcement_posture=no-gate because current heterogeneous evidence cannot
  support a universal predicate.

## History

- [prior cross-track proof review](history/2026-07-19-portable-proof-path-learning-review.md)

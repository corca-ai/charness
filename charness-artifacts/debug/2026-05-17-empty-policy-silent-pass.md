# Empty Policy Silent Pass Debug
Date: 2026-05-17

## Problem

`skill_ergonomics_gate_rules: []` appeared often enough to expose a broader
pattern: an empty policy, rule list, or probe list can disable enforcement while
the standing gate still exits 0 and hides the reason.

## Correct Behavior

Given a repo has a discoverable surface, when an empty config disables a quality
or skill-structure gate, then the validator should report that state as an
explicit warning or weak finding.

Given a standing quality phase exits 0, when its output contains `WARNING`,
`WARN`, `WEAK`, or `ADVISORY` lines, then `run-quality` should replay the phase
log even though the phase passed.

## Observed Facts

- `.agents/quality-adapter.yaml` sets `skill_ergonomics_gate_rules: []`.
- Before this fix, `validate_skill_ergonomics.py --json` returned
  `rules: []`, `checked_skills: []`, `violations: []`, and exited 0 without a
  structured warning.
- The repo-root wrapper `scripts/validate_skill_ergonomics.py` failed only on
  `violations`, so configured-rule discovery errors could pass through the
  wrapper.
- `scripts/run-quality.sh` replayed phase logs only on failure or explicit
  verbose mode, so even valid warning output from a passing phase would be
  hidden in normal operation.
- `inventory_skill_ergonomics.py --json` found 22 skills; after the setup
  refactor, `setup` is no longer flagged, but eight public skills still show
  `long_core` pressure and several others show mode/option pressure.
- A sibling scan found existing warnings for empty adapter fields in
  announcement, impl, find-skills, quality, and retro resolver paths. Those are
  bootstrap visibility signals, not standing quality gates.
- A delegated sibling scan found one additional live sibling:
  `requested_review_commands: []` in `release` returned `status: ok` without
  a configuration status or warning.
- Fresh-eye critique found the same empty-policy class when
  `skill_ergonomics_skill_paths` is explicitly configured but resolves no
  non-vendored skills while rules are empty.

## Reproduction

Before the fix:

```bash
python3 scripts/validate_skill_ergonomics.py --repo-root . --json
CHARNESS_QUALITY_LABELS=validate-skill-ergonomics ./scripts/run-quality.sh
```

The validator passed with no warning payload, and the quality runner printed
only a green phase line.

## Candidate Causes

- Empty rule lists were treated as intentional opt-out without proving that a
  user or adapter had made a conscious decision.
- The validator considered only failure conditions and had no warning channel
  for disabled enforcement over a discoverable surface.
- The root wrapper's exit policy drifted from the helper by ignoring discovery
  errors.
- The quality runner optimized green output too aggressively and hid pass-time
  attention signals.
- Several skill resolver helpers already emit warnings, but those warnings are
  bootstrap-local unless a caller chooses to inspect them.

## Hypothesis

If empty skill ergonomics rules emit a structured warning when skills are
discoverable, and if `run-quality` replays pass-time attention output, then the
same disabled-gate pattern becomes visible without turning every advisory into
a hard failure.

## Verification

Focused proof executed:

- `python3 scripts/validate_skill_ergonomics.py --repo-root .`
- `python3 scripts/validate_skill_ergonomics.py --repo-root . --json`
- `CHARNESS_QUALITY_LABELS=validate-skill-ergonomics ./scripts/run-quality.sh`
- `pytest -q tests/quality_gates/test_skill_ergonomics_gate.py tests/quality_gates/test_quality_runner.py::test_run_quality_replays_passing_attention_logs tests/quality_gates/test_quality_runner.py::test_run_quality_keeps_passing_non_attention_logs_quiet`
- `pytest -q tests/quality_gates/test_release_publish.py::test_requested_review_gate_warns_when_commands_are_empty tests/quality_gates/test_release_publish.py::test_requested_review_gate_blocks_unavailable_release_record tests/quality_gates/test_release_publish.py::test_requested_review_gate_allows_explicit_waiver`

The local repo now reports a `skill_ergonomics_gate_rules_empty` warning with
22 skills present, and `run-quality` replays that warning on a passing phase.

## Root Cause

The root cause was a missing intermediate severity between "hard violation" and
"nothing to check." `skill_ergonomics_gate_rules: []` was a valid low-noise
default, but the validator did not distinguish "no relevant surface exists"
from "a relevant surface exists but enforcement is disabled."

That combined with the quality runner's quiet PASS policy. Even if a validator
did emit a pass-time warning, the default runner would suppress it, so the
operator-visible result still looked like an unqualified pass.

## Detection Gap

- skill ergonomics validator | empty rules with discovered skills produced no
  warning | emit `skill_ergonomics_gate_rules_empty` and preserve exit 0.
- skill ergonomics explicit paths | empty rules with configured paths that
  resolve no non-vendored skills produced no warning | emit
  `skill_ergonomics_requested_paths_empty`.
- root wrapper | discovery errors from configured rules were not fatal through
  the repo-root entrypoint | mirror helper exit policy for `discovery_errors`.
- quality runner | pass-time attention output was hidden | replay logs with
  `WARNING`, `WARN`, `WEAK`, or `ADVISORY` lines.
- release requested-review gate | empty requested-review commands produced a
  bare `ok` status | emit `configuration_status: not_configured` and a warning.
- all-skill health gate | advisory inventory found core pressure but empty
  rules kept it non-enforced | keep warning visible; defer rule opt-in or
  broader refactors to a priced follow-up.

## Sibling Search

- Mental model: an empty list was treated as benign configuration instead of a
  potentially disabled enforcement surface.
- same layer: `runtime_budget_lib.py` already emits `WEAK`/`WARN` for missing
  budgets or samples; the runner-level replay fix now prevents those from being
  hidden when they occur.
- same layer: `retro/scripts/check_auto_trigger.py` already distinguishes
  missing from explicitly empty trigger config and includes remediation; no
  patch needed.
- same layer: adapter resolvers for announcement, impl, find-skills, quality,
  and retro already emit warnings for empty-but-relevant setup fields; no
  standing-gate patch needed unless those bootstrap warnings need promotion.
- same layer: `release/scripts/check_requested_review_gate.py` now
  distinguishes empty requested-review command config from a fully configured
  `ok` result.
- adjacent layer: `validate_cautilus_call_provenance.py` prints "nothing to
  check" when no `.cautilus/runs/` exists; that is not a disabled policy over a
  present surface, so it is a false positive for this incident.
- adjacent layer: HITL `rules: []` is an initial review-state artifact, not a
  quality enforcement rule list; false positive.
- adjacent layer: release fresh-checkout probes report `not_configured` into
  release artifacts; this is visible but may deserve a future release-policy
  warning if installable releases continue without probes.

## Seam Risk

- Interrupt ID: empty-policy-silent-pass
- Risk Class: contract-freeze-risk
- Seam: adapter policy defaults versus standing gate enforcement visibility
- Disproving Observation: focused tests fail if empty skill ergonomics rules
  stop emitting a warning, if wrapper discovery errors pass, or if
  `run-quality` hides a passing `WARNING` line.
- What Local Reasoning Cannot Prove: whether every non-standing bootstrap
  warning should be promoted into a standing quality phase.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep empty-policy states distinguishable from absent-surface states. Validators
that intentionally pass on missing config should still expose `WARNING`,
`WARN`, `WEAK`, or `ADVISORY` when a relevant surface exists and enforcement is
disabled. The runner owns replaying those pass-time attention lines so future
warning channels do not become invisible by default.

Related prior incident:
`charness-artifacts/debug/2026-05-11-issue-145-script-silence-closeout.md`.

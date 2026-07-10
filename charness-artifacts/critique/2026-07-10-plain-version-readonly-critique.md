# Plain Version Read-only Code Critique
Date: 2026-07-10

## Execution

- Two fresh-eye code/behavior angles and one separate parent counterweight
  reviewed the already-landed plain-version optimization before release lock.
- Packet Consumed: `charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.md`
- Target: `references/code-critique.md`

## Decision Under Review

Keep plain `charness version` and exact top-level `charness --version` as fast,
read-only manifest probes while detailed `--verbose`, `--json`, and `--check`
modes retain provenance, state persistence, and explicit release checking.

## Diff Scope

The plain-mode early return in `cmd_version`, the matching state-recording guard
in `main`, and focused version-surface regressions.

## Capability at Stake

The conventional version probe should be predictable and side-effect free
without removing the richer installation provenance and update-inspection modes.

## Angles

- Jackson/Raskin judged the problem/interface boundary and whether a read-only
  probe is more humane than an opportunistic state/update side effect.
- Weinberg/Gawande traced version-state consumers, installed/source behavior,
  alias normalization, detailed modes, and regression strength.
- Counterweight challenged weak latency framing and a vacuous bootstrap mock.

## Findings

- No blocker: the guard applies only to plain version mode; verbose/json/check
  still execute the existing provenance and state-writing path.
- Skipping opportunistic update notice in plain mode is intentional; `--check`,
  doctor, and update own explicit update behavior.
- The 4--16% startup improvement is secondary. The stronger contract is that
  a ubiquitous information probe does not create or rewrite host-local state.
- The proposed `resolve_repo_python` mock did not kill the old behavior because
  old plain version never called it; it is removed in favor of direct no-write
  and byte-unchanged state assertions plus alias coverage.

## Counterweight Triage

### Act Before Ship

- None.

### Bundle Anyway

- Add exact `--version` alias no-write coverage and remove the vacuous bootstrap
  probe test; preserve existing-state bytes as well as absence.

### Over-Worry

- Do not restore undocumented opportunistic notice/provenance side effects to
  plain mode or add missing-repo behavior tests unrelated to this change.

### Valid but Defer

- None beyond the broader parser/import optimization already excluded from S2.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/test_version_surface.py | action: fix | note: replace vacuous bootstrap mock with direct plain and alias read-only proof
- F2 | bin: over-worry | evidence: strong | ref: charness:5233 | action: document | note: plain version intentionally skips opportunistic update notice and provenance writes
- F3 | bin: over-worry | evidence: moderate | ref: charness:3748 | action: document | note: missing explicit repo behavior is pre-existing and outside this speed slice

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: spawn surface accepted requested fields; execution metadata was not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: root CLI version dispatcher and packaging manifest.
- Consumer: scripts/operators probing version and detailed provenance/update modes.
- Owning surface: `charness` plus `tests/charness_cli/test_version_surface.py`.
- Verdict: owned-correctly

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` environment/state leakage lessons
support keeping a read-only query free from hidden host-local writes.

## Capability Gap

None; the current CLI modes already separate plain information, detailed
provenance, and explicit update checking.

## Deliberately Not Doing

- No parser rewrite, lazy urllib, update-policy redesign, or new version mode.

## Pre-Merge Action

Apply the focused test correction, run version and managed-release regressions,
then include this decision in the final quality record.

## Next Move

Commit the corrected tests and critique record, then resume S3 verification.

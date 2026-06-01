# #273 + #261 Mutation Gate Recovery Carrier

Date: 2026-06-01
Repo: corca-ai/charness
Goal: `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`

## Carrier Scope

Close:

- #273 mutation test regression on main

Leave open intentionally:

- #261 mutation-standard policy for equivalent or low-value coordination-cues
  survivors

## Evidence

- Focused implementation commit: `8dbfdae Harden mutation gate helper coverage`
- #273 latest scheduled failure range:
  `dbd9f8a449119451df6e30c201811ef6ce940551..aff563f17b204ee120bde875cec9a0524d0ba27a`
- Local changed-line proof for the new commit range:
  `scripts/check_changed_line_mutation_coverage.py` reported `blocking: []` for
  `36b2c7880331a4942dbd7521dc9cdfbc1d5f95c3..8dbfdae`
- Local changed-line proof for the latest #273 failure range, reusing the new
  coverage report: `blocking: []` with `scripts/host_log_probe_lib.py` included
  in the changed pool
- Focused tests: `tests/test_portable_artifact_lib.py` and
  `tests/quality_gates/test_retro_host_log_probe.py` passed, 17 tests
- #261 survivor disposition: prior scoped proof remains 514/514 executed, 467
  killed, 47 survived, 90.9% reachable score; prior fresh-eye critique records
  the remaining survivors as equivalent/low-value policy residue

## Close Comment

Resolved in the #273 + #261 mutation gate recovery carrier.

JTBD: restore the scheduled mutation gate's changed-line proof on `main` while
keeping #261's broader mutation-standard policy boundary explicit.

Classification: bug for #273; #261 is decision-needed after the mechanical
survivor hardening already landed.

Root cause: helper branch behavior was covered by broad feature tests but not
asserted at the exact branch and mutant-observable boundaries used by the
scheduled mutation gate.

Debug artifact:
`charness-artifacts/debug/2026-06-01-273-mutation-gate-helper-coverage.md`

Siblings: support helpers with CLI/error/path branches, subprocess-only entrypoints, duplicated parser helpers, or sampler nodeid selection | decision: bundle the latest #273 `host_log_probe_lib.py` and `portable_artifact_lib.py` surfaces; defer other helpers until they are sampled or named by the gate | proof: changed-line classifier reports `blocking: []` for the latest #273 range with refreshed coverage.

Prevention: focused tests now cover the latest changed-line blocker paths in
`host_log_probe_lib.py`, and `portable_artifact_lib.py` no longer carries the
sampled survivor branch shapes.

Critique: charness-artifacts/critique/2026-06-01-273-261-mutation-gate-recovery-resolution.md

Close #273.

Evidence:

- Goal artifact:
  `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`
- Carrier artifact:
  `charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md`
- Implementation commit: `8dbfdae Harden mutation gate helper coverage`

Scope note:

- #261 remains open for the equivalent/low-value survivor policy boundary.

## Leave-Open Comment

For #261:

```text
Leaving this open intentionally after the #273 mutation gate recovery carrier.

The mechanical survivor-hardening path is already present through `765f5d4`
and the prior scoped proof remains 514/514 executed, 467 killed, 47 survived,
90.9% reachable score. This run fixed the live #273 changed-line regression and
reconfirmed the #261 boundary: the remaining coordination-cues survivors are an
equivalent/low-value mutation-standard policy question, not a missing #273
coverage fix.

Relevant evidence:
- Goal artifact: charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md
- Carrier artifact: charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md
- Prior critique: charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md
```

## Non-Claims

- No release is part of this carrier.
- Remote CI is not claimed until observed after push.
- #261 is not closed by this carrier.

# Release scheduling code disposition

Date: 2026-09-06

The initial proof-integrity and operability reviewers returned three IDs for
two concrete defects. The parent reproduced both, repaired their owners, and
retained the typed findings. The probe observation record owns stimuli, results,
counterweight disposition, and non-claims.

The single bounded follow-up `goal805-code-release-repair` passed with no
findings in 90.6s. Parent consumed its delivered result and typed report, then
verified the packet as current before staging. Fresh-Eye Satisfaction:
worker-delivered, code review only. No third code round is needed.

- Report: `charness-artifacts/critique/workers/goal805-code-release-repair/worker-report.yaml`
- Packet SHA256: `eb089448a5e4a3b9c7b6de089bdeaac70166191a09ec742f2b9e821d99eab0eb`
- Input SHA256: `5981db108ff9b86d50bfbaf38c8779deebdc93b416707b032f5be8344ab77f6d`
- Findings identity: `49cac9c33d264692b4d1611e28a66afae65954056d22fe2ec240a70cd22be5f8`

The actual-shell newline roundtrip and existing visibility tests passed: seven
tests in 2.51s. The preceding repaired engine/orchestration selection passed
48 tests in 8.26s. Python/shell/Markdown and current code/docs length gates passed.
Canonical export was synchronized. These are scoped observations, not a broad
release pass. Integrated changed-line/broad proof, actual release invocation
counts, consumer comparison and installed behavior remain required.

The first changed-line producer found two legacy expectations outside the
initial focused selection: its receipt fixture lacked the now-required
`pytest-release` measurement, and a receipt-copy test expected disk errors to
be swallowed. Updated those fixtures to the reviewed stricter contract; copy
failure is asserted for both final and preparation runs. The focused replay
passed 12 tests in 2.70s. The failed producer yielded no coverage verdict;
changed-line proof remains pending, not waived.

The next producer passed but exposed one unmeasured changed line:
`scripts/run_quality_engine.py:325`, refusal when no exact selected
`pytest-release` gate exists. Added the renamed-gate consumer stimulus: it
passed, then failed with observed exit 0 versus required 2 when that exact
raise was temporarily replaced with `pass`. Restored the owner immediately;
`git diff` confirmed no production mutation remained. This is the requested
target-bound mutant proof, not a broad mutation score.

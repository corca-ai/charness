# Retro: sustained quality speed token release round 2
Date: 2026-06-26
Mode: session

## Context

Three-hour quality pass across bug fixes, test speed, script execution speed,
token efficiency, closeout proof, and final release preparation. The run
intentionally delayed push/release until the closeout window after the earlier
premature-release correction.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-2.md`
- Release critique:
  `charness-artifacts/critique/2026-06-26-v0-56-3-release-critique.md`
- Release notes:
  `charness-artifacts/release/v0.56.3-notes.md`
- Host log probe:
  `charness-artifacts/probe/2026-06-26-sustained-quality-speed-token-release-round-2-host-log.json`
- Final changed-line mutation consumer:
  `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha 61093b75a23813bf4995c7a8698cb1b0fde3874b --reuse-coverage --require-fresh-coverage`
  returned `ok: true`.

## Waste

- The first release-closeout producer reused a focused pytest command that
covered the newly added fallback tests but dropped coverage for older changed
files. The consumer caught this as a broad false gap.
- The attempted `&&` composition inside `--mutation-coverage-command` was parsed
as arguments to `run_standing_pytest.py`, not as shell syntax. That wasted one
closeout cycle.
- A full `python3 -m pytest -q` coverage run was started as a brute-force
fallback and then stopped after it became clear it was much slower than the
standing-runner path.
- The first release critique packet was structurally valid but too clean-tree
oriented for a 35-commit release range; the range-aware critique had to be added
explicitly.

## Critical Decisions

- Did not publish the release when the user challenged the timing; release work
was held until the actual closeout window.
- Chose to add focused fallback/defensive-path tests instead of weakening the
changed-line mutation coverage consumer.
- Used the standing pytest runner as the coverage producer after confirming the
new closeout test file was in its expanded target set.
- Kept requested-review and scenario-registry follow-ups advisory for this patch
because deterministic validators and release critique covered the release
boundary without inventing a rushed enforcement gate.

## Expert Counterfactuals

- Gawande would have made the release checklist ask for range-aware release
evidence before accepting a clean-tree release packet.
- Minto would have pushed for the release notes earlier so the operator story
was not reconstructed from commit history under time pressure.
- Raskin would have avoided the shell-chaining mistake by checking the producer's
command grammar before trying to compose commands.

## Next Improvements

- applied: added focused fallback tests for timeout/default/error branches and
  verified changed-line mutation coverage with a fresh coverage fingerprint.
- applied: added range-aware release critique and concise v0.56.3 notes before
  publish.
- applied: recorded a goal metric window before the host log probe so closeout
  metrics are scoped to this goal window.
- accepted-risk: did not add a new hard gate for advisory requested-review or
  scenario-registry follow-up in this patch; the release critique records the
  limitation and deterministic validation owns this release boundary.

## Sibling Search

No new cross-repo issue was filed. The transferable waste items were either
fixed in this repo during the run or explicitly accepted as advisory policy risk
for this patch release.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-26-sustained-quality-speed-token-release-round-2-goal-retro.md

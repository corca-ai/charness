# Run-Quality Progress Surface Critique
Date: 2026-08-09

## Decision Under Review

Whether `run-quality.sh` may emit immediate progress outside its buffered
per-phase logs without changing the gate verdict contract.

## Failure Angles

- Combined-stream observability before a slow selected gate completes.
- Requested versus actually executed scope semantics.
- Existing stdout verdict compatibility and stderr noise.
- Bash array edge cases and test process-group cleanup.

## Findings

- Act before ship: none.
- Bundle anyway: rename `scope` to `requested_scope`, because an unknown label is
  a request and not an executed check population. Applied.
- Bundle anyway: observe the `WAIT checks=1 first=... last=...` line before the
  slow fixture exits, rather than stopping after `START`. Applied.
- Bundle anyway: suppress process-lookup races while terminating the test's
  isolated process group. Applied.
- Act before ship, round 2: mixing `select()` on a raw fd with buffered text
  `readline()` could time out after Python had already read `WAIT` into its own
  buffer. The test now follows the real combined-redirect contract and polls one
  file for both lines. This capped-round repair is accepted-unreviewed; the
  current binding packet below records its exact bytes without claiming a third
  review.
- Over-worry: normalize arbitrary newlines in operator-supplied labels, restore
  POSIX `sh` portability, or treat stderr diagnostics as a stable empty stream.
  The script is Bash already, labels are operator input, and stdout continues to
  own the verdict.

## Counterweight Pass

The immediate stderr `printf` crosses the private phase-log boundary, so
`>log 2>&1` receives evidence before the slow phase finishes. `flush_phase`
guards the empty array before reading its first and last labels. The progress
text does not decide pass, fail, or unproven state, and no second review round is
owed because verdict logic did not change.

## Fresh-Eye Satisfaction

parent-delegated. One distinct read-only reviewer consumed the initial packet
and the repaired-surface packet. Round 1 reported no blocker; round 2 confirmed
the code boundary and found the buffered-reader test race above. Parent-side
reviewer-boundary fingerprints verified `verdict: clean` after both responses.

## Reviewer Tier Evidence

- Requested tier: inherited session default.
- Requested spawn fields: `fork_turns=4`; no model, reasoning-effort, or
  service-tier override was requested.
- Host exposure state: metadata-hidden
- Application state: metadata-hidden; the host delivered findings but exposed
  no provider-side model application metadata.
- Delivery state: findings-received.

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-09-run-quality-progress-final-binding-packet.json`
- Packet SHA256: `e4c878df626d8a576a074f1727249a99fa05d9ababbd301557944527620c80d3`
- Reviewer-facing packet: `charness-artifacts/critique/2026-08-09-run-quality-progress-final-binding-packet.md`
  (SHA256 `0fbd4dda322507e5aaad48597307202e29019c3b7cc981f7952cf58bc29919e7`).
- Identity SHA256: `b6d367e0f698f48de7e1b246ae01804cd6b403e9ed6eea185a56914b239bab95`
- Reviewed paths: root runner, generated plugin runner, and progress regression
  test.

## Boundary Ownership

- stderr owns non-verdict progress.
- private phase logs own non-interleaved command output.
- stdout's final quality receipt owns the verdict.
- Verdict: owned-correctly.

## Verification

- Focused runner suites: 66 passed after all review repairs.
- Generated plugin runner is synchronized from the root source.

## Next Move

Run the full quality gate with combined redirection, verify the early progress
lines and terminal summary from the retained log, then commit with the remote-CI
closeout artifacts.

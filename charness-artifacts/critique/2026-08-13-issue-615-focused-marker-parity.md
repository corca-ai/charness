# Issue 615 Focused Marker Parity Critique
Date: 2026-08-13

## Decision Under Review

Remove the focused changed-line producer's `--include-release-only` widening,
bind its marker policy to the broad producer's policy in tests, and prove the
reported historical false clean becomes an exact-line block.

## Failure Angles

- Problem framing: the repair must close #615's producer-population mismatch,
  not merely change command text. The exact historical wrapper run now blocks on
  the same five lines, so the change reaches the recorded failure.
- Diagnostic ownership: the focused producer owns preserving the broad admissible
  population when claiming conservative subset proof. The wrapper cannot repair
  coverage already widened by extra tests.
- Final-workflow proof: the new sentinel proves actual marker deselection;
  standing-runner coverage transport and wrapper consumer tests retain their
  existing seams; the historical receipt proves their incident composition.
- Export boundary: round 2 found the plugin mirror still carried the widening
  flag. `sync_root_plugin_manifests.py` regenerated it, and source/mirror now
  compare byte-identical.
- Post-round-2 gate repair: the duplicate ratchet found that removing the flag
  made the wrapper reconstruct the suggester's exact command. The wrapper now
  consumes the suggester-owned `command` payload directly; this reduces owners
  without changing the marker or target population. Per the two-round cap this
  repair was recorded under the two-round cap, then the round-2 reviewer accepted
  its semantic equivalence during the final binding readback.

## Counterweight Pass

- Act before ship: preserve the repaired historical wrapper receipt and
  synchronize the plugin export. Both were completed before closeout.
- Bundle anyway: keep the broad-policy tripwire, real child-command sentinel,
  focused transport/final-consumer tests, and packaging equality checks together.
- Over-worry: do not add a slow permanent replay of the full historical range;
  the durable incident run owns integration evidence while focused tests own each
  stable seam.
- Over-worry: do not extract one shared marker-policy owner without another
  recorded drift; the parity test fixes the current expected broad value and
  rejects focused widening.
- Valid but defer: hosted CI and arbitrary future producer/transport equivalence
  remain explicit non-claims until an authorized push or a new escape.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: plugins/charness/scripts/prepush_focused_changed_line_coverage.py:165 | action: fix | note: resolved by regenerating the plugin export after round 2 found the stale widening flag
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md | action: document | note: durable debug evidence records blocked exit and exact five historical lines
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_prepush_focused_changed_line_coverage.py:125 | action: fix | note: parity and real-command marker controls ship with existing transport and final-consumer tests
- F4 | bin: over-worry | evidence: strong | ref: charness-artifacts/spec/2026-08-13-issue-615-focused-changed-line-verdict-contract.md | action: document | note: a permanent full historical replay would duplicate an expensive incident receipt rather than stabilize a new seam
- F5 | bin: over-worry | evidence: moderate | ref: cosmic-ray.toml:5 | action: document | note: shared policy extraction is unsupported while the explicit comparator tripwire catches current drift
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_focused_changed_line_coverage.py:165 | action: fix | note: duplicate-ratchet blocker resolved by consuming the suggester-owned command instead of reconstructing it

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host accepted the spawn fields but exposed no applied-model metadata
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Round 1 used two contrasting angle reviewers plus a separate
counterweight reviewer. Because their durable-evidence finding caused repairs,
round 2 used a different reviewer over the repaired full surface; it required
only generated plugin synchronization and found no further source/test repair.
All four reviewer windows passed the parent-side boundary fingerprint with
`verdict: clean` before findings were applied.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-13-issue-615-round2-packet.md
- Packet path: charness-artifacts/critique/2026-08-13-issue-615-round2-packet.json
- Packet SHA256: db7a1adc3aaa19f8efcdfebd02289eaa125f6a9dfd8439a099ecbed2bce0df26
- Identity SHA256: 71ff90a4cdf20095cc4bd17b8a9272370b9df66b9b5db875b11e36e44afd215e

## Boundary Ownership

- Producer: focused test selection in `_focused_pytest_command`, constrained by
  the broad marker policy in `cosmic-ray.toml`.
- Consumer: `prepush_focused_changed_line_coverage.py` after the shared
  changed-line consumer returns its operator-visible verdict.
- Owning surface: authoritative repo script plus deterministic plugin export.
- Verdict: owned-correctly

## Closeout Claims Readback

A separate bounded read-only reviewer audited the proposed direct-commit
carrier against the debug receipt, completed spec, critique, authoritative
source, checked-in plugin export, and focused tests. The reviewer approved with
no corrections after independently confirming the full historical base SHA and
command, coverage fingerprint, exit 1/`blocked`, exact five missing lines,
suggester-owned command, byte-identical plugin copy, recorded 97-test focused
set, two-round wording, and the explicit no-push/no-hosted-CI/GitHub-OPEN
boundary. Parent-side boundary verification returned `verdict: clean`.

The requested high-leverage spawn fields were sent; applied model/tier metadata
was unavailable to the reviewer.

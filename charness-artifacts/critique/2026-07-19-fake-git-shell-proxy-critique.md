# Fake Git shell proxy critique
Date: 2026-07-19

## Decision Under Review

Replace the release-test fake Git Python process with a Bash proxy that keeps
real Git delegation and fault injection while removing repeated interpreter startup.

## Failure Angles

- Semantic review found initial argv-string matching collapsed argument boundaries,
  the sidecar push count could drift from the observable log, and JSON escaping
  omitted legal control characters.
- Proof review checked direct fixture consumers, real-Git delegation, Bash support,
  and whether the timing comparison preserved the same 41-test selection.
- Ownership review found the new shell fixture was initially routed to a lint
  command that did not discover `tests/**/*.sh`; discovery and routing proof were fixed.
- All change-affecting findings were fixed and the updated packet was reviewed again.

## Counterweight Pass

- No act-before-ship concern remains. Preserving the retired Python traceback text
  is implementation coupling, not release proof.
- Pretty-printed legacy preseed logs are intentionally unsupported: every active
  temporary fixture log starts absent and the shell proxy owns its compact format.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/fixtures/release_publish_fake_git.sh | action: fix | note: element-wise argv matching now preserves fault selector boundaries
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_release_publish_fake_git.py | action: fix | note: C0 JSON, log-derived counts, and after-mode failure normalization have direct regressions
- F3 | bin: valid-but-defer | evidence: strong | ref: tests/quality_gates/fixtures/release_publish_fake_git.sh | action: defer | note: retired pretty-printed preseed logs are outside the ephemeral fixture lifecycle
- F4 | bin: over-worry | evidence: strong | ref: tests/quality_gates/fixtures/release_publish_fake_git.sh | action: document | note: exact CalledProcessError traceback text is not a fixture contract
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/check-shell.sh | action: fix | note: shell lint now discovers nested test fixtures and the surface regression proves routing

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model gpt-5.6-terra, reasoning_effort medium, service_tier priority, fork_turns none.
- Host exposure state: requested_fields_sent
- Application state: unverified; reviewer identities were returned without provider-applied model metadata.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.json
- Packet SHA256: fff81f01b36389fe8b033fcda979a6797bad503e2f9c4da03ab3e7874280e8f9
- Identity SHA256: f328b40cf0b23ec69b90ad1b35b7519afa4b95d22e2a97b706445a27bf4c23eb

## Boundary Ownership

- Producer: release-test helpers produce exact Git argv and fault modes.
- Consumer: the fake Git proxy records argv, injects faults, and delegates ordinary calls.
- Owning surface: release test fixtures own test-only execution mechanics.
- Verdict: owned-correctly

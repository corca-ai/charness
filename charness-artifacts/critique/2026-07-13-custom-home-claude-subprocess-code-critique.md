# Custom Home Claude Subprocess Code Critique
Date: 2026-07-13

## Decision Under Review

Route every Claude plugin observation and mutation through a Claude-specific
subprocess seam that binds `HOME` to the selected Charness workflow home.

## Failure Angles

- Ownership and portability: changing generic subprocess execution or only the
  doctor caller could either leak host knowledge or leave mutation siblings unsafe.
- Operational safety: doctor-only proof could pass while init/reset still write
  or remove plugin state under an unrelated process home.

## Counterweight Pass

- The Claude-specific helper is correctly owned and preserves the inherited
  environment for default-home use while overriding only HOME for custom use.
- Mutating wrong-home risk required two durable end-to-end probes: init for
  add/install/enable and reset for uninstall/remove. Separate update and helper
  unit tests would duplicate the same centralized seam without stronger proof.
- XDG and textual symlink semantics remain valid deferrals and explicit nonclaims.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/charness_cli/test_managed_install.py | action: fix | note: add split-home init proof that custom state is created and unrelated `.claude` is untouched; fixed and verified.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/charness_cli/test_managed_install_extended.py | action: fix | note: add split-home destructive proof that reset removes custom-home state without touching process HOME; fixed and verified.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/test_managed_install.py | action: fix | note: strengthen doctor no-touch proof from missing JSON files to an absent unrelated `.claude` tree; fixed.
- F4 | bin: over-worry | evidence: moderate | ref: charness | action: defer | note: no separate update or helper-unit test after centralized call-site inspection plus init/reset end-to-end proof.
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/debug/2026-07-13-custom-home-claude-state-leakage.md | action: defer | note: real Claude XDG and textual-symlink behavior require field evidence before expanding the HOME contract.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: metadata-hidden
- Application state: requested fields were accepted; provider application was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — ownership/portability and operational/security angles plus a
separate counterweight ran read-only; both fingerprint windows verified zero drift.

## Boundary Ownership

- Producer: the Charness workflow selects `home_root`; Claude CLI produces and consumes HOME-owned plugin state.
- Consumer: doctor guidance, init/update installation, and reset/uninstall removal flows.
- Owning surface: the Charness Claude-host subprocess adapter seam.
- Verdict: owned-correctly

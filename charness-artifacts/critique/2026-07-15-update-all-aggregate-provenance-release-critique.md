# Release Critique: update-all aggregate and provenance repair

Date: 2026-07-15

## Execution

Completed before the pending v1.0.11 release. Three contrasting fresh-eye
angles and a separate counterweight reviewed the changed worktree read-only;
the parent verified the reviewer boundary fingerprint after every return.

## Packet Consumed

`charness-artifacts/critique/2026-07-15-083904-packet.md`

## Target

Release critique, shaped by the operational, operator-information, and
problem-framing angles required for a public control-plane correction.

## Decision Under Review

Release a corrective patch that makes `charness update all` and other
high-fanout root responses compact YAML by default, preserving per-tool
evidence only for `--detail`; stop external-tool updates from guessing an
updater from a PATH-only binary.

## Release Scope

v1.0.11 (patch): correct the incomplete v1.0.10 aggregate response and update
provenance behavior. Existing automation that needs aggregate `results` must
move to `--detail`.

## Capability at Stake

Operators and agents need one bounded YAML decision document rather than an
unreadable nested execution graph, without losing a route to the evidence or
mutating an unknown third-party install through a guessed package manager.

## Surface-Lock Inventory

- Root CLI projection in `charness`, including `update all` and `--detail`.
- Tool lifecycle manifests for gitleaks, Ruff, and Specdown plus their checked
  plugin mirrors.
- Generated CLI reference and control-plane operator contract.
- Provenance and managed-install integration tests, including persisted locks.
- Release artifact, versioned plugin manifests, install refresh, and public
  GitHub release surface produced by the publish helper.

## Failure Angles

- Operational: unrecognized PATH provenance, updater routing, stale locks, and
  Homebrew installation behavior could still mutate an unrelated install.
- Humane/operator information: a terse response could hide actionable state or
  silently strand existing `results` consumers.
- Problem framing and regression: a single aggregate fixture could miss detail
  preservation, recognized Go routing, or the managed-install update-all path.

## Findings

- The former scripted Specdown update assertions contradicted the new
  recognized-Go package-manager route; both direct and managed-install tests
  now assert the canonical `go install` command and persisted route.
- The aggregate `results` removal is intentional but discoverable: the CLI
  reference and control-plane contract now direct record-consuming automation
  to `--detail`.
- Gitleaks installation no longer runs `brew upgrade` merely because Homebrew
  is available; explicit installation uses non-upgrading `brew install`.
- Categorized attention IDs plus `--detail` preserve actionable diagnosis; a
  per-category remediation map is not necessary for this release.

## Counterweight Pass

- **Act Before Ship:** none remain after the test, migration-documentation, and
  Homebrew fixes.
- **Bundle Anyway:** the three concrete defects were cheap and were fixed in
  this slice.
- **Over-Worry:** adding a second terse remediation format would duplicate the
  full per-tool next steps already available through `--detail`.
- **Valid but Defer:** recognize Ruff's uv/pipx/pip provenance only after a
  separately evidenced ownership design; manual is the safe current result.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/test_tool_lifecycle.py | action: fix | note: replace stale Specdown curl-route assertions with recognized-Go package-manager and lock assertions.
- F2 | bin: bundle-anyway | evidence: strong | ref: docs/control-plane.md | action: fix | note: document the intentional aggregate-results migration to `--detail`.
- F3 | bin: bundle-anyway | evidence: strong | ref: integrations/tools/gitleaks.json | action: fix | note: make the explicit Homebrew install route non-upgrading.
- F4 | bin: over-worry | evidence: moderate | ref: charness | action: document | note: categorized attention IDs plus `--detail` are sufficient without another default remediation schema.
- F5 | bin: valid-but-defer | evidence: moderate | ref: integrations/tools/ruff.json | action: defer | note: retain manual Ruff updates until uv/pipx/pip provenance can be recognized without PATH guessing.

## Reviewer Tier Evidence

- Requested tier: high-leverage fresh-eye review.
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority.
- Host exposure state: metadata-hidden
- Application state: three angle reviewers and one separate counterweight completed; the host returned no applied-model metadata.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: root `charness` response projection and manifest-declared lifecycle routing.
- Consumer: operators and agent automation reading stdout or persisted tool locks.
- Owning surface: root CLI control plane and integration manifests.
- Verdict: owned-correctly.

## Operator Action Required

No manual action is required to adopt the release. Automation that consumed a
multi-tool `results` map must invoke the same command with `--detail`.

## Upgrade Path

Run `charness update`; then use `charness update all --detail` when an
automation or diagnosis needs individual tool records. PATH-only gitleaks,
Ruff, and Specdown installs report manual guidance rather than receiving a
guessed automatic update.

## Deliberately Not Doing

- Do not infer Ruff ownership from `uv`, `pipx`, or `pip` merely being present.
- Do not add byte clipping or a parallel terse remediation schema to conceal
  the output graph.
- Do not recover or modify third-party installs whose provenance is unknown.

## Next Move

Run the locked release validation, publish v1.0.11 through the repo helper,
verify the public release through an independent channel, and run the actual
installed `charness update all` to capture behavioral proof.

# Charness v1.0.9 Root CLI YAML Release Critique
Date: 2026-07-15

## Decision Under Review

Publish `v1.0.9`: every operational root `charness` response is one YAML
document; the former root `--json` switch is accepted but ignored and no longer
advertised. The release also closes the command-surface and side-effect-contract
drift that let that obsolete guidance persist.

Packet Consumed: charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-packet.md

## Release Scope

`v1.0.9` is a patch release that repairs the established structured-output
contract and makes its migration explicit. Existing JSON consumers must move to
a YAML parser; no persistent-state migration is involved.

## Surface-Lock Inventory

- Root CLI rendering, legacy argument compatibility, operational stderr, and
  standalone bootstrap availability: `charness` and
  `packaging/bootstrap-python.json`.
- Generated command surface, ownership registry, and mutating-mode probe
  declaration: `.agents/command-docs.yaml`, `.agents/command-registry.json`,
  and `.agents/cli-side-effect-probes.json`.
- Consumer-facing migration and rollback statement:
  `charness-artifacts/release/2026-07-15-v1.0.9-notes.md`.
- Release-manifest and install artifacts to be version-bumped and synchronized
  by the repo-owned release helper.

## Failure Angles

- Gawande operational review checked parser/document/registry/render agreement,
  mutations, release phases, and release tests.
- Minto communication review required a self-contained YAML migration,
  compatibility, update, and rollback narrative.
- Raskin interface review checked stdout/stderr boundaries and discovered that
  a copied CLI could lack PyYAML before bootstrap provisioning.
- A separate counterweight pass rejected per-command legacy-flag duplication
  and deferred payload-schema versioning as broader work.

## Counterweight Pass

- Hold only for demonstrated defects: the missing verbose-version side-effect
  entry, an obsolete test invocation, missing release notes, and the
  PyYAML-free standalone path. All have been corrected and independently
  rechecked.
- Do not preserve JSON stdout or add a per-subcommand `--json` matrix: central
  exact-token stripping plus two explicit compatibility tests are the smaller,
  more honest boundary.
- Defer versioned schemas for each command payload; the current release changes
  formatting, not every payload's semantic schema.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/charness_cli/test_managed_install_release_checks.py:159 | action: fix | note: verbose version-state test had stopped exercising its detailed output path; restored it with --verbose
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-07-15-v1.0.9-notes.md:1 | action: document | note: added explicit YAML migration, ignored legacy flag, update, and v1.0.8 rollback instructions
- F3 | bin: act-before-ship | evidence: strong | ref: charness:37 | action: fix | note: standalone CLI now emits JSON syntax as valid YAML without PyYAML and bootstrap runtime requires yaml
- F4 | bin: bundle-anyway | evidence: strong | ref: .agents/cli-side-effect-probes.json:1 | action: fix | note: added version --verbose and all root primary mutating modes to the checked probe contract
- F5 | bin: over-worry | evidence: strong | ref: charness:5220 | action: document | note: central exact-token stripping makes a per-subcommand legacy --json matrix unnecessary
- F6 | bin: valid-but-defer | evidence: moderate | ref: docs/generated/cli-reference.md:5 | action: defer | note: versioned semantic schemas for every root command payload are useful future work but not required for this output migration

## Operator Action Required

Publish with the repo-owned helper and the accompanying v1.0.9 notes. After
publication, run the declared install refresh, then use the release artifact to
record the installed-surface and distinct-channel evidence without treating it
as terminal green.

## Upgrade Path

Run `charness update`, restart the host session, and update automation to parse
YAML. Verify with `charness version` or `charness doctor`. To temporarily retain
the former root JSON contract, reinstall v1.0.8 through the same path and
restart the host; no data migration is required.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`.
- Host exposure state: requested_fields_sent
- Application state: host exposes no resolved-model metadata; reviewer outputs
  and parent boundary fingerprints prove only independent read-only review.

## Fresh-Eye Satisfaction

parent-delegated. Two independent release-angle reviewers and one separate
counterweight reviewer consumed the prepared packet. The post-fix reviewer
approved the standalone YAML fallback; parent fingerprint verification reported
no worktree or index drift for every accepted review.

## Boundary Ownership

- Producer: the root CLI owns public structured rendering; the bootstrap
  contract owns installed runtime requirements; release notes own migration
  communication.
- Consumer: humans and automation consume root YAML; managed install/update
  consumes bootstrap requirements and release metadata.
- Owning surface: root CLI output contract, packaging bootstrap contract, and
  release artifact each retain their own facts rather than encoding them in an
  unrelated helper.
- Verdict: owned-correctly

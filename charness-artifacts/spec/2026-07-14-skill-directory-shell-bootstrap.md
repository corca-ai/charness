# Skill Directory and Reviewer-Boundary Consumer Contract

Date: 2026-07-14

## Problem

The shared bootstrap reference showed non-exported `SKILL_DIR` assignments and
claimed agent runtimes inject the variable automatically. A consuming-repo agent
therefore combined path discovery and command execution as
`SKILL_DIR=/path python3 "$SKILL_DIR/scripts/..."`; shell expansion saw the
previously unset value and invoked `/scripts/...`.

The reviewer-boundary policy then exposed a second consumer seam: it instructed
an arbitrary consuming repository to run Charness source paths under
`skills/shared/` and to find a Claude definition under `.claude/agents/`. Those
assets belong to the installed Charness package, not the consumer repository;
the reported consumer run proved both paths absent.

## Capability Contract

Source-checkout, installed-plugin, and manual-shell consumers resolve the skill
directory once, export it before any command expands it, and run bootstrap or
reviewer-boundary helpers from an unrelated repository directory without
depending on ambient host injection or a copied Charness source tree. Claude
and Codex each consume an explicit host-appropriate reviewer path; neither
infers that a Claude agent definition is a Codex custom agent.

## Current Slice

- Correct the canonical bootstrap-resolution reference and generated plugin
  copy.
- State that a skill source locator may be available to the agent while the
  command environment variable remains unset.
- Warn against command-scoped assignment when the same command expands the
  variable.
- Extend the existing bootstrap-variable validator so the exact unsafe pattern
  cannot silently return from either the canonical reference or an individual
  skill Bootstrap block that cites it.
- Prove source and synchronized plugin bootstrap commands from an unrelated
  temporary repository directory.
- Make the fingerprint invocation resolve relative to the active skill package,
  rather than `<consumer-repo>/skills/shared/`.
- Export the Claude typed reviewer definition in Claude's plugin-native
  `agents/` location.
- Give Codex an explicit first-class native-agent mapping which does not claim
  the Claude tool envelope binds.

## Fixed Decisions

- Use `export SKILL_DIR=...` on its own command before any later
  `"$SKILL_DIR/..."` expansion.
- Do not promise host environment injection. Treat host-provided source metadata
  and shell environment state as different interfaces.
- Keep the individual skill bootstrap commands unchanged; their shared
  reference owns resolution and export semantics.
- The existing validator protects both the canonical reference and the sibling
  public/support skill Bootstrap seams without becoming a general shell parser.
- The shared helper is addressed as
  `"$SKILL_DIR/../../shared/scripts/reviewer_boundary_fingerprint.py"` after
  the bootstrap contract has exported `SKILL_DIR`; consumers never manufacture
  a Charness `skills/` directory.
- Claude's envelope is a plugin asset, not a consumer-repo `.claude/` asset.
  Codex custom agents are project configuration, not plugin assets. The current
  Codex path is its native `explorer` agent with the bounded review packet and
  parent-side fingerprint rail; it does not imply the Claude envelope binds.

## Non-Goals

- Hardcoding one Codex or Claude plugin-cache root.
- Replacing the existing runtime bootstrap shim.
- Exporting `SKILL_DIR` from Charness into arbitrary parent shells.
- Claiming behavior for every future host release.
- Treating a copied `agents/bounded-reviewer.md` as proof that Codex loaded a
  named custom agent.

## Success Criteria

1. Source and manual installed-cache examples export `SKILL_DIR` before use.
2. The reference explicitly explains why
   `SKILL_DIR=/path command "$SKILL_DIR/..."` is unsafe when the prior value is
   unset.
3. The reference no longer claims that the agent runtime necessarily injects a
   shell environment variable.
4. `check_skill_bootstrap_vars.py` fails when the canonical reference or an
   individual skill Bootstrap contains a non-exported `SKILL_DIR=` assignment
   in a positive shell example, even when the skill cites the reference.
5. Source and plugin copies stay synchronized and the debug resolver runs from
   an unrelated temporary repository using the documented two-step export.
6. A clean consumer repository runs the fingerprint snapshot through the
   exported plugin's active skill path and does not require
   `consumer/skills/shared/`.
7. The Claude plugin export contains its typed reviewer definition under
   `agents/`; the Codex path explicitly uses its native `explorer` reviewer and
   documents that the Claude envelope rail is unsupported there.

## Acceptance Checks

- `unit`: validator accepts exported assignments and rejects a non-exported
  assignment in the canonical reference and in a citing skill Bootstrap.
- `shell`: demonstrate the reported command-scoped assignment expands to
  `/scripts/...`, while export-before-use expands to the resolved path.
- `integration`: run source and plugin debug resolver helpers from an unrelated
  temporary repository root.
- `integration`: export the plugin, initialize a clean consumer Git repository,
  and run fingerprint `snapshot` using the installed `SKILL_DIR`-relative path.
- `host`: inspect the Claude and Codex package/configuration layouts separately;
  assert the exported Claude asset exists and that the Codex mapping makes no
  false plugin-envelope discovery claim.
- `quality`: synchronize generated plugin surfaces and pass the locked closeout.

## Boundary Ownership

owned-correctly

The shared reference owns shell-variable resolution semantics; the existing
bootstrap-variable validator owns escape prevention; individual skills own
which helper commands to run; the packaging exporter owns installed assets;
host adapters own Claude/Codex agent discovery semantics.

## Implementation Evidence

- `sh`, `bash`, and `zsh` reproduced `/scripts/...` for the unsafe form and the
  resolved path for export-before-use.
- Source and synchronized plugin debug resolvers ran from an unrelated
  temporary repository directory.
- Nine focused validator tests and all 21 skill-package validations passed.
- The released v1.0.5 cache is deliberately not claimed as updated; delivery
  requires a later authorized release/update boundary.
- Pre-change consumer observation: the attempted `skills/shared/scripts/` and
  `.claude/agents/` paths were absent in a non-Charness repository. This is the
  portability failure the current slice must eliminate; it is not proof of the
  repaired Claude or Codex path.
- A clean consumer Git repository now runs `snapshot` through an exported
  plugin skill directory using the documented `SKILL_DIR`-relative helper path;
  the export also contains `agents/bounded-reviewer.md` for Claude.
- The focused portability, bounded-envelope, and surface suites passed (31
  tests). The host mapping intentionally claims no live Claude envelope bind or
  Codex tier-application signal.

## Critique

- Interrupt Source: skill-dir-shell-expansion
- Seam Summary: skill source locator to shell environment and installed helper command
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the reported command was reproduced across `sh`, `bash`,
  and `zsh`; corrected source and plugin helpers ran from an unrelated repo;
  the validator now owns recurrence prevention.
- What Disproving Observation Is Resolved: a skill source locator does not prove
  `SKILL_DIR` exists in the tool shell, and command-scoped assignment cannot
  supply the value to expansions in that same command.
- Reviewer-boundary carry-forward: a package may contain a helper while a
  consumer repository does not. The final consumer must resolve the helper from
  the active installed skill and must use host-specific agent discovery.
- Rejected alternative: hardcoding one host cache path or weakening helper
  commands would move the fix away from the shared path-to-shell owner.

- Act Before Ship: make source-relative paths conditional on the Charness repo
  root; show an absolute source path from a consuming repo; and keep export plus
  dependent expansion in one persistent shell/tool invocation. Applied.
- Pre-release guard propagation: reuse the exact detector for individual skill
  Bootstrap blocks so a canonical citation cannot mask the same unsafe pattern.
  Applied after a separate release critique and counterweight pass.
- Bundle Anyway: keep the critique scope explicit in its durable artifact.
- Valid but Defer: installed-cache publication/readback belongs to a later
  authorized release boundary.
- Over-Worry: parsing every console prompt or shell dialect, adding a permanent
  installed integration gate, or making plugin-runtime self-validation a new
  contract.

- Final consumer critique: `charness-artifacts/critique/2026-07-14-critique-review.md`
  records two independent host/proof angles plus a counterweight. Each returned
  under a clean parent-side reviewer-boundary fingerprint.

## Resolved Host Decision

Codex does not discover the Claude markdown envelope from a plugin root. Its
current supported path is a native `explorer` reviewer supplied the bounded
review packet, with reviewer-tier fields passed only when the host exposes
them. A project-local Codex custom-agent TOML is a different, authorized setup
surface and is not generated by this plugin slice.

## Deferred Decisions

- Whether a later release should add a live Claude/Codex host-session proof is
  a release-boundary decision. This slice proves package/configuration paths and
  records no claim that a host applied a tool restriction without a live denial.

Fresh-Eye Satisfaction: parent-delegated. Two distinct angles and a separate
counterweight completed under clean reviewer-boundary fingerprints. Requested
reviewer fields were sent; provider application metadata was not exposed.

## Canonical Artifact

This file is the implementation contract. The shared bootstrap reference,
packaging exporter, host-specific reviewer assets, and consumer-path tests own
the executable details.

## First Implementation Slice

Completed: repaired the portable fingerprint path, exported the Claude
envelope, and recorded the Codex native-agent mapping. Generated plugin
surfaces must remain synchronized; publication still requires its own
authorized release and installed-cache proof.

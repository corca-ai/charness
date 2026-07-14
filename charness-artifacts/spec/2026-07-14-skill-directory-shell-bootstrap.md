# Skill Directory Shell Bootstrap Contract

Date: 2026-07-14

## Problem

The shared bootstrap reference shows non-exported `SKILL_DIR` assignments and
claims agent runtimes inject the variable automatically. A consuming-repo agent
therefore combined path discovery and command execution as
`SKILL_DIR=/path python3 "$SKILL_DIR/scripts/..."`; shell expansion saw the
previously unset value and invoked `/scripts/...`.

## Capability Contract

Source-checkout, installed-plugin, and manual-shell consumers resolve the skill
directory once, export it before any command expands it, and run bootstrap
helpers from an unrelated repository directory without depending on ambient
host injection.

## Current Slice

- Correct the canonical bootstrap-resolution reference and generated plugin
  copy.
- State that a skill source locator may be available to the agent while the
  command environment variable remains unset.
- Warn against command-scoped assignment when the same command expands the
  variable.
- Extend the existing bootstrap-variable validator so an unsafe canonical
  example cannot silently return.
- Prove source and synchronized plugin bootstrap commands from an unrelated
  temporary repository directory.

## Fixed Decisions

- Use `export SKILL_DIR=...` on its own command before any later
  `"$SKILL_DIR/..."` expansion.
- Do not promise host environment injection. Treat host-provided source metadata
  and shell environment state as different interfaces.
- Keep the individual skill bootstrap commands unchanged; their shared
  reference owns resolution and export semantics.
- A validator protects the canonical reference because every public/support
  skill delegates this portability boundary to it.

## Non-Goals

- Hardcoding one Codex or Claude plugin-cache root.
- Replacing the existing runtime bootstrap shim.
- Exporting `SKILL_DIR` from Charness into arbitrary parent shells.
- Claiming behavior for every future host release.

## Success Criteria

1. Source and manual installed-cache examples export `SKILL_DIR` before use.
2. The reference explicitly explains why
   `SKILL_DIR=/path command "$SKILL_DIR/..."` is unsafe when the prior value is
   unset.
3. The reference no longer claims that the agent runtime necessarily injects a
   shell environment variable.
4. `check_skill_bootstrap_vars.py` fails when the canonical reference contains
   a non-exported `SKILL_DIR=` assignment in a positive shell example.
5. Source and plugin copies stay synchronized and the debug resolver runs from
   an unrelated temporary repository using the documented two-step export.

## Acceptance Checks

- `unit`: validator accepts exported assignments and rejects a non-exported
  canonical assignment.
- `shell`: demonstrate the reported command-scoped assignment expands to
  `/scripts/...`, while export-before-use expands to the resolved path.
- `integration`: run source and plugin debug resolver helpers from an unrelated
  temporary repository root.
- `quality`: synchronize generated plugin surfaces and pass the locked closeout.

## Boundary Ownership

owned-correctly

The shared reference owns shell-variable resolution semantics; the existing
bootstrap-variable validator owns escape prevention; individual skills own
which helper commands to run; host adapters own path discovery metadata.

## Implementation Evidence

- `sh`, `bash`, and `zsh` reproduced `/scripts/...` for the unsafe form and the
  resolved path for export-before-use.
- Source and synchronized plugin debug resolvers ran from an unrelated
  temporary repository directory.
- Five focused validator tests and all 21 skill-package validations passed.
- The released v1.0.5 cache is deliberately not claimed as updated; delivery
  requires a later authorized release/update boundary.

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
- Rejected alternative: hardcoding one host cache path or weakening helper
  commands would move the fix away from the shared path-to-shell owner.

- Act Before Ship: make source-relative paths conditional on the Charness repo
  root; show an absolute source path from a consuming repo; and keep export plus
  dependent expansion in one persistent shell/tool invocation. Applied.
- Bundle Anyway: keep the critique scope explicit in its durable artifact.
- Valid but Defer: installed-cache publication/readback belongs to a later
  authorized release boundary.
- Over-Worry: parsing every console prompt or shell dialect, adding a permanent
  installed integration gate, or making plugin-runtime self-validation a new
  contract.

Fresh-Eye Satisfaction: parent-delegated. Two distinct angles and a separate
counterweight completed under clean reviewer-boundary fingerprints. Requested
reviewer fields were sent; provider application metadata was not exposed.

## Canonical Artifact

This file is the implementation contract. The shared bootstrap reference and
validator tests own executable details.

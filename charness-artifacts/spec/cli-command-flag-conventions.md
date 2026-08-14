# Spec — Consistent CLI Command and Flag Conventions
Date: 2026-04-22

## Problem

`create-cli` currently covers lifecycle seams, machine-readable output, and
quality gates, but it does not define a portable baseline for command and flag
shape. That leaves repo-owned CLIs free to drift on basic surfaces such as
`version` vs `--version`, whether `-v` means verbose or version, and which
commands are expected to be read-only probes. The resulting CLIs are similar,
but not similar enough for operators or agents to predict them confidently.

## Decision

Adopt a portable baseline for multi-command CLIs created or normalized through
`create-cli`.

Canonical rules:

- multi-command CLIs are subcommand-first
- `version` is the canonical version surface
- top-level `--version` is an ergonomic alias when the CLI already has a stable
  top-level parser
- `-v` is reserved for `verbose`, never for `version`
- `-h` / `--help` are no-side-effect probes on the top level and stable public
  subcommands
- structured output is unconditional YAML; there is no output-format flag.
  `--summary` / `--detail` select payload DEPTH, never format
- destructive confirmations prefer explicit long flags over short aliases

Canonical lifecycle verbs:

- `init`
- `doctor`
- `update`
- `reset`
- `uninstall`
- `version`

These are defaults, not mandatory vocabulary for every CLI. A repo can diverge
when the product surface genuinely differs, but that divergence should be
explicit and documented.

## Amendment 2026-08-14 — `--json` is retired

The rule above read "`--json` means machine-readable output, not 'more detailed
human prose'" until this date. That line outlived the migration it described:
the July 2026 YAML migration moved the root CLI and the public skill helpers to
YAML, deliberately leaving `--json` declared as a hidden compatibility parser
(see `charness-artifacts/debug/2026-07-18-residual-json-flags-after-yaml-migration.md`).
A blessing sentence for a flag that was already scheduled to die is what later
made ~95 surviving declarations read as intentional rather than as residue.

Owner decision: total removal, including backward compatibility. Repo-owned
command output is now unconditionally YAML through `scripts/yaml_output.py`.

- No `--json` flag, no hidden alias, no compatibility parser.
- `--summary` / `--detail` remain, and select payload DEPTH, never format.
- Third-party native JSON (`gh`, `git`, `npm`, `pnpm`, `cautilus`, `cosmic-ray`)
  is NOT this contract's surface and keeps its own flags and parsers.
- Persisted `.json` artifacts are a storage format, not an output format, and
  are untouched.

Migration cost a consumer inherits: any `json.loads` of a repo command's stdout
breaks and must become `yaml.safe_load`. A YAML reader needs no change, because
`render_yaml` already fell back to JSON syntax — which is valid YAML — whenever
PyYAML was absent.

## Current Slice

1. Add a `create-cli` reference that records the canonical command/flag
   baseline.
2. Update `create-cli` core guidance so the baseline is part of the main
   contract instead of an optional naming preference.
3. Prove the pattern in `charness` itself by keeping `version` as the canonical
   subcommand and adding top-level `--version` as an additive alias.
4. Add a CLI test that protects `--version` and ensures `-v` stays free for
   future `verbose` use instead of becoming a version shorthand.

## Non-Goals

- forcing single-purpose helper scripts to adopt a fake subcommand tree
- renaming existing CLIs solely for cosmetic consistency when their product
  contract is already stable
- requiring top-level `--version` on every CLI, including ones that do not
  expose a stable top-level parser
- reserving short aliases for destructive flows just to mirror other tools

## Success Criteria

1. `create-cli` documents a canonical answer for `version`, `--version`, and
   `-v`.
2. `create-cli` explicitly distinguishes read-only probe flags from mutating
   flags.
3. `charness version` remains the canonical version command.
4. `charness --version` returns the same version string as `charness version`.
5. No public contract claims that `-v` means version.

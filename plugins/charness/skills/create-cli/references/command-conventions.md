# Command Conventions

Portable baseline for repo-owned multi-command CLIs:

- prefer a small set of stable subcommands over many top-level mode flags
- keep lifecycle verbs explicit: `init`, `doctor`, `update`, `reset`,
  `uninstall`, `version`
- treat `version` as the canonical version surface
- allow top-level `--version` as an ergonomic alias when the CLI already has a
  stable top-level parser
- reserve `-v` for `verbose`, never `version`
- support `-h` / `--help` as read-only help probes on the top level and stable
  public subcommands
- for Charness-style agent-first commands, use YAML by default and `--detail`
  for full evidence; human-first and third-party CLIs keep their established
  structured-output mode
- prefer explicit long flags for destructive confirmations or irreversible
  behavior

When a CLI diverges from this baseline, make the reason product-shaped, not
stylistic. "The parser happened to allow it" is not a reason.

## Named Option Semantics

Named options (`--flag`, `--flag value`) are order-independent by default:
any valid named option may appear before or after any other named option on
the same command line. A command may diverge from this only for a
documented product reason (for example, a mode flag that changes how later
options are interpreted); "the parser happened to require this order" is not
a reason, matching the baseline rule above.

This baseline is scoped to named options only:

- positional arguments keep whatever order the command's grammar defines;
  order-independence does not extend to them
- an option's *value* (`--target foo`) is bound to that option, not to
  position on the command line, so `--target foo --profile bar` and
  `--profile bar --target foo` must parse identically

A parser that satisfies this baseline must also reject, rather than
silently accept:

- a duplicate named option (unless the command explicitly documents
  last-wins or accumulate semantics)
- an unknown named option
- a named option that requires a value but is missing one

Test the parser contract directly (duplicate/unknown/missing-value
rejection, and that a representative pair of named options parses the same
both orders) rather than enumerating every flag permutation; see
`quality-gates.md` for where this fits alongside other parser smoke tests.

## Read-only Probe Surface

- `tool --help`
- `tool version`
- `tool --version` when supported
- `tool doctor --help`
- cheap command-discovery surfaces such as `tool commands --detail` for a
  Charness-style CLI, or the tool's native machine mode

Do not overload probe surfaces with mutations, background refresh, or install
side effects.

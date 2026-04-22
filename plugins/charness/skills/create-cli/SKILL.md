---
name: create-cli
description: "Use when creating or upgrading a repo-owned CLI, bootstrap script, or command runner. Define the command surface, install/update contract, structured output, dry-run and doctor behavior, distribution path, and quality gates before spreading ad hoc shell or Python entrypoints."
---

# Create CLI

Use this when the task is to add, refactor, or normalize a command-line tool in
`charness` or another repo that `charness` is helping with.

Borrow Jef Raskin-style discoverability and modelessness when shaping the
surface: make the next command obvious, keep mode shifts explicit, and avoid
forcing operators or agents to memorize hidden lifecycle state.

## Bootstrap

Read the smallest current surface that explains how the repo already ships and
tests commands.

```bash
# Required Tools: rg
sed -n '1,220p' README.md
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
rg -n "argparse|click|typer|cobra|urfave|commander|subcommands|--json|--help|dry-run|doctor|install|update" .
find . -maxdepth 3 \\( -name '*.sh' -o -name '*.py' -o -name 'main.go' \\) | sort
```

If the CLI already exists, inspect the entrypoint and one representative test
before changing behavior.

Missing-binary handling follows
`create-skill/references/binary-preflight.md` when the bootstrap or validation
steps call tools outside the baseline shell surface.

## Workflow

1. Define the operator contract first.
   - who runs the CLI: user, maintainer, CI, agent
   - what must be deterministic vs advisory
   - what state must survive for a later agent or operator
2. Shape the command surface.
   - stable nouns and verbs
   - for multi-command CLIs, prefer a subcommand-first surface and follow
     `references/command-conventions.md` for canonical lifecycle verbs and
     version/help flag conventions
   - one obvious install/bootstrap path
   - explicit `doctor`, `update`, `reset`, or `uninstall` commands when the
     product owns lifecycle state
   - if install materializes one host-visible target, treat that target as the
     canonical lifecycle surface instead of inventing a registry first
   - if the product needs one command that refreshes both itself and tracked
     external/runtime surfaces, keep that aggregate path product-owned, such as
     `update all`, instead of leaking harness-internal vocabulary
   - `--json` or another structured mode when agents may consume the output
   - if agents may call the CLI repeatedly, define at least one cheap read-only
     startup probe such as `version`, `--version`, or a lightweight inspect
     command; keep that probe stable enough for standing latency measurement
   - for workflow commands whose primary caller is another agent, explicitly
     decide whether a prep/execute artifact split is the more stable contract
     than a single thick command; see `references/command-surface.md`
     prep/execute split section
   - public subcommands should expose a no-side-effect `--help` contract unless
     there is a strong documented reason not to
   - if wrappers or agents may probe the surface, separate machine-readable
     command discovery such as `commands --json` or `capabilities --json` from
     human help text
   - default stdout should stay concise for human operators; reserve full
     structured payloads for explicit `--json` or equivalent machine mode
   - reserve `-v` for `verbose`, not `version`; prefer canonical `version`
     plus optional top-level `--version` alias when the parser surface is
     already stable
   - separate binary/runtime health from repo- or install-readiness instead of
     overloading one `doctor`
   - if agent/plugin/materialized-surface discoverability matters, give it an
     explicit readiness probe rather than smuggling it into generic health
3. Decide mutation rules.
   - help probes, command discovery, and healthchecks stay read-only
   - `doctor` stays read-only
   - install and update commands must say what they changed
   - long-running mutations should show phase progress so operators can tell
     what is happening before the command finishes
   - if the product manages multiple install targets, make the registry or
     manifest decision explicit and say who cleans up stale entries
   - if `update` has a wider aggregate variant, distinguish self-update from
     tracked dependency refresh in both help text and structured output
   - readiness commands may depend on repo or local install state, but they
     should not pretend to be generic binary health probes
   - partial manual steps should still leave machine-readable breadcrumbs
   - when upgrade guidance depends on install channel, persist version
     provenance and define when cached latest-version checks may run
4. Pick the smallest honest distribution contract.
   - single checked-in entrypoint when possible
   - one canonical bootstrap script if first install is otherwise awkward
   - do not pretend update is automatic unless the host really owns it
5. Keep implementation boring.
   - prefer stdlib argument parsing unless the repo already standardizes on a
     framework
   - factor shared lifecycle logic instead of copying subcommand shapes
   - keep environment detection and filesystem mutation explicit
6. Add the right gates.
   - smoke tests for representative commands
   - `--help` smoke for stable public subcommands
   - validation for generated machine-readable state
   - JSON-shape tests for command discovery output when wrappers or agents
     depend on it
   - checks that docs and examples do not conflate help, healthcheck, and
     readiness semantics
   - a command-docs drift gate when install/update/doctor/reset/uninstall
     semantics are part of the operator contract
   - help text or JSON-shape checks when agents depend on them

## Guardrails

- Do not create a CLI only to hide unclear product boundaries.
- Do not make install, update, or reset mutate hidden files without reporting
  them.
- Do not force users to reverse-engineer the source of truth for installed
  state.
- Do not return prose-only output when an agent must continue the workflow.
- Do not add a framework dependency just to avoid writing small parser glue.
- Do not split install methods across multiple equally-primary paths unless the
  product truly supports them.
- Do not run automatic update checks in CI or other non-interactive paths by
  default.
- Do not guess upgrade commands when the runtime has not recorded install
  provenance honestly.

## References

- `references/command-surface.md`
- `references/command-conventions.md`
- `references/install-update.md`
- `references/version-provenance.md`
- `references/machine-readable-state.md`
- `references/code-shape.md`
- `references/quality-gates.md`
- `references/case-studies.md`

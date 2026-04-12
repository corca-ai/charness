---
name: create-cli
description: "Use when creating or upgrading a repo-owned CLI, bootstrap script, or command runner. Define the command surface, install/update contract, structured output, dry-run and doctor behavior, distribution path, and quality gates before spreading ad hoc shell or Python entrypoints."
---

# Create CLI

Use this when the task is to add, refactor, or normalize a command-line tool in
`charness` or another repo that `charness` is helping with.

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
   - one obvious install/bootstrap path
   - explicit `doctor`, `update`, `reset`, or `uninstall` commands when the
     product owns lifecycle state
   - `--json` or another structured mode when agents may consume the output
3. Decide mutation rules.
   - `doctor` stays read-only
   - install and update commands must say what they changed
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
   - validation for generated machine-readable state
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
- `references/install-update.md`
- `references/version-provenance.md`
- `references/machine-readable-state.md`
- `references/code-shape.md`
- `references/quality-gates.md`
- `references/case-studies.md`

# Lint Ignore Discipline

Lint suppressions are not neutral background noise. They are small local
contracts that say "the standing rule does not fully fit here yet."

Use `$SKILL_DIR/scripts/inventory_lint_ignores.py` when a repo keeps recurring
`# ruff: noqa`, `# noqa`, `# pylint: disable`, or `eslint-disable` comments.

Treat these as prompts, not automatic failures.

Review pressure points:

- blanket suppressions with no named rule
- file-level suppressions that mask a whole entrypoint or module
- policy-level ignores that remain after cleanup but lack a keep decision
- repeated ignore shapes that point to one missing structural seam
- plugin or generated mirrors that duplicate the same suppression debt

Preferred direction:

- first ask whether packaging, entrypoint, or helper structure can absorb the
  rule instead of comment-based suppression
- if suppression remains, keep it narrow, rule-specific, and cheaper than the
  structural change it is deferring
- if the same ignore appears across multiple files, treat that as an
  `AUTO_CANDIDATE` for a shared seam or import/bootstrap refactor

## Retained Policy Ignores

When a cleanup reduces active findings but intentionally leaves policy-level
ignores, record the keep decision beside the source of policy truth. Prefer
comments near `pyproject.toml` per-file ignores, ESLint config, or a repo
decision log over generated `latest.md` artifacts. Use handoff only when the
decision changes the next pickup action.

The keep decision should:

- enumerate the remaining findings by file, rule, and count
- state why each retained class is justified
- record the reviewed commit hash or review date
- name concrete revisit conditions, such as a framework upgrade, CLI schema
  redesign, wrapper deletion, or safer subprocess boundary
- distinguish intentionally retained findings from newly introduced ignores

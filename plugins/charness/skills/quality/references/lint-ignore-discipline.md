# Lint Ignore Discipline

Lint suppressions are not neutral background noise. They are small local
contracts that say "the standing rule does not fully fit here yet."

Use `$SKILL_DIR/scripts/inventory_lint_ignores.py` when a repo keeps recurring
`# ruff: noqa`, `# noqa`, `# pylint: disable`, or `eslint-disable` comments.

Treat these as prompts, not automatic failures.

Review pressure points:

- blanket suppressions with no named rule
- file-level suppressions that mask a whole entrypoint or module
- repeated ignore shapes that point to one missing structural seam
- plugin or generated mirrors that duplicate the same suppression debt

Preferred direction:

- first ask whether packaging, entrypoint, or helper structure can absorb the
  rule instead of comment-based suppression
- if suppression remains, keep it narrow, rule-specific, and cheaper than the
  structural change it is deferring
- if the same ignore appears across multiple files, treat that as an
  `AUTO_CANDIDATE` for a shared seam or import/bootstrap refactor

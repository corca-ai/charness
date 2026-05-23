# Issue Shaping

Use problem-first issue writing.

The receiver should understand what happened before seeing any proposed fix:

- situation: where the problem appeared
- experience: what user, operator, or agent got stuck on
- evidence: files, commands, output, links, issue duplicates, or state
- impact: why the current behavior is confusing, costly, or blocked
- labels: pick from the target repo's existing label vocabulary; check
  `gh label list --repo <org/repo>` if unfamiliar, and add `--label <name>`
  on the create call
- milestone: assign only a milestone the repository already has. List existing
  milestones through the selected backend first (for the `gh` backend:
  `gh api repos/<org/repo>/milestones --jq '.[].title'`), then gate the request
  with `issue_tool.py resolve-milestone` before assigning. Never create a new
  milestone to satisfy a request; if no existing milestone fits, leave it
  unassigned and say so explicitly. If the selected backend exposes no milestone
  capability, report the gap honestly rather than guessing
- source identity (required when the originating context is external —
  Slack thread, Notion page, doc, gathered artifact, web URL): canonical
  URL plus local gathered-artifact path, access mode, and freshness when
  available. See `closeout-discipline.md` for the section shape.
- weak direction: optional candidate outcome, explicitly non-binding

Avoid writing the issue as "implement this mechanism" unless the user is
explicitly filing an already-decided work item. Most cross-repo issues should
preserve enough context for the receiving agent to choose the design.

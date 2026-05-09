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
- weak direction: optional candidate outcome, explicitly non-binding

Avoid writing the issue as "implement this mechanism" unless the user is
explicitly filing an already-decided work item. Most cross-repo issues should
preserve enough context for the receiving agent to choose the design.

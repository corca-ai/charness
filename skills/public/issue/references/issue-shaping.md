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
- rework attribution (required when the issue records work that had to be
  redone, re-decided, or worked around because a charness skill's output was
  wrong or insufficient): add `--label rework` and put one
  `Causing skill: <skill>[, <skill>]` line in the body, naming the public skill
  or skills whose contract produced the rework (for example
  `Causing skill: achieve, issue`). The label is the period filter and the line
  is the attribution; `retro` reads both through
  `gh issue list --label rework` and reports rework per skill. Create the
  `rework` label once per repository if it does not exist yet; this is the
  one label the convention may add, because without it the instrument has no
  filter. Do not label ordinary bugs or feature requests `rework`
- milestone: assign only a milestone the repository already has. List existing
  milestones through the selected backend first (for the `gh` backend:
  `gh api repos/<org/repo>/milestones --jq '.[].title'`), then gate the request
  with `issue_tool.py resolve-milestone` before assigning. Never create a new
  milestone to satisfy a request; if no existing milestone fits, leave it
  unassigned and say so explicitly. If the selected backend exposes no milestone
  capability, report the gap honestly rather than guessing
- source identity and preservation (required when the originating context is
  external — Slack thread, Notion page, doc, gathered artifact, web URL):
  mark the external origin with `Source origin:`, give a stable
  `Source identity:` (canonical URL plus gathered-artifact path, access mode,
  and freshness when available), **and** preserve the original user context in
  one auditable form — a verbatim-enough `Source text:`, a
  `Re-read obligation:` (must re-read the source before resolving/closing), or
  a `Source degraded reason:` (the source was inaccessible).
  `axis: external-source-provider` — Slack is one adapter instance, not the
  schema. See `closeout-discipline.md` for the section shape and the checks.
- weak direction: optional candidate outcome, explicitly non-binding

Avoid writing the issue as "implement this mechanism" unless the user is
explicitly filing an already-decided work item. Most cross-repo issues should
preserve enough context for the receiving agent to choose the design.

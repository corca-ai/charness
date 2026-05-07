# GitHub Issue 108: Support Skill Discoverability

Source: https://github.com/corca-ai/charness/issues/108
Access: `gh issue view 108 --json number,title,state,url,author,labels,createdAt,updatedAt,body,comments`
Captured: 2026-05-07

## Source Identity

- Repository: `corca-ai/charness`
- Issue: `#108`
- Title: Make support skills discoverable when workflow language implies them
- State: open
- Author: `spilist`
- Created: 2026-05-07T00:13:13Z
- Updated: 2026-05-07T00:13:54Z

## Requested Facts

The issue reports that a session working on executable spec authoring edited
`docs/specs/**/*.spec.md` and discussed Specdown-specific syntax and report
surfaces before routing to `support/specdown`. The support skill was present in
the Charness capability inventory, but it remained easy to miss because support
skills are intentionally hidden from the default public skill list.

The desired contract is broader than one Cautilus incident: when task language
implies a support skill, Charness should surface that support skill before the
agent proceeds through nearby public workflows. For Specdown-shaped work, the
examples include `*.spec.md`, `docs/specs/**`, `run:shell`, doctest output,
check tables, `check:jq`, Specdown HTML reports, `report.json`, executable spec
phrasing, adapter checks, and reducing full-run cost during spec iteration.

The recommended next step should point to `skills/support/specdown/SKILL.md`
and the relevant references for syntax, best practices, CLI usage, reports, and
configuration before modifying or running executable specs.

## Scope Boundaries

- Do not overfit the fix to Cautilus.
- Keep Cautilus responsible for behavior-evaluation packets and its bundled
  evaluator skill.
- Keep Charness responsible for public workflow routing, support-skill
  discoverability, readable executable-spec authoring discipline, and Specdown
  support-surface discovery when Specdown is the chosen substrate.

## Open Gaps

- The issue asks for proof that workflow language can recommend
  `support/specdown` without the user naming the support skill directly.
- The proof may be deterministic; it does not require running Cautilus while the
  repo-owned Cautilus adapter is disabled.

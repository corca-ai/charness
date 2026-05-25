# Gather Record: GitHub Issue 217

## Source

- Source type: GitHub issue
- Repository: `corca-ai/charness`
- Issue: `#217` — `Make retro efficiency analysis phase-aware before labeling broad exploration as waste`
- URL: https://github.com/corca-ai/charness/issues/217
- State at gather time: open
- Labels: `feature request`
- Created: 2026-05-25T07:37:28Z
- Updated: 2026-05-25T07:37:28Z

## Access

- Access mode: authenticated local `gh` CLI, direct-cli gather provider
- Commands used:
  - `gh issue view 217 --json number,title,state,author,body,labels,comments,createdAt,updatedAt,url`
  - `gh issue view 217 --comments`
- Comments at gather time: none

## Requested Facts

The issue reports that the current `retro` efficiency framing can misclassify
intentionally broad exploration as token waste. The concrete correction from
dogfood was that broad exploration was not inherently waste; the waste was
failing to separate exploration from triage/fix phases and failing to freeze the
issue list before implementation.

The issue asks `retro` to support phase-aware efficiency analysis with these
behavior changes:

- Identify whether broad exploration was user-intended before labeling it waste.
- Add an `Exploration -> Triage -> Implementation -> Verification` transition check.
- Require triage output to classify findings as `fix now / deferred / needs user call / false positive`.
- Group efficiency audit waste candidates by phase, because the same tool pattern has different meaning before and after triage lock.
- Add counterfactual prompts about intended breadth, where triage lock should occur, what crossed into `fix now`, and which post-lock branches reopened scope.
- Keep per-run intent in the retro narrative or command flags, not durable adapter config.

## Local Context Checked

- `skills/public/retro/SKILL.md` currently requires evidence gathering, a `Waste`
  section, `Critical Decisions`, concrete next improvements, and at least one
  counterfactual lens.
- Current `retro` guidance prefers host-log probes before claiming
  token/tool-call counts, but does not require phase intent or a triage lock
  before waste attribution.
- `skills/public/retro/references/section-guide.md` defines `Waste` generically
  as effort lost through backtracking, hidden assumptions, missing verification,
  repeated reconstruction, and slow approval loops; it does not distinguish
  valuable exploration from post-triage drift.

## Review Notes

The issue is valid and aligns with current `retro` ownership. The smallest
implementation surface is likely a new retro reference for phase-aware
efficiency attribution, plus a short hook from `SKILL.md` and possibly
`section-guide.md`. If a host-log probe or audit helper is later added, it should
annotate observed tool families by phase instead of producing raw count-only
waste claims.

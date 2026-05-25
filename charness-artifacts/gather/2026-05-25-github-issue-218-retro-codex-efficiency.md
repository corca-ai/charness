# Gather Record: GitHub Issue 218

## Source

- Source type: GitHub issue
- Repository: `corca-ai/charness`
- Issue: `#218` — `Evaluate upstreaming repo-local retro Codex efficiency audit dogfood`
- URL: https://github.com/corca-ai/charness/issues/218
- State at gather time: open
- Labels: `feature request`
- Created: 2026-05-25T07:55:26Z
- Updated: 2026-05-25T07:55:56Z

## Access

- Access mode: authenticated local `gh` CLI, direct-cli gather provider
- Commands used:
  - `gh issue view 218 --json number,title,state,author,body,labels,comments,createdAt,updatedAt,url`
  - `gh issue view 218 --comments`
- Comments at gather time: one CodeRabbit auto-generated planning comment; no maintainer discussion.

## Requested Facts

The issue asks Charness to evaluate upstreaming a repo-local `retro` fork from `parental-interaction-eval` into upstream Charness.

The local dogfood reference names:

- commit `5c61c904 Add repo-local retro efficiency audit`
- local skill path `.agents/skills/retro/`
- main script `.agents/skills/retro/scripts/audit_codex_session.py`
- spec artifact `charness-artifacts/create-skill/2026-05-25-retro-codex-efficiency-spec.md`
- dogfood retro `charness-artifacts/retro/2026-05-25-codex-efficiency-dogfood.md`

The local fork added a Codex-only session efficiency evidence path that builds a compact cost map from Codex logs, prefers `~/.codex/logs_2.sqlite`, falls back to bounded TUI log scanning, supports explicit thread selection and bounded output, separates measured/proxy/unavailable signals, reports selection confidence, and avoids raw command snippets by default.

## Design Questions

The issue asks whether the audit script belongs in public `retro` or support, whether it should stay Codex-only, how to separate portable interpretation rules from host-specific parsing, how to expose token snapshots without implying exact session totals, whether token-waste prompts should auto-run the cost map, and whether #217's phase-aware interpretation should come before or alongside this script.

## Relationship to #217

#218 is an evidence-capture and host-log-analysis companion to #217. It should not replace #217's portable interpretation rules. The safer ordering is to define #217's phase-aware waste attribution contract first, then upstream the Codex analyzer as a host-specific producer of evidence that feeds that contract.


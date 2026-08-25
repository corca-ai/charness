# Documentation Principles

> Status: current
> Source of truth: this page and the linked validators
> Last verified: 2026-08-25

Charness documentation is a flat, current-state wiki. Each page answers one
question, starts with a heading and a short orientation paragraph, and links to
the executable source that proves its claims.

## Current state only

Keep `docs/` evergreen. Move superseded decisions, experiments, and session
history to `charness-artifacts/`, or delete them when they have no durable
value. The index is the entry point; it must not preserve a second catalogue.

- [Documentation index](./index.md) — the maintained page map.
- [Artifact policy](./artifact-policy.md) — where history and evidence live.
- [Docs architecture record](../charness-artifacts/spec/2026-08-25-docs-architecture-evergreen.md) — migration rationale.

## One docs lint contract

[`scripts/check-docs.sh`](../scripts/check-docs.sh) is the canonical document lint. It composes Markdown
syntax, current-doc references, awiki reachability, and lychee link checks. The
component scripts remain available for diagnosis, but quality and pre-push use
the composite receipt.

- [check-docs.sh](../scripts/check-docs.sh) — the composed gate.
- [Docs graph checks](./docs-graph-checks.md) — what awiki proves and cannot prove.
- [Lychee tool manifest](../integrations/tools/lychee.json) — managed support binary.
- [Markdown configuration](../.markdownlint-cli2.jsonc) — `MD013` is disabled.

## Authoring shape

Do not hard-wrap prose at 80 columns. A line break is meaningful only when it
improves a list, code block, or link. Use a word budget for artifacts that need
bounded context, not a sentence-length or whole-document gate for evergreen
docs. Keep examples executable and prefer links over copied policy text.

- [Authoring preflight](./authoring-preflight.md) — premise checks before editing.
- [Handoff](./handoff.md) — the short operational continuation record.
- [Quality](../charness-artifacts/quality/latest.md) — current verification receipt.

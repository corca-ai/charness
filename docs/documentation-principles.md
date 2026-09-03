# Documentation Principles

> Status: current
> Source of truth: this page and the linked validators
> Last verified: 2026-09-02

Charness documentation is a flat, current-state wiki. Each page answers one
question, starts with a heading and a short orientation paragraph, and links to
the executable source that proves its claims.

## Docs-as-code principles

Keep documentation easy to trust and easy to navigate:

- Reduce duplication so one fact does not drift across competing copies.
- Reveal intent so a reader can understand why a rule exists and what it owns.
- Let one page own one question; link related pages like a wiki instead of
  restating their contracts.
- Keep the entry surfaces small: [`README.md`](../README.md) is the minimal
  user guide, while [`AGENTS.md`](../AGENTS.md) is a minimal router pointing at
  [`docs/index.md`](./index.md).

Every `docs/*.md` page carries exactly one header line matching
`> Last verified: YYYY-MM-DD`. Update it when the page is materially verified;
[`check-docs.sh`](../scripts/check-docs.sh) rejects a page that lacks the line.

## Current state only

Keep `docs/` evergreen. A page states what is: which mechanism holds a rule,
where a thing lives, what a command does. Instructions to a reader survive
only where a command must be typed or no mechanism exists yet; the why, the
counts, and the dates go to `charness-artifacts/`. Move superseded decisions,
experiments, and session history there too, or delete them when they have no
durable value. The index is the entry point; it must not preserve a second catalogue.
When a decision supersedes a sentence, delete that sentence in the same change:
a superseded line stays quotable until it is gone, and it will be quoted in good
faith (a retired flag convention on 2026-08-14; a false claim about the plugin
mirror on 2026-09-03). Documented flags and subcommands are checked against
each command's own `--help` by the standing lane; every other sentence is held
only by this rule.

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
improves a list, code block, or link. Keep examples executable and prefer
links over copied policy text. A page grows only by displacing something:
every `docs/` page has a 1,000-word budget held by
[`check_docs_length.py`](../scripts/gates/check_docs_length.py) inside
[`check-docs.sh`](../scripts/check-docs.sh),
with the pages already over it recorded in
[`docs-length-baseline.json`](../charness-artifacts/quality/docs-length-baseline.json),
a record that only shrinks.

- [Authoring preflight](./authoring-preflight.md) — premise checks before editing.
- [Goal lifecycle](./goal-lifecycle.md) — the provider-backed continuation record.
- [Quality](../charness-artifacts/quality/latest.md) — current verification receipt.

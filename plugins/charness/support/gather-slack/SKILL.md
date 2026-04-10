---
name: gather-slack
description: "Internal support capability for gathering Slack threads into durable local markdown without asking consumer repos to reimplement Slack export helpers."
---

# Gather Slack

This is a support capability, not a public workflow concept.

Users should still reach this through `gather` when Slack thread material needs
to become a durable local asset.

## Runtime Contract

- prefer a host-provided runtime grant when one exists
- otherwise rely on a process environment `SLACK_BOT_TOKEN`
- keep provider-specific fetching and markdown conversion in this package so
  consumer repos do not have to recreate them

Use the wrapper:

```bash
./scripts/export-thread.sh \
  "https://workspace.slack.com/archives/C123/p1234567890123456" \
  skill-outputs/gather/slack-thread.md \
  "Slack Thread"
```

## Guardrails

- Do not ask the user to paste tokens into chat.
- Do not promise private Slack access when no grant or token is available.
- Preserve the source thread URL and attachment links in the exported markdown.

## References

- `references/runtime-contract.md`
- `references/provenance.md`
- `scripts/export-thread.sh`

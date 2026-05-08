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
- otherwise resolve the runtime token through the consumer repo's
  `<repo-root>/.charness/local/capability.json` (gitignored), looked up by
  the logical capability id `slack.default` (overridable through
  `CHARNESS_SLACK_CAPABILITY`)
- the wrapper invokes `charness capability env <logical-id>` to materialize the
  runtime env name from a non-secret source env name declared by the repo's
  capability profile; it does **not** advertise a direct `SLACK_BOT_TOKEN`
  process-env fallback to model-controlled agent runtimes
- a pre-set `SLACK_BOT_TOKEN` in the process environment is honored for
  ordinary operator-local CLI use only and is not part of the agent-consumable
  contract

Use the wrapper:

```bash
./scripts/export-thread.sh \
  "https://workspace.slack.com/archives/C123/p1234567890123456" \
  charness-artifacts/gather/slack-thread.md \
  "Slack Thread"
```

## Guardrails

- Do not ask the user to paste tokens into chat.
- Do not promise private Slack access when no grant or capability binding is
  available.
- Do not advertise raw process-env tokens as the agent-runtime fallback path
  in any contract or doc that ships with this support skill.
- Preserve the source thread URL and attachment links in the exported markdown.

## References

- `references/runtime-contract.md`
- `references/provenance.md`
- `<repo-root>/scripts/export-thread.sh`

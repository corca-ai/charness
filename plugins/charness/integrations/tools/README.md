# Tool Manifests

`charness` keeps external-tool ownership separate from harness knowledge.

## Files

- `manifest.schema.json`: canonical schema for tool manifests
- `<tool-id>.json`: future tool-specific manifests
- `../locks/`: generated state and lock material, never source-of-truth policy

## Contract Notes

- manifests are JSON for v1 so detection, update, and doctor flows can consume
  the same structured contract without host-specific parsing rules
- source policy lives in manifests; live state belongs in generated lock files
- `support_skill_source` is optional and should be absent when no upstream skill
  is reused
- integrations that declare `support_skill_source` should also declare
  `lifecycle.install.install_url` so agents get one exact install-doc entrypoint
- before bumping a `support_skill_source.ref`, run
  `python3 scripts/check_upstream_support_drift.py --repo-root .` to confirm the
  declared `path` still exists at the new ref (corca-ai/cautilus#32 root-cause
  prevention; standalone online probe, not part of the standing local gate)
- when broad `intent_triggers` could match generic task-text tokens (e.g.,
  filename suffixes used outside the tool's domain), declare a curated
  `strong_intent_triggers` subset; at least one matched trigger must come
  from that subset before the support skill is surfaced. Missing or empty =
  no precision gate, any matched trigger activates
- wrapper skills should be generated or declared explicitly instead of silently
  copied into the public taxonomy

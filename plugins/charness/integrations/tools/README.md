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
- wrapper skills should be generated or declared explicitly instead of silently
  copied into the public taxonomy

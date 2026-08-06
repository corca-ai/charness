Closes #482

Classification: deferred-work
JTBD: Shipped skill documentation must not tell a consumer to execute an authoring-only `skills/<kind>/<skill>/...` command path that exists in no consumer tree.
Boundary: In scope is Markdown command-carrier detection from the consumer path, repair of the 14 live kind-bearing commands, missing-export/partial-tree fail-open coverage, shared `$SKILL_DIR` anchor preservation, and source/plugin parity. Out of scope is JSON/YAML/template carrier coverage and installed-consumer runtime proof.
Resolution brief: inline (no pause) — reject source-existing kind-bearing commands independently of plugin-directory presence, report the expected `<plugin-dir>` spelling and export state, and rewrite own-skill commands to `$SKILL_DIR` while using `<plugin-dir>` for cross-skill helpers.
Implementation: Added the cohesive `scripts/portable_command_carrier.py` consumer-relative command detector and export-state diagnostics wired into `scripts/check_doc_links.py`, preserved shared anchor semantics in `check_documented_command_flags.py`, repaired 14 skill references, added discriminating source/export/partial-tree tests, synchronized plugin mirrors, and recorded quality and critique artifacts.
Prevention: The Markdown gate now refuses source-layout command carriers even when the plugin export is missing or the plugin directory is absent; focused tests pin source-only, exported, missing-export, no-plugin, `$SKILL_DIR`, and shared-anchor cases.
Critique #482: charness-artifacts/critique/2026-08-06-issue-482-command-carrier-resolution-critique.md
Behavior #482: local-only-by-contract — focused portability/plugin suites passed 123 tests; check_doc_links, documented-command flags, plugin-link, and plugin-dir gates passed; strict inventory confirmed 544 references (272 authoring and 272 shipped) with zero findings; consumer execution and remote CI are not claimed.
AI-provenance: Agent-authored direct-commit carrier; implementation, two-round fresh-eye evidence, accepted-unreviewed round-2 disposition, and non-claims are recorded in the linked artifacts.

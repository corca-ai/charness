Closes #480

Classification: deferred-work
JTBD: `<authoring-repo>/<path>` references must be checked against the Charness authoring tree even when they target `docs/` or `charness-artifacts/`, so a checked-looking reference cannot silently dangle.
Boundary: In scope is full authoring-relative path extraction/resolution, source/shipped root ownership, stale-reference repair, mirror parity, and regression coverage. Out of scope is consumer installation/runtime proof and the later non-markdown command-carrier slices.
Resolution brief: inline (no pause) — widen the authoring marker to any relative path, resolve it from the authoring source root, keep `<plugin-dir>/scripts/` on its own shipped root, and make missing targets actionable in strict inventory.
Implementation: Generalized `scripts/inventory_skill_script_references.py`, added source/shipped docs-and-artifacts fixtures and missing-target assertions, repaired two stale references, synchronized the plugin mirror, and recorded the quality and critique artifacts.
Prevention: Strict inventory now covers every `<authoring-repo>/<path>` reference in both layouts; focused tests pin existing and missing docs/artifact targets, root separation, and source/plugin parity.
Critique #480: charness-artifacts/critique/2026-08-06-issue-480-authoring-path-resolver-resolution-critique.md
Behavior #480: local-only-by-contract — focused quality tests and strict inventory confirmed 514 references (257 authoring and 257 shipped) with zero findings and zero unreadable files; remote consumer behavior is not claimed.
AI-provenance: Agent-authored direct-commit carrier; implementation, evidence, non-claims, and bounded fresh-eye review are recorded in the linked artifacts.

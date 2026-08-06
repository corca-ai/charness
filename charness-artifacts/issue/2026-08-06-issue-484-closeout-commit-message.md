Closes #484

Classification: deferred-work
JTBD: `skills/shared/**` ships to consumers and must be governed by an explicit portable package boundary so shared references cannot silently bypass portability checks.
Boundary: In scope is the shared shallow package root, package-relative path resolution, shared plugin-level helper placeholders, source/plugin parity, and Markdown portability regression tests. Out of scope is typed non-Markdown carrier discovery and installed-consumer runtime proof.
Resolution brief: inline (no pause) — treat `skills/shared` as a portable package rooted at `skills/shared`, use an explicit repo-relative package path for the shallow layout, and spell plugin-level helpers as `<plugin-dir>/scripts/...`.
Implementation: Updated `scripts/check_doc_links.py` and its plugin mirror, added shared package-root and unmarked-tree tests, repaired the two shared RCA helper commands, synchronized mirrors, and recorded the quality and critique artifacts.
Prevention: Shared documents now enter the same unmarked-tree, portable-absolute, and portable-link boundary as other portable packages; focused tests pin valid shared helpers, outside-root refusals, plugin references, and source/plugin parity.
Critique #484: charness-artifacts/critique/2026-08-06-issue-484-shared-portable-package-resolution-critique.md
Behavior #484: local-only-by-contract — focused portability/plugin suites passed 77 tests; source and shipped link/plugin gates passed, and strict inventory confirmed 518 references (259 authoring and 259 shipped) with zero findings; consumer runtime and remote CI are not claimed.
AI-provenance: Agent-authored direct-commit carrier; implementation, evidence, ambient non-claim, and bounded fresh-eye review are recorded in the linked artifacts.

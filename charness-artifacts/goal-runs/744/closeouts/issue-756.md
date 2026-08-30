Classification: feature

Jtbd: Reviewer backend command construction, bounded execution, normalization, and typed backend failure need one owner that can evolve independently from lifecycle, validation, receipts, and approval projection.
Decision: Extract the cohesive backend boundary into `reviewer_worker_backend.py`; retain lifecycle and publication in `reviewer_worker_runtime.py`, with no new backend or lifecycle redesign.
Boundary: The backend owner ends at normalized pending output or typed process failure; runtime remains the owner of capability lifecycle, schema validation, provenance joining, receipts, publication, and approval projection.
Resolution Brief: Both supported backends now construct, execute, and normalize through one backend module, while the public worker entrypoint and typed lifecycle contract remain compatible.
Prevention: Retain the source-ownership discriminator that refuses duplicated command/normalization definitions in runtime, plus Codex/Claude normalization and typed timeout/interruption/non-zero-exit fixtures.
Implementation: Commit `ea8084f06845d5e262259a3485e06d9fcf9d5308` introduced the backend owner and runtime delegation.
Critique: charness-artifacts/critique/2026-08-30-issue-756-reviewer-backend-resolution.md
Behavior #756: verified on the integrated branch through 18 backend/runtime tests in 2.75s; an independent Luna slice passed six backend-owner tests and three adjacent runtime discriminators, including Codex/Claude normalization and typed timeout/interruption/non-zero-exit behavior.
AI-provenance: Agent-authored manual closeout from the live issue, integrated source, focused tests, official tokei length checks, and a distinct Luna fresh-eye. Provider state is not behavior proof.

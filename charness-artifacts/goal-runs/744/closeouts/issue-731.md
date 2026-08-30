Classification: feature

Jtbd: Operators need one durable reviewer lifecycle that preserves useful partial progress across timeout or interruption while making approval possible only for terminal, identity-bound, schema-valid findings.
Decision: Add typed accepted/running/partial/timed-out/interrupted/terminal projection, preserve failed worker bytes with identity descriptors, and keep partial, timeout, interruption, process exit, and non-empty output approval-ineligible.
Boundary: This closeout implements the frozen #731 partial-progress Work Item after #756; it does not add a backend, dashboard, credentialed transport, consumer topology policy, or a second partial-verdict protocol.
Resolution Brief: Worker receipts and delivery history now retain validated partial-output carriers, lifecycle projects them through one stable status surface, and terminal pass/block behavior remains distinct from runner success or failure.
Prevention: Retain typed lifecycle/history validation, partial-output size/SHA binding, process-group timeout/interruption tests, terminal provenance checks, pass/block controls, and the named invocation/partial-output ownership split enforced by the official tokei gate.
Implementation: Commit `e7d5fa707` added lifecycle and partial-output behavior; integration repair `8c144f2c7` separated invocation and partial-log owners without weakening the contract.
Critique: charness-artifacts/critique/2026-08-30-issue-731-reviewer-lifecycle-resolution.md
Behavior #731: verified on final integrated HEAD through 93 focused lifecycle, delivery, worker/backend, runner, and semantic-command tests in 16.23s; an independent Luna fresh-eye reran the bounded 93-test surface and returned SHIP.
AI-provenance: Agent-authored manual closeout from the live issue, frozen Work Item, integrated source, focused tests, official tokei gate, and an independent Luna review. Provider state is not behavior proof.

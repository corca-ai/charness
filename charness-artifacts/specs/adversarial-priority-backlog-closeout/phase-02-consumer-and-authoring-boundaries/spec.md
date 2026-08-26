# Phase 2: Resolve consumer and authoring boundaries

Status: planned
Goal: [adversarial-priority-backlog-closeout](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)

## Objective

Close the live consumer-selection, authoring, scaffold, adapter, dependency, and specialized-routing defects with the smallest owner-shaped changes.

## Scope In

- #721, #715, #692, #667, #637, #634, #628, and #546
- repo-local, exported-plugin, and installed-consumer behavior where each issue requires it
- targeted authoring and final-consumer tests

## Scope Out

- generic artifact machinery where a consumer-owned command already answers the JTBD
- broad rewrites of all skills or all operating documents
- release publication without an explicit phase-scoped grant

## Dependencies

- Phase 1 premise and ownership disposition for each issue
- #723/#722 ownership diet applied before adding new artifacts or validators

## Completion Criteria

- Each live issue has a behavior-level fix at its actual producer/consumer boundary
- Each stale or over-scoped residual is split or closed without preserving an umbrella for archival convenience
- Source/export/installed claims are separated and only the executed channel is claimed

## Verification

- Focused tests exercise the prescribed operator path and the first consumer that can misread it
- Package mirrors and generated surfaces are synchronized when touched
- GitHub closeout comments state behavior proof or an explicit typed non-claim per issue

## Non-Claims

- A source-only test does not prove installed-worker adoption
- An optional helper existing does not prove the prescribed workflow routes through it
- No unrelated cleanup is bundled merely because a file is nearby

## Failure Handling

If verification fails, use `debug` and a 5-whys root-cause pass. Record the structural pattern and repair before retrying; a retry alone is not completion.

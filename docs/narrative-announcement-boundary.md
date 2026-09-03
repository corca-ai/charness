# Narrative And Announcement Boundary

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

`narrative` aligns durable truth and compresses it into one audience-neutral
brief skeleton; `announcement` adapts that story for one audience, language,
tone, length, and delivery channel.

- [Boundary rationale](../charness-artifacts/spec/2026-09-03-narrative-announcement-boundary.md) — the spec-phase record.

## Fixed Decisions

- `narrative` owns durable truth alignment first.
- `narrative` may also derive one audience-neutral brief skeleton from that
  aligned truth.
- `narrative` adapter may declare `brief_template` as an ordered list of brief
  section labels, held by [test_narrative_adapter.py](../tests/quality_gates/test_narrative_adapter.py).
- `announcement` owns audience adaptation, language adaptation, channel fit,
  and backend delivery.
- `announcement` adapter may declare one logical delivery capability when a
  human-backend delivery path needs reusable private access.

## Non-Goals

- teaching `narrative` to post to chat backends
- turning `announcement` into the source-of-truth alignment skill
- embedding audience-local formatting rules into narrative adapter defaults

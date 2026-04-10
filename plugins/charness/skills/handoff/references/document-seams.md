# Document Seams

`handoff` is portable, so it should not force one universal path across every
host.

## Canonical Rule

If no host-specific decision exists yet, default to
`skill-outputs/handoff/handoff.md`.

If a repo already uses a better durable handoff surface, move that choice into
the handoff adapter instead of the skill body.

## Non-Goals

- one mandatory filename for every host
- preserving a chronological journal
- duplicating the same state across many docs

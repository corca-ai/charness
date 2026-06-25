# Retro Prepare Packet

The retro prepare packet is the retro-side sibling of critique's prepare packet:
adapter-declared context that should be read before turning a slice into lessons.
It prevents retros from rediscovering the same changed surfaces, known
non-goals, or deferred context after the work has already moved on.

## When It Fires

Run `$SKILL_DIR/scripts/prepare_packet.py --repo-root . --prepared-for "<label>"`
when `retro-adapter.yaml` declares one or more `packet_sections`.

The runner emits:

- `<output_dir>/<slug>-packet.json`
- `<output_dir>/<slug>-packet.md`

The markdown packet is the reader-facing source. The JSON packet is the durable
envelope for scripts and validators.

## Envelope

The packet uses kind `charness.retro_prepare_packet` and version `1`. Section
execution, static includes, script includes, and changed-ref handling reuse the
same producer contract as critique packets. For committed-diff retros, pass
`--changed-ref`, `--commit`, or `--range`; script sections receive the value as
`CHARNESS_RETRO_CHANGED_REF`.

## Consumer Contract

- Read the packet before writing the retro when sections exist.
- Record `Packet Consumed: <path>` in the retro or closeout artifact.
- If no sections exist, record `Packet Consumed: n/a (no adapter sections)` when
  the retro needs to explain why no packet was used.
- Treat packet contents as evidence, not as a conclusion. A packet can focus the
  retro; it cannot decide whether waste, a lesson, or a follow-up exists.

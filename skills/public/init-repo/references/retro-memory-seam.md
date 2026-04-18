# Retro Memory Seam

Seed this only when the repo wants durable retrospective pickup rather than
chat-only retros.

## Goal

Give future sessions one stable place to read the latest recurring traps without
forcing a full weekly retro every time.

## Seeded Files

- [`.agents/retro-adapter.yaml`](../../../../.agents/retro-adapter.yaml)
- [`charness-artifacts/retro/recent-lessons.md`](../../../../charness-artifacts/retro/recent-lessons.md)

## Preferred Path

Use `scripts/seed_retro_memory.py` to create the initial seam:

```bash
python3 "$SKILL_DIR/scripts/seed_retro_memory.py" --repo-root .
```

This seeds:

- `summary_path: charness-artifacts/retro/recent-lessons.md`
- a stable `snapshot_path`
- empty `evidence_paths` and `metrics_commands` that the repo can tighten later
- an expectation that [`AGENTS.md`](../../../../AGENTS.md) should list [`charness-artifacts/retro/recent-lessons.md`](../../../../charness-artifacts/retro/recent-lessons.md)
  in repo memory when the seam is enabled

## Guardrails

- keep it opt-in; not every repo needs durable retro memory on day one
- do not seed hidden telemetry or background collection
- prefer one stable digest path over many ad hoc retro summaries

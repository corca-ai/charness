# Retro Memory Seam

Seed this only when the repo wants durable retrospective pickup rather than
chat-only retros.

## Goal

Give future sessions one stable place to read the latest recurring traps without
forcing a full retro every time. A compact Markdown digest is optional; a repo
that keeps its ledger as the sole lesson surface may declare `summary_path: null`.

## Seeded Files

- `<repo-root>/.agents/retro-adapter.yaml`
- `<repo-root>/charness-artifacts/retro/recent-lessons.md` (optional digest)

## Preferred Path

Use `$SKILL_DIR/scripts/seed_retro_memory.py` to create the initial seam:

```bash
python3 "$SKILL_DIR/scripts/seed_retro_memory.py" --repo-root .
```

This seeds:

- `summary_path: charness-artifacts/retro/recent-lessons.md`
- empty `evidence_paths` and `metrics_commands` that the repo can tighten later

The lesson ledger remains a separate optional memory/selection surface. A repo
that keeps the ledger as its only lesson surface may declare `summary_path: null`.
Setup does not emit session receipts, inject session context, or create a
retro-disposition continuity obligation.

## Guardrails

- keep it opt-in; not every repo needs durable retro memory on day one
- do not seed hidden telemetry or background collection
- prefer one stable digest path over many ad hoc retro summaries

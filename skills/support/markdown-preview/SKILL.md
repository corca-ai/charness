---
name: markdown-preview
description: "Internal support capability for rendering checked-in Markdown into durable preview artifacts so doc-facing workflows can review real terminal output instead of raw source alone."
---

# Markdown Preview

This is a support capability, not a public workflow concept.

Use it when a doc-facing workflow needs rendered terminal snapshots for
README, docs, or spec prose review.

This is not a rule that every Markdown review must use `glow`. When the target
is an executable `*.spec.md` whose authoritative reader surface is a Specdown
report, review the rendered Specdown report instead of treating a raw Markdown
preview as equivalent.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/render_markdown_preview.py" --repo-root . --file README.md --width 80 --width 100
python3 "$SKILL_DIR/scripts/render_markdown_preview.py" --repo-root . --changed-only
python3 "$SKILL_DIR/scripts/render_markdown_preview.py" --repo-root . --config .agents/markdown-preview.yaml
python3 "$SKILL_DIR/scripts/check_glow_backend.py"
```

## Guardrails

- Do not claim rendered review happened when the run fell back to degraded
  source snapshots.
- Do not treat backend-error artifacts as readability proof; fix the renderer
  or record an explicit waiver before delivery-ready closeout.
- Do not hardcode one repo's doc scope into the support skill when config can
  carry that choice.
- Do not use markdown-preview as a substitute for a rendered Specdown report
  when reviewing executable spec documents.
- Do not turn readability into a binary fail gate before the repo has
  established what should be reviewed and at which widths.

## References

- `references/runtime-contract.md`
- `scripts/render_markdown_preview.py`

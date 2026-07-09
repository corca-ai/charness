# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-07-09T22:01:26Z
- **Prepared for**: outcome-driven feedback closeout
- **Adapter**: `.agents/retro-adapter.yaml`
- **Sections**: 1
- **Overall ok**: True


Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/quality/latest.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md
- charness-artifacts/quality/2026-07-10-outcome-driven-feedback.md
- charness-artifacts/retro/2026-07-10-session-retro.md

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/quality/latest.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md, charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md, charness-artifacts/quality/2026-07-10-outcome-driven-feedback.md, charness-artifacts/retro/2026-07-10-session-retro.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-mutation-artifacts: Prompt-mutation experiment manifests, configs, scores, judge packets, and reports.
  source matches: charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md
  verify: for path in charness-artifacts/prompt-mutation/*.json; do [ -e "$path" ] && { python3 -m json.tool "$path" >/dev/null || exit $?; }; done
- retro-lesson-selection-index: Generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/recent-lessons.md, charness-artifacts/retro/2026-07-10-session-retro.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check

Planned sync commands before validators:
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
```

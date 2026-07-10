# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-07-10T00:50:24Z
- **Prepared for**: repo-wide quality speed release closeout retro
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
- charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md
- charness-artifacts/release/latest.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- charness-artifacts/probe/2026-07-10-repo-wide-quality-speed-release.json
- charness-artifacts/retro/2026-07-10-repo-wide-quality-speed-release.md

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md, charness-artifacts/release/latest.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md, charness-artifacts/retro/2026-07-10-repo-wide-quality-speed-release.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-07-10-repo-wide-quality-speed-release.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/recent-lessons.md, charness-artifacts/retro/2026-07-10-repo-wide-quality-speed-release.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check

Planned sync commands before validators:
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
```

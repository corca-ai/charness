# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-08-20T19:19:43Z
- **Prepared for**: release-candidate-session
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
- charness-artifacts/retro/lesson-ledger.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-21-release-candidate.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-21-release-candidate.md

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/retro/lesson-session-receipts/2026-08-21-release-candidate.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, python3 scripts/check_docs_graph.py --repo-root . || { [ "$?" -eq 3 ] && ! command -v awiki >/dev/null; }, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/lesson-session-receipts/2026-08-21-release-candidate.md
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-contract-register: Local cited lesson state and the explicit pre-contract-mutation register probe.
  source matches: charness-artifacts/retro/lesson-ledger.json, charness-artifacts/retro/lesson-session-receipts/2026-08-21-release-candidate.json
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 scripts/check_contract_register.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_lesson_lifecycle.py tests/test_contract_register.py

Planned sync commands before validators:
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

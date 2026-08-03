# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-03T21:24:47Z
- **Prepared for**: Slice A repaired selector and six-row ledger
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `c042790f9a20c2719b928cd7be2596b4600ef4ca582fc018273326a7a9bb90a8`
- **Reviewed paths**: 6
- **Sections**: 2
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/gather/latest.md
- charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md
- charness-artifacts/critique/2026-08-03-211703-packet.json
- charness-artifacts/critique/2026-08-03-211703-packet.md
- charness-artifacts/critique/2026-08-04-slice-a-selector-decision-premortem.md
- charness-artifacts/gather/2026-08-04-goal-issue-sources.md

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/gather/latest.md, charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md, charness-artifacts/critique/2026-08-03-211703-packet.md, charness-artifacts/critique/2026-08-04-slice-a-selector-decision-premortem.md, charness-artifacts/gather/2026-08-04-goal-issue-sources.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-03-211703-packet.json, charness-artifacts/critique/2026-08-03-211703-packet.md, charness-artifacts/critique/2026-08-04-slice-a-selector-decision-premortem.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

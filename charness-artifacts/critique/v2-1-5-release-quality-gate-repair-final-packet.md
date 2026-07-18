# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-18T18:23:04Z
- **Prepared for**: v2.1.5 release quality gate repair
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `ba08ae22e5673490fae4d53f74ca3b6e137db8476b1e5b2ac5252d97a346645b`
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
- charness-artifacts/debug/2026-07-19-critique-scaffold-binding-opt-in.md
- charness-artifacts/debug/2026-07-19-release-quality-contract-gap.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/quality/dup-ratchet-baseline.json
- charness-artifacts/quality/dup-review.json
- charness-artifacts/critique/v2-1-5-release-quality-gate-repair-final-packet.json
- charness-artifacts/critique/v2-1-5-release-quality-gate-repair-final-packet.md

Owning surfaces:
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/debug/2026-07-19-critique-scaffold-binding-opt-in.md, charness-artifacts/debug/2026-07-19-release-quality-contract-gap.md, charness-artifacts/critique/v2-1-5-release-quality-gate-repair-final-packet.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-ratchet-baseline.json, charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json >/dev/null
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/v2-1-5-release-quality-gate-repair-final-packet.json, charness-artifacts/critique/v2-1-5-release-quality-gate-repair-final-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-07-19-critique-scaffold-binding-opt-in.md, charness-artifacts/debug/2026-07-19-release-quality-contract-gap.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check

Planned sync commands before validators:
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
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

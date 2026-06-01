# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-06-01T23:27:04Z
- **Prepared for**: workflow-review Slice 4 sibling-pattern audit
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/quality/2026-06-02-workflow-review-sibling-pattern-audit.md

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/quality/2026-06-02-workflow-review-sibling-pattern-audit.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- The retro skill does not consume this packet today. A retro-side prepare slot (retro-adapter.yaml packet_sections) is a separate follow-up.
```

## Slice Review Contract

Intent:

- Review `charness-artifacts/quality/2026-06-02-workflow-review-sibling-pattern-audit.md`.
- The slice is a sibling-pattern audit for the active workflow-review goal, not
  an implementation slice.
- The user explicitly challenged the phrase "expression difference" as likely
  over-coupled/source-guard reasoning. Treat that concern as first-class.

Expected invariant:

- A finding is actionable only when a producer/adapter/source emits a field,
  diagnostic, readiness decision, closeout claim, or status that a final
  consumer can misread.
- Exact wording differences are not enough unless a hard gate, validator, or
  carrier parser depends on that wording.
- Advisory phrase detectors may remain review state when their enforcement tier
  is `NON_AUTOMATABLE` and they do not block closeout.

Evidence used:

- `inventory_adapter_gate_design.py` found two
  `script.brittle_review_phrase_detector` rows, both `NON_AUTOMATABLE`.
- `inventory_brittle_source_guards.py --json` found `source_guard_count=0`,
  `fragile_count=0`, and no warnings over bounded roots.
- `inventory_public_spec_quality.py --json` found public-spec
  `source_guard_row_count=0`.
- `inventory_skill_ergonomics.py --json` found zero heuristic findings across
  checked public/support skills, while still requiring prose review.
- `docs/deferred-decisions.md` D19 already owns current-pointer scanner
  generalization until a second adapter-resolved bypass appears.

Out of scope:

- Do not file or close GitHub issues in this critique.
- Do not require a broad framework rewrite unless the audit hides a concrete
  final-consumer break.
- Do not use issue numbers or exact phrases as the primary scan key.

Reviewer questions:

1. Does any `rejected for code change` disposition actually hide a hard-gate or
   final-consumer coupling?
2. Is F3 adequately deferred to D19, or should this goal create a new tracked
   issue despite the existing deferral?
3. Is the audit underweighting the user's source-guard concern, or overcorrecting
   by refusing useful deterministic enforcement?
4. Are there missing sibling surfaces in source resolution, diagnostic
   propagation, placeholder/readiness gates, or closeout disposition that should
   be scanned before Slice 4 is called complete?

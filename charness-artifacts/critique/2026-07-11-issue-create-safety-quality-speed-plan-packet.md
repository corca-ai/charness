# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-11T03:36:38Z
- **Prepared for**: issue-create safety quality speed goal
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
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
- charness-artifacts/goals/2026-07-11-issue-create-safety-quality-speed-sweep.md

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/goals/2026-07-11-issue-create-safety-quality-speed-sweep.md
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
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

## Fresh-Eye Satisfaction

parent-delegated — three distinct decision-premortem angles and one separate
counterweight consumed this packet. Parent fingerprint verification reported no
worktree or index drift after every reviewer.

## Boundary Ownership

- Producer: the Before-phase shapes the activation contract from user intent,
  issue evidence, and measured quality/runtime signals.
- Consumer: the activated achieve run uses the goal to select and verify local
  implementation slices.
- Owning surface: the goal artifact before activation; execution-phase ownership
  remains split between release rendering/order and issue carrier semantics.
- Verdict: single-surface

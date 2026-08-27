# Narrative review

Date: 2026-08-27

## Source map

- [README.md](../../README.md)
- [AGENTS.md](../../AGENTS.md)
- [docs/index.md](../../docs/index.md)
- [docs/development.md](../../docs/development.md)
- [docs/workflow-routes.md](../../docs/workflow-routes.md)
- [docs/support-skill-policy.md](../../docs/support-skill-policy.md)
- [docs/public-skill-validation.md](../../docs/public-skill-validation.md)
- [docs/host-packaging.md](../../docs/host-packaging.md)
- [charness-artifacts/quality/latest.md](../quality/latest.md)

## Narrative drift

- The root README, AGENTS file, and docs index had each become a partial
  handbook, so first-touch routing required reading repeated policy.
- Setup's default references and generator injected routing, commit, artifact,
  and session-oriented prose into consumer root files.
- The previous narrative record described a removed session-start model and a
  handoff surface as if they were current.

## Updated truth

- README owns installation and the first successful prompt; the docs index owns
  discovery; deeper pages own procedures.
- AGENTS.md is a short router. `CLAUDE.md` is compatibility, not a second
  source of truth.
- Setup's default is a small flat wiki. Existing AGENTS content is preserved;
  an explicit compact command is available when the owner elects to replace it.
- Goal progress is provider-backed and workflow-owned. There is no required
  session-start hook, standalone handoff file, or duplicate setup routing
  probe.
- `skills/public/` remains canonical and the plugin tree remains generated.

## Brief

### One-line summary

Charness now presents one short path: README for first success, AGENTS for
routing, docs/index for discovery, and owner pages for detail.

### Current contract

The user asks in ordinary language. Setup creates or proposes only the core
operating surfaces and evidence-triggered seams. Quality, release, retro,
issue, and proof workflows own their own deeper contracts.

### What changed

- Removed the setup routing renderer and its dedicated onboarding/eval path.
- Removed setup's root-file detectors for artifact commit prose and commit
  discipline; those were duplicated workflow instructions.
- Compressed setup references and added an explicit digest-bearing `--compact`
  replacement path for an overgrown AGENTS.md.
- Compressed README, AGENTS.md, docs/index.md, and development.md.

## Claim audit

- Claim: the first-touch documents are smaller and non-duplicative.
  Evidence: the current files and the docs receipt inspect their links and
  structure; semantic usefulness of every deeper page is not claimed here.
- Claim: setup no longer creates the removed root policies.
  Evidence: the generated template and focused setup tests cover the create,
  preserve, compact, and conflict paths.
- Claim: the installed host has the same updated skill content.
  Evidence: the canonical exporter was run; final release/package validation is
  still required before publication.

## Non-claims

- This record does not claim that every historical page under `docs/` is ready
  to delete; current owner and consumer references still need an inventory.
- This record does not claim a public release, hosted issue update, or external
  consumer dogfood until those boundaries are separately read back.

## Next step

Run the docs receipt and full release lane, then use their concrete failures to
remove only remaining stale owners or repair their links. Do not recreate a
session hook, handoff artifact, or setup-side mirror of another workflow.

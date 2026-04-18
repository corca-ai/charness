# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `check-doc-links` backtick file-ref rule + required `lychee` for internal link integrity
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: mechanical rewrite of silently-rotting backtick file references into
  markdown links across checked-in docs, plus documentation and lint stance
  updates; no semantic prompt changes intended

## Prompt Surfaces

- `AGENTS.md`
- `.agents/quality-adapter.yaml`
- `skills/public/create-skill/references/adapter-pattern.md`
- `skills/public/find-skills/SKILL.md`
- `skills/public/gather/SKILL.md`
- `skills/public/gather/references/adapter-contract.md`
- `skills/public/gather/references/document-seams.md`
- `skills/public/handoff/SKILL.md`
- `skills/public/handoff/references/adapter-contract.md`
- `skills/public/handoff/references/document-seams.md`
- `skills/public/handoff/references/spill-targets.md`
- `skills/public/hitl/SKILL.md`
- `skills/public/impl/SKILL.md`
- `skills/public/impl/references/adapter-contract.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/agent-docs-policy.md`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/init-repo/references/greenfield-flow.md`
- `skills/public/init-repo/references/normalization-flow.md`
- `skills/public/init-repo/references/operator-acceptance-synthesis.md`
- `skills/public/init-repo/references/probe-surface.md`
- `skills/public/init-repo/references/retro-memory-seam.md`
- `skills/public/narrative/SKILL.md`
- `skills/public/narrative/references/adapter-contract.md`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/quality/references/automation-promotion.md`
- `skills/public/quality/references/bootstrap-posture.md`
- `skills/public/quality/references/entrypoint-docs-ergonomics.md`
- `skills/public/quality/references/operability-signals.md`
- `skills/public/quality/references/prompt-asset-policy.md`
- `skills/public/quality/references/proposal-flow.md`
- `skills/public/quality/references/security-npm.md`
- `skills/public/quality/references/security-overview.md`
- `skills/public/quality/references/security-pnpm.md`
- `skills/public/quality/references/security-uv.md`
- `skills/public/release/SKILL.md`
- `skills/public/release/references/adapter-contract.md`
- `skills/public/release/references/install-surface.md`
- `skills/public/retro/SKILL.md`
- `skills/public/retro/references/adapter-contract.md`
- `skills/public/spec/SKILL.md`
- `skills/support/markdown-preview/SKILL.md`
- `skills/support/specdown/SKILL.md`

## Commands Run

- `python3 scripts/check-doc-links.py --repo-root .`
- `./scripts/check-links-internal.sh`
- `./scripts/check-links-external.sh`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: all four checked-in routing cases still pass after the
  mechanical rewrite; converted `` `path/to/file.ext` `` and
  `` `ROOT_FILE.ext` `` tokens into markdown links without altering the
  conceptual prompt surface

## Follow-ups

- consider extending the rule to bare-basename refs (e.g., `` `check-doc-links.py` ``)
  once we agree on the ambiguity policy for multi-match basenames

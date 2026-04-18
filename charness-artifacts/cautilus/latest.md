# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: explicit file-reference convention — `./` prefix on relative link
  targets + backtick file-reference rule + required `lychee` for internal
  link integrity (continuation of earlier backtick-rewrite slice)
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: mechanical rewrite so every file reference in prose is
  syntactically distinguishable from a concept token; adds structural
  prevention against path-less backtick references (`unique-basename` catch,
  `./` backtick catch, link-target-must-start-with-`./` rule) without
  changing any instruction-surface routing semantics

## Prompt Surfaces

- `AGENTS.md`
- `skills/public/handoff/references/adapter-contract.md`
- `skills/public/handoff/references/spill-targets.md`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/narrative/references/adapter-contract.md`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/quality/references/coverage-floor-policy.md`
- `skills/public/quality/references/prompt-asset-policy.md`
- `skills/public/release/references/adapter-contract.md`
- `skills/public/retro/references/adapter-contract.md`
- `skills/support/markdown-preview/SKILL.md`
- `skills/support/specdown/SKILL.md`

(Earlier slice of this series also rewrote backticked file references
across 43 additional prompt-surface paths; those rewrites are already
folded into HEAD and re-verified under the stricter rule in this slice.)

## Commands Run

- `python3 scripts/check-doc-links.py --repo-root .`
- `./scripts/check-links-internal.sh`
- `./scripts/check-links-external.sh`
- `python3 scripts/migrate-backtick-file-refs.py --repo-root .`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: all four checked-in routing cases still pass after the
  `./` prefix migration and stricter backtick rule; the rewrite is
  syntactic only (markdown renderers treat `./foo` and `foo` identically)
  so prompt semantics are unchanged while file references are now
  structurally separated from concept tokens

## Follow-ups

- document the convention in [operator-onboarding narrative](../../README.md)
  when next editing the top-level README so external adopters see the
  rationale before hitting the linter

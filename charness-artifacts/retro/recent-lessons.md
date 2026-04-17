# Recent Retro Lessons

## Current Focus

- This session closed GitHub issues #25-#31, then corrected the retro scope:
  the key lesson is how charness development should have discovered those
  dogfood failures before sibling repos exposed them.

## Repeat Traps

- Charness tested many scripts as producers, but not enough skills as products
  consumed by an agent under realistic prompts.
- Greenfield/bootstrap paths got more validation than mature-repo sanity-check
  paths, which delayed #30.
- Public skill frontmatter was treated as documentation rather than classifier
  input, which delayed #28, #29, and #31.
- Quality contracts lacked hostile prose/source mutation fixtures, which delayed
  #27.
- Narrative dogfood did not use charness's own first-touch surfaces enough,
  which delayed #26.
- Running generated-surface sync or version mutations in parallel with
  validators created false failures and misleading drift.
- If a repo treats version bumps as published releases, do not leave the slice
  at bump+push. Encode tag and GitHub release in one repo-owned publish helper.

## Next-Time Checklist

- workflow: before closing a skill-behavior slice, run one realistic consumer
  prompt using only the surfaces an agent would actually see.
- workflow: keep a mature-repo fixture corpus for `init-repo` and `quality`.
- workflow: test concrete prompt routing against public skill descriptions and
  generated AGENTS hints.
- workflow: keep `mutate -> sync -> verify -> publish` as a hard phase order,
  and reserve parallelism for read-only inspection only.
- capability: add a dogfood matrix helper for prompt/repo shape, expected skill,
  expected artifact, and acceptance evidence.
- memory: producer-side gates are not enough; charness also needs
  consumer-side dogfood.

## Sources

- `charness-artifacts/retro/2026-04-16-issue-closeout-premortem.md`

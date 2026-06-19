# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Chunk 1 (item-5 dup-ratchet slice 1 + #393) DONE this session.** Three
  commits on top of the prior batch: #393 nose-script coverage; the 16-file
  batch coverage debt; item-5 slice 1 dup-review overlay + seed.
- **Push status:** this session's closing steps were the authoritative
  changed-line gate over the batch, broad `quality_gates`, a fresh-eye critique,
  then a push. Verify the outcome with `git log --oneline origin/main..HEAD`
  (empty = the batch landed; non-empty = push pending, pick up there).
- **#393** (mutation regression) closes on the next *scheduled* mutation run per
  its own contract (a `workflow_dispatch` cannot prove a changed-line fix); the
  local gate over `1d5b11c5..HEAD` already shows the nose scripts non-blocking.
- **Discovery folded in:** the held batch carried a 16-file changed-line gap
  beyond #393 (the #390 `a741e613` bootstrap-shim convergence + gate-4 doc-dup
  work) — same recurrence class, fixed with discovery-based in-process coverage
  tests so the push does not re-file a fresh regression.

## Next Session

- **Item-5 slice 2** (the ratchet's teeth): standalone escalation-ladder gate
  script consuming the seeded
  [dup-review.json](../charness-artifacts/quality/dup-review.json), `dup_ratchet`
  adapter wiring in [quality-adapter.yaml](../.agents/quality-adapter.yaml),
  portability + escalation acceptance tests (closes C5). Open points are listed
  under `## Probe Questions` / the slice-1 block in the
  [spec](../charness-artifacts/spec/boy-scout-dup-ratchet.md): structural-field
  fixable proposal UX, whether `unreviewed` blocks, baseline-`key`↔`family_id`
  reconciliation.
- **Remaining gate items** (B1 advisory pattern, fresh-eye + broad closeout):
  doc-links -> lychee BUY + demote backtick/bare-mention to advisory;
  validate_critique_artifacts (keep tier-honesty, demote rest);
  validate_skill_ergonomics export-leak arm (DELICATE adapter split).
- **Untouched original tracks / open issues:** SRP skill-body reduction +
  [#391](https://github.com/corca-ai/charness/issues/391) extractions + tool_version
  stamp; #387 one-pass goal-closeout shape; #392 gather X/Twitter; #371
  agent-browser orphan teardown.

## Discuss

- Item-5 slice-2 design open points (above) want resolution before the gate is
  built — especially baseline-`key`↔`family_id` reconciliation if the overlay
  should import baseline identities.

## References

- [item-5 spec](../charness-artifacts/spec/boy-scout-dup-ratchet.md),
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [mutation-testing reference](../skills/public/quality/references/mutation-testing.md),
  [design north star](./design-north-star.md)

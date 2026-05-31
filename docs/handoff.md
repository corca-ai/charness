# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`**. A bare
  `/handoff` fires chunked routing (#249); the chunker unions the **live
  open-issue backlog** with the list below, so `## Next Session` is a
  curation/sequencing memo, not the full queue. Then read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **`main` local ahead of `origin/main`; not pushed.** The mutation-gate-health
  achieve goal is complete locally. Final closeout is staged in the branch
  history: #266 was closed by the staged-hook/predict-commit fix, and the final
  closeout commit closes #262, #219, and #267 while intentionally leaving #261
  open for #265.
- **Mutation gate proof complete locally:** the current next-run changed-line
  range `6d85aec..HEAD` ended with `blocking=[]`; host-hook debt over
  `9ee91ff..HEAD` also ended with `blocking=[]`; no push or live GitHub Actions
  mutation run has been performed.
- **New follow-ups filed from retro:** #269 guards achieve artifacts against
  stale mutable-HEAD SHA wording; #270 binds targeted mutant proof to exact
  gate-reported lines before mutation.
- Release line still **v0.13.0** (no release this session).
- **#264 remains the next curated implementation chunk** (follow-up to #250):
  build the precise portability guard in the skill-portability lib
  (author-only doc/test cites, with operator-surface allowlist + marker escape
  hatch), sweep the same-class cross-skill cites, and add the rule sentence to
  the portable-authoring reference.

## Next Session

> Chunk the live backlog rather than trusting this list verbatim.

1. **#264** — portability guard + cross-skill cite sweep (the deferred half of
   #250). Cheap, well-scoped; the discriminator/allowlist live in the issue body.
2. **#265 / #261** — residual exhaustive survivor triage and gate-design
   decision; deliberately left open by the mutation-gate-health closeout.
3. **#269 / #270** — small process-hardening follow-ups from the latest retro.
4. Other open: #259, #258, #252, #243, #241, #237, #236, #185, #184.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- This session hit the #258 echo-flood trap again (batched tool calls under
  delayed output → cascade cancels). Prefer serial tool calls when output
  latency is unstable.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [#264](https://github.com/corca-ai/charness/issues/264) (follow-up scope + allowlist)
- [mutation-gate-health goal](../charness-artifacts/goals/2026-05-31-mutation-gate-health.md)

# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- Current public release after this pickup is expected to be `v0.5.30` on `origin/main`, containing the #170 and #174 repairs. Verify with `gh release view v0.5.30 --repo corca-ai/charness`.
- [#170](https://github.com/corca-ai/charness/issues/170) is fixed by making
  Slack URL task text surface `gather-slack` through `find-skills` support
  recommendations, adding [advise_slack_path.py](../skills/public/gather/scripts/advise_slack_path.py),
  and teaching `gather` to use that helper before browser/private-source fallbacks.
  It preserves `host-mediated` / `none` adapter boundaries and points
  `direct-cli` at [export-thread.sh](../skills/support/gather-slack/scripts/export-thread.sh).
- [#174](https://github.com/corca-ai/charness/issues/174) is fixed by making `debug` sibling search classify every surfaced sibling and record proof level separately; `issue` causal review and bug close comments preserve those decisions.
- Live open GitHub issues after this pickup should be only
  [#171](https://github.com/corca-ai/charness/issues/171) and
  [#172](https://github.com/corca-ai/charness/issues/172), which appear to be
  duplicate c-families habit/context exploration issues needing product
  discussion rather than an obvious autonomous bug fix.
- [scripts/run-quality.sh](../scripts/run-quality.sh) passed on 2026-05-17 with 60 passed / 0 failed in 110.7s; `run_slice_closeout.py --ack-cautilus-skill-review` also passed. Cautilus planner returned `next_action: none`.
- `setup` normalization is green; [AGENTS.md](../AGENTS.md) has the compact Skill Routing block and `CLAUDE.md` remains a symlink to `AGENTS.md`. See [charness-artifacts/setup/latest.md](../charness-artifacts/setup/latest.md).
- `defuddle` is now a repo-local npm dev dependency (`defuddle@0.18.1`) and the public gather/web-fetch reader fallback has live proof in [charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md](../charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md). `gws-cli` is still missing on this machine.

## Next Session

1. Discuss #171/#172 together: decide whether to close one as duplicate and
   whether the surviving c-families issue is product framing, skill behavior,
   or a lightweight docs exploration.
2. Optional gather follow-up: decide whether raw acquired-content persistence
   belongs in a separate gather slice now that trace/proof correctness, Slack
   support routing, and live `defuddle` reader proof all exist.
3. Maintained Cautilus scenario registry mutation remains ask-before-mutate.
   The current #170/#174 repairs are covered by deterministic tests and
   dogfood contract updates, not a scenario-registry edit.
4. Mutation-testing #167, older Cautilus rename details, and long historical
   issue batches are not active handoff work. Reload them from owning artifacts
   or GitHub only if a fresh live signal references them.

## Discuss

- First decision: #171/#172 consolidation. Tradeoff: closing one duplicate
  keeps the queue honest and lets the surviving issue carry a clean product
  question; keeping both open preserves parallel framings if they intentionally
  differ, but today their titles and timing make that difference unclear.
- Whether raw acquired-content persistence belongs in a future gather slice,
  now that trace/proof correctness is locally implemented.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/setup/latest.md](../charness-artifacts/setup/latest.md)
- [charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md](../charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md)

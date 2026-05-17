# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- The gather/#169 work has landed on `origin/main`; the live refresh before this handoff update found no unpublished gather/#169 implementation commits, and [#169](https://github.com/corca-ai/charness/issues/169) is closed as of 2026-05-16T03:53:43Z.
- The gather repair implementation rejects non-HTTP(S), treats invalid regex as invalid proof even when direct transport fails, records every planned route/fallback stage as executed or explicitly skipped/not-implemented/terminal, keeps browser network reconnaissance diagnostic-only, derives final status from `selected_attempt`, removes unimplemented selector-proof wording, and adds `gather_public_url.py` so public `gather` can preserve `web-fetch` trace in a durable asset. The public helper writes durable records only for successful acquisitions; `error`, `blocked`, and `degraded` acquisitions return non-zero JSON without refreshing `latest.md`, and generated slugs include URL path/hash to avoid same-host collisions.
- Live open GitHub issues at the last refresh were [#170](https://github.com/corca-ai/charness/issues/170),
  [#171](https://github.com/corca-ai/charness/issues/171), [#172](https://github.com/corca-ai/charness/issues/172),
  and [#173](https://github.com/corca-ai/charness/issues/173); #168 is no longer blocked on
  Cautilus #44 after the robustness contract landed in Cautilus v0.16.0.
- #168 follow-up is implemented locally: `quality` now has
  `recommend_behavior_test.py`, which emits a recommend-only finding using the
  Cautilus robustness request/plan/report packet vocabulary without adding a
  Charness-owned runner. The source contract is gathered in
  [charness-artifacts/gather/2026-05-17-raw-githubusercontent-com-corca-ai-cautilus-v0-16-0-docs-contracts-robustness-evaluation-md-45a51934.md](../charness-artifacts/gather/2026-05-17-raw-githubusercontent-com-corca-ai-cautilus-v0-16-0-docs-contracts-robustness-evaluation-md-45a51934.md).
- #173 follow-up is implemented locally: release-linked issue resolution can pass
  `--close-issue <number>` to the release helper, which puts close keywords in
  the direct release commit body, verifies GitHub issue state after push/release,
  and performs a manual close fallback only when auto-close did not take effect.
- [scripts/run-quality.sh](../scripts/run-quality.sh) passed on 2026-05-16 with 60 passed / 0 failed in 80.8s; the proof and remaining weaknesses live in [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md).
- `setup` normalization is green; [AGENTS.md](../AGENTS.md) has the compact Skill Routing block and `CLAUDE.md` remains a symlink to `AGENTS.md`. See [charness-artifacts/setup/latest.md](../charness-artifacts/setup/latest.md).
- `defuddle` is now a repo-local npm dev dependency (`defuddle@0.18.1`) and the public gather/web-fetch reader fallback has live proof in [charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md](../charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md). `gws-cli` is still missing on this machine.

## Next Session

1. Optional gather follow-up: decide whether raw acquired-content persistence belongs in a separate gather slice now that trace/proof correctness and live `defuddle` reader proof both exist.
2. Gather/web-fetch acquisition invariants now live in [skills/support/web-fetch/references/runtime-contract.md](../skills/support/web-fetch/references/runtime-contract.md) and [skills/public/gather/references/capability-contract.md](../skills/public/gather/references/capability-contract.md); reload those owner contracts before touching that seam.
3. Mutation-testing #167, older Cautilus rename details, and long historical issue batches are not active handoff work. Reload them from owning artifacts or GitHub only if a fresh live signal references them.

## Discuss

- Whether raw acquired-content persistence belongs in a future gather slice, now that trace/proof correctness is locally implemented.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/setup/latest.md](../charness-artifacts/setup/latest.md)
- [charness-artifacts/spec/gather-acquisition-repair-contract.md](../charness-artifacts/spec/gather-acquisition-repair-contract.md)
- [charness-artifacts/spec/quality-cautilus-behavior-testing-contract.md](../charness-artifacts/spec/quality-cautilus-behavior-testing-contract.md)
- [charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md](../charness-artifacts/gather/2026-05-16-rfc-editor-org-rfc-rfc9110-html-b1b13a12.md)
- [charness-artifacts/critique/2026-05-16-gather-acquisition-repair-plan-critique.md](../charness-artifacts/critique/2026-05-16-gather-acquisition-repair-plan-critique.md)
- [charness-artifacts/critique/2026-05-16-gather-public-url-blocker-fix-critique.md](../charness-artifacts/critique/2026-05-16-gather-public-url-blocker-fix-critique.md)
- [charness-artifacts/critique/2026-05-16-gather-public-url-push-critique.md](../charness-artifacts/critique/2026-05-16-gather-public-url-push-critique.md)
- [charness-artifacts/critique/2026-05-16-handoff-live-state-refresh-critique.md](../charness-artifacts/critique/2026-05-16-handoff-live-state-refresh-critique.md)

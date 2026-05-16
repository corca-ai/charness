# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- The current gather/#169 work has been prepared for direct push to `main`; refresh `git status --short --branch` before assuming whether the push has already landed.
- The gather repair implementation now rejects non-HTTP(S), treats invalid regex as invalid proof even when direct transport fails, records every planned route/fallback stage as executed or explicitly skipped/not-implemented/terminal, keeps browser network reconnaissance diagnostic-only, derives final status from `selected_attempt`, removes unimplemented selector-proof wording, and adds `gather_public_url.py` so public `gather` can preserve `web-fetch` trace in a durable asset. The public helper writes durable records only for successful acquisitions; `error`, `blocked`, and `degraded` acquisitions return non-zero JSON without refreshing `latest.md`, and generated slugs include URL path/hash to avoid same-host collisions.
- Live open GitHub issues:
  - [#169](https://github.com/corca-ai/charness/issues/169) `Review latest insane-search ideas for charness gather fallbacks`: local work exists; do not claim remote closure until the unpublished commits are pushed/PR'd and accepted.
  - [#168](https://github.com/corca-ai/charness/issues/168) `Discuss user behavior robustness testing for Charness`: discussion starter, not an implementation spec.
- [scripts/run-quality.sh](../scripts/run-quality.sh) passed on 2026-05-16 with 60 passed / 0 failed in 80.8s; the proof and remaining weaknesses live in [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md).
- `setup` normalization is green; [AGENTS.md](../AGENTS.md) has the compact Skill Routing block and `CLAUDE.md` remains a symlink to `AGENTS.md`. See [charness-artifacts/setup/latest.md](../charness-artifacts/setup/latest.md).
- `defuddle` and `gws-cli` are missing on this machine. Current gather/web-fetch proof is deterministic command-shape and fallback behavior, not live reader-runtime proof.

## Next Session

1. After the direct push is confirmed on `origin/main`, decide whether [#169](https://github.com/corca-ai/charness/issues/169) should be closed immediately with commit references or left open for maintainer/runtime acceptance.
2. For gather/web-fetch, preserve the intended direction: support skills should acquire as much as safely possible, use reader fallbacks such as `defuddle` when installed, and record truthful attempts, selected proof, blockers, and skipped routes when acquisition is degraded.
3. Optional local proof upgrade: install or expose `defuddle`, then run a real public article URL through `gather_public_url.py` to prove reader extraction beyond deterministic command-shape tests.
4. Keep #168 in `Discuss` until the user chooses a first experiment and assertion model for user-behavior robustness testing.
5. Mutation-testing #167, older Cautilus rename details, and long historical issue batches are not active handoff work. Reload them from owning artifacts or GitHub only if a fresh live signal references them.

## Discuss

- Publish path for the unpublished local commits: direct push vs PR vs keep local until another slice lands.
- #168 product direction: whether Charness should expose user-action fuzzing / behavior mutation testing, and what the smallest useful experiment should assert.
- Whether to install or expose `defuddle` locally now so gather dogfood can prove real reader fallback behavior instead of only deterministic command shape.
- Whether raw acquired-content persistence belongs in a future gather slice, now that trace/proof correctness is locally implemented.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/setup/latest.md](../charness-artifacts/setup/latest.md)
- [charness-artifacts/spec/gather-acquisition-repair-contract.md](../charness-artifacts/spec/gather-acquisition-repair-contract.md)
- [charness-artifacts/critique/2026-05-16-gather-acquisition-repair-plan-critique.md](../charness-artifacts/critique/2026-05-16-gather-acquisition-repair-plan-critique.md)
- [charness-artifacts/critique/2026-05-16-gather-acquisition-subagent-critique.md](../charness-artifacts/critique/2026-05-16-gather-acquisition-subagent-critique.md)
- [charness-artifacts/critique/2026-05-16-gather-public-url-blocker-fix-critique.md](../charness-artifacts/critique/2026-05-16-gather-public-url-blocker-fix-critique.md)
- [charness-artifacts/critique/2026-05-16-gather-public-url-push-critique.md](../charness-artifacts/critique/2026-05-16-gather-public-url-push-critique.md)
- [charness-artifacts/critique/2026-05-16-gather-repair-impl-critique.md](../charness-artifacts/critique/2026-05-16-gather-repair-impl-critique.md)
- [charness-artifacts/critique/2026-05-16-setup-quality-posture-critique.md](../charness-artifacts/critique/2026-05-16-setup-quality-posture-critique.md)
- [charness-artifacts/critique/2026-05-16-critique-packet-provenance-critique.md](../charness-artifacts/critique/2026-05-16-critique-packet-provenance-critique.md)
- [charness-artifacts/critique/2026-05-16-handoff-stale-refresh-critique.md](../charness-artifacts/critique/2026-05-16-handoff-stale-refresh-critique.md)

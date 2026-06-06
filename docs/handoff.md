# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.25.0 shipped** (tag `v0.25.0`, GitHub release verified). The changed-line
  mutation-coverage **pre-push gate is now ACTIVE end-to-end**: slice 1 consumer
  (`run-quality.sh`) + slice 2 producer landed. Tree clean, `origin/main` even.
- **Producer = lever A+B** (drop `dynamic_context`, keep subprocess capture;
  piggyback the closeout broad pytest, one instrumented run). Run it with
  `run_slice_closeout.py --produce-mutation-coverage` (requires
  `--verification-lock`) — emits `reports/mutation/test-coverage.json` + a
  **content-fingerprint** `.fingerprint` marker (supersedes slice-1's SHA `.head`;
  closeout runs pre-commit, so SHA would silently skip — see spec "Freshness
  identity changed"). The gate proved itself on the release push (caught a real
  uncovered `__main__` dispatch + two of its own edge branches; all covered).
- Open issues: **#322, #184**. #320/#321 stay closed.

## Next Session

1. **Human real-host smoke for v0.25.0 (release left it open).** `charness update`
   on a clean temp-home + the nose tool-doctor/install/sync checklist in
   [release latest](../charness-artifacts/release/latest.md). Cannot be done by
   the agent; confirm before treating the operator surface as proven.
2. **#322 (scope C, spec-first).** 4-field self-declaration rollout to ~6
   inference surfaces **plus** the nose family classifier (Q1). `spec`-first per
   the #322 body. Saved analysis:
   [nose-clone interpretation](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md).
3. **Skill portability of the gate's lessons.** Promote the pattern +
   freshness-guard + producer-cost lesson to
   [mutation-testing.md](../skills/public/quality/references/mutation-testing.md);
   optionally offer the gate as a `quality` capability + adapter contract
   (libs-packaging decision). Route via `create-skill`/`quality`; see spec
   "Skill portability".
4. Backlog: **#184** — 제품 성공 기준과 핵심 메트릭 정의.

## Discuss

- **No push/tag CI.** The local `--release` gate is the bundle proof (just
  exercised for v0.25.0). Worth deciding whether to add light push/tag CI, and
  whether to mirror the changed-line gate into a CI-PR check (spec
  "Deferred Decisions").

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; Slice 2 delivered, freshness identity, portability follow-up),
  [release v0.25.0 critique](../charness-artifacts/critique/2026-06-07-release-v0-25-0.md)
- [nose-clone interpretation (#322)](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)

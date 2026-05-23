# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and recent-lessons.md.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs through `gather`.

## Current State

- `main` ahead of `origin/main` (unpushed). Closes on push: **#198**
  (eval_registry coverage-attribution fix — immutability test loads a fresh
  module copy so the frozen-dataclass line re-executes under the test context),
  **#202** (issue existing-only label/milestone + `resolve-milestone` guard),
  **#203** (retro opt-in `## Sibling Search`), **#204** (create-cli `Lint Gate`
  closeout), **#205** (ideation opt-in `## Structured Questions`), **#206**
  (create-skill "Closeout Schema Rule" + advisory survey).
- Sibling follow-up grammar now shared from `artifact_validator`
  (`validate_sibling_followups`) across `debug`, `retro`, and `critique`.
- **#207** RCA done — working-as-designed fail-closed; needs RCA comment +
  by-design close (external, not yet done). **#184/#185** still deferred.

## Next Session

1. **#207 close**: post the RCA (it is the fail-closed scope-gap signal at
   `check_mutation_score.py:200-207`, not a defect) and close by-design. Open
   question: a no-mutable-line changed-file allowlist would reduce false
   failures on string/generated-only commits but weakens the guarantee —
   decide deliberately, do not auto-add.
2. **Ideation for #185 + #184**: spawn `charness:ideation` against the 1차
   메모 (symptom→root-cause counter; LLM-as-judge via Cautilus
   `skill-experiment`; usage-episodes adapter activation).
3. **Optional**: 14 pre-existing "used to resolve the X adapter" strings in
   `release/` + `issue_tool.py` understate their roles; only worth a sweep if
   budget allows.

## Discuss

- New opt-in artifact validators (`validate_ideation_artifact.py`,
  `validate_retro_artifact.py`) are section-gated + changed-paths-default, so
  the 70 historical retro artifacts and prose-only output stay valid.
- `validate_skill_output_schemas.py` is intentionally advisory (report, exit 0,
  un-wired) — a hard gate over freeform Output Shape prose would false-fire.
- `resolve-milestone` strips the requested title but not existing titles
  (backend titles are authoritative); exact case-sensitive match is correct
  for GitHub.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock` +
  `pytest-xdist`; seed-cache LRU eviction; release proof suppression;
  D21–D26 reopen-trigger watchlist; 2 pre-existing ruff errors in the vendored
  notion-to-md converter (out of scope).

## References

- [open-issue sweep closeout](../charness-artifacts/critique/2026-05-23-handoff-open-issues-closeout.md)
- [quality posture](../charness-artifacts/quality/latest.md),
  [release surface](../charness-artifacts/release/latest.md)
- [usage-episodes spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md),
  [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md)
- Closes on push: [#198](https://github.com/corca-ai/charness/issues/198),
  [#202](https://github.com/corca-ai/charness/issues/202),
  [#203](https://github.com/corca-ai/charness/issues/203),
  [#204](https://github.com/corca-ai/charness/issues/204),
  [#205](https://github.com/corca-ai/charness/issues/205),
  [#206](https://github.com/corca-ai/charness/issues/206). By-design (RCA, no
  fix): [#207](https://github.com/corca-ai/charness/issues/207).

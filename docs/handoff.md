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

- Latest local commit `4e69881` (**1 ahead of `origin/main`, not yet pushed** —
  push is the maintainer's call): a latent-bug sweep (no open GitHub bug — the
  issue queue held only deferred ideation). Four self-found defects fixed with
  regression tests through the design→impl→pattern-scan→RCA→final-critique loop
  and bounded fresh-eye subagents: `parse_selector` now rejects issue#<1 (was
  returning `[0]`); `is_valid_followup_tail` strips trailing punctuation so
  `deferred.` is caught (shared by debug/retro/critique);
  `bump_version --set-version` validates format before mutating the manifest;
  `issue brief-path` emits structured `{"ok": false}` on a non-positive
  `--number` instead of a raw traceback. A final independent fresh-eye subagent re-derived
  all four fixes, proved each regression test non-vacuous (revert→fail,
  restore→pass), and cleared the commit SAFE-TO-PUSH; 114 affected tests + full
  read-only quality gate (67 passed) green; exports synced byte-identical.
  Closeout: [bug-sweep critique](../charness-artifacts/critique/2026-05-23-handoff-bug-sweep-closeout.md).
- `main` previously in sync with `origin/main` (pushed `858da76` + retro `89f6a0b`).
  Closed earlier: **#198** (eval_registry coverage-attribution fix —
  immutability test loads a fresh module copy so the frozen-dataclass line
  re-executes under the test context), **#200/#201** (prior-session fixes that
  had silently stayed OPEN), **#202** (issue existing-only label/milestone +
  `resolve-milestone` guard), **#203** (retro opt-in `## Sibling Search`),
  **#204** (create-cli `Lint Gate` closeout), **#205** (ideation opt-in
  `## Structured Questions`), **#206** (create-skill "Closeout Schema Rule" +
  advisory survey). **#207** closed by-design (RCA: fail-closed scope-gap
  signal, not a defect).
- Sibling follow-up grammar now shared from `artifact_validator`
  (`validate_sibling_followups`) across `debug`, `retro`, and `critique`.
- Only **#184/#185** remain open (deferred ideation).

## Next Session

1. **Ideation for #185 + #184**: spawn `charness:ideation` against the 1차
   메모 (symptom→root-cause counter; LLM-as-judge via Cautilus
   `skill-experiment`; usage-episodes adapter activation).
2. **Deferred design**: a no-mutable-line changed-file allowlist for the
   mutation scope-gap signal would cut false failures on string/generated-only
   commits but weakens the just-hardened guarantee — needs spec + critique, do
   not auto-add. Reopen #207 only with a recurring false-positive pattern.
3. **Optional**: 14 pre-existing "used to resolve the X adapter" strings in
   `release/` + `issue_tool.py` understate their roles; sweep only if budget.

## Discuss

- New opt-in artifact validators (`validate_ideation_artifact.py`,
  `validate_retro_artifact.py`) are section-gated + changed-paths-default, so
  historical retro artifacts and prose-only output stay valid.
- `validate_skill_output_schemas.py` is intentionally advisory (report, exit 0,
  un-wired) — a hard gate over freeform Output Shape prose would false-fire.
- New repeat-trap (retro `89f6a0b`): a single `Fixes #a #b` closes only the
  first issue; repeat the keyword per number, then verify each issue state
  after push.
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
- Closed: [#198](https://github.com/corca-ai/charness/issues/198),
  [#202](https://github.com/corca-ai/charness/issues/202),
  [#203](https://github.com/corca-ai/charness/issues/203),
  [#204](https://github.com/corca-ai/charness/issues/204),
  [#205](https://github.com/corca-ai/charness/issues/205),
  [#206](https://github.com/corca-ai/charness/issues/206); by-design
  [#207](https://github.com/corca-ai/charness/issues/207).

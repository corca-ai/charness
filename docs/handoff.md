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

- Fixed **#208** (scheduled Mutation Tests red ~2 days): the changed-file
  scope-gap BLOCKER reused whole-file selection predicates, so a well-tested
  change to a partially-covered CLI/validator was failed by unrelated untested
  plumbing. Rescoped the blocker to *changed lines*
  ([mutation_changed_files_lib.py](../scripts/mutation_changed_files_lib.py));
  whole-file coverage exclusions are now advisory, budget exclusions still
  block. Added the two genuinely-uncovered changed-line tests (brief-path
  success, valid set-version); next-run window reports
  `changed_line_uncovered=[]`. RCA:
  [debug](../charness-artifacts/debug/2026-05-24-mutation-changed-scope-gap-whole-file.md).
- #207 was the prior by-design close of this same auto-filed regression; #208 is
  the recurrence it anticipated, now fixed. Known limitation: changed-line
  *statement* coverage is weaker than mutation-line (executed ≠ asserted),
  sampled files keep full rigor.
- Prior: bug-sweep `4e69881` (v0.7.11); closed #198, #202–#206.
- Open: **#184/#185** (deferred ideation).

## Next Session

1. **Ideation for #185 + #184**: spawn `charness:ideation` against the 1차
   메모 (symptom→root-cause counter; LLM-as-judge via Cautilus
   `skill-experiment`; usage-episodes adapter activation).
2. **Mutation blocker follow-up** (see #208/#207 thread): if the changed-line
   statement-coverage blocker proves too weak, consider mutation-line coverage
   of changed lines (needs Cosmic Ray init on all changed files) — spec +
   critique first.

## Discuss

- New opt-in artifact validators (`validate_ideation_artifact.py`,
  `validate_retro_artifact.py`) are section-gated + changed-paths-default, so
  historical retro artifacts and prose-only output stay valid.
- `validate_skill_output_schemas.py` is intentionally advisory (report, exit 0,
  un-wired) — a hard gate over freeform Output Shape prose would false-fire.
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

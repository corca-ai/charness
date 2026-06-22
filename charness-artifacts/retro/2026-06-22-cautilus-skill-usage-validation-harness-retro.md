# Retro — cautilus skill-usage-validation-harness goal (session)

Mode: session

## Context

One activated `achieve` goal, 8 slices: a real headless-run usage-validation
harness so a charness skill change can be proven by a real `claude -p` run scored
by cautilus `evaluate skill-experiment`. Built the stream-json transcript capture
(runner flip), the keystone transcript→`skill_clone_experiment_input.v1`
extractor, the wrapper wiring, the obligations spec, and ran one real
baseline-vs-variant scorer pass. Verdict: `discard` (honest zero source-coverage
delta). Chain proven end-to-end; the verdict is the chain working, not a
promotion claim.

## Evidence Summary

Changed files + commits (fb3660a0 → cfca493c, 7 commits); cautilus Go source at
`/home/hwidong/codes/cautilus` 181ebef7 (the S1 de-risk authority); the
slice-closeout runs; the captured transcripts + `report.json`; host-log probe
(codex sqlite logs only — this claude session's turn/token timing is not exposed
to the probe).

## Waste

- **API 529 overload thrash (S6).** Three sonnet capture attempts failed or
  partially failed on `529 Overloaded` (one read 6/7 refs but the closing turn
  errored) before switching to haiku, which captured cleanly first try. ~15 min +
  tokens lost retrying the same overloaded tier.
- **Capture-design iteration (S6/S7).** The first capture prompt NAMED the concept
  refs, so a capable agent reached them by filename in BOTH arms (zero delta). The
  v2 "follow pointers only" prompt over-corrected into runaway broad exploration
  (16 refs, no clean result). Two wasted capture passes before settling on the
  honest v1 result.
- **Surface-manifest blind spot (S5, S7 — recurred).** The slice closeout blocked
  twice on new files (`evals/cautilus/skill-experiment/`, then
  `charness-artifacts/cautilus/skill-experiment-2026-06-22/`) not being in
  `.agents/surfaces.json`. Pre-commit does NOT catch this; only the closeout does.
- **Markdown lint timing (S4 — minor).** `check-markdown.sh` only lints tracked
  files, so my pre-`git add` check missed 3 MD errors in the new untracked docs;
  pre-commit then blocked the commit.

## Critical Decisions

- **Read the cautilus Go source directly (S1)** instead of trusting the proposal
  prose — confirmed BLOCKER-1 (cautilus is a deterministic scorer over
  host-captured `output.sourceRefs`, not a transcript analyzer) and gave the exact
  required-field + `isolationSafe` + status-enum contract the extractor was built
  against. The single highest-leverage move; without it the extractor ships wrong.
- **Honest `discard` over a gamed `promote`.** When both arms read the same refs, I
  reported the zero-delta `discard` and explained why (source-coverage measures
  file-set, not pointer-directness) rather than re-tuning obligations to force a
  promotion. North-star aligned.
- **Isolated read-only worktrees, never the shared install clone** (BLOCKER-2) —
  install clone untouched at `d2cf1b75`; no #258-class corruption risk.
- **Fold the fresh-eye CONCERN before locking S3** — preferring the transcript's
  own init `cwd` as the relativization root closed a silent worktree-symlink
  coverage-zeroing hazard before the real captures depended on it.

## Expert Counterfactuals

- **Measurement-design lens (Cem Kaner / metrology).** Would have asked, BEFORE
  capturing, "is the measured signal causally downstream of the intervention?" —
  immediately surfacing that source-coverage (which files) is orthogonal to this
  disposition's pointer-directness, and that a name-hinted task lets the agent
  bypass pointers. That single check would have saved both wasted capture passes
  and is the most transferable lesson here.
- **Reliability-engineering lens.** Would have set a model fallback ladder
  (sonnet→haiku) for the captures up front given known 529 volatility, instead of
  retrying the overloaded tier three times.

## Next Improvements

- **memory:** eval-design rule — for a skill-experiment, the capture TASK must make
  the measured signal (source-coverage) causally require the intervention; a
  name-hinted task defeats a pointer-directness disposition. Recorded in
  `charness-artifacts/cautilus/latest.md` Follow-ups + this retro.
- **workflow:** under repeated `529 Overloaded`, switch model tier early (haiku for
  bounded file-reading captures) rather than retrying the same tier.
- **capability/workflow:** new files under a surfaces-managed dir need a
  `.agents/surfaces.json` entry; the gap is that pre-commit doesn't check surface
  coverage, only the slice closeout does — a candidate pre-commit guard.
- **code (carried S3 nit):** `findResultEvent` (extractor) and
  `findClaudeResultEvent` (runner) are duplicated ~10-line scanners; consolidate
  into a shared `stream-json` helper in a later slice.

## Sibling Search

Transferable waste named: the **pre-commit-vs-closeout coverage gap** (a managed
manifest enforced only at closeout, not pre-commit). Four-axis scan:
- other-skill: n/a (repo-local tooling).
- other-script: the same `.agents/surfaces.json` coverage is enforced by
  `run_slice_closeout.py` but NOT by any pre-commit hook — that is the one real
  sibling surface, already the subject of the capability improvement above.
- other-doc / other-workflow: no additional siblings — the markdown-lint timing
  miss is narrowly local (stage-then-check), `n/a — trivial`.
Decision: tracked as a `capability` next-improvement (pre-commit surface-coverage
guard candidate), not opened as an issue this session (low friction, single
recurrence pair S5/S7).

## Persisted

(filled by persist helper)

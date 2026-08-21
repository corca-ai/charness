# Reviewer Boundary Runtime Output Debug Review
Date: 2026-08-21

## Problem

The round-2 fresh-eye workers returned typed reports, but the parent boundary
fingerprint reported `boundary-drift` for every worker because their expected
file-backed result, receipt, ledger, prompt, and log files appeared as
`untracked-added` paths. This quarantines the boundary proof even though the
workers were read-only with respect to source and index.

## Correct Behavior

Given a review window and a canonical file-backed worker output directory, the
boundary verifier must ignore only declared ephemeral runtime state while
continuing to report source, index, and non-runtime untracked drift. The final
consumer must keep delivery proof separate from this tree-integrity rail. This
restores the parent's ability to distinguish an allowed evidence carrier from
an unauthorized reviewer worktree mutation without weakening `critique`/`prove`.

## Observed Facts

- All three round-2 workers completed through the canonical runner with typed
  receipts, matching output hashes, `findings-received`, and combined reports.
- All three semantic verdicts were `block`; no approval was claimed.
- The verifier command returned `ok: false`, `verdict: boundary-drift`, with
  each `.charness/reviewer-round-2/r2b-*` output as `untracked-added`.
- The verifier's documented scope intentionally excludes gitignored runtime
  files, and `.charness/reviewer-boundary/` is already ignored; the worker
  output directory was not.

## Reproduction

Run the round-2 verifier against
`.charness/reviewer-boundary/2026-08-21-r2-semantic-candidate-provider-schema-round-2b.json` <!-- reproduction-source -->
with window id `r2-semantic-candidate-provider-schema-round-2b`. It returns
`boundary-drift` and lists the worker runtime files as untracked additions.

## Candidate Causes

- The worker launcher allowed a caller-selected in-repo runtime directory
  without requiring it to be ignored.
- The repository ignore contract covered the snapshot directory but not the
  file-backed round directory.
- The verifier was incorrectly treating all untracked files as source drift.

## Hypothesis

The primary cause is an incomplete runtime-state ownership contract: the
canonical file-backed output location was not in the repository's ignored
runtime surface. If the directory is ignored and a regression assertion checks
that fact, a clean review window should stop reporting those evidence files
while a source-like untracked file must still drift. The cheapest disconfirmer
is: disconfirmer: run `git check-ignore` for the canonical output path, then
run the focused boundary suite and create a source-like untracked file; if the
runtime files still drift or the source-like file is hidden, this hypothesis is
false.

## Verification

Confirmed the hypothesis at the boundary: `.charness/reviewer-round-2/...` <!-- reproduction-source -->
was absent from `git status --ignored`, while the verifier explicitly emitted
`untracked-added` for it. The repair adds the directory to `.gitignore` and a
quality test checks the exact rule. The full round must be re-snapshotted before
any future fresh-eye window; this existing window remains quarantined.

## Root Cause

The file-backed worker contract defined typed output and delivery state but did
not define ownership of the output directory at the Git boundary. The parent
therefore created legitimate runtime evidence in a path the boundary rail
classified as a user-visible worktree mutation.

## Invariant Proof

- Invariant: when a file-backed worker emits runtime evidence, the boundary
  rail ignores that evidence directory while the final closeout still requires
  typed receipt, matching ledger, combined report, and reviewer verdict.
- Producer Proof: the worker runner writes result/receipt/ledger/report files
  in the round directory and the verifier observed those exact paths.
- Final-Consumer Proof: the boundary verifier is the consumer of tree drift;
  the critique consumer separately refused to treat the three `block` verdicts
  as approval.
- Interface-Shape Sibling Scan: `.charness/reviewer-boundary/` and other
  `.charness/*` runtime directories use the same ignore ownership pattern.
- Non-Claims: this does not prove provider-host behavior, typed-subagent host
  application, Windows cleanup, release publication, or approval.

## Detection Gap

- Boundary suite: it tested generic untracked reviewer files but not the repo's
  canonical file-backed output directory. Add the root ignore regression test.
- Runner contract: it accepted arbitrary output paths without surfacing their
  worktree ownership. The next semantic slice must add path/collision and
  runtime-location checks; this ignore repair alone is not full portability.
- Manual review: the round was the first direct detector; its result is
  quarantined rather than silently reclassified.

## Sibling Search

- Mental model: runtime evidence is mistaken for source mutation when ownership
  is implicit.
- same layer: `.charness/reviewer-boundary/` | decision: same class, fix now |
  proof: existing verifier self-drop and ignore rule.
- abstraction up: `.charness/quality-failure-logs/` and
  `.charness/standing-pytest/` | decision: same class, diagnostic-only for this
  slice | proof: static `.gitignore` scan; their lifecycle is not changed here.
- specialization down: worker result/receipt/log paths | decision: same bug,
  fix now | proof: round-2 drift payload.
- cross-file: `skills/shared/scripts/run_reviewer_worker.py` | decision: valid
  follow-up outside the slice | proof: static read shows caller-controlled
  paths; follow-up: deferred `docs/handoff.md` Current State.

## Seam Risk

- Interrupt ID: reviewer-boundary-runtime-output-unignored-2026-08-21
- Risk Class: none
- Seam: worker output path -> git status -> boundary verifier -> critique closeout
- Disproving Observation: a fresh window with ignored runtime output and a
  source-like untracked file yields only the latter as drift.
- What Local Reasoning Cannot Prove: provider/host behavior or other checkout
  layouts.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md

## Prevention

Keep file-backed worker runtime evidence under an explicitly ignored repository
surface (or outside the checkout), test that ownership at the root contract,
and take a new boundary snapshot after every parent commit. Never convert a
boundary-drift result into clean by hand; repair the ownership rule, then rerun
the verifier. The remaining mode, identity, stale-output, collision, timeout,
and ledger-race findings stay open for the next semantic repair slice.

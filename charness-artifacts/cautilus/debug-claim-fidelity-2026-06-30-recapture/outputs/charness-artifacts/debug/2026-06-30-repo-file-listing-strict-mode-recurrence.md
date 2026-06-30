# Repo File Listing Strict-Mode Recurrence Debug
Date: 2026-06-30

## Problem

A standing repo file-scanner gate is reported to pass locally but fail only in
CI by silently including gitignored files: it walks the repo through the shared
listing helper without opting into strict git-aware mode, so on any invocation
where `git ls-files` does not succeed the scan degrades to a non-gitignore-aware
glob (CI is the plausible trigger; no live CI red was observed — see Non-Claims).

## Correct Behavior

Given a standing quality gate that scopes proof to repo-visible files, when
`git ls-files -z --cached --others --exclude-standard` does not succeed, the gate
must fail closed with command diagnostics rather than widen its scope to
gitignored files. Local and CI runs must scan the identical gitignore-filtered
set. Non-git fixtures and detection/one-shot helpers may keep the fallback.

## Observed Facts

- `scripts/repo_file_listing.py:46` returns `None` when `git ls-files` exits
  non-zero (default `require_git=False`); `iter_repo_files` then falls back to
  `repo_root.rglob("*")` (`:64-68`) and `iter_matching_repo_files` to bare
  `repo_root.glob(pattern)` with no git-visible `allowed` filter (`:115-121`).
  Gitignore filtering exists only on the git path (`:107-114`), so the fallback
  includes gitignored files by construction.
- The exact root cause was remediated on 2026-05-22
  (`2026-05-22-repo-file-listing-strict-mode.md`): a `require_git` strict mode
  plus `--require-git-file-listing` threaded through ~16 gates in
  `scripts/run-quality.sh`.
- That remediation is incomplete. `scripts/check_markdown_inline_code.py:79`
  calls `iter_matching_repo_files(repo_root, SCAN_GLOBS)` with no `require_git`
  and exposes no CLI flag, yet is a standing gate (run via
  `scripts/check-markdown.sh:63`) — structurally unable to fail closed.
- A second parallel helper, `skills/public/quality/scripts/git_inventory_lib.py:15`
  (`visible_repo_files`, `require_git=False`, `None` on failure), duplicates the leaky contract.

## Reproduction

`python3 scripts/check_markdown_inline_code.py --repo-root <non-git copy with
gitignored *.md>`: git path skipped, fallback glob runs, gitignored markdown
under `reports/`/`.artifacts/`/`mutants/`/`skills/support/generated/*`/`pytest-tmp/`
(all `.gitignore`d) is scanned. At a local git checkout they are excluded → passes.

## Candidate Causes

- The helper encodes discovery failure (`None`) identically to "fallback
  acceptable," so a consumer cannot distinguish git-unknown from git-empty.
- Strict mode is a per-call opt-in (`require_git=True`), easy to miss; new/missed
  gates default to the leaky fallback.
- CI runs gates against trees where `git ls-files` differs from local (copied
  fixtures, export trees, git-absent contexts) and materializes gitignored
  artifacts earlier — so the leak is CI-only.

## Hypothesis

A standing gate consuming the helper without `require_git=True` scans gitignored
files on any git-failing invocation while passing at a local git checkout. The
recurrence persists because strict mode is per-call with no meta-gate enforcing
it across all standing scanners.

## Verification

- `check_markdown_inline_code.py:79` passes no `require_git` and defines no
  `--require-git-file-listing` (read-confirmed); `check-markdown.sh:63` invokes
  it with no flag to pass.
- `inventory_gitignore_scan_hygiene.py` `DEFAULT_PATH_GLOBS` (`:27-33`) =
  `skills/public/quality/scripts/*.py`, `scripts/*inventory*.py`,
  `scripts/*quality*.py`, `scripts/*scan*.py` — `check_markdown_inline_code.py`
  matches none. Even in scope, `iter_matching_repo_files`/`iter_repo_files` are
  in `GIT_AWARE_MARKERS` (`:15-26`), so any call passes regardless of `require_git`.

## Root Cause

Git-awareness is conditional on a per-call strict opt-in, but the helper's
failure value (`None`) makes "git visibility unknown" indistinguishable from
"fallback acceptable." Standing gates that omit the opt-in silently substitute a
non-gitignore-aware walk for a gitignore-filtered proof scope. The 2026-05-22 fix
added the opt-in but left it per-call with no enforcement, so one missed gate
reintroduces the failure. Structural cause: a **missing invariant** — nothing
forces every standing repo-scanner to use strict git-visible listing.

## Invariant Proof

- Invariant: a standing gate's file scope is gitignore-filtered end-to-end; a
  `None`/failed listing from the producer must fail the gate, never widen the
  consumer's scan to gitignored files.
- Producer Proof: `repo_file_listing.git_list_repo_files` has strict mode and
  returns `None` on git failure (`:37-47`); gitignore filter is the `allowed`
  set on the git path only (`:107-114`).
- Final-Consumer Proof: `check_markdown_inline_code._candidate_files` (`:78-88`)
  consumes without `require_git`, so the `None` path scans the unfiltered glob.
  Producer-has-strict-mode is not end-to-end proof; the consumer never opts in.
- Interface-Shape Sibling Scan: `git_inventory_lib.visible_repo_files` (`:15`)
  has the same `set|None` shape and default; any consumer omitting
  `require_git=True` inherits the gap.
- Non-Claims: not verified that CI materializes gitignored `*.md` on a
  git-failing path for this gate today; proof is structural, not a live CI red.

## Detection Gap

- hygiene-gate scope | `inventory_gitignore_scan_hygiene.py` `DEFAULT_PATH_GLOBS`
  (`:27-33`) excludes `scripts/check_*.py` | broaden globs to all standing-gate
  scanners.
- hygiene-gate invariant | helper names in `GIT_AWARE_MARKERS` (`:15-26`) count
  as git-aware without `require_git=True` | flag helper calls omitting
  `require_git=True`; make strict opt-in the inspected invariant.
- run-quality wiring | `check-markdown.sh:63` runs the gate with no strict flag
  (none exists) | add `--require-git-file-listing` threaded to the helper.
- regression coverage | no fail-closed regression for this gate on a non-git
  tree (2026-05-22 siblings each got one) | add the same test.

## Sibling Search

- Mental model: "a broader filesystem scan is safe; using the shared helper is
  itself proof of gitignore-awareness" — both false (helper is git-aware only in
  strict mode; the fallback is unfiltered).
- same layer: `scripts/check_markdown_inline_code.py:79` — standing markdown gate,
  no `require_git`. | decision: valid follow-up outside the slice | proof: static
  scan only | follow-up: deferred docs/handoff.md#repo-file-listing-strict-mode-recurrence
- same layer (non-gate, advisory): `scripts/lint_ignore_inventory_lib.py:56`
  (consumer `inventory_lint_ignores.py` always returns 0, not in run-quality),
  `scripts/quality_bootstrap_detect.py:64` (preset detection), and
  `scripts/migrate_backtick_file_refs.py:58` (one-shot migration) — all consume
  the helper with no `require_git`. | decision: same class, diagnostic-only for
  this slice | proof: static scan only | no-action reason: none is a pass/fail
  standing gate; 2026-05-22 prevention allows fallback for non-gate-grade
  discovery (leaky scope only pollutes advisory review, never fails closed).
- abstraction up: the "`None`=git-unavailable=fallback-OK + default
  `require_git=False`" contract is duplicated in `scripts/repo_file_listing.py`
  and `skills/public/quality/scripts/git_inventory_lib.py:15` — general pattern
  "a failure value reused as a permissive default." | decision: valid follow-up
  outside the slice | proof: static scan only | follow-up: deferred
  docs/handoff.md#repo-file-listing-strict-mode-recurrence
- mental-model sibling: `inventory_gitignore_scan_hygiene.py` `GIT_AWARE_MARKERS`
  (`:15-26`) trusts a helper *name* as proof — a checker trusting an implicit
  authority over the strict-mode invariant. | decision: valid follow-up outside
  the slice | proof: static scan only | follow-up: deferred
  docs/handoff.md#repo-file-listing-strict-mode-recurrence
- cross-file: all siblings live outside subject file `scripts/repo_file_listing.py`.

## Seam Risk

- Interrupt ID: repo-file-listing-strict-mode-recurrence
- Risk Class: external-seam, host-disproves-local
- Seam: git file visibility -> standing gate proof scope
- Disproving Observation: gate passes at a local git checkout and only includes
  gitignored files where git listing fails — a CI/host difference local
  reasoning cannot reproduce.
- What Local Reasoning Cannot Prove: which CI step materializes gitignored files
  on a git-failing invocation.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/repo-file-listing-strict-mode-recurrence.md

## Prevention

Map prevention to the detection-gap outputs, not another per-call opt-in: (1)
broaden `inventory_gitignore_scan_hygiene.py` to all standing-gate scanners and
flag helper calls omitting `require_git=True`; (2) consolidate the two listing
helpers behind one strict contract; (3) give `check_markdown_inline_code.py` a
`--require-git-file-listing` path plus a fail-closed regression. Repeated symptom
on an external CI seam → route the fix through `spec` (handoff:
charness-artifacts/spec/repo-file-listing-strict-mode-recurrence.md), not `impl`.

## Related Prior Incidents

- `2026-05-22-repo-file-listing-strict-mode.md`: original diagnosis; added
  `require_git` strict mode and threaded `--require-git-file-listing`. This is
  its recurrence via a missed gate and a name-trusting meta-gate.

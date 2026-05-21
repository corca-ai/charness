# Repo File Listing Strict Mode Debug
Date: 2026-05-22

## Problem

`scripts/repo_file_listing.py` returned `None` when `git ls-files` failed, so
callers silently fell back to `glob` or `rglob` scanning. That fallback is useful
for non-git fixtures, but unsafe for standing quality gates that rely on
git-aware visibility and gitignore filtering.

## Correct Behavior

Given a standing Charness quality gate asks for repo-visible files, when
`git ls-files -z --cached --others --exclude-standard` fails, then the gate
must fail with command diagnostics. Direct helper consumers and non-git fixture
tests may still use the default fallback mode when they do not request strict
git listing.

## Observed Facts

- `git_list_repo_files()` returned `None` on any nonzero `git ls-files` result.
- `iter_repo_files()` then scanned every file under the root with `rglob("*")`.
- `iter_matching_repo_files()` similarly dropped to pattern-based globbing
  without gitignore filtering.
- Several standing gate scripts use the shared helper to define their proof
  scope, while many unit tests intentionally run those scripts against non-git
  temporary repos.

## Reproduction

Call `iter_matching_repo_files(<non-git-dir>, ("README.md",), require_git=True)`
or run `check_python_lengths.py --require-git-file-listing` against a non-git
directory. The strict path now exits with `repo file listing failed` and the
failed `git ls-files` command.

## Candidate Causes

- The helper had only one failure representation: `None`, meaning both "git is
  unavailable" and "fallback is acceptable."
- Standing gates and non-git fixtures shared the same default behavior.
- `run-quality` did not tell git-aware scanners that git listing was required
  for gate-grade proof.

## Hypothesis

If the shared helper exposes an explicit strict mode, and `run-quality` passes
that mode to gate scripts that use repo file listing for proof scope, then
standing gates fail closed while fixture/default helper behavior remains
compatible.

## Verification

- Focused helper and CLI tests passed for strict listing failure and default
  non-git fixture compatibility.
- `CHARNESS_QUALITY_LABELS=validate-profiles,validate-presets,validate-adapters,check-python-lengths,check-python-filenames,check-skill-bootstrap-vars,check-export-safe-imports,check-doc-links,check-spec-evidence-durability,check-references-link-inventory,check-test-production-ratio,check-duplicates ./scripts/run-quality.sh --read-only` passed.
- `ruff check` and `py_compile` passed for the changed helper and gate scripts.
- Fresh-eye review found `check-python-runtime-inheritance` and
  `inventory-gitignore-scan-hygiene` still used fallback listing in standing
  gates; both now have strict gate paths and focused fail-closed regressions.
- Final sibling scan found `inventory-ci-local-gate-parity` also had a
  workflow-listing fallback in a standing gate; it now requires strict git file
  listing from `run-quality` and has a focused regression.

## Root Cause

The repository file listing helper encoded discovery failure as an ordinary
fallback signal. That made unknown git visibility look like a valid non-git
scan to callers that needed git-aware proof.

## Detection Gap

- central repo listing helper | failed `git ls-files` fell back to repo-wide
  scan | add `require_git` mode and helper regression.
- standing gate scope | run-quality did not request strict listing | pass
  `--require-git-file-listing` to repo file-listing gates.
- inventory-specific listing | quality gitignore scan hygiene had its own
  `git ls-files` fallback | add a strict flag and run it from standing quality.
- workflow listing | CI/local gate parity had its own `git ls-files` fallback |
  add a strict flag and run it from standing quality.
- CLI diagnostics | strict failure could have produced a traceback | use a
  `SystemExit`-style exception carrying command diagnostics.

## Sibling Search

- Mental model: a broader filesystem scan is safer than an empty git-aware scan.
- fixed now: shell file listing, read-only quality changed paths, critique
  changed paths, mutation changed-file discovery, release proof discovery, and
  central repo file listing all have fail-closed paths for their gate-grade
  discovery surfaces.
- deferred: final sibling scan still needs to verify no obvious `check=False`
  discovery failures remain in standing release/quality paths.

## Seam Risk

- Interrupt ID: repo-file-listing-strict-mode
- Risk Class: none
- Seam: git file visibility -> standing gate proof scope
- Disproving Observation: selected run-quality repo-listing gates pass with
  strict git file listing enabled.
- What Local Reasoning Cannot Prove: none for the command-health boundary.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Keep fallback and strict discovery as separate contracts. Fixture-friendly
helpers may keep broad fallback defaults, but standing gates must opt into
strict discovery and carry command diagnostics when proof scope is unknown.

## Related Prior Incidents

- `2026-05-22-shell-file-listing-suppression.md`: shell gate file listing
  failure could hide behind fallback behavior.
- `2026-05-22-run-quality-changed-path-suppression.md`: changed-path discovery
  failure needed to widen or fail closed instead of reading as no changes.
- `2026-05-22-critique-changed-path-discovery-suppression.md`: changed-path
  discovery failure validated zero critique artifacts.

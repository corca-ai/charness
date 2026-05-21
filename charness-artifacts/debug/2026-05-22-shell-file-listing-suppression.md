# Shell File Listing Suppression Debug
Date: 2026-05-22

## Problem

Shell quality gates used required git file listing as proof input, but several
paths could treat a failed `git ls-files` command as an empty file set or hide
the collector failure behind fallback behavior.

## Correct Behavior

Given a quality gate is inside a git worktree and needs a tracked/unignored file
list, when `git ls-files` fails, then the gate should exit nonzero with the
command, exit code, stdout, and stderr. A successful listing that is genuinely
empty may still take the existing no-work success path.

## Observed Facts

- `scripts/check-markdown.sh` used `mapfile ... < <(git ls-files ...)`;
  Bash does not propagate the process substitution command's exit status to
  `mapfile`.
- `scripts/check-links-internal.sh` used the same process-substitution pattern
  before the "No markdown files to check." success path.
- `scripts/check-secrets.sh` used a process-substitution read loop on the
  secretlint path, so failed listing could produce "No tracked or unignored
  files to scan."
- The gitleaks path used a pipeline with `pipefail`, so it did not empty-pass,
  but it still hid git-listing or staging failures by falling through to a
  different scan mode.
- Fresh-eye reviewers independently confirmed the smallest safe repair is to
  materialize required git listings to temp files, check the producer exit
  status, and only then parse the list.

## Reproduction

Run each real script from a temp repo with a fake `git` first on `PATH`. Let
`git rev-parse --is-inside-work-tree` return true where needed, and make
`git ls-files` exit `42` with `forced git listing failure`. Before the fix, the
markdown/link/secretlint paths could reach their empty-list success messages, or
gitleaks could silently switch scan modes. After the fix, each script exits 1
with a `git file listing failed` diagnostic.

## Candidate Causes

- Process substitution made the file-list consumer's success hide the
  file-list producer's failure.
- The secrets gitleaks path treated "not in a worktree" and "worktree listing
  failed" as equivalent fallback cases.
- The gates optimized for no-work ergonomics before proving that no-work state
  came from successful discovery.

## Hypothesis

If every required `git ls-files` invocation writes stdout and stderr to a temp
file and the script checks the producer return code before reading the list,
then failed discovery will be distinct from successful empty discovery without
changing the existing empty-repo behavior.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_python_and_security_gates.py -k 'check_markdown or check_links_internal or check_secrets'` passed.
- `shellcheck scripts/check-markdown.sh scripts/check-links-internal.sh scripts/check-secrets.sh` passed.
- `ruff check tests/quality_gates/test_python_and_security_gates.py` passed.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` synced exported
  plugin copies.

## Root Cause

Required file discovery was represented as a file-list consumer operation
instead of a status-bearing producer operation. When the producer failed, the
consumer still succeeded with an empty array or the script switched to a
fallback scan mode, so unknown proof input was not distinguishable from an
empty proof result.

## Detection Gap

- markdown/link shell gates | no fake-git regression for `git ls-files`
  failure before empty-list success | add real-script tests that assert the
  file-listing diagnostic and absence of the no-work message.
- secrets shell gate | no fake-git regression for secretlint or gitleaks
  discovery failure | add real-script tests proving neither fallback invokes a
  scanner after failed worktree listing.
- shell gate review | process-substitution collectors were not treated as
  proof-input boundaries | scan `done < <(...)` and `mapfile < <(...)`
  collectors when the command feeds a gate decision.

## Sibling Search

- Mental model: if a list-consuming command exits successfully with no rows,
  the producer must have succeeded with no rows.
- fixed now: markdown and internal-link gates fail closed when tracked markdown
  discovery fails.
- fixed now: secretlint fallback fails closed when tracked/unignored file
  discovery fails.
- fixed now: gitleaks path fails closed when worktree file discovery or staging
  fails instead of silently switching to another scan mode.
- next sibling: `scripts/check-shell.sh` uses process substitution around
  `find`; it is not git-based but should be checked for the same collector
  failure shape.

## Seam Risk

- Interrupt ID: shell-file-listing-suppression
- Risk Class: contract-freeze-risk
- Seam: git file discovery -> shell quality gate empty-work decisions
- Disproving Observation: fake `git ls-files` failure now exits 1 for
  markdown, internal-link, secretlint, and gitleaks paths.
- What Local Reasoning Cannot Prove: whether maintainers want a shared shell
  helper instead of local copies once more shell collectors are audited.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Any gate that turns command output into proof input must check the producer's
status before classifying the result as empty. Process substitution is acceptable
only for optional inputs or when the producer failure is explicitly handled by
another checked status path.

## Related Prior Incidents

- `2026-05-22-run-quality-changed-path-suppression.md`: process substitution
  hid changed-path discovery failure before coverage selection.
- `2026-05-22-mutation-changed-diff-suppression.md`: failed changed-file
  discovery was represented as an empty mutation sample priority set.
- `2026-05-22-release-diff-failure-suppression.md`: failed release diff
  discovery was represented as an empty release delta.
- `2026-05-17-empty-policy-silent-pass.md`: earlier empty-state incident where
  missing enforcement inputs could look like intentional no-work state.

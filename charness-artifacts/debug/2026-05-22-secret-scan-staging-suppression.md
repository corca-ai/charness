# Secret Scan Staging Suppression Debug
Date: 2026-05-22

## Problem

`check-secrets.sh` used `tar --ignore-failed-read` while staging git-listed
files for the gitleaks scan, so a file that could not be staged could be omitted
from the scan while the gate still ran on a partial tree.

## Correct Behavior

Given the secret gate has a git-produced file list, when any listed file cannot
be staged into the temporary gitleaks scan directory, then the gate must exit
nonzero before invoking gitleaks. A complete staged tree may still run gitleaks
normally, and the secretlint fallback remains driven by the same checked
git-listing helper.

## Observed Facts

- `git ls-files -z --cached --others --exclude-standard` was already checked
  through `run_git_listing_to_file()`.
- The gitleaks path then piped that list through
  `tar --null --ignore-failed-read -T ... -cf - | tar -xf - -C "$scan_dir"`.
- GNU tar returns zero for missing listed files under `--ignore-failed-read`,
  after printing only a warning.
- A focused fixture can commit `secret.txt`, delete it from the working tree,
  and show that the listed file cannot be staged.

## Reproduction

Run `check-secrets.sh` in a repo where `secret.txt` is tracked by git but absent
from the working tree, with a fake `gitleaks` first on `PATH`. Before the fix,
tar warning output did not block the gitleaks invocation. After the fix, the
script exits 1, prints `check-secrets: failed to stage git file listing for
gitleaks scan.`, includes `secret.txt`, and leaves the fake gitleaks marker
absent.

## Candidate Causes

- The staging command intentionally ignored failed reads even though the file
  list was the proof boundary for the scan input.
- Existing tests covered git listing failure for both gitleaks and secretlint,
  but not failure to read a file after successful listing.
- The gitleaks fast path copied files into a temporary tree, creating a second
  producer boundary after git listing.

## Hypothesis

If the gitleaks staging tar command removes `--ignore-failed-read`, then any
listed-file staging failure will make the pipeline fail under `pipefail`, block
gitleaks, and preserve the existing staging error message.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_python_and_security_gates.py -k 'check_secrets'` passed.
- `shellcheck scripts/check-secrets.sh` passed.
- `ruff check tests/quality_gates/test_python_and_security_gates.py` passed.

## Root Cause

The gitleaks fast path checked the git file-list producer but then allowed the
staging producer to downgrade unreadable listed files into warnings. That
collapsed an incomplete secret-scan input tree into a normal scan.

## Detection Gap

- secret scan staging | no regression where git listing succeeds but staging a
  listed file fails | add a tracked-then-deleted fixture and assert gitleaks is
  not invoked.
- producer boundaries | listing and staging were treated as one proof step |
  keep both boundaries fail-closed.
- security gate output | partial scan warnings came from tar rather than the
  gate contract | preserve the explicit staging failure message before exit.

## Sibling Search

- Mental model: a checked file list is enough proof that the downstream scan
  input is complete.
- fixed now: gitleaks staging fails closed when any git-listed file cannot be
  copied into the scan directory.
- checked non-blocker: markdown/link/shell file-listing gates already fail on
  required discovery producer failure.
- checked non-blocker: the secretlint fallback passes the git-listed paths
  directly to secretlint after checked listing, so it does not have the extra
  tar staging producer.

## Seam Risk

- Interrupt ID: secret-scan-staging-suppression
- Risk Class: contract-freeze-risk
- Seam: git file listing -> temporary gitleaks scan tree -> secret scan result
- Disproving Observation: tracked-then-deleted file staging now exits 1 before
  fake gitleaks is invoked.
- What Local Reasoning Cannot Prove: whether every possible filesystem race
  during a live scan can be made deterministic rather than fail-closed.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Treat every producer that shapes a security scan input as a separate proof
boundary. File discovery success cannot justify ignoring copy/staging failures.

## Related Prior Incidents

- `2026-05-22-shell-find-collector-suppression.md`: shell lint could consume a
  partial file list after producer failure.
- `2026-05-22-shell-file-listing-suppression.md`: shell gates hid required git
  listing failures before file-based quality checks.
- `2026-05-22-run-quality-changed-path-suppression.md`: changed-path discovery
  failure could previously collapse into selected-test fallback behavior.

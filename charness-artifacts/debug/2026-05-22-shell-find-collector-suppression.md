# Shell Find Collector Suppression Debug
Date: 2026-05-22

## Problem

`check-shell.sh` used `find` output as the proof input for shell linting, but a
failed required discovery command could still let the gate run `shellcheck` on a
partial list or exit with an empty no-work result.

## Correct Behavior

Given `check-shell.sh` is discovering shell files, when required discovery for
the repo root or `scripts/` fails, then the gate should exit nonzero with the
collector command, exit code, stdout, and stderr. Missing `.githooks` remains an
intentional optional case, and a successful empty discovery may still exit 0.

## Observed Facts

- `scripts/check-shell.sh` used `mapfile -t sh_files < <({ find ...; find ...; find ...; } | sort)`.
- `mapfile` reports whether it read the process-substitution stream, not whether
  the producer commands succeeded.
- A command group can also hide an earlier failing `find` if a later `find`
  exits 0, so `pipefail` alone is not enough.
- Fresh-eye review reproduced the partial-list false green: root discovery
  emitted a file, `find scripts` exited 42, and the old script still reached
  `shellcheck` on the incomplete list.

## Reproduction

Run the real `check-shell.sh` in a temp repo with fake `find` and fake
`shellcheck` first on `PATH`. Make `find .` emit `./root.sh` and exit 0, make
`find scripts` emit `forced find failure` to stderr and exit 42, and make
`shellcheck` leave a marker if invoked. Before the fix the script could invoke
`shellcheck` on `./root.sh`; after the fix it exits 1, prints the partial stdout
and failure stderr, and leaves the shellcheck marker absent.

## Candidate Causes

- Process substitution hid the producer status from the file-list consumer.
- The collector command group did not return immediately when a required
  `find` failed.
- The intentionally optional `.githooks` discovery was not separated from
  required repo-root and `scripts/` discovery.

## Hypothesis

If shell-file discovery is moved into a checked collector function that returns
immediately on required `find` failure, writes its sorted output to a temp file,
and only then feeds `mapfile`, then incomplete discovery cannot be treated as a
complete shellcheck input list.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_python_and_security_gates.py -k 'check_shell'` passed.
- `shellcheck scripts/check-shell.sh` passed.
- `ruff check tests/quality_gates/test_python_and_security_gates.py` passed.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` synced the
  plugin copy.

## Root Cause

The gate coupled shell-file discovery to a list-consuming `mapfile` instead of
checking the producer as a proof boundary. Inside the producer, a later
successful `find` could overwrite an earlier required discovery failure, so a
partial file list could look like a successful complete list.

## Detection Gap

- shell lint gate | no fake-find regression for partial discovery failure before
  `shellcheck` invocation | add a real-script test that plants a root file,
  fails `find scripts`, and asserts `shellcheck` is not called.
- optional hook discovery | missing `.githooks` compatibility was implicit in a
  swallowed failure | add a success test proving absent `.githooks` still lints
  discovered `scripts/*.sh` files.
- shell collector review | process substitution and command groups were not
  reviewed as producer-status boundaries | scan shell gates for `mapfile < <(...)`
  and grouped pipelines that feed quality decisions.

## Sibling Search

- Mental model: if a sorted stream exists, every producer that contributed to it
  must have succeeded.
- fixed now: `check-shell.sh` fails closed on required root or `scripts/`
  discovery failure before calling `shellcheck`.
- fixed now: `.githooks` absence is an explicit optional branch, not an
  accidental process-substitution side effect.
- checked non-blocker: `install-git-hooks.sh` prechecks `.githooks` before
  `find "$HOOKS_DIR" | sort`, and `set -o pipefail` applies directly because the
  pipeline is not hidden behind `mapfile`.
- remaining candidate: release post-create verification recovery remains the
  only named deferred proof-suppression item in the current handoff.

## Seam Risk

- Interrupt ID: shell-find-collector-suppression
- Risk Class: contract-freeze-risk
- Seam: shell file discovery -> shellcheck quality gate input list
- Disproving Observation: fake partial `find` failure now exits 1 and prevents
  the fake `shellcheck` marker from being written.
- What Local Reasoning Cannot Prove: whether a shared shell collector helper is
  worth the extra abstraction after this family of shell gates is fixed.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

When a shell gate pipes multiple producer commands into a gate decision, each
required producer must return explicitly on failure before the aggregate output
is consumed. Optional discovery should be represented as an explicit branch, not
as a swallowed command failure.

## Related Prior Incidents

- `2026-05-22-shell-file-listing-suppression.md`: git file-listing shell gates
  hid required discovery failures behind `mapfile` or fallback scan modes.
- `2026-05-22-run-quality-changed-path-suppression.md`: process substitution
  hid changed-path discovery failure before coverage selection.
- `2026-05-22-mutation-changed-diff-suppression.md`: failed changed-file
  discovery was represented as an empty mutation sample priority set.

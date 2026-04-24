# Init Repo Unreadable Markdown Debug
Date: 2026-04-24

## Problem

`charness update` failed while refreshing the install surface because
`skills/public/init-repo/scripts/inspect_repo.py` raised `FileNotFoundError`
for `/Users/ted/.claude/plugins/marketplaces/corca-plugins/.cwf/projects/260216-03-hitl-readme-restart/session-log.md`.

## Correct Behavior

Given `charness update` refreshes the install surface, then it should not scan
the current working repo for onboarding unless the operator passes
`--target-repo-root`.

Given `init-repo` or `quality` inventories fixed-string source guards, then the
scanner should ignore hidden workflow/cache directories, skip any remaining
unreadable markdown file, emit a structured warning, and keep the review
command running.

## Observed Facts

- The traceback came from `init_repo_adapter._source_guard_rows`.
- The failing path ended in `session-log.md`, a volatile workflow artifact path.
- The same direct `read_text()` pattern existed in the quality brittle
  source-guard inventory.
- `charness update` built doctor payloads that included repo onboarding for the
  current working directory even though update is primarily an install refresh.
- Existing tests covered valid source-guard tables but not unreadable markdown
  paths discovered by `Path.rglob("*.md")`.

## Reproduction

Create a temp repo with a valid source-guard spec and a broken markdown symlink,
then run `skills/public/init-repo/scripts/inspect_repo.py --repo-root <repo>`.
Before the fix, reading the broken symlink can raise `FileNotFoundError`.

Run installed `charness update --json` from a repo with malformed onboarding
state. Before the fix, update still tried to inspect that repo by default.

## Candidate Causes

- A broken symlink was yielded by markdown discovery and followed by
  `Path.read_text()`.
- A workflow cleanup removed a markdown file between `rglob()` discovery and
  file read.
- A consumer repo contains external workflow artifacts under a project path
  that should be advisory input, not a hard install/update dependency.
- Update reused the doctor payload builder without distinguishing install
  refresh from explicit repo onboarding inspection.

## Hypothesis

If update skips repo onboarding unless `--target-repo-root` is explicit, and
source-guard scanners ignore hidden directories plus catch `OSError` around
markdown reads, then install refresh stops depending on volatile consumer repo
files while explicit reviews still leave operator-visible evidence.

## Verification

Added regression tests for skipped update onboarding, hidden workflow markdown
dirs, and unreadable markdown specs in both init-repo inspect and quality
brittle source-guard inventory.

## Root Cause

`charness update` ran repo onboarding by default for the invocation CWD, and the
source-guard scanners treated every markdown path discovered by `rglob()` as
readable. Hidden workflow directories, broken symlinks, and volatile files
violate that assumption.

## Seam Risk

- Interrupt ID: init-repo-unreadable-markdown
- Risk Class: operator-visible-recovery
- Seam: consumer repo workflow artifacts scanned during install/update refresh
- Disproving Observation: local regression tests cover broken markdown symlinks
- What Local Reasoning Cannot Prove: the exact filesystem state on the other Mac at the time of failure
- Generalization Pressure: monitor

## Interrupt Decision

- Premortem Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep update's install refresh path separate from explicit repo onboarding, keep
advisory scans out of hidden workflow/cache directories, and surface skipped
paths through structured warnings instead of Python tracebacks.

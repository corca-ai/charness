# Doc Link Repo Boundary Debug
Date: 2026-04-20

## Problem

Issue `#43` reported that `scripts/check_doc_links.py` allowed a checked-in
markdown link to escape the current repo root and point at a sibling checkout
such as `../../../other-repo/...` when that path existed on the maintainer
machine.

## Correct Behavior

Given a repo-owned markdown document,
when it contains a relative markdown file link,
then the validator should only accept the link if it resolves inside the
current repo root and the target exists there.

## Observed Facts

- `scripts/check_doc_links.py` resolved relative links with
  `(doc.parent / relative_target).resolve()`.
- The script only checked `candidate.exists()` after resolution.
- A sibling checkout path outside the repo therefore passed locally whenever
  that external path existed.
- Clean single-repo environments such as GitHub Actions then failed later
  because the sibling checkout was absent.

## Reproduction

- Create `repo/docs/handoff.md` with a link like
  `../../other-repo/README.md`.
- Create `other-repo/README.md` as a sibling directory outside `repo`.
- Run `python3 scripts/check_doc_links.py --repo-root repo`.
- Before the fix, validation passed because the resolved target existed.

## Candidate Causes

- The validator enforced path syntax but not the repo-boundary invariant.
- Relative-link validation assumed local filesystem existence was a sufficient
  portability check.
- Repo docs encoded a file-link convention, but no deterministic test covered
  sibling-checkout escape paths.

## Hypothesis

If `check_doc_links.py` rejects any resolved relative target outside
`repo_root`, then maintainer-local sibling checkout links will fail at the
shared default gate instead of leaking into downstream release or CI workflows.

## Verification

- Added a `candidate.relative_to(root)` boundary check before the existing
  `candidate.exists()` check.
- Added a regression test that creates a real sibling repo path outside the
  repo root and verifies the validator now fails with `escapes repo root`.
- Re-ran `pytest -q tests/quality_gates/test_check_doc_links.py`, `ruff check`
  on the touched files, and `python3 scripts/check_doc_links.py --repo-root .`.

## Root Cause

The shared doc-link validator treated "resolves to an existing file" as the
whole invariant. It never encoded the stronger portability rule that checked-in
markdown links must stay inside the current repo root.

## Prevention

- Keep repo-boundary enforcement inside the shared validator instead of relying
  on reviewer memory.
- Preserve the sibling-checkout regression test so future refactors cannot drop
  the invariant silently.
- Treat cross-repo references as plain text or gathered local artifacts rather
  than markdown file links.

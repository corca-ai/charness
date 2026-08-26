# Goal Run `backlog-637` — artifact preflight export boundary

## Scope receipt

- Repository: `corca-ai/charness`
- Parent Goal Run: `#724`
- Work item: `backlog-637` / issue `#637`
- Base SHA: `3d08c6bb238bcf3c0cb713e40123328a9fc7b79f`
- Target SHA: `3d08c6bb238bcf3c0cb713e40123328a9fc7b79f`
- Proof branch: `proof/issue-637-artifact-preflight-20260827`
- Proof path: `/tmp/charness-637-proof-20260827`
- Path scope:
  - `scripts/check_artifact_surface_preflight.py`
  - `plugins/charness/scripts/check_artifact_surface_preflight.py`
  - `tests/quality_gates/test_check_artifact_surface_preflight.py`
- Worktree shape: named branch, non-detached, isolated index/git dir; clean
  before and after proof. `__pycache__`, pytest cache, basetemp, and coverage
  were kept outside the proof worktree.

## Implemented boundary

Commit `3d08c6bb238bcf3c0cb713e40123328a9fc7b79f` resolves registered shape
producers against the package containing the preflight dispatcher. Canonical
`skills/public/...` paths work in the source checkout; exported plugins use the
flattened `skills/...` path. The resolver refuses missing and ambiguous
producer candidates and names both candidate paths. Consumer artifact roots are
never searched for Charness-owned shape producers.

## Executed proof

1. `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
   --pytest-target
   tests/quality_gates/test_check_artifact_surface_preflight.py` — `62 passed`.
2. The test's export-only consumer fixture exercised a flattened positive
   `critique --emit-stub` run — exit `0` with the required sections.
3. The same fixture removed the flattened producer — exit `1` with
   `missing shape source` and the `flattened-installed` candidate.
4. The same fixture supplied both canonical and flattened producers — exit `1`
   with `ambiguous shape source` and both candidates.
5. `py_compile`, Ruff, and source/mirror byte comparison passed.

The earlier broad changed-line runner is not used as a blocking gate here. It
was an inappropriate whole-provider mutation proof for this slice and remains
a non-claim; no large test expansion was added to make it green.

## Non-claims

This proves the Charness source and export-layout contract plus a temporary
consumer-shaped fixture. It does not prove an installed host, marketplace or
GitHub installation, remote CI, retro-planner behavior, release, push, tag, or
hosted enforcement. No installed-host mutation or fresh-eye review was run.

## External readback

- The #637 body was updated through `goal-run-apply` with
  `body_verified: true`; started/terminal observations are
  `backlog-637-artifact-preflight-20260827-1.started.json` and
  `backlog-637-artifact-preflight-20260827-1.terminal.json`.
- Independent `issue_tool.py read` returned `comments_read: true`,
  `comment_count: 2`, the accepted boundary and proof body, and state `CLOSED`
  after closeout.
- `close-with-comment --classification bug --reason completed` read preflight
  state `OPEN`, posted the carrier, and read back `state: CLOSED`.
- The close comment is
  `https://github.com/corca-ai/charness/issues/637#issuecomment-5429922177`.
- `verify-closeout --carrier manual-fallback
  --manual-fallback-reason operator-directed-manual-close
  --expect-state CLOSED` returned `status: verified` through
  `issue_verify_closeout@gh` / `backend-state-readback` with no missing fields.
- The fresh-eye critique was intentionally skipped under the operator-directed
  implementation path and remains an advisory, not a claim of execution.

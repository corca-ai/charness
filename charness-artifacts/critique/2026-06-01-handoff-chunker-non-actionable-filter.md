# Fresh-Eye Critique: Handoff Chunker Non-Actionable Filter

Target: handoff chunker candidate filtering before merge/rank.

Packet consumed: `charness-artifacts/critique/2026-06-01-101145-packet.md`

## Change

The handoff parser now drops non-actionable pickup entries before the user sees
ranked chunks:

- local/repo/branch/worktree/open-issue preflight commands such as `git status`,
  `git log`, and `gh issue list`
- activation entries that reference a `Status: complete` goal artifact
- `during`/`while` cadence or invariant constraints that should shape execution

The live handoff was also refreshed so the next bare pickup presents only the
#184/#261 issue choice.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated.

Reviewers:

- Pasteur (`019e82ab-4e5e-74b0-a821-572b09d764f2`) — semantic correctness
- James (`019e82ab-63ad-7500-ad0c-475dbd63622c`) — docs/workflow alignment
- Epicurus (`019e82ab-7832-7ce0-a356-5463141c8e98`) — regression/export coverage
- Noether (`019e82b2-c779-7cf3-9b5f-f7f828759354`) — counterweight

## Act Before Ship

Fixed before closeout:

- Broadened local-state preflight filtering so "Verify local branch state" and
  issue-list refresh entries do not survive merely because they are not written
  as "Verify local state".
- Broadened completed-goal activation filtering so markdown-link goal
  references are handled, not only slash-command activation strings.
- Added repo-cwd inference for the explicit `docs/handoff.md` CLI shape, so
  completed-goal filtering works for the advertised direct-path parser command.

## Counterweight Triage

No remaining ship blocker after the fixes.

Bundle anyway:

- Keep the live handoff rewrite, parser tests, docs contract, retro, and plugin
  mirror in the same commit because they are one workflow correction.
- Keep the current-handoff pipeline regression because the observed failure was
  user-visible routing output.

Over-worry:

- Do not expand this into a general English classifier now.
- Do not block on arbitrary explicit handoff paths outside the repo cwd; those
  already need `--repo-root` for repo-backed behavior.

Valid but defer:

- The activation-word heuristic is broad. If a future handoff needs to run
  analysis from a completed goal as real work, narrow that classifier then.

## Verification Cited

- `pytest -q tests/test_handoff_chunker_parse.py tests/test_handoff_chunker_end_to_end.py`
- live parser/proposer pipeline on `docs/handoff.md` emitted one actionable
  candidate: choose #184 or #261
- broad changed-surface pytest passed after fixes

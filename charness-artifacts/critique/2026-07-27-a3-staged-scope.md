# Critique Review

Date: 2026-07-27

## Decision Under Review

Fix bug-hunt A3: a deletion-only or rename-only staged commit scheduled zero
commit-boundary gates, because one path list — collected with
`--diff-filter=ACM` — was asked both "what does this commit touch" and "which
staged files exist on disk". The scheduling list now comes from
`collect_staged_scope_paths` (`--name-status --find-renames -z`, both rename
sides); the per-file validator list is derived from it by `is_file()`.

## Failure Angles

- **Jackson (problem framing).** The named problem was "this class of commit
  reaches HEAD ungated"; the delivered fix is "this class of commit is
  scheduled". Of the gates a deletion now schedules, only
  `check_staged_mirror_drift` reads the index — the rest walk the worktree, and
  `check_staged_reversion` passes a genuine deletion by design. So the hook now
  prints gate names and `ok` over a deletion most of those gates did not
  inspect: legible assurance where there used to be silence, which is the same
  class (d) in a more trusted form. Separately, the second list still used
  `ACM`, so a renamed-and-edited file — new content, on disk, exactly what a
  per-file validator exists for — got no `py_compile`, no `ruff`, no length
  check, and a test pinned that as the control.
- **Gawande (operational).** The presence guards covered the gates whose own
  script the commit might delete, but only 3 of ~12 sites; deleting
  `scripts/validate_attention_state_visibility.py` would have scheduled the
  script it just removed and refused its own commit. A whole-surface validator
  keyed on one named file (`validate-handoff-artifact`) crashed with
  `FileNotFoundError` when that file was the deletion. And `git rm --cached` is
  now blocked by `check_staged_reversion`, whose recovery line told the operator
  to `git add` the file back — undoing the commit they meant to make.

## Counterweight Pass

- Fixed in-slice: the rename half (the per-file list is derived from scope now),
  the crash on a single-file validator's own deletion, the unguarded validator
  sites, and the `git rm --cached` recovery text.
- Recorded rather than fixed: "scheduled is not judged". Making the scheduled
  gates read the index instead of the worktree is a change to every gate, not to
  the plan, and it is the honest residual — so the ledger row is `PARTIAL` and
  names it.
- Over-worry: the cost of the newly-scheduled plan. Planning a deletion-only
  commit measures 0.1s; the expensive members (`staged-plugin-mirror-drift`,
  `run-evals`) are the same ones an equivalent edit already paid for.
- Not this slice: A5 and A6, which sit inside the floor A3 restores. Fixing them
  raises what this floor is worth, and both are their own rows.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/staged_commit_gate_plan.py:245 | action: fix | note: the per-file list still used `--diff-filter=ACM`, so a renamed-and-edited file with a syntax error planned no py_compile/ruff/lengths; reproduced, then derived from scope by `is_file()`
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/staged_commit_gate_plan.py:97 | action: fix | note: deleting `docs/handoff.md` scheduled `validate-handoff-artifact`, which raised FileNotFoundError; single-file validators now key on the still-present list
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/staged_commit_gate_plan.py:296 | action: fix | note: six surface validators had no presence guard, so retiring one would schedule the script the commit deletes and refuse its own commit
- F4 | bin: act-before-ship | evidence: moderate | ref: scripts/check_staged_reversion.py:120 | action: fix | note: `git rm --cached` is now reachable by this gate, and its recovery line told the operator to `git add` the file back; the untrack reading and the env escape are named now
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md:49 | action: document | note: the row claimed FIXED while only scheduling was fixed; it is PARTIAL with the three residuals named
- F6 | bin: bundle-anyway | evidence: strong | ref: scripts/staged_commit_gate_plan_helpers.py:22 | action: fix | note: `-z` with `text=True` would crash the hook on a non-UTF-8 filename, since git stops C-quoting under `-z`; bytes plus surrogateescape
- F7 | bin: bundle-anyway | evidence: strong | ref: scripts/staged_commit_gate_plan_helpers.py:143 | action: fix | note: the argv-site `is_file()` rule belongs in the gates, not the callers — the structural sweep and full closeout pass one collapsed list that has always carried deletions
- F8 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md:96 | action: document | note: scheduled is not judged — only the mirror-drift gate reads the index; the rest walk the worktree, so `git rm --cached` of a linked doc passes them | follow-up: deferred docs/handoff.md `## Next Session`
- F9 | bin: valid-but-defer | evidence: strong | ref: .githooks/pre-commit | action: document | note: probed — `git revert` runs no pre-commit hook, so reverting a sync commit still lands a mismatched mirror ungated; pre-push is the floor for that shape | follow-up: deferred docs/handoff.md `## Next Session`
- F10 | bin: over-worry | evidence: strong | ref: scripts/staged_commit_gate_plan.py:1 | action: defer | note: the added plan cost for a deletion-only commit measures 0.1s, and its expensive members are the ones an equivalent edit already paid

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, where the repo contract uses typed `bounded-reviewer` agents with session-model inheritance rather than the Codex model/effort request
- Host exposure state: host-defaulted
- Application state: host-defaulted — typed `bounded-reviewer` spawns accepted; the adapter's Codex fields were not sent
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — three bounded read-only reviewers: one scoped pass over the
first draft (9 findings, including the invariant break on the positional caller
shape and the `-z` decode hazard) and two angle reviewers (Jackson, Gawande) over
the packet below. Boundary fingerprint snapshot/verify bracketed each window and
returned `parent-attributed` with zero unattributed drift.

Non-claim: the F1-F4 repairs were not re-reviewed by a further fresh eye. Each is
covered by a regression test and, for F1 and F2, by a live reproduction with a
control.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-27-a3-staged-scope-packet.json
- Packet SHA256: 2427477f5afa05a2f4a5653e897ec1fa7ef2fbb72bba0ed4ed85868a7d5e48e9
- Identity SHA256: b3ce81e238c660002c28b9c731eab20a045e8a1be44fadde92799a6777d87732

## Boundary Ownership

- Producer: git's staged-diff query produces the path facts; `staged_commit_gate_plan` produces the gate plan from them.
- Consumer: `.githooks/pre-commit`, `run_slice_closeout.py --predict-commit`, and the structural sweep.
- Owning surface: `repo-python` owns the planner; the gates it schedules own their own verdicts.
- Verdict: owned-correctly

## Deliberately Not Doing

- Not converting the scheduled gates from worktree readers to index readers.
  That is what "scheduled is not judged" would take, and it is a change to every
  gate rather than to the plan. Recorded as the A3 residual instead of half-done.
- Not adding a pre-commit trigger for `git revert` / auto-merge. Git does not
  run the hook there at all; pre-push is the documented floor for that shape.
- Not fixing A5 or A6, which sit inside the index-hygiene trio this floor
  schedules. They are their own rows and raise what the floor is worth.

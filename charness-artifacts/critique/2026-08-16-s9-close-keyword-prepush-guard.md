# Critique Review
Date: 2026-08-16

## Decision Under Review

Building the close-keyword pre-push guard (handoff Next Session item 1), and repairing
the commit-msg carrier whose comment-stripping let the prose "S7 closes\n#626/..."
close [#626](https://github.com/corca-ai/charness/issues/626) on push. Both are
verdict logic on a proof surface, so the two-round floor applies.

## Failure Angles

- A new BLOCKING gate at an irreversible boundary that refuses correct work: the
  remedy for a false refusal here is rewriting a landed commit, and an unfollowable
  remedy makes `--no-verify` routine.
- A second surface claiming to apply "the same floor" as an existing one while
  re-deriving its parts, so the two answer differently and the newer one fails open.
- Detection narrower than GitHub's own close grammar: a spelling the scanner misses is
  a silent false green in exactly the class the guard exists for.
- A repaired proof surface carrying the class it repaired — the reason the contract
  requires the second round.
- Calibration over a population selected for passing the floor already, reported as if
  it were a false-refusal rate.

## Counterweight Pass

Round 1 (two bounded reviewers, disjoint angles: verdict logic, operator surface) and
round 2 (one bounded reviewer over the repairs) produced 24 findings. Round 2 earned
its cost for the third measured slice running: both of its blockers were defects **in
round 1's repairs**, not in the original code.

REAL, and acted on. Round 1's two blockers were both false-green/false-refusal pairs
on the same axis: the guard re-derived classification from the message alone (so an
artifact-carried `question` close was refused with a demand for the root-cause claims
that disposition exists to refuse), and it omitted the protected-target authorization
entirely (so a `--no-verify` commit close-keywording a crosswalk-protected issue *with
a complete ledger* passed). Both were fixed by CALLING the carrier's parts —
`_issue_closeout_artifacts` gained injectable readers, `partition_closeout_carriers`
was extracted so the pause carve-out has one answer.

Round 2 then found that the new maintainer arming check — written to stop the guard
being silently deleted — counted a MENTION as an invocation and tested `|| true`
against the first of the invocation's two continued lines. Both reproduced by
execution before repair. Both are verbatim the class the SIBLING arming check's own
round 2 had already removed one lane over: re-deriving a judgment instead of calling
the module's existing `_logical_lines`/`_split_commands` machinery re-created it.

OVER-WORRY, and left alone. Round 2 suggested the guard's `_git` should share the
worktree doctor's probe. Their contracts are opposite — the doctor answers `None` for
a missing fact because that is a SKIPPED check there, while a git failure that
degraded to "no commits" would render the guard's pass on an unread range. Recorded as
`intentional` in `dup-review.json` with that reasoning rather than merged.

NOT FIXED, disclaimed instead. The guard over-fires on non-default-branch pushes,
applies today's floor to old commits a merge brings in, is not offline-safe for the
`consolidated` classification, and caps an unbounded ref-creation scan. Each is named
in its module docstring's `Not claimed` list; naming a gap is not closing it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_guard.py | action: fix | note: classification re-derived from the message alone refused an artifact-declared `question` close as a `bug`.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_guard.py | action: fix | note: `authorize_commit_carrier` was never called, so a protected close with a valid ledger passed.
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_scan.py | action: fix | note: `GH-N` and full-issue-URL close spellings were undetected; widened here, shared-scanner gap stated not fixed.
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_scan.py | action: fix | note: `origin` was hard-coded; the hook now forwards the remote git is pushing to.
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_guard.py | action: fix | note: a crash exited 1, this guard's documented REFUSAL code.
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py | action: fix | note: `missing_close_keywords` could name a number the message visibly contains, with a remedy already satisfied.
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_guard.py | action: fix | note: "never linked" overstated the evidence; only "closed" is supported.
- F8 | bin: act-before-ship | evidence: strong | ref: scripts/validate_maintainer_setup.py | action: fix | note: a MENTION counted as an invocation, so the guard could be deleted with the check green.
- F9 | bin: act-before-ship | evidence: strong | ref: scripts/validate_maintainer_setup.py | action: fix | note: the swallow test read the first of the invocation's two continued lines.
- F10 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_guard.py | action: fix | note: repo-filtered targets reached authorization, so a protected FOREIGN ref escaped.
- F11 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_guard.py | action: fix | note: the pause overlap used the filtered set and briefs were dropped with no report.
- F12 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_guard.py | action: fix | note: an artifact-only commit was refused with a summary asserting a close keyword it did not have.
- F13 | bin: act-before-ship | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py | action: fix | note: F6's repair covered the `#`-line channel only, leaving the fenced one unfollowable.
- F14 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_scan.py | action: fix | note: the no-exclusion fallback was unbounded; now capped, and the cap is reported.
- F15 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_close_keyword_scan.py | action: fix | note: comma-lists were not honored for `GH-`/URL spellings.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (the repo's typed read-only subagent), session-inherited model.
- Requested spawn fields: `subagent_type: bounded-reviewer`, scope prompt, no host addressing `name` (per the repo's spawn-shape rule).
- Host exposure state: host-defaulted
- Application state: host-confirmed: each reviewer reported `envelope-unbound does not apply` — Bash/Edit/Write/Agent absent, so the read-only envelope bound.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No packet was consumed; reviewers read the working tree and diffed against origin/main. -->

## Boundary Ownership

- Producer: `prepush_close_keyword_scan.py` (which commits, what the message says, what GitHub would close) and the issue skill's `verify_closeout` (the ledger verdict).
- Consumer: `.githooks/pre-push`, via `prepush_close_keyword_guard.py`.
- Owning surface: the closeout floor stays with `check_issue_closeout_commit_msg.py` and the issue skill; the push-time placement is the guard's.
- Verdict: owned-correctly

Detection and range resolution moved to `scripts/prepush_close_keyword_scan.py`, which
answers factual questions and renders no verdict; the guard owns the verdict, refusal,
and remediation. The closeout FLOOR is CALLED, not copied — `partition_closeout_carriers`
was extracted to its owner for that reason. The arming check stayed with
`validate_maintainer_setup.py`, beside the sibling lane it mirrors.

## Proof

- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock
  --refresh-broad-pytest-proof` -> `status: completed`, exit 0, 9893 passed, 0 failed.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .` ->
  `status: clean`, 0 unmapped, exit 0.
- Calibration: `--range <sha>~1..<sha>` over `git log -400 origin/main`; 20 carry a
  close-keyword ref, 19 pass, the one refusal is `7817ace88`. Re-measured after both
  rounds and after the file split.

## Non-claims

Round-2 repairs and the coverage tests that followed them ship at the two-round cap
and are themselves unreviewed. The GitHub-side behavior of `GH-N` and issue-URL close
spellings is asserted from documentation knowledge, not measured against GitHub. No
push, tag, bump, publish, or issue closure has run, and no consuming repo has executed
this tree.

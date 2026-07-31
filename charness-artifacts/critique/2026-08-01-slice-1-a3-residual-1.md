# Slice 1 — A3 residual 1 — the untrack shape the staged-worktree gate could not see
Date: 2026-08-01

## Decision Under Review

Repair the pre-commit gate that printed `ok` over a commit removing a file from the tree, by replacing the staged-vs-unstaged intersection with an index-entry question.

Two bounded read-only review rounds, each bracketed by
`reviewer_boundary_fingerprint.py` snapshot/verify. Round 2 read the REPAIRS,
which is where this repo's measured pattern says the class recurs.

## Failure Angles

- Does the repaired predicate hold at its edges, or does it carry the class it repairs?
- Who does a newly-blocking condition refuse that it should not?
- Does every consumer of the changed verdict still render and consume it correctly?
- Does the repair state a claim over a scope it did not establish?

## Counterweight Pass

Findings binned below. `act-before-ship` items were fixed inside the slice and
re-verified; `over-worry` items are recorded with why they were not folded rather
than silently dropped. Every blocker was reproduced by the parent with a command
before being accepted — no finding here rests on a reviewer's reading alone.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_staged_worktree_consistency.py:153 | action: fix | note: round 1: git's default rename detection collapses `D old` + `A new` into one `R` entry whose `--name-only` prints only the destination, so the first cut's `--diff-filter=D` missed move-and-recreate entirely. Confirmed by command. The predicate is now `staged(--no-renames) - ls-files(--full-name)`, dropping the status-letter allowlist the file's own comment argues against
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_staged_worktree_consistency.py:249 | action: fix | note: round 1: the offered `git rm <path>` exits 128 on a path with no index entry (`pathspec ... did not match any files`), so the gate handed the operator a command that errors after blocking their commit. Confirmed by running it. `rm` and `git reset --` are offered now
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_staged_worktree_consistency.py:236 | action: fix | note: round 1: untracking on purpose is a legitimate workflow and the message treated it as a mistake with no correct exit. Reframed: the refusal is about assurance scope, and the bypass is named inside the branch the way check_staged_reversion does
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/check_staged_worktree_consistency.py:167 | action: fix | note: round 2 (read the repairs): the case-only-rename exemption folded over the whole tracked set, so untracking `Foo.md` escaped whenever an unrelated `foo.md` was tracked — a fail-open in the repaired predicate, in the class the slice closes. Parent reproduced it returning `[]` before fixing; the fold is over `staged & tracked` now
- F5 | bin: bundle-anyway | evidence: strong | ref: scripts/check_staged_worktree_consistency.py:146 | action: fix | note: round 2: `--no-renames` belonged on BOTH reads. An intent-to-add rename (what `git add -p` creates for a new file) hid a staged-then-deleted path and resurfaced the ORIGINAL shape-1 defect. Confirmed by command
- F6 | bin: bundle-anyway | evidence: strong | ref: scripts/check_staged_worktree_consistency.py:147 | action: fix | note: round 2: `ls-files` is cwd-relative and cwd-scoped while `diff --cached` is repo-wide, so from a subdirectory the orphan branch would quietly go empty. `--full-name` added
- F7 | bin: over-worry | evidence: moderate | ref: scripts/check_staged_worktree_consistency.py:29 | action: document | note: the bypass env var's NAME does not describe an untrack. Real, and the message names the case in words instead; adding a second control would multiply bypasses for one question

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, where this repo's contract uses typed `bounded-reviewer` agents with session-model inheritance rather than the Codex model/effort request
- Host exposure state: host-defaulted
- Application state: host-defaulted — typed `bounded-reviewer` spawns accepted; the adapter's Codex fields were not sent
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each reviewer was handed an inline slice packet naming the changed files, the pre-slice baseline command, the intent, and the reproduction. -->

## Boundary Ownership

- Producer: git's index/worktree diff queries
- Consumer: `.githooks/pre-commit` via `run_slice_closeout.py --predict-commit`, plus the structural sweep
- Owning surface: `repo-python` owns the gate; the gates it schedules own their own verdicts.
- Verdict: owned-correctly

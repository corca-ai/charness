# Issue 529 resolution critique
Date: 2026-08-07

## Decision Under Review

Resolving issue #529 by making `issue_create.py` emit `number`/`url` (the names the
skill contract already documented) rather than by rewriting the docs to say
`created_number`/`created_url`, plus removing `state` from the create-side ask and adding
a test that reconciles doc-named ledger keys against the helper's emitted keys.

## Failure Angles

- **Symptom vs. cause.** A rename could satisfy the reported nulls while leaving the
  intra-skill naming split (`issue_read.py` emits `number`, create emitted
  `created_number`) that produced them. Direction (b) removes the split; direction (a)
  would have entrenched it. The causal review established direction (b) has zero
  programmatic consumers — four assertions in one test file, nothing outside this repo's
  tests.
- **A prevention claim larger than the prevention.** The new guard covers multi-key brace
  sets in three named doc files against a static source parse. Claiming it "prevents the
  class" would be the same over-claim this repo's north star exists to refuse.
- **Gate weakening dressed as tidy-up.** Deleting `state` is load-bearing for the green:
  direction (b) alone leaves the new guard failing on `state`. If `state` had been a real
  obligation, deleting it to reach green would be exactly the move the goal's Non-Goals
  forbid.
- **The guard's own fragility.** A static parse over a whole source file can silently
  widen its "emitted" set when a formatter wraps an unrelated dict literal, making the
  assertion pass when it should fail. A doc-side regex unscoped from the create ledger
  can fail on a correct doc, and the cheapest escape from that red is deleting the guard.
- **Residual null.** `number` is still null when the backend's output cannot be parsed —
  the one state where an agent might still retry and file a duplicate.

## Counterweight Pass

- The `state` removal is **not** a narrowing. Nothing depends on state at create time:
  `issue_read.py` `READ_FIELDS` and `issue_close.py` (`json_fields="number,state,url"`)
  are read/close paths and are untouched, and the obligation is re-stated with a concrete
  command for the paths that genuinely need it. Removing an obligation no create path can
  ever satisfy is not weakening a gate. Recorded explicitly because it *is* load-bearing
  for the green and a future reader deserves to audit the judgment rather than rediscover
  it.
- The alias retention is not clutter. Charness installs into consumer repos where
  something may already read `created_number`; four keys carrying two values is the
  cheaper error than breaking an unseen reader, and both sites document which names are
  canonical.
- The residual null is inherent rather than a defect: the payload is self-describing and
  carries `verify_error` telling the reader to re-read before reporting success. It
  needed a doc clause, not code.
- `SKILL.md:48` and `resolve-flow.md:50` were deliberately left unedited. That is not an
  oversight — direction (b) made those sentences true, which is the stronger outcome than
  editing them.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_issue_closeout_discipline.py:79 | action: fix | note: the emitted-key parse read the whole source file, so a formatter wrapping any other dict literal would widen the set and turn the assertion into a false negative; scoped it to the payload literal
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_issue_create.py:124 | action: fix | note: the behavioral suite pinned only the deprecated names, so deleting the canonical keys left it fully green; added runtime assertions on `number` and `url`
- F3 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_issue_closeout_discipline.py:58 | action: fix | note: the doc-side regex was unscoped, so bracing the read shape `{number, url, state}` would fail the guard against a correct doc and invite deleting it; scoped to brace sets containing `repo` and added the prose-named keys explicitly
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/issue/references/closeout-discipline.md:36 | action: fix | note: nothing told the agent that a null `number` means the issue EXISTS and must not be retried, which is the last corner of the reported job-to-be-done; added the clause
- F5 | bin: valid-but-defer | evidence: strong | ref: skills/public/issue/scripts/issue_create.py:138 | action: file-issue | note: `url` takes raw backend stdout, so on a backend printing a bare number the URL slot holds a non-URL; a wrong value rather than a false negative, outside this issue's job-to-be-done | follow-up: https://github.com/corca-ai/charness/issues/539
- F6 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/SKILL.md:69 | action: file-issue | note: sibling of the same class found by the causal review's sweep — the step names `scaffold_quality_artifact.py` but instructs flags and keys owned by `resolve_quality_artifact.py` | follow-up: https://github.com/corca-ai/charness/issues/538
- F7 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_create.py:128 | action: document | note: the four-keys-two-values duplication reads like clutter but breaks nothing — no validator or test asserts an exact payload key set, and consumer-repo readers of the old names are the reason to keep them

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (repo-typed read-only reviewer, `.claude/agents/bounded-reviewer.md`).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, session-model inheritance per the per-host split for Claude Code hosts.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported `envelope-bound (only Read, Grep, Glob visible — no Bash/Edit/Write/Agent)` and returned findings inline.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Two delegated reviewers ran on this issue: a causal review before the
fix was designed (root cause, sibling sweep, blast radius) and this resolution critique
after it was built. Both ran read-only in the shared parent worktree, and both windows
were bracketed by `reviewer_boundary_fingerprint.py` snapshot/verify, each returning
`verdict: clean` with empty drift.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewers were given the changed-file
set inline and read the worktree directly at HEAD 8b33af7e plus uncommitted changes. The
binding floor is therefore not turned on for this artifact. -->

## Boundary Ownership

- Producer: `skills/public/issue/scripts/issue_create.py`, which owns the create payload's key names.
- Consumer: the agent following `skills/public/issue/SKILL.md` and `references/closeout-discipline.md`, which renders the closeout report from that payload.
- Owning surface: the `issue` public skill package (helper plus its own references).
- Verdict: single-surface

## Non-Claims

- The new guard narrows the seam; it does not close the class. It does not cover keys
  named singly in prose beyond the three listed explicitly, camelCase keys, doc files
  outside the three scanned, or runtime emission as opposed to source literals.
- Whether doc-to-helper key agreement should be gated repo-wide — and whether such a gate
  is declaration-based or inference-based — is a design question this resolution
  deliberately does not answer.
- The causal review's sibling sweep reached `announcement`, `debug`, `hitl`, `handoff`,
  `release`, the `issue` planner, and `issue-backend.md` (all clean) and found one
  mismatch in `quality`. It did NOT reach `create-skill`, `critique`, `gather`,
  `ideation`, `impl`, `narrative`, `prove`, `retro`, `setup`, or `spec` at depth, so the
  sweep is a sample, not a closed set.

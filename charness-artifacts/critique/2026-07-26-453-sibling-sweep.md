# #453 sibling sweep critique
Date: 2026-07-26

## Decision Under Review

Whether the ~14 same-class siblings named in the #453 resolution critique are now
proven, and whether the way they were proven is itself honest. The siblings are
rejection and renderer lines that are *executed* by existing tests but never
*asserted* — the defect class #453 was filed for. This slice is test-only: no
source line in `scripts/quality_policy_defaults.py` or
`skills/public/quality/scripts/runtime_budget_lib.py` changed.

## Failure Angles

One bounded read-only `bounded-reviewer` subagent, scoped to five angles rather
than to re-running the suite: per-line coverage completeness against the named
list, assertion strength (which mutant does each new test actually kill), the
defaults-vs-merge vacuity trap, test placement/ownership against the
`check-python-lengths` cap, and false claims in the new module's own prose.

Parent-side integrity was fingerprinted around the review with
`reviewer_boundary_fingerprint.py`; post-review `verify` reported
`{"ok": true, "drift": []}`, so no reviewer-attributable worktree or index change
occurred.

## What The Review Changed

**The gate blocked mid-slice and the first split was the wrong one.**
`check-python-lengths` failed at 953 code lines against an 800 cap once the
`mutation_testing` rejection tests were added to `test_quality_mutation_testing.py`.
The reactive fix moved only enough tests to clear the bar, which left
`_validate_mutation_score_break`'s two branches proven in two different files —
the exact split-proof condition #453's own root-cause finding names. The reviewer
caught it as an undeclared seam rather than a cohesive one. The seam is now
declared and cut on its merits: **every** `mutation_testing` rejection reached
through `load_quality_adapter` moved, and the module docstring names what stayed
behind and why (`test_auto_issue_label_with_comma_is_refused` calls the private
helper directly, so it sits on the other side of the entrypoint boundary).

**Three claims in the new module's own prose were false.** "Every case here
asserts the exact message AND that the merged config kept its default" was
falsified by five acceptance/edge cases in the same file; "only its rejection
messages live here" was falsified by six tests still in the old module; "which is
what a mutant on either line would break" was untrue for the two unknown-sub-key
warnings. On the slice whose entire subject is that an unproven claim reads as
proof, an overclaiming docstring is the wrong artifact to ship. All three
rewritten to describe what the code does.

**Two assertions killed no mutant and now do.**

- The `continue` at `quality_policy_defaults.py:504` survived: for a non-string
  rule entry, removing it appends a second, misleading `` unknown rule `7` ``
  error while both original assertions still pass. Pinned with a
  `not any("contains unknown rule" ...)` guard, the same idiom the module already
  used for `auto_issue.enabled`.
- The two unknown-sub-key tests asserted that a typo'd key did not become
  configuration — which is true for every mutant, since an unknown key matches no
  branch either way. Rewritten to supply a **known** key after the typo, so the
  skip must be a `continue` rather than a `break` or an early return.

## Counterweight Pass

- **The defaults-vs-merge trap is avoided in the rejection cases, and the reviewer
  verified it by hand rather than asserting it.** `infer_quality_defaults` seeds
  each block before validation, so `== DEFAULT_*[key]` could be vacuous. It is not,
  because every rejection case supplies a value differing from the default in value
  or type. The one near-miss (`declined: 1` against a `False` default) is carried
  by the explicit `is False`.
- **The two "scalar block" assertions are weak, and are now labelled as weak
  rather than removed.** When the block is a scalar the validator returns `None`
  and the key keeps its seeded deep copy, so the equality discriminates only a
  `return None -> return value` mutant. The message assertion is what has teeth
  there; the comments now say so instead of claiming more.
- **Duplicate mapping-shape coverage is deliberate, not oversight.** The
  `standing_doc_provenance` / `changed_line_mutation_gate` gate scripts already
  pin `must be a mapping` through their own `adapter_errors` payload. Measured
  coverage showed the canonical in-process `load_quality_adapter` path was
  genuinely unreached, so these are a second entrypoint rather than a second copy.
  The docstring says which is which.
- **`test_a2_auto_issue_enabled_wrong_type_rejected` was dropped, not lost.**
  `test_a2_auto_issue_string_slot_non_string_is_rejected` supplies the same
  `enabled: "yes"` and asserts the same message plus the negative delegation
  check, so the deleted test was strictly subsumed.

## Residuals

- **Mutation strength is inferred, not measured.** Every claim here is per-line
  coverage plus a hand-traced mutant argument; no cosmic-ray run was executed
  against these lines. The scheduled run is the measuring instrument, and it has
  not run on this tree.
- **`_ADAPTER_HEADER` and the resolve helper are now duplicated** across
  `test_quality_mutation_testing.py` and the new module. `dup-ratchet` passes, so
  it is below the clone threshold; it will drift.
- **The reviewer had no Bash**, so it could not run pytest, `tokei`, or
  `git show HEAD:<path>`. It marked which of its claims that limited — notably it
  could not confirm which new tests were moves versus new writes, and could not
  compute the code-line counts behind the cap that forced the split.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_adapter_block_rejections.py:1 | action: fix | note: the module docstring declared an ownership boundary the tree did not have — six `mutation_testing` rejection tests remained in the old module; the seam was cut to clear a line cap rather than on its merits
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/quality_policy_defaults.py:302 | action: fix | note: `_validate_mutation_score_break`'s type and range branches were proven in two different files, reproducing #453's split-proof root cause inside the sweep meant to close it; both now live together
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_adapter_block_rejections.py:1 | action: fix | note: three docstring claims were falsified by cases in the same file; rewritten to state what the module actually asserts and what deliberately lives elsewhere
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/quality_policy_defaults.py:504 | action: fix | note: the per-entry `continue` survived every assertion; removing it appends a spurious second error, now pinned by a negative-message guard
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/quality_policy_defaults.py:439 | action: fix | note: the unknown-sub-key tests could not fail, since an unknown key matches no branch with or without the guard; now supply a known key after the typo so `continue` vs `break` is discriminated
- F6 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_quality_adapter_block_rejections.py:260 | action: document | note: the two scalar-block post-rejection assertions discriminate only one mutant shape; kept for that shape, with the comment reduced to what is true
- F7 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_quality_adapter_block_rejections.py:38 | action: defer | note: the duplicated adapter header/resolve helper is authored duplication introduced by the split, but sits below the dup-ratchet threshold and `dup-ratchet` passes
- F8 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/critique/2026-07-26-issue-453-resolution.md:108 | action: defer | note: mutation strength for these lines remains inferred until a scheduled cosmic-ray run covers them; per-line coverage is the proof this slice has

## Reviewer Tier Evidence

- Requested tier: typed `bounded-reviewer` subagent (read-only: Read/Grep/Glob), session-model inheritance per the Claude Code host branch of the repo subagent contract.
- Requested spawn fields: `subagent_type: bounded-reviewer`, five-angle scope prompt for the #453 sibling sweep, no model or effort override.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported Read/Grep/Glob only, with no Bash/Edit/Write/Agent, and the parent-side boundary fingerprint verified clean.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

The reviewer's central finding was not about coverage — coverage was complete on
first pass — but about the split that coverage forced, and about the module's own
prose overclaiming. Both were acted on. Its per-line trace of the
defaults-vs-merge mechanism also converted an assumption of mine into a checked
fact.

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer read the uncommitted worktree at aeca200f plus the #453 resolution critique and docs/handoff.md. -->

## Boundary Ownership

- Producer: the adapter-block validators, which decide whether a bad config is refused and with what message.
- Consumer: an operator reading a failed `charness` quality run and editing `.agents/quality-adapter.yaml` from the message text.
- Owning surface: the tests, which are the only thing that makes the message text a contract rather than an incidental string.
- Verdict: owned-correctly — the message text is the producer's contract and the tests are where it is held, so the proof belongs beside the validators rather than in the consuming gate scripts.

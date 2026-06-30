# Resolution Critique — issue #409 (cautilus capture→grade evidence loss)

- **Target**: code-critique (recurrence focus), pre-close resolution critique for the fix of
  corca-ai/charness#409.
- **Execution**: 3 bounded fresh-eye angle subagents + 1 separate counterweight subagent.
- **Fresh-Eye Satisfaction**: parent-delegated (repo `Subagent Delegation` contract).
- **Packet Consumed**: charness-artifacts/critique/2026-06-30-212038-packet.md

## Change

Fix #409 (two gaps in the cautilus capture→grade evidence pipeline that blinded the
SUBSTANCE judge for skill runs that COMMIT their slice and/or COMPLETE cleanly):

- **Gap 1** — `capture-skill-run.sh` records the detached worktree base commit to
  `base-commit.txt`; `_changed_files` / `preserve_outputs` / `_git_added_lines` diff
  against that base (param defaults to `HEAD`) instead of the run-advanced `HEAD`.
- **Gap 2** — `_write_transcript` reads the complete `stream.jsonl` instead of the
  session-tree `*.jsonl` glob (which can drop the final assistant block on clean exit).
- Sibling `_git_added_lines` bundled; `output_lines` caveat updated.

## Capability at Stake

The per-skill correctness sweep's substance judge must grade against the run's REAL
produced files (non-empty `outputs/`) and COMPLETE transcript (closeout present), proven
through the final consumer (`grade_skill_outcome.py`), not just the producer helpers.

## Angles + Findings

1. **Behavioral fidelity / edge-case correctness** — diff `base→working-tree` correctly
   unions committed-since-base + uncommitted-vs-base (deduped, no double-count); untracked
   set disjoint. stream-json emits one complete `assistant` event per message (no
   partial/duplicate text); secret-safety (tool_result excluded) preserved. Base edge cases
   (multi-commit, amend, missing marker→`HEAD`) do not crash. End-to-end tests reach the
   real grader. Only gap: the simultaneous commit+untracked case is not exercised by a
   fixture (logic sound by construction).
2. **Recurrence / detection-gap** — the bash `base-commit.txt` emit is unexercised by any
   test and `_capture_base`'s `HEAD` fallback SILENTLY MASKS its removal (reintroduces #409
   with zero test signal); deferred sibling `build-skill-execution-observation.mjs`
   (tree-as-truth for metrics) was unrecorded in `deferred-decisions.md`; the `base="HEAD"`
   default is a latent trap for a hypothetical third callsite; no anti-pattern guard for new
   `diff … HEAD` / tree-glob.
3. **Seam integrity / metric-semantics / portability** — `output_lines` redefinition is
   in-scope and safe (self-test excludes it; advisory; never gates; internally consistent).
   base-commit.txt cross-process seam robust (same `out_dir` both sides, `.strip()`, `HEAD`
   fallback) — stronger than the `SESSION_TREE=` stdout marker. No bundle pollution;
   secret-safety preserved; soft host coupling on stream-json schema (degrades to empty).

## Structured Findings

<!-- bins: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer -->
- F1 | bin: bundle-anyway | evidence: moderate | ref: tests/test_skill_efficiency_ab.py | action: fix | note: static guard pinning the bash base-commit.txt emit and its ordering, the untested seam whose silent failure (masked by the HEAD fallback) recreates #409.
- F2 | bin: bundle-anyway | evidence: moderate | ref: docs/deferred-decisions.md | action: document | note: D32 records the build-observation.mjs tree-as-truth metrics sibling with a reopen trigger so the deferral does not rot.
- F3 | bin: over-worry | evidence: weak | ref: scripts/run_skill_efficiency_ab.py:224 | action: defer | note: a ratchet for the base default defends a non-existent future callsite; both real callsites pass an explicit base.
- F4 | bin: over-worry | evidence: weak | ref: tests/test_skill_efficiency_ab.py | action: defer | note: grep anti-pattern guard and combined commit+untracked fixture guard patterns nobody is adding; logic sound by construction.
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/agent-runtime/build-skill-execution-observation.mjs:81 | action: defer | note: the metrics extractor tree-as-truth channel itself stays deferred (recorded as D32); advisory metrics, separate mjs slice.

## Counterweight Triage

- **Act Before Ship**: none — the JTBD is proven end-to-end by the grader tests.
- **Bundle Anyway (this commit)**: F1 (static bash-emit ordering guard) and F2 (D32 entry).
- **Over-Worry (ignored)**: F3 (default-base ratchet) and F4 (grep anti-pattern / combined
  fixture).
- **Valid but Defer**: F5 (the `build-observation.mjs` metrics channel itself, recorded as
  D32); the `output_lines` non-comparability of pre-fix reports is accepted (advisory).

## Deliberately Not Doing

- No ratchet/lint guard against future `diff … HEAD` or tree-glob siblings (Over-Worry:
  speculative future callsites; the two real callsites are correct and tested).
- No rerouting of `build-observation.mjs` metrics off the session tree (deferred as D32 —
  advisory metrics, separate `.mjs` slice; bundling would widen past the reporter's JTBD).
- No live `claude -p` capture re-run in this resolution (the bash emit is proven by the
  static ordering guard + the `_capture_base` consumer contract; the JTBD behavior is proven
  end-to-end in Python against the real grader). Non-claim: no second committing-skill live
  capture was run (matches the issue's own n=1 caveat).

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied -->
- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: host-defaulted
- Application state: requested fields not host-confirmed; Claude Code spawned its default bounded reviewer

## Next Move

Bundle the two cheap prevention items (done), commit with close keywords + behavioral
verdict, push, verify GitHub state.

Fresh-Eye Satisfaction: parent-delegated

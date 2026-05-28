# Retro

Mode: session

## Context

Closeout of the #230 + #229 achieve goal at
`charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md`.
The goal targeted the lighter-self-substitution pattern itself: the
agent inline-paraphrasing a prescribed sub-skill instead of executing
it. 8 slices delivered: spec → Before-phase anti-anchoring + portability
self-test → achieve After-phase guard + shared helper → issue closeout
guard → release closeout guard → markdown hook quieting (reordered
ahead) → push-gate batching → closeout. Pairs with the source retro
at `charness-artifacts/retro/2026-05-28-issue-226-achieve-run.md`.

## Evidence Summary

Host-log probe (`probe_host_logs.py`) found this Claude Code session's
JSONL (`906f4924-6f39-4090-ab3f-05eba79695a7.jsonl`). Real metrics
parsed inline:

- output tokens: 332,815; non-cache input: 31,783; cache_read: 82.1M;
  cache_creation: 1.04M.
- wall clock: 04:39:15Z → 05:27:20Z (~48 minutes) at probe time; this
  retro and the final commit/handoff steps still add some tail.
- 265 tool calls: Bash 124, Edit 56, Read 48, TaskUpdate 15, Write 9,
  TaskCreate 8, Agent 3, Skill 1, ToolSearch 1.
- 3 bounded fresh-eye subagent critiques (slice 1 plan, slice 6 hook,
  slice 7 push-gate router), all parent-delegated; none collapsed to
  a same-agent local pass.

Compare against the #226 origin retro: ~377.8K output / 120 tool calls /
~2h52m wall for a single-issue goal. This run did 8 slices in roughly
the same token budget, 2.2× the tool calls, and 0.28× the wall time.

## Waste

1. **Doc-link backtick trap, hit three times.** Each spec/reference
   edit had to be rewritten when `check_doc_links` flagged backticked
   paths that did not yet exist. The `<repo-root>/` placeholder
   convention is documented in `recent-lessons.md` (Repeat Trap #4) but
   each new file rediscovered it. Net cost: ~6 extra Edit calls across
   slices 1, 3, 5, 6. Smaller than #230 Waste 2 but still chronic.
2. **Markdown table column-style auto-rejection at slice 1 commit.**
   The slice-1 spec table was written with extra column alignment
   padding (`| --- | --- | --- |` works; `| ----------- | ... |`
   doesn't). Caught by the pre-commit markdown lint and re-committed
   without flooding context (because slice 6 was not yet in). Two extra
   commit attempts on slice 1 alone.
3. **F4 oversimplification in slice 1 critique.** The critique fold for
   F4 said "no `critique/SKILL.md` body change" but `validate_skills`
   strictly requires every reference file to be listed in SKILL.md.
   Slice 2 had to relax F4 to "no net growth" (1-line addition + 1-line
   compression). This was caught fast at slice 2's first validate run,
   but the spec doc had to be amended after the fact. The critique
   reviewer probably could have caught this if I had given them the
   validate_skills source rather than only the policy summary.

Phase-aware note: Bash 124 is high but the per-slice breakdown shows
~15 Bash calls/slice spread across read-only probes (git status, file
inspection), targeted test runs, and validator invocations — discovery
+ verification, not waste. The 3 subagent critiques cost 3 Agent calls
each but each surfaced concrete findings I folded. Critique cost was
real value, not ceremony.

## Critical Decisions

- **Mid-run slice reorder of slice 6 ahead of slices 4/5/7.** The
  markdown hook flood was visibly polluting context in real time;
  closing it mid-run saved measurable tokens on subsequent slices.
  Recorded honestly in the slice 6 log so a fresh session can
  reconstruct the reorder from the artifact (slice-2 portability
  self-test paid off here — the goal artifact is fresh-session
  reconstructible).
- **Hard refusal of upsert to `complete` without evidence (slice 3).**
  The achieve After-phase gate is now non-bypassable. Live-tested by
  this very session: a `upsert_goal --status complete` attempt before
  this retro ran refused with exit 1 and the structured payload. The
  goal-closes-its-own-pattern proof.
- **Slice 1 critique blockers folded inline before activation.** F1
  (issue-verify duplication), F3 (slice-plan discriminator), F4
  (200-line gate trade-off) all folded into the spec before slice 2
  began. F2 (skip-reason enum) was deferred to slice 3 with a named
  reopen condition; closed exactly when the achieve guard's real
  evidence shape existed. This is the spec-critique-acted-on flow
  working as designed.
- **Slice 7 push-gate critique caught F1 (docs-only would have lost
  link/slug/pointer regressions).** The fold from "skip on docs-only"
  to "docs-only subset of ~15 phases" was the design-changing finding.
  The subset then immediately caught a real preexisting find-skills
  inventory drift — vindication of the fold within minutes of writing
  it.

## Expert Counterfactuals

- **Atul Gawande (checklist discipline):** the achieve After-phase
  guard from slice 3 IS the checklist this goal targets. The retro
  artifact + host-log probe lines are now mechanically required before
  `complete`. The previous-session miss ("Auto-Retro paraphrased
  without running retro") cannot recur from the achieve lifecycle
  prescribed path. Changed action this run: invoked `retro` as a Skill
  (this file), invoked `probe_host_logs.py` as a script, and recorded
  both as real paths in the goal artifact — not as inline paraphrase.
- **Donald Knuth (premature optimization):** the slice 7 docs-only
  subset is exactly the right *form* of optimization — the broad gate
  was demonstrably bottlenecking work, and the optimization preserves
  every correctness check via the subset rather than skipping. The
  alternative (force-full-gate-everywhere forever) would have kept the
  100-120s cost on every closeout/bookkeeping commit. Changed action:
  measured the real cost (50.6KB hook output × 8+ commits this session)
  before approving the change, not after.

Through-line: every slice that produced a guard or filter was first
*demonstrated* (live-flood capture for slice 6, live-refusal capture
for slice 3, live-drift catch for slice 7's F1 fold) before being
called done. The #226 miss was claiming verification without the
verification step running; this run made each verification step
execute observably.

## Next Improvements

- **workflow:** include the validator source (e.g.
  `validate_skills.py` line ranges) in slice-level critique prompts
  when the change touches a public skill. Slice-1 F4 fold was relaxed
  in slice 2 because the critique didn't see the strict listing rule;
  giving the reviewer the gate code itself prevents that.
- **capability:** the `<repo-root>/` placeholder convention should be
  auto-applied or pre-checked in spec/doc authoring. Repeat-trap #4
  hit three times this run despite already being documented. A small
  pre-commit fixer (`check_doc_links --autofix-placeholder`) would
  retire this trap.
- **memory:** this artifact captures the closed-loop achievement —
  the goal aimed at #230 + #229 also produces its own proof artifacts
  (retro file + host-log probe + 3 subagent critiques). Future
  achieve runs inherit the gate by default; no separate enforcement
  needed.

## Sibling Search

Transferable waste pattern: "doc-link backtick trap" (Repeat Trap #4)
hit three times this session despite being documented in
`recent-lessons.md`. Four-axis scan:

- **scripts**: `check_doc_links.py` is the gate; no sibling validators
  miss path-like backticks the same way.
- **skills**: every public skill's `SKILL.md` and references would
  benefit from the same auto-fixer; the convention isn't skill-local.
- **docs**: this trap appears whenever a planned-future file is
  referenced; spec authoring is the most exposed surface (slice 1, 3,
  5, 6 all hit it).
- **workflow**: the trap is independent of the work being done; it's
  an authoring-tool gap.

Decision: workflow-wide. Candidate follow-up: add
`scripts/check_doc_links.py --autofix-placeholder` or a pre-commit
fixer that converts `\`unbuilt/path.py\`` to `\`<repo-root>/unbuilt/path.py\``
when the path doesn't yet exist. Deferred (not filed as an issue this
run) since it's a hygiene improvement, not a workflow gap.

## Persisted

yes — written to `charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md`.

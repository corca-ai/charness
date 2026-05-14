---
name: hitl
description: "Use when automated review is not enough and deliberate human judgment needs to be inserted into a bounded review loop. Keeps review state resumable, chunked, and adapter-driven without hardcoding one host runtime."
---

# HITL

Use this when the user wants interactive review, approval-gated change
inspection, or a resumable human-in-the-loop pass over a bounded target.

`hitl` is one public concept:

- insert deliberate human judgment where automation is insufficient
- keep the review bounded and resumable
- record rules and decisions so the loop can continue coherently
- make the review comfortable for the human: explain dense generated tables or
  matrices in plain language before showing raw structure as evidence

Borrow Atul Gawande-style checklist discipline here: keep the loop explicit
enough that judgment stays human while omissions, handoff loss, and repeated
misreads become harder.

## Bootstrap

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then
resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

## Worktree Readiness

Before review-driven commits, run a non-fatal worktree readiness probe when
`charness` is available. If the JSON status is not `pass`, surface
`charness worktree prepare` as the next action and have the operator confirm
before continuing. Skip silently when `charness` is not on PATH.

```bash
command -v charness >/dev/null 2>&1 && charness worktree doctor --json || true
```

Default durable artifact:

- `<repo-root>/charness-artifacts/hitl/latest.md`

Default runtime directory:

- `.charness/hitl/runtime`

If the adapter is missing but the repo would benefit from explicit chunking or
state location, scaffold one:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

Runtime helpers:

- start: `python3 "$SKILL_DIR/scripts/bootstrap_review.py" --repo-root .`
- report queue: `python3 "$SKILL_DIR/scripts/render_report.py" --repo-root . --input <packet.json>`
- pre-edit gate: `python3 "$SKILL_DIR/scripts/check_review_state.py" --repo-root . --session-id <session-id> --phase pre-edit`
- cursor gate: `python3 "$SKILL_DIR/scripts/check_review_state.py" --repo-root . --session-id <session-id> --phase cursor-advance`
- closeout sync: `python3 "$SKILL_DIR/scripts/sync_review_artifact.py" --repo-root . --session-id <session-id>`
- durable artifact freshness check: `python3 "$SKILL_DIR/scripts/sync_review_artifact.py" --repo-root . --session-id <session-id> --check`
- chunk self-check: `python3 "$SKILL_DIR/scripts/check_chunk_contract.py" --chunk-file <path>`

If the adapter is missing, stop after surfacing or scaffolding the bounded
review contract. Do not start a resumable human-review loop in earnest until
the repo has named where state, rules, and queue ownership live.

## Workflow

1. Restate the review goal.
   - what human judgment is needed
   - what target is under review
   - what must not be auto-decided
   - if the input came from a `quality` `NON_AUTOMATABLE` proposal, preserve
     its review loop, observation point, and revisit cadence
2. Resolve the target surface.
   - branch diff
   - one file or doc
   - one proposal or spec artifact
3. Resolve or create resumable state.
   - scratchpad for agreements and rationale
   - state file for cursor and status
   - rules file for accepted review rules
   - queue file for pending chunks or items
4. Start with agreement-level context.
   - record the user's review criteria and concerns first
   - capture any high-level rule that should apply to every later chunk
5. Review in bounded chunks per `references/chunk-contract.md`.
   - each chunk: original material as direct, line- or hunk-anchored excerpt;
     related context; Agent Assessment against active criteria; non-binding
     Recommended Disposition; concrete decision for the human; then pause
   - render Markdown-in-Markdown excerpts with display-only pseudo-tags such
     as `<bash>`, `<md>`, or `<json>`; do not nest fenced code blocks
   - if the source is a table, scorecard, or generated matrix, lead with the
     plain-language interpretation and keep raw structure as evidence
   - question-only chunks are not enough; the agent commits to a recommended
     disposition before asking the human
6. Propagate accepted rules.
   - if the user gives a stable rule, write it down and apply it to remaining
     chunks in the same run
   - before editing or rewriting a chunk, read accepted rules, state the active
     constraints, and verify target, cursor, queue item, and line bounds
7. Record accepted chunk state.
   - after every accepted chunk, write the accepted working text to the
     scratchpad before presenting the next chunk
   - keep rationale, caveats, and summaries under notes instead of making them
     the only durable state
   - update the state cursor, such as `last_presented_chunk_id`, after the
     accepted text is recorded
   - after a requested rewrite is applied to HITL working text or session
     state, show the rewritten chunk excerpt before advancing, ask
     accept-or-revise, and record `applied_rewrite_review_status`
   - treat chat as the review UI and the scratchpad/state files as the durable
     review state
   - if the user points out a missed state update, run a short retro and repair
     the HITL state before continuing
8. Resume honestly.
   - if files or docs changed out of band, resync intent before presenting the
     next chunk
9. Close with a concise summary.
   - what was reviewed
   - what rules were accepted
   - what still needs action or follow-up
   - sync live runtime state into `charness-artifacts/hitl/latest.md` and run
     the durable artifact freshness check
10. Report Mode. For generated report packets, render first-class decision
    cards with concrete questions, plain-language evidence interpretation,
    optional evidence links, comment fields, and display-only suggested actions.
    Order cards by decision leverage when priority metadata is present, then
    recalculate the remaining queue after explicit human review input. If an
    accepted answer makes the remaining queue stale, present a human-owned
    restart recommendation instead of mechanically continuing through obsolete
    chunks.
    Persist only explicit human decisions/comments as structured JSON; untouched
    `unreviewed` cards must be dropped from the saved decisions packet.
11. Apply Phase. Only after all chunks are accepted and the closing summary is
    written, propose the consolidated target edit as one reviewable operation.
    Never edit the target file mid-chunk or between accepted chunks while the
    review loop is still in progress. If `require_explicit_apply` is true, wait
    for an explicit apply instruction before touching the target file.
12. Full Target Review. After accepted edits are applied or staged, present the
    updated target with an Agent Assessment and Recommended Disposition per
    `../../shared/references/agent-assessment-invariant.md`, record
    `full_target_review`, and only then close the target as accepted.

## Output Shape

The result should usually include Review Goal, Target, Current Chunk, Original
Material, Related Context, Agent Assessment, Recommended Disposition (display-only), Decision Needed, Active Rules Applied, Target/Cursor
Checked, Accepted Working Text, Accepted Rules, and Next State.

## Guardrails

- Do not present isolated snippets without enough context for judgment.
- Do not present a chunk that asks for a disposition without an Agent
  Assessment and a non-binding Recommended Disposition.
- Do not ask for judgment on summary-only paraphrases when the underlying text,
  diff, or artifact excerpt can be shown directly.
- Do not make raw tables or generated matrices the primary human review
  surface; explain the table's significance first and keep the raw structure as
  inspectable evidence.
- Do not put nested fenced code blocks inside user-facing review excerpts; use
  display-only pseudo-tags for inner examples instead.
- Do not persist suggested decisions as human approval unless the human
  explicitly changes a card decision.
- Do not keep advancing when the current item is still unresolved.
- Do not advance to the next accepted chunk while the scratchpad and state
  cursor still depend on chat memory.
- Do not edit a chunk while `target_cursor_checked` is stale or accepted rules
  have not been selected into `active_rules_applied`.
- Do not summarize a requested rewrite as "applied and checked" or advance
  `last_presented_chunk_id` while `applied_rewrite_review_status` is pending.
- Do not silently apply edits that require explicit human approval.
- Do not edit the target file while the review loop is in progress; touch it
  only in the Apply Phase and after explicit approval when required.
- Do not close a target as accepted until the `full_target_review` item records
  whole-target acceptance or the explicit need for another pass.
- Do not close or hand off a HITL run while runtime state is newer than the
  durable artifact, or while durable target, cursor, queue, or accepted rules
  disagree with the runtime session.
- Do not lose accepted review rules between chunks in the same session.
- If manual edits changed the target out of band, resync intent before the next chunk.

## References

- `references/adapter-contract.md`
- `references/chunk-contract.md`
- `references/report-mode.md`
- `references/state-model.md`
- `references/rule-propagation.md`
- `../../shared/references/agent-assessment-invariant.md`
- `scripts/bootstrap_review.py`
- `scripts/check_chunk_contract.py`
- `scripts/check_review_state.py`
- `scripts/render_report.py`
- `scripts/sync_review_artifact.py`

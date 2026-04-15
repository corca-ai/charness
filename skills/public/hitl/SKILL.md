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

## Bootstrap

Resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Default durable artifact:

- `charness-artifacts/hitl/latest.md`

Default runtime directory:

- `.charness/hitl/runtime`

If the adapter is missing but the repo would benefit from explicit chunking or
state location, scaffold one:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

When starting a new HITL run, initialize runtime artifacts:

```bash
python3 "$SKILL_DIR/scripts/bootstrap_review.py" --repo-root .
```

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
5. Review in bounded chunks.
   - each chunk should include the primary material, enough related context,
     and the concrete question that needs human judgment
   - pause for user judgment before moving on
6. Propagate accepted rules.
   - if the user gives a stable rule, write it down and apply it to remaining
     chunks in the same run
7. Resume honestly.
   - if files or docs changed out of band, resync intent before presenting the
     next chunk
8. Close with a concise summary.
   - what was reviewed
   - what rules were accepted
   - what still needs action or follow-up

## Output Shape

The result should usually include:

- `Review Goal`
- `Target`
- `Current Chunk`
- `Related Context`
- `Decision Needed`
- `Accepted Rules`
- `Next State`

## Guardrails

- Do not present isolated snippets without enough context for judgment.
- Do not keep advancing when the current item is still unresolved.
- Do not silently apply edits that require explicit human approval.
- Do not lose accepted review rules between chunks in the same session.
- If manual edits changed the target out of band, resync intent before the next
  chunk.

## References

- `references/adapter-contract.md`
- `references/chunk-contract.md`
- `references/state-model.md`
- `references/rule-propagation.md`
- `scripts/bootstrap_review.py`

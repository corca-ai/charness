# Rule Propagation

HITL becomes more valuable when repeated human guidance turns into durable
review rules inside the current session.

When the user gives a stable rule:

- normalize it into a short durable entry
- record its scope when known
- apply it to remaining chunks
- revisit already reviewed material only if the new rule actually changes the
  judgment
- if the rule came from repeated observations in a `quality` handoff loop,
  record whether it should become an `automation_candidate`

Do not keep the rule only in conversational memory.

## Active Pre-Edit Constraints

Before editing or rewriting a chunk, reread accepted rules for the current HITL
run and select the rules relevant to the current chunk. State those active
constraints briefly before patching so the human can see which rule set is
guiding the edit.

The pre-edit gate should also verify that target, cursor, queue item, and line
bounds match the chunk being edited. If the cursor is stale, the target differs,
or the line bounds exclude evidence needed for judgment, stop on the same chunk
and repair the review state before editing.

After editing, scan the changed chunk for known forbidden or risky term classes
before presenting it. If a violation is found, keep the cursor on the same chunk
until the rule violation is repaired or the reviewer changes the rule.

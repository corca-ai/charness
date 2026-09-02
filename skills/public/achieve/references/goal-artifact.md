# Goal Draft

The Goal Draft is one compact planning record for a long-running objective. It
holds intent until approval and then becomes immutable through Goal Binding.
Provider-backed Goal Run state carries execution; the draft is never a local
progress log or completion record.

## Location

```text
charness-artifacts/goals/<yyyy-mm-dd-slug>.md
```

The path is fixed, date-prefixed, and slugified. Values written into the record
are normalized and checked for balanced fences and headings so the markdown
shape survives readback.

## Shape

```markdown
# Achieve Goal: <title>

Created: <date>
Planning record: mutable until Goal Binding; the binding freezes these exact bytes.

## Goal
<outcome>

## Non-Goals
## Boundaries
## User Acceptance
## Agent Verification Plan
### Low-Cost Checks
### High-Confidence Checks
### External or Live Proof
## Slice Plan
| Slice | Objective | Why Now | Dependencies |
| --- | --- | --- | --- |
## Discuss Before Activation
- Discuss before activation: none — no consequential planning decision identified
## Context Sources
## Interview Decisions
## Plan Critique Findings
```

The planning sections are intentionally allowed to be empty while the plan is
being shaped. A consequential trigger in the planning material requires an
explicit resolved, confirmed, or approved discussion before binding. An
unanswered interview decision remains an ordinary wait for the operator and
does not become a local `blocked` state.

## Writer

Use the one planning writer:

```bash
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . \
  --slug acme-184-push-confidence \
  --fields-file /tmp/goal-fields.json
```

The JSON file may contain `title` and `goal-body`; it keeps prose out of a
shell. A new call scaffolds the complete planning shape. A later call updates
only the title and `## Goal` body, preserving authored planning sections. Once
the sibling `.binding.json` exists, the writer refuses all changes.

Do not add execution state to this record. Use the issue-owned Goal Run for
provider mutation and execution state.

## Binding and pickup

Approval freezes the draft and the binding records its SHA-256 as the identity
of the plan that was approved. The binding also records the parent identity and
the approved Work Item manifest. Resume uses the issue-native objective
`/goal #N`; the Goal Run pickup validates that identity and selects the provider
cursor's next child.

What is bound is identity, not prose. A child is identified by its
`<!-- charness-work-item-key: <key> -->` marker, membership by the provider's
sub-issue graph, and the plan by the approval-time draft hash. Child prose, the
parent's human-readable body, and the draft may be corrected afterwards; those
edits are reversible and visible in provider or git history, so pickup reports
`draft_amended` instead of refusing. A Work Item added after binding is an
*amendment*: the parent metadata carries `amendments`, each naming the issue,
rank, dependencies, reason, and operator approval, and the issue-owned
`add-child` operation records it. The binding file itself is never rewritten.

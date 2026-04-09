---
name: announcement
description: "Use when drafting or delivering a repo change announcement, release note, or chat-ready summary. Draft value comes first; delivery, audience, and omission policy stay adapter-driven."
---

# Announcement

Use this when the user wants a concise announcement of recent repo work, a
release-note style summary, or a delivery-ready team update.

`announcement` is one public concept:

- recover the human-facing value of recent changes
- draft the message in a stable shape
- optionally deliver it through an adapter-defined backend
- record what was delivered so later announcements can continue from there

## Bootstrap

Resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Default durable artifact:

- `skill-outputs/announcement/announcement.md`

Default delivery log:

- `skill-outputs/announcement/announcements.jsonl`

If the adapter is missing but the repo would benefit from explicit section
order, audience tags, or delivery defaults, scaffold one:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

Then inspect current state:

```bash
sed -n '1,220p' <resolved-announcement-artifact> 2>/dev/null || true
python3 "$SKILL_DIR/scripts/collect_commits.py" --repo-root .
python3 "$SKILL_DIR/scripts/infer_audience_tags.py" --repo-root .
git status --short
```

If the adapter is missing, use inferred defaults and continue. Missing delivery
config must not block drafting.

## Workflow

1. Restate the announcement goal.
   - draft only
   - draft plus delivery
   - release-note style versus chat-ready summary
2. Resolve drafting context.
   - collect commits since the last recorded announcement when possible
   - if no delivery record exists yet, use a bounded recent commit window
   - inspect commit intent or adjacent docs when the user-visible value is not
     obvious from the subject alone
3. Recover audience value before wording.
   - who benefits
   - what surface changed
   - what humans can now do, avoid, or understand better
4. Apply adapter policy.
   - ordered sections
   - audience tags when configured
   - omission lenses that force high-value but easy-to-miss items into the
     draft
5. Draft the message first.
   - prefer short sections and concrete bullets
   - explain why a change matters, not only the mechanism
   - omit low-signal hygiene unless the user explicitly wants a full changelog
6. Show the draft before delivery.
7. If the user wants delivery, resolve the backend seam only then.
   - `none`: draft only
   - `release-notes`: update a checked-in markdown file
   - `command`: run an adapter-defined post command
8. Record the result after delivery or explicit draft finalization.
   - append a JSONL record so the next run can continue from the current head

## Output Shape

The result should usually include:

- `Scope`
- `Audience`
- `Draft`
- `Delivery Plan`
- `Recorded Head`

## Guardrails

- Do not block draft creation on missing delivery backend.
- Do not silently invent audience tags when the adapter leaves them unset.
- Do not turn implementation details into the headline unless they changed
  human-visible behavior or operator confidence.
- Do not deliver anything without explicit user confirmation.
- If delivery depends on a repo helper, command template, or permission, say so
  explicitly before posting.

## References

- `references/adapter-contract.md`
- `references/draft-shape.md`
- `references/delivery-seams.md`
- `references/audience-policy.md`
- `scripts/collect_commits.py`
- `scripts/infer_audience_tags.py`
- `scripts/record_announcement.py`

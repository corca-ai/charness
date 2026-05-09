# Chunk Contract

Every HITL chunk should carry enough material for real judgment.

Minimum contract:

- original material under review, shown directly as the smallest excerpt
  sufficient for judgment
- source anchor for that material when possible: file path plus line span,
  diff hunk, or stable artifact section
- related context that explains why it matters
- agent assessment against the active review criteria and accepted rules:
  whether the chunk meets them, with concrete risks, gaps, or drift the agent
  noticed
- recommended disposition (`accept`, `revise`, `defer`, or a chunk-specific
  verb), explicitly non-binding and display-only — the human still owns the
  decision
- the concrete decision or question for the human, presented after the
  assessment and recommendation

Suggestions never auto-record as approval. See `report-mode.md` for the
persistence rules; the same rule applies to ordinary chunks: the recommended
disposition is metadata, not a default that becomes a decision when the
human stays silent.

When the chunk comes from a `quality` `NON_AUTOMATABLE` handoff, preserve:

- `review_question`
- `decision_needed`
- `must_not_auto_decide`
- `observation_point`
- `revisit_cadence`
- `automation_candidate`

Good chunks are:

- bounded
- direct about what text or diff is actually being judged
- line-anchored when possible
- stable enough to resume later

## Markdown-In-Markdown Presentation

When the original material is Markdown and includes fenced code examples, avoid
nested fences in the user-facing review chunk. Keep the outer excerpt in a
normal fenced block when that helps preserve the Markdown shape, and render
inner examples as display-only pseudo-tags:

```md
## Setup

Use the repo helper:

<bash>
./scripts/run-quality.sh
</bash>
```

The pseudo-tags are only for review presentation. They are not instructions to
edit the target document into pseudo-tag syntax.

Bad chunks are:

- isolated one-line excerpts
- summary-only paraphrases that hide the actual wording under review
- full-file dumps when only one local issue needs judgment
- giant undifferentiated walls of text
- nested fenced code blocks that make the rendered review excerpt ambiguous
- questions with no surrounding rationale
- "needs human review" labels with no decision, observation point, or revisit
  cadence

## Applied Rewrite Review

When the reviewer asks for a rewrite, revision, or other current-chunk change,
the next review surface after applying that edit must show the rewritten chunk
itself. A verification summary alone is not enough.

Minimum applied-rewrite surface:

- `applied_rewrite_review` state or scratchpad entry tying the rewrite to the
  chunk id
- applied chunk excerpt with a line anchor, hunk anchor, or explicit source
  boundary when possible
- enough surrounding context for the human to judge whether the rewrite fits
- Agent Assessment of how the rewrite fits the original criteria, with any
  remaining risks or drift, before the decision prompt
- Recommended Disposition (`accept`, `revise`, `defer`), explicitly
  display-only
- verification results only as secondary information
- a decision prompt asking whether the rewritten chunk is accepted or still
  needs another revision

## Full Target Review

When all chunks are accepted and edits are applied or staged, the full target
review surface presents the updated target as a whole. The same invariant
applies: include Agent Assessment + Recommended Disposition (display-only)
before the human's accept-or-revise decision. See
`../../../shared/references/agent-assessment-invariant.md`.

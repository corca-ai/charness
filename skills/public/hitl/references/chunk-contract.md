# Chunk Contract

Every HITL chunk should carry enough material for real judgment.

Minimum contract:

- original material under review, shown directly as the smallest excerpt
  sufficient for judgment
- source anchor for that material when possible: file path plus line span,
  diff hunk, or stable artifact section
- related context that explains why it matters
- the concrete decision or question for the human

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

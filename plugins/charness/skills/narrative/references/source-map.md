# Source Map

`narrative` begins by identifying the smallest honest set of documents that
currently define the repo's story.

Default order:

1. adapter-declared `source_documents`
2. inferred common docs when no adapter exists
3. adjacent docs discovered during alignment work

Freshness check rules:

- check git freshness before trusting a handoff as current truth
- remote-ahead does not automatically force a stop
- stop when local truth cannot be trusted without a merge or explicit user
  choice

Alignment rules:

- rewrite contradictions at the source, not only in the brief
- prefer one durable narrative over several parallel summaries
- keep the next-session handoff consistent with the newly aligned story

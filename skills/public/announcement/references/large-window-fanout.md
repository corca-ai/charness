# Large-Window Fan-out

Use when the announcement window spans many commits, multiple sources
(`in_progress_sources`, `control_repos`), or non-overlapping audience tags.
Single-pass triage is cheap when the window is small; it becomes noisy and
slow when the window is large or multi-source.

Fan-out is a judgment primitive, not a hard rule. Decide per call.

## When fan-out pays for itself

- the commit window is large enough that reading every `subject` plus most
  `body` content in one pass would crowd context
- the window spans more than one source (main repo plus one or more
  `control_repos`/`in_progress_sources` entries)
- `outputs[i]` declare audience tags that do not meaningfully overlap, so
  per-output drafting is independent work
- cadence is monthly or longer on a busy repo, so the triage payload is
  many small unrelated values

## When single-pass is cheaper

- the window is small enough that one pass already fits comfortably
- audience tags overlap heavily across outputs, so per-output drafting would
  redo the same triage
- the adapter is in `delivery_kind: none` (draft-only) on a short window
- the agent already holds the relevant context from a recent run

## Two fan-out seams

### Seam 1: commit-range or source partition

Partition `collect_commits.py` output by:

- commit-range chunks
- source (main repo vs each `control_repos`/`in_progress_sources` entry)
- audience tag when one tag dominates a contiguous range

Each subagent receives:

- its partition's commits with `subject`, bounded `body`, `trailers`,
  `closing_references`
- the same adapter policy (audience tags, omission lenses, sections,
  `outputs`)
- instructions to return audience-tagged bullets only, not finished section
  wording

The caller merges per-section before drafting final wording.

### Seam 2: per-output drafting

When `outputs` is non-empty and audience tags do not meaningfully overlap
across outputs:

- fan out per `outputs[i]`
- each subagent drafts one output's body from the same shared bullet pool
- no cross-output reconciliation is required at merge

## Merging partial drafts

- preserve the section order from adapter policy
- deduplicate bullets that landed in multiple partitions (same
  `closing_references` or near-duplicate subjects)
- run the omission-lens pass against the merged bullet list once, not per
  partition
- run public-body and audience-tone enforcement once on the merged draft
  (see `draft-shape.md`)

## Anti-patterns

- fanning out for a small window because subagents look modern
- failing to pass each subagent the adapter policy (audience tags, omission
  lenses, `outputs`) — partial drafts diverge in tone and section assignment
- accepting fan-out output without a merge pass — section bullets become
  noisy duplicates
- partitioning by file path or commit author instead of by audience or
  source — the partitions are not independent in audience value
- letting subagents invent new audience tags or section labels that the
  adapter never declared — merge becomes a relabeling exercise instead of a
  deduplication pass. The caller must compare every returned bullet against
  the adapter's `audience_tags` and `sections`; reject or remap before merging
  rather than papering over divergence in the final draft.

## Cost calibration

Partitioned triage costs roughly one read per partition plus one merge pass.
Single-pass triage costs roughly one read of the whole window. Fan-out pays
when each partition's output is already audience-tagged bullets the caller
can merge without re-reading commits, and when the window is large enough
that the partition reads can run in parallel without doubling wall-clock.

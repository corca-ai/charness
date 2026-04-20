# State Selection

Handoffs should include only the facts that change the next action.

## Keep

- current repo status when it affects continuation
- the most recent material output only when it changes the next command
- the first recommended next action and its prerequisite checks
- unresolved product or ops decisions
- one pointer to the artifact that owns detailed evidence
- a repo-local task id or task-state path when the repo ships a structured
  claim/submit/abort envelope for bounded agent work

## Drop

- low-level implementation detail that no longer matters
- stale history
- speculative future work that is not the next step
- coverage, runtime, or test deltas that are already recorded in a quality
  artifact and do not change the next action
- stable release numbers, version surfaces, or dogfood/proof counts that are
  already owned elsewhere and do not change the first move
- always-loaded host instruction surfaces that the host already injects
  automatically unless omitting them would change the first move
- debug or retro story detail when a link is enough

## Compression Rule

For each bullet, ask: would removing this line make the next operator choose a
different first action? If not, drop it or replace it with a reference. Trust
the next operator to follow one good link and infer stable repo defaults.

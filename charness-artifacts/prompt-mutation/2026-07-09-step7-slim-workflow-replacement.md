## Workflow

1. Chunked routing (conditional). A handoff doc/skill invocation with no task
   directive — including a bare `/handoff` call, not only a doc mention
   — fires the chunker before pickup/refresh; it reasons over the live backlog
   (issues unioned with handoff entries via `--with-issues`). See
   `references/chunked-routing.md` for the trigger rule, pipeline, end-only write discipline, and `/achieve` draft.
2. Determine whether this is pickup or refresh.
   - for pickup, treat the workflow trigger as authoritative next-step
     instruction
   - for refresh, inspect only the live state that changes the next action
   - if the current handoff exceeds the size gate or stacks dated
     `This Session` sections, prune or spill before adding new prose
3. Identify the canonical handoff artifact.
   - default to the adapter-resolved artifact path
   - if the repo already has a checked-in handoff surface, point the adapter
     there instead of hardcoding the host choice into the skill
4. Rewrite the handoff around continuation, not history.
   - exact workflow trigger
   - continuation capability the next operator must have after reading
   - current state facts that change the next action
   - ordered next actions
   - open decisions that still need user input
   - tight reference list
   - one reference to the owning artifact for metrics, history, or proof detail
     instead of replaying that detail inline
   - if the handoff carries a standing invariant, recurring workflow rule, or
     future-regression guard, promote it to the owning contract, reference, or
     validator surface and leave only a short pickup pointer
   - leave always-loaded host instruction surfaces out of `References` by
     default; include them only when omitting them would realistically change
     the first action
   - when the next action depends on an external originating context, carry
     canonical source identity (URL, gathered-artifact path, access mode,
     freshness) per `../../shared/references/closeout-discipline.md` so the
     next session does not rediscover the source
5. Keep the trigger explicit.
   - if a named workflow or skill should run next, say it directly
   - if the next pickup depends on reading specific files first, name them
6. Run a bounded misunderstanding critique when the handoff changed materially.
   - call `critique` for material workflow or ownership changes
   - focuses: wrong next action, workflow trigger ambiguity, ownership/boundary
     misread, and examples that could be over-literalized
   - use `../../shared/references/fresh-eye-subagent-review.md` before reporting
     the reviewer path as blocked
   - incorporate only concrete clarity fixes, not speculative churn
7. Finish with a clean baton pass.
   - the next operator should know what to do first without interpretation
   - on a refresh, close with the tokens defined in `## Closeout Vocabulary`


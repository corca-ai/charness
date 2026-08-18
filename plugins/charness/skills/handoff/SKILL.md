---
name: handoff
description: "Use when the user wants the next session prepared or asks to update a handoff artifact. Keep the handoff short, current, and operationally useful, and treat mention-only pickup as an instruction to continue the workflow named in the handoff trigger."
---

# Handoff

Use this when the goal is to let the next operator continue without re-deriving
the session state.

The handoff should describe the exact next pickup path, not preserve a diary of
everything that happened.
Keep Christopher Alexander-style sequence discipline in the baton pass: record
the next move in the order it should unfold, not in the order this session
happened. See `references/continuation-sequence.md` when several plausible
pickups exist.

## Bootstrap

Plan the run first, then read only the artifact, references, and gates named by
the plan.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/plan_handoff_run.py" --repo-root . --intent <chunked_routing|pickup|refresh>
```

By default, `handoff` writes its durable artifact to
`<repo-root>/docs/handoff.md`. Repos can override the directory with
`<repo-root>/.agents/handoff-adapter.yaml`.

You are the one reading the user's request, so you DECLARE the routing —
`--intent chunked_routing` when `references/chunked-routing.md`'s rule holds,
otherwise `--intent pickup` or `--intent refresh`. `--intent auto` only reads
structural signals and will hand the decision back. For a bare direct skill
invocation with no task, `--invoked-directly` declares that shape and routes to
chunked routing.
The planner resolves the adapter, summarizes the artifact, lists
`required_reads`, and names cheap `gate_packets`.
Open the listed reads using each entry's `base` before broader exploration; a
read carrying a `command` is answered by running it BEFORE writing. For an
existing target, run the rules preflight before the target preflight, then apply the semantic
receipt audit in `references/spill-targets.md`.
Treat deterministic gates as evidence for shape and freshness, then use
judgment for the actual baton pass. The repo-owned size budget counts CONTENT
lines — blank lines, the required `##` headings, and the whole `## References`
block are free — with a target of 25-50 and a hard stop the repo owns (78 unless its adapter
sets `max_content_lines`); the planner
reports `content_line_count` and flags `near_limit`/`over_limit`. Trimming formatting
or shortening reference links buys nothing, so cut state instead. Multiple dated
`## This Session (<date>)` sections are a hard diary smell.
Assume a competent next operator can follow one good link. Aim for `## Current
State` and `## Next Session` to read as a list of links, with prose only where no
artifact owns the claim yet. Each entry — and every `## References` line, which is
refused when its whole content is one link — is a link plus one line on the same
physical line saying what that document HOLDS, not what to do about it. The reading agent decides the action; a contents description goes
stale only when that document changes, while a next-action description goes
stale whenever the world does. Order carries the priority, and the section
heading carries the verb. The link target is whatever artifact owns the detail —
a quality artifact, a spec, a convention doc
(`./references/state-selection.md` shows how to choose what survives at all).
Where no artifact owns the claim, carry the command that regenerates it instead,
and where nothing can, spill the detail first (`./references/spill-targets.md`).

The gate enforces the floor under that aim: every list entry in
those two sections must carry an OWNER (a markdown link, an inline command that
regenerates the fact, or an issue id), and the planner reports `unowned_entries`
with line numbers. `## Discuss` is exempt: an open question has no owner yet,
which is what makes it open.
These sections are a FLAT list: every list marker starts its own entry, so a
sub-bullet needs its own owner, and there are no multi-paragraph entries. A fenced block
may sit in the section — a machine-read ledger block often must — but it owns
nothing, so a bullet whose only command is in a code block is refused; that
bullet belongs in the artifact it should be linking. An inline command must take
arguments — a bare path is a link, not a command, and a single-word command is
indistinguishable from an identifier. Fences must close: an unpaired delimiter
makes every later line read as fenced, so both sections become unscannable and
the artifact is refused rather than passed.
The floor is narrower than the aim, and the gap is yours to close, not the
gate's: `## Workflow Trigger` and `## Continuation Capability` are NOT checked,
an entry passes on one owner while paraphrasing a second artifact beside it, and
the link is never followed. Ownership makes a claim checkable; it does not make
it true, and it does not shorten the artifact — only spilling detail to the
owning artifact does that.

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
   - run the receipt/owner classification in `references/spill-targets.md`
   - exact workflow trigger
   - continuation capability the next operator must have after reading
   - current state facts that change the next action
   - ordered next actions
   - open decisions that still need user input
   - tight reference list
   - one reference to the owning artifact for metrics, history, or proof detail
     instead of replaying that detail inline
   - put any prerequisite before the next slice it governs; a `Discuss` item
     about automating that prerequisite later does not replace the ordered
     `Next Session` action needed now
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
   - read `../../shared/references/fresh-eye-subagent-review.md` BEFORE spawning,
     not only before reporting the reviewer path as blocked: it owns the spawn
     shape, and a wrongly-shaped spawn succeeds while its findings never arrive
   - incorporate only concrete clarity fixes, not speculative churn
7. Finish with a clean baton pass.
   - the next operator should know what to do first without interpretation
   - on a refresh, close with the `## Closeout Vocabulary` tokens: `Refresh kept:`
     naming the state retained because it changes the next action, and
     `Refresh non-claims:` naming what was dropped as non-actionable, spilled to an
     owning artifact, or not proven (or `Refresh non-claims: none`)

## Output Shape

The handoff should usually contain:

- `Workflow Trigger`
- `Continuation Capability`
- `Current State`
- `Next Session`
- `Discuss`
- `References`

## Closeout Vocabulary

Emittable-verbatim refresh closeout tokens (the claim-fidelity floor
substring-matches these); the compression and spill WHY-prose stays in
`references/state-selection.md` and `references/spill-targets.md`.

- `Refresh kept:` — the state retained because removing it would change the next
  operator's first action (the state-selection Compression Rule outcome).
- `Refresh non-claims:` — what was dropped as non-actionable, spilled to an owning
  artifact, or left unproven; or `Refresh non-claims: none`.

## Guardrails

- On a session-open pickup — including one routed here by the SessionStart hook
  or the handoff Workflow Trigger after a
  bare handoff-doc mention — invoke the workflow named in the `Workflow Trigger`
  instead of only re-reading the handoff; mention-only reading is the
  recurring routing miss this contract guards against.
- Do not write unverified state as fact.
- Do not leave a `## Current State` or `## Next Session` entry without a link,
  command, or issue id; spill the detail to its owning artifact and link that.
- Handoff is a continuation pointer, not a diary: keep only what changes the next
  action and honor the size gate as a failure guard, not a target. The keep/drop,
  stale-detail, and dated-`This Session` rules live in
  `references/continuation-sequence.md` and `references/state-selection.md`.
- Single-source detail to the owning artifact (Workflow step 4): never replay
  quality/retro/debug/changelog/release detail or promote a recurring capability
  invariant inline, and leave host instruction surfaces out of `References` when
  the host already injects them automatically (`references/spill-targets.md`).

## References

- `references/adapter-contract.md`
- `references/chunked-routing.md`
- `references/continuation-sequence.md`
- `references/workflow-trigger.md`
- `references/state-selection.md`
- `references/spill-targets.md`
- `../../shared/references/closeout-discipline.md`
- `../../shared/references/fresh-eye-subagent-review.md`

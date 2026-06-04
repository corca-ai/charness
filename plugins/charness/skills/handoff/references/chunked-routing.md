# Chunked Routing

Conditional workflow phase that absorbs the recurring manual cost of
reading `<repo-root>/docs/handoff.md`, identifying
which residual tasks unblock which, picking an advantageous order, and
shaping a `/goal @file` activation skeleton.

The chunker is an **additive phase** of `handoff`. It does not replace
state selection, spill targets, or continuation sequence; those still
own refresh and pickup once the chunker either fires + completes or
declines to fire.

This reference owns the operator-facing surface. In the charness source
repo the full implementation contract lives at
`docs/handoff-chunked-routing.md` (authoring-repo-internal; not vendored
with the skill).

## Deterministic Trigger Rule

The chunker fires iff there is **no explicit task directive** AND a
**handoff signal** is present — for the current user invocation (the most
recent user-authored message before the agent acts):

1. **No explicit task directive.** The invocation contains none of:
   - an imperative verb naming a concrete next action paired with a noun
     other than the handoff itself (`do <X>`, `fix <X>`, `implement <X>`,
     `close <X>`, `push <X>`, `run <X>`, `start <X>`, `work on <X>`,
     `resolve <X>`, `merge <X>`, `release <X>`, `revert <X>`)
   - an explicit issue id pattern `#\d+`
   - a file path other than the handoff itself
   - a slash command other than `/handoff`
   - a `--<flag>` token

   A task directive **always bypasses** — even a direct skill invocation that
   carries one (`/handoff fix #233` does not fire).
2. **Handoff signal**, at least one of:
   - literal token `docs/handoff.md`, `handoff.md`, or `/handoff`
   - phrase `handoff skill`, `handoff 스킬`, or `charness:handoff`
   - imperative referencing the handoff surface without naming a task:
     `read the handoff`, `check the handoff`, `read handoff`,
     `what's in the handoff`, `next from handoff`, `pick up from handoff`,
     `핸드오프 봐`
   - **direct skill invocation** (`invoked_directly`): the handoff skill was
     launched with no task — a bare `/handoff` / `charness:handoff` call.
     Invoking the skill is itself enough; no doc mention is required. This is
     the #249 trigger-widening path, so a pickup reasons over the backlog even
     when the operator did not type a handoff filename.

When both hold the chunker fires. When the task-directive check fails (the
user named a specific next task), the chunker steps aside and the rest of the
handoff workflow runs as usual.

The trigger fixture (in the charness source repo at
`tests/test_handoff_chunker_trigger.py`; authoring-repo-internal, not
vendored with the skill) is the source of truth; any divergence between this
prose and that fixture is the prose's bug.

## Pipeline

The chunker runs as a six-step pipeline. Steps 1, 2, 3, 5, 6 are scripts;
step 4 is the active agent.

1. **Parse (+ live backlog).** Run
   [`parse_handoff_entries.py`](../scripts/parse_handoff_entries.py)
   against the resolved handoff artifact. Each numbered entry in
   `## Next Session` becomes a `HandoffEntry` record with title, body,
   referenced paths/issues/skills, and a non-trivial-filtered
   `boundary_tokens` set, except non-actionable pickup checks are filtered
   before ranking. Local-state preflight entries such as `git status`/`git log`
   checks are operator setup, not user-selectable chunks; goal activation
   entries pointing at a `Status: active` or `Status: complete` goal artifact are stale and are
   also dropped; `during`/`while` cadence or invariant entries shape the chosen
   chunk instead of becoming standalone candidates. Pass `--with-issues` (the pickup default; #249)
   to also union the live open-issue backlog: each open issue becomes a
   `HandoffEntry` (boundary tokens from its **title + specific labels**, not
   its body — body paths over-cluster), routed through the `issue` skill
   backend seam (no hardcoded provider literal; trackerless hosts fall back
   to doc-only), gated behind the handoff adapter's optional `issue_source:`
   block. An issue a handoff entry already cites (`#NNN`) is **merged into
   that entry**, not double-counted, so the chunker surfaces the open issues
   the hand-written `## Next Session` omitted without duplicating the ones it
   names.
2. **Prepare deterministic hints.** Pipe the parsed entries to
   [`propose_merges.py`](../scripts/propose_merges.py). The proposer
   computes pairwise `boundary_tokens` overlap and emits a
   `MergeProposal` whose `standalone` list always carries one
   `ChunkCandidate` per entry; the `merged` list is additive (zero or
   more multi-entry candidates per shared-boundary cluster). These are
   overlap hints, not the final user-facing package list.
3. **Propose work packages.** Run
   [`prepare_chunk_packet.py`](../scripts/prepare_chunk_packet.py)
   against the parsed entries. The packet carries source IDs, overlap hints,
   adapter chunk policy, prompt, and schema. The active agent fills `chunks`
   with coherent work packages: included source IDs, excluded nearby IDs when
   relevant, objective, rationale, downstream unlock, and basis boundary tokens
   when tokens justify a merge. The parent validates the response with
   `chunked_routing_lib.validate_chunk_proposal_response`, then materializes it
   with `materialize_chunk_proposal_response`. Validation rejects unknown,
   duplicated, missing, or over-large source groups, empty rationale, and
   broad-label-only merges unless adapter policy explicitly allows that label.
4. **Rank.** Run
   [`prepare_ranker_packet.py`](../scripts/prepare_ranker_packet.py)
   against the materialized package proposal. The script emits a self-contained JSON
   packet (version + merge proposal + canonical Christopher Alexander
   generative-sequence prompt + response schema). The active agent
   fills the `ranked_chunks` array (one entry per candidate with
   `candidate_label`, `rank`, and 2–3 sentences of `reasoning`
   naming what each chunk unlocks downstream). The parent then runs
   `chunked_routing_lib.validate_ranker_response` on the filled
   payload; a structural failure (missing label, duplicate rank,
   empty reasoning, etc.) refuses materialization.
5. **Present.** Render the ranked list inline in the conversation:
   one chunk per line with rank, label, objective summary, and the
   pre-computed reasoning. Merged candidates carry a
   `(package: <rationale>)` marker so the user sees the basis
   for the bundle proposal. Ask the user to pick a chunk (or to
   decline). A follow-up question like "why not chunk N?" must be
   answered from the already-rendered reasoning — do not re-invoke
   the ranker.
6. **Draft.** On selection, pipe the chosen `ChunkCandidate` JSON to
   [`draft_goal_from_chunk.py`](../scripts/draft_goal_from_chunk.py).
   The drafter writes a goal artifact at
   `<repo-root>/charness-artifacts/goals/<yyyy-mm-dd-slug>.md` at
   status `draft`, seeds Goal / Non-Goals / Boundaries / Context
   Sources, and leaves User Acceptance / Agent Verification Plan /
   Slice Plan (header rows only) / Interview Decisions / Plan
   Critique Findings as placeholder lines for the achieve
   Before-phase to fill. The drafter validates the result with
   `check_goal_artifact.check_goal` in-process; an artifact that
   fails the gate is rolled back. On success the draft is still
   **unshaped** (User Acceptance / Agent Verification Plan / Slice
   Plan are placeholders), so the next move is to **shape** it through
   the achieve Before-phase: surface the drafter's `next_step` /
   `shape_command` (`/achieve @<artifact>`), not `/goal @<artifact>`.
   `/goal` is the artifact's `activation` line and starts the During
   run only after shaping has filled the placeholders (#246).

## Override UX

The presented ranking is a proposal, not a directive. The user can:

- accept a chunk and proceed to step 5
- decline all proposals and route to `handoff`'s normal pickup or
  refresh flow
- ask "why not chunk N?" — the agent answers from the rendered
  `reasoning` for chunk N (or the comparison reasoning between two
  chunks), without re-running the ranker
- accept or reject each merge proposal independently — the user is
  not bound to take the bundle just because the proposer found a
  shared boundary; the corresponding standalone candidates are
  always present in the same list

## End-Only Write Discipline

The chunker runs at **pickup** and writes exactly one durable artifact: the
derived goal skeleton (step 5, a forward artifact). It must **never** rewrite
`handoff.md` at pickup. The baton is written at **closeout** only — a
pickup-time rewrite is churn because the session's own work moves the state
again. A stale `## Next Session` item discovered at pickup (already done, or
now superseded by the live backlog) is carried in the conversation and folded
into the single closeout write. The owning rule, in the charness source repo, is
`docs/conventions/operating-contract.md` (Session Discipline;
authoring-repo-internal, not vendored with the skill); `## Next Session`
is a curation/sequencing memo, not a synced task queue.

## Standalone Usefulness

The chunker is one conditional phase, not a replacement. The trigger
gate above guarantees that:

- `handoff` without the chunker still works exactly as today. Any
  invocation with an explicit task directive bypasses the chunker;
  state selection, spill targets, and continuation sequence run as
  normal.
- `/achieve` without a chunker-drafted skeleton still works. The
  auto-drafted artifact conforms to the achieve goal-artifact gate
  (`../../achieve/scripts/check_goal_artifact.py`, skill-relative)
  exactly as a hand-shaped artifact would; a Before-phase interview
  on an auto-drafted skeleton is indistinguishable from one on a
  hand-shaped goal.

# Resolution Critique — issue #385: boundary matrix before `achieve` marks a goal blocked

- Date: 2026-06-18
- Target reference: `code-critique` (recurrence focus)
- Issue: corca-ai/charness#385
- Fix unit: pre-block remaining-boundary-matrix floor in `achieve`
- Framing question: what would let this class of issue, and the step-4 siblings, come back?

## Execution

- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: n/a (no adapter sections)
- Reviewers: 3 angle subagents (Weinberg diagnostic, Jackson problem-framing,
  Gawande operational) + 1 separate counterweight, each a bounded fresh-eye
  subagent over the staged diff. Prior context = the step-4 causal-review block
  (so reviewers did not redo root cause).

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority` (adapter `.agents/critique-adapter.yaml` Codex-host mapping; this Claude Code run spawned each bounded reviewer with `model=opus` via the Agent tool; reasoning_effort/service_tier are not exposed through the Agent spawn interface)
- **Host exposure state**: `requested_fields_sent`
- **Application state**: `unverified-by-host` (the host does not confirm applied spawn fields back to the parent; sent fields are not proof of application)
- **Instruction**: Review artifacts record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed.

## Diff Scope

A deterministic pre-block floor: before `achieve` flips a goal to `blocked`,
`upsert_goal.py` (via new `skills/public/achieve/scripts/goal_artifact_blocked_matrix.py`)
refuses unless a `## Remaining Boundary Matrix` classifies every external/live
proof lane AND no lane is self-classified runnable
(`runnable`/`preauthorized-runnable`/`approved`). `check_goal_artifact.py`
re-surfaces it post-flip. Prose in lifecycle.md / goal-artifact.md / SKILL.md.
Tests in `tests/quality_gates/test_goal_artifact_blocked_matrix.py`.

## Prior context (causal review, step 4)

Root cause: the `blocked` flip used bare `set_status` with no evidence gate
while `complete` had a full one (`goal_artifact_lib.py`). Mistaken mental model:
"one blocked lane ⇒ whole unit blocked." Step-4 siblings: Operator Decision
Queue rule ("stop only when the decision blocks ALL safe next slices") = correct
inverse pattern, reused; timebox candidate ledger = precedent; closeout-state
taxonomy = defer ("blocked-state taxonomy").

## Findings (collapsed across angles)

- All three angles independently confirmed the fix is at the **right layer** and
  the `no-runnable-contradiction` clause is the real teeth (reproduced by
  `test_check_runnable_lane_blocks` / `test_upsert_refuses_blocked_with_runnable_lane`),
  not merely "a matrix exists".
- **Creation-path bypass** (all 3 angles, cheap-bundle): `upsert_goal --status
  blocked` on a *new* goal skipped the floor (only the `path.exists()` flip
  branch was gated); the post-flip checker re-surfaced it, but the deterministic
  refusal was skippable at birth.
- Residual gameability (mislabel a runnable lane as `blocked`/`approval-required`)
  is **honestly disclaimed** in the module docstring and prose as rung-2 /
  human territory — not over-claimed.
- `approved`-as-runnable is the least-obvious token and a future editor could
  mis-bin it.
- Purely-local blockers (no external lanes) are still forced to author a matrix.

## Counterweight Triage (four bins)

### Act Before Ship → Bundled into this commit

- **Creation-path bypass.** Gate the create branch in `upsert_goal`: a requested
  `status == "blocked"` re-runs `flip_refusal` on the rendered body and refuses
  (status `missing`) when unclean. New test
  `test_upsert_refuses_create_straight_to_blocked`. Closes the only path to
  `blocked`-on-disk without a matrix that did not require the post-flip checker.

### Bundle Anyway → Bundled

- One-line WHY comment for `approved`-as-runnable beside `RUNNABLE_TOKENS`.
- One clarifying sentence in `lifecycle.md`: a purely-local blocker records the
  matrix with a single `classification: blocked` self-lane, so even a local stop
  names what it stops on (removes the "what do I write?" friction).

### Over-Worry → Rejected (not surfaced in close comment)

- "Floor is gameable by mislabeling a runnable lane." The floor never claimed to
  detect dishonest self-classification; the docstring/prose assign that to the
  fresh-eye reviewer and human (rung-2). Demanding the floor catch it is
  speculative-adversary scope creep.
- "Should be advisory, not blocking." #385 proves prose already existed and did
  not prevent the false handoff; a recorded recurrence with a deterministic
  mechanical signal is exactly when a blocking floor is justified. Recorded via
  the `# floor-addition-restraint: keep` call.

### Valid but Defer → Recorded in the close comment

- A formal **"blocked-state taxonomy"** mirroring the closeout-state taxonomy
  (the step-4 abstraction-up sibling). No #385 evidence demands it now; bundling
  it would expand blast radius into the closeout-taxonomy contract.
- Revisit purely-local-blocker matrix ergonomics only with real dogfood churn
  evidence.

## Defect Class Cross-Link

Repeat-trap class: workflow-boundary propagation (a producer decision
over-generalized to the final consumer). Same family as prior achieve closeout
gates that separate "process ran" (deterministic floor) from "substance is
right" (rung-2 reviewer/human).

## Deliberately Not Doing

- Not turning the floor into a content classifier of whether a lane is "truly"
  runnable — that re-imports the word-list over-fire trap the repo forbids.
- Not building the blocked-state taxonomy now (deferred above).

## Next Move

Bundle fixes applied; re-verify (focused pytest + structural sweep), record the
public-skill scenario review in the dogfood registry, then commit with
`Close #385`, the closeout ledger, and this critique path; verify CLOSED.

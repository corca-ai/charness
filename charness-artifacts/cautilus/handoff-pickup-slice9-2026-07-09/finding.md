# handoff pickup RCF→substance MOVE — workflow-trigger.md (#410 Slice 9)

## What ran

**2026-07-09, ask-before-run capture, operator-authorized** (operator instruction:
proceed with the entire remaining #410 queue; `justification.md`). Skill change
under test committed at `e4f3626d`; captured via `capture-skill-run.sh --ref HEAD`
on an isolated worktree with the exact `pickup.spec.json` prompt.

## The MOVE

`workflow-trigger.md` retired from the pickup doc-open floors:

- `plan_handoff_run.py` no longer forces `references/workflow-trigger.md` for the
  pickup intent (census INLINE — the trigger-first gist is inlined in SKILL.md
  steps 2/5 and the session-open guardrail; the live trigger TEXT is the
  artifact's `## Workflow Trigger`, still the planner's first forced read). It
  stays forced for `judge_from_user_request` (intent-deciding, load-bearing).
- `pickup.spec.json`: RCF `[workflow-trigger.md]` → `[]`; the floor is now the
  sibling `outcome-assertions.json` SUBSTANCE judge (valid per claim_fidelity_lib
  substance-floor-only support, `325909f7`).
- `pickup-ambiguous.spec.json`: RCF → `[continuation-sequence.md]` — strictly
  weaker; its retained ref was genuinely opened in the proven 2026-07-02 capture
  and the planner still forces it under the ambiguous condition (unchanged code
  path), so the clean-MOVE rule applies at zero new capture cost.

Why substance instead of an RSF token: the prior deferral was real — a faithful
pickup hands off to the invoked workflow, so no closeout token owned by handoff is
stable in the final text. The judge reads the TRANSCRIPT, so it grades the
handoff-owned behavior (trigger consulted from the artifact, live state verified,
workflow started or a repo-owned boundary explicitly named) regardless of which
workflow owns the final message.

## Outcome — verification (all from the captured stream, observed not assumed)

- **Grade vs flipped spec: `passed`.** 1,023,712 total tokens, 133,770 ms wall,
  10 tool calls, zero waste smells.
- **Compaction achieved.** `Read(workflow-trigger.md) = 0` — the pickup consulted
  the artifact's `## Workflow Trigger` (docs/handoff.md Read) and never opened the
  retired reference. Coverage 0/5 DEPTH refs (workflow-trigger.md excluded as
  INLINE).
- **Old spec FAILED the same faithful run** (`observed.old-spec.v1.json`:
  `command log missing required fragment: workflow-trigger.md`) — post-planner-
  change, the doc-open RCF is a false floor that fails honest pickups; the
  cleanest counter-evidence shape (same class as setup slice2b).
- **Substance judge: 4/4, pass_rate 1.0** (`outcome-grade.md`, live
  `outcome_judge_cmd.py`). The run verified live state through non-handoff
  channels (gh reads of #421, `plan_cautilus_proof.py`), honored the
  self-referential trigger by executing the `## Next Session` queue, and stopped
  exactly at the repo's ask-before-run Cautilus boundary while naming it.
- **Falsifiability probe (evidence: `falsifiability-probe.json`):** a synthetic
  mention-only pickup context (read the handoff, summarize, no live checks, no
  named boundary) was judged `fail` by the same judge + assertion — the guarded
  routing miss stays red under the new floor. (The probe's first run was
  transcript-only; the fresh-eye reviewer flagged the bundle gap and the probe
  was re-executed with its input+verdict saved as the bundle artifact.)

## Honest instrument iteration (recorded, not hidden)

The FIRST judge pass scored 2/4 (0.333): one assertion let the judge demand
refresh-only `Refresh kept:` tokens from a pickup run (authoring scope defect),
and one read the run's contract-faithful stop at the ask-before-run boundary as
"never started" (the live fixture's pinned task is itself ask-gated, and the live
trigger is self-referential). Both statements were re-scoped to grade per-intent
behavior and to accept a stop that explicitly names a repo-owned boundary —
while keeping the mention-only failure mode red (verified by the probe above).
This is capture-before-pin doing its job on the instrument itself; the
deterministic matcher was never softened.

## Non-Claims

- A pinned-task scenario whose safe next action is startable in-fixture would
  exercise the "actually STARTED it" arm live (the current live-handoff fixture
  gates it); scenario candidate, not a floor gap — the boundary-naming arm is
  proven and the mention-only arm is red.
- The substance floor is advisory by design; the deterministic RCF/RSF floor for
  the clear pickup arm is intentionally empty per substance-floor-only support.

Raw capture (worktree/config/stream/credentials) scrubbed — not committed.

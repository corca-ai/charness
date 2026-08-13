# Handoff / Retro Feedback-Loop Capability Brief

## Capability

Improve the existing public `handoff` and `retro` skills so their declared
contracts are exercised at the moment they matter:

- before editing a handoff, inspect the current target for copied receipt
  detail and route that detail to an owning artifact;
- during a retro, read adapter-declared local evidence and operate a repo-owned
  lesson evaluator only when its selected lessons were actually presented
  before the observed work.

This is an **improve** slice for two existing public skills. It does not create a
new skill or a new lesson-score policy.

## Audience And Trigger

- Handoff authors refreshing a continuation artifact after a meaningful slice.
- Retro authors closing a session in a repo that declares additional evidence
  or a local lesson-selection/scoring mechanism through its adapter.
- Triggering evidence in this repo:
  - `docs/handoff.md` passed its shape gate while carrying duplicated release,
    commit, and test receipts instead of mostly owning links.
  - the lesson ledger had only two declared sessions and three score events,
    all from its initial implementation day; later sessions did not operate it.

## Capability Failures

### Handoff

The core already prefers links and says to spill proof detail, but the planner
only put the rule-only authoring preflight in `required_reads`. The
target-specific preflight remained a post-edit gate packet. A compliant run
could therefore learn the abstract rule before writing yet miss that the
current artifact already contained copied receipts until after the rewrite.

### Retro

The core tells the agent to read adapter-defined `evidence_paths`, but
`plan_retro_run.py` does not include those paths in `required_reads`. This repo's
adapter also did not declare the lesson-ledger state or its local authoring
procedure. The scoring mechanism consequently depended on the user reminding
the agent that it existed.

## Portable Contract

### Handoff

- For a planner action that authors an existing handoff, emit both:
  - the surface-rule preflight; and
  - a target-specific preflight against the current handoff.
- Run both before editing. The target preflight deterministically catches only
  its declared markdown/link/length and regenerable-literal classes (for
  handoff, version/SHA/count literals); it does not detect every semantic proof
  receipt. Follow it with an agent-owned entry audit that classifies each
  Current State / Next Session item as an owning link, regenerating command, or
  copied receipt, and spills the last class to its owner.
- Put prerequisites in `Next Session` before the slice they govern. A `Discuss`
  item about future automation does not substitute for the immediate ordered
  action.

### Retro

- Promote adapter `evidence_paths` into planner `required_reads`, preserving
  declared order and disclosing file/directory/missing status. Missing optional
  evidence does not block an ordinary retro.
- When those repo-owned sources expose a declared-session lesson evaluator,
  score only sparse, anchored effects for lessons that were both selected and
  actually presented before the relevant work.
- A stored selection snapshot proves containment/declaration, not presentation.
- If presentation did not happen, append no score and state `Lesson evaluation:
  not evaluated — presentation not established for <session-id>; no score
  events appended` in the retro artifact. Put the missing start-of-session
  action into the handoff. Never backfill scores from a later retro.
- Presentation is a contemporaneous agent-authored session-start action that
  shows the selected list before affected work. Retro-time inspection of a
  snapshot is not presentation; uncertainty resolves to `not evaluated`.
- Repos without such evidence continue using the ordinary portable retro; no
  lesson evaluator is inferred or required.

## Repo-Local Seam

The public core remains generic. Charness declares these existing local sources
through `.agents/retro-adapter.yaml`:

- `charness-artifacts/retro/lesson-ledger.json` for declared sessions and score
  events;
- `docs/development.md` for the local authoring commands and proof non-claims.

The public skill does not hardcode Charness commands, ledger schema, score
weights, or digest policy.

For this repo, the handoff carries the start-of-session prerequisite and links
the authoring procedure. That is the first-touch mechanism for the next slice;
the retro repairs a missed prerequisite into the next handoff instead of
inventing a delivery receipt in the ledger. A new typed adapter schema is
deferred until more than one repo-local evaluator demonstrates that generic
evidence discovery is insufficient.

## Topology

- Canonical sources: `skills/public/handoff/` and `skills/public/retro/`.
- Repo adapter: `.agents/retro-adapter.yaml`.
- Generated export: corresponding paths under `plugins/charness/`, synchronized
  only after canonical edits.

## Prompt Simulation

- Cold start, no adapter evidence: retro behaves as today and makes no scoring
  claim.
- Warm handoff refresh: target preflight exposes copied receipts before the
  author rewrites; final handoff links to owners and preserves only
  next-action-changing state.
- Warm evaluated retro: planner names ledger state and local procedure; the
  agent records only evidence-backed scores for the previously presented list.
- Error case, snapshot exists but was not shown: no score is appended; the
  retro states `not evaluated`, and the next handoff schedules declaration plus
  presentation before the next work slice.

## Proof Plan

- Planner unit tests pin the two handoff authoring preflights and their ordering
  before editing.
- Planner unit tests pin adapter evidence as required retro reads, file /
  directory / missing disclosures, and behavior for empty evidence lists.
- Skill contract tests pin the presentation/non-backfill language and the
  handoff prerequisite-ordering rule.
- Canonical/plugin source parity is checked after export sync.
- Exercise the two existing public-skill dogfood prompts against the new
  first-touch behavior. Inspect the maintained Cautilus mappings for changed
  coverage, but Cautilus remains ask-before-run and is not claimed.

## Non-Goals

- No lesson score-policy tuning or comparison verdict.
- No claim that a ledger snapshot proves a lesson was displayed.
- No hosted/runtime telemetry or hidden machine-write location.
- No change to handoff size limits or ownership-validator verdict logic.

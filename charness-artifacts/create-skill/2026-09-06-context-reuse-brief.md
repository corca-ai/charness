# Context reuse capability brief

Date: 2026-09-06

## Contract

Improve existing public `spec`, `debug`, and `retro` skills for an agent carrying
a long delegated task. The failure is repeated context discovery or fixed-form
work after the information needed for the next action is already current.
Keep one canonical implementation per skill; generated host-facing placements
are exports, not forks. The valid create-skill adapter supplies this topology.
No new dependency, host vocabulary, mode, cache, or progress artifact is added.

Current consumer contracts were read from `docs/public-skill-dogfood.json` via
the skill's suggestion helper: spec produces a living contract from repo truth;
debug diagnoses before code and preserves the record; retro makes a reviewed
lesson and persists when the task needs durable learning. This slice claims
`improve` for redundant operations, `preserve` for those capabilities. The
approved living contract is the Goal #805 `context-reuse` WorkItem.

## Proposed smallest transformation

- Spec reuses already-read current instructions, contract, and acceptance
  context. Inspect relevant deltas and unresolved questions; discover owners
  when context is missing. Risk/provider truth remains current. Broad search
  examples are discovery tools, not commands repeated on every transition.
- Debug may reuse a subject-matched current planner/artifact contract when its
  inputs and next action remain known. New subjects, changed adapter/output
  contracts, or missing context take the existing planner/scaffold path. Keep
  the emitted validator, durable record, falsifiable hypothesis, reproduction,
  causal review, and recurrence routing. Replace three invented candidate causes
  with the plausible alternatives the uncertainty warrants; test alternatives
  before commitment when cause is uncertain or competing evidence remains.
- Retro chooses chat or persistence from the request and evidence obligation
  before scaffolding. A short chat-only reflection uses current evidence and a
  direct counterfactual without adapter/planner/scaffold or an irrelevant lens
  catalog read. Durable, metrics-dependent, recurring, or follow-up-bearing work
  takes the existing owned path; an explicit chat-only request is respected and
  unperformed durable obligations are stated, not silently declared complete.

Each skill owns selection in core; references only deepen the selected move.
Inspect direct bootstrap/reference/test consumers to avoid contradictory rules.
Remove prose-pinning assertions only where they do not guard a parsed boundary.
Preserve frontmatter/schema/validator checks and negative boundary fixtures.

## First-reader acceptance scenarios

1. Warm spec: consumer has current contract and same checked inputs, asks to
   refine one remaining acceptance question. Reach that question without a broad
   repository discovery/planner loop. Cold/missing context must find the owner;
   a changed contract must be read and reconciled before a stale edit.
2. Debug: a small regression has one directly testable cause, and a second case
   has two plausible competing causes. The first need not invent a quota; the
   second must test a disconfirming alternative. New and recurring subjects
   retain distinct records/handoff and do not overwrite unrelated incidents.
3. Retro: “Give me a short chat-only retro on this local edit; don't write files.”
   Reflect with a concrete counterfactual and truthful non-persistence. Contrast
   “Persist the repeat trap this workflow should have caught”: use the durable
   owner, retain sibling/follow-up obligations, and validate the artifact.

Use missing, stale, thin, and valid adapter states where they affect each
choice. First-reader proof must use checked/exported SKILL.md and its reachable
resources, realistic prompts, and observed actions/artifacts; author-side prose
matches are not proof. The frozen downstream four-arm protocol separately
tests long-task context reuse and does not claim to cover all debug/retro cases.

## Review and cost boundary

Before editing bootstrap/default behavior, a bounded customer review tests the
first prompts, adapter fallbacks, overstated success, and hidden proof losses.
A distinct simplification lens checks whether replacement selection costs more
than the removed work. Parent dispositions own design acceptance. After edits,
focused contract checks plus an independent forward consumer scenario establish
local readiness; the candidate pilot and shipped observer supply final evidence.
Report removed calls and replacement instructions/reads honestly. No timing or
general reliability improvement is claimed before observation.

## Review dispositions and concrete fixtures

Customer-01 is accepted as a packet-completeness gap, not a demand for execution
before design. Follow-up input includes the actual dogfood registry, debug/retro
adapter contracts, and the direct lens/trigger consumers. Cost findings F1–F4
are accepted as required bounded edits, with the following fixed precedence.

An explicit chat-only/no-write request suppresses **all** writes: adapter,
artifact, summary, lesson score/seeding, and RCA ledger. Automatic triggering
selects reflection, not persistence; merely having an output directory does
not select durable work. Keep state-before-triggered when actually consuming
the probe. A no-write reflection may identify recurrence and follow-up owners,
but names the outstanding obligations and leaves durable completion open.

Every retro needs at least one concrete counterfactual that changes an action.
A name or second lens is optional only for distinct insight. Scope planner and
catalog instructions to the selected owned path; reconcile `expert-lens.md`,
`section-guide.md`, and emitted planner next-action/barrier text. Current,
already-read governing-standard context may satisfy alignment; missing or
changed context requires the targeted read. Parsed artifact sections remain.

Debug reuse applies only to the same **open** investigation with known emitted
target, subject, evidence mode, output contract, and validator. Reconcile pointer,
resolution, and repo-wide risk deltas; subject equality alone proves none of
these. New/resolved/mismatched/unknown/contract-changed cases use the planner's
subject/evidence-preserving emitted command. This also governs Reported-Finding
Mode. Keep cross-subject interrupts. Replace both the workflow's numeric quota
and guardrails' plural-only rule; one cause still requires a falsifier.

Concrete adapter states for the bounded scenarios:

- missing: no `.agents/debug-adapter.yaml` or `.agents/retro-adapter.yaml`;
  debug uses its documented default via planner, durable retro initializes its
  owner, chat-only retro neither creates nor repairs an adapter;
- thin: valid version 1, repo `consumer`, language `en`, owned relative output
  directory, no optional fields; absent options retain existing defaults, and
  explicit empty/null fields keep the adapter's documented meaning;
- stale: previously read adapter points to `notes/old`, current bytes point to
  `notes/current`, or a debug pointer is now resolved/another subject;
  refresh the affected owner before writes and preserve the old record;
- invalid: retro output escapes the repo or debug budget has an invalid type;
  durable path repairs/refuses through its owner, but chat-only reflection
  ignores irrelevant invalid configuration without writing;
- valid/current: the same known owner and open subject remain applicable;
  warm continuation removes rediscovery, not current evidence reads.

Spec is adapter-free: test missing/current/stale contract context, not an
invented spec adapter. Also test unchanged local files but contradictory live
provider state: the next action must change after required provider readback.
For debug, include same-subject transition to evidence-led mode and an unrelated
open incident with cross-subject interrupt. For retro, cross explicit no-write
with a recurring lesson: reflect, identify the unperformed durable follow-up,
and leave that claim open. These intersection cases refine the numbered first
prompts above. Observable proof is the next action, read/write trace and artifact
result, not matching replacement prose. No new eligibility certificate is built.

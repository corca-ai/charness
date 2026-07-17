# Spec — CLI Output Affordance Contract

Date: 2026-07-17 (slice 2 — convergence — added same day after operator
approval; slice 1 shipped in `24e4919e` and stays recorded below)

## Problem

A HATEOAS-lens review of the CLI output surfaces found that the harness already
treats "state output carries the next action" as a design value
(`docs/control-plane.md` next-action summary, `run_plan_envelope.py` mandatory
`next_action.kind`, north-star P5 "a gate may force a question, not declare
completion") but applies it inconsistently:

1. **Failure payloads are dead ends.** `task_failure` rejections emit
   `{event: rejected, status, reason}` with no pointer to the recovering
   command, while every task success path carries `next_step`. The blocked
   caller — the one who most needs an affordance — gets none.
2. **The affordance is not persisted.** `next_step` is appended to the CLI
   response after `write_task()`, so `.charness/tasks/<id>.json` never carries
   it. The task envelope's stated purpose is "the next actor continues without
   re-deriving state", and the next actor usually reads the file, not the
   original stdout.
3. **The convention is out-of-band knowledge.** `docs/generated/cli-reference.md`
   documents every flag but never says that payloads carry `next_step` /
   `next_action` affordances or what shape each has.
4. **Field naming/shape drift.** Four names (`next_step`, `next_steps`,
   `next_action`, `guidance`) and three types for `next_action` (doctor dict,
   worktree plain string, skill-envelope `{kind, ...}` dict) across ~40 files.

## Capability Contract

Actor: any agent (or operator) consuming `charness` CLI output or reading
persisted `.charness/tasks/*.json` state. Capability delta: a blocked or
resuming actor can find the next recovering/continuing command inside the
payload or state file itself, without out-of-band knowledge. Acceptance
boundary: the `charness task` YAML payloads, the persisted task state files,
and the generated CLI reference header.

## Current Slice (2 — Convergence, Operator-Approved, Breaking Allowed)

1. **String `next_action` → `next_step`.** The worktree libs (doctor, prepare,
   create, cleanup, audit payloads and the `CheckResult` field) and the
   `charness tool` aggregate attention response rename their plain-string
   `next_action` to `next_step`. No compatibility alias.
2. **`next_steps` split.** The runtime doctor/update/init host-keyed map
   (`{codex: msg, claude: msg, repo: msg}`) renames to `host_next_steps`;
   plural `next_steps` now always means a **list of human-readable follow-up
   strings** (tool doctor, `capability init`, gather advise keep the name and
   are now convention-conformant).
3. **Prefix unification.** The human affordance line prefix on `charness` CLI
   summaries is `NEXT:`: worktree text renderers change `next:` → `NEXT:`, the
   runtime doctor human block header changes `NEXT_ACTION:` → `NEXT:`, the
   version summary `NEXT:` is already conformant, and the repo closeout helper
   `suggest_mutation_coverage_command.py` (which shipped `next:` lines) joins.
   Quality-plane advisory scripts that print their own `Next action:` prose
   are outside the CLI output boundary and unchanged.
4. Documentation converges with the code: the generated CLI reference header
   convention text, `specs/tool-doctor.spec.md` (executable), and
   `skills/public/create-cli/references/command-surface.md` name the new
   vocabulary; the `plugins/` mirror re-syncs.
5. Tests: all assertions on the old names/prefixes move to the new ones; the
   executable tool-doctor spec asserts `host_next_steps`.

## Shipped Slice 1 (2026-07-17, `24e4919e`)

1. `task_failure` gained a per-status `next_step` affordance string naming the
   recovering command; success paths persist `next_step` into
   `.charness/tasks/<id>.json` before `write_task()`; the CLI reference header
   and `docs/agent-task-envelope.md` document the convention; tests cover the
   rejection, persistence, and status surfaces.

## Fixed Decisions

- Canonical vocabulary after convergence (CLI output boundary):
  - `next_step`: single human-readable affordance **string** on command
    payloads (task, tool, worktree surfaces; success and failure alike).
  - `next_steps`: **list** of human-readable follow-up strings.
  - `host_next_steps`: host-id → message map on runtime doctor/update/init.
  - `next_action`: **structured object** for machine routing (runtime doctor
    `{kind, message, ...}`, skill plan envelopes `{kind, ...}`).
  - Human print prefix for affordance lines: `NEXT:`.
- Breaking is approved (operator, 2026-07-17 chat): consumers of the old
  names/prefixes may break; no alias. Published payload shapes change, so the
  release ships under a major bump.
- Task state schema stays `schema_version: 1`; `next_step` is additive and
  optional on read.
- Rejection payloads keep exit code 1 and the existing `event: rejected` shape.

## Probe Questions

- None blocking. Whether other failure surfaces (catalog refresh errors,
  `CharnessError` prose) want the same structured affordance is answered by
  usage, not up front — see Deferred Decisions.

## Deferred Decisions

- ~~Field-name/shape convergence beyond documentation~~ — APPROVED 2026-07-17
  (operator, chat) with breaking changes allowed; now the Current Slice above.
- Structured affordances on `CharnessError` and catalog/session-capture error
  paths; revisit when a real consumer hits those dead ends.
- Internal quality-plane planner payloads (`plan_cautilus_proof.py`
  `next_action: "none"`, risk-interrupt and usage-episode warning
  `next_action` strings) keep their names: they are script plan surfaces
  consumed by repo scripts, not the CLI output boundary this contract owns.
  Revisit only if they graduate into `charness` CLI payloads.
- The `charness doctor --next-action` flag keeps emitting
  `{"next_action": <message string>}`: it is an explicit "give me only the
  message" projection named after the flag, not a payload-shape violation; the
  default doctor payload carries the structured object. Revisit only if a
  machine consumer trips on it.
- The worktree manifest **input** key `next_action_hint` keeps its name: it is
  operator-authored config, not a payload affordance, and renaming it flips
  every existing external `worktree-adapter.yaml` to invalid (the schema is
  `additionalProperties: false`), dropping their custom doctor checks — a
  worse failure class than the naming drift. Revisit on the next manifest
  schema version bump.

## Non-Goals

- A hypermedia link-relation registry or affordances on every read-only
  inspection payload (`capability explain`, `catalog list`, `version`). The
  consumer is a judgment-capable agent; descriptive reads stay descriptive
  (north-star P1).
- Changing exit semantics or payload envelopes of existing commands.

## Deliberately Not Doing

- A blocking validator that forces every new payload to carry an affordance —
  that is the floor-addition reflex `implementation-discipline.md` warns
  against; the documented convention plus judgment is the P1-honest tool here.

## Constraints

- `charness` CLI stays stdlib-only (plus packaged PyYAML) and runnable from a
  managed checkout.
- Generated surfaces (`docs/generated/cli-reference.md`, `plugins/` mirror)
  re-sync before validators (`mutate -> sync -> verify -> publish`).

## Success Criteria

- A blocked `charness task` caller can execute the recovering command by
  reading only the rejection payload.
- An agent reading only `.charness/tasks/<id>.json` sees the same continuation
  affordance the original stdout carried.
- A reader of the generated CLI reference learns the affordance convention
  without reading source.

## Acceptance Checks

- unit: `tests/charness_cli/test_task_envelope.py` asserts rejection payloads
  carry a `next_step` naming the recovering command for `missing`,
  `already-owned`, and `missing-result` statuses (slice 1, standing).
- unit: worktree doctor/create/cleanup/audit tests assert the payload key is
  `next_step` and the human affordance line prefix is `NEXT:`; managed-install
  and doctor tests assert `host_next_steps` on runtime doctor/update payloads.
- unit: no source or test under `scripts/worktree_*.py`, `charness`, or
  `tests/charness_cli/` references the removed string-`next_action` key or the
  `NEXT_ACTION:` / `next:` affordance prefixes (grep-clean check inside tests
  or review; the deliberately-kept manifest input key `next_action_hint` and
  the structured `next_action` object are expected matches, not violations).
- e2e/specdown: `specs/tool-doctor.spec.md` asserts root doctor emits a
  structured `next_action` dict **and** a non-empty `host_next_steps` dict.
- integration: `python3 scripts/run_slice_closeout.py --repo-root .` passes
  with the regenerated CLI reference and plugin mirror staged.

## Boundary Ownership

- Verdict: owned-correctly — the affordance convention lives on the CLI and
  generated-docs surfaces this repo owns; the deferred convergence stays
  visible here and in the handoff rather than moving to a new owner.

## Critique

- Public-skill validation review (slice 2, 2026-07-17): the only public-skill
  surface change is one bullet in
  `skills/public/create-cli/references/command-surface.md` renaming the doctor
  guidance example `next_steps` → `host_next_steps`. Routing, prompt, tier
  (`hitl-recommended`), and acceptance evidence in
  `docs/public-skill-dogfood.json` are unaffected; the existing dogfood row
  stays frozen as-is. Closeout reruns with `--ack-cautilus-skill-review` on
  this recorded decision.
- Risk interrupt planner: `status: not-applicable` (no forced debug interrupt).
- Bounded fresh-eye critique runs at slice closeout with this spec plus the
  implementation diff in the reviewer packet, per
  `docs/conventions/operating-contract.md` critique discipline (one bounded
  critique per substantial bundle).
- Likely implementer misread guarded in text: "converge everything now" — the
  Deferred Decisions section names why not.

## Canonical Artifact

- This document, plus `tests/charness_cli/test_task_envelope.py` as the
  executable acceptance surface.

## First Implementation Slice

- Slice 1 (shipped `24e4919e`): the task-envelope affordance changes in
  `charness` plus tests, then the documentation surfaces, then
  sync/verify/critique/commit, then release.
- Slice 2 (current): worktree-lib rename first (libs + tests as one unit),
  then the `charness` CLI renames (`host_next_steps`, tool-attention
  `next_step`, `NEXT:` header) + tests, then docs/specdown/reference
  regeneration, then mirror sync, verify, critique, commit, push, and a
  major-bump release.

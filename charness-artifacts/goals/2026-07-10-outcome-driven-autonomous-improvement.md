# Achieve Goal: Outcome-driven autonomous repo improvement

Status: active
Created: 2026-07-10
Activation: `/goal @charness-artifacts/goals/2026-07-10-outcome-driven-autonomous-improvement.md`

This file is the living goal scratchpad. The user activated implementation
continuation in the originating session with "네 진행하세요"; the activation
command remains the portable resume form for a fresh host session.

## Active Operating Frame

- Current slice: S0 goal shaping and bounded design critique before code mutation.
- Current slice intent: freeze the smallest outcome-driven loop that can add
  honest feedback evidence without treating delivery as satisfaction or
  weakening privacy boundaries.
- Next action: pass pursue-readiness, activate the goal, then delegate the S1
  implementation slice to a lower-power coding agent.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Make Charness self-improvement outcome-driven: repair stale operating state, establish the first privacy-safe feedback signal beyond slice closeout delivery, and use prompt-mutation evidence to reduce judgment-surface ambiguity without unsafe deletion.

## Non-Goals

- Do not increase gate, artifact, or usage-episode counts as ends in themselves.
- Do not infer satisfaction from artifact creation, a green local gate, silence,
  or raw usage volume.
- Do not capture prompts, transcripts, user identity, or private source bodies.
- Do not delete handoff prompt sections from the N=2 mutation pilot alone;
  mutation survival may rank a demotion candidate but cannot prove dead content.
- Do not perform a push, issue close, release, external write, or live Cautilus
  evaluation in this goal without a new boundary-specific operator decision.
- Do not consume the 80-site argparse-help backlog before the outcome loop is
  proven; it remains low-priority mechanical debt.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Local reversible edits, tests, generated-surface sync, critique artifacts,
  goal/retro/handoff updates, commits, and read-only repository inspection are
  authorized by the user's implementation-continuation approval.
- Host axis: Claude and Codex are both supported; the feedback record contract
  must remain host-neutral, with host-specific observation confined to adapters
  or hook integrations.
- Evidence-channel axis: delivery evidence, operator feedback, issue/release
  lifecycle evidence, and repository state are distinct; no one channel may be
  silently relabeled as another.
- Privacy axis: only closed-enum outcome/feedback values and portable evidence
  references may be persisted; free-form user content is excluded.
- Handoff timing: stale state discovered at pickup is carried in this goal and
  repaired once at closeout, per the operating contract.

## User Acceptance

- Run the usage-episode report and see at least one supported, privacy-safe way
  to attach or emit observable feedback separately from `slice_closeout`
  delivery, without rewriting raw prompts or counting delivery as acceptance.
- Inspect focused tests showing invalid feedback values, missing evidence, or
  accidental sensitive/free-form payloads are rejected.
- Read `docs/handoff.md` after closeout and see current pushed/release state and
  the next-session sequence, without the obsolete #427-unpushed instruction.
- Inspect the prompt-mutation disposition and see either a proven small demotion
  or an explicit evidence-backed defer; no unproven deletion is acceptable.

## Agent Verification Plan

### Low-Cost Checks

- Goal artifact validator and authoring preflights for every changed gated
  artifact/doc/skill surface.
- Focused unit tests for the feedback writer/reconciler, validator, and reporter
  consumer paths; include importer/registry tests if a new module or CLI is added.
- Existing usage-episode validation/report commands over fixture data and the
  current local adapter state.
- Handoff and prompt-mutation document preflights when those surfaces change.

### High-Confidence Checks

- Fresh-eye critique of the design and final diff using a bounded slice packet.
- `run_slice_closeout.py --skip-broad-pytest` at slice boundaries.
- Final verification-lock closeout after the mutation set is frozen, with
  mutation coverage only if an eligible mutation-pool Python file changes.

### External Or Live Proof

- No external/live proof is authorized. Current-repo fixture proof and a
  privacy review establish the local capability; actual consumer-repo feedback
  coverage remains a non-claim until observed outside this dogfood checkout.
- Cautilus is validation-ready but does not fit the first deterministic data
  contract slice; any later behavior-eval request must first use the repo planner
  and ask-before-run wrapper contract.

## S1 Implementation Contract

### Fixed Decisions

- A `usage_episode` record remains producer-owned delivery/first-value evidence;
  `slice_closeout` must never emit or backfill satisfaction feedback.
- Feedback is a separate append-only `usage_feedback` event in the existing
  `usage_episode.jsonl` stream. The record schema becomes a discriminated union
  while existing v1 episode records remain valid.
- Every feedback event carries a closed `feedback_signal`, a
  `target_episode_id`, a deterministic/idempotent `feedback_id`, a closed source
  category, and a privacy-safe evidence reference. Raw bodies, prompts,
  transcripts, user identity, extra fields, and free-form evidence prose are
  rejected.
- The feedback vocabulary is the documented set: `accepted`, `edited`,
  `corrected`, `ignored`, `retried`, `follow_up_requested`, `human_confirmed`,
  `closed_issue`, and `released`. Reporter categories must classify every value,
  with any deliberately neutral value named explicitly.
- Validation rejects an unlinked target, duplicate conflicting idempotency key,
  invalid enum, or missing evidence. Exact duplicate CLI invocation is a no-op.
- Reporting keeps delivery episode count and feedback event count separate,
  joins valid feedback to the target episode, and computes coverage over delivery
  episodes only. Delivery alone can never satisfy feedback coverage.

### Probe Questions

- Probe: can the existing JSONL/schema/validator path carry the union without a
  parallel stream or registry? Answer location: S1 Slice Log. Default prediction:
  yes; create a separate file only if focused implementation evidence disproves it.
- Probe: should `edited` be neutral or friction? Answer location: S1 Slice Log
  and product-evidence tests. Default prediction: explicit neutral, because an
  edit alone does not establish satisfaction or failure.

### Deferred Decisions

- Automatic observers for issue closure, releases, handoff, or host conversation
  events reopen after the explicit writer/reconciliation seam is proven.
- Historical backfill of 1,329 local delivery records is not allowed without
  trustworthy target evidence.
- Consumer-repo feedback coverage, push, and remote/live proof remain operator
  decisions after local closeout.

### Acceptance Checks

- Schema and writer tests: one valid linked feedback event; invalid signal,
  missing target/evidence, extra sensitive/body fields, free-form evidence, and
  duplicate conflict are rejected; exact replay is a no-op.
- Validator tests: a base delivery without feedback remains valid and uncovered;
  linked feedback validates; unlinked/duplicate feedback fails with a useful
  error.
- Reporter tests: one delivery plus one linked `accepted` event reports one
  delivery, one feedback event, 100% linked feedback coverage, and one
  satisfaction signal; delivery count is not two.
- Classification tests: all nine feedback enum values are satisfaction,
  friction, or explicit neutral; unclassified count remains zero.
- Packaging/importer tests: source and plugin integration schemas/scripts stay
  synchronized, and any new CLI appears on its owning generated/package surface.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S0 | Shape, activate, and critique the outcome-driven goal | Prevent autonomy from collapsing into an unbounded cleanup pass | Pursue-ready goal, bounded plan critique, explicit boundaries | in progress |
| S1 | Add the smallest privacy-safe feedback evidence path beyond delivery | 1,329 local episodes have zero feedback and one emitter | Focused tests, validated schema/records, reporter distinguishes linked feedback from delivery | pending |
| S2 | Reconcile semantic operating state at closeout | Handoff says #427 is unpushed although its commits are on origin/main and v0.63.1 is released | Commit ancestry/readback evidence, concise current handoff, doc preflight | pending |
| S3 | Disposition the prompt-mutation demotion candidate | The pilot found one narrow redundancy but only N=2 and one scenario | Integrated deterministic proof and fresh-eye reading review, or evidence-backed defer | pending |
| S4 | Final quality, retro, and commit closeout | Task-completing repo work requires durable proof and learning | Verification lock, critique/retro artifacts, complete goal, clean committed tree | pending |

## Operator Decision Queue

- Decision: whether to push the completed local bundle and collect
  consumer/remote feedback evidence.
- Owner: operator.
- Why deferred: local implementation and verification do not require an
  irreversible remote write.
- Unblock action: explicitly authorize the bounded push/remote-proof lane after
  local closeout.
- Revisit trigger: goal artifact complete, commits ready, clean worktree.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the find-skills-recommended skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- Routing: find-skills ranked handoff from the task phrase, but repo semantics require achieve to operate the goal, impl for the code slice, quality for validation posture, critique for fresh-eye review, retro for learning, and handoff only at closeout; Cautilus is validation-ready but not justified for the first deterministic slice
- Gather: n/a — no external URL or private organizational source is required; all shaping evidence is checked into this repository
- Release: n/a — version, package, and publish surfaces are out of scope
- Issue closeout: n/a — this goal does not claim resolution of a tracked GitHub issue

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — the user approved implementation continuation and local commits with "네 진행하세요"; push, issue close, release, external writes, and live evaluator spend remain outside that approval and are queued separately

## Slice Log

## Context Sources

- `docs/design-north-star.md` — reversible judgment and irreversible-boundary
  evidence standard.
- `docs/product-success-metrics.md` — outcome vocabulary and explicit feedback
  coverage gaps.
- `charness-artifacts/quality/latest.md` — current quality posture and the
  low-priority argparse-help debt.
- `charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md` —
  N=2 demotion candidate, confounds, and scenario coverage debt.
- `charness-artifacts/retro/recent-lessons.md` — current false-proof and
  blinding repeat traps.
- `docs/handoff.md` plus current git ancestry/release commits — stale operating
  state to reconcile at closeout.

## Interview Decisions

- Mode family: artifact-only versus implementation-continuation. Chosen:
  implementation-continuation, because the user explicitly said to proceed.
  Rejected: stopping at a plan would not satisfy the activation message.
- Improvement family: mechanical warning cleanup versus outcome-loop repair.
  Chosen: feedback evidence first because the local report has 1,329 delivery
  records and zero feedback signals. Rejected: argparse help is real but does
  not reduce the central product-evidence veto gap.
- Autonomy family: unrestricted external action versus local reversible
  autonomy. Chosen: local edits/tests/commits with external boundaries queued.
  Rejected: the prompt did not authorize push, release, or issue closure.
- Feedback-source family: raw conversational capture versus closed-enum durable
  evidence. Chosen: closed enum plus portable evidence references. Rejected:
  raw content violates the existing privacy posture.
- Axis check: host is a real Claude/Codex axis; feedback source and evidence
  channel are also real axes. No observed value is promoted to a global host or
  provider default. The current checkout is a single-point dogfood source only.

## Plan Critique Findings

- Same-agent shaping critique: a new public `autopilot` skill would duplicate
  existing achieve/impl/quality/retro composition; rejected in favor of a goal.
- Same-agent shaping critique: handoff must not be rewritten at pickup; folded
  into S2 closeout timing.
- Same-agent shaping critique: counting another emitter without observable
  feedback would repeat the delivery-as-satisfaction error; folded into S1
  acceptance and privacy/evidence boundaries.
- Fresh-eye plan critique: two parent-delegated spec angles plus a separate
  counterweight completed; findings are persisted in
  `charness-artifacts/critique/2026-07-10-outcome-driven-feedback-loop-pre-implementation-critique.md`
  and folded into `## S1 Implementation Contract`.

## Off-Goal Findings

- Existing goal artifacts with `Status: active` were found on disk, but no host
  goal slot is active. Auditing historical lifecycle drift is outside this goal
  unless it blocks validation.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named

# Achieve Goal: Make subagent delegation work without an AGENTS.md block

Status: draft
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-make-subagent-delegation-work-without-an-agents-md-block.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-03-make-subagent-delegation-work-without-an-agents-md-block.md` after confirming the draft is
  still intended.
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

**A repo that installs charness should get bounded fresh-eye subagent review
without having to declare it in its own `AGENTS.md` prose.** Today it does not,
and the operator hit this directly.

Root cause, verified by reading the surface rather than assuming:
[fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md)
line 86 names exactly ONE source of the standing delegation request —

> "If `<repo-root>/AGENTS.md` contains a dedicated `Subagent Delegation` contract
> that says repo-mandated bounded fresh-eye reviews are already delegated, treat
> that as the explicit delegation request …"

That reference is what an agent reads when deciding whether it may spawn. With a
single named source, its ABSENCE reads as absence of authorization, so an agent
in a repo without the block falls back to "no explicit user request" and declines
to delegate. The skill that MANDATES the review cannot authorize it.

What is NOT broken, and must not be "fixed": the two code consumers of that
text — `validate_critique_artifacts.has_repo_delegation_contract` and
`issue_critique_observer.repo_requires_delegated_observer` — already degrade
open. A repo without the block is not held to the stricter critique/close rules
at all (`issue_resolution_critique.py:269`: "A repo without the contract is not
held to it at all"). Neither gates spawning. Verified before shaping this goal;
the fix is to the CONTRACT surface, not to those validators.

Tracked as [#475](https://github.com/corca-ai/charness/issues/475), filed from the
operator's own observation: a repo where `setup` never ran refuses to spawn
subagents automatically.

The deliverable is that the standing request has more than one legitimate source,
and that a fresh repo with charness installed and no hand-written `AGENTS.md`
block gets bounded review — proven on a real repo, not argued.

## Non-Goals

- **Not removing `AGENTS.md` as a source.** Repos that carry the block keep
  working unchanged; this ADDS sources, it does not migrate.
- **Not loosening what counts as a real block.** A genuine tool refusal, missing
  spawn surface, or exhausted budget stays a blocker, and a same-agent substitute
  stays forbidden. This goal changes where AUTHORIZATION may come from, never
  what counts as PROOF that a review ran.
- **Not #472.** The forbidden-phrase list is a critique-artifact recording rule
  and has nothing to do with whether delegation works. Measured and left filed.
- **Not the dormant-gate sweep** now parked in
  [the sibling draft](./2026-08-03-count-the-rest-of-the-class-this-run-kept-finding-by-accident.md).
- **Not a new blocking floor.** Nothing here should add a gate; a repo that wants
  no subagents must stay able to have none.

## Boundaries

- **External side-effect scope, enumerated in full.** (1) `git push` to `main` of
  work this goal creates, plus the `quality-core` runs those pushes trigger.
  (2) Filing an issue for the defect this goal fixes, and for anything it
  surfaces and does not fix. NOT approved and NOT carrying forward: a publish, a
  tag, a version bump, or any `cautilus evaluate` run. The 2026-08-02 approval
  was scoped to that goal and does not carry.
- **Phase-scoped approval.** Push approval covers the phase that requests it and
  does not carry to a later phase; batch local proof, run remote CI once.
- In scope: [fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md)
  (the authorization rule), the public SKILL.md surfaces that mandate bounded
  review (`critique`, `quality`, `prove`, `setup`), and whatever `setup` writes
  or inspects for the delegation contract.
- Also in scope: the generated `plugins/charness/` mirror of every touched file,
  and a real-repo proof that a fresh install delegates. Sync mirrors before
  validators (`mutate -> sync -> verify`).
- Stop conditions: (1) if making the skill self-authorize turns out to require a
  trust posture the operator has not approved (see `## Discuss Before
  Activation`), STOP and bring the choice back rather than picking one.
  (2) If the proof requires a scratch repo outside this checkout, create it under
  a temp path and record it; do not mutate an unrelated real repo.
  (3) If the fix starts growing into a rewrite of the review contract, cut back
  to the authorization-source change.

## User Acceptance

- **The symptom is gone, proven on a real repo:** a scratch repo with charness
  installed and NO `Subagent Delegation` block in its `AGENTS.md` (or no
  `AGENTS.md` at all) gets a bounded fresh-eye review when a task-completing
  `critique` / `quality` run calls for one. Proven by an actual spawn that
  returns findings, not by reading the contract and concluding it should work.
- **The authorization rule names more than one source**, and states for each what
  makes it legitimate — so a future reader can tell why a skill invocation counts
  and cannot silently add a weaker source.
- **Repos that DO carry the block are unchanged**, pinned by a test.
- **No new refusal.** A repo whose host genuinely cannot spawn still degrades to
  `blocked <host-signal>` exactly as before, pinned by a test.
- **Global:** every figure in `## Final Verification` carries
  `<value> — <source>` or `<value> — unbacked: <why>`, and every corpus
  measurement states its denominator, what population it selects, and when it was
  taken.

## Agent Verification Plan

### Low-Cost Checks

- **Verify the premise before shaping each slice.** This goal exists because the
  previous session spent a lane on a phrase list that had nothing to do with the
  operator's actual symptom; the root cause was one line in a reference.
- Re-read the two code consumers before touching them — both already degrade
  open, and "fixing" them would be a change with no defect behind it.
- `check_python_lengths.py --headroom` before a large addition; SPLIT rather than
  shave when it refuses.
- Targeted `pytest` AND `ruff check` in the same breath.
- The dup-ratchet at the FIRST edit to a gated file, not at the closeout
  aggregate. Three consecutive runs have written this line and then not done it.
- File the issue first, then write its number into prose.
- Run `validate_handoff_artifact.py` before composing a commit message that
  touches the handoff.

### High-Confidence Checks

- One bounded fresh-eye round per slice; **TWO for the authorization-rule
  change**, because it changes when an agent may spawn — round 2 reads the
  repairs.
- `reviewer_boundary_fingerprint.py snapshot` around each review, and
  `verify --before` the MOMENT the reviewer returns, before any parent write.
- A closeout-claims review by a DISTINCT observer before the complete flip.
- **The real-repo proof is the acceptance, and it is a behavioural claim**: a
  contract change that reads correct but does not change behaviour is the exact
  failure mode this goal is about. Do not accept "the rule now permits it" as
  evidence that an agent did it.

### External Or Live Proof

- A scratch repo with charness installed and no delegation block, where a
  task-completing run actually spawns and receives a bounded review. This is the
  goal's central evidence, not a nice-to-have.
- `git push` to `main` and the remote CI it triggers, confirmed per P4 by a
  different observer AND a different evidence channel than the push exit code.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Reproduce the symptom on a scratch repo with no delegation block, and record exactly what the agent does instead of spawning | A behavioural defect needs a behavioural reproduction first. The operator has already OBSERVED it once (a repo where `setup` never ran refuses to spawn automatically), which is why this is tracked as [#475](https://github.com/corca-ai/charness/issues/475) rather than as a hypothesis — this slice turns that observation into a repeatable one | A recorded reproduction: the repo shape, the run, and the agent's own stated reason for not delegating | pending |
| B | Give the standing request more than one legitimate source, and state why each is legitimate | The skill that mandates bounded review cannot currently authorize it, so the mandate is inert in exactly the repos that installed the skill to get it | The amended authorization rule; tests pinning that block-carrying repos are unchanged and that a genuine host block still degrades to `blocked`; two bounded rounds | pending |
| C | Re-run slice A's reproduction and show the review now happens | The acceptance is behavioural. A contract that reads correct and changes nothing is this goal's own failure mode | The same scratch repo, same run, now spawning and returning findings | pending |
| D | Closeout: bundle gate, final verification, closeout-claims review, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest number; `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | pending |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
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
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: TWO items. (1) THE TRUST POSTURE, and it is the whole design decision. Today the standing delegation request is the REPO OWNER's, checked into their own `AGENTS.md`. Every alternative source shifts who is granting it: (a) invoking the skill counts as the user's act, so `/charness:critique` authorizes the bounded reviewers that skill mandates — most direct, and the plugin effectively grants itself spawn rights in any repo that installs it; (b) a structured opt-in that `setup` writes (e.g. an adapter field), which keeps the grant repo-owned and removes only the PROSE-MATCHING fragility that #471 proved, but still needs a file in the repo; (c) both, with `AGENTS.md` kept as a third. My recommendation is (c) with (a) scoped narrowly to the named bounded-reviewer scopes only — never a general spawn licence — but this is the operator's call because it changes who authorizes work that costs tokens. (2) IRREVERSIBLE SIDE EFFECTS — `git push` to `main` plus the CI each push triggers, and filing issues. Needs explicit approval at activation; the 2026-08-02 approval does not carry.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md)
   — line 86 is the defect. Read the whole `## Distinct Named Lenses` neighbourhood
   for what the contract is protecting before changing where authorization comes from.
2. [issue_resolution_critique.py](../../skills/public/issue/scripts/issue_resolution_critique.py)
   line 269 and
   [issue_critique_observer.py](../../skills/public/issue/scripts/issue_critique_observer.py)
   — the two code consumers, both already degrading open. Read them to confirm
   they are NOT the defect before touching them.
3. [scripts/templates/agents_subagent_delegation.txt](../../scripts/templates/agents_subagent_delegation.txt)
   — what `setup` writes into a managed repo today.
4. [docs/design-north-star.md](../../docs/design-north-star.md) — the mandate here
   is inert in the repos that installed the skill to get it, which is a fail-open
   proof surface: no failure, no log line, no ticket.
5. [The 2026-08-03 goal](./2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md)
   — repaired the same contract's CODE reader (#471). Its lesson applies directly:
   a rule keyed on matching repo prose fails silently.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

1. **What is the actual defect?** Family considered: {the phrase list is too
   narrow; the validators refuse repos without the block; `setup` fails to write
   the block; the authorization rule names only one source}. **Chosen: the
   authorization rule.** The operator reported the symptom directly — delegation
   does not happen in repos without the block — and reading the two code
   consumers showed both already degrade open, so no validator is refusing
   anything. Rejected: the phrase list, which is a critique-artifact RECORDING
   rule and was a full session's detour before the symptom was stated.
   Anti-anchoring: `axis: layer` — this looked like a code defect for one whole
   session and is a contract-text defect.
2. **How is it proven?** Family considered: {read the contract and argue; a unit
   test over the rule text; a real scratch repo with a real spawn}. **Chosen: the
   scratch repo with a real spawn**, reproduced BEFORE the fix and again after.
   Rejected: the text test alone, because "the rule now permits it" is exactly
   the kind of evidence that let a guard sit dormant for months — a contract that
   reads correct and changes no behaviour is this goal's own failure mode.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

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

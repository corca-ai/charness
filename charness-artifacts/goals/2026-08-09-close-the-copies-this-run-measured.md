# Achieve Goal: Close the copies this run measured, and the two proof surfaces it deliberately did not

Status: draft
Created: 2026-08-09
Activation: `/goal @charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md` after confirming the draft is
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
  `- Discuss before activation: RESOLVED. Slice 1 DELETES or re-shapes a proof
  surface — the owner-inspection half of the `#514/#515/#518` freeze receipt —
  which is a consequential change to something another issue family owns. It is
  claimed anyway because the measurement is complete and filed (6 of 20 locators
  changed in one day, five re-stamps, an observed 0/5 true-positive rate, and
  `refreeze` is one mechanical command that until the predecessor run recorded no
  basis), and because leaving it unclaimed a third time is itself a decision
  nobody is taking. The source-snapshot half is explicitly out of scope, and the
  slice's acceptance admits EITHER outcome — removal, or a required basis — so the
  goal does not presuppose the answer.
- Discuss before activation: RESOLVED. Closing the claimed issues rides the repo's
  standing close-on-floor approval, and the predecessor closed five that way with
  a delegated resolution critique and an adapter readback each time. Broad proof
  runs ONCE at the bundle boundary per `## Active Operating Frame`. Every
  proof-level non-claim is named in `## Agent Verification Plan`, and no push,
  release, tag, or Cautilus run is implied by activation; each stays per-request.

## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Predecessor: `charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md`. It is the FIRST goal in this family to finish its plan — five slices, five reached, five issues closed and verified — and its measurements, not its leftovers, shape this one.

**What it measured, and why that changes how these are built.**

1. **Eighteen blockers across ten delegated rounds, and NOT ONE was in a first diagnosis.** Every premise check was right about the defect; every blocker was in a REPAIR. That is a different fact from "round 2 is useful" — it says the cost of a verdict-logic slice is roughly double what a one-round plan budgets, so two rounds are planned as a COST here rather than remembered as a rule.

2. **A repair inherits HALVES.** The sharpest single theme. One repair inherited half a layout (source tree but not installed, so every installed capture would have died), one half an exception contract (a typed refusal swallowed by the caller's broad `except RuntimeError`), and one half an owner (delegating to a consolidated function while passing its `required` set empty, one slice after building that floor). Ask of every repair what it did NOT inherit.

3. **Opening the file is necessary and NOT sufficient.** The predecessor's rule was "open every location an instruction names". This run opened one, printed the evidence, and then wrote the opposite two steps later. Quote the read back into the claim.

4. **A test that re-implements its subject is another copy of the rule.** Shipped inside the slice about copies of rules: it rebuilt a loader's candidate list and asserted on its own copy, so it would have passed with the loader deleted. And a pin must read the SOURCE — a mutant survived a pin that read the generated mirror, because the mirror lags until the next sync.

5. **A premise check verifies the claim it is pointed at, and nothing else.** It correctly refuted two issues' stated blockers and was silent about the one that actually held — a binary-position difference found only by executing the replacement. Smoke-test a consolidation before believing any analysis of it.

**The remaining work**, and it is deliberately two proof surfaces plus a structural tail:

- `#562`: the owner-inspection locator pin, with an observed 0/5 true-positive rate over five re-stamps. A proof-surface DELETION touching ~35 `sha256` references plus a schema bump. Named as not-claimed by two goals in a row on budget grounds; this goal claims it, with two rounds budgeted from the start.
- `#561`: two probes pin EQUALITY against a corpus ordinary work mutates, while a third pins the invariant and has never needed a refresh. The decision between the two styles belongs to D47's owner and should be taken deliberately.
- `#560`: the ready-path payload is owned only by tests requiring a clean worktree, so while any blocker is live NOTHING exercises it.
- The structural tail this run measured but did not spend: `issue_verify_closeout.py` at 351/360 with the next addition owing a split, and the renderer-versus-reference spelling split in `setup` (the renderer is gated against baking a model id into the contract while a reference instructs an agent to write exactly that).

**One inherited obligation that is not a slice.** The backlog stands at 28 open. The prompt-surface cluster (`#519`-`#532`) remains a measurement question and is still not this family's.

## Non-Goals

- **Do not build `#562` in one round.** Two goals refused it on budget grounds and
  both were right; claiming it here means paying the budget, not shrinking the
  work. Its build gets two delegated rounds from the start, and the round-2 slot
  is planned rather than earned.
- **Do not touch the freeze's SOURCE-SNAPSHOT half.** That half defends a
  genuinely external mutable dependency (issue bodies) and is sound. Only the
  owner-inspection locator pin is in question, and `#514`/`#515`/`#518` own the
  receipt it lives in.
- **Do not decide `#561` from the measurement alone.** Equality-versus-invariant
  is D47's owner's call; this goal's job is to put the choice in front of that
  owner with both costs measured, not to take it.
- Do not take the prompt-surface cluster (`#519`-`#532`). Still a measurement
  question, and still not this family's.
- Do not re-home the six issues the predecessor returned to the backlog
  unclaimed. They were released deliberately; re-adopting them without a premise
  check is how a plan grows past what it can reach.
- No release, tag, version bump, push, or Cautilus run unless separately granted.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- `#562` reaches a verdict: either the owner-inspection locator pin is REMOVED
  with the freeze's source-snapshot half intact, or each re-stamp is required to
  record a BASIS and the 0/5 measurement is recorded against that choice. Whichever
  is chosen is proven by CONSTRUCTION — an input that would have produced the old
  behaviour is shown refused or shown recorded.
- `#561` is put to its owner as a decision with both costs measured, or is closed
  with the measurement that makes the choice obvious. It is not silently adopted.
- `#560`: something exercises the ready path that does not require a clean
  worktree, so the payload stops being unowned whenever a blocker is live.
- Every slice that changes verdict logic gets TWO delegated review rounds, and the
  second round's findings are recorded whether or not they produced repairs.
- Each slice records its premise-check verdict BEFORE the build, and any slice
  that CONSOLIDATES or DELEGATES is smoke-tested against a real caller before the
  premise check's conclusion is believed.
- Verification cadence follows `## Active Operating Frame`. This section names no
  command and no boundary frequency on purpose.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin
  sync BEFORE validators.
- `check_dup_ratchet.py --summary` and `check_python_lengths.py --headroom` EARLY
  in each slice, not at the commit boundary. The predecessor hit three
  commit-boundary blocks and each forced a full aggregate re-run; every one was
  right and named a real second owner or a real module boundary.
- After ANY commit-gate rejection, run the aggregate (`run_slice_closeout.py`)
  rather than fixing one rejection at a time.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- **TWO delegated review rounds on any slice that changes verdict logic, budgeted
  as a plan-level COST.** The predecessor's measurement: eighteen blockers across
  ten rounds, and not one was in a first diagnosis. Round 2 reads the REPAIRS.
- **Ask of every repair what it did NOT inherit.** Half a layout, half an
  exception contract, half an owner — three of the predecessor's round-2 blockers
  were exactly that shape.
- **Mutate every REPAIR, not only the original code**, and pin the SOURCE rather
  than a generated mirror; a mutant survived a mirror-reading pin because the
  mirror lags until the next sync.
- **Smoke-test a consolidation before believing any analysis of it.** A premise
  check verifies the claim it is pointed at and nothing else.
- **Verify the reviewer boundary the moment a reviewer returns, BEFORE repairing.**
- For any claim about where a fact lives, quote the read back into the claim.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer AND
  a different channel than the push exit code.
- An issue's `CLOSED` state is a non-claim until `verify-closeout --expect-state
  CLOSED` reads it back through the adapter.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

Three slices, and the budget is deliberately front-loaded onto the largest one.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `#562`: the owner-inspection locator pin, 0/5 measured true positives | Two goals refused it on budget grounds; it is claimed here BECAUSE the budget is planned rather than borrowed from a tail slice | A verdict either way, proven by construction; the freeze's source-snapshot half untouched; TWO delegated rounds recorded | planned |
| 2 | `#561`: equality-versus-invariant probe pins | The decision is D47's owner's, and it should be taken with both costs measured rather than by whoever next hits the red | The choice put to its owner with the measurement, or closed with the measurement that settles it | planned |
| 3 | `#560` plus bundle proof and closeout | Cheapest, and composition can drop what each slice proved alone | The ready path exercised without requiring a clean worktree; verification lock recorded; broad proof ONCE | planned |

NOT claimed, and named so the next session does not re-derive the decision:
`#563` (needs a decision on 3 non-English titles first), the prompt-surface
cluster, and the six issues the predecessor returned to the backlog unclaimed
when it closed at five of eleven rows.

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: **28 open issues** on 2026-08-08 via
  `gh issue list --repo corca-ai/charness --state open --limit 100 --json number`,
  down from 33 because the predecessor closed five. Rerun the command before
  reshaping scope; the reconciliation is a command, not an adjective.
- Claims: `#562` (the owner-inspection locator pin, 0/5 measured true positives —
  a proof-surface DELETION touching ~35 `sha256` references plus a schema bump,
  refused by two goals in a row on budget grounds and claimed here WITH the budget),
  `#561` (equality-versus-invariant probe pins, a decision D47's owner should take
  deliberately), and `#560` (the ready path is owned only by tests requiring a clean
  worktree, so while any blocker is live nothing exercises it). Three.
- Not claimed: `#563` (`check-title-slug-drift` reports clean over a scope excluding
  `charness-artifacts/goals`; widening it needs a decision on 3 non-English titles
  first or it lands red on day one). The prompt-surface cluster `#519`, `#520`,
  `#521`, `#523`, `#524`, `#525`, `#527`, `#531`, `#532` — still a measurement
  question and still not this family's. `#514`/`#515`/`#518` — consumer ownership,
  and the source-freeze receipt this goal's `#562` slice touches is theirs, so
  changing it needs their owner in the loop. `#539`, `#545` — provider/publication
  safety. `#530`, `#535`, `#554` — operator decisions carried forward. `#534` —
  BUILT green, then REFUTED and REVERTED by an earlier goal; re-scope from the
  refutation, never from the title. `#528`, `#542`, `#546`, `#547`, `#549`, `#550` —
  returned to the backlog UNCLAIMED when the `one-rule-one-owner` goal closed at
  five of eleven rows rather than carrying them into a plan nobody would reach.

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
- **Successor goal step** — required at EVERY completion, not conditionally. Add
  a `Successor goal:` line naming the next goal artifact this run's lessons
  designed, or write `Successor goal: n/a — <reason>` to say out loud that none
  is wanted. The closing goal is the only place that still holds what the session
  measured about this repo's real shape; a completion that does not spend it
  throws that away, and the next session re-derives it.

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


## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. TODO the repo's governing design standard, and what it says about THIS goal —
   which facets bear on its boundaries, where its teeth belong, and which
   irreversible boundaries it crosses. Read it while SHAPING, not at closeout:
   the standard is what tells you where a wrong answer escapes, and that is a
   Before-phase question. (The retro's `## North Star Alignment` asks the
   backward-looking half; this is the forward-looking one.)

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

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

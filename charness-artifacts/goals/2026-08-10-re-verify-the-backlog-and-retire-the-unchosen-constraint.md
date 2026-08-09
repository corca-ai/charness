# Achieve Goal: A record is not a fact: re-verify the backlog, consolidate what survives, and retire the constraint nobody chose

Status: draft
Created: 2026-08-10
Activation: `/goal @charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md` after confirming the draft is
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

**The finding this goal is designed from.** `#554` — "achieve shapes a goal without ever reading the tracker" — has been FIXED since before it was last read: `skills/public/achieve/references/lifecycle-before.md:35` carries the tracker-recount step, and that reference quotes `#554`'s own complaint as its reason for existing. Nobody re-read the issue after shipping its fix. `#571` files the same defect one layer up (a goal is shaped around a remedy a durable record already proposed, and nothing re-checks it), which makes `#554`'s staleness `#571`'s evidence.

**The pattern, measured on the backlog's provenance rather than on its titles.** The 25 open issues are not 25 defects. They are roughly six gaps seen from four angles, because the backlog grows per COMPARISON SESSION, not per defect: `#519 #520 #521` came from one anthropics/skills reading, `#524 #525` from one ceal reading, `#527` from one mattpocock reading, `#523 #566` from craken-agents, `#515 #518 #528` from cmanki. Each sibling-repo session files four to six issues describing the same underlying gap from that repo's vantage, and no step ever folds them back together or re-checks them against a tree that has since moved.

**The pattern of the pattern, and why this goal leads with a deletion.** `docs/prompt-mutation-policy.md` — every commit authored by an agent identity on 2026-07-09, referenced by no script, gate, or skill, read only by `docs/README.md` — has been operating as a binding constraint. A prior goal's Operator Decision Queue parked "may `AGENTS.md` be physically shrunk" underneath it, so an unarmed document nobody chose became a cut vertex on real work. The operator's ruling, taken this session, is that deletion and compaction must be actively available. The same disease appears twice more in the same backlog: a stale issue believed because nobody re-read it, and a 7-day audit that concluded `create-cli` had "no consumer trace" by measuring artifact write paths — a population that structurally cannot contain a process skill used to BUILD a CLI, which the operator refuted from direct use. Three surfaces, one shape: **a record was treated as a fact because re-reading it was nobody's step.**

**What this goal does, in the order the finding suggests.** Retire the unchosen constraint first, because it gates the compaction moves every later slice may need. Then make backlog re-verification executable, because it shrinks the denominator for everything after it and is the durable answer to an append-only backlog. Then consolidate on GitHub — which forces a design question this repo has not answered: what closeout floor applies to a close that claims NOTHING about the defect, only that it moved. Then take group A, the one family whose defect reaches consumers as a false green.

**What it does not do.** It does not re-measure the consumer repos. That measurement has been taken repeatedly across sessions and is not the bottleneck; the bottleneck is that nothing folds those readings together or re-checks them. Re-running it would be this goal committing the error it exists to name.

## Non-Goals

- **Not a consumer-repo measurement run.** The five consuming repos have been
  read repeatedly across sessions and their findings already sit in the issue
  bodies. Measurement is not the bottleneck; re-running it would be this goal
  committing the error it exists to name.
- **Not a fix for groups B through E.** Those become shaped umbrella issues.
  Turning a consolidation goal into a five-family repair goal is how the previous
  attempt reached `complete` with most of its slices still `planned`.
- **No gate that auto-closes an issue.** The re-verification tool renders a typed
  premise state and stops. A tool that closed issues from its own verdict would be
  a new false-verdict surface inside the tool built to stop them.
- **No Cautilus run.** Skill evaluation belongs to `../cautilus`; the operator
  ruled `#519`/`#520` a cadence question, not a build.
- **Not a bloat-reduction goal.** The 7-day audit refuted that premise. Slice 1
  removes ONE constraint because it gates work, not because the repo is too big.

## Boundaries

- **The prompt-mutation policy's evidentiary rule survives; only its reach is
  cut.** "A survival verdict is not a deletion proof" stays true INSIDE that
  experiment pipeline. What ends is that rule governing ordinary editorial
  deletion and compaction, which it was never chosen to govern.
- **Consolidation closes claim nothing about the defect.** A consolidated close
  says the issue moved, not that it was fixed. It must be a different typed
  disposition from a resolution close, or the repo buys twenty cheap closes at
  the price of its closeout floor's meaning.
- **Issue close stays an irreversible boundary.** Roughly twenty closes run here;
  each renders a state others read as done. The floor applies per close, in
  whichever form its disposition names. No batch waiver.

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.


## User Acceptance

- The open-issue list reads as work units: roughly six items where there were
  twenty-five, each one something a person could pick up, with the rest closed
  and linked to where they went.
- No open issue describes a live consumer-facing false green. Group A is fixed or
  explicitly dispositioned with its reason recorded on the issue.
- Asking the repo "is this issue still true?" is one command, not a reading
  session. Running it names at least one issue whose premise the tree has already
  refuted, the way `#554` was found by hand.
- Shrinking a prompt surface no longer needs an operator decision, and the record
  says who decided that and when.
- Nothing in the closeout record claims a consolidated issue was fixed.

See `## Active Operating Frame` for when each is proven.

## Agent Verification Plan

### Low-Cost Checks

- `check_doc_links.py` and the staged-mirror gate after every docs or policy edit.
- The re-verification tool's unit tests, seeded with `#554` as an issue whose
  premise the tree refutes AND one whose premise still holds, so a tool that
  always answers `holds` fails.
- `issue_tool.py validate-closeout-draft` against every carrier before any GitHub
  mutation.

### High-Confidence Checks

- `./scripts/run-quality.sh --release` at the bundle boundary.
- Bounded fresh-eye review on the policy retirement, on the consolidated-close
  disposition (a proof-surface change, so it owes the second round reading the
  repaired surface), and on group A's repairs.
- Group A's refuting measurement must be taken in a tree that is not this one.
  `#576`'s whole content is that the reader corpus cannot be established outside
  this repo, so an in-repo probe cannot answer it.

### External Or Live Proof

- Per-issue GitHub state readback via `issue_tool.py verify-closeout
  --expect-state CLOSED`, plus a separate read of each umbrella issue's rendered
  body confirming its members are linked.
- Hosted `Quality Core` on the final bundle.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Retire the constraint nobody chose | A cut vertex: a prior goal parked `AGENTS.md` shrinking underneath it, and slices 3-4 may need compaction moves it forbids. Cheapest unblock available | The policy scoped to its own pipeline; the operator ruling recorded with date and reasoning; `#521` closed citing it | planned |
| 2 | Make backlog re-verification executable | It shrinks the denominator for slices 3 and 4, and it is the durable answer to an append-only backlog. Building it later would mean consolidating issues nobody re-checked | A repo-owned command emitting a typed premise state per open issue; `#554` reproduced as a refuted premise; `#571` closed in place | planned |
| 3 | Consolidate on GitHub | Only safe now: the stale ones are known and the constraint is gone. Forces the unanswered design question of what floor applies to a close that claims nothing about the defect | A typed consolidated-close disposition in the closeout contract; up to four umbrella issues filed; members closed, linked, and state-verified | planned |
| 4 | Close the family that reaches consumers | Group A is the only remaining set whose defect ships as a false green to installing repos, which is what the north star's diagnosis is about | `#576` `#518` `#528` `#515` `#546` fixed or dispositioned, each proven against a tree that is not this repo | planned |


### Slice 3 design — decided 2026-08-09, execute as written

The question slice 3 forces: **what closeout floor applies to a close that
claims nothing about the defect?** Neither existing branch fits. The resolution
classifications (`bug`/`feature`/`deferred-work`) demand `Implementation:`,
`Prevention:`, and `Behavior #N:` — a consolidation implements nothing, so
satisfying them means writing sentences that are not true. The exempt
classifications (`question`/`decision-needed`) fit no better: using them would
misclassify the issue AND open a path where any inconvenient bug reaches the
light floor by relabelling.

**Decision: add `consolidated` as a sixth classification. It is not floor-exempt;
it swaps the resolution floor for its own.** All of its checks are
machine-verifiable and none declares completion:

1. `Consolidated into: #N` is present and names exactly one destination.
2. `#N` exists and is OPEN at close time, read back from the backend rather than
   asserted in prose. Consolidating into a closed issue would evaporate the work.
3. **`#N`'s body contains this issue's number.** This is the load-bearing check:
   it forces the question "does the content actually live somewhere?" without
   answering "therefore this is resolved", and prose cannot satisfy it.
4. `#N` is not itself closed as `consolidated` — no chains.
5. The backend close reason is `not planned`, not `completed`.
   `skills/public/issue/scripts/issue_close.py` already threads `--reason`
   through the backend command templates, so this needs no new plumbing. The
   tracker itself then renders the distinction, which puts the signal on a
   channel outside this repo's prose.
6. No `Behavior #N:` and no `Critique #N:` are required, because nothing about
   the defect is claimed. Conversely, a carrier that DOES claim a repair must be
   refused under `consolidated`.

**Member survival, decided alongside it.** An umbrella's own close carries the
normal resolution floor AND must state an outcome for every member number it
absorbed — fixed, declined, or re-split. Without that rule, consolidation is a
laundering path: fifteen issues close quietly when one umbrella closes.

Implementation notes for the executing session: `KNOWN_CLASSIFICATIONS` and
`FLOOR_EXEMPT_CLASSIFICATIONS` both live in `skills/public/issue/scripts/`;
`consolidated` joins the first and NOT the second. This is a proof-surface
change, so it owes the second bounded review round reading the repaired surface.

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: 25 open issues on 2026-08-09 by `gh issue list --state open --limit 100 --json number --jq 'length'`, after nine closed against `v4.1.0` earlier the same session.
- Claims: all 25, in three senses that must not be conflated. FIXED — `#576` `#518` `#528` `#515` `#546`. CLOSED FOR A REASON THAT IS NOT A FIX — `#554` (already repaired; its fix quotes it), `#519` `#520` (cadence, owner is cautilus), `#572` (a bot notification about an old SHA, resolved by reading hosted state), `#521` (operator ruling), `#571` (closed in place by slice 2). CONSOLIDATED, CLAIMING NOTHING ABOUT THE DEFECT — `#525` `#524` `#514` `#535` `#542` `#561`; `#568` `#569`; `#531` `#532` `#527`; `#534` `#550` `#539`.
- Not claimed: none is left untouched, but fifteen are only MOVED. The umbrella issues carry the actual work forward and this goal does not do it.

## Operator Decision Queue

Already taken this session, carried in rather than re-asked:

- Deletion and compaction of prompt surface are actively allowed; the
  agent-authored `docs/prompt-mutation-policy.md` does not govern ordinary
  editorial deletion. Operator, 2026-08-09.
- Consolidate on GitHub with umbrella issues rather than labels or an in-repo map.
  Operator, 2026-08-09.
- Backlog re-verification becomes executable in this goal. Operator, 2026-08-09.
- `#519`/`#520` close as a cadence question. Operator, 2026-08-09.

Open, and inherited:

- `#561`'s equality-versus-invariant probe pin. Both costs are already measured in
  a predecessor's queue. If it is consolidated rather than decided, say so on the
  issue.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Phases** — name the phases this run's recorded work crossed, e.g.
  `Phases: debug, quality`, or `Phases: n/a — <reason>` when it crossed none. YOU
  say this; the floor used to infer it by matching words in your prose and was
  wrong in both directions — plain-English debug work did not register, while the
  word "gate" in an unrelated sentence demanded a quality route.
- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / issue work (both detected from records you wrote) and every
  phase you declared above need this `Routing:` evidence or a
  `Routing: n/a — <reason>` opt-out.
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

- `Phases: <declared phases, or n/a — why none were crossed>`
- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

- Discuss before activation: resolved — the four consequential decisions
  (prompt-surface deletion, GitHub consolidation, executable re-verification,
  `#519`/`#520` cadence) were taken by the operator on 2026-08-09 and are recorded
  in the operator decision queue. One consequential default is stated rather than
  asked because a strong default settles it: roughly twenty issue closes run
  inside this goal, and every one keeps the per-close floor in whichever form its
  disposition names.

## Slice Log

## Context Sources

Durable references this goal was shaped from, in reading order.

1. `docs/design-north-star.md`. The facets bearing on this goal: **P5** governs
   slice 2 — the re-verification tool may force the question "is this still true?"
   and may not answer "therefore close it"; **P4** governs slice 3, where twenty
   issue closes are irreversible boundaries and a consolidation close needs a
   disposition that cannot be read as a resolution; **P1** governs slice 1, since
   a policy constraining reversible editorial work bears the burden of showing why
   judgment alone fails, and an unarmed agent-authored document never carried it.
   Irreversible boundaries crossed: issue close, and a proof-surface change.
2. `charness-artifacts/audit/2026-08-08-open-issue-opinion.md` — the backlog
   grouped by the decision each issue needs. Heed its own warning: its headline
   thesis was refuted, and this session refuted one more of its measurements.
3. `charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`
   — the previous attempt at this backlog, `complete` at 8 closed with several
   slices still `planned`. Read why before shaping scope.
4. `docs/prompt-mutation-policy.md` and its git provenance — the constraint slice
   1 retires, and the evidence that an agent authored it and nothing consumes it.
5. `charness-artifacts/critique/2026-08-09-post-4-1-0-bug-closeout-critique.md`
   and its surface counterpart — the residuals the `v4.1.0` closes carried, four
   of which this goal may absorb or leave.

## Interview Decisions

- **Success metric.** Options: close all 25 as a count; drive live
  consumer-facing false greens to zero; both. Chose the false-green measure with
  consolidation as the mechanism. Rejected the count because the north star says
  count is not the metric in either direction, and a count target pressures the
  run toward whatever closes cheapest.
- **Whether to re-measure the consumer repos.** Considered making "measure in a
  different tree" the organizing move. The operator refuted it: it has been done
  repeatedly and the artifacts confirm it. The bottleneck is folding and
  re-checking, not measuring.
- **Consolidation mechanism.** Options: umbrella issues, labels only, an in-repo
  map. Chose umbrella issues so the tracker reads as work units from outside.
  Rejected labels because the count stays at 25, and the in-repo map because the
  noise is only visible from GitHub.
- **`#521`'s scope.** The issue, and this session's first summary of it, both read
  the policy as a blanket ban on shrinking prompt surface. Reading the file
  refuted that: it is an evidentiary rule about one experiment pipeline. The
  decision is therefore narrower than the issue asked for and larger in effect —
  the rule keeps its meaning and loses its reach.
- **Slice order.** Considered leading with group A, the highest-severity family.
  Rejected: slices 3 and 4 may both need compaction moves slice 1 unblocks, and
  consolidating before re-verifying would file umbrella issues containing members
  the tree has already answered.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

Shape these minimum fields before activation; closeout workflows prove the values.

- Reviewed inputs: this goal artifact; the four closeout critiques named in
  context sources; the re-verification tool's emitted premise report; each
  umbrella issue body.
- Frozen target: the commit landing slice 4's last repair; bind the closeout
  packet to that exact SHA.
- Fresh-eye: bounded `bounded-reviewer` subagents, unnamed and synchronous, in a
  context separate from the author. Channel for group A is execution against a
  tree that is not this repo; channel for the disposition change is the closeout
  validator's own refusal behavior, never a re-read of its source.
- Verification lock: `./scripts/run-quality.sh --release`, with per-check failures
  retained under `.charness/quality-failure-logs/`.
- Complete flip: record packet, reviewer, and lock evidence, then write terminal
  status and the successor-goal line outside the reviewed identity.

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

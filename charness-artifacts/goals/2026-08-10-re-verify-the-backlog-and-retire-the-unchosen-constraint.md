# Achieve Goal: A record is not a fact: re-verify the backlog, consolidate what survives, and retire the constraint nobody chose

Status: active
Created: 2026-08-10
Activation: `/goal @charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 3b (part 2) — file the umbrella issues, then move members.
- Current slice intent: implement the four BACKEND readbacks the disposition
  names but does not perform (destination exists, is OPEN at close time, its body
  contains this issue's number, and it is not itself a consolidated close), file
  the umbrella issues, then move members. This names the reviewable-intent unit in
  progress and the commits it spans; critique and broad proof do not re-fire
  within one unchanged intent (meaningful-slice-cadence).
- The four readbacks now EXIST and run on both carriers, including the one a
  consolidated close is required to use. The remaining precondition is authoring:
  check 3 requires each umbrella's body to name every member BEFORE the closes run,
  and only an edit to the destination can satisfy it.
- **Still no close may run**, for a different reason than before: filing umbrella
  issues and closing members are external side effects, and the only external grant
  this run holds is the push/release one for the slice 1+2 bundle, which is
  phase-scoped and does not carry.
- Next action: ask for the issue-filing/close grant, then file umbrellas naming
  their members. The push/release grant stays BLOCKED on `#580`, which is an
  operator floor decision, not something to force.
- Slice 1 status: done before activation in `ac019102`, re-verified against the
  tracker on 2026-08-10 (`#521` `#519` `#520` all CLOSED; 22 open, not 25).
- Slice 2 status: done. The seam ships with NO prose matching and NO fitted
  constants — residue is a typed `Premise-residue:` marker plus unchecked
  `- [ ]` items. Two bounded rounds ran; round 2 measured the prose version
  collapsing to 21-of-22 refusals and the operator refuted the approach itself.
- External side-effect grant, phase-scoped: the operator granted PUSH and
  RELEASE for the slice 1+2 bundle on 2026-08-10. It does not carry into slice 3;
  slice 3's issue closes need their own grant and their own per-close floor.
- Carried into slice 3: the record residue channel is WORKING BUT EMPTY —
  historical records carry no marker. Consolidation must WRITE `Premise-residue:`
  markers as it moves members, because nothing recovers intent from prose.
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
| 1 | Retire the constraint nobody chose | A cut vertex: a prior goal parked `AGENTS.md` shrinking underneath it, and slices 3-4 may need compaction moves it forbids. Cheapest unblock available | The policy scoped to its own pipeline; the operator ruling recorded with date and reasoning; `#521` closed citing it | done (`ac019102`, tracker-verified 2026-08-10) |
| 2 | Make backlog re-verification executable, as an EXTENSION of the existing recount seam (STATUS: done — structural markers only; the prose/threshold design was built, measured, and deleted) | It shrinks the denominator for slices 3 and 4, and it is the durable answer to an append-only backlog. Building it later would mean consolidating issues nobody re-checked | A typed premise state per open issue, emitted by the recount seam rather than by a second backlog reader; `#554` reproduced as `premise-refuted-with-live-residue`; `#571` closed in place | done — with one revision to the recorded expectation: `#554` is reproduced as a refusal via a typed marker, NOT by inferring a decline from record prose, and `#571` stays open into slice 3 |
| 3a | The `consolidated` disposition (done) / 3b consolidate on GitHub (not started) | Only safe now: the stale ones are known and the constraint is gone. Forces the unanswered design question of what floor applies to a close that claims nothing about the defect | A typed consolidated-close disposition in the closeout contract; up to four umbrella issues filed; members closed, linked, and state-verified | 3a done — the typed disposition ships with two bounded rounds; 3b NOT started, and no close may run until the four backend readbacks exist |
| 4 | Close the family that reaches consumers | Group A is the only remaining set whose defect ships as a false green to installing repos, which is what the north star's diagnosis is about | `#576` `#518` `#528` `#515` `#546` fixed or dispositioned, each proven against a tree that is not this repo | planned |


### Slice 2 design — two constraints that are not optional

**It extends the recount seam; it is not a second backlog reader.** `#554`'s part
2 says this outright — "building a second backlog reader inside `achieve` would be
the wrong repair" — and the same conclusion arrives independently from the
system-improving-itself lens: the recount step and the re-verification step are one
artifact seen at two scales, and building the second without noticing it subsumes
the first is how a harness accumulates parallel machinery. `#555` already
consolidated the tracker-BACKEND rule to one owner; this must not re-fork it.

**A refuted premise is not a close signal.** The naive typed state — `premise-holds`
/ `premise-refuted` — would have pushed the wrong way on the very instance that
motivated this slice. `#554`'s premise WAS refuted (the shaping step shipped) and
the correct answer was still DO NOT CLOSE, because its part 2 was live and the
goal that shipped part 1 said so in its own slice log. `#571`'s instance 2 (`#567`,
fully repaired, dispositioned from the issue body rather than from the commit that
fixed it) is the same shape. So the emitted state must distinguish:

- `premise-holds` — the issue still describes the tree.
- `premise-refuted-clean` — refuted, and no other ask or record contradicts closing.
- `premise-refuted-with-live-residue` — refuted, but the body carries a further ask,
  or a durable record (a goal slice log, an audit, an issue comment) explicitly
  declined to close it. This state is a REFUSAL to recommend, not a close candidate.
- `unverifiable-by-machine` — the premise is not decidable from the tree.

The residue check is what makes the tool worth building: grepping the issue number
across `charness-artifacts/goals/` is one command, and it is the command that would
have caught `#554` before a reviewer round was spent on it.

### Slice 3b grouping — the recount's groups were REFUTED on 2026-08-10

A bounded read of all fourteen member bodies (several are Korean; the titles do
not carry the gap) found the `## Backlog Recount` grouping was made by SURFACE
rather than by defect. Corrected, with the reason each move is not cosmetic:

- **Umbrella A — proof/evidence infrastructure is prose, not schema:** `#514`
  `#524` `#525` `#535`. These four cross-reference each other's boundaries in
  their own text, which is what a real family looks like. `#542` and `#561` were
  in this group and do not belong: `#542` is refusal-message granularity in an
  authorization branch, and `#561` is an equality-versus-invariant question in a
  regression probe. Neither is about binding a claim to evidence.
- **Umbrella B — a verification surface silently stops verifying:** `#568` `#569`.
  Endorsed unchanged. Both are a green that says nothing.
- **Umbrella C — a harness surface discards state it already has:** `#531` `#532`.
  `#527` was grouped here and must NOT be consolidated wholesale: only one of its
  six observations (the invocation lock on destructive skills) fits, and the
  issue's own author asks for it to be split.
- **Umbrella D — a gate pins volatile identity instead of the invariant:** `#534`
  `#561`. This pairing did not exist in the recount at all. `#534`'s family id
  rotates on a move; `#561`'s probe reds on any corpus write; each surface already
  contains the fix template the other needs. `#561` still carries its open
  operator decision and the umbrella must say so rather than absorb it.
- **NOT consolidated — `#550` `#539` `#542`, and the rest of `#527`.** `#550` is
  the ratchet working correctly and surfacing real duplication, which is the
  opposite of `#534`'s false block; grouping them because they touch one tool is
  the surface error in miniature.

The second read also found two members whose CITED instances are already fixed
while their real ask is live: `#535`'s issue-source freeze has a `refreeze`
command, and `#569`'s two awiki tests now have captured fixtures. Neither is
closable — both issues ask for the general rule, not the instances — but a
maintainer picking them up must be told, which is exactly the staleness this
goal exists to stop.

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

Open, and RAISED BY THIS RUN — the push the operator granted is blocked on it:

- **`check-seed-fixture-budget`'s 1000ms budget refuses every push, and it is not
  measuring this slice.** Filed as `#580` with the measurement: the check runs in
  0.06s standalone over a 152 KiB / 12-file tree, and `run-quality.sh` records
  1167ms for the same command — roughly 1.1s of process startup and contention
  against ~85 parallel gates. Two hypotheses were tested and REFUTED: machine load
  (still 1167ms at load 2.5) and accumulated pytest scratch (pruned 126 MiB / 13,012
  files to 152 KiB; the sample did not move). The recent median is self-sustaining
  because each blocked push appends another slow sample. DECISION NEEDED: re-baseline
  the budget, measure the check's own work instead of wall-clock-under-fan-out, or
  give the gate a reachable per-label escape. This run did NOT weaken the floor and
  did NOT use `--no-verify`, because either would revoke the push grant itself.
  Two commits are landed locally, fully gated, and unpushed pending this. Every
  other gate is green: the final push attempt reported `85 passed, 1 failed`
  with `check-runtime-budget` as the only failure.

Open, and inherited:

- `#561`'s equality-versus-invariant probe pin. Both costs are already measured in
  a predecessor's queue. If it is consolidated rather than decided, say so on the
  issue.
- Premise-residue: `#561` — an operator decision is open on it (equality-versus-invariant
  probe pin), inherited from a predecessor's queue and not taken in this goal. Refuse to
  recommend closing it until that decision is recorded.

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

### Slice 1: Slice 1 — retire the constraint nobody chose

- Objective: Stop `docs/prompt-mutation-policy.md` from governing ordinary editorial deletion and compaction of prompt surface, keeping its evidentiary rule inside the mutation-experiment pipeline where it was actually chosen. Close `#521` citing the operator ruling, and close `#519`/`#520` as a cadence question owned by `../cautilus`.
- Why this approach: The Slice Plan named this a cut vertex: a prior goal parked "may `AGENTS.md` be physically shrunk" underneath an unarmed agent-authored document, so slices 3 and 4 could not use compaction moves until the reach was cut. Cheapest available unblock.
- Commits: `ac019102` docs: scope the prompt-mutation policy to its own verdicts
- What changed: `docs/prompt-mutation-policy.md` gained a `## Scope: this governs the pipeline's verdicts, not editing` section recording the operator ruling with its date and reasoning, and the demote-never-delete section was retitled to say it is about the verdict, not about the editor. The goal artifact carried the shaping.
- Alternatives rejected: Deleting the policy outright was rejected: its evidentiary rule ("a survival verdict is not a deletion proof") is still true inside the experiment pipeline, so the correct move keeps the meaning and cuts the reach. Relabelling `#521` as a question was rejected because the operator had already ruled.
- Targeted verification: Tracker readback rather than record trust — the goal's own thesis applied to its own slice. `gh issue view` reports `#521` CLOSED 2026-08-09T17:35:28Z, `#520` CLOSED 2026-08-09T17:35:29Z, `#519` CLOSED. `gh issue list --state open` now returns 22, down from the 25 recorded in `## Backlog Recount`. The Scope section is present in the working tree at `docs/prompt-mutation-policy.md`.
- Test duplication pressure: n/a — no tests added or expanded; this slice changed one docs surface.
- Critique: Deferred to the slice-2/3 boundary: the policy retirement is a docs-scope change with no executable verdict surface, and the goal's Agent Verification Plan binds its bounded fresh-eye round alongside the consolidated-close disposition, which IS a proof surface. Recorded here so the obligation is not lost.
- Off-goal findings: None filed.
- Lessons carried forward: This slice landed before activation and was re-verified against the tracker rather than believed from the commit message — the exact discipline slice 2 is about to make executable. The recount in the goal artifact is now stale by three issues, which is itself evidence for slice 2: a hand-written count decays the moment work lands.
- Metrics:

### Slice 2: Slice 2 — make backlog re-verification executable, as an extension of the recount seam

- Objective: Answer "is this issue still true?" in one command instead of a reading session: emit a typed premise state per open issue from the `achieve` recount seam, and STOP — never close an issue, never recommend closing one.
- Why this approach: It shrinks the denominator for slices 3 and 4, and it is the durable answer to an append-only backlog. Building it later would mean consolidating issues nobody re-checked. It is also the originating issue's part 2, which the tracker-backend consolidation had unblocked.
- Commits: pending — this slice's commit lands with this log entry
- What changed: NEW `skills/public/achieve/scripts/recount_premise_state.py` (tracker seam + report envelope), `recount_premise_lib.py` (verdict typing), `recount_residue_lib.py` (structural residue detection). `references/lifecycle-before.md` gained the routing and the marker contract. `skills/public/quality/references/attention-state-visibility.json` declares both new skipped-state surfaces. `charness-artifacts/quality/dup-review.json` classifies three loader/idiom families. `docs/public-skill-dogfood.json` records the review for `achieve`, `issue`, `quality`. Generated `plugins/` mirror synced. Two OFF-SLICE proof-surface repairs came from a sweep this slice provoked and are recorded under Off-goal findings.
- Alternatives rejected: REJECTED — a second backlog reader inside `achieve`: the originating issue names that as the wrong repair, so the tracker goes through the `issue` skill's `issue_backend.resolve_op`/`run_backend`, the contractual owner. REJECTED — importing `handoff`'s `list_open_issues`: it is gated behind the handoff adapter's optional `issue_source:` block, so a host disabling handoff pickup would silently disable this too, and a floor another skill's adapter can switch off is not a floor. REJECTED — a two-state `premise-holds`/`premise-refuted` typing: the motivating instance was genuinely refuted and still must not close. REJECTED, AFTER BUILDING IT — inferring a decline from record wording: see Critique.
- Targeted verification: 61 tests in `tests/test_recount_premise_state.py`, seeded in both directions so a constant-answer tool fails. LIVE MARKER ROUND-TRIP against this repo's 22 open issues: a `Premise-residue:` marker written into a durable record produced exactly one refusal citing that marker's path and line, with the other 21 clean. `run_slice_closeout.py --skip-broad-pytest` structural sweep green after declaring both skipped-state surfaces. Dup ratchet OK (0 new fixable families). 707 issue-lane tests green after the off-slice repairs. Broad `pytest tests/` run at the slice boundary.
- Test duplication pressure: `check_dup_ratchet.py --repo-root . --summary` run three times during the slice. It first reported 8 new fixable families; 5 were removed by real deduplication (collapsing two module loaders into one, delegating the backend runner to the `issue` skill's owner, collapsing two one-line accessor wrappers the ratchet named immediately), and 3 were classified `intentional` in `dup-review.json` with reasons. Final state OK, `fixable_ceiling=0 <= floor_F=0`. The advisory hook fired on every write and was acted on inside the slice rather than at closeout.
- Critique: TWO bounded fresh-eye rounds, both unnamed and read-only, both boundary-verified clean with `reviewer_boundary_fingerprint.py`. This is verdict logic on a proof surface, so the second round was owed and it earned itself. ROUND 1 confirmed the typing (caller-supplied judgement, bare-mention-is-not-residue, never-recommends-close all survived attack) and found four recall defects, each producing the close-leaning state on evidence a human reads as "do not close": line-scoped matching missing wrapped declines, a truncated root list, a silent empty scan, and an unread body silently meaning "no further ask" while the reason string asserted the body was clear. ROUND 2 read the REPAIRS and found what round 1 could not: the repairs' own defects. Measured, not asserted — with all 22 issues judged refuted, 21 refused, i.e. the tool had become a constant. Root cause was a CATEGORY ERROR: this repo's own recount floor REQUIRES a `Not claimed:` bullet naming the issues a goal does not take, and "this goal is not taking it" says nothing about closability; one such bullet reads "closable now" of the very issue the scanner was citing as evidence not to close. Round 2 also found JSON/JSONL collapsing into one block, `files_scanned == 0` not being a channel gap, and F4 reopened at the CLI seam via `.get("body") or ""`. THE OPERATOR THEN REFUTED THE WHOLE APPROACH, and correctly: the decline vocabulary was repo-specific English/Korean hardcoding inside a PORTABLE skill, and the proximity windows had been fitted by watching this repo's clean count go 1, 3, 7, 10 across successive tunings — a verdict surface fitted to its own test set, which is the defect this goal family exists to remove, arriving inside the tool built to remove it. All prose matching and all fitted constants were deleted.
- Off-goal findings: A bounded read-only sweep for the same defect class across `skills/public/**`, `skills/support/**`, `skills/shared/**` found ~11 instances in ~326 files — present but not widespread, clustered in the achieve closeout floors and the issue closeout observer. Three were fixed IN THIS SLICE at the operator's instruction rather than filed. (1) `issue_critique_observer._denies_delegation`: an English negation list inside a 24-character window, the span narrowed until this repo's corpus looked right. MEASURED: `no fresh-eye reviewer was available, so nothing parent-delegated ran` returned `delegated`, permitting an issue close asserting a review nobody ran. Repaired to clause-scoped negation using punctuation boundaries; also catches right-side negation (`never ran`) that no leading window could, and a paragraph break is now a clause boundary. A leading-token test was considered and REJECTED on evidence (ten artifacts use `satisfied — parent-delegated ...`). Residual English-only limitation stated in the module, not hidden. (2) `goal_artifact_coordination_floors._RELEASE_SURFACE_TOKENS`: four of this repo's own script/artifact names gating the release coordination floor, making it silently inert in every consuming repo — worse than no floor, because it reads as coverage. Repaired with ecosystem-standard version manifests and publish commands plus an adapter-declared `release_surface_tokens` seam. (3) `issue_closeout_ledger_counts`: a comment named `unif*` as a known miss and the code never carried it, so `Four implementations, three unified.` passed a floor that refused the synonym `three consolidated.`; the fitted `{0,80}` clause cap is also gone. Surfaces confirmed CLEAN are recorded in the sweep, including `goal_artifact_disposition_grammar`, which documents the word-list trap in-file and matches structure only.
- Lessons carried forward: The round that reads the REPAIRS catches a different class than the round that reads the original — round 2's finding inverted the tool's value and round 1 could not have seen it, because it did not exist yet. Measure a heuristic's output distribution before believing it: 21-of-22 refusals looked like caution and was a constant. And the strongest signal that a threshold is fitted is that you can narrate the sequence of values you tried — if the number came from watching the output, it is a fit, not a contract. Slice 3 inherits a working but EMPTY record channel: historical records carry no `Premise-residue:` marker, so consolidation must write markers as it goes rather than expecting the tool to recover intent from prose.
- Metrics:

### Slice 3: Slice 3a — the `consolidated` disposition (the closes themselves are NOT run)

- Objective: Answer the question this goal said slice 3 forces: what closeout floor applies to a close that claims NOTHING about the defect, only that it moved. Add `consolidated` as a sixth classification that swaps the resolution floor for its own machine-verifiable one.
- Why this approach: It had to exist before any member could move. Both existing branches cost the floor its meaning: the resolution branch demands `Implementation:` and `Prevention:`, so satisfying it means writing sentences that are not true, and the exempt branch would misclassify the issue while opening a path where any inconvenient bug reaches the light floor by relabelling.
- Commits: pending — lands with this log entry
- What changed: NEW `skills/public/issue/scripts/issue_consolidated_closeout.py` (the disposition's own floor) and `issue_closeout_classification_ledger.py` (one table of what each classification owes, extracted because the new branch created a second dispatch on the same key). Wired through `issue_verify_closeout_body.py`, `issue_verify_closeout.py`, `issue_validate_closeout_draft.py`, `issue_close.py`, `audit_brief.py`, `scripts/check_issue_closeout_commit_msg.py`, plus the author-facing `SKILL.md` and `issue_plan.py`. 30 tests in `tests/quality_gates/test_issue_consolidated_closeout.py`.
- Alternatives rejected: REJECTED — reuse `question`/`decision-needed`: floor-exempt, so it would both misclassify the issue and open a one-word relabelling path to the lightest floor. REJECTED — reuse a resolution classification: a consolidation implements nothing, so meeting that floor means writing false sentences, and a floor met by writing false sentences is worse than none because the false sentences become checked-in evidence. REJECTED, AFTER BUILDING IT — deriving the repair-claim set from the resolution rows: it over-refused (see Critique).
- Targeted verification: 30 focused tests plus 1086 across the issue lane. Every refusal exercised against the wired path (`_missing_ledger_fields`), not only the module's direct call — round 2 showed that distinction was load-bearing, because three checks passed their direct-call tests while never firing where the carrier actually runs. Gate aggregate green; dup ratchet OK; broad suite at the slice boundary.
- Test duplication pressure: One new fixable family (two refusal messages sharing a join-and-append shape) classified `intentional` with its reason rather than abstracted: they name different subjects, cite different lists, and prescribe different remedies, so a shared builder would parameterize three prose fragments to save one line and make both refusals harder to read at the moment someone is blocked by them.
- Critique: TWO bounded rounds, both boundary-verified clean, and round 2 again found what round 1 could not. ROUND 1 found the classification UNREACHABLE: it was in `KNOWN_CLASSIFICATIONS` and the ledger table while every live carrier still refused it, and the commit hook's `_infer_classification` fell through to `bug` — so the only path that worked demanded exactly the repair claims the disposition exists to forbid. It also found `REQUIRED_CLOSE_REASON` read by nobody, and the self-reference check never firing on the wired path. ROUND 2 read those repairs and found the seams they left. (a) The close-reason floor was only half real: `issue_close` enforces it, but the PRIMARY carrier is GitHub auto-closing from a keyword, where no reason argv exists — and the module's own recommended neutral `Closes` produces the same public `completed` event. Repaired by refusing the auto-closing carriers outright. (b) Splitting presence and arity between two owners left a seam: `Consolidated into: the umbrella issue` satisfied the presence owner (a substantive string) while the arity owner had been told to stay silent about absence, so the one fact this disposition exists to require went unrequired. (c) The self-reference check compared only the first close-keyword number, so in the intended shape — one carrier closing twenty issues into an umbrella — the destination could be one of the other nineteen. (d) Fence stripping, correct for field reads, re-opened the documented fenced-`Fixes` evasion, which GitHub still honours. (e) The derived claim set over-refused: `Root cause:`, `Siblings:` and `Boundary:` are diagnostic or scoping, an unfixed issue can carry all three, and consolidating a cluster IS a sibling search — so the most natural honest sentence was being refused. The claim predicate is now what it always meant, an assertion that something was BUILT.
- Off-goal findings: `#580` filed: `check-seed-fixture-budget`'s 1000ms budget measures runner contention rather than the 0.06s check, and it refuses every push. Two hypotheses were tested and refuted (machine load; accumulated pytest scratch). The operator-granted push and release for the slice 1+2 bundle are blocked on it, and this run did NOT weaken the floor or use `--no-verify`, because either revokes the grant.
- Lessons carried forward: The pattern held a third and fourth time: the round that reads the REPAIRS finds a different class than the round that reads the original, and every one of round 2's findings lived in a seam the repair itself created. Two of them share one shape worth naming — a check that passes its own direct-call test while never firing on the wired path — which is this goal's originating defect in miniature: a record (the green test) treated as a fact about a path it never exercised. The remedy applied here is that every refusal is now tested through `_missing_ledger_fields`, the way the carrier calls it. NOT DONE, and deliberately: the ~20 member closes, the umbrella issues, and the four backend readbacks (destination exists, is OPEN, contains this issue's number, no chains) are unimplemented. Slice 3b owes them, and it must not run a single close until they exist.
- Metrics:

### Slice 4: Slice 3b (part 1) — the four tracker readbacks the disposition named and nobody implemented

- Objective: Make the four facts a consolidated close depends on actually checkable against the tracker: the destination exists, is OPEN at close time, its body names the issue moving into it, and it is not itself a consolidation.
- Why this approach: Slice 3a's disposition listed them under `not_checked_here` and implemented them nowhere, which a bounded reviewer named for what it also was — four checks whose only effect was to appear in a JSON payload no consumer read. To a downstream operator that reads like handled work. Until they exist, a destination could be closed, nonexistent, or silently not mention the issue that moved into it, and no close may run.
- Commits: pending — lands with this log entry
- What changed: NEW `skills/public/issue/scripts/issue_consolidation_readback.py` (the four checks, pure over a fetched payload, plus the per-closeout loop) and `issue_state_readback.py` (the backend state read, extracted from the verifier because two consumers now need it and the verifier was at its length cap). Wired into BOTH `issue_verify_closeout.py` and `issue_close_comment_floor.py`/`issue_close.py`. 21 tests in `tests/quality_gates/test_issue_consolidation_readback.py`.
- Alternatives rejected: REJECTED — leaving the four as documented non-goals: a list of unimplemented checks in a payload reads as coverage, which is the defect class this goal exists to remove. REJECTED — checking them only in `verify_closeout`: that is the carrier an operator runs AFTER the close, so 'the destination is OPEN at close time' would first be evaluated once the irreversible act had already happened.
- Targeted verification: 21 focused tests plus 1104 across the issue lane; broad suite at the slice boundary. The `not_checked_here` list is now backed by executing code, and the reviewer's one unfetchable item was answered directly: `git show HEAD:...` diffed against the extracted module proves `view_issue_state` is byte-identical to the `_view_issue_state` it replaced apart from the rename.
- Test duplication pressure: One new fixable family — the standalone-script import preamble, shared with `issue_runtime.py` — classified `intentional`: it exists precisely because these files are executed directly as often as imported and the export flattens the layout, so a shared preamble would itself need loading by the same preamble. Its id rotated once mid-slice when a neighbouring comment changed, which is the known content-addressed rotation rather than a new family, and the note records that.
- Critique: One bounded round on this surface, boundary-verified clean, and it found the same shape a third time. THE HEADLINE: the readback ran in `verify_closeout` but NOT in `close-with-comment` — which is the one carrier a consolidated close is REQUIRED to use, because it is the only path that passes `--reason 'not planned'`. So the carrier a consolidation must use was the one carrier checking neither its destination grammar nor whether that destination exists. The close floor's own comments already name this asymmetry twice for HOTL and AI-provenance; this was the third instance. ALSO FOUND: (a) the readback never checked that the payload described the destination it ASKED about — the sibling expected-state loop already does this and records why ('being told is not obeying, and a wrong-repo answer carries the RIGHT number'), and without it a cross-repo anchor would be fetched against the source repo where an unrelated same-numbered issue could pass all four checks; (b) a truthy non-dict payload escaped as an AttributeError traceback, contradicting the module's own rule that any backend failure is 'did not run'; (c) failure amplification — twenty closes into one bad umbrella produced ~40 byte-identical lines that buried every other finding, because three of the four facts are destination-scoped and were re-emitted per source. All repaired with regression tests. NOT REPAIRED, recorded instead: the chain check is near-inert against real chains (a consolidated destination is CLOSED, so check 2 catches what check 4 claims to) and can false-positive on an umbrella that documents the convention in a fence.
- Off-goal findings: None new. `#580` still blocks the operator-granted push and release.
- Lessons carried forward: Three surfaces in this goal have now shipped a check that existed and never ran: the premise-state channels, the `consolidated` classification itself, and now these readbacks. The tell is identical each time — a green test exercising a DIRECT call while the wired path never reaches the code — so the durable remedy applied here is that every check is tested through the surface an operator actually invokes, including one test that asserts a backend call was made at all. That is the same defect this goal was designed from, arriving three more times inside the work meant to remove it.
- Metrics:

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

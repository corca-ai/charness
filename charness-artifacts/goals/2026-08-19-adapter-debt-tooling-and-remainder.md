# Achieve Goal: Build the tool the review rounds paid for, then finish the adapter-consumer corpus

Status: complete
Created: 2026-08-19
Activation: `/goal @charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **none — the run is closed.** Slices 1 (`#674`), 2 (`#673`) and 3 (`#675`)
  landed, each with the two bounded rounds the proof-surface rule requires, all folded.
- **Two of five `## User Acceptance` items are NOT met and one is partial.** The per-item
  verdict and the command that answers each are in `## User Verification Instructions`.
- **Slice 2 produced a live example rather than a hypothetical one.**
  `scripts/refresh_current_pointer.py` refuses through its loader and no longer guards
  itself, so it is recorded `accepted-risk-unguarded` with the mechanism in prose — which
  inflates the accepted-risk count by one and is exactly the measurement distortion `#675`
  reports. It is the migration's first test case.
- **HALTED BEFORE SLICE 4 under the Slice Plan's own stop rule.** Slices 1-2 overran: SIX
  bounded rounds across NINE reviewer reports, and three of those rounds found defects the
  repairs themselves introduced. Slice 4 and slice 5 go to
  `charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`.
- Recount, never read off this file:
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .` — SEVENTEEN rows
  remain unpaid at closeout (`accepted-risk-unguarded: 6` + `no-version-validation: 11`), not
  the nineteen the Slice Plan projected before slices 2 and 3 moved rows in both directions.
- No `Timebox:` field: the operator set no fixed duration, so the timebox clock does not
  apply. The Slice Plan's own stop rule (halt BEFORE slice 4 if slices 1-2 overrun) was the
  only bound, and it fired — slices 4 and 5 go to the successor goal.
- Activation time: 2026-08-19T03:30Z
- Closeout reserve: one slice boundary's worth, held and spent. The retro, the closeout
  binding and the push readback are work, not follow-up.
- Done-early policy: continue_next_improvement.
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

Build the mechanical detector that thirteen bounded review rounds paid for by hand, then
spend it: close the resolver split that keeps every consumer guard blind on two of its
three doors, and finish the adapter-consumer corpus with the remaining nineteen rows.

The predecessor goal proved the probe mechanism on twenty-six real rows and drove
`accepted-risk-unguarded` from 37 to 11. It also measured its own cost: EVERY review round
found something, and by the second half almost everything they found was a CLAIM defect
rather than a code defect — four probe records shipped a polarity control that could not
fail, and a refuted sentence was re-published into eight surfaces. All of it was visible
from data already inside the artifacts. None of it was caught by a tool.

This goal's thesis is the predecessor's own retro conclusion: the language and the habits
improved, the TOOLING did not, and continuing to pay rows without closing that gap buys
another ten review rounds spent on prose.

## Non-Goals

- **Not a re-litigation of the twenty-six paid rows.** Their probe records, census reasons
  and review folds stand. Re-measuring them is out of scope unless slice 2 changes what a
  guard can see, in which case the affected records are corrected rather than re-derived.
- **Not the three operator decisions** staged in the predecessor's `## Operator Decision
  Queue` (planner diagnostic, `#628`, the seeded-verdict pair). They stay there and stay
  the operator's; this goal does not decide them and does not wait on them except where a
  slice explicitly says so.
- **Not slice 4's no-increase ratchet.** It is blocked on the seeded-verdict ruling, and
  ratcheting over a possibly mis-seeded row freezes the mis-seeding. Naming it here does
  not unblock it.
- **Not a release.** No version bump, no publish, no tag.

## Boundaries

- **Push: ONE push, at the END of the goal, after the closeout retro.** Granted by the
  operator on 2026-08-19 (`## Discuss Before Activation` (b)). Phase-scoped to that
  boundary: it does NOT authorize a per-slice push, and it is not re-usable if the goal
  stops early — an early stop needs its own grant. A distinct-channel hosted readback is
  required, as it was for the predecessor.
  **RE-CONFIRMED by the operator on 2026-08-19 at the closeout phase**, after the stop rule
  fired. The original grant was written for a five-slice completion; this run stops after
  three, so the re-confirmation is what makes the push authorized rather than inherited.
- **Everything before that boundary lands locally.** An ahead-of-origin count during the
  run is expected and is not a defect to fix.
- **Issue filing is standing-approved. Issue CLOSING is not**, and this goal expects to
  close `#673`, `#674` and `#675` — each needs the `issue` closeout floor and a
  phase-scoped grant, never inferred from a green gate.
  **GRANTED by the operator on 2026-08-19, at the closeout phase, for exactly these three
  issue numbers.** Scoped to this closeout: it does not authorize closing any other issue,
  and it does not survive into the successor goal. Each close still runs the `issue`
  closeout floor first; the grant removes the approval blocker, not the proof floor.
- **No release, no tag, no version bump, no Cautilus evaluation.** If any becomes
  necessary, it stops and asks.
- Slice 1 changes `check_probe_record` — a PROOF SURFACE that renders a verdict about
  other evidence. Slice 2 changes six resolvers every skill reads. Both carry the
  two-round bounded review floor by the operating contract, not by choice.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

1. **A probe record whose reproduction steps do not reproduce is refused.** Run
   `check_probe_record.py --require-evaluated` against a record whose `## Stimulus` no
   longer produces its recorded `## Base observable`, and against one whose two arms
   produce identical output; both resolve `not-established` naming the diff. The four
   records this goal's predecessor shipped with dead controls are the regression corpus,
   available in git history.
2. **All sixteen public resolvers answer a malformed adapter the same way.** Run each
   `resolve_adapter.py` against `version: !!int 9` and against a stray-indent document;
   every one renders a verdict rather than a traceback, and every one records the dropped
   line where a consumer guard can see it.
3. **`adapter_version_verdict.declarations_dropped` is reachable for all sixteen**, so a
   consumer guard's claim to refuse when the reader honored nothing is true everywhere
   rather than for ten of sixteen.
4. **The census answers "how much of this debt is actually closed"** without reading prose
   reasons — `guarded` no longer means four different coverage levels.
5. **The 45-row corpus is finished**: every row is `guarded`, or carries a recorded
   decision naming why a guard there is wrong or impossible, with its caller coverage
   measured.

What the user can do to verify completion directly — the OUTCOMES, not the
verification cadence. Whichever line of `## Active Operating Frame` states when
broad or expensive proof runs (`Gate cadence:` in the charness default frame; a
consumer adapter may seed its own) is the one owner of that answer. Restating it
here creates a second owner, and an agent reading its own acceptance criteria
obeys the acceptance criteria: one measured session paid roughly two and a half
hours re-running a 12-minute suite that way. Name what is true when the goal is
done, and point at `## Active Operating Frame` for when it is proven.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`
  at every commit boundary.
- `python3 scripts/check_adapter_consumer_classification.py --repo-root .` — recount, never
  read a count off prose.
- `python3 scripts/check_probe_record.py --record <path> --require-evaluated` for each
  record touched.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  AFTER each slice commit and BEFORE the broad lane. `no-verdict` is not a pass.

### High-Confidence Checks

- `python3 scripts/run_standing_pytest.py` at slice boundaries.
- `python3 -m pytest -q -m release_only` at bundle boundaries.
- TWO bounded `bounded-reviewer` rounds per slice, spawned UNNAMED and read-only, with
  `reviewer_boundary_fingerprint.py` snapshot/verify around each. Slices 1 and 2 both
  change verdict logic on a proof surface, so the second round is owed by contract; a
  first round producing no repairs discharges it.
- Mutation proof for every new refusal: delete the guard, name the test that fails, revert.

### External Or Live Proof

- Push, with a distinct-channel hosted readback (GitHub API, not the local ref).
- Issue closeout for `#673` / `#674` / `#675` through the `issue` floor, each with a
  phase-scoped grant.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `#674` — `check_probe_record --replay-stimulus` replays the adapter declarations a record's `## Stimulus` writes and refuses the ones no reader honors | Every claim defect this corpus produced was visible from data already in the record, and none was caught by a tool | Six published dead controls refused at their original documents and passing at their corrected ones; a FIFTH record's dead control found that no review round had; all thirteen records pass the sweep gate | done (`a12ba86f5`) |
| 2 | `#673` — the FIVE resolvers that call `load_yaml_file` bare route through the reporting loader (`announcement` was already repaired; measured, not read off the issue) | Until this lands, `parse_refused` and `declarations_dropped` are structurally dead for six skills, so every consumer guard there is one-door | All sixteen resolvers render a verdict for a parse refusal and record a dropped line; one test sweeps all sixteen | done (`e54132c47` + folds) |
| 3 | `#675` — a census verdict vocabulary that distinguishes coverage levels, with a witness that checks the level | `guarded` now means four things and the gate sees one; slice 2 changes which rows qualify for which | Per-level counts printed; existing rows migrate with measured evidence, none upgraded without a measurement | done (`a21e0d0d3` + round-1 fold) |
| 4 | The remaining nineteen rows — NOT STARTED, stopped by the Slice Plan's own rule | After slices 2-3 a row's coverage is uniform and legible, so the per-row claim stops needing a paragraph of caveats | Each row `guarded` or carrying a recorded decision with measured caller coverage | handed to a successor goal |
| 5 | Slice 6 of the predecessor: two-round bookkeeping as typed critique fields; `#628` to the operator queue | The obligation is currently remembered, not recorded | Typed fields; `#628` staged with its design call | handed to a successor goal |

Slices 1-3 are the tooling arc and slice 4 is the payoff. **If slice 1 or 2 overruns, the
honest stop is BEFORE slice 4**, not partway through it: nineteen rows measured under a
half-built detector is the shape this goal exists to avoid.

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: 27 open issues on 2026-08-19 via `gh issue list --repo corca-ai/charness --state open`.
  Three of them (`#673`, `#674`, `#675`) were filed by the predecessor goal and are this
  goal's slices 2, 1 and 3 respectively.
- Claims: `#674` (slice 1), `#673` (slice 2), `#675` (slice 3). Each is claimed for
  RESOLUTION; closing any of them needs the `issue` closeout floor and its own
  phase-scoped grant. `#550` ("Adapter resolver bodies are near-identical") is the same
  family as `#673` and is expected to become closeable or narrowable by slice 2 — claimed
  only as a re-read, not as a close.
- Not claimed: the remaining 23. `#628` is staged as an operator design call in the
  predecessor's queue and slice 5 only moves it, never closes it. `#672`, `#599` and the
  three umbrellas `#582`/`#583`/`#584` sit adjacent to this work but none was verified as
  still true here, and counting is not re-verifying.

## Operator Decision Queue

RAISED BY THIS RUN:

- Decision: 55 rows carry `safe-checks-errors`, and that token now covers materially
  different coverage the same way `guarded` did before slice 3 split it. Four of them
  (`proof_mismatch`, `cautilus_scenarios_lib`, `plan_cautilus_proof`,
  `control_plane_lifecycle_lib`) read through `cautilus_adapter_lib` /
  `proof_semantics_adapter_lib`, which still call `load_yaml_file` bare, so two of the three
  doors are structurally dead for them; the rest sit behind full-reporting resolvers. Owner:
  repo operator. Why deferred: splitting the largest class is a slice of its own and this
  goal stopped at its own rule. Unblock action: rule whether `safe-checks-errors` gets the
  same level treatment, or whether those two libraries should simply be routed through
  `read_declared_adapter` (which would make the question moot). Revisit trigger: the
  successor goal, or any change to either library. Found by a round-1 bounded review of
  slice 3.


- Decision: `User Acceptance 1` names the bare `check_probe_record.py --require-evaluated`
  as the command that must refuse a non-reproducing record. It does not; the working
  command is `--replay-stimulus --require-evaluated`. Owner: repo operator. Why deferred:
  proceeding either way is safe and blocking would stall the whole goal, so slice 1 shipped
  the opt-in form and recorded the deviation. Unblock action: rule whether the replay should
  join the `--require-evaluated` path. Consequence recorded rather than softened — the
  issue-close and release closeout floors call this CLI, so folding it in makes every close
  boundary run up to sixteen resolver subprocesses per record, and executing a record's own
  declarations at a close is a cost those floors did not ask for. The corpus sweep gate
  (`tests/quality_gates/test_probe_record_corpus_replays.py`) is the standing-lane
  substitute that keeps the detector from being inert either way. Revisit trigger: the first
  probe record authored after this goal, or any change to the issue-close floor.

INHERITED, and deliberately NOT re-decided here — these stay the predecessor's and stay
the operator's:

- Decision: should `plan_retro_run` / `plan_debug_run` keep their diagnostic plan under an
  unhonored declaration, or is the one-line refusal right for that input class? Owner:
  repo operator. Why deferred: it is a design call, and the current shape is pinned by
  test so it cannot drift silently. Unblock action: rule keep-refusal or restore-plan.
  Revisit trigger: slice 4 touching either planner.
- Decision: `#628` — does quality's same-day scaffold overwrite stay or go? Owner: repo
  operator. Why deferred: design call, and closing `#628` either way is irreversible.
  Revisit trigger: slice 5.
- Decision: the contestable seeded verdict pair
  (`reconcile_usage_episodes_host_hooks.py` vs `quality_label_universe.py`). Owner: repo
  operator. Why deferred: ratcheting over a mis-seeded row freezes the mis-seeding.
  Unblock action: rule which verdict is correct. Revisit trigger: any attempt to build the
  no-increase ratchet — which this goal does NOT attempt.

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

- `Phases: impl, quality, critique, retro`
- `Routing: charness:achieve — the goal operator for the whole run; it coordinated impl for
  the three slices, quality for the gate cadence and the duplicate ratchet, critique for the
  six bounded rounds, and retro at closeout, without absorbing any of them.`
- `Gather: n/a — this goal read no external URL, Slack, Notion, Doc or Drive source; every
  input was a checked-in artifact, a GitHub issue body already quoted in the goal, or a
  measurement this run made itself.`
- `Release: n/a — no version bump, no install-manifest edit, no tag and no publish. The
  Boundaries section forbids all four and none became necessary.`
- `Issue closeout: #673, #674, #675 are RESOLVED but NOT CLOSED. Closing is not standing-
  approved and this run has no phase-scoped grant for it, so no carrier was drafted and
  issue_tool.py validate-closeout-draft / verify-closeout were not run. The resolutions and
  their proof are in ## Slice Log; the close is the operator's to grant.`
- `Successor goal: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md (draft; it also
  carries this goal's unfinished slices 4 and 5)`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED 2026-08-19 by the operator, on both surfaced
  decisions.

  **(a) Scope — RESOLVED: all five slices.** The operator chose the full arc: three
  tooling slices, the remaining nineteen rows, and the predecessor's slice 6. The
  alternative considered and rejected was cutting at slice 3 and letting a successor claim
  the rows; what settled it is that the context for WHY each remaining row remains is
  currently written down in one place and is expensive to rebuild. **The Slice Plan's stop
  rule survives this decision and is not softened by it**: if slices 1-2 overrun, the
  honest halt is BEFORE slice 4, not partway through. Claiming five slices is a scope
  decision, not a promise to finish them at any cost.

  **(b) Push cadence — RESOLVED: ONE push, at the end.** Per-slice push was considered
  because this goal touches six resolvers and a proof surface, and was rejected by the
  operator. Consequence recorded rather than softened: every intermediate state stays
  local, so a mid-goal handoff to another machine has nothing on the remote to pick up,
  and the single push carries the whole arc at once. `## Boundaries` holds the grant.

## Slice Log

### Slice 1: Slice 1 — `#674`, the stimulus-replay detector

- Objective: Build the mechanical detector thirteen bounded review rounds paid for by hand: replay the adapter declarations a probe record's `## Stimulus` writes and refuse the ones no reader honors.
- Why this approach: Every claim defect this corpus produced was visible from data already inside the record, and none was caught by a tool. Building it before paying more rows was the goal's own thesis.
- Commits: `687a1e86b` (detector + two record corrections), `fb54e488b` (verdict for an outright-refused construct + coverage), `567a4b947` (round-1 fold), `a12ba86f5` (round-2 fold + module split).
- What changed: NEW `scripts/probe_stimulus_documents.py` (shell/heredoc grammar and text surgery) and `scripts/probe_stimulus_replay.py` (resolve and judge), split on the concept boundary `probe_record_lib`/`probe_record_parse` already uses. `check_probe_record.py` gains `--replay-stimulus`; `probe_record_lib` gains `demoted_result` so the merge has one construction site. NEW `tests/test_probe_stimulus_replay.py` (63) and `tests/quality_gates/test_probe_record_corpus_replays.py` (the standing-lane corpus sweep). Corrected: the `release-planner` and `scaffold-family` probe records, and `tests/quality_gates/test_release_planner_version_refusal.py`, which still declared the dead key. Two dup families classified `intentional`.
- Alternatives rejected: REJECTED: replay the CLI half of the stimulus and diff against `## Base observable`, which is what `#674` literally asks for. It is defeated by the PARTIAL dead control this corpus actually produced — the quality record's dead control flipped three of its five CLIs — and again by volatile bytes, and it would execute a record's own shell at a proof surface. REJECTED: fold the replay into `--require-evaluated`, because the issue-close and release floors call that path and would silently acquire sixteen subprocess resolves. Recorded in the Operator Decision Queue as a deviation from User Acceptance 1's literal command.
- Targeted verification: `run_slice_closeout.py --skip-broad-pytest` at every commit boundary (four, all exit 0); `prepush_focused_changed_line_coverage.py --refuse-unestablished` after each commit and before the broad lane (clean); coverage measured at 115/115 and 133/133 rather than inferred from passing tests; TWELVE mutations across the three rounds of repair, each naming the test that failed. The corpus sweep is the standing-lane witness that the detector runs at all.
- Test duplication pressure: `check_dup_ratchet.py --summary` at each boundary. Two new families, both classified `intentional` with measured notes: `a2a04eacbcea76ec` (argparse CLI entrypoint boilerplate across seven gates) and `1bca07c734ac01f8` (a two-line `if <mapping>.get(<key>): return <verdict>` guard clause across four unrelated classifiers, the same family as the already-classified `003780cc89f2ccfd`). Ratchet clean at the close.
- Critique: TWO bounded rounds, two reviewers each, all spawned UNNAMED and read-only as `bounded-reviewer`; `reviewer_boundary_fingerprint.py` snapshot/verify around each window, both `ok: true` / `clean`. NEITHER ROUND WAS CLEAN. Round 1 found the detector defeatable five ways and INERT — nothing in the repo ran it, so `#674`'s own premise held for record fourteen — plus nine claim defects including a test corpus whose docstring claimed `verbatim` for a constant never published in any form. Round 2 found THREE of round 1's six repairs carrying the class they repaired: the variant generator emitted a flow sequence, then suffixed an inline comment the reader strips back off, then produced type-invalid values for booleans, floats, quoted and block scalars; and the per-line ablation the nesting repair introduced called YAML document markers declarations. It also found the demotion merge to be a THIRD hand-rolled construction of a shape whose single-owner rule is recorded forty lines above it. Per the two-round cap, the round-2 repairs are ACCEPTED-UNREVIEWED: no third round read them.
- Off-goal findings: The detector measures whether the RESOLVER honors a declaration, not whether any consumer READS it. A field that passes nested keys through verbatim (`command_timing_log`, `host_extensions`) makes an unread key change the payload, so it reads live. `scripts/adapter_key_registry.py` already answers the reader question without a subprocess; wiring it in is unmade and is recorded in the module's blind class rather than filed, because slice 3 changes the census surface that would consume it.
- Lessons carried forward: A detector's first version is a hypothesis about its own blind class, and the fastest way to test it is to hand a reviewer the mechanism and ask only `what is the cheapest input that still gets past this`. Both rounds answered with inputs the author could not see. The sharper one: EVERY generator this slice wrote — the variant, the ablation, the extraction — reproduced the defect class it was built to detect, three times in a row. A tool that constructs inputs for a reader must be checked against that reader's own parser, not against the author's model of it.
- Metrics:

### Slice 2: Slice 2 — `#673`, one answer from all sixteen resolvers

- Objective: Make every public resolver answer a malformed adapter the same way, so `adapter_version_verdict.parse_refused` and `declarations_dropped` stop being structurally dead for the skills whose libraries called `load_yaml_file` bare.
- Why this approach: Until this landed, two of the three doors every consumer guard reaches through were unreachable for five skills — the predicates answered False for exactly the inputs they were written to catch, and no test could see it because the resolver never returned.
- Commits: `d6f19aab2` (the repair), `eedb6a540` (parser coverage, two dead branches deleted), `a776bd37d` (dup classification), `e54132c47` (round-1 fold), `21849d8e4` and two follow-ups (coverage of the guards the changed-line gate named), plus the round-2 fold.
- What changed: `adapter_lib` gains `read_declared_adapter`, `resolve_declared_adapter` and `resolve_adapter_payload`, and loses this repo's YAML dialect to NEW `scripts/adapter_yaml_parse.py` (re-exported, so no call site changed). Five libraries routed through them. NEW `tests/quality_gates/test_every_resolver_answers_a_refused_document.py` sweeps all sixteen and replaces the per-family branches three files carried; NEW `tests/quality_gates/test_artifact_path_refuses_an_unhonored_adapter.py` and `tests/test_adapter_yaml_parse_branches.py`. Six tests that pinned the old blind behavior flipped; `RAW_TRACEBACK_SKILLS` deleted. Corrected across the repo: `adapter_version_verdict` (three stale docstrings plus a refuted justification), `boundary_probe_lib`'s measured comment, seven census rows, `docs/handoff.md`, and ten dup-review notes.
- Alternatives rejected: REJECTED: normalising the sixteen exit codes, which `#673`'s acceptance asks for. Fourteen exit 0 with `valid: false` and two exit 1; that divergence is not what made a consumer guard blind, and changing it is a behavior change for every caller that branches on the code. Pinned in `NON_ZERO_EXIT_SKILLS` so a move in either direction is a diff. REJECTED: classifying the duplicate families `#673` surfaced instead of extracting them — the convergence IS `#550`'s subject, so `resolve_adapter_payload` was extracted and only the residue classified, each with its own reason. REJECTED: an adoption scan collapsing the two parser module instances, because it makes which instance wins depend on import order.
- Targeted verification: `run_slice_closeout.py --skip-broad-pytest` at every commit boundary; `run_standing_pytest.py` at each slice-shaped boundary (final: 10601 passed, 0 failed); `prepush_focused_changed_line_coverage.py --refuse-unestablished` after each commit and before the broad lane, clean at the close; three mutations on the three doors and one on the unregister arm, each naming its failing test. The sixteen-resolver sweep asks `adapter_version_verdict`'s predicates directly rather than matching message text.
- Test duplication pressure: `check_dup_ratchet.py` at each boundary. Ten new families, all classified `intentional` with per-family reasons: four are the `#550` residue this slice surfaced, four are untouched pairs re-fingerprinted by the module split, one is the parser's two loop preambles, one is the module bootstrap contract. Ratchet clean at the close.
- Critique: TWO bounded rounds, two reviewers in round 1 and one in round 2, all spawned UNNAMED and read-only as `bounded-reviewer`, with `reviewer_boundary_fingerprint.py` snapshot/verify around each window — both `ok: true` / `clean`. NEITHER ROUND WAS CLEAN, and round 1 found a REGRESSION THIS SLICE CAUSED: making five resolvers exit 0 instead of tracebacking removed `resolve_artifact_path`'s only protection, and it began resolving `charness-artifacts/quality/latest.md` over a repo that declared `docs/mine-q`. Round 1 also found twelve claim defects on surfaces someone reads to decide, including the consumer-guard module itself telling readers that six resolvers are blind when zero are. Round 2 then found THREE of those repairs carrying the class they repaired: the census row for the very file the slice repaired still said `accepted-risk-unguarded` with a reason the file refutes; the new guard's dropped-line message glued on a tail that is false for that arm; and the unregister arm's bare `del` reproduced the second-error-hides-the-first shape its own comment names. Round 2's repairs are ACCEPTED-UNREVIEWED per the two-round cap.
- Off-goal findings: `refresh_current_pointer` is now protected by its loader rather than by itself, and the census has no token for that — recorded as `accepted-risk-unguarded` with the mechanism named, which inflates the accepted-risk count by one. That is `#675`'s subject with a live example, and slice 3 is where it gets a name and a witness that checks the level. `proof_semantics_adapter_lib` and `cautilus_adapter_lib` still call `load_yaml_file` bare; they are outside `#673`'s sixteen and are the residual surface.
- Lessons carried forward: A repair that changes HOW a surface fails changes what its consumers can observe, and the exit code is an observable. Nothing in the slice plan asked `who was relying on the old failure mode`, and the answer was a guard whose only protection was a return code. The reusable move is to ask, before any change to a refusal's shape, which consumers key on the SHAPE rather than the condition — and the reusable proof is what the census now records: keyed on the condition, a resolver's exit convention can change again without disarming it.
- Metrics:

### Slice 3: Slice 3 — `#675`, a verdict per coverage level

- Objective: Give the census a verdict per coverage level and a witness that checks the LEVEL, so "how much of this debt is actually closed" is answerable without reading prose reasons.
- Why this approach: One `guarded` token covered materially different states and the gate saw one, so two rows with the same token could differ by whether a one-character typo bypassed them. Slice 2 had just produced a live example the vocabulary could not express.
- Commits: `a21e0d0d3` (vocabulary and witness), `136d9b851` (round-1 fold), `d30d918e1` (coverage of the guards the changed-line gate named), and the round-2 fold.
- What changed: `scripts/check_adapter_consumer_classification.py` gains `guarded-all-doors` / `guarded-errors-only` / `guarded-upstream`, `measured_guard_level`, `_guard_level_problems` and `_covers` (a chain walk with cycle detection); `row_verdicts` now refuses three manifest shapes that silently dropped a declared class. 35 `guarded` rows migrated to their measured level; six rows moved between accepted-risk and upstream coverage in both directions. Eight new tests. `docs/handoff.md` names the vocabulary.
- Alternatives rejected: REJECTED: `#675`'s own proposal to key the level on whether the file's RESOLVER routes through the reporting loader. Slice 2 made all sixteen public resolvers report all three doors, so that axis is uniform across every guarded row and would measure nothing; keyed on what the CONSUMER asks it is real and was measured first. REJECTED: `#675`'s name `guarded-by-caller`, because the only live row is covered by its CALLEE — the field would have published a call-graph claim in the wrong direction. REJECTED: keeping a coverage-order print that is identical to alphabetical for these tokens, and the test that claimed to pin it.
- Targeted verification: `run_slice_closeout.py --skip-broad-pytest` at every commit boundary; `run_standing_pytest.py` at each boundary, green; `prepush_focused_changed_line_coverage.py --refuse-unestablished` after each commit and before the broad lane, clean at the close. ELEVEN mutations across the two rounds. Two of them are the slice's own finding: the coverage-order code and its test both survived deletion, so both were removed rather than kept as an unprovable pair.
- Test duplication pressure: `check_dup_ratchet.py` at each boundary. Four new families, all the argparse CLI-entrypoint family re-fingerprinting as `main()` changed — three times in this slice alone. That the identity is content-based, so a gate whose `main()` grows a line rejoins under a new id and owes a fresh classification, is recorded in the last note rather than absorbed.
- Critique: TWO bounded rounds, one reviewer each, spawned UNNAMED and read-only as `bounded-reviewer`, with `reviewer_boundary_fingerprint.py` snapshot/verify around each window — both `ok: true` / `clean` at reviewer completion. NEITHER WAS CLEAN. Round 1: the gate's headline accepted-risk number was inflated by half (five rows already carried "every production caller is guarded" in their own reasons and sat in that class only because no token existed for them); the new token named the wrong direction; the level witness is call-presence and the BLIND CLASS did not say so; the previous fold's `row_verdicts` fix was one-sided. Round 2: TWO of the five `covering_rows` lists I wrote were wrong, both derived from prose rather than the call graph — one incomplete in both directions and one a row that should never have migrated, because it CAN guard itself and simply does not. The gate had also forbidden a legitimate two-hop chain, so the enumerated set was being shaped by what the checker accepts rather than by the call graph — `#675`'s own distortion, reproduced by `#675`'s own gate. Round-2 repairs are ACCEPTED-UNREVIEWED per the two-round cap.
- Off-goal findings: 55 rows carry `safe-checks-errors`, which now covers materially different coverage exactly as `guarded` did — four of them read through `cautilus_adapter_lib` / `proof_semantics_adapter_lib`, which still call `load_yaml_file` bare, so two of three doors are dead for them. Raised in `## Operator Decision Queue` rather than split here. `scripts/retro_floor_scope_lib.py` is a real adapter consumer with NO census row, because it calls a helper rather than a `load_*adapter*` name and the AST enumerator cannot see it.
- Lessons carried forward: A list derived from a paragraph is evidence about the paragraph, not about the code — I wrote five `covering_rows` lists out of prose, flagged them as the slice's weakest evidence, and two were wrong. The transferable rule is narrower than 'check your sources': when a token's whole value is that it publishes an ENUMERATED set, the enumeration owes the same measurement the verdict does, and prose that already lists members is the most tempting place to skip it. The second lesson is the gate shaping its own input: forbidding a legitimate two-hop chain did not produce a refusal, it produced a manifest that quietly omitted a real caller.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [The design north star](../../docs/design-north-star.md), read while shaping. Its
   demand — brief a capable judge, keep teeth only where a wrong answer escapes, and
   confirm at irreversible boundaries through a different observer AND a different
   evidence channel — is what this goal is built around. The predecessor satisfied the
   observer half twelve times and the teeth were placed correctly; what escaped was the
   CLAIMS around them, which is a legibility failure (P4) rather than a coverage one. That
   is why slice 1 is a detector and not another guard. Irreversible boundaries crossed:
   push, and three issue closes.
2. [The predecessor goal](./2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md) —
   its `## Active Operating Frame` holds the remaining rows and WHY each remains; its
   `## Slice Log` holds twelve review rounds. Do not re-derive either.
3. [The session retro](../retro/2026-08-19-session-retro.md), `## Second Window`. Its
   Engelbart counterfactual is this goal's premise, stated before this goal existed.
4. [The operating contract](../../docs/conventions/operating-contract.md) — the two-round
   critique floor, which both slice 1 and slice 2 trigger.
5. `#673`, `#674`, `#675` as filed — each carries its own measured evidence and acceptance,
   so this goal does not restate them.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

**Q1 — what does the next session start with?** Options: (a) keep paying rows, the
established pattern with measured bases already in hand; (b) build the detector first;
(c) close the resolver split first. CHOSE (b). Rejected (a) because the predecessor
measured its own failure mode — every round found something, and the later rounds found
prose, so nineteen more rows buys roughly ten more rounds spent on claims a tool can
check. Rejected (c) as FIRST despite it being the deeper fix, because slice 2 will itself
produce probe records, and building the detector after them repeats the mistake one level
up.

**Q2 — does this goal claim the remaining rows, or stop at tooling?** Options: a
three-slice tooling goal with a successor for the rows; a five-slice goal claiming both.
CHOSE five, with an explicit stop rule in the Slice Plan and the decision surfaced in
`## Discuss Before Activation` rather than assumed. The predecessor showed that context
about WHY a row remains is expensive to rebuild, and it is currently written down in one
place.

**Q3 — should slice 2 fix all six resolvers, or only the consequential ones?** Options:
all six; only those whose consumers are gates. CHOSE all six. The predecessor already
repaired `announcement` alone, ahead of `#673`, because its consumer was a publish gate —
and that partial fix is exactly what produced the "guarded means four things" problem
slice 3 now has to solve. Repairing a subset again would buy a fourth coverage level.

**Q4 — is `#550` in scope?** Options: claim it, ignore it, re-read it. CHOSE re-read.
Slice 2 changes the very duplication `#550` reports, so leaving it unexamined would let
this goal close its cause without noticing. Claiming it as a close would be scope creep
into a refactor this goal has no measurement for.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: this artifact, `#673` / `#674` / `#675` as filed, and the predecessor
  goal's `## Active Operating Frame` (the source of the remaining-row decisions). The
  retro, review packets, reviewer reports and lock record are terminal evidence, not
  semantic inputs.
- Frozen target: commit the last semantic change, then bind the closeout packet to that
  exact SHA. Any edit to this artifact's Goal / Boundaries / Slice Plan after binding
  requires rebinding.
- Fresh-eye: a `bounded-reviewer` spawned UNNAMED and read-only, distinct from every
  round already run in the slice — and a different EVIDENCE channel from the parent's:
  the reviewer reads code and artifacts, the parent re-runs the CLIs. `git show` for base
  state is a third channel and its absence has left five prior reviewers with unverified
  items; state the reviewer's actual tools in the packet.
- Verification lock: `python3 scripts/run_slice_closeout.py --verification-lock`, evidence
  under `.charness/quality-failure-logs/` on failure and in the closeout receipt on pass.
- Complete flip: record packet / reviewer / lock evidence, then flip `Status:` and write
  `## Final Verification` and `## Auto-Retro` outside the reviewed identity.

## Off-Goal Findings

- **`#676` filed** (standing-approved): a repair shipping the class it repairs, six measured
  instances across three surfaces. The retro's transferable waste.
- **`scripts/retro_floor_scope_lib.py` is a live adapter consumer with NO census row.** It
  calls `retro_artifact_prefix` rather than a `load_*adapter*` name, so the census's AST
  enumerator cannot see it — a blind spot in the enumerator, not a missing classification.
- **`scripts/adapter_key_registry.py` already answers "which readers read this key"** without
  a subprocess; wiring it into the stimulus replay would close that module's stated gap
  between "the resolver honors it" and "a consumer reads it". Unmade.
- **`proof_semantics_adapter_lib` and `cautilus_adapter_lib` still call `load_yaml_file`
  bare.** Outside `#673`'s sixteen, so routing them is a behavior change this goal did not
  measure. They are the residual surface for `#550`.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-19-adapter-debt-tooling-and-remainder.md
Host log probe: skipped: host-log-not-exposed: this host surfaces no per-turn token, wall-clock or tool-call log to the session, so any efficiency figure would be fabricated rather than measured; the goal's own proof is the gate receipts and the nine reviewer reports instead
Disposition review: charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder-disposition-review.md

## User Verification Instructions

TWO OF FIVE ARE NOT MET AND ONE IS PARTIAL. Stated here rather than left to inference,
because an artifact reading `complete` above five acceptance items is read as five satisfied
items.

**1 — NOT MET as written; substantively partial.** The named command does not do it:
`check_probe_record.py --require-evaluated` never replays, because the replay is gated on
`--replay-stimulus`. Run instead
`python3 scripts/check_probe_record.py --repo-root . --record charness-artifacts/probe/2026-08-19-release-planner-version-refusal.md --replay-stimulus`
— it resolves `evaluated` today and resolved `not-established` before that record was
corrected. The acceptance also asks for a DIFF against `## Base observable`; the shipped
mechanism is declaration ablation, which catches the CAUSE of a dead control rather than the
arms. Both deviations are in `## Operator Decision Queue`.

**2 — MET.** `python3 -m pytest tests/quality_gates/test_every_resolver_answers_a_refused_document.py -q`
— 81 cases over a roster pinned as a SET of sixteen skill ids.

**3 — MET.** Same file, `test_the_dropped_line_door_is_reachable`, which asks
`adapter_version_verdict.declarations_dropped(payload)` directly rather than matching text.

**4 — PARTIALLY MET.** `python3 scripts/check_adapter_consumer_classification.py --repo-root .`
answers it for the `guarded` family without reading a reason: 32 / 3 / 5 across three named
levels, with callouts. It does NOT answer it for `safe-checks-errors` — 55 rows now carrying
one token over materially different coverage, the same defect on the largest class, staged in
`## Operator Decision Queue`. `guarded-upstream` also publishes an enumerated `covering_rows`
the gate cannot verify in either direction.

**5 — NOT MET.** Same command: `accepted-risk-unguarded: 6` plus `no-version-validation: 11`
= 17 rows unpaid. Slice 4 never started. Carried by
`charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`.

## Auto-Retro

Retro dispositions: applied + issue + accepted-risk — each improvement the retro surfaced is
dispositioned below: five shipped changes, one filed issue, two accepted risks staged for the
operator. No prose-only improvement remains. The wording said "every ... dispositioned"
before the closeout disposition review found one missing (the `covering_rows` guard).

- `applied: tests/quality_gates/test_probe_record_corpus_replays.py` — the `#674` detector
  was INERT until a bounded round grepped and found nothing ran it. A standing-lane sweep
  over every checked-in probe record now does, so `#674`'s own premise ("thirteen review
  rounds, no gate") stops being true for record fourteen.
- `applied: scripts/resolve_artifact_path.py` `_refuse_unhonored_adapter` — the regression
  slice 2 caused, closed on the CONDITION rather than the exit code, with a three-door test.
- `applied: scripts/check_adapter_consumer_classification.py` — the level witness refuses in
  BOTH directions, which is what makes an over-conservative row visible; the previous
  witness never checked one, and one sat wrong through an entire slice.
- `applied: scripts/adapter_lib.py` `_load_yaml_module` — fail-clean path loading, so a
  missing parser reports its own cause instead of an `AttributeError` for every module in
  the same process.
- `applied: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md` — the
  successor goal, whose slice 1 is the structural answer to the transferable waste below.
- `issue #676` — a repair shipping the class it repairs, six times across three unrelated
  surfaces in this goal, every one caught by the second bounded round rather than by a gate.
- `accepted-risk: covering_rows publishes an ENUMERATED set the gate cannot verify in either
  direction — it checks the named rows are guarded, never that they are callers or that the
  list is complete, and two of the first five lists shipped wrong. Recorded in that module's
  blind class; a witness walking the call graph for the covered symbol would close it.`
- `accepted-risk: 55 safe-checks-errors rows carry one token over materially different
  coverage, exactly as guarded did before slice 3 split it — four of them read through
  libraries that still call load_yaml_file bare, so two of three doors are dead for them.
  Accepted for this goal and staged in ## Operator Decision Queue with its measured
  evidence; splitting the largest class is a slice of its own.`

Structural follow-up: issue #676 (recurs: six measured instances in one goal — a probe-record detector, an adapter loader contract, and a census gate)

The transferable waste is A REPAIR
SHIPPING THE CLASS IT REPAIRS, and the answer this run recommends is an affordance rather
than another review round: when a slice's diff adds a REFUSAL, emit the refused input class
and ask whether the repair's own new code contains it. Designed as slice 1 of the successor
goal; filing the issue is standing-approved and the design call is the operator's.

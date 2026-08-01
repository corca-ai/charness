# Achieve Goal: Push the lane, then close the closeout record, the mutation regression, and the sweep's remaining high rows

Status: complete
Created: 2026-08-01
Activation: `/goal @charness-artifacts/goals/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md` after confirming the draft is
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

Push the local backlog (recount with `git log --oneline origin/main..HEAD`; a
transcribed count goes stale in place) so the changed-line lane stops inheriting
other sessions' blocks; then repair the closeout evidence record so a goal's own
claims carry their proof; then settle issue #467 against a measurement that can
actually see its survived mutants; then disposition the sweep's remaining high
rows, with the premise of D45's NAMED REMEDY read before any S31 work.

## Non-Goals

- **Not a release.** No version bump, no publish, no tag. The push is to `main`;
  it is not a release, and the D48 publish refusal armed on 2026-08-01 has still
  never fired against a real publish after this goal.
- **Do not arm D46, D47, or D48's refusals.** All three stay deferred; the
  2026-08-01 operator call is recorded in each entry and this goal does not revisit
  it.
- **Do not build a gate that checks gates.** Lane B repairs a proof surface, and
  [the north star](../../docs/design-north-star.md) names "meeting a gate-quality
  problem with another bespoke gate" as the anti-pattern *and applies it to
  itself*: "What this does not license is a gate that checks gates." The teeth
  Lane B may add are a captured observable and a named scope, never another green.
- **Do not retry D47's per-field distinctiveness or D48's sync-derived surface
  set.** Both are marked `Withdrawn, do not retry` with reasons.
- **Not a rewrite of frozen artifacts.** If a repair would require editing a
  checked-in quality review or goal artifact to satisfy a later floor, stop and
  record — that is the Goodhart move this repo's own validators exist to refuse.

## Boundaries

- **External side-effect scope, enumerated in full** (the previous run's recorded
  miss was a non-claims block that omitted an issue filing, so this lists every
  write, not only the push): (1) ONE `git push` of the existing local backlog to
  `main`, Lane A only, plus the `quality-core` run it triggers; (2) ONE issue
  close + closing comment on #467, Lane C only; (3) any issue FILED by a Lane D
  disposition or a closeout retro. Approved by the operator on 2026-08-01,
  phase-scoped, and NOT carrying forward to a publish, a tag, a version bump, or a
  second push of work this goal creates.
- **Second-order write, named because it is inside the blast radius and nobody
  chose it:** `mutation-tests.yml` runs on a 12-hourly cron with `issues: write`
  and dedupes against OPEN issues carrying its marker. Closing #467 removes that
  marker, so the next cron may file a fresh duplicate. Lane C must state whether
  it accepts that or leaves the issue open.
- **Any new Lane B floor carries its own `*_RULE_DATE` and grandfathers goals
  created before it**, as every existing `goal_artifact_*` floor does. Without one
  a floor landing today is in scope for every undatable prior goal, and the only
  way to green those is to edit frozen artifacts — which the Non-Goals forbid.
- In scope (Lane A — push and re-base):
  [.github/workflows](../../.github/workflows) as a read surface only, and the
  changed-line lane's base resolution in
  [run-quality.sh](../../scripts/run-quality.sh) /
  [check_changed_line_mutation_coverage.py](../../scripts/check_changed_line_mutation_coverage.py).
- In scope (Lane B — the closeout evidence record):
  [check_goal_artifact.py](../../skills/public/achieve/scripts/check_goal_artifact.py)
  and the `goal_artifact_*` floor modules it composes,
  [append_slice_log.py](../../skills/public/achieve/scripts/append_slice_log.py)
  (the empty `Commits:` / `Metrics:` fields),
  [reviewer_boundary_fingerprint.py](../../skills/shared/scripts/reviewer_boundary_fingerprint.py)
  (the overwriting default `--out`), and
  [goal-artifact.md](../../skills/public/achieve/references/goal-artifact.md).
- In scope (Lane C — #467): the survived mutants in
  [check_chunk_contract.py](../../skills/public/hitl/scripts/check_chunk_contract.py)
  and whatever the re-based mutation run still reports.
- In scope (Lane D — sweep rows):
  [the sweep](../../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
  rows S15, S31, S36, S37, S111, and
  [D45](../../docs/deferred-decisions.md) as S31's precondition.
- Also in scope everywhere: the regression tests for each change, and the
  generated `plugins/charness/` mirror of every touched skill file. Sync mirrors
  before validators (`mutate -> sync -> verify`); `quality-core` reds on committed
  export drift.
- Portable per implementation-discipline: Lane B touches a PUBLIC skill's
  validator, so any new observable must be expressible by a consumer repo that
  does not use this repo's artifact conventions.
- **NOT in scope: arming D45.** Its named remedy is `--require-evaluated-scope` in
  `run-quality.sh`, which would redden this repo's parity gate immediately. Lane D
  READS D45's premise; it does not act on it. `run-quality.sh` is absent from every
  in-scope list above deliberately.
- Stop conditions: (1) if the `quality-core` run the push triggers comes back RED
  ON ANY STEP, STOP and report before starting Lane B — a red main is the
  operator's call, not a lane to work around. The comparator is per-channel and
  NOT "worse than #467": #467 is a mutation-workflow verdict, and the push does not
  run that workflow, so the two are incommensurable. (2) If a Lane B repair would
  require rewriting a frozen artifact, record instead. (3) If S36/S37 cannot be
  REPRODUCED, refute them rather than repairing a lead — and reproduce at FUNCTION
  level, never by performing a publish, which the Non-Goals forbid. (4) If the
  premise of D45's named remedy turns out false, record that on D45 and
  re-disposition S31 on its own terms — S31 has NO recorded repair to withdraw
  (its status is `OPEN (narrowed 2026-08-01, NOT closed)`), and the recorded
  direction is S31 -> D45, not the reverse.

## User Acceptance

- **Lane A:** `git log --oneline origin/main..HEAD` is empty, and the
  `quality-core` run the push triggered is named with its URL and its verdict —
  including if the verdict is red. **The local changed-line lane is NOT the
  evidence here and must not be cited as it:** after the push `merge-base
  origin/main HEAD` IS `HEAD`, so the analyzed range is empty and
  `check_changed_line_mutation_coverage.py` returns `ok: true` by construction.
  That is a zero denominator rendering a PASS — the exact class this repo's own
  sweep rows S1/S26/S30/S32 catalogue — and citing it would be this goal
  committing the defect it exists to close. The meaningful verdict is CI's, whose
  base is `github.event.before` (the pre-push main).
- **Lane B**, scoped to THIS goal's own artifact plus a pinned fixture that fails
  before each repair and passes after — not to "any artifact produced afterward",
  which no closeout can execute:
  - `## Final Verification` carries each figure in a checkable FORM —
    `<value> — <source path or command>` or `<value> — unbacked: <why>` — a
    presence/form floor in this repo's existing enum idiom. The validator checks
    the form; whether the citation is honest stays author judgment plus the
    fresh-eye round. It must NOT try to decide "is this number backed", which is
    not machine-decidable and would ship as a Goodhart proxy.
  - `Retro:` and `Disposition review:` must resolve to DIFFERENT PATHS. Path
    distinctness is buildable; "different author" is not — no signal in a
    checked-in file determines authorship, and a bounded reviewer never commits.
    A proxy for authorship would rubber-stamp the exact defect it was built for.
  - `Commits:` is populated per slice — see the Boundaries note: the flag already
    exists, so this is a usage repair, and the SHA of the commit that CLOSES a
    slice cannot appear in the text that commit contains.
- **Lane C:** each of the six survived mutants in `check_chunk_contract.py` has a
  per-mutant verdict — killed by a named test, or refuted IN WRITING as equivalent
  (several look cosmetic: `ensure_ascii=False`, `indent=2`). Only then is #467
  closed, with those verdicts in the closing comment. **Three outcomes are
  admissible and "no longer in the changed set" is NOT one of them:** the push
  cannot kill a mutant, and closing on a shrunken denominator would be the
  zero-denominator class committed at an irreversible boundary. If the mutants are
  not settled, #467 stays OPEN and is re-scoped instead.
- **Lane D:** each of S15, S31, S36, S37, S111 carries a disposition its own row
  states — CLOSED, NARROWED with the residual named, or REFUTED — and no row is
  marked closed on a repair whose premise was not checked. D45 records whether its
  named remedy's channel exists.
- Every claim above is backed by a command in `## Final Verification` with its
  actual output, and anything not executed is named as a non-claim.

## Agent Verification Plan

### Low-Cost Checks

- the dup-ratchet at the FIRST edit to a gated file in each slice, never at the
  closeout aggregate
- `python3 scripts/check_python_lengths.py --headroom --paths <file>` BEFORE a
  large addition, not after the cap refuses — and when it does refuse, SPLIT the
  concept; shaving comments to fit is a recorded P2 violation from the last run
- targeted `pytest` for the touched modules, plus the owning validator
- **after any scripted string edit, assert the superseded text is absent** — the
  last run reported a repair that had silently never applied
- **when a number replaces a number in a durable record, grep the repo for the old
  value** before closing

### High-Confidence Checks

- the full serial suite for touched families at each slice boundary
- one bounded fresh-eye round per slice; a SECOND round for any slice that changes
  verdict logic on a proof surface — Lane B is entirely that class, so every Lane B
  slice owes two
- `reviewer_boundary_fingerprint.py snapshot --out <per-window path>` around each
  review; the default `--out` overwrites and is itself a Lane B repair target
- **a closeout-claims review by a DISTINCT observer before the complete flip** —
  not the retro's author. The last run found four blockers this way, all in claims

### External Or Live Proof

- ONE `git push` to `main` in Lane A, and the remote CI it triggers. Confirmed per
  the north star's P4: a different observer AND a different evidence channel than
  the push command's own exit code — read the workflow run's own verdict, and
  re-read `origin/main` state through a channel other than the push output.
- Explicitly NOT in this plan, and therefore non-claims: any release publish, tag,
  or version bump; any second push of work this goal creates; any `cautilus
  evaluate` run.

## Slice Plan

Four lanes, sequenced so each closes independently, and the goal is explicitly
expected to span more than one session. Do NOT start a lane whose predecessor is
unclosed. **One exception, stated because it is the irreversible one: stopping
after Lane A is NOT clean if CI is red** — that leaves the pushed backlog on
`main` with a red gate and no revert lane, which is why Q1 is pre-seeded.

Cut by the plan critique and recorded so nobody re-adds them: persisting each
fingerprint window to its own file (`.charness/reviewer-boundary/` is gitignored,
so it would be visible only on the authoring machine, and changing `snapshot`'s
default breaks `verify --before`'s pairing — the discipline fix is to pass
`--out` per window, which needs no code change); and refusing a same-AUTHOR
disposition review (unimplementable — see Lane B row).

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Push the existing local backlog to `main`; read the `quality-core` run it triggers; confirm `origin/main` through a channel other than the push output | FIRST because the changed-line gate inherits other sessions' blocks until this lands. It is the only irreversible action in the goal, so it gets the freshest care. NOTE the plan critique's correction: it does NOT unlock Lane C's measurement — `mutation-tests.yml` has no `push:` trigger | `git log --oneline origin/main..HEAD` empty; the run URL and its per-step verdict quoted, red or green; a distinct-channel readback of `origin/main`. NOT the local changed-line lane: post-push its range is empty by construction and its green would be a zero denominator | pending |
| B | Three BUILDABLE repairs only, after the plan critique cut two: (i) a form floor on `## Final Verification` figures (`<value> — <source>` or `<value> — unbacked: <why>`); (ii) `Retro:` and `Disposition review:` must resolve to different PATHS; (iii) populate `Commits:` per slice — a usage repair, the flag exists | The machinery every later closeout uses, including this goal's own — repairing it first means lanes C and D are held to the repaired standard rather than the one that let four blockers through last run. This is the Engelbart move the repo briefs | Each floor pinned by a fixture that fails before and passes after; each carries its own `*_RULE_DATE`; mirrors synced; TWO bounded rounds per slice (verdict logic on a proof surface); every addition a form check or a named scope, never a new green | pending |
| C | Kill or refute each of the six survived mutants in `check_chunk_contract.py`, then settle #467 on those verdicts | Does NOT depend on A the way the first draft claimed. Verified during the plan critique: `check_chunk_contract.py` has not been touched since `989a1134`, so the mutants survive the push untouched, and `mutation-tests.yml` has no push trigger. The measurement must be a SCOPED LOCAL mutation run naming those mutants — a cron green is explicitly "a candidate, not a verdict" in the workflow's own words, because its sample seed rotates per run | A per-mutant verdict, killed-by-named-test or refuted-as-equivalent in writing; then #467 closed via `issue` with those verdicts in the comment, or left OPEN and re-scoped. Never closed on "no longer in the changed set" | pending |
| D | Disposition S15, S31, S36, S37, S111 — reading the premise of D45's NAMED REMEDY ("move the exemption to the adapter") before touching S31 | Last, and deliberately: volume work whose value depends on the record being trustworthy (B). The direction is S31 -> D45, not the reverse (D45 calls itself S31's *consequence*); what is unverified is whether an adapter-declared exemption seam exists in `ci_local_gate_parity_lib.py` at all. S36/S37 are LEADs never reproduced, so their first move is reproduce-or-refute at FUNCTION level — never by publishing | The remedy's premise answered by a file read, recorded on D45; each row's disposition on its own row with residuals named; any LEAD that will not reproduce marked REFUTED rather than quietly repaired | pending |
| E | Closeout: bundle quality gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as part of task-completing work — and the last run proved the closeout itself needs an observer it does not author | `./scripts/run-quality.sh` output at the new base; `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | pending |

## Operator Decision Queue

The goal's own two activation decisions — push scope, and lane selection — were
answered before shaping. One is pre-seeded because it will fire and the run should
not stop on it.

### Q1 — pre-seeded: what if the push's CI comes back red?

- Decision: whether a red `main` after Lane A's push is a stop-and-report or a
  lane to work through.
- Owner: operator.
- Why deferred: it may not fire. #467 already records main as failing on the
  changed-line signal, and 25 commits of coverage have landed since, so the
  plausible outcomes are "better", "same", and "new failure".
- Unblock action: Boundaries stop condition (1) already fixes the default —
  STOP and report if CI comes back WORSE than #467 already records. What needs an
  answer only if that happens: revert, fix forward, or accept and continue.
- Revisit trigger: the workflow run Lane A triggers.

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

- Routing: achieve — owns the goal lifecycle this run executes and the closeout floors Lane B repairs.
- Routing: impl — selected from installed metadata for the code-bearing slices (Lane B's two floor modules and the regression tests in Lanes A and C); its `prove` stop gate is what `run_slice_closeout.py` runs at every commit boundary here.
- Routing: quality — selected for the validation posture: the dup-ratchet classifications, the changed-line gate reading, and the public-skill validation call that returned `next_action: none`.
- Routing: issue — selected for the tracked-regression work: #467's closeout draft validation and close, plus filing #469 and #470.
- Routing: critique — selected for the four bounded review rounds and the two checked-in critique artifacts.
- Routing: retro — selected for the closeout efficiency review and its dispositions.
- Gather: n/a — no external URL, Slack, Notion, Docs, or Drive source entered this run's working context; every input is a checked-in repo artifact or a GitHub API read of this repo's own issues and workflow runs.
- Release: n/a — no version bump and no install-manifest edit anywhere in this run; "Not a release" is a stated Non-Goal, and quality-core.yml is the only push-triggered workflow, declaring permissions contents read.
- Issue closeout: #467 — carrier manual-fallback (operator-directed-manual-close), proved by `issue_tool.py validate-closeout-draft --classification bug --carrier manual-fallback` returning `status: draft_verified` before the close, and `gh issue view 467` returning `state: CLOSED, stateReason: COMPLETED` after it. Also FILED this run (creations, not closeouts): #469 and #470.
- Public-skill validation: `plan_cautilus_proof.py --detail` returned `next_action: none`. Both touched skills (achieve, quality) are hitl-recommended, and the Lane B change is additive AFTER-phase validator surface that does not alter achieve's frozen dogfood consumer contract. Deterministic tests own this closeout; acked with `--ack-cautilus-skill-review`. No `cautilus evaluate` run — a stated non-claim.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: Approved by the operator on 2026-08-01, three items. (1) IRREVERSIBLE SIDE EFFECT — one `git push` of the existing local backlog to `main`, plus the remote CI it triggers. Approved explicitly; the approval is scoped to Lane A and to commits that already exist locally, and does NOT extend to a publish, a tag, a version bump, or a second push of work this goal creates. Confirmation follows the north star's P4: a different observer AND a different evidence channel than the push command's own exit code. (2) ISSUE CLOSE — Lane C may close #467, which is irreversible in the sense the north star defines (a reopened issue was already read as done); resolved by requiring the re-based measurement to be quoted in the closing comment, so the close carries its evidence rather than pointing at it. (3) BROAD BUNDLED SCOPE and PROOF-LEVEL NON-CLAIMS — four lanes in one goal, explicitly expected to span more than one session, with each lane closing independently so a stop between lanes is clean; and no release, no tag, no cautilus run, so every non-push verdict stays local. Resolved: accepted and stated rather than implied.

## Slice Log

### Slice 1: A — push the lane

- Objective: Push the 30-commit local backlog to main, read the quality-core run it triggered, and confirm origin/main through a channel other than the push output.
- Why this approach: First because the changed-line gate inherits other sessions' blocks until this lands, and it is the goal's only irreversible action.
- Commits: 9ea738bb (push blockers), f40ff27c (CI fix-forward); pushed as 989a1134..9ea738bb then 9ea738bb..f40ff27c
- What changed: tests/quality_gates/test_inventory_ci_local_gate_parity.py; charness-artifacts/retro/lesson-selection-index.json; charness-artifacts/retro/recent-lessons.md
- Alternatives rejected: Reverting the push after the first red CI (rejected by operator: fix forward). Widening DOC_GLOBS or silencing the local warning (out of scope; filed as an issue instead).
- Targeted verification: git ls-remote origin refs/heads/main = f40ff27c (channel distinct from push output); git log --oneline origin/main..HEAD empty; CI run 30702242447 both jobs success.
- Test duplication pressure: check_dup_ratchet --summary PASS at each commit boundary; no new duplicate families.
- Critique: Pending bounded round.
- Off-goal findings: Issue #469: the local changed-line gate returns PASS over a partial denominator and cleared a push CI then blocked.
- Lessons carried forward: A local gate that names its own unanalyzed files and still says PASS is not a weaker CI; it is a different denominator. Read the warning, not the verdict.
- Metrics:

### Slice 2: B — the closeout evidence record

- Objective: Repair the machinery every later closeout uses: a path-distinctness floor, a figure-form observable, and populated Commits: per slice.
- Why this approach: The Engelbart move: repair the record first so lanes C and D are held to the repaired standard.
- Commits: 836d5034 (first cut), d8800ae7 (round-1 repairs), 815d3eba (round-2 repairs)
- What changed: NEW goal_artifact_evidence_distinctness.py and goal_artifact_figure_form.py; goal_artifact_floor_grammar.py (+grandfathered_report); operator_queue and blocked_matrix migrated onto it; check_goal_artifact.py + describe_goal_closeout_shape.py wiring; lifecycle-after.md; D49; test_goal_closeout_record_floors.py; dup-review.json; attention-state-visibility.json; plugins mirrors
- Alternatives rejected: Refusing a same-AUTHOR disposition review (cut in plan critique: unimplementable). Arming the figure floor (tried in round 1, refuted in round 2 by its denominator). A finer grandfather key than a date (deferred: contract change across the floor family).
- Targeted verification: 27 tests in the new file; 248 across the achieve families; distinctness over all 147 goal artifacts (23 in scope, 0 refused, of which only 2 dated-and-compared); figure floor over 127 DATED artifacts (strict 90, relaxed 41).
- Test duplication pressure: check_dup_ratchet hard-blocked five times. The real duplication (the grandfathered payload) was EXTRACTED to the shared substrate and two inline copies migrated; the rest is module-bootstrap boilerplate and one recorded deliberate divergence, classified with reasons rather than shaved.
- Critique: TWO bounded rounds, both changed the outcome. Round 1: a BLOCKER (a refusal naming a floor that had passed) plus a refutation of the deferral. Round 2: round 1's arming rested on a zero-denominator green, plus three silent passes from the soft-wrap join. Round-2 repairs accepted-unreviewed per the two-round cap.
- Off-goal findings: None new in this lane.
- Lessons carried forward: A fix for a verdict-logic defect carries the class it fixes. Any measurement over a grandfathered corpus must state its denominator in DATED artifacts.
- Metrics:

### Slice 3: C — the #467 mutants

- Objective: Give each of the six survived mutants a per-mutant verdict, then settle #467 on those verdicts.
- Why this approach: Verified in the plan critique not to depend on Lane A: check_chunk_contract.py was untouched since 989a1134 and mutation-tests.yml has no push trigger.
- Commits: f3961290 (mutant verdicts), fe2785f9 (the correction and the real fix)
- What changed: tests/quality_gates/test_hitl_chunk_contract.py; NEW tests/quality_gates/test_skill_gate_report_render.py; charness-artifacts/critique/2026-08-01-467-mutation-regression-resolution-critique.md
- Alternatives rejected: Killing the L65 ensure_ascii mutant by making check_chunk_contract echo chunk text (rejected: writing a defect to satisfy a mutant). Reopening #467 after the correction (rejected: the signal is now settled by direct line coverage, and reopening would churn the cron dedupe marker without improving the evidence).
- Targeted verification: Scoped cosmic-ray reproduced exactly the six; re-run after the new test went killed 65 to 66, survived 9 to 8. scripts/skill_gate_report_render.py measured 0 percent before and 100 percent after.
- Test duplication pressure: Two tests added to an existing file plus one new file; dup ratchet clean on this lane.
- Critique: One bounded round, run AFTER the close — the ordering error this run's retro names as its top waste. It caught the closing comment citing a CI run whose base was the second push, which pulled the real thread: the file had left the changed set, so blocking empty never meant the line was covered.
- Off-goal findings: #469.
- Lessons carried forward: Reading a gate's verdict is not reading its denominator. Run the resolution critique BEFORE the irreversible close.
- Metrics:

### Slice 4: D — the sweep rows

- Objective: Disposition S15, S31, S36, S37, S111 on their own rows, with D45's named-remedy premise read before any S31 work.
- Why this approach: Last and deliberately: volume work whose value depends on the record being trustworthy, which Lane B repaired.
- Commits: fe2785f9
- What changed: charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md (5 status cells, 3 in-cell correction markers, a dispositions section); docs/deferred-decisions.md (D45 premise answered)
- Alternatives rejected: Arming D45's --require-evaluated-scope (out of scope: would redden the parity gate immediately). Repairing S36 with a runtime disclosure (named, not made: publish_release.py is a release surface and release work is a Non-Goal). Widening DOC_GLOBS for S111 (rejected: artifact links rot by design).
- Targeted verification: S37 CLOSED via git show 3cc0b27d (the claimed shape present at the sweep date) plus a function-level execution proving the arm now runs. S36 reproduced by loading a vendored copy with no bootstrap ancestor: returns silently. D45's premise answered by reading read_gate_policy and evaluate_workflow signatures — no adapter parameter exists.
- Test duplication pressure: n/a — this lane changed records, not code.
- Critique: Covered by the closeout-claims review, which found two status cells asserting what their own narratives refuted; in-cell correction markers added.
- Off-goal findings: None.
- Lessons carried forward: A LEAD that will not reproduce may be FIXED rather than REFUTED, and those are different facts about whether the gates work. One git show separates them.
- Metrics:

## Context Sources

Follow these in order; a fresh session can reconstruct the whole originating
context from them without this session's memory.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — the standard
   Lane B is measured against, and the source of its hardest constraint (P5: "no
   gate that checks gates", stated as applying to itself).
2. [The preceding goal](./2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md)
   and its
   [closeout-claims review](../critique/2026-08-01-three-unarmed-refusals-closeout-claims-review.md)
   — Lane B exists because that review found four blockers in that goal's own
   closeout claims, and the review's `## Residual, not closed` section IS Lane B's
   work list.
3. [Its retro](../retro/2026-08-01-three-unarmed-refusals-retro.md) — the waste
   analysis and the Engelbart counterfactual that argues for Lane B's ordering.
4. [issue #467](https://github.com/corca-ai/charness/issues/467) — Lane C's
   subject; note its blocking signal is anchored to `989a1134`, the last pushed
   commit, which is why Lane A precedes it.
5. [issue #468](https://github.com/corca-ai/charness/issues/468) and
   [D45](../../docs/deferred-decisions.md) — Lane D's precondition: the pattern
   and its next unverified instance.
6. [The sweep](../audit/2026-07-28-evidence-surface-triage-sweep.md) rows S15,
   S31, S36, S37, S111 — Lane D's rows, with their current dispositions.
7. [docs/conventions/implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
   Change Discipline and
   [operating-contract.md](../../docs/conventions/operating-contract.md) Critique
   Discipline — the two rules promoted out of the previous baton, which this
   goal's verification plan operationalizes rather than restates.

## Interview Decisions

Two questions were asked; each records the family, the choice, the rejection
reason, and the anti-anchoring probe.

1. **Which objective?** Family considered: {the closeout evidence record; the
   sweep's remaining high rows + D45; #467 + push; the E-cluster}. **Chosen: the
   first three, all of them.** Rejected: the E-cluster, on scope — the handoff
   itself records it as the most expensive lane, and three lanes plus a push is
   already more than one session. Rejected: picking only one, because the operator
   wanted the backlog moved on three fronts and the lanes have a real dependency
   order (push re-bases the gate that judges everything else) rather than
   competing for the same hour. Anti-anchoring: `axis: lane independence` — the
   design varies on whether lanes share a surface. These three do not (release CI,
   achieve floors, hitl script, sweep rows), which is what makes a multi-lane goal
   safe here and would not make it safe for lanes that overlap.
2. **Is push in scope?** Family considered: {push included; stay local as the
   previous run did}. **Chosen: push included.** Rejected: staying local, because
   the unpushed backlog actively degrades the changed-line gate — it inherits
   other sessions' blocks — and because #467's blocking signal is anchored to the
   last pushed commit, so the issue cannot be honestly measured without it.
   Anti-anchoring: `single-point: this backlog` — push scope is a property of this
   accumulated state, not a standing policy; the approval does not carry to the
   next goal, and the Boundaries say so.

## Plan Critique Findings

Reviewer provenance: one bounded fresh-eye round, typed `bounded-reviewer`
(read-only, Read/Grep/Glob only), parent-delegated, in the shared parent worktree
with a PERSISTED fingerprint window —
`.charness/reviewer-boundary/next-goal-plan-critique.json`, id
`w-20260801T115429Z-1806444`. It read the plan, the north star, the preceding
goal's closeout-claims review, both GitHub workflows, and every in-scope surface.

**Blockers folded, each parent-verified before folding.** Three of four were
cases of the plan asserting something the tree contradicts — the class this goal's
Lane B exists to make harder.

- **B1 — Lane A's acceptance was a ZERO-DENOMINATOR GREEN.** After the push,
  `merge-base origin/main HEAD` IS `HEAD`, so the changed-line lane's range is
  empty and it returns `ok: true` by construction. The plan cited that as proof the
  session's own lane was clean. It is sweep rows S1/S26/S30/S32's class, written
  into the acceptance criteria of a goal whose purpose is closing that class.
  Folded: the local re-run is explicitly named NOT the evidence, and CI's verdict
  (base `github.event.before`) is.
- **B2 — Lane C's premise fused two independent signals.** Changed-line coverage is
  base-dependent; six survived mutants are a property of code and tests. A push
  kills no mutant. Verified: `check_chunk_contract.py` has NOT been touched since
  `989a1134` (`git log 989a1134..HEAD -- <path>` → 0 commits), and
  `mutation-tests.yml` has **no `push:` trigger**, so Lane A cannot produce Lane C's
  measurement at all. The only way the push "self-resolves" #467 is by the
  denominator shrinking — the same zero-denominator class, at an irreversible
  boundary. Folded: Lane C now requires a scoped local mutation run and per-mutant
  verdicts, and "no longer in the changed set" is named as inadmissible.
- **B3 — "refuse a same-AUTHOR disposition review" is unimplementable.** No signal
  in a checked-in file determines authorship, and a bounded reviewer never commits.
  Any built floor would be an authorship PROXY, which this repo's own disposition
  module already argues against ("a deterministic false-positive trains
  token-theater"). Folded: narrowed to path-distinctness, which is what the
  original defect actually was and is buildable.
- **B4 — "make an unbacked number say so" is not machine-decidable.** Folded:
  restated as a FORM floor in this repo's existing enum idiom, with the judgment
  left to the author and the fresh-eye round.

**Minors folded:** the external-side-effect scope now enumerates all three write
classes plus the second-order cron duplicate-issue risk; new Lane B floors must
carry rule dates or they force the frozen-artifact rewrite the Non-Goals forbid;
generated mirrors and tests added to scope; the stop condition's comparator fixed
(the push does not run the mutation workflow, so "worse than #467" was
incommensurable); the D45/S31 direction corrected (S31 -> D45, and S31 has no
recorded repair to withdraw); Lane B acceptance scoped to this goal plus a fixture
rather than quantified over all future artifacts; S36/S37 reproduction pinned to
function level so it cannot collide with the no-publish Non-Goal; and the
fingerprint-persistence item CUT (`.charness/reviewer-boundary/` is gitignored and
changing the default breaks `verify`'s pairing).

**A number in the plan was itself unbacked.** The goal said "25 commits"; the real
count is 29. The reviewer named the irony directly — an unbacked number in a plan
about unbacked numbers. Folded by removing the transcribed count and carrying the
recount command instead.

**Over-worry raised, not folded.** A Non-Goal predicted a post-run fact ("the D48
publish refusal has still never fired after this goal"). Restated as a constraint
rather than a prediction, since this goal's whole Lane B exists because pre-written
closeout claims went unverified.

**Category the reviewer found CLEAN, and it matters:** there is no release,
publish, deploy, or tag-creating workflow in this repo. `quality-core.yml` is the
only push-triggered workflow and declares `permissions: contents: read`. So the
"Not a release" Non-Goal is enforceable at the workflow level and the operator's
push approval is honest.

## Off-Goal Findings

- **#469** — the local changed-line mutation gate returns PASS while printing `analyzed only 49 of 51 changed mutation-pool file(s)`, and it cleared a push that CI then blocked on one of the two unanalyzed files. Filed on an explicit operator instruction to file rather than fix; `run-quality.sh` is deliberately out of this goal's scope.
- **#470** — zero-denominator greens recurred three times in this one run, plus the two structural follow-ups: Created-gated floors can be armed on a corpus of undatable artifacts, and the issue resolution critique runs after the irreversible close.
- **D49** — the figure-form floor's arming call, deferred with its measurement stated in dated artifacts.
- **D45** — its named remedy's premise answered (a build, not a rewire); the deferral itself is unchanged.
## Final Verification

Every figure below carries its source in the form Lane B built
(`<value> — <source>` or `<value> — unbacked: <why>`), because a closeout that
asserts numbers with no way to check them is the defect this goal existed to
repair. The floor that reads this section is advisory (D49), so this is the
author holding the record to a standard the validator does not enforce.

**Lane A — the push and its CI**

- 33 commits pushed to `main` — `git log --oneline 989a1134..f40ff27c | wc -l`
- 31 in the first push and 2 in the second — `git log --oneline 989a1134..9ea738bb | wc -l` and `git log --oneline 9ea738bb..f40ff27c | wc -l`
- 0 commits left unpushed when Lane A closed — `git log --oneline origin/main..HEAD | wc -l`
- `origin/main` is `f40ff27c5a7245caf8537534652004347888c578` — `git ls-remote origin refs/heads/main`, a channel distinct from the push output
- First run RED, 1 of 2 jobs failed — <https://github.com/corca-ai/charness/actions/runs/30701478239>
- Second run GREEN, 2 of 2 jobs success — <https://github.com/corca-ai/charness/actions/runs/30702242447>
- Deliberately NOT cited as evidence: the post-push local changed-line lane, whose analyzed range is empty by construction

**Lane B — the closeout evidence record**

- 27 tests in the new floor file — `python3 -m pytest -q tests/quality_gates/test_goal_closeout_record_floors.py`
- 248 tests across the achieve goal-artifact families — `python3 -m pytest -q tests/quality_gates/test_goal_*.py tests/quality_gates/test_describe_goal_closeout_shape.py`
- Distinctness floor: 23 in scope of 147, 0 refused — `goal_artifact_evidence_distinctness.check` over `charness-artifacts/goals/*.md`
- Of those 23: 20 undatable, 3 dated, 2 actually compared — `goal_artifact_evidence_distinctness.check` plus `goal_artifact_floor_grammar.parse_created_date` over the same corpus; stated because a bounded reviewer caught that "0 refused" is misleading without it
- Figure floor, strict form: 90 refusals of 127 dated artifacts — `goal_artifact_figure_form.check` with the rule date lowered, over dated artifacts only
- Figure floor, shipped relaxed form: 41 refusals of 127 — same command against the shipped module; an earlier draft said 44, measured before the heading-grouping repair, and that stale value was grepped out of `skills/` and `plugins/`
- 2 bounded review rounds, both of which changed the outcome — `.charness/reviewer-boundary/lane-b-round1.json` and `lane-b-round2.json`

**Lane C — #467**

- 6 survived mutants reproduced, exactly matching the issue — `cosmic-ray exec /tmp/mut467/scoped.toml` then `cosmic-ray dump`
- 1 killed and 5 refuted in writing — the per-mutant table in <https://github.com/corca-ai/charness/issues/467> and `charness-artifacts/critique/2026-08-01-467-mutation-regression-resolution-critique.md`
- killed 65 to 66 and survived 9 to 8 after the new test — a second scoped `cosmic-ray` session over the same config
- `scripts/skill_gate_report_render.py` 0 percent before and 100 percent after — `python3 -m coverage report --include "*skill_gate_report_render.py" -m`
- 0 tests referenced that module before this run — `grep -rn skill_gate_report_render tests/`

**Lane D — the sweep rows**

- 5 rows dispositioned, 1 CLOSED and 3 NARROWED and 1 OPEN — [the sweep](../audit/2026-07-28-evidence-surface-triage-sweep.md) `## Dispositions 2026-08-01`
- S37's claimed shape present at the sweep date — `git show 3cc0b27d:skills/public/release/scripts/publish_release_narrative_gate.py`
- 0 adapter parameters on the two functions D45's remedy must reach — read of `read_gate_policy` and `evaluate_workflow` in `ci_local_gate_parity_lib.py`

**Bundle gate**

- `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review` completed at every slice boundary — the command's own `Closeout status: completed`
- 6551 tests passed and 0 failed in the broad standing suite — `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
- The final `--verification-lock` bundle run did NOT schedule broad pytest — unbacked: its changed set was markdown and artifacts only, so the standing-suite surface did not match; the broad suite was therefore run explicitly, on the line above, rather than claimed from that bundle
- Public-skill validation `next_action: none` — `python3 scripts/plan_cautilus_proof.py --repo-root . --detail`
- No `cautilus evaluate` run — unbacked: a stated non-claim of this goal; no live evaluator proof was requested or performed

**Non-claims**

- No release, no version bump, no tag, no publish. `quality-core.yml` is the only push-triggered workflow and declares `permissions: contents: read`.
- 4 bounded reviewer spawns, all `parent-delegated` with findings delivered inline. **No `verify --before` result is recorded for any window**, and 2 of the 4 reviews (Lane C's and the closeout-claims round) have no persisted fingerprint window at all — a shortfall against this goal's own High-Confidence Checks, recorded rather than implied satisfied.
- Lane B's two rounds produced no separate critique artifact — unbacked: their findings survive only as the parent's summary in this artifact's Slice Log, so 3 of the 4 spawns are attested by the party being reviewed rather than by a checked-in reviewer record.
- D46, D47, and D48 were not revisited and their refusals remain unarmed.

Retro: charness-artifacts/retro/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md
Host log probe: skipped: host-log-not-exposed: this Claude Code session exposes no token, timing, or tool-call log file a probe could read, so no goal-window metrics block was rendered and none is claimed anywhere in this artifact
Disposition review: charness-artifacts/critique/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows-closeout-claims-review.md
## User Verification Instructions

## Auto-Retro

Retro dispositions: issue #470 (recurs: the review-ordering item — the resolution critique must run BEFORE the irreversible issue close, and this run closed #467 then discovered the closure was wrong); issue #470 (recurs: the capability item — a shared assertion that a Created-gated floor's corpus measurement states a non-empty DATED denominator, so "0 refused" cannot be produced by grandfathering); applied: the memory rule "a clean measurement of my own work needs its denominator stated before it is believed", written into `test_the_corpus_measurement_the_non_arming_rests_on` (which fails both when nothing refuses and when the dated denominator collapses) and into the corrected denominator statements in this artifact's `## Final Verification` and the retro's Evidence Summary
Structural follow-up: issue #470 (recurs: the zero-denominator class recurred three times in this single run — a floor armed on an undatable corpus, an issue closed on a file that had left the changed set, and a local gate passing over a partial denominator — and #468 already records the sibling pattern of a deferred decision's remedy stored as unverified prose, so this is a repeat rather than a novel finding)

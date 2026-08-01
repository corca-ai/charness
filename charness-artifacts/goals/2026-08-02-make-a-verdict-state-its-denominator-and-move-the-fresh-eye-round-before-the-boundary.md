# Achieve Goal: Make a verdict state its denominator, and move the fresh-eye round before the irreversible boundary

Status: complete
Created: 2026-08-02
Activation: `/goal @charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Lane B — the resolution-critique floor reads the cited
  artifact's own `Fresh-eye satisfaction:` value.
- Current slice intent: make a self-authored resolution critique
  DISTINGUISHABLE from a parent/nested-delegated one at the issue-close
  boundary, and state explicitly whether the floor refuses on it. This names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: read `issue_resolution_critique.py` and
  `validate_critique_artifacts.py` and verify the premise (that the floor
  checks only for a `Critique #N: <path>` line and never reads the artifact's
  own satisfaction field) BEFORE shaping the change.
- Lane A: DONE, committed, reviewed (1 round, 1 blocker folded). Its
  two-round question is settled below.
- Round count for Lane A, recorded because the artifact contradicts itself:
  `## Discuss Before Activation` item (2) says Lane A owes TWO rounds; the
  plan critique's "Minors folded" paragraph then narrowed A to a payload-shape
  change and explicitly MOVED the two-round obligation to Lane B. The fold is
  the later shaping and it agrees with the repo contract, which triggers a
  second round on VERDICT-LOGIC changes — Lane A changed no verdict, pinned by
  a control test. Lane A ran ONE round; its blocker was a sync omission, not a
  verdict defect. Recorded rather than silently resolved.
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

Close the defect class the previous run proved it could not close by
inspection: a verdict that reads clean because nothing distinct ever checked it.
Two repairs, both narrowed by a plan critique that found the FIRST draft of this
goal asserting three things the tree contradicts:

1. **A partial denominator carries a numerator.** The changed-line gate already
   emits `unanalyzed_changed_pool_files`; what it never emits is the pair — how
   many of how many — on the paths a reader actually gets.
2. **A resolution-critique floor stops accepting a critique nobody else read.**
   `issue_resolution_critique.py` checks that a `Critique #N: <path>` line exists.
   It does NOT read that artifact's own `Fresh-eye satisfaction:` value, so a
   self-authored critique satisfies the floor at an irreversible boundary.
   **AMENDED 2026-08-02:** this item originally ended "— which is exactly what
   happened to #467". It is not. See the amendment in `## User Acceptance`: #467's
   critique was genuinely parent-delegated, and its failure was that the review ran
   AFTER the close. The mechanism claim — that the floor never reads the field —
   was verified and is true; only the worked example was wrong.

Both are P4 applications: a claim confirmed by a distinct observer, not by
re-reading the same proxy. Neither adds a gate.
## Non-Goals

- **Not a gate that checks gates.** Every repair here is a captured observable
  inside an EXISTING verdict, or an existing floor reading a field that already
  exists. If a slice starts wanting a new validator that audits other validators,
  stop.
- **Not arming a refusal on partial denominators.** Lane A discloses; whether the
  gate should REFUSE is D45's toll question and stays the operator's.
- **Not re-implementing what HEAD already has.** The first draft of this goal
  proposed adding `unanalyzed_changed_pool_files` (already emitted, 5 tests), a
  precondition before `close_with_comment` (already refuses before any backend
  call), and a host-blocked degradation valve (already shipped). All three were
  cut by the plan critique. Read `## Plan Critique Findings` before the first
  slice.
- **Not a shared corpus-measurement helper for the `goal_artifact_*` floors.**
  Cut: no floor performs a corpus measurement in code, so the helper had no
  caller. The measurement that motivated it lives in a test.
- **Not arming D45–D49.** All stay deferred.
- **Not a release**, and not the E-cluster.
- **Not a rewrite of frozen artifacts.**
## Boundaries

- **External side-effect scope, enumerated in full.** (1) `git push` to `main`
  of work this goal creates, plus the `quality-core` runs those pushes trigger.
  (2) Any issue FILED or CLOSED by a lane or the closeout retro, including
  #469 and #470 — both approved by the operator on 2026-08-02, and both subject
  to Lane B's new ordering rather than the old one. NOT approved and NOT carrying forward:
  a publish, a tag, a version bump, or any `cautilus evaluate` run. **Every
  clause of this list is enumerated because the last two runs each found a write
  their non-claims block had omitted.**
- **Phase-scoped approval.** Push approval covers the phase that requests it and
  does not carry to a later phase; batch local proof and run remote CI once over
  the bundled state rather than per slice.
- In scope (Lane A — the denominator observable):
  [check_changed_line_mutation_coverage.py](../../scripts/check_changed_line_mutation_coverage.py)
  (which already COMPUTES `unanalyzed_changed_pool_files` and prints a warning,
  then returns PASS anyway — so this is a verdict-shape change, not new
  measurement), and the `goal_artifact_*` floor family's corpus-measurement
  helpers in [skills/public/achieve/scripts](../../skills/public/achieve/scripts).
- In scope (Lane B — review ordering): the `issue` skill's close path,
  [issue_tool.py](../../skills/public/issue/scripts/issue_tool.py)
  `close-with-comment` and
  [issue_resolution_critique.py](../../skills/public/issue/scripts/issue_resolution_critique.py),
  plus [coordination.md](../../skills/public/achieve/references/coordination.md)
  where the ordering is documented.
- Also in scope everywhere: regression tests for each change, and the generated
  `plugins/charness/` mirror of every touched skill file. Sync mirrors before
  validators (`mutate -> sync -> verify`).
- Portable: both lanes touch PUBLIC skills, so any new observable must be
  expressible by a consumer repo that does not use this repo's artifact
  conventions, and any new precondition must degrade on a host that cannot spawn
  a reviewer — the same shape `Disposition review: skipped: host-blocked-subagent:`
  already answers.
- Stop conditions: (1) if a repair would require editing a frozen artifact,
  record instead. (2) If making the changed-line gate refuse on a partial
  denominator turns this repo's own lane permanently red, STOP — that is D45's
  toll question and it is the operator's call, not a lane to work around.
  (3) If a hard precondition on issue close would strand closes on a
  subagent-blocked host, do NOT ship it as a hard precondition; ship the
  degradation valve with it or record instead.
## User Acceptance

- **Lane A:** the changed-line gate's emitted payload carries an explicit
  analyzed/changed COUNT PAIR on every path that emits a verdict — not only on
  `_blocking_report`, where the numerator list lives today. Pinned by a fixture
  on a non-blocking path whose payload states both numbers. **Refusal behaviour
  is unchanged, pinned by a control test.** Whether a partial denominator should
  refuse is explicitly NOT in this acceptance.
- **Lane B:** `issue_resolution_critique` reads the cited critique artifact's
  `Fresh-eye satisfaction:` value and distinguishes `parent-delegated` /
  `nested-delegated` from a self-authored or absent one. Acceptance is that the
  distinction is RECORDED in the floor's report and surfaced at the close path;
  whether it REFUSES is a separate call the slice must state explicitly and
  defend, because a hard refusal strands closes on a host that cannot spawn —
  and the existing `Critique: blocked <signal>` valve is the precedent for how
  that degrades. Pinned by three fixtures: delegated, self-authored, blocked.
  **AMENDMENT (2026-08-02) — the #467 worked example is WITHDRAWN.** This criterion
  originally read: "The #467 closure is the worked example: its critique existed and
  validated at close time, and was still a same-observer artifact." That is FALSE,
  and the run verified it before building on it.
  `charness-artifacts/critique/2026-08-01-467-mutation-regression-resolution-critique.md:6`
  records `Fresh-eye satisfaction: parent-delegated` with `Delivery state:
  findings-received`, and the correction comment on the issue says the review was
  "run after the close" (closed 14:25:16Z, corrected 14:35:22Z). #467 was an
  ORDERING failure, not a self-authorship one, so **this floor would not have
  prevented it** — the ordering rule that would is now prose in
  `skills/public/achieve/references/coordination.md`. The self-authored fixture is
  therefore SYNTHETIC, and the hole it closes was demonstrated independently: the
  floor never opened the cited file at all. Recorded as an amendment rather than
  silently rewritten, matching the precedent in `## Context Sources` item 2.
- **Global:** every figure in `## Final Verification` carries `<value> — <source>`
  or `<value> — unbacked: <why>`, and every corpus measurement states its
  denominator in DATED artifacts. The figure-form floor reads this goal but is
  NON-BLOCKING (D49), so this is the author holding the record to a standard the
  validator does not enforce — the same posture the previous goal took, and for
  the same reason.
## Agent Verification Plan

### Low-Cost Checks

- **verify a named remedy's premise BEFORE shaping a slice around it** — this
  goal's own first draft failed exactly here, on three of three lanes
- the dup-ratchet at the FIRST edit to a gated file in each slice, never at the
  closeout aggregate
- `check_python_lengths.py --headroom` before a large addition; when it refuses,
  SPLIT the concept
- targeted `pytest` AND `ruff check` in the same breath — the last run spent two
  closeout re-runs on import-order rejections after a green suite
- after any scripted string edit, assert the superseded text is absent; when a
  number replaces a number, grep for the old value
- **never edit a markdown artifact by `text.index("## Heading")`** — the last run
  destroyed the same goal artifact twice that way, because the heading string
  also appears in the artifact's own prose. Match at line start.

### High-Confidence Checks

- one bounded fresh-eye round per slice; TWO for Lane B, which changes verdict
  logic on a proof surface
- `reviewer_boundary_fingerprint.py snapshot --out <per-window path>` around each
  review, **and a `verify --before` whose result is RECORDED** — the last run
  snapshotted three windows and recorded no verify result for any
- a closeout-claims review by a DISTINCT observer before the complete flip; it
  found four blockers last run, all in claims
- every corpus measurement re-stated with its DATED denominator before it is
  believed

### External Or Live Proof

- `git push` to `main` and the remote CI it triggers, confirmed per P4 by a
  different observer AND a different evidence channel than the push exit code.
- Closing #469 / #470 if a lane resolves them — through Lane B's repaired
  ordering, with a delegated (not self-authored) resolution critique.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.
## Slice Plan

Two lanes plus closeout. Each independently closable; stopping between lanes is
clean. The plan critique cut two lanes and re-aimed the rest, so the row bodies
below are the SECOND shaping, not the first.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Emit an analyzed/changed COUNT PAIR on every verdict-emitting path of `check_changed_line_mutation_coverage.py` | The field exists; the pair does not. A reader of a PASS gets a denominator list on some paths and no numerator on any, so "49 of 51" is reconstructable only by `len()`-ing two lists that are not both always present. This is the residual after the critique cut the rest of the lane | A fixture on a NON-blocking path whose payload states both counts; a control test proving PASS/FAIL behaviour is unchanged; the existing `unanalyzed_changed_pool_files` assertions still green (4 asserts — not the 5 the plan critique's B1 stated; re-measured this run rather than inherited) | done |
| B | Make `issue_resolution_critique` read the cited artifact's `Fresh-eye satisfaction:` value, so a self-authored critique is distinguishable from a delegated one at the close boundary | The real #467 defect, found by the plan critique. The floor's presence check is satisfiable by an artifact the closing agent wrote, at an irreversible boundary, and `validate_critique_artifacts.py` ALREADY enforces the form of the field the floor is not reading. Verdict logic on a proof surface, so TWO bounded rounds | Three fixtures (delegated / self-authored / blocked); the floor's report carrying the distinction; an explicit, defended statement of whether it refuses, with the degradation path named | done |
| C | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `./scripts/run-quality.sh`; `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | pending |
## Operator Decision Queue

- Decision: whether #469 and #470 should be closed, narrowed, or left open. This run did NOT close either.
- Owner: operator (repo owner)
- Why deferred: closing them was approved *if a lane resolved them*, and neither lane resolves either issue's full requested outcome. #469 asks for the changed-line gate's partial-denominator behaviour to be settled; Lane A disclosed the pair and deliberately left the refusal question to D45. #470's two follow-ups are the two lanes, but its second follow-up is MIS-STATED (the resolution-critique precondition already fires before the close; what was missing is a distinct observer reading the critique) — closing it as written would ratify a false description. Local progress was never blocked by this.
- Unblock action: either correct #470's second follow-up body and close both against this goal's two commits, or narrow each to the residual it still names and leave open.
- Revisit trigger: the next goal that touches D45 (the changed-line refusal toll) or the issue-close boundary.

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

- Routing: impl — selected from installed skill metadata as the owner of the code-writing phase both lanes spent their time in; achieve operated the goal lifecycle around it, issue owns the close-path floor Lane B changes, quality owns the validation posture consulted before the closeout gate, critique supplied the four bounded rounds (1 on Lane A, 2 on Lane B, 1 closeout-claims), and retro produced the closeout review
- Gather: n/a — no external source; every input is checked into this repo or is this repo's own GitHub issue state, read read-only via gh.
- Release: n/a — no version bump, no install-manifest edit, no publish. Explicit non-claim.
- Issue closeout: n/a — #469 and #470 are named in ## Context Sources as THIS GOAL'S SUBJECT (its two lanes, and Lane A's concrete subject), and closing them was pre-approved IF a lane resolved them. Neither was closed, because neither lane resolves either issue's full requested outcome. Calling them mere context would understate what they were; the reasons and the operator's unblock action are in ## Operator Decision Queue. One issue WAS filed this run: #471.

Proof-surface dispositions (one line per added path, per the new-proof-surface advisory):

- `Fresh-eye pass: skills/public/issue/scripts/issue_critique_observer.py — IS a proof surface, and two bounded rounds found seven blockers in it. Class (h), a self-declared field deciding whether the surface's own floors run, is literally what this module reads, and the contract gate that decides whether it runs was measured INERT in this repo (round 1 B1). Class (g), fenced text read as the author's own assertion, was live via unhandled `~~~` fences. Class (f), a denominator silently narrowed, appeared as three successive over-blocks on the honest corpus, each caught by re-measuring 133 citable resolution critiques rather than by inspection. Classes (a)-(e) checked, none found. Round-2 repairs are accepted-unreviewed per the two-round cap.`
- `Fresh-eye pass: scripts/changed_line_scope_counts.py — IS a proof surface (it authors what a gate's verdict says about its own scope); one bounded round, one blocker (an unsynced plugin mirror that would have shipped the un-repaired gate plus a ModuleNotFoundError), plus a class-(f) finding folded: its docstring claimed an equal count pair means nothing was left out, which is false on an --allow-dirty run.`

Public-skill validation decision (required because this slice edits `achieve` and `issue`; consulted `plan_cautilus_proof.py --detail` first, per repo policy):

- `Validation: deterministic validation owns this closeout. plan_cautilus_proof reports run_mode: ask, proof_kinds: none, next_action: none — routine live Cautilus proof is NOT required for prompt-affecting paths, and a cautilus evaluate run is an explicit non-claim of this goal (## Boundaries). No maintained scenario coverage is changed and evals/cautilus/scenarios.json is NOT mutated: both lanes change validator/floor CODE and its tests, not the skill prose a scenario exercises, and the behavior change is pinned by 24 + 12 deterministic tests plus a corpus measurement with a stated denominator. `issue` is evaluator-required and `achieve` is hitl-recommended; the dogfood-contract freeze follow-ups are recorded as unactioned in ## Off-Goal Findings rather than silently satisfied.`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: APPROVED by the operator on 2026-08-02, three items. (1) IRREVERSIBLE SIDE EFFECTS — `git push` to `main` of work this goal creates plus the remote CI each push triggers, AND closing #469 / #470 if a lane actually resolves them. Approved explicitly and scoped to this goal; the previous goal's push approval was scoped to ITS Lane A and did not carry forward, and this one does not carry forward either. Confirmation will follow the north star's P4: a different observer AND a different evidence channel than the push command's exit code. Note the ordering constraint the approval creates: closing #469/#470 is exactly the boundary Lane B is repairing, so those closes must go through Lane B's NEW order — resolution critique and its fresh-eye round BEFORE the close call, not after. The previous run got that backwards on #467 and had to post a public correction. (2) PROOF-SURFACE AUTHORING — Lane A changes what a gate's verdict record says, which the north star classifies as an irreversible boundary in its own right ("a proof surface that fails open" propagates to every consuming repo and is silent by construction). Resolved by requiring TWO bounded rounds on Lane A rather than one, and by fencing the refusal question out of acceptance entirely. **AMENDED 2026-08-02, in place so an operator reading this approved term is not misled:** the plan critique's own "Minors folded" paragraph subsequently narrowed Lane A to a payload-shape change and MOVED the two-round obligation to Lane B. Lane A ran ONE round. The closeout-claims reviewer checked that reading against `operating-contract.md` and found it contract-conformant — the second-round trigger is changing what a surface DECIDES, and Lane A's exit codes are pinned unchanged by a control test — but also found that recording the departure only in the transient `## Active Operating Frame` was not enough. (3) PROOF-LEVEL NON-CLAIMS — no release, no tag, no version bump, no `cautilus evaluate`, and Lane A2 migrates ONE floor rather than all five, naming the rest as unmigrated. Resolved: stated rather than implied, so a reader does not infer a sweep that did not happen.

## Slice Log

### Slice 1: Lane A — the denominator observable

- Objective: Emit an analyzed/changed COUNT PAIR (`changed_pool_file_counts`) on every verdict-emitting path of the local changed-line mutation gate. Disclosure only: refusal behaviour unchanged.
- Why this approach: The two lists the gate already emits are not both present on any single path, so "1 of 2" was reconstructable by len()-ing on some paths and not at all on others. New module `scripts/changed_line_scope_counts.py` rather than an append: the gate was at 476/480 code lines, and Change Discipline says start a module rather than spill. The scope SPLIT (`apply_file_limit`) moved there with the scope REPORT so the module is a cohesive owner of scope arithmetic and not a D33 length-dodging companion; the gate ended at 468/480, lower than it started.
- Commits: `cf88b750` — Make every changed-line verdict state how many of how many it read. Critique artifact: `charness-artifacts/critique/2026-08-02-lane-a-changed-line-denominator-critique.md`.
- What changed: scripts/changed_line_scope_counts.py (new, 71 code lines); scripts/check_changed_line_mutation_coverage.py (import + alias, count pair in `_run_metadata` startup dict and `_emit_no_base_sha` as not-computed, real pair merged right after the limit split, `_apply_file_limit` added to `__all__`); tests/quality_gates/test_changed_line_scope_counts.py (new, 12 tests); one added assertion in tests/quality_gates/test_changed_line_mutation_coverage.py; regenerated plugins/charness/scripts/ mirror of both source files.
- Alternatives rejected: Rejected: making a partial denominator REFUSE — that is D45's toll question and is fenced out of this goal's acceptance. Rejected: shrinking the pair on an --allow-dirty run so it never overstates — the pair's population is the RANGE's, which keeps it comparable across runs; the uncommitted gap is disclosed by the sibling `dirty_pool_unverified` / `uncommitted_pool_files` keys instead, and a test now pins that reading. Rejected: declaring `scripts/changed_line_scope_counts.py` in attention-state-visibility.json — the gate fired on the word "skipped" in a docstring for a module that has no skip state, so the wording was the defect, not the registry.
- Targeted verification: pytest tests/quality_gates/test_changed_line_scope_counts.py tests/quality_gates/test_changed_line_mutation_coverage.py -> 54 passed. 227 passed across the 10 modules that reference this gate or prepush_focused (test_degradation_branch_coverage, test_new_proof_surface_advisory, test_mutation_coverage_consumer_execution, test_changed_line_coverage_gate, test_prepush_focused_changed_line_coverage, test_subprocess_only_coverage_advisory, test_a_declaration_is_not_its_own_corroboration, test_mutation_coverage_producer, test_scaffold_changed_line_coverage, test_slice_closeout_reporting). run_slice_closeout.py --skip-broad-pytest -> PASS on all 20 verify commands (pre-lock; broad pytest deliberately deferred to the locked bundle). Broad pytest NOT run at this slice — non-claim.
- Test duplication pressure: 12 new tests in a new module. The seeding helpers are IMPORTED from the sibling test module rather than re-declared (precedent: test_dup_ratchet_unestablished_inputs.py), so no clone family was added; check_dup_ratchet.py --summary passed in closeout. One near-duplicate the reviewer flagged (M3) was resolved by giving the first test a distinct claim — that the stderr and JSON channels now agree — rather than by deleting it.
- Critique: ONE bounded fresh-eye round, typed `bounded-reviewer` (Read/Grep/Glob only), parent-delegated, shared parent worktree. reviewer_boundary_fingerprint.py snapshot .charness/reviewer-boundary/lane-a-round1.json; verify --before result RECORDED: ok true, verdict "clean", no drift. ONE BLOCKER, parent-verified before folding: B1 — the packet's claim "no skill files, so no plugins/ mirror is involved" was FALSE; packaging_lib.py:248-250 mirrors the whole scripts/ tree, so the export would have shipped the un-repaired gate and a ModuleNotFoundError for the new module. Verified by parent (plugins/charness/scripts/changed_line_run_trust.py exists as the mirrored twin of the previous split; the new module did not) and folded by running the sync. Minors folded: M1 (the new module's own docstring claimed an equal pair means "nothing was left out", which is false on --allow-dirty — this goal's exact defect class in the code written to fix it) rewritten and pinned by a new test; M2 (the SCOPE_MISMATCH path's pair depends on the rebind landing before the check, untested) closed by an assertion in the existing mismatch test; M3 folded as above; M5 (`_apply_file_limit` re-export absent from `__all__`, the exact shape a recorded ruff --fix incident once deleted) added. M4 (the computed pair does not restate its population) folded into the docstring rather than the payload. Reviewer confirmed invariants 1-4 hold: all 8 emit sites carry the key, and main() differs from HEAD by exactly the one inserted rebind statement.
- Off-goal findings: none from this lane — the lane's own reviewer findings were all in-scope and folded; #471 came out of Lane B.
- Lessons carried forward: The packet I handed the reviewer asserted a non-claim I had not checked ("no plugins/ mirror is involved"), and that unchecked assertion was the round's only blocker. A slice packet's non-claims are claims; they need the same premise check as the plan's remedies.
- Metrics: unbacked: the host exposes no per-turn token or wall-clock log to this agent; no efficiency figure is stated for this slice.

### Slice 2: Lane B — the close boundary reads who reviewed

- Objective: Make the issue-close resolution-critique floor READ the cited artifact's own `Fresh-eye satisfaction:` value, so a record stating that no distinct observer read the resolution is distinguishable from one stating a delegated review — and decide, explicitly, whether it refuses.
- Why this approach: The floor checked that a `Critique #N: <path>` line exists and binds; it never opened the file. New portable module `issue_critique_observer.py` classifies delegated / blocked / blocked-unsubstantiated / undelegated / absent; `issue_resolution_critique.py` records it on both report paths and ANDs `ok` with the refusals; the close carrier prints the specific reason and now surfaces the critique's advisories on a PASSING close too (previously the one carrier that writes to GitHub was the quietest). REFUSAL DECISION, stated and defended: refuses `undelegated` / `unreadable` / `blocked-unsubstantiated` / `absent`, but ONLY in a repo whose AGENTS.md carries the delegation contract, and NEVER for an artifact predating the typed contract (2026-07-05). Degradation path: `blocked <host-signal>` passes with a REVIEW advisory, so a subagent-blocked host is never stranded — stop condition (3) satisfied.
- Commits: `31303275` — Let the close boundary read who actually reviewed the resolution. Critique artifact (both rounds): `charness-artifacts/critique/2026-08-02-lane-b-close-boundary-observer-critique.md`.
- What changed: skills/public/issue/scripts/issue_critique_observer.py (new); issue_resolution_critique.py; issue_close_comment_floor.py; issue_close.py; issue_markdown_lib.py (`~~~` fences, per-marker close tracking); skills/public/achieve/references/coordination.md (the ordering rule); tests/quality_gates/test_issue_critique_observer.py (new, 24 tests); one assertion in test_issue_close_comment_floor.py; regenerated plugins/charness/ mirror.
- Alternatives rejected: Rejected: advisory-only. At an irreversible public boundary a record that positively states no distinct observer read the work should not close silently, and the honest escape costs one line. Rejected: refusing everywhere rather than gating on the delegation contract — that holds every consuming repo to a convention it never adopted. Rejected: letting `absent` pass under the contract, which was the FIRST design; round 1 proved the rationale false (the authoring validator runs at the COMMIT boundary and close-with-comment performs no commit), so omission was a live bypass. Rejected: prefix-matching the typed value — ten checked-in artifacts write `satisfied — parent-delegated ...`. Rejected: value-wide negation scanning, which demoted 11 honest post-cutoff artifacts on the words 'no blockers'. NOT fixed, recorded as off-goal: `validate_critique_artifacts.has_repo_delegation_contract` is broken the same way B1 was and is still inert in this repo.
- Targeted verification: pytest tests/ -k 'issue or critique or closeout' -> 914 passed. pytest of the new module -> 24 passed. ruff clean. CORPUS MEASUREMENT WITH ITS DENOMINATOR, pinned by a test: of 133 citable issue-resolution critiques in charness-artifacts/critique/ (packets and plan critiques excluded — they are never cited as resolution evidence), 0 would be refused. Two earlier versions of the reader would have refused 11 and 6 respectively, both times honest records. Contract gate confirmed LIVE: repo_requires_delegated_observer(Path('.')) is True (it was False before the round-1 repair). Broad pytest NOT run at this slice — non-claim.
- Test duplication pressure: 24 tests in a new module; helpers imported from issue_closeout_support rather than re-declared. Round 2 flagged that the unit tests used a local COPY of the fence stripper, proving the injected callable rather than the wired-in one; they now import the production function — which mattered, because the two had already diverged on `~~~`.
- Critique: TWO bounded fresh-eye rounds, typed `bounded-reviewer`, parent-delegated, shared parent worktree; the second round is owed because this slice changes verdict logic on a proof surface. Both windows fingerprinted; both verify results RECORDED as `parent-attributed` / drift [] after declaring the parent's own repair paths. ROUND 1: five blockers, all parent-verified, all folded — B1 the refusal was INERT in this repo (the contract marker substring-matched an unbolded literal against an AGENTS.md that writes `**already delegated**`; measured False), B2 the reader missed the corpus's bold-bullet form so bolding the key was a two-asterisk bypass, B3 `blocked` was a magic word with no signal floor, B4 the `absent`-passes rationale was false, B5 prefix matching would have refused ten honest historical artifacts. ROUND 2 read the REPAIRS and found TWO blockers that round 1 could not have seen, both introduced BY the repairs: B-R1 matching delegated tokens by containment before testing `blocked` turned the valve's most natural phrasing into a completed delegation AND made the new signal floor bypassable in 24 characters — cheaper than the bare word B3 had just closed; B-R2 the section-body fix still refused six checked-in artifacts. Both parent-verified by direct execution before folding. Folding B-R1 introduced a THIRD over-block (value-wide negation markers demoting 'no blockers'), caught by re-measuring the corpus rather than by a third round; narrowed to a negation window and re-measured to 0/133. Round-2 minors folded: non-UTF-8 read now errors='replace' (it would have tracebacked out of the close command), deeper ATX headings, the false parity claim about has_repo_delegation_contract. Accepted-unreviewed per the two-round cap: the section-body empty-value label and the _refusal_reason else-branch.
- Off-goal findings: scripts/validate_critique_artifacts.has_repo_delegation_contract has the SAME unbolded-literal defect round 1 found in the new module, so repo_has_delegation is False in this repo and whatever it gates (including _check_forbidden_blocker_phrases) is inert. Confirmed by both reviewers. Not fixed here: different gate, different boundary, and repairing it TIGHTENS an authoring gate across 400+ artifacts, which needs its own before/after measurement. To file at closeout.
- Lessons carried forward: The goal's own worked example was wrong and I checked it before building: the #467 critique records parent-delegated with delivery evidence, and the correction comment says the review 'run after the close'. #467 was an ORDERING failure, not a self-authorship one — so this floor would NOT have prevented it. The hole is real and independently demonstrable; the motivation had to be re-derived from that fact rather than inherited. Second lesson, mechanical: I ran both boundary verifies AFTER making repairs, so each needed parent-path declarations and rests on my testimony rather than a clean no-write window. Verify immediately when the reviewer returns.
- Metrics: unbacked: the host exposes no per-turn token or wall-clock log to this agent; no efficiency figure is stated for this slice.

## Context Sources

Follow these in order; a fresh session can reconstruct the whole originating
context without this session's memory.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — P4 and P5 are
   this goal's entire derivation. Read the "boundary (load-bearing)" section:
   authoring a proof surface IS an irreversible boundary, which is why Lane A
   owes two rounds.
2. [The preceding goal](./2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md)
   and its
   [closeout-claims review](../critique/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows-closeout-claims-review.md)
   — that run committed this goal's subject defect three times and had every
   instance caught by a reviewer rather than a gate. Its `## User Acceptance`
   carries an AMENDMENT recording a criterion it did not meet.
3. [Its retro](../retro/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md)
   — the waste analysis and the Goodhart/Feynman counterfactuals that argue for
   both lanes.
4. [issue #470](https://github.com/corca-ai/charness/issues/470) — this goal's
   two lanes, with the three instances that motivated them.
5. [issue #469](https://github.com/corca-ai/charness/issues/469) — Lane A1's
   concrete subject, with both payloads quoted.
6. [The #467 resolution critique](../critique/2026-08-01-467-mutation-regression-resolution-critique.md)
   — Lane B's fixture: what a closure looks like when its review runs afterward.
## Interview Decisions

Shaped from the previous run's own findings rather than a fresh interview, so
the decisions below record the design space a fresh session should see.

1. **Which of the three recurrences to repair?** Family considered: {the local
   gate's partial-denominator PASS; the Created-gated floors' arming corpus; the
   issue-close review ordering; all three}. **Chosen: all three, as two lanes** —
   the first two are the same repair at two scales (a verdict stating its scope)
   and share a slice boundary; the third is a different mechanism and gets its
   own lane. Rejected: picking one, because the previous run's evidence is that
   this class recurs across surfaces within a single session, so a single-surface
   fix would leave the pattern intact. Anti-anchoring: `axis: repair register` —
   the design varies on whether the fix is a refusal or a disclosure. Disclosure
   is chosen deliberately; the refusal question is D45's toll and is fenced out
   by stop condition (2).
2. **Should Lane A arm a refusal on partial denominators?** Family considered:
   {refuse; disclose only; disclose now and defer the refusal}. **Chosen:
   disclose only, refusal explicitly out of acceptance.** Rejected: refusing,
   because files legitimately map to no standing test and a hard refusal would
   block ordinary pushes — the same toll D45 refuses to pay unilaterally, and
   the same mistake D49 made by arming on a corpus that could not object.
   Anti-anchoring: `single-point: this repo's mapping coverage` — the refusal may
   well be right in a repo where every pool file maps; it is a property of this
   corpus, not a standing policy.
## Plan Critique Findings

Reviewer provenance: one bounded fresh-eye round, typed `bounded-reviewer`
(read-only, Read/Grep/Glob only), parent-delegated, in the shared parent
worktree. It read the plan, the north star, the previous goal, and every
in-scope surface.

**Four blockers, three of them the plan asserting what the tree contradicts —
the same ratio as the previous goal's plan critique.** All four folded, and each
was parent-verified before folding.

- **B1 — Lane A1's objective already existed.** The plan said the gate emits
  `unanalyzed_changed_pool_files` only to stderr. It is merged into `metadata` at
  `check_changed_line_mutation_coverage.py:502` and rides every downstream
  payload, with five assertions in
  `tests/quality_gates/test_changed_line_mutation_coverage.py`. Activating that
  lane would have produced a closeout claiming a pre-existing repair — the exact
  class this goal exists to close. Folded: Lane A re-scoped to the real residual,
  the missing count pair.
- **B2 — Lane B's premise was false.** `close_with_comment` already evaluates the
  close-comment floor at `issue_close.py:87-92` and raises BEFORE `_run_backend`
  at `:129`; the message says "refusing before any GitHub mutation". The
  host-blocked valve already exists (`issue_resolution_critique.py:82-91`), and
  the test the acceptance asked for already exists. What ran late on #467 was the
  fresh-eye round ON the critique, not the requirement. Folded: Lane B re-aimed
  at the actual gap — the floor never reads the artifact's own
  `Fresh-eye satisfaction:` value, so a self-authored critique passes.
- **B3 — Lane A2's named in-scope surface does not exist.** No `goal_artifact_*`
  module performs a corpus measurement; every floor is per-artifact `check(text)`.
  The D49 measurement lives in `test_the_corpus_measurement_the_non_arming_rests_on`,
  already shipped and already dispositioned `applied:`. Folded: the lane is CUT,
  and the Non-Goals record why so it is not re-proposed.
- **B4 — the goal's self-application claim was backwards.** It said the previous
  goal was grandfathered by the figure-form floor. `is_floor_in_scope` is
  `created >= rule_date` and that goal is `Created: 2026-08-01` against a
  `2026-08-01` rule date, so it was IN scope; and this goal is not "the first
  created after the rule date". Folded: the Global acceptance now states the
  floor is non-blocking, which is the fact that actually matters.

**Minors folded:** "all five floors" was unbacked (there are nine `*_RULE_DATE`
constants in `skills/public/achieve/scripts`); Lane A's "touches no verdict
logic" contradicted the verification plan's "Lane A is entirely that class" —
resolved by narrowing A to a payload-shape change and moving the two-round
obligation to Lane B, which is the one that changes a verdict; stop condition (2)
was dead by construction once refusal was fenced out of acceptance, and is
restated as a live check on the current tree; and Lane A2's "every floor that
could be armed" quantifier repeated a blocker the PREVIOUS plan critique had
already folded once.

**Not folded, recorded as the lesson:** this plan was shaped around remedies the
previous run's retro and #470 named, without verifying their premises — which is
the rule
[implementation-discipline](../../docs/conventions/implementation-discipline.md)
Change Discipline states, and which the previous run itself promoted into that
contract. The rule fired at design time and was skipped at design time.
## Off-Goal Findings

Issues or deferred findings discovered during the run.

- **issue #471 (filed this run, readback-verified)** — `has_repo_delegation_contract`
  in `scripts/validate_critique_artifacts.py:167-172` is INERT in this repo: it
  substring-tests an unbolded marker literal against an `AGENTS.md` that writes
  `**already delegated**`, so `repo_has_delegation` is `False` and
  `_check_forbidden_blocker_phrases` has never fired here. Same defect the Lane B
  reviewer found in the new module's copy of the markers. Filed rather than fixed:
  repairing it makes a dormant authoring gate LIVE across 400+ checked-in critique
  artifacts, which needs its own before/after measurement — arming on an unmeasured
  population is the mistake this repo already made once. Both bounded reviewers
  agreed leaving it was defensible for lane scope.
- **Public-skill dogfood contract freeze, NOT actioned** — `plan_cautilus_proof.py`
  emits follow-ups to freeze the current `achieve` and `issue` consumer contracts in
  `docs/public-skill-dogfood.json`. Recorded here rather than silently satisfied:
  this slice changed floor CODE and its tests, not the skill prose a dogfood case
  exercises, so the freeze is a real follow-up and not a precondition this run met.
- **Not audited, stated as a non-claim** — whether the nine other `*_RULE_DATE`-gated
  floors in `skills/public/achieve/scripts` render verdicts with unstated
  denominators. The sibling search names the axis; no sweep was run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md
Host log probe: skipped: host-log-not-exposed: this Claude Code session exposes no per-turn token/time log to this agent, so any wall-clock or token figure here would be fabricated rather than measured; the goal window is recorded only as the commit range below.
Disposition review: charness-artifacts/critique/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary-closeout-claims-review.md

Every figure below carries `<value> — <source>` or `<value> — unbacked: <why>`.

- Lanes shipped: 2 of 2 — commits `cf88b750` (Lane A) and `31303275` (Lane B), `git log --oneline`.
- Bounded fresh-eye rounds: 4 — 1 on Lane A, 2 on Lane B (verdict logic on a proof surface), 1 closeout-claims; each is a checked-in critique artifact under `charness-artifacts/critique/2026-08-02-*`.
- Blockers found by those rounds: 21 — 6 (Lane A) + 5 (Lane B r1) + 2 (Lane B r2, both INTRODUCED by r1's folds) + 8 blocker-binned findings from the closeout-claims round, enumerated as F-rows in `charness-artifacts/critique/2026-08-02-lane-a-changed-line-denominator-critique.md`, `charness-artifacts/critique/2026-08-02-lane-b-close-boundary-observer-critique.md`, and `charness-artifacts/critique/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary-closeout-claims-review.md`. **This figure was first written as "9" BEFORE the closeout-claims round returned, with terms summing to 8 — a count stated for an observer that had not reported, which is this goal's own defect class committed in its own closeout. That reviewer caught it; it is restated post-hoc and recorded rather than quietly corrected.**
- Blockers found by a deterministic gate: 0 — unbacked: this is an absence, and no command can enumerate findings that no gate produced. It is an honest read of the run rather than a measurement: every F-row in the three `charness-artifacts/critique/2026-08-02-*` artifacts is attributed to a bounded reviewer, and no gate failure this run named one of them. `run_slice_closeout.py` did block twice (attention-state vocabulary, dup-ratchet), but on neither of the classes those rows describe.
- Boundary fingerprint windows: 3 snapshotted, 3 `verify --before` results recorded — `.charness/reviewer-boundary/lane-a-round1.json`, `lane-b-round1.json`, `lane-b-round2.json`; Lane A `clean`, both Lane B windows `parent-attributed` after declaring the parent's own repair paths.
- Critique artifacts the new refusal would block: 0 of 133 — the denominator is every `charness-artifacts/critique/*.md` whose FILENAME contains `resolution` or `issue`, minus `-packet.md`. That is a filename heuristic, not a semantic class: it also admits disposition reviews, code critiques and release critiques. Independently recounted by the closeout-claims reviewer as exactly 133. `test_the_corpus_this_refusal_would_actually_block_is_measured_with_its_denominator` asserts the ZERO and guards the denominator only against collapse (`len(citable) > 100`); it does not pin 133.
- Three earlier versions of that reader would have blocked 10, 6 and 11 of that same population — the prefix version (10), the first-section-line version (6), and the value-wide negation version (11); every blocked artifact was an honest record. The first two were caught by bounded reviewers, the third only by re-measuring. Each was measured with the same one-command sweep now pinned by `tests/quality_gates/test_issue_critique_observer.py::test_the_corpus_this_refusal_would_actually_block_is_measured_with_its_denominator`, run against the intermediate reader before each fold; the F-rows are F5/F7 in `charness-artifacts/critique/2026-08-02-lane-b-close-boundary-observer-critique.md` and the third is recorded in that artifact's fold note. These numbers are why the contract gate and the date grandfather exist; the earlier "11 and 6" phrasing silently dropped the first of them.
- Contract gate state before repair: `False`; after: `True` — `repo_requires_delegated_observer(Path('.'))`, run directly against the checked-in `AGENTS.md`.
- Changed-line gate size: 476 -> 468 of 480 code lines — `check_python_lengths.py --headroom`; it ended smaller than it started because the scope split moved out with the scope report.
- Focused tests green at closeout: 1043 — `pytest tests/ -k "issue or critique or closeout or changed_line"`.
- Push to `main`: `5839df60..24bf8c6b` — confirmed per P4 by a DIFFERENT observer on a DIFFERENT channel than the push exit code: `gh api repos/corca-ai/charness/commits/main --jq .sha` returns `24bf8c6b81d716355cca20ac7b466cb284b2f3cc`.
- Remote CI: `Quality Core` on `24bf8c6b` — `completed/success`, read from `gh run list` (GitHub's verdict, not the local gate's).
- Local pre-push gate: 82 passed, 0 failed — the `git push` hook run. It REFUSED the first attempt on nine uncovered changed lines in this goal's own two new modules, all degrade branches; commit `24bf8c6b` walked them and changed-line coverage went to `clean`, 7 of 7 pool files analyzed.
- Broad pytest: 6595 passed — `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`, run once over the committed bundle at closeout. Recorded precisely because the locked `run_slice_closeout.py --verification-lock` run did NOT select broad pytest: by then the changed set was markdown-only, so the gate had nothing python-shaped to run and would have reported `completed` beside a broad proof that never happened. Both lane closeouts ran with `--skip-broad-pytest`, so this is the run's only broad proof.
- Token/time efficiency figures: unbacked: the host exposes no usage log to this agent; none are stated.

## User Verification Instructions

Every command is read-only unless noted.

1. **The two lanes are on `main`.** `git log --oneline -3` shows `cf88b750`
   (Lane A) and `31303275` (Lane B), plus this closeout commit.
2. **Lane A's acceptance — the count pair on every verdict path.**
   `python3 -m pytest tests/quality_gates/test_changed_line_scope_counts.py tests/quality_gates/test_changed_line_mutation_coverage.py -q`
   → 54 passed. The control test
   `test_disclosing_the_denominator_does_not_change_the_verdict` is the one that
   proves the verdict did not change.
3. **Lane B's acceptance — the three fixtures and the corpus measurement.**
   `python3 -m pytest tests/quality_gates/test_issue_critique_observer.py -q`
   → 24 passed.
   `test_the_corpus_this_refusal_would_actually_block_is_measured_with_its_denominator`
   is the one that fails if the refusal starts blocking honest artifacts again.
4. **The refusal is live here, not inert.**
   `python3 -c "import importlib.util,pathlib; s=importlib.util.spec_from_file_location('o','skills/public/issue/scripts/issue_critique_observer.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.repo_requires_delegated_observer(pathlib.Path('.')))"`
   → `True`. Before the Lane B round-1 repair this printed `False`, and every
   refusal was dead.
5. **Broad proof.** `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
   → 6595 passed. Run explicitly rather than inferred from the locked closeout:
   that gate reported `completed` without selecting broad pytest, because by then
   the changed set was markdown-only. A `completed` there is not a broad-proof
   claim, and reading it as one is the class this goal exists to close.
6. **What was NOT done**, and should not be inferred: no release, tag, version
   bump, or `cautilus evaluate` run; #469 and #470 are still OPEN and are the
   operator's call (see `## Operator Decision Queue`).


## Auto-Retro

Retro dispositions: applied: `docs/conventions/operating-contract.md` — verify the reviewer boundary fingerprint IMMEDIATELY on the reviewer's return, before any parent write (the rule went into the contract that already owns fingerprint discipline, because the failure is ordering and the tool cannot detect it); applied: `tests/quality_gates/test_issue_critique_observer.py::test_the_corpus_this_refusal_would_actually_block_is_measured_with_its_denominator` — measure a changed refusal against the real checked-in corpus and pin the number with its denominator, the one place this run converted review judgment into a gate and the one that caught the over-block inspection missed; applied: `charness-artifacts/retro/recent-lessons.md` — a slice packet's non-claims are claims and need the same premise check as a plan's remedies, which was the only blocker in Lane A's review; issue #471 (novel: no prior instance in this repo's ledger of a gate keyed on matching repo prose being measured inert) — a guard whose own activation condition is never tested; out-of-scope: whether the other `*_RULE_DATE` floors in `skills/public/achieve/scripts` render verdicts with unstated denominators was NOT audited this run, and is recorded as an explicit non-claim in `## Off-Goal Findings` and carried to the handoff rather than implied clean
Structural follow-up: applied: tests/quality_gates/test_issue_critique_observer.py — the corpus-measurement test is the transferable guard the retro's waste analysis names (three successive over-blocks, only the third caught by measuring rather than by inspection); the ordering and packet-non-claim lessons land in the operating contract and recent-lessons respectively.

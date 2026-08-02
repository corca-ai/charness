# Achieve Goal: Fix the rule that cannot fire where it was written to, then count the rest

Status: complete
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Lane A COMPLETE (#475 ladder shipped, two bounded rounds). Next: Lane B — write the can-this-fire predicate, then measure.
- Current slice intent: Lane B — count the rest of the class with a written-down
  predicate and a stated denominator. Lane A's intent (the #475 ladder) is closed.
  This names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: Lane B. Write the predicate BEFORE reading the population,
  then enumerate `*_RULE_DATE` constants, `validate_*` / `check_*` scripts,
  AND the contract/reference surfaces an agent reads. #473 is a known member;
  #476 (filed this run) is a measured member already.
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

One class, four known instances, and the operator hit the worst one directly:
**a rule that cannot fire in the situation it was written for.** It emits no
failure, no log line, no ticket — the north star's hardest-to-see shape.

- **#471** — `has_repo_delegation_contract` compared a literal against prose this
  repo writes bolded, so it returned False in the repo that authored the
  contract, and the check it gated had never executed. *(repaired 2026-08-02)*
- **#473** — `--fail-on-pre-rule-refusal` reports 0 for every possible corpus,
  because the predicates it compares are mutually exclusive by control flow.
  *(annotated, not repaired)*
- **#475** — bounded fresh-eye review is MANDATED by several skills and is inert
  in any repo that never ran `setup`, because
  [fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md)
  line 86 names exactly ONE source of the standing delegation request. The skill
  that mandates the review cannot authorize it. **Operator-reported.**
- A fourth, unnumbered: that same run's own repair shipped a population statement
  that hid a third intake bucket until a second review round read it.

Every one was found by a person, never by a gate. Four accidents is not a
measurement.

**Lane A fixes #475**, because it is the one costing the operator work right now
and because it is the class's clearest worked example. **Lane B then counts the
rest**, using #475 to widen the population the earlier draft of this sweep had
wrong: it enumerated only code (19 `*_RULE_DATE` constants across 14 files, 93
`validate_*` / `check_*` scripts), and #475 lives in a CONTRACT SURFACE an agent
reads. A sweep that only reads code cannot find the instance that started it.

**Lane C** is the affordance half of "make the next run better" (#474): surface
duplicate-ratchet pressure at the FIRST edit to a gated file, the way the
length-headroom advisory already does for its sibling trap. Three consecutive
runs wrote "run it early" into a plan and hit it at the closeout aggregate
anyway — a prose checklist fires exactly when nobody is reading the prose, which
is this goal's own thesis pointed at itself.

## Non-Goals

- **Not a validator that audits validators.** The north star names this as the
  anti-pattern applied to itself. Lane B's output is a one-off MEASUREMENT plus
  targeted repairs and dispositions, never a permanent meta-gate in CI.
- **Not arming anything on a corpus that cannot object.** No floor is widened and
  no rule date moves without a measured count of what it would newly refuse AND a
  recorded disposition. This repo has got that wrong twice (D49).
- **Not #472 — CLOSED as not planned 2026-08-02, before this goal was
  activated.** Widening `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES` polices an agent's
  self-report about why it skipped a review: it cannot make the review happen,
  and it is evaded by rewording, which is literally the defect that was reported.
  Its cause is #475, and once Lane A's ladder lands, "the user declined" becomes
  a legitimate record this rule must NOT refuse. Do not reopen it as a lane here.
- **Not removing `AGENTS.md` as a delegation source.** Lane A ADDS sources; repos
  carrying the block keep working unchanged.
- **Not loosening what counts as PROOF that a review ran.** Lane A changes where
  AUTHORIZATION may come from. A genuine tool refusal stays a blocker and a
  same-agent substitute stays forbidden.
- **Not the E-cluster**, not D40–D49, not `parse_created_date`'s remaining
  uncorroborated consumers.

## Boundaries

- **External side-effect scope, enumerated in full.** (1) `git push` to `main` of
  work this goal creates, plus the `quality-core` runs those pushes trigger.
  (2) Closing [#475](https://github.com/corca-ai/charness/issues/475),
  [#473](https://github.com/corca-ai/charness/issues/473) and
  [#474](https://github.com/corca-ai/charness/issues/474) if their lanes resolve
  them, each through the close path's floor with a DELEGATED resolution critique
  running BEFORE the close call. (3) Filing new issues for anything the sweep
  surfaces and does not fix — expected to be Lane B's main output.
  **(1) and (3) are APPROVED by the operator for this run (2026-08-02); (2) is
  approved in principle and still runs through the close path's floor.**
  NOT approved and NOT carrying forward: a publish, a tag, a version bump, or any
  `cautilus evaluate` run. The 2026-08-02 approval was scoped to that goal.
- **Phase-scoped approval.** Push approval covers the phase that requests it and
  does not carry to a later phase; batch local proof, run remote CI once over the
  bundled state.
- In scope (Lane A): the shared fresh-eye authorization rule, the public SKILL.md
  surfaces that mandate bounded review (`critique`, `quality`, `prove`, `setup`),
  and what `setup` writes or inspects for the delegation contract.
- In scope (Lane B): the `*_RULE_DATE` constants, the `validate_*` / `check_*`
  scripts, **and the contract/reference surfaces an agent reads to decide what it
  may do** — read for one question only: can this rule fire where it was written
  to fire?
- In scope (Lane B, repairs): only findings whose repair is unambiguous AND
  refuses nothing new. Everything else is filed, not fixed.
- In scope (Lane C): the closeout runner's advisory surface for #474.
- Also in scope: regression tests for each change and the generated
  `plugins/charness/` mirror of every touched exported file. Sync mirrors before
  validators (`mutate -> sync -> verify`).
- **No scratch repo.** An earlier draft asked for a throwaway repo as Lane A's
  behavioural proof. That was over-specified: the decision under test is made by
  an AGENT reading its own repo root's contract, so a subagent spawned from this
  session — whose repo root is charness, block and all — cannot reproduce it.
  Telling a subagent to pretend a temp directory is its repo root yields testimony
  about instructions the parent wrote, not behaviour. The honest split is in
  `## User Acceptance`: the agent proves the MECHANISM, and the BEHAVIOURAL proof
  is the operator re-running in the repo where they observed the refusal — a
  different observer and a different channel, and stronger than any synthetic repo.
- Stop conditions: (1) if Lane A's fix needs a trust posture the operator has not
  approved, STOP and bring the choice back. (2) If Lane B's population turns out
  materially larger than counted once the predicate is written, STOP and re-scope
  rather than silently sampling. (3) If any repair would newly refuse a
  checked-in artifact, it becomes an operator decision, not a fix. (4) If Lane B
  starts growing a permanent meta-validator, cut it back to the measurement.
- **Cut order if the session runs short: C, then B's repairs (keep B's
  measurement), never A.** Lane A is the operator's reported defect.

## User Acceptance

- **Lane A, the chosen shape (operator decision, 2026-08-02): a three-rung
  ladder, checked in order, with NO silent self-grant.**
  1. `<repo-root>/AGENTS.md` carries the `Subagent Delegation` block — delegate
     immediately, exactly as today. Repos that have run `setup` see no change.
  2. Else a structured, repo-owned opt-in (an `.agents/` field, not prose) —
     delegate. This is the rung that removes the prose-matching fragility #471
     proved: a bolded word must never again decide whether a rule fires.
  3. Else **ask the user once**, name the bounded reviewer scopes being
     requested, and on approval PERSIST the answer into rung 2 so the question is
     asked at most once per repo.
  The rejected alternative and why: letting a skill invocation self-authorize
  (pure option (a)) removes all friction and was defensible — `bounded-reviewer`
  is read-only, so the blast radius is token cost — but it would let the plugin
  grant itself spawn rights in every repo that installs it, with no per-repo
  record of what was authorized. The ladder keeps the grant the USER's while
  still closing the never-ran-`setup` case, at a cost of one question per repo.
- **A refusal to grant must be honoured and remembered.** If the user declines at
  rung 3, that is recorded too; the run degrades to `blocked <host-signal>`-shaped
  handling and does not re-ask every slice.
- **Lane A, agent-provable half (the MECHANISM):** the authorization rule names
  all three rungs and states why each is legitimate; the grant reaches every
  surface a consuming repo actually reads (the shared reference, the `setup`
  template, the generated block, and the compact-contract snippets — #458's
  propagation gap is the worked example of a fix that stopped at the authoring
  repo); repos that DO carry the block are unchanged, pinned by a test; a host
  that genuinely cannot spawn still degrades to `blocked <host-signal>`, pinned by
  a test.
- **Lane A, operator-provable half (the BEHAVIOUR):** the operator re-runs a
  task-completing `critique` / `quality` run in the repo where they observed the
  refusal, and a bounded reviewer actually spawns. **This session cannot prove
  it** — the decision is made by an agent reading its own repo root, and every
  agent this session can reach is rooted in charness, which carries the block.
  Recorded as an explicit non-claim until the operator confirms, never as
  "the rule now permits it, therefore it happens".
- **Lane B:** a checked-in sweep artifact stating, with its denominator, how many
  rules in the enumerated population were READ, how many can fire where they were
  written to, how many cannot, and what happened to each one that cannot
  (`repaired` / `issue #N` / `accepted: <reason>`). A reader must be able to tell
  "checked and live" from "not checked" — the absence of that distinction is what
  made four findings look like bad luck. #473 is resolved: either the
  forced-scope probe exists and the flag can now fail, or the flag is deleted as
  a guard that cannot guard, with a test pinning the choice.
- **Lane C:** editing a dup-ratchet-gated file surfaces the pressure BEFORE the
  closeout aggregate, pinned by a test, and #474 closes.
- **Global:** every figure in `## Final Verification` carries
  `<value> — <source>` or `<value> — unbacked: <why>`, and every corpus
  measurement states its denominator, what population that denominator selects,
  AND when it was taken (the 2026-08-02 run shipped a denominator measured before
  its own artifacts landed in the corpus it was measuring).

## Agent Verification Plan

### Low-Cost Checks

- **Verify the premise before shaping each slice, and ask what the operator
  actually observed before trusting a previous run's reviewer list.** The session
  that shaped this goal spent a lane on a phrase list that had nothing to do with
  the reported symptom; the root cause was one line in a reference.
- Re-read Lane A's two code consumers before touching them — both already degrade
  open, so "fixing" them would be a change with no defect behind it.
- **Write Lane B's predicate down BEFORE reading the population**, so "can this
  rule fire?" is answered the same way every time and the count means something.
- Run each measurement before the fold and again after, and record WHEN it was
  taken; a corpus containing this run's own artifacts moves under it.
- The dup-ratchet at the FIRST edit to a gated file. This is the fourth run to
  write this line; if Lane C lands it stops being a line and becomes a signal.
- `check_python_lengths.py --headroom` before a large addition; SPLIT the concept
  rather than shaving lines when it refuses.
- Targeted `pytest` AND `ruff check` in the same breath.
- File the issue first, then write its number into prose.
- Run `validate_handoff_artifact.py` before composing a commit message that
  touches the handoff, and preserve key order when editing a checked-in JSON
  policy file (diff the line count against the expected insert size).

### High-Confidence Checks

- One bounded fresh-eye round per slice; **TWO for Lane A** (it changes when an
  agent may spawn) and **TWO for any Lane B repair that changes what a rule
  refuses**, with round 2 reading the repairs.
- `reviewer_boundary_fingerprint.py snapshot` around each review, and
  `verify --before` run the MOMENT the reviewer returns, before any parent write.
- A closeout-claims review by a DISTINCT observer before the complete flip. It
  found 4 overstated claims last run, including a denominator stale for the tree
  that shipped.
- A slice packet's NON-CLAIMS get the same premise check as its claims.
- **The sweep artifact is itself a verdict surface**: its counts are claims and
  get re-derived by the reviewer, not read back.
- **Do not accept "the rule now permits it" as evidence that an agent did it.**
  A contract that reads correct and changes no behaviour is this goal's own
  failure mode, and is exactly how #471 stayed dormant.

### External Or Live Proof

- **The operator's own re-run** in the repo that showed the refusal is Lane A's
  central behavioural evidence, and it is NOT obtainable from this session. Write
  it into `## User Verification Instructions` with the exact command, and record
  the Lane A behaviour claim as unproven-in-session until it comes back.
- `git push` to `main` and the remote CI it triggers, confirmed per P4 by a
  different observer AND a different evidence channel than the push exit code.
- Closing #475 / #473 / #474 if their lanes resolve them, through the close
  path's floor, with a DELEGATED resolution critique whose round runs BEFORE the
  close call.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.

## Slice Plan

Three lanes plus closeout, ordered by operator cost. Each is independently
closable, so stopping between lanes is clean; the cut order is in `## Boundaries`.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Implement the operator-chosen three-rung authorization ladder (AGENTS.md, else structured opt-in, else ask-once-and-persist), propagate it to every surface a consuming repo reads, and hand the operator a one-command behavioural check | It is costing the operator work right now, it is the class's clearest worked example, and it defines the axis Lane B's earlier draft was missing — a rule inert in a CONTRACT surface, not in code | The amended authorization rule with each source's legitimacy stated; propagation to the `setup` template / generated block / compact-contract snippets; tests pinning block-carrying repos unchanged and genuine host blocks still degrading; the operator's verification command; two bounded rounds | done |
| B | Write the can-this-fire predicate, enumerate the population INCLUDING contract surfaces, measure, repair the unambiguous, file the rest — resolving #473 as the known member | Four instances of this class surfaced by accident, all found by people rather than gates. A fifth accident is not a plan; a stated count is. Lane A supplies both the widened population and the worked example | A sweep artifact with read / can-fire / cannot-fire counts and their denominators, a disposition per finding, #473 resolved with a test pinning the choice | pending |
| C | Surface duplicate-ratchet pressure at the first edit to a gated file (#474) | Four consecutive runs have written "run the dup ratchet early" into a plan and hit it at the aggregate anyway. The length-headroom advisory already proves the affordance shape works | The advisory firing on a changed gated file, a test pinning it, #474 closed through the close path's floor | pending |
| D | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | pending |

## Operator Decision Queue

- Decision: confirm Lane A's BEHAVIOURAL half — re-run a task-completing `critique` or `quality` run in the repo where the refusal was observed, and confirm a bounded reviewer actually spawns
- Owner: operator
- Why deferred: not obtainable from this session. The decision under test is made by an agent reading its OWN repo root, and every agent this session can reach is rooted in charness, which carries the `AGENTS.md` block — so the ladder resolves at rung 1 here and rungs 2 and 3 are never exercised by a real agent.
- Unblock action: run the command in `## User Verification Instructions` in that repo and report whether the reviewer spawned, and at which rung
- Revisit trigger: the operator's next session in a repo that has never run `setup`

- Decision: whether to reconcile the two spellings of the delegation contract (issue #476)
- Owner: operator
- Why deferred: both repair directions newly APPLY floors to repos previously outside them, so it needs a measured count and a recorded disposition first (D49). Filing preserved the finding without arming anything.
- Unblock action: decide whether the template gains the marker sentence or the markers widen to accept the standing-request spelling, then measure what each would newly hold to the contract
- Revisit trigger: the next `setup`-surface slice, or a consuming repo reporting an inert bounded-review floor

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

- Routing: achieve — selected from installed skill metadata as the owner of the goal lifecycle, slice cadence, and closeout floors for this three-lane run; `critique` supplied the bounded review rounds Lane A's proof-surface changes owe, `quality` owns the dup-ratchet contract Lane C extends, and `issue` filed #476 and stages the closes.
- Routing: impl — selected from installed skill metadata for the code-and-contract slices in all three lanes (the ladder and its record store, the two widened readers, the edit-time advisory); `impl` owns the smallest-meaningful-slice loop and hands its stop gate to `prove`, which is where the bounded rounds and the slice closeout ledger came from.
- Gather: n/a — every `## Context Sources` URL is a GitHub issue in this repo's own tracker, read through `gh issue view` against the repo's own backend rather than fetched as external web content; no external source became working context.
- Release: n/a — this run touches no version, install manifest, or release surface; no publish, tag, or version bump was performed or claimed.
- Issue closeout: #475, #473, #474 CLOSED through `issue_tool.py close-with-comment` after a DELEGATED resolution critique ran first and refused #473 until its probe was made capable of failing. Carrier: close-comment (not commit keywords), so `verify-closeout --carrier direct-commit` reports the ledger lines missing from the COMMIT message — that is a carrier mismatch in the verification call, not a failed close. Confirmed on a different channel: `gh issue view` reads back CLOSED (COMPLETED) for all three, and each posted comment carries its `Behavior:` / `Critique:` / `AI-provenance:` lines (3/3 each). #476 filed this run and left OPEN by design.


The four lines above are this run's recorded routes, each on ONE physical line so
the floor reads the whole value.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED / APPROVED 2026-08-02 — all three items settled by the operator in-transcript. Item (2) APPROVED and item (3) SETTLED — `git push` to `main` plus the CI it triggers and filing new issues are approved for this run; closing #475 / #473 / #474 still runs through the close path's floor; the throwaway scratch repo was WITHDRAWN as over-specified (see `## Boundaries`), so no temp repo is created; and this stays ONE goal with three lanes under the written cut order (C, then B's repairs, never A). Item (1) RESOLVED 2026-08-02: the operator chose the three-source ladder with an ask-once rung — `AGENTS.md` block, else a structured repo-owned opt-out/opt-in, else ASK ONCE and persist the answer. The plugin never self-grants silently. Design detail is folded into `## User Acceptance` and Lane A. Original framing preserved below. (1) THE TRUST POSTURE FOR LANE A, and it is the whole design decision. Today the standing delegation request is the REPO OWNER's, checked into their own `AGENTS.md`. Every alternative source shifts who grants it: (a) invoking the skill counts as the user's act, so `/charness:critique` authorizes the bounded reviewers that skill mandates — most direct, and the plugin effectively grants itself spawn rights in any repo that installs it; (b) a structured opt-in `setup` writes, which keeps the grant repo-owned and removes the prose-matching fragility #471 proved, but still needs a file in the repo so it does NOT fix the never-ran-setup case alone; (c) both, with `AGENTS.md` kept as a third. Recommendation: (c), with (a) scoped narrowly to the named bounded-reviewer scopes and never a general spawn licence. Operator's call, because it changes who authorizes work that costs tokens. (2) IRREVERSIBLE SIDE EFFECTS — `git push` to `main` plus the CI each push triggers, closing #475 / #473 / #474 if their lanes resolve them, filing new issues, and creating a throwaway scratch repo under a temp path. The 2026-08-02 approval was scoped to that goal and does NOT carry. (3) SIZE — three lanes plus closeout is larger than the last two-lane run, which consumed a full session with four reviewers. The cut order is written into `## Boundaries` (C, then B's repairs, never A); confirm that is the wanted trade rather than splitting this into two goals.

## Slice Log

### Slice 1: Lane A — the three-rung delegation authorization ladder (#475)

- Objective: Make the standing bounded-review delegation request reachable in a repo that never ran `setup`: AGENTS.md, else a structured .agents/subagent-delegation.json record, else ask once and persist. No silent self-grant.
- Why this approach: The operator reported the symptom directly, and both code consumers were verified to already degrade open before any edit — so this is a contract-and-mechanism change, not a validator fix. Rung 2 is structured rather than prose because #471 proved a bolded word must never decide whether a rule fires.
- Commits:
- What changed: skills/shared/references/fresh-eye-subagent-review.md (new `## Where The Delegation Request Comes From`, step 0, Do Not bullets); NEW skills/shared/scripts/resolve_subagent_delegation.py + subagent_delegation_record.py; scripts/validate_critique_artifacts.py and skills/public/issue/scripts/issue_critique_observer.py (both now walk the ladder and model the declined / narrowed-scope / unreadable states); scripts/validate_quality_artifact.py and the critique blocked-signal floor (accept `delegation signal:`); issue_resolution_critique.py (operator advisory distinguishes a decline from a host incapacity); setup + critique SKILL.md and setup references; NEW tests/quality_gates/test_subagent_delegation_ladder.py (44 tests); plugins/charness mirrors; dup-review.json (6 families classified intentional).
- Alternatives rejected: Letting a skill invocation self-authorize (the plugin grants itself spawn rights in every installing repo, with no per-repo record) — rejected by the operator's chosen design. A scope-aware rung 1 — rejected: rung 1 reads prose, so parsing a hand-narrowed block would re-create the fragility rung 2 removes; the limitation is stated in the payload instead. Proving human authorship of a rung-2 grant — impossible for any file-based mechanism; auditability replaces it.
- Targeted verification: 44 focused tests green; ruff clean; validate_critique_artifacts --all green over 688 critique artifacts (988 files = 688 artifacts + 300 prepare packets, excluded by content kind); all three readers still report this repo adopted at rung 1 and no rung-2 record exists here, so nothing is newly refused in-repo; run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review = completed.
- Test duplication pressure: check_dup_ratchet.py hard-blocked with 6 new code families, ALL of them the deliberate portable-vs-repo reader duplication the repo already documents; classified `intentional` in dup-review.json with the parity test named as the guard. Ratchet now clean. Note: this is the FOURTH consecutive run to hit the ratchet at the closeout aggregate rather than at first edit — live evidence for Lane C (#474).
- Critique: charness-artifacts/critique/2026-08-02-lane-a-the-delegation-authorization-ladder.md — four bounded reviewers over two rounds, all findings received, both boundary fingerprints exit 0 clean. Round 2 confirmed the fix REPRODUCED the class it fixes: the round-1 `delegation signal` widening could not fire on the one-line record the contract prescribes, and blocked_kind was computed while the operator advisory still called a decline a host incapacity. Both repaired; round-2 repairs recorded as accepted-unreviewed per the two-round cap.
- Off-goal findings: https://github.com/corca-ai/charness/issues/476 — the shipped compact AGENTS.md template carries marker 1 but not marker 2, so a setup-created repo reads as never-adopted by all three readers. Verified by measurement. Not repaired in place: both repair directions newly APPLY floors to repos previously outside them, which needs a measured count and a recorded disposition (D49).
- Lessons carried forward: A reviewer fixture that spells a string the way the matcher wants is how the whole class hides — build test inputs from the source constant, not by retyping. And a repair on a proof surface earns its second round: round 2 found blockers round 1 structurally could not see, because it was reviewing code that no longer existed.
- Metrics:

### Slice 2: Lanes B and C — count the rest, and move the ratchet signal to the edit

- Objective: Lane B: apply a predicate written down BEFORE reading the population across three strata, verify every cannot-fire claim adversarially, repair the unambiguous, file the rest, resolve #473. Lane C: surface dup-ratchet pressure at the first edit to a gated file (#474).
- Why this approach: Four instances of this class were all found by people, never by a gate; a fifth accident is not a plan. Lane C: this run became the FOURTH consecutive one to hit the ratchet at the closeout aggregate after writing 'run it early' into a plan.
- Commits:
- What changed: NEW charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md (predicate committed before the population was read, then counts); scripts/validate_current_pointer_freshness.py (deleted a registered check whose body was `_ = repo_root`); NEW tests/quality_gates/test_pre_rule_refusal_tripwire.py (#473's forced-scope probe); audit_disposition_corpus.py docstring; NEW scripts/dup_ratchet_edit_advisory.py; scripts/post_edit_skill_anchor_guard.py (carries the advisory on hookSpecificOutput.additionalContext); NEW tests/quality_gates/test_dup_ratchet_edit_advisory.py (16 tests); dup-ratchet.md, implementation-discipline.md, .gitignore, dup-review.json.
- Alternatives rejected: Deleting #473's flag as a guard that cannot guard — REJECTED: the situation it was written for is the grandfather LEAKING, not the current corpus, and in that situation it fires; deleting a tripwire because its regression has not happened yet is the opposite error from this goal's. A membership-aware advisory — rejected: the baseline stores fingerprints and content hashes, not paths, so it needs a full rescan per edit. A permanent meta-validator — rejected by the goal's own non-goals; the output is a one-off measurement.
- Targeted verification: Sweep: 197 units assigned, 172 read (87%), 25 unread and counted; 201 rules classified; 14 cannot-fire claims of which adversarial verification REFUTED 11 and confirmed 1. That one re-read independently by the parent before repair. 20 focused tests green (4 tripwire + 16 advisory); ruff clean; validate_current_pointer_freshness green after the deletion; run_slice_closeout --skip-broad-pytest --ack-cautilus-skill-review = completed.
- Test duplication pressure: check_dup_ratchet hard-blocked twice more this slice. First round: 6 families, all the deliberate portable-vs-repo reader duplication, classified intentional. Second round: 3 families of which 2 were REAL duplication I had just written — repaired by reusing path_portability_lib.resolve_within_repo and collapsing my own two subprocess blocks — leaving 2 genuine idiom families classified with reasons. The Lane C advisory then fired on its own implementing edit and I ran the ratchet when told; it was clean.
- Critique: charness-artifacts/critique/2026-08-02-lanes-b-and-c-sweep-and-edit-time-advisory.md — one bounded reviewer on Lane C (boundary verify exit 0 clean) plus 12 surveyor/verifier agents on Lane B. The reviewer found the advisory printing to stderr while the hook contract branches on exit codes: it computed correctly and was thrown away — this goal's own class, freshly minted in the fix for it.
- Off-goal findings: https://github.com/corca-ai/charness/issues/476 (filed in Lane A). The sweep's consuming-repo reading is under-measured and recorded as a non-claim rather than a finding.
- Lessons carried forward: Adversarial verification refuted 11 of 14 findings. Without it this run would have checked in a confident, wrong measurement — worse than none. And the advisory that fired on the edit that implemented it is the cheapest behavioural proof this session got: build the affordance, then let it catch you.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — "The boundary
   (load-bearing)". Every instance here is a fail-open proof surface, and the
   north star also names the anti-pattern Lane B must not become.
2. [issue #475](https://github.com/corca-ai/charness/issues/475) — Lane A, with
   the root cause traced to one line and the two code readers cleared as NOT the
   cause. Operator-reported.
3. [fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md)
   — line 86 is Lane A's defect. Read the surrounding contract for what it is
   protecting before changing where authorization may come from.
4. [issue #473](https://github.com/corca-ai/charness/issues/473) and
   [issue #474](https://github.com/corca-ai/charness/issues/474) — Lane B's known
   member and Lane C's subject.
5. [The 2026-08-03 goal](./2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md)
   and [its closeout-claims review](../critique/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator-closeout-claims-review.md)
   — where the class was repeatedly found, and what that run's own claims got
   wrong. Read before writing any figure here.
6. [That run's retro](../retro/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md)
   — `## Sibling Search` names the class; `## What Created Waste` is this plan's
   Low-Cost Checks.
7. [issue #472](https://github.com/corca-ai/charness/issues/472) — CLOSED as not
   planned. Its close comment carries the full measurement and the reasoning for
   why a self-report word filter was the wrong instrument; read it before
   proposing any phrase-list work, so the analysis is not re-derived.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

1. **One goal or two?** This goal supersedes two separate drafts — a sweep-only
   goal and a #475-only goal. Family considered: {sweep alone; #475 alone; both,
   sequenced in one goal; both, as two goals run back to back}. **Chosen: one
   goal, #475 first.** They are the same class, and each improves the other:
   #475 is the sweep's clearest worked example, and it WIDENS the population the
   sweep draft had wrong (that draft enumerated only code, and #475 lives in a
   contract surface an agent reads — a sweep that only reads code could not have
   found the instance that prompted it). Rejected: #475 alone, as too small for
   the session and leaving four accidental findings uncounted. Rejected: the
   sweep alone, because it defers the operator's live cost.
   Anti-anchoring: `axis: size register` — combining lanes is normally how a goal
   overruns; the defence is the explicit cut order, not optimism.
2. **What is #475's actual defect?** Family considered: {the phrase list is too
   narrow; the validators refuse repos without the block; `setup` fails to write
   the block; the authorization rule names only one source}. **Chosen: the
   authorization rule.** The operator reported the symptom directly — a repo that
   never ran `setup` refuses to spawn automatically — and reading the two code
   consumers showed both already degrade open, so no validator refuses anything.
   Rejected: the phrase list, which is a critique-artifact RECORDING rule and was
   a full lane's detour before the symptom was stated.
   Anti-anchoring: `axis: layer` — this read as a code defect for a whole session
   and is a contract-text defect.
3. **How is Lane A proven?** Family considered: {read the contract and argue; a
   unit test over the rule text; a scratch repo with a real spawn; the operator
   re-running in the repo where they SAW the refusal}. **Chosen: the operator's
   re-run, with the agent proving only the mechanism.** The scratch repo was
   chosen first and then WITHDRAWN on the operator's challenge, which was
   correct: the decision under test is made by an agent reading its OWN repo
   root, and every agent this session can reach is rooted in charness, which
   carries the block. A subagent told to treat a temp directory as its repo root
   reports on instructions the parent wrote — testimony, not behaviour — and
   would have been a synthetic proof of a real defect. Rejected: the text test
   alone, since "the rule now permits it" is exactly the evidence that let a
   guard sit dormant for months. Anti-anchoring: `axis: who observes` — the
   strongest available observer here is the person who hit the bug, not a
   fixture this session builds for itself.
4. **Is #472 in?** Family considered: {fold it in; leave it filed and surface the
   toll; take it only if Lane B finishes early; close it}. **Chosen: CLOSE it**,
   after the operator asked what it actually buys — a question nobody had asked
   in the three sessions that carried it.
   The measurement is preserved in the close comment: widening to the
   `delegation policy` stem refuses exactly 2 artifacts of 589 with a readable
   value, both dated 2026-05-21, so an enforce-from-date floor would refuse 0
   today; a broader `delegat* + policy` rule refuses 4, but 2 of those are honest
   `parent-delegated` records that merely mention policy, so that variant is
   rejected on measurement rather than on taste.
   The closing reason went past the toll: the rule inspects an agent's own
   statement about why it skipped a review, so it neither causes the review nor
   resists rewording — and this repo had already written the general objection,
   that teeth over a self-report land on honest authors rather than on liars.
   Its cause is #475, and after Lane A "the user declined" is a legitimate record
   the rule must not refuse. Keeping it open implied planned work nobody
   recommended.
   Anti-anchoring: `axis: worth doing at all` — three sessions optimised HOW to
   widen the list before anyone asked WHETHER to.

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

Retro: charness-artifacts/retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md
Host log probe: skipped: host-log-not-exposed: this Claude Code session exposes no per-turn token/time/tool-call log to the agent, so any figure here would be fabricated; the reviewer/workflow token counts quoted below come from the host's own spawn summaries, not from a probe.
Disposition review: charness-artifacts/critique/2026-08-02-lanes-b-and-c-sweep-and-edit-time-advisory.md

Every figure carries its source or is marked unbacked.

- Broad pytest: **1 failed, 6675 passed** on the first explicit run, then **6676 passed, 0 failed** on the final run over the shipped tree — `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`. The one failure was a test pinning the refusal message this run widened; repaired. Recorded rather than smoothed: the closeout gate had reported `completed` while that test was failing, which is exactly why the handoff says a `completed` gate is not broad proof.
- Push + remote CI: pushed `3ea81087..518fc846` to `main` after the pre-push quality gate reported **82 passed, 0 failed**; remote `Quality Core` on `518fc846` reports **completed success** — `gh run list`. Confirmed per P4 by a different observer (GitHub Actions) and a different evidence channel than the push exit code.
- Pre-push refusals before that: the changed-line mutation lane refused the push **four times**, naming 3 files and then 6, 3, and 1 uncovered changed lines. Every refusal was correct — the repairs had added failure branches nothing exercised — and closing them added 12 tests. The final line was the `__main__` CLI entrypoint, marked `# pragma: no cover` per this repo's existing convention rather than tested through a subprocess.
- Critique-artifact corpus: **688 validated, exit 0** — `python3 scripts/validate_critique_artifacts.py --repo-root . --all`, measured 2026-08-02 AFTER this run's own artifacts landed in it. Denominator: 988 `.md` files in `charness-artifacts/critique/` = 688 artifacts + 300 prepare packets, the latter excluded by content kind in both selection modes (re-derived with `candidate_paths(all_artifacts=True)`).
- Sweep: **197 units assigned, 172 read (87%), 25 unread**, 201 rules classified, 14 `cannot-fire` claims, **11 refuted**, **1 confirmed and repaired** — source `charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md`, which states each stratum's own denominator.
- Reviewer boundary: **3 windows, every verify exit 0**, `{"ok": true, "verdict": "clean", "drift": []}`, nothing parent-declared — `skills/shared/scripts/reviewer_boundary_fingerprint.py verify`.
- Focused tests added this run: **44** (ladder) + **16** (advisory) + **4** (#473 probe) = **64**, all green.
- Bounded reviewers: **6** (2 Lane A round 1, 2 Lane A round 2, 1 Lane C, plus 12 sweep survey/verify agents in a dynamic workflow). All findings received in the parent context; no delivery failure.
- Duplicate-ratchet families classified `intentional` this run: **8** — 6 portable-vs-repo reader duplication, 2 idioms; source `charness-artifacts/quality/dup-review.json`.
- Token/time cost per lane: **unbacked: this host exposes no per-turn accounting to the agent.** The workflow's own summary reported 1,347,297 subagent tokens over 18 agents for the sweep; that is a host-reported figure for that workflow only, not a goal total.

## User Verification Instructions

**Lane A's behavioural half — the one thing this session cannot prove.** In the
repo where you saw the refusal (one that has never run `setup`, so it carries no
`AGENTS.md` `Subagent Delegation` block), first check what the ladder now
resolves:

```bash
python3 ~/.agents/src/charness/plugins/charness/shared/scripts/resolve_subagent_delegation.py resolve --repo-root .
```

Expect `"delegation": "ask"`, `"rung": 3` — the repo has not refused, it has not
been asked. Then run a task-completing `/charness:critique` (or `quality`) there
and confirm the agent ASKS once, naming the bounded reviewer scopes, and that on
approval a bounded reviewer actually spawns and its findings come back. The
answer persists, so it should not ask again:

```bash
cat .agents/subagent-delegation.json
```

Recorded as an explicit non-claim until you confirm: the rule now permits it is
NOT evidence that it happens, and that gap is exactly how #471 stayed dormant.

**Lane C, if you want to see it fire:** add ~30 lines to any file under
`scripts/` or `skills/public/` and the advisory appears in the agent's context at
the edit, once per file per HEAD.

**Lane B's measurement** is
`charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md`; its counts are
re-derivable from the stated denominators.


## Auto-Retro

Retro dispositions: applied: the edit-time dup-ratchet advisory (`scripts/dup_ratchet_edit_advisory.py`, wired to the PostToolUse hook, 16 tests) turns the "run the ratchet early" plan bullet into a workflow signal
Retro dispositions: applied: test inputs are built from the source constant rather than retyped (`_decline_status_line` reads `_DECLINE_ACTION`), after the hand-typed version passed against a form nothing prescribes
Retro dispositions: applied: the second bounded round on a proof-surface repair is now evidenced twice over in this goal's critique artifacts, both times finding the class reappearing in the repair
Structural follow-up: applied: `scripts/dup_ratchet_edit_advisory.py` plus its hook wiring and `skills/public/quality/references/dup-ratchet.md` *Two Arms* — the transferable waste named in `## Sibling Search` (a recurring trap living in prose) now has a deterministic non-blocking signal, and the consuming-repo-inertness and fixture-shape items are carried to the handoff as named anchors

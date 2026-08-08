# Achieve Goal: Retire the second live goal, then close the four filed issues that reach a verdict

Status: active
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: COMPLETE. Five slices planned, five reached — the first goal in
  this family to finish its plan. All five claimed issues are `CLOSED` and
  verified through the adapter (`#536`, `#558`, `#557`, `#559`, `#556`), and the
  second goal artifact is terminal, so the repo has ONE live goal.
- Current slice intent: none — terminal. Read `## Slice Log` slice 8 for the
  bundle proof (which was RED first, with four failures read rather than routed
  around) and `## Coordination Cues` for the routing and closeout evidence.
- Next action: none here. The successor is
  `charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md`,
  and it is `--pursue-ready`.
- 13-FOR-13 across the family, and this goal's three built slices are the sharpest
  evidence yet: fourteen of the blockers its six rounds found were in REPAIRS, not
  in the original analysis. Round 2 is not optional on a verdict surface.
- REPAIRS INHERIT HALVES. Round 2 of slice 3 found three findings with one theme:
  a repair inheriting half a layout (source tree but not installed), half an
  exception contract (a typed refusal swallowed by the caller's broad `except`),
  and half an owner (delegating to `resolve_op` while passing `required` empty,
  one slice after building that floor). Ask what the repair did NOT inherit.
- A TEST THAT RE-IMPLEMENTS ITS SUBJECT IS A COPY OF THE RULE. Shipped one inside
  the slice about copies of rules; it would have passed with the loader deleted.
  Call the function. And pin the SOURCE, not the generated mirror — a mirror-only
  assertion survived a mutant because the mirror lags until the next sync.
- 9-FOR-9, and slice 1 is the first where BOTH rounds landed on the REPAIRS rather
  than the build. Round 1 found four blockers in the shipped closeout draft; round
  2 found three more inside round 1's repairs, including a claim I had already
  read the refuting evidence for in the same session. Budget round 2 on every
  remaining slice; it is not optional on a verdict surface.
- Opening a file is NECESSARY AND NOT SUFFICIENT. The predecessor's lesson was
  `open every location an instruction names`. I did — printed the whole block,
  read three keys quoting counts — and then wrote `transcribes no figures at all`
  two steps later. Write the claim from what the read RETURNED.
- A NEW surface added to a list must be checked against the LIST'S OWN CONTRACT,
  not only against its neighbours. Pairing a counterfactual command with a prose
  sentence passed every neighbour test and violated the header's definition of
  what a pairing means; executed, that instruction pins the wrong threshold.
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

Predecessor: `charness-artifacts/goals/2026-08-08-one-cadence-one-owner-stop-contradicting-the-agent.md`. It built and closed slices 1-3 of a nine-slice plan and closed EARLY rather than push six more slices through an exhausted session. This goal carries the remaining six, reshaped by what those three measured.

**What the predecessor established, and why it changes how these are built.**

1. **Every one of its three slices shipped a fix carrying the class it fixed, and round 2 caught all of them.** Slice 1 refused a goal while leaving `activation_ready: true` beside it (one fact, two owners — inside the slice about one fact having one owner). Slice 2's blocker fix silently dropped 25 in-repo `skills/support/` files (D9 again, in the file whose comment records D9). Slice 3's fix for `file.py:12` swallowed every SENTENCE-FINAL count, and widened trigger verbs while leaving removal labels behind. Round 2 is not optional on a verdict surface; budget it.

2. **The premise check was refuted or corrected on ALL THREE slices, at design time.** Slice 1's count was wrong in both directions (three artifacts, not five; one it named was not a contradiction, one it missed was). Slice 2's goal named the WRONG OWNER — the script it called "the precedent" was itself a hand-rolled copy. Slice 3's plan asked for a check where the answer was a shape. Verify the remedy's premise, and verify the OWNER the remedy names, before shaping.

3. **A duplicate-hash chase must not design a proof surface.** The dup ratchet was right the first time and caught a real defect. Chasing a later ROTATED hash is what routed two `complete`-state floors onto a level-aware section walk — a latent false green. Classify with a reason instead; the predecessor's `dup-review.json` entries carry the worked reasoning.

4. **Mutants are necessary and not sufficient.** 37 mutants were killed across three slices, and seven survived first. But none of round 2's blockers were mutation-findable — a reviewer found them by reading what the code would MEET, not what it was tested against.

**The remaining work**, renumbered from the predecessor's plan:

- The two lessons a gate cannot hold, written where the next session reads them (a substring pin cannot see an INVERSION; a test whose subject IS live repo state cannot be mutation-tested by editing the worktree). `recent-lessons.md` is GENERATED from retro artifacts via a selection index — this needs a retro artifact plus a refresh, not a hand edit.
- `#557` and `#559`: the fourth and fifth copies of the backend rule. `#559` had ALREADY drifted from the owner when it was filed.
- `#558`: `{repo}` is the unclosed half of an issue's identity; a wrong-repo CLOSED verdict is still reachable by reading.
- `#560` and `#561`: ready-path coverage and equality-versus-invariant pins, both deliberately deferred with reasons.
- `#556`: a check reachable only for a directory named `charness` — the same permanent-green class.
- Bundle proof and closeout.

**Two inherited obligations that are not slices.**

- **RESOLVED, and the residue is now `#562`.** FOUR of twenty locators frozen by the `#514/#515/#518` source-freeze receipt are stale, changed by the predecessor's slices 2 and 3 (including one from a round-2 repair). ONE test is red: `tests/test_issue_source_freeze.py`. It was deliberately not re-stamped: `refreeze` would assert an inspection of files for issues neither goal owns. The operator ruled that an unrelated slice's locator change may be re-stamped without re-inspection; it was, and the tests are green. The RESIDUE is the finding worth carrying: a source freeze cannot distinguish 'the file I reasoned about changed meaningfully' from 'someone added a flag elsewhere in it', so every incidental edit costs a human decision. Filed as `#562` with the measurement: 6 of 20 locators changed in one day, the inspection has been re-stamped FIVE times, and every single one of those five was incidental to the issues' scope — an observed 0/5 true-positive rate. The second-order cost is the real one: `refreeze` is one mechanical command, none of the five prior re-stamps recorded any basis, and that reflex will fire on the day a locator's semantics genuinely change. NOT built here on purpose: ~35 `sha256` references plus a schema bump makes it a proof-surface slice wanting two review rounds, and this run had neither the budget nor the context to do that safely.
- **The section-locating walk is consolidated in seven call sites and NOT in seven others** inside the `achieve` package, including `slice_plan_data_row_count` in the very file that now hosts the owner. Recorded honestly in `dup-review.json` after a first draft overclaimed completeness and round 2 refuted it.

## Non-Goals

- **Do not plan nine slices.** The predecessor planned nine and reached three,
  and the three it reached were good BECAUSE they got two review rounds each.
  This goal plans five and names what it does not claim.
- **Do not build `#562` (the freeze locator pin) without two review rounds.** It
  is a proof-surface deletion touching ~35 `sha256` references and a schema
  version. The measurement is already done and filed; the build is not cheap.
- Do not touch the freeze's SOURCE-SNAPSHOT half. That half defends a genuinely
  external mutable dependency (issue bodies) and is sound. Only the
  owner-inspection locator pin is in question.
- Do not take the prompt-surface cluster (`#519`-`#532`). Still a measurement
  question, and still not this family's.
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

- The repo has ONE unfinished goal at closeout, not two. `#536` is closed through
  the full floor and `2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`
  reaches a terminal status, or the reason it cannot is recorded against a named
  blocker.
- A wrong-repo `CLOSED` verdict is no longer reachable by reading (`#558`), proven
  by CONSTRUCTION — an input that would have produced the wrong verdict is shown
  refused, not inferred from a green suite.
- The tracker-backend rule has one owner, or every remaining copy carries a
  measured reason for existing (`#557`, `#559`). The exemption list shrinks; a
  copy that merely passes is not a reason.
- A check that could only ever fire for a directory literally named `charness`
  fires for a consumer-shaped repo (`#556`), proven by construction.
- Every slice that changes verdict logic gets TWO delegated review rounds, and the
  second round's findings are recorded whether or not they produced repairs.
- Each slice records its premise-check verdict BEFORE the build, including which
  OWNER the remedy names — the predecessor's slice 2 was refuted on exactly that.
- Verification cadence follows `## Active Operating Frame`. This section names no
  command and no boundary frequency on purpose; that duplication is the defect the
  predecessor's slice 1 repaired and its validator now refuses.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin
  sync BEFORE validators; `check_python_lengths.py --headroom` before adding to a
  gated file; `check_dup_ratchet.py --summary` EARLY, not at the commit-message
  boundary — it hard-blocked four times in the predecessor and was right the first
  time every time.
- After ANY commit-gate rejection, run the aggregate (`run_slice_closeout.py`)
  rather than fixing one rejection at a time.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- **Two delegated review rounds on any slice that changes verdict logic.** Round 2
  reads the REPAIRS. The predecessor family is now 8-for-8 that the repair carried
  the class it fixed, and NONE of round 2's blockers were mutation-findable.
- **Mutate every REPAIR, not only the original code.** Seven mutants survived
  first in the predecessor, all on repairs.
- For a guard over a MESSAGE, mutate an INVERSION (swap two lists, swap two
  pairings), not only a deletion — a substring pin survives every deletion-shaped
  mutant it should.
- For a test whose subject is live repo state, prove discriminating power by
  INJECTION; editing the worktree changes the subject and the mutant looks killed.
- **Verify the reviewer boundary the moment a reviewer returns, BEFORE repairing.**
  The predecessor missed this on all three slices and had to reconcile afterwards,
  which is strictly weaker.
- Before writing any instruction that tells a reader where to look, OPEN every
  location it names.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer AND
  a different channel than the push exit code.
- An issue's `CLOSED` state is a non-claim until `verify-closeout --expect-state
  CLOSED` reads it back through the adapter.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

Five slices, ordered by MEASURED cost and leverage rather than by size.

| Slice | Objective | Why HERE | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Close `#536` and retire the still-active `one-rule-one-owner` goal | It is BUILT and reviewed; one closeout retires a whole goal artifact, and two live goals is the "one issue, two owners" defect this family keeps repairing | `validate-closeout-draft` reports `draft_verified`, a DELEGATED resolution critique runs BEFORE the close, `verify-closeout --expect-state CLOSED` reads back through the adapter, and that goal reaches a terminal status | done — `#536` CLOSED and verified at `7c09bc2a`; the goal artifact is `complete` at `30517c46`; two delegated rounds found seven blockers, all in repairs |
| 2 | `#558`: `{repo}` is the unclosed half of an issue's identity | A wrong-repo `CLOSED` verdict is a FALSE GREEN at an irreversible boundary — the highest-severity item in the filed set | The wrong-repo answer is refused or detected, proven by a constructed input rather than by a passing suite | done — CLOSED and verified at `01d1c5a8`; refusal proven by CONSTRUCTION at three surfaces; two rounds, five blockers, all in repairs |
| 3 | `#557` and `#559`: the fourth and fifth copies of the backend rule | `#559` had ALREADY drifted from the owner when it was filed, which is the copy-rot this family exists to stop | Each consolidated or classified with a measured reason; the exemption list shrinks | done — both CLOSED and verified at `00937ae1`; the fourth copy REMOVED and the exemption list shrinks to one; the fifth kept with an EXECUTABLE reason |
| 4 | `#556`: a check reachable only for a directory named `charness` | Cheapest of the filed set, same permanent-green class | The check fires for a consumer-shaped repo, proven by construction | done — CLOSED and verified at `34919616`; fires for a consumer-shaped repo, proven by CONSTRUCTION at both ends |
| 5 | Bundle proof, goal closeout, successor | Composition can drop what each slice proved alone | Verification lock recorded; broad proof ONCE, at this boundary | done — broad proof RED first (4 failed, one a real regression), repaired, then `7968 passed, 0 failed`; verification lock recorded |

NOT claimed, and named so the next session does not re-derive the decision:
`#562` and `#563` (both filed by the closing run: a proof-surface deletion, and
a drift gate whose population excludes the goals directory — measurements filed,
builds not this run's), `#560`/`#561` (deliberate
deferrals whose cost has not yet been re-measured), and the original slice 4 of
the predecessor's plan (writing two lessons into `recent-lessons.md`, which is a
GENERATED digest whose selection index gave its slots elsewhere — the durable
retro artifact already carries them, so the remaining work is understanding the
selector, not writing prose).

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: **32 open issues** on 2026-08-08 via
  `gh issue list --repo corca-ai/charness --state open --limit 100 --json number`.
  The count rose from 31 because this family filed `#562` while closing its
  predecessor. Rerun the command before reshaping scope; the reconciliation is a
  command, not an adjective.
- Claims: `#536` (built by the predecessor, owes only its closeout), `#558`,
  `#557`, `#559`, `#556`. Five.
- Not claimed: `#562` (a proof-surface deletion needing its own budget) and
  `#563` (`check-title-slug-drift` reports clean over a scope excluding
  `charness-artifacts/goals`, where 2 genuine drifts are live; widening it needs a
  decision on 3 non-English titles first or it lands red on day one). Both were
  filed by the closing run. `#560`, `#561` (deliberate deferrals). The prompt-surface cluster
  `#519`, `#520`, `#521`, `#523`, `#524`, `#525`, `#527`, `#531`, `#532` — a
  measurement question. `#514`/`#515` — consumer ownership. `#539`, `#545` —
  provider/publication safety. `#530`, `#535`, `#554` — operator decisions.
  `#534` — BUILT green, then REFUTED and REVERTED by an earlier goal; re-scope
  from the refutation, never from the title. `#518`, `#528`, `#542`, `#546`,
  `#547`, `#549`, `#550` — the predecessor family's unfinished slices.

## Operator Decision Queue

- Decision: does `#562` (the owner-inspection locator pin, 0/5 measured true
  positives) get built as a proof-surface DELETION, or is the freeze's
  owner-inspection half kept and its remediation given a required basis instead?
  Owner: operator. Why deferred: it is claimed by the successor goal, and the
  choice between deleting the pin and requiring a recorded basis for each
  re-stamp is a policy call about how much the freeze should cost, not a
  refactor. The measurement supporting either choice is complete and filed.
  Unblock action: pick a direction, or authorise the successor to pick one from
  the measurement. Revisit trigger: the successor's slice 1 premise check.
- Decision: the renderer-versus-reference spelling split in `setup`. The setup
  renderer is gated against baking a model id into the AGENTS.md contract, while
  `skills/public/setup/references/default-surfaces.md` instructs an agent to
  write exactly that profile — so an agent following the reference produces an
  AGENTS.md the same inspector can flag. Owner: operator, as the owner of the
  setup contract. Why deferred: surfaced by slice 4's round 2 refuting a comment
  rather than by a failing gate, and choosing which surface is right is a
  contract decision. Unblock action: decide whether the reference or the gate
  states the intended policy. Revisit trigger: the next `setup` contract change.
- Decision: `git push`. 27 local commits are unpushed, five of which carry issue
  closeouts. Owner: operator. Why deferred: `git push` is explicitly NOT a
  standing approval in this repo and must be requested each time; nothing here
  requires publication to be correct locally. Unblock action: grant or decline
  the push. Revisit trigger: any request that depends on remote CI.

## Coordination Cues

Recorded routes and closeout evidence for this run:

- Routing: issue — selected from installed skill metadata; every one of this goal's four build slices resolves tracked GitHub issues end-to-end through the adapter-resolved backend, which is `issue`'s declared scope, and its `bug` classification routing is what required the delegated resolution critique before each close. `achieve` owned the goal lifecycle and slice ledger; `impl`/`prove` were consumed inside each slice for the build and its closeout; `critique` supplied the bounded-reviewer contract for all ten rounds; `quality` owned the slice-boundary gate cadence via `run_slice_closeout.py` and the dup/length ratchets; `retro` closed the run.
- Routing: debug — substrate consumed rather than run standalone, which is the honest record for four `bug`-classified resolutions whose causes were all reproduced by CONSTRUCTION before any fix was shaped. No slice opened an investigation with an unknown cause, so no separate `charness-artifacts/debug/` record was written and each closeout ledger carries `Debug Artifact: none` with the reproduction commands instead of a path.
- Routing: quality — owned the verification cadence rather than a standalone review: `run_slice_closeout.py --skip-broad-pytest` at every slice boundary, `check_dup_ratchet.py --summary` and `check_python_lengths.py --headroom` inside slices, and the broad `pytest tests/` reserved for this bundle boundary. The dup ratchet hard-blocked twice and was right both times, each block naming a real second owner.
- Gather: n/a — no external source was consulted. Every input is in-repo or read through the tracker adapter: five issue bodies, the predecessor goal artifacts, and the working tree. `## Context Sources` names no URL, Slack, Notion, Docs, or Drive source.
- Release: n/a — no release surface was cut or bumped. `skills/public/release/scripts/publish_release_helpers.py` was EDITED (a drift repair plus a typed refusal) and its reference doc updated, but no version bump, no install-manifest edit, and no tag; the `plugins/` mirror resync is a generated-export sync obligation rather than a release. A delegation of that helper was attempted and REVERTED precisely because it would have changed what command a release runs.
- Issue closeout: `#536`, `#558`, `#557`, `#559`, `#556` — five issues, all CLOSED and verified. Carrier `direct-commit` for each, with close keywords and the classification ledger in the commit body and the same body posted as the closing comment through `issue_tool.py close-with-comment` (the repo's commits are unpushed, so GitHub auto-close cannot fire from the keyword alone). Each passed `issue_tool.py validate-closeout-draft` with `status: draft_verified` BEFORE any GitHub mutation, and each was read back with `issue_tool.py verify-closeout --expect-state CLOSED` against its own carrier commit — `7c09bc2a`, `01d1c5a8`, `00937ae1` (bundled `#557`/`#559`), and `34919616` — every one returning `status: verified` with empty `state_mismatches` and `confirmed: issue_verify_closeout@gh via backend-state-readback`.
- Successor goal: charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md — designed from what this run MEASURED rather than from what it left over. It claims the two proof surfaces this goal deliberately refused on budget grounds (`#562`, `#561`) plus `#560`, and it budgets two delegated rounds per verdict-logic slice as a plan-level cost because eighteen of eighteen blockers here were in repairs. Its frame carries the four traps no gate holds.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision.

- Discuss before activation: RESOLVED. Closing `#536` and the four other claimed
  issues rides the repo's standing close-on-floor approval, and the predecessor
  family closed four that way with a delegated resolution critique and an adapter
  readback each time. Slice 1 also flips ANOTHER goal artifact to a terminal
  status — that is bookkeeping on a goal whose work is already built and reviewed,
  not new scope, and leaving two goals live is itself the defect this family
  repairs. Every proof-level non-claim is named in `## Agent Verification Plan`.
  No push, release, tag, or Cautilus run is implied by activation; each stays
  per-request.
- Discuss before activation: RESOLVED by measurement, not preference — the scope
  is FIVE slices, not nine. The predecessor planned nine, reached three, and the
  three were good precisely because each got two review rounds. Planning to the
  budget that produced quality is the decision; `## Slice Plan` names what is not
  claimed so the cut is visible rather than implied.

## Slice Log

### Slice 1: Slice 1 premise check (#536's closeout) — CONFIRMED, including the OWNER the remedy names

- Objective: Before building the closeout, establish by execution rather than by reading the predecessor's record that `#536`'s remedy is genuinely delivered — and, because the predecessor's slice 2 was refuted on exactly that, establish which OWNER the remedy's central claim names and whether that owner is real.
- Why this approach: This goal's `## User Acceptance` requires each slice to record its premise-check verdict BEFORE the build, including the owner the remedy names. Slice 1 also flips a SECOND goal artifact to a terminal status, so a premise that failed here would mean stopping and recording a blocker rather than retiring a goal on an unmet floor — the open risk this goal's `## Plan Critique Findings` named.
- Commits: none — this record precedes the closeout build, per this goal's User Acceptance.
- What changed: No source changed. Read: `tests/probe_drift_support.py`, `tests/test_probe_drift_message.py`, the three drift sites, `scripts/measure_inventory_marker_rule.py`, `scripts/measure_inventory_consumption_floor.py`, `scripts/validate_inventory_consumption.py`. Executed: the two pinned test files against a constructed markdown artifact under `charness-artifacts/quality/`, then removed it and verified the tree clean. Read through the adapter: `issue_tool.py read --repo corca-ai/charness --number 536` with `comments_read: true` and 0 comments.
- Alternatives rejected: Rejected: taking the predecessor goal's `## Active Operating Frame` line (`#536` built and BOTH review rounds complete) on trust. That line is a claim like any other, and this goal exists because a goal artifact is a verdict surface downstream sessions plan against. Rejected: inferring the owner claim from the round-2 commit message, which states it — the commit is the thing under test.
- Targeted verification: VERDICT: CONFIRMED on both halves. (1) DELIVERY: all three drift sites import `probe_drift_message` from one module (`tests/test_inventory_marker_rule_measurement.py:18`, `tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py:18`), and a constructed markdown write produced `3 failed, 57 passed` with the full message rendered at all three — the corpus-versus-rule split, six discrimination paths, and the surface list with per-surface commands. The `.json`-versus-`.md` correction the predecessor's premise check made still holds. (2) OWNER: the message's central and most load-bearing claim is that `MIN_ENGAGEMENT_RESIDUAL_CHARS`, `residual_chars`, `ENFORCED_FROM_DATE` and `ARTIFACT_DATE_RE` live in `scripts/validate_inventory_consumption.py` and NOT in either measure script — the exact claim whose earlier wrong version would have sent a rule regression to the corpus remedy. Checked at DEFINITION sites rather than by grep count: all four are defined at `validate_inventory_consumption.py:42,43,113,125`, and every other occurrence in `inventory_measurement_lib.py`, `measure_inventory_consumption_floor.py` and `measure_inventory_marker_rule.py` is a `gate.`-qualified reference through an import. The owner the remedy names is real.
- Test duplication pressure: n/a — no tests added or expanded in this record; it is a read-only premise verdict.
- Critique: The premise held, which this goal family's record says is the less common outcome — the predecessor was refuted or corrected on all three of its premise checks. Worth stating why it held here: this remedy had already survived two bounded rounds, and both of those rounds were specifically about the location claims a premise check re-tests. The check still paid rather than merely confirming: it converted `built and reviewed` from an inherited assertion into an executed reproduction plus a definition-site owner verdict, and the reproduction is what the closeout's behavioural verdict now cites as a channel distinct from the unit pins. A premise check that confirms is not a wasted one.
- Off-goal findings: None filed from this record. Noted for the build: the reproduction is the only channel available that is genuinely distinct from the pins, and it is the same TOOL as the pins — the closeout should say so rather than claim an independent implementation.
- Lessons carried forward: Verifying the OWNER separately from the REMEDY was the right split, and it is cheap: four definition-site checks, one command. Carry into slice 2 (`#558`) — where the identity claim is `(repo, number)` and the question is again which surface owns it.
- Metrics:

### Slice 2: Slice 1 build (#536's closeout) — two more rounds, seven blockers, all of them in the repairs

- Objective: Close `#536` through the full floor: `validate-closeout-draft` reporting `draft_verified`, a DELEGATED resolution critique BEFORE the close call, a behavioural verdict from a channel distinct from the fix's own, and `verify-closeout --expect-state CLOSED` read back through the adapter. Retiring the second live goal follows from this closeout, not the other way round.
- Why this approach: First because one closeout retires an entire active goal artifact, and because two live goals is the `one issue, two owners` shape this goal family has repaired three times in code. Ordered by leverage rather than by size, per `## Interview Decisions`.
- Commits: the closeout commit carrying this record, the critique artifact, and the two rounds' repairs. The message itself was built at `67beced4` (build plus round-1 repairs) and `1fa7fd75` (round-2 repairs) by the predecessor goal.
- What changed: `tests/probe_drift_support.py`: new `FLOOR_COUNTERFACTUAL_COMMAND`, `GATE_MIRROR` and `MIRROR_SYNC_COMMAND`; the surface list grows from seven entries to nine and two existing entries are corrected. `tests/test_probe_drift_message.py`: ten pins become fourteen, and three existing pins are tightened. New: `charness-artifacts/critique/2026-08-08-issue-536-resolution-critique.md`. No exported surface changed, so `check_changed_surfaces.py` planned NO sync commands.
- Alternatives rejected: Rejected: closing on the predecessor's two rounds alone. The closeout floor requires a delegated resolution critique before the close call, and that critique found four blockers the build's own two rounds had not. Rejected: treating the resolution critique's repairs as bookkeeping and closing on one round. Those repairs changed verdict logic on a proof surface (the pins), which this repo's contract says owes a SECOND round reading the repaired surface — and that round found three more blockers, including the worst one of the slice. Rejected during round-2 repairs: keeping the new counterfactual surface paired with a `run:` command and merely warning about it in prose, because the module's own pairing contract says a paired command's output REPLACES the surface; the entry is unpaired now, which is a shape change rather than a wording change.
- Targeted verification: Behavioural verdict by reproduction, twice: a constructed markdown artifact under `charness-artifacts/quality/` produces `3 failed, 57 passed` across exactly the two files the issue names, with the full repaired message rendered at all three sites (both closeout-added surfaces appear in all three renders). Tree verified clean after each run. Mutation on the REPAIRS, not the original code: 8/8 killed on the round-1 repairs (swap `--recursive` between the two marker commands, which is round 2's exact harm; give `FLOOR_COMMAND` a `--floor`; delete the marker measure script from `DISCRIMINATION_PATHS`; drop `_provenance.why`; pair the counterfactual surface with the default command; drop the NON-ZERO warning; drop `TWICE`; delete the counterfactual surface), then 6/6 on the round-2 repairs (restore the refuted figure-free claim; re-pair the counterfactual surface as a paste target; soften the do-not-paste warning; delete the exported-mirror surface; revert to the misnamed transcription location; add a rule cause naming a `.md` file the old parse could not see). `check_dup_ratchet.py --summary` reports `status: clean`, `hard_block: false`, `new_code_family_count: 0`. `check_python_lengths.py --headroom`: 188/800 and 312/800, no pressure. `validate_critique_artifacts.py` exits 0. `validate-closeout-draft --carrier direct-commit` reports `status: draft_verified` with no missing fields and the critique bound to 536.
- Test duplication pressure: Four pins added and three tightened, all in one existing module. `check_dup_ratchet.py --summary` run after the additions: clean, zero new code or doc families, no hard block; the only messages are two ADVISORY membership REDUCTIONS in unrelated families. Length headroom checked before adding rather than after: the two touched files sit at 188/800 and 312/800.
- Critique: Two delegated bounded rounds, both boundary-fingerprinted `clean` and both VERIFIED THE MOMENT THE REVIEWER RETURNED, before any repair — the thing the predecessor missed on all three of its slices. Seven blockers, and every one was in a repair rather than in the shipped build. Round 1 found two omitted surfaces (the marker probe's `_provenance.why` ends on the presence-only total while the list framed `current_corpus` as THE prose field; the floor probe's `_provenance.counterfactual_floor_20` transcribes a corpus-moving pair with no regenerating command) and CONSTRUCTED two pin holes: the pairing pin compared constant to constant, so moving `--recursive` between the two marker constants kept all ten pins green while instructing a paste of recursive output over the top-level payload; and `DISCRIMINATION_PATHS` could be gutted while a rule cause still named the deleted file. Round 2 read those repairs and found three more. The factual one is the sharpest indictment: my repair for the omitted prose field asserted that the floor probe's `_provenance` transcribes no figures at all, when three of its keys quote counts and I had PRINTED those keys in the same session before writing the sentence. The structural one is worse in effect: I paired the new counterfactual surface with `run:`, and executed, `--floor 20 --json` emits a payload whose key set is IDENTICAL to the probe's top-level payload with `floor` set to 20 — so a literal follow does not leave stale prose, it pins a threshold the gate does not use, which is the single outcome the whole message exists to prevent. The third was the new population parse silently measuring nothing for whole classes of cause. None of the seven was mutation-findable; fourteen mutants were killed across both repair sets, and every one was written from what the code already met.
- Off-goal findings: No new issues filed. Two existing ones carried as siblings with proof rather than re-derived: `#561` (a third probe pins the INVARIANT and has never needed a refresh) and `#562` (the same re-stamp reflex on the source-freeze locator pin, 0/5 measured true positives). Recorded, not repaired: the recursive pin's `refused_citation_count` branch cannot fire against the checked-in probe — pre-existing, and a dead branch rather than a misleading message.
- Lessons carried forward: 1) The class this goal family keeps measuring is now 9-for-9, and slice 1 is the first instance where BOTH rounds landed on repairs rather than on the build. The rule `round 2 reads the REPAIRS` earned its place again: round 1's repairs were the most defective code in the slice. 2) A stronger statement of the recurring root cause than `open every location an instruction names`: I had ALREADY OPENED the location. I printed the floor probe's whole `_provenance` block, read three keys quoting counts, and then wrote `transcribes no figures at all` two steps later. Opening the file is necessary and not sufficient — the claim has to be written from what the read RETURNED, not from the shape the sentence wants. 3) A surface added to fix an omission can be worse than the omission, and the tell is the CONTRACT the surface list already declares: `run:` means output-replaces-surface, so pairing a counterfactual command with a prose sentence was a category error the list's own header defines. Check a new entry against the list's contract, not only against its neighbours. 4) A pin that parses prose to build its own population is a verdict surface twice over — once for what it asserts, once for what it selected. Assert the population.
- Metrics:

### Slice 3: Slice 2 premise check (#558) — DEFECT REPRODUCED BY CONSTRUCTION, SUGGESTED REMEDY REFUTED, and the right OWNER is already in the tree

- Objective: Before shaping anything, establish by execution whether `#558`'s premise holds — that a `view_state` template omitting `{repo}` silently drops it and can report a live citation CLOSED from another repo's issue — and establish which OWNER the remedy should land on, since the issue itself offers three options and calls none obviously right.
- Why this approach: This goal's `## User Acceptance` requires the premise verdict and the OWNER verdict before the build, and `#558` is the one claimed item that reaches an IRREVERSIBLE boundary. The issue also carries an explicit non-claim — `Not reproduced against a real repo-agnostic binary` — and the acceptance demands proof by CONSTRUCTION, so the reproduction is owed regardless.
- Commits: none — this record precedes the build.
- What changed: No source changed. Read: `skills/public/handoff/scripts/chunked_routing_issue_backend.py` (`VIEW_STATE_REQUIRED`, `VIEW_STATE_PLACEHOLDERS`, `GH_VIEW_STATE_ARGS`, `_resolve_command`, `issue_state`), `skills/public/issue/scripts/issue_backend.py` (`resolve_op`, `try_resolve_op`), `skills/public/issue/scripts/issue_verify_closeout.py` (`_view_issue_state` and the payload consumption at lines 296-330), `skills/public/issue/scripts/issue_close.py` (`GH_VIEW_DEFAULT`, `VIEW_PLACEHOLDERS`). Executed: a constructed repo-agnostic binary plus an adapter declaring `view_state: ["view", "{number}"]`, driven through the real `issue_state`; and `gh issue view --json repository` against the live tracker.
- Alternatives rejected: Rejected: building the issue's cheapest suggested direction on the strength of its being cheapest. Rejected: inferring the reproduction from the code path the issue traces — the issue traces it correctly, and constructing it anyway is what turned a read into a measurement and exposed that the cheap remedy is inert.
- Targeted verification: VERDICT: the DEFECT is confirmed and now REPRODUCED; the SUGGESTED REMEDY is refuted as a closure; the OWNER the remedy names is the wrong one, and the right one is already in the tree. (1) REPRODUCED BY CONSTRUCTION — the thing the issue explicitly did not claim. With `backend = {id: acme, binary: <repo-agnostic stub>, commands: {view_state: ["view", "{number}"]}}`, calling `issue_state("corca-ai/charness", 558)` returns `CLOSED` while the argv log shows the binary was asked only `view 558`: the repo was dropped without comment and `LAST_STATE_RESOLUTION_DIAGNOSTIC` is `None`, so nothing anywhere reports a problem. `#558` is OPEN in `corca-ai/charness`. That is a live backlog citation reported CLOSED, which is the manufactured stale verdict `chunked_routing_staleness` exists to refuse. (2) MECHANISM confirmed exactly as the issue states: `VIEW_STATE_REQUIRED` is `frozenset({"number"})` at line 122; `resolve_op` validates `set(subs) - allowed` and `required - used` but never checks that a SUPPLIED substitution was CONSUMED; `issue_state`'s second guard compares `payload.get("number")` only. (3) SUGGESTED DIRECTION 1 REFUTED as a closure — `verify the ANSWER's repository when the payload carries one`. The default template is `["issue", "view", "{number}", "--repo", "{repo}", "--json", "number,state"]`: it requests NO repo-bearing field, so the payload never carries one and the guard cannot fire on the default path. And on the vulnerable path — a custom template omitting `{repo}` — nothing guarantees the host's payload carries a repo either; the constructed stub's does not. A guard that cannot fire is this goal's own permanent-green class, the same shape as `#556`. It is worth having as defence-in-depth, but only after the default args request a repo-bearing field, and it does not close the path. (4) OWNER VERDICT, and this is the finding that reshapes the build: the identity rule already has TWO owners in the tree and they give DIFFERENT answers. `issue_backend.resolve_op` enforces whatever `required` set each caller passes, and the callers disagree — `handoff`'s `issue_state` passes `frozenset({"number"})`, while `issue`'s own closeout verifier `_view_issue_state` passes `required=frozenset({"repo", "number"})`. So the correct answer to `#558` is already implemented, one skill over, at the surface where a wrong verdict is irreversible. The remedy is to make the weaker caller match the stronger one and to give the deliberate waiver a place to live, NOT to invent a new payload check.
- Test duplication pressure: n/a — no tests added or expanded in this record.
- Critique: The issue frames `{repo}` as having been left optional because requiring it would break a genuinely repo-scoped host, and calls that trade unresolvable from inside the resolver. The premise check shows the trade is real but the framing is not exhaustive: the choice is not `require it and break repo-scoped hosts` versus `leave it optional and accept a false CLOSED`. It is `require it, and let a repo-scoped host DECLARE that its binary carries the scope` — omission stops being a silent waiver and becomes a loud error, and the waiver becomes a recorded decision. That is the same shape as slice 2 and slice 3 of the predecessor goal (state the FACT, leave the policy to the caller) and the same shape as `#528`'s declared-versus-defaulted-versus-absent distinction. It is also the third option the issue lists, reached from the owner rather than per caller. One thing the issue does not say and the reproduction shows: `LAST_STATE_RESOLUTION_DIAGNOSTIC` stays `None` on this path, so the module's own diagnostic channel — built precisely so that `template is broken` and `tracker unreachable` do not read identically — reports nothing at all for the worst of the three.
- Off-goal findings: Found during the owner check, and it is a SIBLING at the irreversible boundary rather than a separate issue: `issue_verify_closeout` fetches `--json number,state,url` and reports `url` in both of its mismatch records, but never CHECKS it. Its template requires `{repo}`, so it is far harder to reach than `#558`'s path — a host binary would have to ignore an argument it was given — but the data needed to close it is already in hand and already being carried. That is cheap in-scope prevention on the surface that produced this session's own `#536` CLOSED verdict, so it will be bundled and recorded rather than filed.
- Lessons carried forward: The OWNER check paid for the second slice running, and differently than in slice 1. In slice 1 it CONFIRMED the owner a message named. Here it found that the tree already contains two implementations of one identity rule with different strictness, and that the stricter one sits on the more dangerous surface — so the build is a reconciliation, not an invention. Carry into slices 3 and 4: when an issue says `none of these options is obviously right from inside X`, check whether some Y in the same tree has already chosen.
- Metrics:

### Slice 4: Slice 2 build (#558) — one identity rule, three surfaces, and two rounds that both landed on the repairs

- Objective: Make a wrong-repo `CLOSED` verdict unreachable by reading, proven by CONSTRUCTION rather than by a passing suite: an input that produced the wrong verdict is shown refused.
- Why this approach: The only claimed item that reaches an IRREVERSIBLE boundary. Severity outranks cheapness, per `## Interview Decisions`.
- Commits: the slice commit carrying the owner change, both consumer call sites, the close path, the tests, the reference, and the regenerated `plugins/` mirror.
- What changed: Owner: `skills/public/issue/scripts/issue_backend.py` (`answer_repo`, `_qualified`, `_scope_waived`, and a `waivable` parameter on `resolve_op`/`try_resolve_op`). Adapter: `skills/public/issue/scripts/resolve_adapter.py` parses `repo_scoped`, and `default_backend()` declares it absent. Consumers: `skills/public/handoff/scripts/chunked_routing_issue_backend.py` (`VIEW_STATE_REQUIRED` gains `repo`, new `VIEW_STATE_WAIVABLE`, `GH_VIEW_STATE_ARGS` requests `url`, `issue_state` checks the answer, `answer_repo` delegates to the owner); `skills/public/issue/scripts/issue_verify_closeout.py` (one `mismatch()` builder replacing three literal records, plus a `repository` mismatch); `skills/public/issue/scripts/issue_close.py` (the post-close readback now requires both halves and checks the answer). Docs: `skills/public/issue/references/issue-backend.md` gains an `Issue Identity` section. Tests: new `tests/test_issue_identity_is_repo_and_number.py` (15), two new in `tests/quality_gates/test_issue_closeout_verifier.py`, two RETARGETED in `tests/test_tracker_backend_single_owner.py`. Records: `charness-artifacts/quality/dup-review.json`. Generated: `plugins/` mirror synced before validators each time.
- Alternatives rejected: Rejected on premise-check evidence: the issue's own cheapest suggested direction, `verify the ANSWER's repository when the payload carries one`, as the CLOSURE. The default template requested `--json number,state`, so the payload never carried a repository — a guard that cannot fire, which is this goal's own permanent-green class. It is kept as defence-in-depth, but only after widening the default args to request `url`. Rejected: requiring `{repo}` outright with no escape, which would break a host binary genuinely bound to one repository — the documented reason it was optional. Rejected during round-2 repairs: keeping `repo_scoped` as a boolean, because this skill routes to TWO targets and an unqualified waiver cannot say which repository it covers. Rejected during round-2 repairs: invalidating the whole adapter on a malformed `repo_scoped`, because this file's own norm is that consumer-authored mistakes warn rather than refuse — and ignoring the key is also the fail-closed direction, since no declaration means no waiver. Rejected: consolidating the `issue_backend` and `release_backend` adapter parsers that the dup ratchet surfaced; that is `#559` and slice 3, and unifying two adapter keys is a contract decision.
- Targeted verification: Acceptance met by CONSTRUCTION, four ways, each an input that produced or could produce the wrong verdict. (1) The reported path: an adapter declaring `view_state: ["view", "{number}"]` against a repo-agnostic stub. BEFORE: `issue_state("corca-ai/charness", 558)` returned `CLOSED` while the binary was asked only `view 558`, and `LAST_STATE_RESOLUTION_DIAGNOSTIC` stayed `None` — a live citation reported closed with no signal anywhere. AFTER: `None` (UNKNOWN) with the diagnostic naming `missing required placeholders ['repo']`, and the backend never invoked. (2) A declared repo-scoped host still resolves — through the REAL adapter parser, not a hand-built dict — and is refused the moment it is asked about a DIFFERENT repository. (3) A backend that is TOLD the repo and ignores it: template correct, payload URL naming another repository, refused at the answer layer; the same payload asked about the repo it actually answered for returns `CLOSED`. (4) The closeout verifier: a stub returning the right number and the expected state, differing only in its URL's repository, now fails with `field: "repository"` and `confirmation.line: None`; a payload naming no repository at all still verifies, because silence is not a mismatch. Mutation on the REPAIRS: 8/8 on the build, 6/6 on the round-1 repairs, 5/5 on the round-2 repairs — 19 total, including two INVERSIONS (owner/repo swapped in the URL parse; the waiver failing open instead of closed) and one that reintroduced each named blocker. `./scripts/run-quality.sh` phases green via the aggregate; `run_slice_closeout.py --skip-broad-pytest` verdict `completed`; 211 tests across the eight touching suites pass; both reviewer boundaries verified `clean` before any repair.
- Test duplication pressure: The duplicate ratchet HARD-BLOCKED once and was right: adding a fourth field to `_parse_backend` made it converge with `skills/public/release/scripts/release_backend.py`, a second adapter-backend parser. Classified `intentional` in `dup-review.json` with the measured reason rather than baselined away — the two read DIFFERENT adapter keys owned by different skills, and the release copy has ALREADY drifted from the issue owner on rendering, so unifying them changes at least one skill's observable refusals. That is `#559`, which is slice 3. Length headroom stayed honest rather than shaved: `issue_verify_closeout.py` went OVER its limit at 364/360 when the repository check was added, and the fix was to extract the three near-identical mismatch records into one builder (351/360) rather than to squeeze — which also removed the duplicate family the ratchet had just flagged inside that file.
- Critique: Two delegated bounded rounds, both fingerprinted `clean` and both verified the MOMENT the reviewer returned, before any repair. Five blockers, and every one was in a repair rather than in the original defect analysis — the family is now 11 for 11. Round 1: (B1) the escape hatch was INERT and the fix hard-broke the hosts it was meant to protect. `resolve_adapter._parse_backend` returns a fixed key set, so `repo_scoped` never reached the runtime — and every waiver test hand-built the backend dict, bypassing the parser, so the suite structurally could not see it. That is the `a test that cannot fail for the reason it exists` shape, inside the slice about a check that cannot fire. (B2) the waiver was subtracted GLOBALLY inside the owner, silently LOOSENING the closeout verifier, which had required both halves absolutely — I loosened an irreversible boundary in order to fix a reversible reader. (B3) a bare `true` could not say WHICH repository, and this skill routes to two targets. Round 2 read those repairs: (B4) the owner-shape rule was applied to the `repository` STRING branch and not the DICT branch, so `{"nameWithOwner": "charness"}` still returned a bare half-identity — a WRONG value, which refuses a correct closeout, in the shape a host-mediated backend most naturally emits. (B5) the CLOSE path's own post-close readback — the evidence that the irreversible mutation landed, and the exact code that closed `#536` an hour earlier in this session — passed no `required` set at all and never read the `url` it was already fetching. Advisories taken as fixes: the waiver failed OPEN when no repo was supplied; a malformed declaration took the whole adapter red against this file's own warn-not-refuse norm, and `count("/") != 1` left nested-namespace hosts unable to declare their scope; two prose sites still instructed the refused `repo_scoped: true`; and one test accepted any `RuntimeError` mentioning `repo`, which the unknown-placeholder message also does.
- Off-goal findings: No new issues filed. Recorded, not repaired: `answer_repo` is genuinely INERT for path-prefixed installs (`https://host/gh/owner/repo/issues/<n>`) and for providers that nest differently — the docstring now names the two URL shapes it covers instead of implying it covers all of them, because a positional guess is what made the first version return a wrong repository. `skills/public/issue/scripts/issue_verify_closeout.py` sits at 351/360 with 9 lines of headroom; the next addition there should split the module rather than squeeze. The `issue_backend`/`release_backend` parser convergence is `#559` and is claimed by slice 3.
- Lessons carried forward: 1) `A test that bypasses the parser proves nothing about the parser` is the sharpest form of this slice's lesson, and it is a generalisation of the premise-check rule one layer down: I verified the OWNER of the identity RULE and did not verify the PATH by which a value reaches it. Ask of any new configuration key: which function actually constructs the dict the runtime reads, and does a test go through it? 2) A guard added at one call site through a SHARED helper changes every call site. Subtracting the waiver inside `resolve_op` was the natural place to put it and silently loosened the irreversible boundary; making it opt-in per call site is what encodes that a staleness reader and a closeout verifier have different risk budgets. Default to the strict behaviour every existing caller already had. 3) `Wrong is worse than silent` is a real design axis and it needs stating per branch, not per function: silence is accepted, so a wrong value REFUSES a correct verdict, and the rule has to be applied to every shape a payload can arrive in — B4 was the same rule missing from one branch of the function that introduced it. 4) When a gate hard-blocks on duplication, read WHICH files: this one named the exact second owner the next slice already claims, which turned a block into evidence.
- Metrics:

### Slice 5: Slice 3 premise check (#557, #559) — NOT one repair, and BOTH issues' stated blockers are narrower than they claim

- Objective: Before shaping, establish by reading whether `#557` and `#559` hold, and test the bundling assumption this goal's own `## Plan Critique Findings` flagged: they share a FACE (a copy of the backend-resolution rule) and may not share a REMEDY.
- Why this approach: This goal's Plan Critique names the risk explicitly, and the predecessor family measured TWICE that issues sharing a face do not share a fix — once refuting a bundle mid-slice, once splitting a slice at its premise check. `#557` and `#559` also each arrive with a recorded reason for NOT having been consolidated, and this repo's Change Discipline rule fires exactly there: verify the premise of a remedy some durable record already names, before shaping around it.
- Commits: none — this record precedes the build.
- What changed: No source changed. Read: `scripts/issue_source_capture_lib.py::build_page_argv`, `skills/public/release/scripts/publish_release_helpers.py::backend_command` and `OP_PLACEHOLDERS`, `skills/public/issue/scripts/issue_backend.py::resolve_op`/`try_resolve_op`, and `tests/test_tracker_backend_single_owner.py::_KNOWN_UNCONSOLIDATED`. Both issues read through the adapter with `comments_read: true` and 0 comments.
- Alternatives rejected: Rejected: bundling them as one consolidation because the dup-ratchet and the grep both group them. That grouping is exactly the FACE. Rejected: taking each issue's own `Why it was not consolidated` paragraph on trust — those paragraphs are the durable records this repo's Change Discipline rule says to verify first, and both turned out to be narrower than stated.
- Targeted verification: VERDICT: BOTH premises hold as DEFECTS, they are NOT one repair, and each issue's stated BLOCKER is narrower than the issue claims. (1) `#557` CONFIRMED: `build_page_argv` derives the binary, looks up `commands.source_capture`, refuses a non-gh backend that declared none, and renders `part.format(**subs) if "{" in part` — the owner's rule, without the owner's allowlist. Its stated blocker also CONFIRMED: the built-in default really is a conditionally assembled GraphQL invocation (`if after is not None: argv.extend([...])`), so it is not a template. But the blocker covers only ONE of the two branches. The TEMPLATE branch is the part that needs the allowlist and is exactly what `resolve_op` owns; the GraphQL default can stay local because it is not a template at all. And the adapter key is `issue_backend` — the same key, the same contractual owner — so no contract decision is involved. This is consolidatable today. (2) `#559` CONFIRMED, and its drift claim is now WIDER than filed: `if subs and "{" in part` versus the owner's `if "{" in part` still stands, and slice 2 ADDED `required`, `waivable` and `_scope_waived` to the owner, which the release copy has no equivalent of — so the two implementations of one rule have diverged FURTHER during this very goal. Its stated blocker, however, is REFUTED as stated: `#559` says unifying them 'means deciding whether one module owns resolve-a-command-template for ANY adapter-declared backend', framed as a contract decision. `resolve_op` takes a plain `backend` dict and reads only `binary`, `id` and `commands`; it is already adapter-key agnostic in behaviour. The only coupling to `issue_backend` is in three ERROR MESSAGE strings. Unifying the RENDERING does not require unifying the KEYS, and the refusal TYPE (`SystemExit` versus `RuntimeError`) is exactly the caller-owned policy the predecessor's slice 3 already separated from the mechanical part via a second entry point. (3) NOT ONE REPAIR: `#557`'s obstacle is a SHAPE problem inside one branch of one function under the owner's own key; `#559`'s is an OWNERSHIP and MESSAGE-COUPLING problem across two skills. Different in kind, different files, different risk — a release surface is the least reversible in this repo.
- Test duplication pressure: n/a — no tests added or expanded in this record.
- Critique: The interesting result is that both issues UNDER-scoped their own remedies in the same way, and the pattern is worth naming: each looked at the whole function, found one part that genuinely does not fit the owner's contract, and concluded the whole function cannot be consolidated. For `#557` the non-fitting part is the GraphQL default and the fitting part is the template render. For `#559` the non-fitting part is the adapter KEY and the refusal TYPE, and the fitting part is the entire rendering rule. In both cases the correct move is the one this goal family has now reached from four directions: consolidate the MECHANICAL part, leave the POLICY to each caller. Recording it as a rule rather than as two coincidences — when an issue says `X cannot be consolidated because of Y`, check whether Y is the whole of X or one branch of it.
- Off-goal findings: Recorded, not filed: this goal's slice 2 measurably widened `#559`'s drift by adding `required`/`waivable` to the owner without the release copy. That is evidence for the issue rather than a new one — a hand-synced pair drifts on the ordinary work of the repo, which is the claim `#559` makes.
- Lessons carried forward: SLICE NOT SPLIT, but the two halves get separate remedies and separate proofs inside it, recorded as the verdict rather than discovered mid-build. Carry into slice 4 (`#556`): its issue also names a reason a check cannot be fixed simply; check whether that reason covers the whole surface or one branch.
- Metrics:

### Slice 6: Slice 3 build (#557, #559) — one copy removed, one kept with a MEASURED reason, and two rounds that found six more blockers in the repairs

- Objective: Discharge `#557` and `#559`: the tracker-backend rule has one owner, or every remaining copy carries a measured reason for existing and the exemption list shrinks.
- Why this approach: `#559` had ALREADY drifted from the owner when it was filed, which is the copy-rot this goal family exists to stop — and slice 2 measurably WIDENED that drift by adding `required`/`waivable` to the owner, so the pair was diverging on this goal's own ordinary work.
- Commits: the slice commit carrying the owner helpers, both copies, the tests, the debt ledger, the reference docs, and the regenerated `plugins/` mirror.
- What changed: Owner: `skills/public/issue/scripts/issue_backend.py` gains `backend_binary()` and an `adapter_key` parameter that names the SUBJECT of its refusal messages; `probe_backend` stops re-deriving the binary. `#557`: `scripts/issue_source_capture_lib.py` — the adapter-template branch delegates to `resolve_op` with a derived `SOURCE_CAPTURE_PLACEHOLDERS` allowlist, a `SOURCE_CAPTURE_REQUIRED` set, and a repo-identity disjunction check; the GraphQL default stays local; a two-layout owner loader; every rendering failure typed as `CaptureRefusal`. `#559`: `skills/public/release/scripts/publish_release_helpers.py` — the drift repaired and the rendering failure typed, NOT consolidated. Tests: new `tests/quality_gates/test_release_backend_agrees_with_the_owner.py` (5, parametrised over every op) and new `tests/test_issue_source_capture_backend_delegation.py` (6, split out on the length cap). Records: `charness-artifacts/quality/dup-review.json`, `tests/test_tracker_backend_single_owner.py::_KNOWN_UNCONSOLIDATED` and its module docstring. Docs: `skills/public/release/references/adapter-contract.md`.
- Alternatives rejected: Rejected on premise-check evidence: treating these as ONE repair because the dup ratchet and the grep group them. That grouping is the FACE. Rejected: `#557`'s own stated blocker as covering the whole function — it covers one of two branches, and the branch needing the allowlist is exactly the branch that fits the owner. Rejected: `#559`'s stated blocker (`unifying two adapter keys is a contract decision`) — refuted by the premise check, since `resolve_op` reads only `binary`/`id`/`commands` and was already adapter-key agnostic. ATTEMPTED AND REVERTED: delegating `backend_command` to the owner. A smoke test found the real blocker — `release_backend` templates INCLUDE the binary and `backend_command` never reads `backend["binary"]`, while the owner PREPENDS it — so delegation hands every existing release adapter its binary twice, on the least reversible surface in this repo. Rejected during round-2 repairs: expressing the capture lane's repo-identity requirement by widening the owner's flat `required` set to carry one caller's disjunction; it is checked in the lane where the vocabulary lives instead.
- Targeted verification: `#557` DISCHARGED and its `_KNOWN_UNCONSOLIDATED` entry REMOVED — the exemption list shrinks from two to one. Proven by construction: a `source_capture` template naming an unknown placeholder is now refused (it used to raise a raw `KeyError` inside a lane whose refusals are otherwise typed); a template naming NO repository in either spelling is refused before the backend is reached; both real spellings (`{repo}`, and `{owner}`+`{name}`) resolve; a brace-bearing JSON part refuses typed with the doubling remedy named; the gh GraphQL default is unchanged. `#559` KEPT with a measured reason, and the reason is EXECUTED rather than argued: `test_the_binary_contract_is_why_they_are_not_one_function` runs the same default through both and shows the owner producing `['gh', 'gh', 'release', 'view', 'v1']`, and separately shows that changing `release_backend.binary` changes nothing. The DRIFT is repaired and pinned in both directions, and the differential now covers all four ops in `OP_PLACEHOLDERS` rather than one. Mutation on the REPAIRS: 4/4 on the build, 3/3 on round 1, 5/5 on round 2 — one of which SURVIVED first (a mirror-only assertion passed over a broken source, because the generated mirror lags until sync) and is now killed by pinning the source as well. `run_slice_closeout.py --skip-broad-pytest` verdict `completed`; 131 tests across six suites pass; both reviewer boundaries `clean` and verified before any repair.
- Test duplication pressure: The duplicate ratchet HARD-BLOCKED once and was right, naming the exact pair `#559` describes. Classified `intentional` in `dup-review.json` with the measured binary-position reason rather than baselined away, and the classification points at the differential test that keeps the reason honest. Length: `tests/test_issue_source_capture.py` crossed its cap at 802/800, and the six new tests moved to their own module on a COHESIVE boundary — everything moved answers one question (does the lane delegate?) while the parent file is about capture completeness — rather than being shaved or spilled into an `_extra_lib` companion.
- Critique: Two delegated bounded rounds, both fingerprinted `clean` and verified before any repair. Six blockers, and every one was in a repair. Round 1: (B1) the new owner loader knew only the SOURCE-tree layout, so in the exported mirror the owner path does not exist — and `spec_from_file_location` returns a spec WITH a loader for a nonexistent path, so my shape guard structurally could not fire and `exec_module` raised an untyped `FileNotFoundError` into a lane whose entire contract is typed refusal codes. Worse, it fired BEFORE the gh-default return, so every installed capture would have died, not only templated ones. The repo already owned the two-layout pattern in two places. (B2) the debt ledger's module docstring still said the copy was NOT removed while the set entry was gone — rot in the half no test iterates. Round 2 read those repairs: (B3) `CaptureRefusal` subclasses `RuntimeError`, so the loader's own new typed code was caught by the caller's broad `except RuntimeError` and re-raised as `invalid_capture_command` — routing an operator to the adapter file for a broken INSTALL. The code the repair added could never be observed. (B4) my new both-layouts test RE-IMPLEMENTED the loader's candidate list and asserted on its own copy, so it would have passed with the loader deleted — a second copy of the rule under test, inside the slice about copies of a rule. (B5) a brace-bearing template still escaped untyped, because `PLACEHOLDER_RE` matches only `{lower_snake}` and a JSON part clears the allowlist and then raises inside `format` — and a `source_capture` template is GraphQL/JSON-shaped by nature, so that is the EXPECTED case here. The release copy already guarded it. (B6) the delegation passed `required=frozenset()`, discarding the identity protection slice 2 had just built, in the slice that consolidates onto that very owner.
- Off-goal findings: No new issues filed. `#559`'s residual is now recorded in three places that agree: the `_KNOWN_UNCONSOLIDATED` entry, the `dup-review.json` classification, and an executable test. Recorded, not repaired: the parametrised differential exercises only the TEMPLATE path, so the gh-default branch is compared per op only indirectly; and `adapter-contract.md` previously said `release_backend` mirrors `issue_backend`, which the new test measures to be false in exactly the binary position — the doc now says so.
- Lessons carried forward: 1) `A test that re-implements the thing under test` is the same defect as `a copy of a rule`, and I shipped one inside the slice about copies of rules. The tell is structural: if the test rebuilds the candidate list, the parse, or the lookup, it is a second implementation and it will pass while the first is broken. CALL the function. 2) An exception hierarchy is a contract: `CaptureRefusal` subclasses `RuntimeError`, so a broad `except RuntimeError` translating an owner's errors silently ate the lane's own typed refusal. When adding a typed refusal inside a function whose caller translates a supertype, check what the caller catches. 3) `spec_from_file_location` returns a spec with a loader for a path that does not exist — a guard on `spec is None` cannot detect a missing file. Check `is_file()`. 4) Consolidating onto an owner means inheriting the owner's PROTECTIONS, not just its code: passing `required=frozenset()` took the delegation and left the identity floor behind, one slice after building that floor. 5) A mirror-only assertion lags the source until the next sync, so a mutant against the source survived a pin that reads the mirror. Pin the source; the mirror is generated.
- Metrics:

### Slice 7: Slice 4 build (#556) — a check that could only fire for one directory name now fires for a consumer, and both rounds landed on the repairs again

- Objective: Make `critique_adapter_codex_profile_drift` reachable for a consumer-shaped repo, proven by CONSTRUCTION — and without turning a permanent green into a wolf-cry.
- Why this approach: Cheapest of the filed set and the same permanent-green class as `#552`, ten lines from the predicate `#552` repaired. It was found by that issue's own delegated resolution critique sweeping the same function family.
- Commits: the slice commit carrying the new module, the predicate, the tests, and the regenerated `plugins/` mirror.
- What changed: New module `scripts/setup_critique_adapter_inspection.py`, split out of `scripts/setup_agent_docs_lib.py` when that file crossed its 480-line cap — it carries `CODEX_DEFAULT_REVIEWER_TIER_FIELDS`, the new `CODEX_POLICY_DECLARATION_TOKENS` and `_declares_codex_reviewer_profile()`, and the moved `_detect_critique_adapter_normalization()`. Tests: `tests/quality_gates/test_setup_inspect_critique_adapter.py` grows from 9 to 17, and two pre-existing greens gained a `found is True` precondition. Generated: `plugins/` mirror synced before validators each time.
- Alternatives rejected: Rejected: the issue's third option, deleting the check. Its subject is real — a reviewer profile that silently drifts is exactly what the finding is for — and the reach problem is in the gate, not the check. Rejected: having setup WRITE a declaration the reader then requires (the `#552` remedy), because a gate already forbids the generated template from baking a model id into the contract, so the renderer cannot be the writer here. Rejected during round-1 repairs: keying adoption on `any profile FIELD being declared`, which would tell a repo pinned to another model that it drifts from a Codex default it never adopted. Rejected during round-2 repairs: excluding `model` from the measured fields on a circularity worry — a tier naming the model is by definition not drifted on it, so excluding the field cost nothing and silently dropped the mixed case.
- Targeted verification: Acceptance proven by CONSTRUCTION at both ends. FIRES: a repo in a directory named `my-product`, with no prose declaration at all and an adapter declaring the profile the way a consumer would, now produces the `review_required` finding — and the test asserts WHICH tier drifted, because an earlier version could have fired from an absent tier instead. INVARIANT: two repos identical in every file and differing only in directory name now produce the same verdict; before, one fired and the other structurally could not. DOES NOT over-fire: a repo pinning `claude-opus-5` is left alone, a repo declaring one correct tier is left alone, and both assert the adapter actually LOADED so a green cannot pass for an unrelated reason. Mutation on the REPAIRS: 4/4 on the build, 2/2 on round 1, 2/2 on round 2 — including restoring the directory-name predicate, reverting the prose token to one no writer emits, measuring absent tiers again, and dropping the drifted fields from the message. `run_slice_closeout.py --skip-broad-pytest` verdict `completed`; 137 tests across five setup suites pass; both reviewer boundaries `clean` and verified before any repair.
- Test duplication pressure: Eight tests added to one existing module; the dup ratchet stayed clean with no new families. Length headroom was the binding constraint and was NOT shaved: `setup_agent_docs_lib.py` crossed its cap at 487/480, and the critique-adapter concern moved to its own module on a cohesive boundary — everything moved answers one question (what does this repo's critique adapter declare, and does it match the profile it claims?) while the parent inspects AGENTS.md prose surfaces.
- Critique: Two delegated bounded rounds, both fingerprinted `clean` and verified before any repair. Four blockers, all in repairs. Round 1: (B1) keying adoption on the model made `the repo left the profile entirely` unreachable where it used to fire inside `charness` — a coverage DELETION alongside the reach widening — and my docstring claimed other findings covered it, which is false, because the missing-adapter finding requires the adapter to be absent. (B2) drift was measured against the literal pair `high-leverage`/`medium`, each defaulting to `{}` when absent, so a consumer declaring ONE correct tier drifted against an empty dict whose every field is `None != expected` and got a `review_required` finding naming a tier it does not have — a wolf-cry I introduced, made newly reachable for consumers by removing the very gate that had hidden it. Round 2 read those repairs: (B3) my fix for B2 narrowed measurement to that pair's truthiness, so a repo with a RENAMED tier evidenced adoption and then measured NOTHING — a permanent green for a repo shape my own docstring claimed to support, which is this check's original defect reproduced inside its repair, in the opposite direction from the round-1 finding. (B4) the comment I wrote to be honest about the prose token claimed it is emitted by no production writer; opening `default-surfaces.md` refuted that — it INSTRUCTS an agent to write exactly that profile into a repo's contract. Advisories taken as fixes: two new greens lacked a loaded-adapter precondition, and the finding reported tier names while discarding the drifted FIELDS it had computed, so `left the profile` and `has fork_turns: all` read identically.
- Off-goal findings: Recorded, not filed: a live two-spellings tension this slice surfaced rather than created — the setup RENDERER is gated against baking a model id into the contract, while `skills/public/setup/references/default-surfaces.md` instructs an agent to write exactly that profile into `## Subagent Delegation`. An agent following the reference produces an AGENTS.md the same inspector can flag. The module now records the tension where the predicate reads it rather than smoothing it over; resolving it is a setup-contract decision, not this slice's.
- Lessons carried forward: 1) The same line moved in OPPOSITE directions across two rounds, and both moves were defects: too wide (measuring absent tiers) then too narrow (measuring only a literal pair). The invariant neither version held is the one to state — the set a check MEASURES must match the set its applicability predicate ITERATES. When those two are written in different places, they drift, and the drift is invisible from either site. 2) Widening a check's reach and preserving its coverage are separate obligations. Round 1 caught a coverage deletion hiding inside a reach improvement; a permanent green becoming a narrower green is not progress, and only asking `what could fire before that cannot now` finds it. 3) A comment written specifically to be HONEST about a limitation was itself false, because I described the writer landscape from memory instead of opening the reference. Being about honesty is not the same as being checked.4) Length caps keep producing better structure than the code had: the split this forced is a real concept boundary, and it is the second time this session that the cap named a module that wanted splitting.
- Metrics:

### Slice 8: Slice 5 — bundle proof, which was RED, and the goal closeout

- Objective: Prove the bundled state with the broad suite once at this boundary, record the verification lock, and close the goal through its own floor with a successor designed from what this run measured.
- Why this approach: Composition can drop what each slice proved alone, and no earlier slice was permitted to claim a broad green. This is the only place that claim is allowed to be made.
- Commits: the bundle-proof commit carrying this record, the four repairs the broad run exposed, the retro, the disposition review, and the successor goal; then a bookkeeping commit for the terminal flip.
- What changed: `tests/quality_gates/test_closeout_authorization_ingress.py` (`BackendSpy` now echoes the issue and repository it was asked about). `tests/quality_gates/test_goal_artifact_cadence_owner.py` (new `_shaped_non_terminal` helper; two tests decoupled from one artifact's lifecycle). `charness-artifacts/spec/2026-08-07-issue-514-515-518-owner-inspection.json` and its freeze receipt (re-stamped WITH a recorded basis). New: `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`, the disposition review beside this goal, and `charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md`. Regenerated: `recent-lessons.md`, `lesson-selection-index.json`, `plugins/` mirror.
- Alternatives rejected: Rejected: treating the broad run's four failures as environmental and proceeding. One was a real regression this goal introduced. Rejected: reverting the post-close number check that caused it — the check is correct, is the same class as the repository check beside it, and the closeout verifier already had its equivalent; what was wrong was a test double that modelled a backend answering about a different issue than it was asked for. Rejected: deleting the two cadence-owner tests that broke when their live fixture reached `complete` — their intent is sound and the coupling, not the assertion, was the defect. Rejected: re-stamping the freeze silently, as the five prior re-stamps did.
- Targeted verification: BUNDLE PROOF, and the first run was RED: `pytest tests/` returned `4 failed, 7964 passed` over the bundled state. All four were read rather than routed around. (1) A REGRESSION this goal introduced: slice 2's post-close identity check refused a shared `BackendSpy` that answered `number: 1` for every issue, including one asked about `#9001`. The check is right; the spy modelled a backend that cannot exist, and now echoes what it was asked. (2 and 3) Two `cadence_owner` tests read the `one-rule-one-owner` artifact as a realistic fixture and poison one line — and slice 1 flipping that goal to `complete`, which was this goal's own acceptance, made the refusal they assert deliberately skip (`a terminal record is one nobody may repair`). Decoupled by normalising the fixture's status rather than by weakening either assertion. (4) The source-freeze receipt went stale because slice 2 edited a frozen locator; re-stamped under the standing operator ruling, and — for the first time in six re-stamps — WITH a recorded basis naming the change, why it does not touch what `#514/#515/#518` reason about, and what is explicitly not claimed. That basis is the residue `#562` names. Re-run over the repaired bundle: `pytest tests/` returns **7968 passed, 0 failed** in 758s. `run_slice_closeout.py --verification-lock` records the lock over that state.
- Test duplication pressure: No new duplicate families; the dup ratchet is clean. The three tests changed here were all REPAIRED rather than weakened, and each carries the reason in its docstring: a spy made realistic, a fixture decoupled from one artifact's lifecycle, and a freeze note that records its basis.
- Critique: No new delegated round: this slice adds no verdict logic. Its own findings came from the broad gate, which is the fresh eye this boundary is for, and it found something no slice-level gate could — a regression whose blast radius crossed from `issue` into a shared test double, and two tests whose subject was an artifact this goal deliberately changed. Worth recording as the strongest argument for the bundle boundary existing at all: every slice was green at its own boundary, three of these four failures were invisible from inside any single slice, and the fourth was a regression a slice's own suites had no reason to run.
- Off-goal findings: No new issues filed. The freeze re-stamp is now the sixth, and the first with a basis — evidence for `#562` rather than a new finding. Two operator decisions are queued: the direction for `#562`, and the renderer-versus-reference spelling split in `setup`. A third queue item records that `git push` remains ungranted for the 29 local commits.
- Lessons carried forward: 1) The bundle boundary earned its cost in one run. Every slice was green at its own gate; three of the four broad failures were invisible from inside any single slice, and one was a real regression. A goal that skips this boundary ships a green that was never composed. 2) A test whose fixture is a LIVE artifact inherits that artifact's lifecycle. Both cadence tests were correct, well-reasoned, and used a real goal deliberately — and both broke because this goal did the thing it was created to do. Normalise the axis the test is not about. 3) My repair's blast radius crossed a package boundary into a shared test double, which no slice-level suite would have run. When a check is added at an irreversible boundary, grep for the doubles that stand in for that boundary, not just its callers. 4) The freeze re-stamp is the sixth and the first to record a basis; doing that took two sentences and turned a mechanical reflex into a reviewable decision, which is the entire content of `#562`'s proposal.
- Metrics:

## Context Sources

Durable references this goal was shaped from, in reading order.

1. `charness-artifacts/goals/2026-08-08-one-cadence-one-owner-stop-contradicting-the-agent.md`
   — the immediate predecessor, `complete`. Its `## Slice Log` holds the measured
   instance behind every lesson in this goal's `## Goal`, including all three
   round-2 blockers and all three refuted premise checks.
2. `charness-artifacts/retro/2026-08-08-one-cadence-one-owner-retro.md` — the
   durable owner of the two gate-proof lessons (inversion-blind substring pins;
   live-repo-state tests needing injection).
3. `charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`
   — still `active`, owes only `#536`'s closeout. Slice 1's subject.
4. `docs/design-north-star.md` — read while SHAPING. It governs where this goal's
   teeth belong: `#558` is the one claimed item that reaches an irreversible
   boundary (an issue close), so it gets construction-proof rather than a suite
   verdict, and a different observer than the one that produced the fix. The rest
   are reversible repo-local repairs where judgment is the default and a gate that
   cries wolf costs more than the defect.
5. Live tracker recount 2026-08-08: 32 open, reconciled against the claim split in
   `## Backlog Recount`.

## Interview Decisions

- **Ordered by leverage, not size.** `#536` is first because one closeout retires
  an entire active goal artifact, and because two live goals is the "one issue,
  two owners" shape this family has repaired three times in code.
- **`#558` before the copy-rot issues.** It is the only filed item that reaches an
  IRREVERSIBLE boundary: a wrong-repo `CLOSED` verdict is a false green on a real
  issue. Severity outranks cheapness.
- **`#562` deliberately NOT claimed**, despite being this family's own finding and
  despite the measurement being complete. Rejected alternative: fold it in as a
  sixth slice. Refused because it is a proof-surface DELETION (~35 `sha256`
  references, a schema bump, the mirror) and this family's measured record is that
  every proof-surface slice shipped a fix carrying the class it fixed. It wants a
  goal-sized budget with two rounds, not a tail slice.
- **Five slices, not nine.** Rejected alternative: carry the predecessor's full
  remaining plan. Refused on its own evidence — it reached three of nine.
- **The original slice 4 is re-scoped, not dropped.** Its acceptance ("
  `recent-lessons.md` carries the two lessons") turned out to be about a GENERATED
  digest, so the real work is understanding the selection index. The durable retro
  artifact already carries both lessons; that is recorded rather than re-done.

## Plan Critique Findings

- Corrected while drafting: the first shape put the five filed issues first
  because they have numbers, leaving `#536`'s closeout last. That would have left
  a second goal artifact live for the whole run — the exact defect the goal
  family exists to repair, reproduced in its own plan.
- Corrected while drafting: this goal's `## User Acceptance` originally restated
  the gate cadence. That is precisely what the predecessor's slice 1 repaired, and
  its validator now REFUSES it — the cheapest possible dogfood, caught before
  activation rather than by the gate.
- Open risk, not resolved: slice 1 flips another goal's status. If `#536`'s
  closeout floor cannot be met (the draft does not verify, or the delegated
  critique finds the work incomplete), slice 1 must STOP and record a blocker
  rather than flip a goal to terminal on an unmet floor. The floor is the
  authorization, not a checklist to route around.
- Open risk, not resolved: `#557`/`#559` may turn out to be one repair, not two.
  The predecessor family measured twice that issues sharing a FACE do not share a
  REMEDY. Premise-check them separately before bundling the slice.
- Named, not folded: the broad suite has not been run since before this family's
  commits. Slice 5 owns it, and no earlier slice may claim a broad green.

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

Retro: charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md
Host log probe: skipped: host-log-not-exposed: this artifact carries no `Host metric window:` line, so `probe_host_logs.py` reports `goal_window_audit: not_requested` and can bound nothing to this goal; the session's own JSONL exists but attributing a whole-session token and tool-call total to one goal would be a fabricated per-goal metric rather than a measured one.
Disposition review: charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues-disposition-review.md

## User Verification Instructions

## Auto-Retro

Retro dispositions: applied: the successor `charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md` budgets TWO delegated rounds per verdict-logic slice as a plan-level COST, on this run's measurement that eighteen blockers across ten rounds were all in repairs; applied: that successor's Low-Cost Checks run the dup ratchet and length headroom EARLY in each slice, after three commit-boundary blocks here each forced an aggregate re-run; applied: the four traps no gate holds are carried in the successor's `## Active Operating Frame` and in the regenerated `charness-artifacts/retro/recent-lessons.md`; issue #561; issue #562. Reviewed for binding and honesty in `charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues-disposition-review.md`.
Structural follow-up: issue #561 (recurs: measured across three probes and five hand re-stamps — two probes pin EQUALITY against a corpus ordinary work mutates, while a third pins the invariant `min_residual >= floor` and has never needed a refresh)

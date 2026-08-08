# Achieve Goal: Retire the second live goal, then close the four filed issues that reach a verdict

Status: active
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 1 — `#536`'s closeout. Premise CONFIRMED (both delivery and the
  owner claim, at definition sites). Both delegated rounds are complete and the
  seven blockers they found are repaired. `validate-closeout-draft` reports
  `draft_verified`. Remaining: commit the carrier, close through the adapter,
  verify `CLOSED`, then retire the `one-rule-one-owner` goal.
- Current slice intent: close `#536` through the full floor and retire the second
  live goal artifact. Spans the closeout commit and the goal-retirement commit.
- Next action: run the closeout aggregate, commit the carrier, then
  `close-with-comment` + `verify-closeout --expect-state CLOSED`. Then flip
  `2026-08-08-one-rule-one-owner-one-check-its-own-voice.md` to a terminal status
  — and NOT before `#536` reads back `CLOSED`, because that goal's only remaining
  obligation is this closeout.
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
| 1 | Close `#536` and retire the still-active `one-rule-one-owner` goal | It is BUILT and reviewed; one closeout retires a whole goal artifact, and two live goals is the "one issue, two owners" defect this family keeps repairing | `validate-closeout-draft` reports `draft_verified`, a DELEGATED resolution critique runs BEFORE the close, `verify-closeout --expect-state CLOSED` reads back through the adapter, and that goal reaches a terminal status | in progress — closeout floor met (`draft_verified`, two delegated rounds, seven blockers repaired); carrier + readback + goal retirement remain |
| 2 | `#558`: `{repo}` is the unclosed half of an issue's identity | A wrong-repo `CLOSED` verdict is a FALSE GREEN at an irreversible boundary — the highest-severity item in the filed set | The wrong-repo answer is refused or detected, proven by a constructed input rather than by a passing suite | planned |
| 3 | `#557` and `#559`: the fourth and fifth copies of the backend rule | `#559` had ALREADY drifted from the owner when it was filed, which is the copy-rot this family exists to stop | Each consolidated or classified with a measured reason; the exemption list shrinks | planned |
| 4 | `#556`: a check reachable only for a directory named `charness` | Cheapest of the filed set, same permanent-green class | The check fires for a consumer-shaped repo, proven by construction | planned |
| 5 | Bundle proof, goal closeout, successor | Composition can drop what each slice proved alone | Verification lock recorded; broad proof ONCE, at this boundary | planned |

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

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named

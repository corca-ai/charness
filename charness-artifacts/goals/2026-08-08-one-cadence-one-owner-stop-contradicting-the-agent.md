# Achieve Goal: One cadence, one owner: stop the harness contradicting itself to the agent

Status: active
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-one-cadence-one-owner-stop-contradicting-the-agent.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 3 — the closeout ledger states population and removals separately.
- Current slice intent: slices 1 and 2 are BUILT, reviewed in two rounds each,
  and committed. Next intent unit is slice 3: make the closeout ledger state
  population and removals as SEPARATE numbers, so `N implementations, M
  consolidated` cannot silently count the owner among the removals. Critique and
  broad proof do not re-fire within one unchanged intent — update this when the
  intent changes, not per commit (meaningful-slice-cadence).
- **Standing correction, twice missed:** verify the reviewer boundary IMMEDIATELY
  when a reviewer returns, BEFORE repairing. Both slices went straight into
  repairs and both had to be reconciled afterwards by declaring parent paths.
  That reconciliation is honest but weaker: it cannot distinguish reviewer writes
  from mine, and only the reviewers' lack of write tools makes it sound.
- Slice 1 premise check (verdict BEFORE the build): **HOLDS, but the goal
  OVERCOUNTS.** Measured over all 190 checked-in artifacts: THREE carry the
  contradiction, not five. The two `complete` ones the goal named carry an
  acceptance line but no deferring `Gate cadence:` line, so they were never
  two-owner contradictions; a live artifact the goal did NOT name
  (`2026-08-07-repair-declaration-to-verdict-at-root.md`, active) does, and was
  repaired under the goal's own stated criterion.
- Slice 1 review: TWO bounded rounds, both delegated. Round 1 found 8 (including
  a clobbered refusal reason and a `complete` skip disarmed by the repo's own
  annotated `Status:` style); round 2 read the REPAIRS and found the fix had
  carried its own class — one fact left with two owners, and a consolidation that
  routed two `complete`-state floors onto a level-aware section walk, a latent
  false green. All repaired; round-2 repairs accepted-unreviewed per the cap.
- Slice 2 premise check (verdict BEFORE the build): **REFUTED as written.** The
  goal names `check_current_pointer_writes.py` as the population owner; measured,
  that script hand-rolled its own `git ls-files` and the real owner is
  `scripts/repo_file_listing.py` (~21 consumers). Building to the letter would
  have shipped an eighth copy. The slice pointed the goal's own named precedent
  at the real owner instead.
- Slice 2 review: round 1 found a BLOCKER (the delegation crashed a standing gate
  under `CHARNESS_SUPPORT_DIR`) and that `require_git` had been added and never
  used; round 2 found the blocker fix had CARRIED ITS OWN CLASS, silently
  dropping this repo's 25 in-repo `skills/support/` files under the same
  override — D9 again, in the file that carries the D9 scar. Repaired to a union.
- Next action: premise-check slice 3 before building it. Read the predecessor's
  three blocked closeouts for the actual phrasing that failed, not the summary.
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

The predecessor closed four issues in five slices and cost roughly two and a half hours of pure wall-clock waiting, and the waste was NOT agent sloppiness. It was a surface contradicting its own owner, which is the same defect class the predecessor spent five slices repairing in code — one layer up, in the instructions the agent reads.

**The measured instance.** `skills/public/achieve/scripts/goal_artifact_scaffold.py` seeds the correct rule: `Gate cadence: pre-lock slices use run_slice_closeout.py --skip-broad-pytest; final/bundle proof records the verification lock and uses --verification-lock`. The same artifact's hand-written `## User Acceptance` then demands `./scripts/run-quality.sh --read-only exits 0 at EVERY slice boundary, and pytest tests/ -q reports zero failures`. Those two contradict: one says skip broad pytest until the lock, the other requires the full suite every slice.

An agent that reads its own acceptance criteria follows the acceptance criteria. The 12-minute suite ran about thirteen times. `./scripts/run-quality.sh --read-only` already runs a pytest phase in ~110s over 146 standing targets, so most of those runs re-proved what was already green.

**It is an idiom, not a slip.** That acceptance sentence appears verbatim in FIVE checked-in goal artifacts. And `check_goal_artifact.py` never compares the two sections — a repo-wide grep for `User Acceptance` or `Gate cadence` in that validator returns zero. So the cadence has one owner and the acceptance line is a second, contradicting owner that no reader reconciles. That is `#552`'s shape exactly: a rule stated twice, and the copy nobody validates is the one the agent obeys.

**The goal.** Repair the instruction surfaces that made a careful agent do the expensive wrong thing, and the guard-shaped surfaces the predecessor proved unreliable — then carry the predecessor's own filed structural findings. Per the north star this means fixing the surface that misled the judge, not adding gates that cry wolf: the predecessor measured that trade repeatedly, and every gate that fired in it was right.

The predecessor's other structural findings, each measured rather than supposed:

1. **A guard's POPULATION is a verdict surface.** Three successive versions of one sweep were wrong about which files they covered, each caught by a different reviewer. The repo already holds the better precedent — `scripts/check_current_pointer_writes.py` derives its population from `git ls-files`, is AST-based, covers four roots, and records that omitting one root once produced a clean report over a scope that excluded a real violation. That lesson was not carried across.

2. **Closeout ledger arithmetic failed the same way in three of four closeouts** — counting the owner among the things consolidated, so `four implementations, three consolidated` where two private copies were removed. Blocked three closeouts at the resolution-critique stage.

3. **A substring pin over a message cannot see an INVERSION.** Swapping two cause lists, or two command pairings, left ten assertions green while making the message actively harmful.

4. **A test whose subject IS live repo state cannot be mutation-tested by editing the worktree.** The edit is itself a state change; the test then fails at an earlier assertion and the mutant looks killed.

## Non-Goals

- Do not add a gate that re-runs the broad suite, or any gate whose failure an
  operator would learn to ignore. The predecessor measured this trade repeatedly and
  every gate that fired in it was right; the fix here is to stop a surface lying to
  the agent, not to add a louder one.
- Do not build a generic "two surfaces disagree" detector. Repair the measured
  instances first; generalisation is the last slice's question if the evidence
  supports it. The predecessor's Non-Goals said the same thing and were right.
- Do not rewrite the achieve gate cadence itself. It is CORRECT — cheap deterministic
  proof at commit boundaries, expensive proof at slice and bundle boundaries. The
  acceptance line that contradicts it is what moves.
- Do not take the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`,
  `#525`, `#527`, `#531`, `#532`). Still a different question: measuring prompt
  efficacy.
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

- The cadence is stated ONCE. `## User Acceptance` in a goal artifact no longer
  restates when broad proof runs; it points at `## Active Operating Frame`'s gate
  cadence, which the achieve scaffold owns. Proven by a validator that REFUSES an
  artifact whose acceptance demands per-slice broad proof while its cadence defers it.
- The scaffold no longer seeds a shape that invites the contradiction, and the two
  artifacts a session will still read — the active predecessor and the activatable draft
  — are repaired. Terminal records are NOT rewritten, by operator decision, so the
  validator skips `complete` artifacts rather than reddening on records nobody may fix.
- A new sweep-shaped guard inherits its POPULATION from one owner rather than
  hand-rolling it, and the owner is the `git ls-files`-derived precedent this repo
  already has — proven by pointing at least one existing hand-rolled sweep at it and
  showing the population is unchanged.
- The closeout ledger states population and removals as SEPARATE numbers, so
  "N implementations, M copies removed" cannot silently count the owner among the
  removals. Proven by the arithmetic that blocked three closeouts now failing a check
  instead of a reviewer.
- `charness-artifacts/retro/recent-lessons.md` carries the two lessons a gate cannot
  hold: a substring pin cannot see an inversion, and a test whose subject is live repo
  state cannot be mutation-tested by editing the worktree.
- Verification cadence follows `## Active Operating Frame`. This section deliberately
  names no command and no boundary frequency — that duplication is the goal's subject.
- The Slice Log records the premise-check verdict BEFORE each build.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin sync
  BEFORE validators; `check_python_lengths.py --headroom` before adding to a gated
  file; `check_dup_ratchet.py --summary` EARLY rather than at the commit-message
  boundary — it hard-blocked three times in the predecessor and was right each time.
- After ANY commit-gate rejection, run the aggregate (`run_slice_closeout.py`) rather
  than fixing one rejection at a time.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- Mutation-check every new verdict path, including one mutant at the CALL SITE. For a
  guard over a MESSAGE, mutate an INVERSION (swap two lists, swap two pairings) and not
  only a deletion — a substring pin survives every deletion-shaped mutant it should.
- For a test whose subject is live repo state, prove discriminating power by INJECTION.
  Editing the worktree changes the subject, and the mutant then looks killed.
- Before writing any instruction that tells a reader where to look, OPEN every location
  it names. Two message versions in the predecessor were worse than the number they
  replaced, both because a location was asserted rather than checked.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer AND
  channel than the push exit code.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | The cadence contradiction: fix the SOURCE, add the validator, repair only the artifacts still being read | Measured cost is ~2.5h in one session, and the source keeps reproducing the sentence | The validator refuses a reconstructed contradicting artifact, passes the repaired ones, and SKIPS `complete` artifacts; the scaffold no longer seeds the shape; THREE live artifacts repaired (not two — see the premise check) | done |
| 2 | One owner for a sweep's population, pointed at the `git ls-files` precedent | Three successive guards were wrong about their own population, each caught by a different reviewer | `check_current_pointer_writes` delegates to `repo_file_listing`; population 683 before / 683 after, identical set. The goal's NAMED owner was refuted and corrected | done |
| 3 | Closeout ledger states population and removals separately | The same arithmetic error blocked three of four closeouts at the resolution-critique stage | The blocked phrasing now fails a check rather than a reviewer, and the repaired phrasing passes | planned |
| 4 | The two lessons a gate cannot hold, written where the next session reads them | Both cost real rework and neither is gate-shaped | `recent-lessons.md` carries them; no new gate is added | planned |
| 5 | `#557` and `#559`: the fourth and fifth copies of the backend rule | Both filed by the predecessor with their reasons; `#559` has ALREADY drifted from the owner | Each consolidated or classified with a measured reason; the exemption list shrinks | planned |
| 6 | `#558`: `{repo}` is the unclosed half of an issue's identity | A wrong-repo CLOSED verdict is still reachable by reading | The wrong-repo answer is refused or detected, proven by construction | planned |
| 7 | `#560` and `#561`: ready-path coverage and equality-versus-invariant pins | Both are decisions the predecessor deliberately deferred with reasons | A fixture-ready case exists, or the deferral is re-recorded with its cost | planned |
| 8 | `#556`: a check reachable only for a directory named `charness` | Cheapest, and the same permanent-green class | The check fires for a consumer-shaped repo, proven by construction | planned |
| 9 | Bundle proof, goal closeout, successor | Composition can drop what each slice proved alone | Verification lock recorded; broad proof ONCE, at this boundary | planned |

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: 31 open issues on 2026-08-08 via `gh issue list --repo corca-ai/charness
  --state open --limit 100 --json number`. The predecessor closed four (`#552`, `#548`,
  `#555`, `#537`) and filed six (`#556`, `#557`, `#558`, `#559`, `#560`, `#561`), which
  is why the count rose from 29. Rerun the command before reshaping scope; the
  reconciliation is a command, not an adjective.
- Claims: `#557`, `#559`, `#558`, `#560`, `#561`, `#556` — the six the predecessor
  filed, all found by a delegated review or a gate rather than by reading the backlog.
  Plus the four structural repairs above, which have no issue numbers because they are
  defects in this repo's own instruction surfaces.
- Not claimed: the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`,
  `#525`, `#527`, `#531`, `#532`) — a measurement question. `#514`/`#515` — consumer
  ownership. `#539`, `#545` — provider/publication safety. `#530`, `#535`, `#554` —
  operator decisions carried in the predecessor's queue. `#534` — BUILT green, then
  REFUTED and REVERTED by an earlier goal; re-scope from the refutation, never from the
  title. `#536`, `#542`, `#546`, `#547`, `#549`, `#550`, `#518`, `#528` — the
  predecessor's unfinished slices, which stay with it until it closes; `#536` is built
  and awaiting only its closeout.

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

Recorded during the run:

- Routing: achieve — this run is a goal lifecycle, and `achieve` owns activation, the slice cadence, the slice log, and the closeout floors; slice 1's work was instruction-surface plus validator repair inside `achieve`'s own package, so no separate implementation owner was warranted.
- Gather: n/a — `## Context Sources` names only in-repo paths and one live `gh` recount; no external URL, Slack, Notion, Docs, or Drive source applies.
- Release: n/a — slice 1 touches no version bump and no install manifest; the `plugins/` mirror resync is a generated-surface sync, not a release surface.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED by the predecessor's recorded precedent, except
  one item held for the operator (below). Settled: closing the six claimed issues rides
  the repo's standing close-on-floor approval, and the predecessor closed four that way
  with a delegated resolution critique and an adapter readback each time; the broad
  scope is nine slices grouped by defect class, the same shape that held for four
  measured slices; every proof-level non-claim is named in `## Agent Verification Plan`
  and repeated at each closeout; no push, release, tag, or Cautilus run is implied by
  activation, and each stays per-request.
- Discuss before activation: RESOLVED 2026-08-08 by explicit operator instruction —
  "이미 지난 건 상관없음" (what is already past does not matter). Slice 1 does NOT
  rewrite terminal records. It repairs the SOURCE that keeps reproducing the sentence
  (`goal_artifact_scaffold.py`), adds the validator, and repairs only the artifacts a
  session will still READ: `2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`
  (active, still owes `#536`'s closeout) and
  `2026-08-08-finish-the-declaration-to-verdict-sequence.md` (draft, activatable).
  Left untouched as past: `2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`
  (complete) and the two superseded 2026-08-07 goals. The validator must therefore scope
  itself to non-complete artifacts, or it reddens on records nobody is allowed to fix —
  which would be the wolf-crier this goal's Non-Goals forbid.

## Slice Log

### Slice 1: The cadence contradiction — fix the source, add the validator, repair what is still read

- Objective: Stop a goal artifact from carrying two owners for one rule. `## Active Operating Frame`'s `Gate cadence:` line owns WHEN broad proof runs; several hand-written `## User Acceptance` sections restated it as per-slice broad pytest, and the measured cost was ~2.5h of wall-clock waiting in one predecessor session (a 12-minute suite run about thirteen times). Repair the scaffold that keeps reproducing the sentence, add a validator that refuses the pair, and repair only the artifacts a session will still read.
- Why this approach: First because its instance is still costing. The instruction-surface repairs come before the filed issues because they change how the remaining slices are executed.
- Commits: one commit on `main` (local); nothing pushed
- What changed: NEW `skills/public/achieve/scripts/goal_artifact_cadence_owner.py` (the floor). `goal_artifact_lib.py` — `check_cadence_owner`, wired into BOTH `check_goal` and `pursue_readiness`; `append_slice` delegated. `goal_artifact_pursue.py` — NEW `status_token` + `is_terminal_status`, sibling of `is_shaping_status`. `goal_artifact_markdown.py` — NEW `section_bounds` / `logical_lines`; `join_soft_wraps` delegates. `goal_artifact_floor_grammar.py` — NEW `masked_section_body` over the FLAT walk. `goal_artifact_template.md` + `references/lifecycle-during.md` — the source repair and its contract. `attention-state-visibility.json` — declares the new module's `skipped` state. Six sibling modules migrated off hand-rolled section walks (draft_frame, early_close_report, timebox, metric_window, operator_queue, blocked_matrix). Three live goal artifacts repaired: `2026-08-08-one-rule-one-owner-one-check-its-own-voice.md` (active), `2026-08-08-finish-the-declaration-to-verdict-sequence.md` (draft), `2026-08-07-repair-declaration-to-verdict-at-root.md` (active). Tests: `test_goal_artifact_cadence_owner.py` (22), `test_flat_section_walk_divergence.py` (8).
- Alternatives rejected: REJECTED a generic `two surfaces disagree` detector — the Non-Goals forbid it and the measured instances come first. REJECTED rewriting `complete` artifacts — explicit operator ruling; the floor skips them, because a validator that reddens on records nobody may repair is a wolf-crier by construction. REJECTED matching `run-quality.sh --read-only` as broad proof: it is a ~110s gate that per-slice cadence AGREES with, and the predecessor measured it naming four real defects nothing else caught. REJECTED classifying the section-walk duplication away when the ratchet blocked; consolidating was the correct repair and is the goal's own subject.
- Targeted verification: PREMISE CHECK (verdict BEFORE the build): **HOLDS, but the goal OVERCOUNTS.** The goal claims the acceptance sentence appears verbatim in FIVE checked-in artifacts. Measured over all 190: THREE carry a per-slice broad-proof acceptance line, and only those three carry BOTH it and a deferring `Gate cadence:` line. The two `complete` artifacts the goal named carry an acceptance line but NO cadence line, so they were never two-owner contradictions. A third live artifact the goal did NOT name — `2026-08-07-repair-declaration-to-verdict-at-root.md` (active) — does carry the pair, and was repaired under the goal's own stated criterion (artifacts still being read). Confirmed separately: `check_goal_artifact.py` compares the two sections nowhere, and the scaffold does seed the correct cadence. — PROOF: 22 + 8 new tests; 550 passing across the goal/achieve suites; 152 passing across the indirect-consumer paths round 2 named (`test_goal_helpers`, `test_record_metric_window`, `test_handoff_chunker_auto_draft`, `test_goal_coordination_floors`, `test_artifact_naming`). Corpus scan: 3 refused before repair, 0 after. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`: `Closeout verdict: completed`. Cautilus: `not-required`, no run. Reviewer boundary fingerprinted snapshot/verify around BOTH rounds: round 1 `clean`; round 2 `parent-attributed` with 17/17 declared and zero undeclared drift. MUTATION: 20 mutants constructed, 20 killed, counted from re-runs. Round-1 set (10): the `complete` skip, deferral-always-true, re-adding `run-quality.sh` to the broad matcher, dropping the frequency requirement, dropping the subdirectory lookahead, physical-vs-logical lines, an INVERSION swapping the two roles in the refusal message, and both CALL SITES. Round-1-repair set (6). Round-2-repair set (4): `activation_ready`, the unbalanced-fence guard, `status_token` punctuation, and `masked_section_body` back onto the level-aware walk.
- Test duplication pressure: `check_dup_ratchet.py --summary` hard-blocked FOUR times and was right every time. The first block is the one that mattered: it caught that the new floor was shipping a 6th copy of a section-locating walk already hand-rolled across the package — in a slice whose subject is one rule having one owner. Consolidating seven call sites was the repair. Final state: `ok: true`, 0 new families. Three families classified `intentional` with reasons (one cross-package `achieve`/`handoff` pair; two rotation artifacts of the consolidation itself).
- Critique: TWO bounded fresh-eye rounds, both delegated, both `parent-delegated` context. ROUND 1 found 8: `pursue_readiness` CLOBBERED the joined refusal reason (rebuilding the single-winner defect `_reason`'s own docstring records repairing) and borrowed the reserved `unshaped:` vocabulary; `status == "complete"` was DISARMED by the repo's own annotated `Status: COMPLETE (date) — ...` house style; the two owners were read with DIFFERENT line models, so a `Gate cadence:` value wrapping before `--skip-broad-pytest` (two live corpus instances) disarmed the floor entirely while it reported the reassuring "no cadence line that defers broad proof"; the acceptance body was scanned UNMASKED, so an artifact quoting the banned shape to warn against it was refused; `pytest -q tests/` was invisible; the exclusion's stated rationale was FACTUALLY WRONG (`run-quality.sh` does queue `run_standing_pytest.py`, so scope was the wrong argument — the right one is measured cost); the template asserted a `Gate cadence:` line no adapter is required to seed; and the repair had duplicated its own rationale into three artifacts — the same defect one layer down. ALL REPAIRED. ROUND 2 read the REPAIRS and earned its keep exactly as the contract predicts: the round-1 fix CARRIED THE CLASS IT FIXED. `pursue_readiness` set `pursue_ready: False` but left `activation_ready: True` in the same payload — one fact with two owners, in the slice about one fact having one owner. And the unplanned consolidation had routed the operator-queue and blocked-matrix floors onto the LEVEL-AWARE, case-insensitive `section_span` — against a sentence in that function's own docstring saying those two keep the flat variant "unless a divergence-exposing proof migrates them". Under it an ordinary `### Operator Decision Queue` quoted in a slice log becomes the section, so a `- Decision:` line there satisfies a `complete`-state floor while the real H2 holds scaffold prose: a false green at a terminal boundary, latent in every artifact. Also: the floor was the one new reader consuming a possibly-fail-open mask while claiming fenced examples could not act as an owner; `is_terminal_status` was a third normalisation owner and missed the live `Status: complete.` spelling; and the `intentional` dup note made a completeness claim seven remaining copies contradicted. ALL REPAIRED; round-2 repairs are accepted-unreviewed per the two-round cap. NOTE — three of the four round-2 repairs initially SURVIVED their mutants; the tests were added and re-run until all four were killed. One test-side defect was found the same way in round 1: a `startswith` assertion went vacuous once reasons were joined.
- Off-goal findings: (1) The section-locating walk still has ~7 un-migrated copies inside the `achieve` package — `slice_plan_data_row_count` (in the very file that now hosts the owner, with a deliberately different `body_start == -1` fallback), `closeout_evidence`, `pursue`, `discussion`, `section_placeholders`, `closeout_delegation`, and `early_close_report`'s remaining walk. Recorded in the dup-review note rather than claimed as finished. (2) The `achieve`/`handoff` copies need a `skills/shared/` home; that is a cross-package move with its own compatibility surface. Both are slice-2 shaped (its objective is one owner for a population) and should be premise-checked against it rather than filed blind.
- Lessons carried forward: (1) PREMISE-CHECK THE POPULATION, NOT JUST THE PREMISE. The goal's count was wrong in both directions — two named artifacts were not contradictions, one unnamed live artifact was. A grep for the sentence would have inherited the overcount; running the floor over the whole corpus is what produced the real number. (2) THE RATCHET WAS RIGHT AND THEN THE RATCHET WAS THE PROBLEM. Its first block caught a real defect. But chasing a later rotated hash is what routed two `complete`-state floors onto the wrong section walk — a latent false green. A duplicate-hash chase must not drive the design of a proof surface; classify with a reason instead. (3) A REPAIR VERIFIED ONLY AGAINST THE FINDING THAT PROMPTED IT IS UNVERIFIED. Three of four round-2 repairs survived their mutants on the first pass. Mutate every repair, not only the original code. (4) VERIFY THE REVIEWER BOUNDARY BEFORE REPAIRING, not after — round 2's window had to be reconciled by declaring 17 parent paths because I went straight into repairs.
- Metrics: Host metrics not exposed to this session; no token/time figures claimed.

### Slice 2: One owner for a sweep's population — and the goal named the wrong owner

- Objective: A guard's POPULATION is a verdict surface: a sweep wrong about which files it covers reports clean over a scope that excluded the violation. Give the population one owner, and prove the population is unchanged.
- Why this approach: The predecessor measured three successive guards each wrong about their own population, each caught by a different reviewer. Slice 1's own dup-ratchet block was a fourth instance of the same class one layer down.
- Commits: one commit on `main` (local); nothing pushed
- What changed: `scripts/check_current_pointer_writes.py` — `_git_visible_python_files` delegates to `repo_file_listing.iter_matching_repo_files`; the hand-rolled `git ls-files` subprocess is gone and the module imports no process-spawning machinery. NEW `_display_path` (one owner for the reported name). NEW `--require-git-file-listing`, threaded `main` -> `scan_repo` -> the owner. `scripts/run-quality.sh:882` passes it. `tests/quality_gates/test_current_pointer_writes.py` — 27 pre-existing, 2 repointed, 6 new (35 total).
- Alternatives rejected: REJECTED imitating the goal's named precedent — see the premise check; it was itself a copy. REJECTED migrating the repo's other sweeps in the same slice: one delegation, measured before and after, is the acceptance criterion, and slice 1's lesson was that a consolidation's blast radius is where the real defects hide.
- Targeted verification: PREMISE CHECK (verdict BEFORE the build): **REFUTED as written — the goal names the WRONG owner.** The goal calls `scripts/check_current_pointer_writes.py` the `git ls-files`-derived precedent this repo already has. Measured: that script does NOT use the repo's shared population owner. It hand-rolled its own subprocess. The real owner is `scripts/repo_file_listing.py`, consumed by ~21 source-tree validators (round-1 review counted them; my own estimate of 10+ was understated), with its own error type, contract tests, and a checked-in debug artifact naming it as the convergence target. So the goal's precedent was a copy, and imitating it would have propagated one. The slice therefore points the goal's own named precedent AT the real owner. — PROOF: population 683 before, 683 after, identical sets, re-measured after every repair. 35 tests. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`: `Closeout verdict: completed`. `tests/control_plane/test_monorepo_layout.py` (the blast-radius path round 1 named): 6 passed. Reviewer boundary fingerprinted around both rounds; each reconciled `parent-attributed` with every drifted path declared and none undeclared. Three review claims independently verified by execution before acting: the split-layout crash (reproduced), git's C-quoting of a newline path (one quoted entry — NOT two fragments), and pathlib `**` matching zero directories (366 files, direct children included). MUTATION: 11 mutants, 11 killed. Round-1 set (3): reverting to the hand-rolled listing, dropping `skills/shared` from `SCAN_ROOTS` (the original measured defect), ignoring `require_git`. Round-1-repair set (4). Round-2-repair set (4): union-back-to-swap, a colliding external prefix, dropped `resolve()` symmetry, and an untracked-file union.
- Test duplication pressure: No new duplicate families; `check_dup_ratchet.py --summary` clean throughout this slice. The tests added are behavioural, not textual — round-1 review specifically rejected an earlier textual assertion as not testing what its name claimed.
- Critique: TWO bounded fresh-eye rounds, both delegated. ROUND 1 confirmed the premise verdict and found a BLOCKER I had shipped: my own docstring claimed an external `CHARNESS_SUPPORT_DIR` tree is now scanned rather than silently empty, and in fact three call sites did a bare `path.relative_to(repo_root)`, so a split-layout host got an uncaught `ValueError` from a standing gate. I reproduced the crash before repairing. It also found that `require_git` had been ADDED AND NEVER USED — ~18 sibling gates pass `--require-git-file-listing` and this one did not, so the slice added the ability to refuse and did not exercise it; two tests that passed for reasons other than the ones they named; and that my stated MECHANISM for the newline defect was wrong. ROUND 2 read the REPAIRS and earned its keep exactly as the contract predicts. The blocker fix CARRIED THE CLASS IT FIXED: `iter_matching_repo_files` SWAPS a `skills/support/` pattern for the external tree rather than adding it, so delegating naively DROPPED this repo's own 25 tracked files under `skills/support/` — silently, on precisely the hosts that set the override. That is D9 again, in the file that carries the D9 scar, and it traded a silently-empty external tree for a silently-dropped in-repo one. Measured: 683 files with no override, 660 under one. Repaired to a UNION (683 / 685). Round 2 also found that naming an external file `skills/support/<rel>` COLLIDES with a real, different, in-repo path, so a reader following the clickable `path:line` lands on unrelated code; that the corrected false mechanism had been fixed in one docstring and left intact in its twin; that the external-tree test stubbed the population owner and so could not support its own closing claim; and an asymmetric `resolve()` that would have gone green on Linux and red on macOS. ALL REPAIRED; round-2 repairs are accepted-unreviewed per the two-round cap. Round 2 also cleared the `--require-git-file-listing` safety question with a fact I did not have: `run-quality.sh:876` already passes that flag unconditionally six lines earlier, so no environment's git requirement changed.
- Off-goal findings: `docs/deferred-decisions.md:205` states that the static scanner continues to catch string-literal `latest.md` / `latest.json` writes only. That has been false since the computed-name detector landed. Pre-existing, adjacent, and not this slice's to fix — but it is a stale claim on a durable record, which is this goal's own subject.
- Lessons carried forward: (1) PREMISE-CHECK THE REMEDY'S NAMED OWNER, not just its diagnosis. The goal's diagnosis was right and its prescribed owner was a copy; building to the letter would have shipped an eighth hand-roll. (2) A DELEGATION IS A BEHAVIOUR CHANGE, and the shared helper's semantics are not the caller's. `iter_matching_repo_files` SWAPS the support root rather than adding it — a reasonable contract for its other consumers and exactly wrong for a repo-wide sweep. Measure the population under every layout the helper branches on, not just the default one. (3) VERIFY A REVIEW'S CLAIM BEFORE ACTING ON IT. Three were checked by execution here; one (the C-quoting mechanism) corrected my docstring, and had I taken the review's wording on faith I would have written a different wrong sentence. (4) The boundary-verify-before-repairing lesson from slice 1 was NOT applied here either — both rounds again needed reconciliation by declaring parent paths. It is now a frame line rather than a slice-log line.
- Metrics: Host metrics not exposed to this session; no token/time figures claimed.

## Context Sources

1. `charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`
   — the predecessor. Its `## Slice Log` holds the measured instance of every structural
   finding this goal claims, including the three guard-population failures and the
   ledger arithmetic that blocked three closeouts.
2. `skills/public/achieve/scripts/goal_artifact_scaffold.py` and
   `skills/public/achieve/references/lifecycle-during.md` — the OWNER of the gate
   cadence, read to confirm the seeded rule is correct and that the acceptance line is
   the copy that contradicts it.
3. `scripts/run-quality.sh` and `scripts/run_standing_pytest.py` — read and executed to
   establish that the read-only gate runs a pytest phase over 146 standing targets in
   ~110s, so the broad suite adds coverage but is not the slice-boundary proof.
4. `scripts/check_current_pointer_writes.py` — the `git ls-files`-derived, AST-based
   sweep precedent this repo already has, and which three later guards did not reuse.
5. Live tracker recount 2026-08-08: 31 open issues, reconciled against this goal's claim
   split.

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. TODO the repo's governing design standard, and what it says about THIS goal —
   which facets bear on its boundaries, where its teeth belong, and which
   irreversible boundaries it crosses. Read it while SHAPING, not at closeout:
   the standard is what tells you where a wrong answer escapes, and that is a
   Before-phase question. (The retro's `## North Star Alignment` asks the
   backward-looking half; this is the forward-looking one.)

## Interview Decisions

- Ordered by MEASURED COST, not by size. Slice 1 is first because its instance cost
  about two and a half hours of wall clock in one session and the sentence is in five
  artifacts, so it is still costing.
- The instruction-surface repairs come before the filed issues, because they change how
  the remaining slices are executed. Fixing the cadence contradiction after eight slices
  would mean eight slices paid the tax first.
- Grouped as "a surface contradicting its own owner" rather than by area. That is the
  predecessor's class one layer up, and the predecessor's evidence is that a class
  grouping lets slices share evidence — confirmed four times there.
- `#536` is NOT claimed even though it is built. It belongs to the predecessor, which
  owes only its closeout; claiming it here would give one issue two owners, which is
  this goal's own subject.

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

## Plan Critique Findings

- Corrected while drafting: the first shape put the six filed issues first because they
  have numbers and the structural repairs do not. That buries the change that makes the
  remaining slices cheaper behind the slices that would pay for its absence.
- This goal's own `## User Acceptance` deliberately names NO command and NO boundary
  frequency, because restating the cadence there is the defect it repairs. If a later
  edit adds one, the goal has reproduced its own subject — and slice 1's validator
  should catch it, which is the cheapest possible dogfood.
- Resolved, was the one blocking risk: slice 1's scope. The operator ruled that past
  records are out of scope, so slice 1 fixes the source and the two live-read artifacts
  and the validator must skip `complete` ones. That scoping is itself the interesting
  part — a validator that refuses what nobody is permitted to repair is a wolf-crier by
  construction.
- Open risk, not resolved: slices 2 and 3 add checks, and this goal's Non-Goals forbid
  wolf-criers. The justification is frequency — three guard-population failures and
  three ledger failures out of four closeouts — but if either check fires on correct
  work during its own slice, that is the wolf-crier signal and it should be withdrawn
  rather than tuned.
- Open risk, not resolved: nine slices is large, and the predecessor reached five. If
  slices 1-4 do not make the later ones visibly cheaper, the grouping premise is refuted
  and the goal should be re-cut rather than pushed through.

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

- **The section-locating walk has ~7 un-migrated copies left inside the `achieve`
  package** (slice 1). Consolidating seven call sites onto one owner was forced by
  the duplicate ratchet mid-slice and is genuinely done; the package is NOT
  finished. Remaining: `goal_artifact_markdown.slice_plan_data_row_count` — in the
  very file that now hosts the owner, and with a deliberately DIFFERENT
  `body_start == -1` fallback — plus `closeout_evidence`, `pursue`, `discussion`,
  `section_placeholders`, `closeout_delegation`, and `early_close_report`'s
  remaining walk. Recorded in the `dup-review.json` note rather than claimed as
  finished, because a first draft of that note asserted completeness and round-2
  review refuted it.
- **The `achieve`/`handoff` copies need a `skills/shared/` home** (slice 1). The
  one duplicate family left unclassified-by-repair spans two independently-shipped
  skill packages, which cannot import each other's private scripts. Accepted as
  `intentional` with that reasoning; the real fix is a cross-package move with its
  own compatibility surface.
- Both are slice-2 shaped — its objective is one owner for a population — and
  should be premise-checked against the `git ls-files` precedent rather than filed
  blind. Not filed as GitHub issues yet for that reason. NOTE: slice 2 did not
  absorb them; it delegated ONE sweep and measured it. They remain open.
- **`docs/deferred-decisions.md:205` carries a stale claim** (slice 2): it says
  the static current-pointer scanner catches string-literal filenames only, which
  has been false since the computed-name detector landed. Pre-existing and
  adjacent, but a stale claim on a durable record is this goal's own subject.

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

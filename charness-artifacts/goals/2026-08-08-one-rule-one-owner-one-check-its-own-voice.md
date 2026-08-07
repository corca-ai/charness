# Achieve Goal: One rule, one owner; one check, its own voice

Status: active
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 1 of 9 — `#552`, a checker requiring a token its renderer never
  emits. THREE delegated reviews complete (slice round 1, slice round 2, and the
  closeout resolution critique), all repairs committed, behavioural verdict taken
  from a detached worktree at `fe1546ed`. Remaining: post the closeout and close
  `#552`.
- Current slice intent: make the routing block `charness setup` writes readable
  as charness-managed, so the two AGENTS.md policy checks gated behind
  `charness_managed` can fire at all. Spans `37886090` (build + round-1 repairs),
  `6d0b308e` (round-2 repairs), `fe1546ed` (resolution-critique repairs), and the
  closeout commit. This intent is unchanged since activation, so critique and
  broad proof do not re-fire within it (meaningful-slice-cadence).
- Next action: post the closeout and close `#552` (`validate-closeout-draft`
  reports `draft_verified`, then `verify-closeout --expect-state CLOSED`), then
  premise-check `#548` before shaping slice 2.
- Carried into slice 2: the round-2 lesson is that a verdict-logic repair can
  reintroduce its own class through the SHAPE of its matcher, not its tokens —
  the one-sentence rule made punctuation load-bearing. For `#548`, expect the
  same trap in whatever mechanism replaces `write_artifact_path`'s two meanings.
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

Two goals in a row have now found the same three mechanisms, and the harness
caught every instance through its EXPENSIVE channels — bounded review and the
broad gate. The mechanisms are cheap enough to check; the instances are spread
across surfaces nobody has connected. This goal connects them.

**One defect class, three faces.** A verdict surface asserts something it did not
establish. It shows up as:

1. **One rule, two owners.** The same rule is implemented twice, so a fix lands
   on one copy and the other keeps its old answer — or, worse, the two disagree
   and nothing notices. Fixed twice BY HAND in the predecessor (a sibling gate
   predicate; two goal-artifact producers), and the tracker already carries four
   more: `#548`, `#552`, `#555`, `#550`.

2. **A refusal that cannot say its own name.** A correct refusal surfaces as some
   unrelated symptom, so an operator debugs the symptom. `#537` was hit LIVE in
   the predecessor — an unmatched-surface blocker appeared as five broken bundle
   tests — and worked around without anyone noticing the issue existed. `#536`,
   `#549`, `#542` are the same shape.

3. **A label that reads as protection but establishes nothing.** The predecessor's
   subject, unfinished: `#518`, `#528`, `#546`, `#547`.

`#552` is the sharpest instance in the tracker: a checker requires a literal
token that the renderer writing the block never emits, so `charness_managed` is
permanently False and TWO AGENTS.md policy checks can never fire. A gate that
cannot fire is a permanent green.

The predecessor closed early at 2 of 7 slices so its remaining claims could be
re-homed here rather than run under a frame that did not name what they share.

## Non-Goals

- Do not build ONE generic "duplicate rule" detector before three real instances
  are repaired. A framework built ahead of its evidence is how a gate becomes a
  wolf-crier, and the predecessor measured that trade twice.
- Do not take the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`,
  `#525`, `#527`, `#531`, `#532`). It is a different question — measuring prompt
  efficacy — and the predecessor's record says mixing it in is how a goal stops
  being reviewable.
- Do not close `#530` on the gate alone. The resolver still emits the literal
  string in its title; that is an operator decision carried forward, not a
  closeout to infer.
- No release, tag, version bump, push, or Cautilus run unless separately granted.

## Boundaries

- **Premise check is a phase, not a step.** 5 for 5 across this goal family,
  INCLUDING where the premise held. Its largest save wired a skill to the wrong
  owner before a line was written.
- **A slice that changes verdict logic owes round-1 AND round-2 bounded review,
  and round 2 reads the REPAIRS.** Now 4 for 4: every measured slice shipped a
  fix carrying the class it fixed.
- **Assert a floor's REFUSAL through the composed verdict, never only through the
  module that computes it.** Three instances in the predecessor. This is the
  house failure mode.
- **When a finding says "this predicate is wrong", grep every caller before
  repairing one.** Hardening one of two sibling gates makes the other reachable.
- **No denominator in a rationale without the command that produced it.** Two
  wrong numbers shipped in one paragraph last run, both derived rather than
  measured.
- **Sync before verify, and run the gate AGGREGATE after the first rejection.**
  Two full-suite runs and four serial re-runs were burned on these two.
- **A `-k` filter is not the suite.** Run `./scripts/run-quality.sh --read-only`
  at every slice boundary; it caught what filtered runs missed three times.
- Bounded reviewers run read-only in the shared worktree, fingerprinted, and the
  window is CLOSED before the parent starts repairing.

## User Acceptance

- `#552`: a repo seeded by `charness setup` reads as charness-managed, and the
  two AGENTS.md policy checks that could never fire now can — proven by
  constructing a seeded repo and observing each check fire.
- `#548`: `write_artifact_path` means ONE thing, or the two producers name their
  meanings distinctly; no caller can write to the previous review's file believing
  it is a fresh target.
- `#555`: one tracker backend has one owner; `handoff` consumes `issue`'s rather
  than reimplementing it.
- `#550`: adapter resolver duplication is reduced or classified with a measured
  reason, not left as an unreviewed near-copy.
- `#537`: a correct bundle-preflight refusal reports ITSELF; it no longer appears
  as unrelated broken tests.
- `#536`, `#549`, `#542`: each failure names what it is and what it did not
  establish.
- `#518`, `#528`, `#546`, `#547`: no declared-but-unreached surface renders as
  clean; a repo can declare a sub-key ABSENT; a budgeted label with no sample
  stops reading as protection; a re-bind reports WHICH identities moved.
- `./scripts/run-quality.sh --read-only` exits 0 at EVERY slice boundary, and
  `pytest tests/ -q` reports zero failures.
- The Slice Log records the premise-check verdict BEFORE each build.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin
  sync BEFORE validators; `check_python_lengths.py --headroom` before adding to a
  gated file; `check_dup_ratchet.py --summary` before writing the commit message.
- After ANY commit-gate rejection, run the aggregate (`run_slice_closeout.py`)
  rather than fixing one rejection at a time.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- Mutation-check every new verdict path and report the count from a re-run.
  Include at least one mutant at the CALL SITE, not only inside the helper.
- For every repaired predicate, mutate each caller independently.
- Construct the refused input; never infer a refusal from a green suite.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer
  AND channel than the push exit code.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

| Slice | Objective | Issues | Why HERE in the sequence | Status |
| --- | --- | --- | --- | --- |
| 1 | A checker requiring a token its renderer never emits — two policy checks that can never fire | #552 | Sharpest instance of the class, smallest surface, and a PERMANENT green today | planned |
| 2 | One key name meaning opposite things in two scaffolds | #548 | Same shape, and one branch can overwrite the previous review | planned |
| 3 | One tracker backend, one owner | #555 | Unblocks `#554` part 2; the duplicate was found by the predecessor's premise check | planned |
| 4 | A correct refusal that reports itself | #537 | Hit LIVE in the predecessor and worked around; also unblocks honest gate reads for later slices | planned |
| 5 | Failures that name what they did not establish | #536, #549, #542 | Cheaper once slice 4 has fixed the reporting seam | planned |
| 6 | Declared-but-unreached surfaces and absent sub-keys | #518, #528 | The predecessor's unfinished subject; largest surface, so it goes after the mechanisms are guarded | planned |
| 7 | Labels that read as protection | #546, #547 | Local, and slices 1-6 will have exercised them | planned |
| 8 | Resolver duplication | #550 | Cheapest last | planned |
| 9 | Bundle proof, goal closeout, successor | (none) | Composition can drop what each slice proved alone | planned |

## Backlog Recount

- Counted: 29 open issues on 2026-08-08 via `gh issue list --repo corca-ai/charness
  --state open`, then reconciled against this section by set-differencing the live
  numbers against the `Claims:`/`Not claimed:` lists parsed out of this very file —
  claimed + not-claimed = 29 exactly, no gaps, no already-closed entries. The
  reconciliation is a command, not an adjective: rerun it before reshaping scope.
- Claims: `#552`, `#548`, `#555`, `#550`, `#537`, `#536`, `#549`, `#542`, `#518`,
  `#528`, `#546`, `#547` — twelve issues sharing one defect class.
- Not claimed: the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`,
  `#525`, `#527`, `#531`, `#532`) — a different question, measuring prompt efficacy.
  `#514`/`#515` — consumer ownership, predating this line of work. `#539`, `#545` —
  provider/publication safety, unrelated to this class. `#530` and `#554` — carried
  forward with operator decisions recorded in THIS goal's Operator Decision Queue
  (the predecessor's queue carries only `#530`; a bounded round caught that
  mis-citation). `#535` — released for an operator decision, also queued below,
  because no goal has ever premise-checked it. `#534` — NOT claimed: a prior goal
  BUILT it green with seven passing tests, then REFUTED and REVERTED it, posted the
  refutation to the issue, and concluded it may not be worth building at all
  (`2026-08-07-close-every-open-issue-declaration-to-verdict.md`). Re-shaping a
  slice around the refuted framing is the Work Phase Map trap this goal's own
  Boundaries name; if `#534` returns it must be re-scoped from the refutation, not
  from the issue title.
- Overlap warning: `charness-artifacts/goals/2026-08-08-finish-the-declaration-to-verdict-sequence.md`
  is a LIVE draft that also claims `#518`. Two draft goals owning one issue is this
  goal's own subject at the artifact layer. Resolve the ownership before slice 6.

## Operator Decision Queue

- Decision: is the GATE the right surface for `#530`, or must the RESOLVER warn
  too? Owner: operator. Carried forward from the predecessor with its cost
  measurement (a 3.1s reader scan on every resolver invocation, including the 16
  subprocesses the gate itself spawns). Until resolved, `#530` stays open.
- Decision: is `#535` (identity-binding surfaces ship without a one-command
  re-bind) worth claiming at all? Owner: operator. Why deferred: it pairs with
  `#547`, which this goal DOES claim, but no goal has ever run a premise check on
  `#535` itself — it was carried between goal artifacts by inheritance. Unblock
  action: premise-check it, or say it is not wanted. Revisit trigger: slice 7
  (`#547`) discovering it cannot finish without the re-bind.
- Decision: does `#554` part 2 (an automated recount helper) ship once `#555`
  gives the tracker one owner? Owner: operator. Why deferred: the floor already
  makes the recount mandatory and visible; the helper is convenience, and its
  seam only becomes clean after slice 3.

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

CONFIRMED 2026-08-08 by explicit operator instruction in session: take the
structural class as the goal's center of gravity, go LARGER than the remaining
slices, and pull in the related open issues.

- RESOLVED — scope is the thirteen issues named in `## Backlog Recount`, chosen
  by defect class rather than by area.
- RESOLVED — the predecessor is closed EARLY at 2 of 7 by the same instruction,
  and its unfinished claims are re-homed here rather than run in parallel.
- RESOLVED — the prompt-surface cluster stays excluded; it is a measurement
  question, not a verdict question.
- RESOLVED — no push, release, tag, or Cautilus run is implied by activation.
  Each is per-request, and `#530`/`#554` closure awaits operator decisions.

## Slice Log

### Slice 1: Slice 1 premise check (#552) — CONFIRMED, both halves, before any build

- Objective: Before shaping any repair, establish by execution rather than by reading titles whether `#552`'s premise holds: that the detector `skill_routing_declares_charness_management` requires a literal token the shipped renderer never emits, and that two AGENTS.md policy findings are therefore unreachable for any repo `charness setup` seeded.
- Why this approach: This goal's Boundaries record the premise check as a PHASE, 5 for 5 across the goal family including where the premise held. `#552` also arrives with a `Suggested direction (not a decision)` naming a remedy, and the Work Phase Map's Change Discipline rule fires exactly here: verify the remedy's premise before shaping a slice around it.
- Commits: none yet — this record precedes the build, per this goal's User Acceptance (`The Slice Log records the premise-check verdict BEFORE each build`).
- What changed: No source changed. Read: `scripts/setup_skill_routing_lib.py`, `scripts/setup_agent_docs_lib.py` (`_detect_charness_subagent_policy`, and the second predicate caller at line 408), `skills/public/setup/scripts/render_skill_routing.py`, `skills/public/setup/SKILL.md`, `tests/quality_gates/test_setup_render_skill_routing.py`, `tests/quality_gates/test_subagent_delegation_ladder.py`, `charness-artifacts/spec/session-start-hook-host-split.md`.
- Alternatives rejected: Rejected: inferring the premise from the issue body, which already states it precisely. The issue is a claim about executable behavior, so it is cheap to EXECUTE and the record is then a measurement rather than a re-reading.
- Targeted verification: Executed the shipped detector against the shipped renderer's real output (imported `_render_skill_routing` and fed its markdown to `skill_routing_declares_charness_management`). VERDICT: CONFIRMED, and sharper than the issue states. Exactly ONE of six signals fails — signal 6 (`sessionstart` AND `context-only`); the other five (handoff/workflow-trigger, installed-metadata/model-judgment, read-only/catalog, gather/external/url, quality/validation) all pass against the renderer's real text. So `skill_routing_declares_charness_management` is False and `skill_routing_semantically_complete` is False for a setup-seeded repo. Second half confirmed by reading `_detect_charness_subagent_policy`: both `agents_missing_charness_dynamic_workflow_policy` and `agents_missing_subagent_model_policy` are guarded by `if charness_managed and ...`, so both are unreachable. Writer-of-record confirmed: `skills/public/setup/SKILL.md:60` runs this renderer and its markdown is what an operator writes into AGENTS.md.
- Test duplication pressure: n/a — no tests added or expanded in this record; it is a read-only premise verdict.
- Critique: Two findings the premise check produced that the issue does not name, both feeding the repair's shape. (1) A SECOND predicate caller exists at `scripts/setup_agent_docs_lib.py:408`, where the same False makes a seeded repo's own block read as `skill_routing_block_custom_or_drifted` and recommends `review_existing_skill_routing` — charness telling an operator to review the block charness just wrote. The Boundaries rule `grep every caller before repairing one` earned its place here. (2) EVERY existing fixture for this predicate — five in `test_setup_render_skill_routing.py` and the routing preamble inside `test_subagent_delegation_ladder.py`'s own BOTH-readers pin test — hand-writes `context-only`. The issue's line `Pinning a fixture is how this hid` is literally true of the test that was written to stop this class.
- Off-goal findings: `charness-artifacts/spec/session-start-hook-host-split.md` probe `P2` asked this exact question (`Does skill_routing_semantically_complete need a new signal set, or only edited strings? ... Determine during implementation`) and was never determined; that same spec's Constraints say `a renderer that disagrees with AGENTS.md is a drift bug by definition`. The spec named the drift, deferred the decision, and shipped. Not filed separately: it is this slice's subject and the repair resolves P2.
- Lessons carried forward: The premise held, so no reshape — but it held with one signal, not a diffuse mismatch, which makes the repair small and makes the canonical-spelling question the only real decision. Carry forward: the detector must keep working on HAND-WRITTEN AGENTS.md too, so it cannot become a string comparison against the renderer; the reconciliation belongs in a test that pins the renderer's REAL output, not in the predicate.
- Metrics:

### Slice 2: Slice 1 build (#552) — a checker requiring a token its renderer never emits

- Objective: Make the routing block `charness setup` writes readable as charness-managed, so the two AGENTS.md policy checks gated behind `charness_managed` can fire at all. Acceptance from the goal: a seeded repo reads as managed, and each of the two checks is observed firing.
- Why this approach: Sharpest instance of the goal's defect class, smallest surface, and a PERMANENT green today. Chosen first over `#518` deliberately — the predecessor stalled by putting its largest surface first.
- Commits: `37886090` (build + round-1 review repairs), `6d0b308e` (round-2 review repairs), `fe1546ed` (delegated resolution-critique repairs), plus the closeout commit. Round-2 repairs are accepted-unreviewed under the two-round cap; the round-3 repairs came from the issue-closeout resolution critique, which is a separate delegated review the closeout floor requires, not a third slice round.
- What changed: Owning source: `scripts/setup_skill_routing_lib.py` (signal 6 rewritten as `_declares_session_start_hook_is_not_authoritative` + `_routing_segments`; two adjacent completeness regexes un-brittled for inflection). Writers corrected: `skills/public/setup/references/default-surfaces.md`, `skills/public/setup/references/bootstrap-seams.md`. Tests: `tests/quality_gates/test_setup_render_skill_routing.py` (renderer pin, seeded-findings, five signal-6 behaviour tests, reference-writer pin), new module `tests/quality_gates/test_setup_routing_charness_managed.py`, `tests/quality_gates/test_subagent_delegation_ladder.py` (its hand-written routing preamble replaced by the renderer's real output plus a gate-is-open assertion), `tests/quality_gates/support.py` (`seed_normalize_repo` extracted). Records: `charness-artifacts/spec/session-start-hook-host-split.md` (P2 resolved), `docs/public-skill-dogfood.json` (setup evidence). Generated: `plugins/` mirror synced before validators each time.
- Alternatives rejected: Rejected — changing the RENDERER to emit `context-only` instead of changing the reader: it would fix future setups and leave every already-seeded repo permanently invisible. Rejected — making the detector compare against the renderer's output: it must keep reading hand-written AGENTS.md, so the reconciliation belongs in a test, not in the predicate. Rejected TWICE inside the repair itself, both times by bounded review: searching the section as one blob (lets the polarity word be about anything), then requiring ONE SENTENCE to carry the whole claim (makes punctuation load-bearing). What survived: the denial must name its own subject (`hook` or `block`), matched per line as well as per sentence.
- Targeted verification: Premise executed before the build (see the preceding Slice Log entry). Mutation checks: 4/4 killed on the first shape, then 9/9 on the redesign, including one mutant at EACH of the three call sites independently and one for each new verdict path (`A` drop the polarity subject, `B` sentence-only segmentation, `C` drop names-the-hook, `D` signal always true, `E` revert to the literal token, `F` pass collapsed text, `G` revert the inflection fix, `H`/`I` the two `setup_agent_docs_lib` call sites). One mutant SURVIVED mid-run — dropping `HOOK_NOUN_RE` killed no test — so the guard was real but unproven; a test was added rather than the guard deleted, and it is now killed. Refusal asserted through the COMPOSED `inspect_repo` verdict, not only the module that computes it. Both previously unreachable findings observed firing against a constructed seeded repo, and the real shipped delegation template observed clearing both. Parity differential via `scripts/parity_harness.py` over 34 REAL routing texts (renderer output, live AGENTS.md/CLAUDE.md, every routing-shaped literal in the setup tests, both reference docs): 0 divergences against the committed baseline, so the complement is unchanged; the intended deltas were then confirmed one by one. `./scripts/run-quality.sh --read-only` exits 0. Two counts appear in this record for the same command and both are real: 85 passed with `check-changed-line-mutation-coverage` UNPROVEN while the worktree was still dirty (that check refuses to certify a tree it cannot analyze), then 86 passed, 0 failed, no UNPROVEN once the work was committed. The second is the one that counts as proof. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review` verdict `completed`. Reviewer boundary fingerprinted around both review windows: round 1 `clean`, round 2 `parent-attributed` with no unattributed drift.
- Test duplication pressure: `check_dup_ratchet.py --summary`: `status: clean`, `new_code_family_count: 0`, `new_doc_family_count: 0`, `hard_block: false` — run twice, after each block of additions to a ratchet-scoped file. Length headroom stayed honest rather than shaved: a gate warned `test_setup_inspect_policy.py` was at 796/800, so the seeding helper moved to `support.py` and the new tests moved to their own module, taking that file to 712/800 (88 left) instead of squeezing two lines in.
- Critique: Round 1 (bounded, read-only, fingerprinted) returned 7 findings; all 7 were accepted and repaired. The load-bearing one was a THIRD writer — `references/default-surfaces.md` described the block with no standing claim at all, so a repo hand-written from the shipped reference stayed refused: the same one-rule-two-owners defect one layer out from the one the issue named. Round 2 read the REPAIRS and returned a genuine BLOCKER: the one-sentence rule I had introduced made the verdict punctuation-dependent, so BOTH directions came back — a bulleted block (no terminal periods) collapsed to one segment and silently restored the blob search it replaced, accepting a block that declared the hook AUTHORITATIVE, while a correct block spelling the claim as two sentences was REFUSED. Both were reproduced by execution before repairing. Round 2 also found a FOURTH writer (`references/bootstrap-seams.md`), showed the corrected guidance's own second spelling produced a block the code then rejected, and caught three overclaims in the records I had just written. The repo's rule that a verdict-logic slice owes round 2 is now 5 for 5 — and this is the first measured instance where round 2 found a blocker in the REPAIR rather than a gap in the original.
- Off-goal findings: Found by executing the reference docs against the reader rather than reading them: `CATALOG_FAILURE_ACTION_RE` was `\b(report|surface)\b`, which does not match `reports` — the third-person voice `default-surfaces.md` itself uses. So a block written from that reference read as drifted from the block that reference describes. Same reader/writer split as `#552`, one signal over, found inside this slice and fixed here with its own test rather than filed, because it is the same defect on the same surface. One new issue filed: `#556`, found by the delegated resolution critique sweeping the same function family — `scripts/setup_agent_docs_lib.py:160` gates a `review_required` finding on `repo_root.name == "charness"` or a phrase no writer in this repo emits, so it is a permanent green for every consumer repo. Filed rather than folded in: different contract, different owner, and the repair needs a design decision about what should declare that policy.
- Lessons carried forward: 1) A repair to verdict logic can reintroduce the class it fixes through the SHAPE of its matcher, not its tokens: the one-sentence rule was tighter in appearance and punctuation-dependent in fact. Ask of any new matcher `what unrelated property does this make load-bearing`. 2) A parity differential over real corpora is silent about shapes the corpus does not contain — 0 divergences across 34 real texts said nothing about bulleted blocks, because every real routing text in this repo joins the claim with a semicolon. Corpus agreement is evidence about the corpus. 3) `grep every caller` was not enough; the writers needed the same sweep, and there were four. 4) A surviving mutant is a decision point, not a nuisance: it correctly identified an unproven guard, and the answer was a test, not a deletion.
- Metrics:

## Context Sources

1. `charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`
   — the predecessor. Its Slice Log holds the measured instances of all three
   mechanisms and is this goal's evidence base.
2. `charness-artifacts/retro/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster-retro.md`
   — the retro whose `## Sibling Search` named this goal's scope.
3. Live tracker recount 2026-08-08: 29 open issues, reconciled against this
   goal's claim split programmatically.
4. `#552`, `#548`, `#537` read in full during shaping to confirm the class rather
   than infer it from titles.

## Interview Decisions

- Ordered by SHARPNESS, not by issue number or size. `#552` goes first because a
  check that can never fire is a permanent green and its surface is small.
- Grouped by defect class rather than by owning skill. The predecessor's evidence
  is that these instances share a mechanism, so slices can share evidence and
  avoid repairing the same shape three times independently.
- `#535` is NOT claimed despite being in the predecessor's list: it pairs with
  `#547`, and the predecessor recorded no premise check for it. Left for a
  decision rather than inherited silently.
- A generic detector is deliberately NOT slice 1. Three real repairs come first;
  generalization is slice 9's question if the evidence supports it.

## Plan Critique Findings

- Corrected while drafting: the first shape put `#518` first because it is the
  predecessor's next numbered slice. That buries the mechanism work behind the
  largest surface in the goal, which is exactly how the predecessor stalled at
  2 of 7. Reshaped to put the sharp, small, permanent-green instance first.
- Open risk, not resolved: thirteen issues is large for one goal. Mitigation is
  the class grouping — if slices 1-3 do NOT share evidence as predicted, that
  refutes the grouping premise and the goal should be re-cut, not pushed through.
- Open risk, not resolved: `#518` has never been scoped by any goal that claimed
  it. Its premise check must run before any remedy is shaped, and the record is
  5 for 5 that the named remedy is wrong.
- Open risk, not resolved: the portable-gate generalization is parked at slice 9
  of 9, and the two preceding goals reached slices 2 and 2. On that record slice 9
  is the least likely slice to be reached. The deferral is defensible on
  wolf-crier grounds; its SCHEDULING is not, and if slices 1-4 make the mechanism
  obvious the generalization should be pulled forward rather than left last.
- Open risk, not resolved: `#528` and `#550` are the weakest members of the class.
  `#528` is a missing third state (declared/defaulted/absent), a capability gap
  rather than a false green; `#550`'s acceptance can be discharged by classifying
  duplication rather than repairing a verdict surface. The re-cut trigger above
  extends to them.
- Open risk, not resolved: repairing duplication (`#550`, `#555`) can itself
  create a shared surface that drifts. Any consolidation ships with a test that
  fails if the two consumers diverge again.

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

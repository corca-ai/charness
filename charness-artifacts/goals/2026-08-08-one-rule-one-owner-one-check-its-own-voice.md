# Achieve Goal: One rule, one owner; one check, its own voice

Status: active
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 5 — `#536` built and BOTH review rounds complete. `#552`, `#548`,
  `#555`, `#537` are CLOSED and verified. Remaining for slice 5: post the `#536`
  closeout and close it.
- Current slice intent: `#536` — make a probe-drift failure name its cause,
  distinguish a corpus change from a rule change, and list every surface a re-record
  must touch. Spans `67beced4` and the round-2 repairs.
- Next action: post the `#536` closeout and close it. Then slices 5a (`#549`) and 5b
  (`#542`), which slice 5's premise check RE-HOMED because they share this issue's
  face and not its remedy — do not rebuild them as one slice.
- SLICE PLAN NOW HAS 11 ROWS, not 9. Rows 5a and 5b were added by slice 5's premise
  check. The goal is still described as 9-slice in prose above; read the table.
- Grouping premise CONFIRMED for the CLASS and REFUTED for one bundle: slices 1-4 each
  shared a mechanism, and slice 5's three issues shared only a face. That is the
  distinction to carry — a shared face predicts nothing about a shared remedy.
- Cross-slice lesson that keeps paying: I fix the instance an issue reports and measure
  against that instance. In slice 4 the class was two greps wider; in slice 5 the
  MESSAGE I wrote was twice worse than the number it replaced, both times because I
  asserted where something lived instead of checking. Version 1 would have deleted
  `_provenance`; version 2 sent a rule change to the corpus remedy by naming the wrong
  files. Check the location of every fact a message states.
- Issues filed while working, none planned: `#556`, `#557`, `#558`, `#559`, `#560`,
  `#561`. Every one came from a delegated review or a gate.
- Carried forward: (a) a test whose subject IS live repo state cannot be
  mutation-tested by editing the worktree — prove it by injection; (b) a substring pin
  over a message cannot see an INVERSION (swapped lists, swapped command pairings), so
  pin the pairing and the ordering, not the vocabulary; (c) the commit-msg gate reads
  prose for close keywords — `a fix: #536` in a sentence blocked two commits, and it
  was right to.
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
- `#536`: the probe-drift failure names its cause, distinguishes a corpus change from
  a rule change (whose remedies are opposite), and names every surface that carries
  the same numbers. Discharged by slice 5.
- `#549`, `#542`: each failure names what it is and what it did not establish.
  RE-HOMED to slices 5a and 5b by slice 5's premise check — they share the face and
  not the remedy, so slice 5 does NOT discharge these two.
- `#518`, `#528`, `#546`, `#547`: no declared-but-unreached surface renders as
  clean; a repo can declare a sub-key ABSENT; a budgeted label with no sample
  stops reading as protection; a re-bind reports WHICH identities moved.
- Every slice is proven green at the cadence `## Active Operating Frame` states.
  This line names no command and no boundary frequency on purpose; the frame owns that.
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
| 1 | A checker requiring a token its renderer never emits — two policy checks that can never fire | #552 | Sharpest instance of the class, smallest surface, and a PERMANENT green today | done |
| 2 | One key name meaning opposite things in two scaffolds | #548 | Same shape, and one branch can overwrite the previous review | done |
| 3 | One tracker backend, one owner | #555 | Unblocks `#554` part 2; the duplicate was found by the predecessor's premise check | done |
| 4 | A correct refusal that reports itself | #537 | Hit LIVE in the predecessor and worked around; also unblocks honest gate reads for later slices | done |
| 5 | A drift failure that names its cause and its full update set | #536 | Reproduced, and the only one of the three whose remedy is a message | done |
| 5a | A survive-truncation mechanism built once, and a consumer contract with no reader | #549 | RE-HOMED from slice 5 by its premise check: shares the face, not the remedy | planned |
| 5b | A refusal that cannot name a CLI/body disagreement | #542 | RE-HOMED from slice 5: needs a design decision about threading the carrier source, not a message | planned |
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

### Slice 3: Slice 2 premise check (#548) — HOLDS IN SUBSTANCE, MECHANISM MISSTATED; remedy reshaped before any build

- Objective: Establish by execution whether `#548`'s premise holds: that `write_artifact_path` means opposite things in the debug and quality scaffolds, and that only one of the two is safe to write to.
- Why this approach: This goal's Boundaries make the premise check a phase, and the Work Phase Map's Change Discipline rule fires specifically when a slice would be SHAPED around a remedy some durable record already names. `#548` names one: make the two producers' key names distinct, with debug's behaviour as the implied correct model. That model is what needed checking before a line was written.
- Commits: none yet — this record precedes the build, per this goal's User Acceptance.
- What changed: No source changed. Executed: `scaffold_quality_artifact.py --repo-root .` and `scaffold_debug_artifact.py --repo-root . --title 'Premise probe'`. Read: `skills/public/debug/scripts/scaffold_debug_artifact.py` (`payload_for`, `_resolved_followup_record_payload`, `_resolution`), `skills/public/quality/scripts/scaffold_quality_artifact.py`, `scripts/scaffold_artifact_lib.py`, and the live `charness-artifacts/{quality,debug}/latest.md` symlinks.
- Alternatives rejected: Rejected: accepting the issue's description of the debug side, which is the half a title-level read would have taken on trust. Executing both scaffolds cost two commands and changed the slice's shape.
- Targeted verification: VERDICT: the DEFECT holds, the issue's MECHANISM for the debug side does not. Confirmed as stated for quality: with `charness-artifacts/quality/latest.md` a symlink to `2026-08-07-quality-review.md`, the scaffold returns `write_artifact_path` = that existing dated file with `write_artifact_role: current_pointer_target`. Writing there overwrites a finished review, and because the path is dated nothing signals the mistake. REFUTED as stated for debug: the issue says debug resolves a FRESH dated record when the current pointer already resolves and explicitly rejects any candidate equal to the current pointer target. Executed, the debug scaffold returned `write_artifact_path` = `charness-artifacts/debug/2026-08-07-issue-518-...-debug.md` with `write_artifact_role: current_pointer_target` and `current_pointer_target_exists: true` — an EXISTING file, not a fresh one. Reading `payload_for` shows why: the fresh-record branch is guarded by `if _resolution(current_write_path) == "resolved"`, and `_resolution` returns resolved only when the artifact carries a literal `- Resolution: resolved` line. For an OPEN investigation the debug scaffold deliberately hands back the current record, because continuing the open investigation in the same record is its job. The rejection logic the issue describes exists only INSIDE the resolved-follow-up branch, not as a general property of debug's `write_artifact_path`.
- Test duplication pressure: n/a — no tests added or expanded in this record.
- Critique: The remedy the issue implies — rename or re-home the keys so quality's matches debug's safe semantics — rests on the refuted half. There is no single safe-target semantics to copy: debug's key means append to the open record here, or a fresh one if the last is closed, and quality has no resolution-state analogue to make that decision with. Shaping slice 2 as make-quality-behave-like-debug would have required inventing a resolution state for quality reviews, which is a product decision nobody has taken. The honest defect is narrower and sharper than the issue's framing: `write_artifact_role` already carries the truth (`current_pointer_target`), and what differs between the two skills is whether writing to a `current_pointer_target` is SAFE — which depends on whether that artifact is still open. The key name hides exactly that, and `#538` is the recorded instance of an agent nearly acting on it.
- Off-goal findings: Noted, not filed: both scaffolds return `write_artifact_role: current_pointer_target` for a path that already exists, and neither payload states whether writing there APPENDS to open work or DESTROYS finished work. That distinction, not the key name alone, is the thing a reader needs. It is this slice's subject rather than a separate issue.
- Lessons carried forward: 5 for 5 becomes 6 for 6, and this is the second time in this goal that a named remedy did not survive contact: `#552`'s suggested direction was sound but incomplete (the writer sweep found four more instances), and `#548`'s rests on a property its subject does not have. Carry into the build: the fix must make the SAFETY of a write target legible, not merely make two key names differ — renaming alone would leave both payloads still failing to say whether the target is open or finished.
- Metrics:

### Slice 4: Slice 2 build (#548) — one owner for the pointer rule, and a payload that says what writing destroys

- Objective: Make `write_artifact_path` mean one thing, and make the SAFETY of a write target legible rather than inferable. Acceptance from the goal: no caller can write to the previous review's file believing it is a fresh target.
- Why this approach: Second instance of the goal's class, and the premise check reshaped it before any code: the issue's implied remedy rested on a property its own subject does not have.
- Commits: `acdcc5a8` (build + slice round-1 repairs), `58b5a66c` (slice round-2 repairs), plus the resolution-critique repairs and closeout commit that follow.
- What changed: Owner: `scripts/scaffold_artifact_lib.py` (`current_pointer_state`, `published_pointer_state`, `current_pointer_write_path`, `write_target_facts`, `with_write_target_facts`, `dated_record_payload`). Consolidated onto it: `scripts/resolve_artifact_path.py`, `scripts/inventory_current_pointer_layouts.py`, `skills/public/quality/scripts/resolve_quality_artifact.py`, `skills/public/debug/scripts/scaffold_debug_artifact.py`, `skills/public/debug/scripts/plan_debug_run.py`. Facts added to every producer naming a write target, including handoff, critique, retro, ideation, and both run planners. Docs: `skills/public/debug/SKILL.md`, `skills/public/quality/SKILL.md`. Test: `tests/test_write_artifact_path_single_owner.py`. Records: `charness-artifacts/quality/dup-review.json` (four families classified). Generated: `plugins/` mirror synced before validators each time.
- Alternatives rejected: Rejected on premise-check evidence: making quality behave like debug, the issue's implied remedy. Debug's `write_artifact_path` is not a fresh target in general — its fresh-record branch is guarded by a literal `- Resolution: resolved` line, and for an open investigation it deliberately returns the current record. Copying that would have required inventing a resolution state for quality reviews that nobody has designed. Rejected: renaming the keys so the two producers differ, which would leave both payloads still silent about whether the target is open or finished. Rejected during round-2 repairs: lengthening `scaffold_debug_artifact`'s copied key list, because the same staleness would return with the next key; the facts are recomputed from the final write target instead.
- Targeted verification: SIX implementations of the pointer rule existed — the owner plus five private copies. Two were named by the issue, one was surfaced by the duplicate-ratchet gate mid-consolidation, and two by bounded review. Mutation: 6/6 killed on the consolidation, then 4/4 on the round-1 repairs (effect always `create_new_file`; facts not recomputed after the record swap; debug regrows its private copy; owner grows a repo-module import). `git show` used to confirm the removed copies returned `current_pointer_target_exists: None` exactly as the owner does, so no producer's published shape changed. Behavioural verdict from a DETACHED worktree at `58b5a66c` through the shipped CLIs' stdout: with `latest.md` symlinked to a finished `2026-08-01-quality-review.md`, `scaffold_quality_artifact.py` reports that path with `write_artifact_effect: overwrite_existing_content`, and `--intent record` reports a fresh dated path with `create_new_file`. `./scripts/run-quality.sh --read-only` exit 0; `pytest tests/` 7842 passed; closeout aggregate `completed`; dup ratchet clean.
- Test duplication pressure: The duplicate ratchet HARD-BLOCKED this slice three times and was right every time. First: the consolidation's own delegating stubs were near-identical, and the fix exposed a fourth copy of the rule. Second: adding the facts made critique, retro, and ideation identical, so the shared shape moved into `dated_record_payload`. Third: the one-line planner echo made the debug and retro packet builders converge. What remained after each extraction is per-package portability boilerplate, classified `intentional` in `dup-review.json` with a measured reason and an explicit `not claimed as measured against a prior scan` hedge, rather than baselined away. Length headroom checked; no file near a limit.
- Critique: Three delegated bounded reviews, each finding a real defect the previous one could not. Round 1 found the repair carrying the class it fixed: `scaffold_debug_artifact` swaps its write target through a FIXED KEY LIST that did not include the new facts, so the resolved-followup branch reported `overwrite_existing_content` for a path the code guarantees does not exist — while the `SKILL.md` sentence just written told the agent to trust it. Round 2 found the guard itself had become the defect: a hand-maintained PRODUCER list, already missing four producers, and a sixth copy of the rule in the debug planner that the readlink-shaped guard structurally could not see. The resolution critique found the guard STILL wrong after being made tree-derived: matching a dict-literal key excluded every producer that builds its payload by delegation — which is both scaffolds the issue names. The predicate now selects by literal OR delegation call, scans four roots rather than two, refuses on a dynamically assembled key name, and carries a floor so a producer cannot vanish silently.
- Off-goal findings: Recorded, not repaired here: `skills/public/gather/scripts/gather_writer_lib.py` implements the pointer-WRITER rule a second time and answers the target-exists question with a third policy (refuse, against debug's append and quality's prohibition) — a different contract with a different owner. `resolve_artifact_path.payload_for` silently falls through to the current-pointer branch for `--intent record` when the artifact class is not `history`, while the payload still echoes `intent: record`; the new facts mitigate it but the mismatch is unswept. `docs/artifact-policy.md` never enumerated payload keys at all, so it is a granularity gap rather than a drift. The owner's dependency-free guard cannot see a third-party import.
- Lessons carried forward: 1) A guard's POPULATION is a verdict surface too. Three successive versions of the same check were wrong about which producers exist — hand list, then literal-only glob, then literal-or-delegation — and each was found by a different reviewer. When a check claims `every X`, the next question is always `selected how`. 2) The premise check paid for itself twice in this goal: here it refuted the remedy, and its refutation produced a strictly better design (state the FACT, leave the policy to each skill) than the issue's framing would have. 3) Recompute at the end beats lengthening a copy list; the copy list is the defect shape. 4) A gate that hard-blocks three times in one slice is not noise — each block named a real second owner, and two of the six copies would not have been found without it.
- Metrics:

### Slice 5: Slice 3 premise check (#555) — DUPLICATION CONFIRMED, SUGGESTED REMEDY WOULD BREAK A LOAD-BEARING REFUSAL

- Objective: Establish by reading and executing whether `#555`'s premise holds: that GitHub tracker backend resolution is implemented twice, in `handoff` and `issue`, and whether the issue's suggested direction — route `handoff` through the `issue` skill's backend module — is safe to build.
- Why this approach: Third slice, and the third time this goal's Work Phase Map rule fires at design time: `#555` names a remedy (`have handoff's issue backend resolve through the issue skill's backend module rather than reimplementing it`), and a slice shaped around a named remedy must verify that remedy's premise first. The two previous premise checks both changed the build.
- Commits: none yet — this record precedes the build, per this goal's User Acceptance.
- What changed: No source changed. Read: `skills/public/handoff/scripts/chunked_routing_issue_backend.py` (`_resolve_command`, `issue_state`, `_default_runner`, `_load_issue_module`), `skills/public/issue/scripts/issue_runtime.py` (`newest_open_issue`, `_backend_json`), `skills/public/handoff/scripts/chunked_routing_staleness.py`. Executed the issue's own grep for the shared expression.
- Alternatives rejected: Rejected: building the consolidation the issue describes without first reading what each refusal path is FOR. The two functions look parallel and the shared expression is literally identical, so a diff-driven consolidation is the obvious move and is the one that would have broken the consumer.
- Targeted verification: VERDICT: the duplication is CONFIRMED and the suggested remedy is REFUTED as stated. Confirmed: `binary = backend.get("binary") or backend.get("id") or "gh"` appears verbatim at `chunked_routing_issue_backend.py:97` and `issue_runtime.py:148`, both preceded by the same `backend or {"id": "gh", "binary": "gh", "commands": None}` default and the same non-gh-without-template refusal shape. Dependency direction confirmed acyclic as the issue states: `handoff` already imports `issue` modules through `_load_issue_module`, and `issue` imports neither `handoff` nor `achieve`. Refuted: the two refusal paths are NOT interchangeable. `handoff._resolve_command` RETURNS `(None, backend_id)` and its `issue_state` turns that into `None` meaning UNKNOWN, which `chunked_routing_staleness.py:98` consumes; `issue.newest_open_issue` RAISES `RuntimeError`. The handoff docstring states why the non-raising path is load-bearing — reporting a guess here would manufacture the stale verdict that surface exists to refuse. Routing handoff's call through `issue`'s function, which is what the issue's suggested direction says, would convert an UNKNOWN into an exception in a staleness reader.
- Test duplication pressure: n/a — no tests added or expanded in this record.
- Critique: The honest shape of this slice is therefore narrower than the issue's framing and matches slice 2's lesson exactly: consolidate the MECHANICAL part and leave the POLICY to each caller. The mechanical part is the built-in `gh` default template, the binary resolution, the template lookup, and the placeholder substitution — the part the handoff docstring already says `must stay identical across commands`. The differing part is what a missing template for a non-gh backend MEANS: a configuration error to `issue`, an UNKNOWN to `handoff`'s staleness reader. A single owner that returns the resolved argv or a typed `missing-template` signal serves both; a single owner that decides the refusal serves neither. Slice 2 reached the same conclusion from the other direction, where `write_target_facts` had to be a FACT because overwriting is correct for debug and destructive for quality.
- Off-goal findings: Noted for the build, not filed: `#554` part 2 (an automated recount helper) is the third implementation this issue warns about, and it sits in this goal's Operator Decision Queue awaiting a decision. Whatever owner slice 3 creates should be the one a recount consumes, so the decision on `#554` should be taken with slice 3's seam in view rather than after it.
- Lessons carried forward: Three premise checks, three reshapes: `#552`'s suggested direction was sound but incomplete (the writer sweep found four more instances), `#548`'s rested on a property its subject lacked, and `#555`'s would break a consumer that depends on a non-raising refusal. The pattern is now specific enough to state as a rule for the remaining slices: when an issue proposes `have A use B instead of reimplementing it`, the thing to check first is whether A and B REFUSE the same way. Identical happy paths hide different failure contracts, and the failure contract is usually why the copy was made.
- Metrics:

### Slice 6: Slice 3 build (#555) — one owner for tracker backend resolution, and both refusal contracts kept

- Objective: Make backend command resolution have one owner, without collapsing the two callers' opposite answers to the undeclared-op question. Acceptance from the goal: one tracker backend has one owner, and `handoff` consumes `issue`'s rather than reimplementing it.
- Why this approach: Third instance of the goal's class, and the one where the named remedy was most clearly unsafe: the issue's suggested direction would have converted a staleness reader's UNKNOWN into a crashed pickup.
- Commits: `53d4b33d` (build + slice round-1 repairs), `bd47ab96` (slice round-2 repairs), plus the resolution-critique repairs and closeout commit that follow.
- What changed: Owner: `skills/public/issue/scripts/issue_backend.py` gains `op_is_declared` and `try_resolve_op`. Delegating: `skills/public/issue/scripts/issue_runtime.py` (`newest_open_issue`), `skills/public/handoff/scripts/chunked_routing_issue_backend.py` (`_resolve_command`, plus a memoized module loader, per-op required sets, resolution inside `issue_state`'s guard, `LAST_STATE_RESOLUTION_DIAGNOSTIC`, and a payload-number-match guard). Tests: new `tests/test_tracker_backend_single_owner.py` (15), and `tests/test_handoff_chunker_parse.py`'s installed-layout fixture now copies the REAL owner instead of hand-stubbing it, plus a name-aware loader patch in `tests/test_handoff_chunker_issue_source.py`. Records: `charness-artifacts/quality/dup-review.json`. Generated: `plugins/` mirror synced before validators each time.
- Alternatives rejected: Rejected on premise-check evidence: the issue's own suggested direction, `have handoff resolve through the issue skill's backend module`. Rejected: extracting to `skills/shared/scripts/`, which the issue also offers — it moves the surface away from its contractual owner, and `issue` was already both the owner and a leaf. Rejected during round-2 repairs: lengthening the guard's exemption list instead of fixing what the guard matched on.
- Targeted verification: FOUR implementations existed: the owner plus three private copies. TWO copies were removed here; the third (`scripts/issue_source_capture_lib.py`) could not be, because its built-in default is a conditionally assembled GraphQL invocation rather than a template. Mutation: 5/5 on the consolidation, 3/3 on round-1 repairs, 5/5 on round-2 repairs — including `collapse the two contracts`, `let the owner's raise escape issue_state`, `required back to empty`, `drop the payload number-match guard`, `narrow the guard back to RuntimeError`, `drop the memo`, and `stop recording the diagnostic`. Behavioural verdict from a DETACHED worktree at `bd47ab96` through the real `parse_handoff_entries.py --with-issues` CLI, against a real `.agents/issue-adapter.yaml` and a REAL executable stub binary on PATH that logged the argv it received: the log contains exactly `list corca-ai/charness 50` and `view --repo 451`, and the payload reports `issue_entry_count: 1`, `issue_states_checked: true`, `closed_issue_count: 1`. `./scripts/run-quality.sh --read-only` exit 0; `pytest tests/` 7858 passed; closeout aggregate `completed`; dup ratchet clean.
- Test duplication pressure: One new duplicate family, classified `intentional`: the `issue` skill's sibling-import preamble, which is irreducible by construction because it exists to bootstrap loading a sibling. Ten `issue` modules already carried it; this slice added it to one more so that module could stop re-deriving the backend rule — a three-line bootstrap idiom traded for the removal of a duplicated verdict rule that had no placeholder validation. The changed-line mutation gate then blocked on an uncovered delegation at `issue_runtime.py:159`, which was a real gap: `newest_open_issue` was rewritten and no test reached it.
- Critique: Three delegated bounded reviews, and every one found a defect the previous could not. Round 1: an existing test broke because it patched the module loader NAME-BLIND (caught by the read-only quality gate, not by my filtered run); `issue_state` gained four raising paths that escaped to an `except`-less `main()`; `required=frozenset(allowed)` narrowed the adapter contract; the owner was loaded once per cited issue. Round 2 read those repairs and found the worst defect of the slice in one of them: setting required to EMPTY was worse than requiring everything, because `{number}` is IDENTITY-bearing and a `view_state` template omitting it resolves to a listing whose first row is read as the asked-about issue's state — reporting a live citation CLOSED, silently, with `issue_states_checked: true`. Round 2 also found `except RuntimeError` missing `ImportError` (which this slice created) and the owner's `format` crash; a FOURTH copy in a directory my guard did not scan while its name claimed `no other module`; and three of my new tests patching a `runpy.run_path` COPY of globals, so the patches did nothing and the tests passed for the wrong reason. The resolution critique then found the ledger arithmetic wrong the same way `#548`'s was (the owner counted as a consolidation of itself), the guard file's docstring contradicting its own exemption list, a live comment and a live test message both still instructing the refuted empty-required choice, and the guard anchored on the CHEAPEST half of the rule — binary derivation, the line a copy most readily delegates — proven by a live fifth instance it could not see.
- Off-goal findings: Three issues filed. `#557`: the fourth copy in `scripts/issue_source_capture_lib.py`, with the reason it needs its own slice. `#558`: a `view_state` template omitting `{repo}` silently drops it, so a wrong-repo issue with a colliding number can still produce a CLOSED verdict — `(repo, number)` is the identity and `{number}` is half of it; pre-existing, narrowed but not closed. `#559`: `publish_release_helpers.backend_command` is a fifth implementation over the `release_backend` key and has ALREADY drifted from the owner (`if subs and "{" in part` versus `if "{" in part`), so the two disagree on an input both accept. Recorded, not filed: the owner's `part.format` raises raw `KeyError`/`ValueError` for a non-placeholder brace; `issue-backend.md` documents neither `list_open`, `view_state`, nor `{limit}` while the runtime now enforces an allowlist over them, and `search_newest_open` requiring `{repo}` is a new undocumented adapter refusal; `_load_issue_module`'s `repo_root` parameter is dead.
- Lessons carried forward: 1) A guard is only as good as what it matches ON, not just what it scans. Anchoring on binary derivation looked reasonable and was the cheapest half of the rule — the half a copy delegates first — so a live fifth instance passed. The verdict-bearing tell was the rendering step. 2) The first tell I tried for that flagged three CORRECT callers, and a tell that fires on correct code trains people to widen the exemption list, which is worse than having no tell. 3) `runpy.run_path` returns a COPY of module globals: patches into it silently do nothing and tests pass for the wrong reason. Load a real module object when a test needs to patch. 4) Ledger arithmetic has now been the blocking finding in all three closeouts, always the same way — counting the owner among the things consolidated. State the population and the removals as separate numbers.
- Metrics:

### Slice 7: Slice 4 premise check (#537) — REPRODUCED EXACTLY, one claim refined, suggested direction confirmed FEASIBLE

- Objective: Establish by execution whether `#537`'s premise holds: that a correct bundle-preflight refusal surfaces as five broken tests instead of its own blocker message, and whether the issue's second suggested direction — split shape assertions from one repo-readiness assertion — is buildable.
- Why this approach: Fourth slice, fourth time the Work Phase Map's Change Discipline rule fires at design time: `#537` names two candidate directions and explicitly marks one as preferred. Three previous premise checks each changed the build. This one also had a cheap falsifier available — create an unowned path and run the two files — so reading would have been the expensive option.
- Commits: none yet — this record precedes the build, per this goal's User Acceptance.
- What changed: No source changed. Created `charness-artifacts/spec/premise-probe-537.json`, ran the two gate files, then removed it (tree verified clean afterwards). Read: `tests/quality_gates/test_final_bundle_preflight.py`, `tests/quality_gates/test_closeout_bundle.py`, and executed `closeout_bundle_lib.build_plan` directly against the blocked repo.
- Alternatives rejected: Rejected: inferring the failure shape from the issue's transcript. The reproduction cost one file and one pytest run, and it corrected a claim that would otherwise have shaped the fix wrongly.
- Targeted verification: VERDICT: reproduced exactly, with one claim refined and the preferred direction confirmed buildable. (1) EXACT REPRODUCTION: adding one file under an unowned path produced `5 failed, 32 passed`, and the five are precisely the five the issue names. (2) REFINED: the issue says the blocker payload's `code`/`message`/`remediation` reach the reader not at all. Not quite — the unowned path DOES leak, but only inside pytest's truncated `CompletedProcess` repr, with the middle elided as `...`, so it arrives mangled and by accident. The deliberate channel contributes nothing: `assert result.returncode == 0, result.stderr` passes `result.stderr`, which is EMPTY, because the script writes its payload to stdout. So the correct statement is not `the message is lost` but `the message is never deliberately reported, and what leaks is an incidental repr` — which matters, because a fix aimed at making the message appear would conclude it already does. (3) DIRECTION CONFIRMED: executed `build_plan` against the blocked repo and every shape assertion those tests make survives — `mode`, all six `phases` in order, `preflight.status`, `preflight.surface_unmatched_paths`, and `blockers[].code`. So the shape tests genuinely do not need the repo to be clean, and the split the issue prefers is buildable rather than aspirational.
- Test duplication pressure: n/a — no tests added or expanded in this record.
- Critique: The issue's own framing of the fix is sound and its preference is right, which is a first for this goal: three earlier premise checks each refuted the named remedy. Worth stating plainly rather than assuming the pattern continues. What the reproduction adds is the reason the WEAKER direction (print the blocker on failure) is insufficient: the payload already leaks through a repr, so printing more is an improvement in legibility that leaves five tests failing for one cause. The count is the cost the issue actually measured — five failures for one finding, alongside thirty others — so the fix has to reduce the count, not just improve the text. That points at the split, with the printing as a secondary nicety on the ONE test that remains.
- Off-goal findings: Noted, not filed: `assert result.returncode == 0, result.stderr` is a pattern worth checking elsewhere — passing `stderr` as an assertion message is silently empty for any script that reports on stdout, so the custom message reads as diagnostic and carries nothing. Whether that pattern appears in other gate tests is a sweep this slice should run rather than a separate issue, since it is the same defect on the same kind of surface.
- Lessons carried forward: First premise check in this goal where the issue's named remedy SURVIVED. The check still paid: it corrected a factual claim about what the reader sees, and it converted `the preferred direction is probably feasible` into `every shape assertion survives a blocked repo, executed`. A premise check that confirms is not a wasted one — this goal's Boundaries already say 5 for 5 including where the premise held, and this is the fourth confirmation of that rule rather than of the remedy.
- Metrics:

### Slice 8: Slice 4 build (#537) — a bundle refusal that reports itself, measured on three blocker classes

- Objective: Make a correct bundle-preflight refusal report ITSELF rather than appear as five unrelated broken tests, without dropping the readiness coverage the issue explicitly warned against removing.
- Why this approach: Fourth instance of the goal's class, and the one where the harm was measured rather than theoretical: five tests were red for six commits alongside thirty others, so a correct finding about ten unowned artifacts went unread.
- Commits: `15b15c78` (build + slice round-1 repairs), `a4feee83` (slice round-2 repairs), plus the resolution-critique repairs and closeout commit that follow.
- What changed: `tests/quality_gates/support.py` gains `bundle_payload_or_report` (defensive parse that surfaces stderr when there is no payload) and `bundle_blocker_report` (renders `code`, `message`, `remediation`, and each `subject`). `tests/quality_gates/test_final_bundle_preflight.py` and `tests/quality_gates/test_closeout_bundle.py`: two new tests own readiness, one per surface; five shape tests keep their subjects and lose their live-repo verdict couplings; two tests renamed off `is_ready`.
- Alternatives rejected: Rejected, and the issue rejects it too: dropping the `ready` assertion to make a red go away. Rejected as insufficient: the issue's weaker direction, printing the blocker on failure — the premise check found the payload already leaks through a truncated repr, so printing more would leave five tests failing for one cause, and the COUNT is what the issue measured. Rejected during round-2 repairs: asserting `preflight["status"] == "ready"` as the closeout readiness test's structural claim, because it is derived from the same value as the outer assertion.
- Targeted verification: Acceptance measured by reproduction on THREE blocker classes, not one. `unmatched_surface_path`: 5 failures to 2, both named for readiness, each printing code, message, remediation, and the offending path. Drifted plugin mirror: 5 with 3 misnamed, to 3 all correctly named. Broken manifest: 5 with 3 misnamed and two bare `KeyError`s, to 3 with the cause named and no `KeyError` at all. Behavioural verdict from a DETACHED worktree at `a4feee83` using the issue's OWN reproduction recipe: `2 failed, 37 passed`, and the operator reads `final_bundle_preflight is not bundle-ready; status='blocked'` followed by the full blocker. Mutation: 3/3 reporting mutants killed, 2/2 round-1 repair mutants killed by precise mutation (the CLI taking its own error path; the preflight crashing before any payload), with the reason reaching the reader in both. `./scripts/run-quality.sh --read-only` exits 0 with 86 passed, 0 failed, no UNPROVEN; `pytest tests/` 7861 passed; dup ratchet clean; closeout aggregate `completed`.
- Test duplication pressure: No new duplicate families. The shared helpers were put in `support.py` rather than copied into both gate files precisely because two copies of a reporter is the shape this goal keeps repairing.
- Critique: Three delegated reviews, and each found a defect the previous could not — with the deepest one arriving last. Round 1 found a straight coverage DELETION: `closeout_bundle.py` emits an error payload with `status: "blocked"` for any exception, so accepting `{ready, blocked}` let a crashed CLI pass, and the readiness test could not recover it because it calls `build_plan` in process. Round 1 also found that parsing stdout before asserting the exit code made a CRASHING preflight report strictly LESS than before — a bare `JSONDecodeError` with the traceback discarded — and that `assert "Blockers:" in stdout` was vacuous because the ready branch prints `Blockers: none`, which contains it. Round 2 found the acceptance had been measured on ONE blocker class: a drifted mirror still fanned out to five failures with three misnamed, because `mirror_inventory["status"] == "matched"` and `critique_inventory[0]["status"] == "current"` were the same coupling as `ready`. The resolution critique then found a THIRD instance of that coupling — `candidate_snapshot["head_sha"]`, which is `{}` for the manifest-integrity classes and failed with a bare `KeyError` naming nothing, a worse diagnostic than the one the issue was filed about — plus a comment naming a critique-inventory OWNER that does not exist, leaving that verdict unowned, and a false claim in two comments that `planned_commands` is empty when blocked (measured: 56 entries, all carrying `reason_surface_ids`).
- Off-goal findings: Filed `#560`: the ready-path payload and render shape are owned only by tests that require the live worktree to be clean, so while any blocker is live NOTHING exercises the ready path — the mirror image of this issue — and the spec already declared a fixture acceptance check nobody implemented. `#560` also carries the last misnamed failure, in a monkeypatch-heavy test that still reads the real manifest and needs a fixture manifest rather than a one-line change. NOT swept, and the decision is recorded rather than left implicit: `assert result.returncode == 0, result.stderr` occurs 913 times in the tree (910 in tests; the other three are this goal's own artifacts and a transcript). The idiom is CORRECT wherever failures go to stderr — the artifact validators print violations there — and is vacuous only for scripts reporting failure detail on stdout. A bounded round enumerated the 14 stdout-reporting scripts of that shape and found the right stream chosen everywhere it checked. A 913-site sweep is the wolf-crier trade this goal's Non-Goals forbid.
- Lessons carried forward: 1) I fixed the instance the issue reported and measured the fix against that instance. The class was one grep wider than the report — twice: the mirror class, then the manifest class. When an issue names a symptom, enumerate the OTHER inputs that produce the same symptom before claiming the class is closed. 2) My process conclusion from round 2 was WRONG and the resolution critique corrected it. I had concluded that mutation testing is unreliable against live-repo-state assertions, because mutating a file dirtied the worktree and the test failed at an earlier assertion. The failure output already named the confound (`code: needs_sync`); I failed to read WHICH assertion failed — which is the exact failure mode `#537` is about, committed while fixing `#537`. The honest, narrow lesson is that a test whose subject IS the worktree's cleanliness cannot be mutation-tested by editing the worktree, and its discriminating power must be proven by INJECTION instead. Generalising further would license skipping mutation proof on the verdict surfaces this repo requires two rounds for. 3) The round-2 finding that prompted that mistake was itself a false positive: `preflight["status"] == "ready"` was a redundant cross-layer agreement check, not a dead assertion. The replacement (the `verification_lock` command, which comes from the readiness-gated closeout entry) is still better, for a different reason than the one first recorded.
- Metrics:

### Slice 9: Slice 5 premise check (#536, #549, #542) — one REPRODUCED with a corrected trigger, three faces, NO shared remedy; slice split

- Objective: Before building, establish each issue's premise by execution and test the bundling assumption itself: the Slice Plan groups `#536`, `#549`, and `#542` as one slice on the theory that they share a mechanism. The recorded next action required checking that, and splitting rather than building one fix for three symptoms if they do not.
- Why this approach: This goal's own Plan Critique named the risk: if grouped issues do not share evidence, the grouping premise is refuted and the goal should be re-cut rather than pushed through. Four slices in, that rule had only ever been applied ACROSS slices; this is the first slice where it applies WITHIN one.
- Commits: none yet — this record precedes the build, per this goal's User Acceptance.
- What changed: No source changed. Executed: a `.json` and then a `.md` write under `charness-artifacts/quality/` against the two probe test files; `grep -rl quality-failure-logs scripts skills`; read `scripts/evidence_boundary_crosswalk.py` around the `not_singleton` refusal and `tests/quality_gates/test_setup_hook_failure_guidance.py`.
- Alternatives rejected: Rejected: taking the Slice Plan's bundling on trust. Four premise checks in this goal have each changed a build; the fifth changed the SLICE SHAPE instead, which is cheaper to discover now than after one fix had been stretched over three unrelated remedies.
- Targeted verification: `#536` REPRODUCED, with the reported trigger CORRECTED. Adding a `.json` file under `charness-artifacts/quality/` changed nothing — 60 passed. Adding a `.md` file turned exactly 3 tests red across the 2 files the issue names, with `artifacts_scanned drifted from the recorded probe; update D47 and the probe together / assert 132 == 131` and a second, differently-worded recursive-variant failure at `150 == 149`. So the trigger is a markdown artifact, not any write, and the issue's own reproduction would not have reproduced it. The message is also better than the issue implies: it DOES name D47 and the probe as a coupled pair. What it does not say is that an ordinary quality-artifact write is the cause, that a SIBLING probe carries the denominator D47 cites, or how to regenerate either. `#549` CONFIRMED as stated: `grep -rl quality-failure-logs scripts skills` returns exactly ONE file, and the only enforcement tests assert that the reference is mirrored and that `setup` routes to it — nothing reconciles the consumer contract against any executable reader. `#542` CONFIRMED as stated, and the source already agrees with the issue: `evidence_boundary_crosswalk.py` carries a comment saying there is deliberately NO `target_disagreement` refusal and that such a refusal would have to know the carrier SOURCE to be correct.
- Test duplication pressure: n/a — no tests added or expanded in this record.
- Critique: The three issues share a FACE and not a REMEDY, and the remedies are not merely different in size, they are different in kind. `#536` needs a failure message that names its cause and its full regeneration set — a message change plus a coupling between two probes and one prose document. `#549` needs either a mechanism generalized beyond one script or an executable reader for a consumer contract that currently has none; generalizing to every long-running script is exactly the wolf-crier trade this goal's Non-Goals forbid, so its honest core is the missing reader. `#542` needs a refusal that cannot be made correct without threading the carrier SOURCE through the crosswalk — a design decision the source code already documents as deliberately deferred, not a wording fix. Building these as one slice would have produced one commit whose reviewable intent was three unrelated things, which is the condition this goal's Boundaries call a slice that stops being reviewable.
- Off-goal findings: Noted for the build: the two probe failures use DIFFERENT wordings for the same class of drift (`drifted from the recorded probe; update D47 and the probe together` versus `drifted from the recorded recursive run`), and only the first names D47. Whatever fix lands should make both say the same things, or the next reader will learn the remedy from one failure and not the other.
- Lessons carried forward: SLICE SPLIT, recorded as the verdict rather than discovered mid-build: slice 5 takes `#536` alone. `#549` and `#542` are re-homed as their own slices with the reasons above, because a shared face is not a shared fix. Also: the fifth premise check is the first to correct a REPRODUCTION rather than a remedy — the issue's own recipe (`adding one artifact`) does not reproduce, because the probe counts markdown. An issue's reproduction steps are a claim like any other.
- Metrics:

### Slice 10: Slice 5 build (#536) — a drift failure that names its cause, after two versions that were worse than the number

- Objective: Make the probe-drift failure name what caused it and what a re-record must touch, so a correct measurement mismatch stops arriving as three drifted numbers the reader has to reverse-engineer.
- Why this approach: Fifth instance of the goal's class, and the only one of slice 5's three issues whose remedy is a message. The premise check split the slice rather than stretching one fix over three unrelated remedies.
- Commits: `67beced4` (build + slice round-1 repairs), plus the round-2 repairs and closeout commit that follow.
- What changed: New `tests/probe_drift_support.py` (the shared message, its cause lists, its surface/command pairings, and the discrimination paths) and `tests/test_probe_drift_message.py` (10 pins). Wired into the three drift sites in `tests/test_inventory_marker_rule_measurement.py` and `tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py`. Goal artifact: Slice Plan rows 5/5a/5b, the User Acceptance split, and the Status column.
- Alternatives rejected: Rejected by the premise check: building `#536`, `#549`, and `#542` as one slice. Rejected during round-2 repairs: rewording the git-availability cause instead of REMOVING it — it named a field and value no code produces, got a shallow checkout backwards, and cannot move any pinned number on this corpus because every artifact resolves `not-claimed` before git is consulted. A cause that cannot fire is the wolf-crier this goal's Non-Goals forbid. Recorded as a deliberate absence with a pin asserting it stays absent.
- Targeted verification: Acceptance measured by reproduction: with a markdown artifact under the corpus, all three failures print the corpus-versus-rule split, the files to diff, and all seven surfaces with per-surface commands. Mutation: 4/4 on the first pin set, then the round-2 pins killed two INVERSIONS that the first set could not see — swapping the corpus and rule cause lists, and swapping the marker and floor commands in the surface list, both of which left every substring assertion green while making the message actively harmful. `./scripts/check-secrets.sh` reports no leaks; `./scripts/run-quality.sh --read-only` exits 0 with 86 passed, 0 failed; `pytest tests/` 7866 passed at the round-1 boundary; dup ratchet clean; closeout aggregate `completed`; both reviewer boundaries verified with no unattributed drift.
- Test duplication pressure: No new duplicate families. The message lives in one module both gate files import rather than copied into each, which is the shape this goal keeps repairing.
- Critique: Two bounded rounds, and BOTH found the message worse than the number it replaced — the same failure twice, from the same root cause: I asserted where a fact lived instead of checking. Round 1: my instruction said `copy each payload into the probe file`, but `--json` emits only the payload while a probe is `_provenance` PLUS that payload, and the recursive payload nests under `_provenance.recursive_variant`. Following it deleted `_provenance` and produced a bare `KeyError` on the next run. Round 1 also found `the fix is to re-record, not to undo the write` unhedged and wrong for any rule change, and `three surfaces` an undercount. Round 2 read those repairs and found: the discrimination step still pointed at the wrong files, because three of the four thresholds it named live in `scripts/validate_inventory_consumption.py` and not in either measure script — so a reader would diff the measure scripts, see nothing, and re-record a rule regression, which is the exact harm round 1 had just repaired; a SEVENTH surface, the gate module's own comments, which transcribe the corpus label minimum twice; that the floor probe has no `_provenance.current_corpus` field my message claimed it had; that D47 does not name the floor probe or `field_mention_residuals` at all, so my stated reason for the coupling was false even though the coupling is real; and that the `_provenance` bookkeeping fields (`date`, `repo_head_at_run`, `worktree`, the refresh counts) would be left stale by a literal follow, producing a payload wearing a provenance block that names an older run.
- Off-goal findings: Filed `#561`: a THIRD probe pins the INVARIANT (`min_residual >= floor`) rather than equality and has never needed a refresh, which is the difference between making a recurring tax cheaper and removing it — an alternative this slice never considered on the record until a review pointed at it, and a decision D47's owner should take deliberately. `#561` also carries that third site's missing drift message. Recorded, not repaired: the recursive pin's `refused_citation_count` branch cannot fire against the checked-in probe (pre-existing), and the gitleaks `key,` trap is entropy-gated so other sites in the repo pass by luck rather than design.
- Lessons carried forward: 1) The same mistake twice, and it is worth naming precisely: I stated WHERE something lived — a payload's shape, a threshold's module, a document's citation — without opening the file. Every one of those was wrong, and each wrong one made an instruction that would have caused the harm it was written to prevent. For any message that tells a reader where to look, open each location first. 2) A substring pin over a message cannot see an INVERSION. Swapping two lists or two command pairings left ten assertions green while turning the message harmful; pinning the PAIRING and the ORDERING is what catches it. 3) The repo's own commit-msg gate blocked two commits because prose containing `a fix: #536` parses as a GitHub close keyword — it would have auto-closed the issue on push with no ledger. A gate reading prose for side effects is not over-reach; it caught a real one.
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

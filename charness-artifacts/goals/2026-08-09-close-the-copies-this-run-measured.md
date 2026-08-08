# Achieve Goal: Close the copies this run measured, and the two proof surfaces it deliberately did not

Status: active
Created: 2026-08-09
Activation: `/goal @charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 1 — `#562`, drop the owner-inspection locator content pin.
- Current slice intent: remove the whole-file `sha256` content pin from the
  owner-inspection half of the issue source freeze (0/5 measured true positives),
  keeping locators as provenance, and leave the source-snapshot half's
  re-derivation and tamper refusal untouched. Verdict-logic surface, so TWO
  delegated review rounds are budgeted from the start.
- Premise check (slice 1, recorded BEFORE the build; smoke-tested against the real
  caller `validate_issue_source_freeze.py validate`, which was GREEN at
  `reviewed_input_identity 9c26b473e05f`):
  - CONFIRMED — the pin refuses on a purely incidental edit. Appending
    `# charness-562 baseline probe` to `scripts/run-quality.sh` produced, quoted:
    `validate_issue_source_freeze: REFUSED (stale_inspection) scripts/run-quality.sh is now a34e2ecc2224, inspected at 61920016ac36`
    (exit 1); reverting restored green. That is the 0/5-true-positive noise shape.
  - PARTLY REFUTED — the issue's "~35 `sha256` references, 22 in
    `tests/test_issue_source_freeze.py` alone" is NOT the locator-pin surface.
    Measured: that test carries 18 `sha256` occurrences, and most are source-half
    (`raw_response_sha256`, `source_snapshot_sha256`, `snapshot_file_sha256`),
    which this slice must not touch. The pin's real surface is 4 code sites
    (`issue_source_freeze_lib.py` `file_sha256`, the `stale_inspection` loop, the
    `sha256` key inside `inspection_identity`, and `validate_issue_source_freeze.py`
    `stamp_inspection`), 1 schema constant, and the checked-in freeze artifacts.
  - CONFIRMED — the schema bump is load-bearing, not cosmetic:
    `inspection_identity()` hashes each locator's `sha256`, so dropping the field
    changes that identity and cascades through `reviewed_input_identity` ->
    `freeze_identity` -> the crosswalk's `source_identity`.
  - NEW, and not in the issue — the inherited half. `file_sha256()` is the ONLY
    code that touches a locator's file at all. Deleting the pin naively also
    deletes the sole existence check, so "I inspected `foo.py`" would become
    unfalsifiable prose again for a path that never existed. The pin is therefore
    REPLACED by a path-existence check, not merely removed.
- Slice 1 status: BUILT and PROVEN. Two delegated rounds run (12 findings; every
  one repaired except the deliberately deferred receipt-schema field), 16
  source-level mutants all killed, three construction proofs green,
  `run_slice_closeout.py --skip-broad-pytest` -> `Closeout verdict: completed`.
  `#562` is not yet CLOSED — that rides the bundle boundary with the delegated
  resolution critique and the adapter readback.
- Next action: slice 2 — `#561`, put the equality-versus-invariant probe decision
  to D47's owner with both costs measured, and give
  `test_measure_evidence_residual.py` the drift message the issue says needs no
  decision.
- Routing: `charness:achieve` owns the goal lifecycle; `charness:issue` owns the
  `#562`/`#561`/`#560` resolution and closeout shape at the bundle boundary;
  bounded `charness:bounded-reviewer` subagents own every fresh-eye round.
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

Predecessor: `charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md`. It is the FIRST goal in this family to finish its plan — five slices, five reached, five issues closed and verified — and its measurements, not its leftovers, shape this one.

**What it measured, and why that changes how these are built.**

1. **Eighteen blockers across ten delegated rounds, and NOT ONE was in a first diagnosis.** Every premise check was right about the defect; every blocker was in a REPAIR. That is a different fact from "round 2 is useful" — it says the cost of a verdict-logic slice is roughly double what a one-round plan budgets, so two rounds are planned as a COST here rather than remembered as a rule.

2. **A repair inherits HALVES.** The sharpest single theme. One repair inherited half a layout (source tree but not installed, so every installed capture would have died), one half an exception contract (a typed refusal swallowed by the caller's broad `except RuntimeError`), and one half an owner (delegating to a consolidated function while passing its `required` set empty, one slice after building that floor). Ask of every repair what it did NOT inherit.

3. **Opening the file is necessary and NOT sufficient.** The predecessor's rule was "open every location an instruction names". This run opened one, printed the evidence, and then wrote the opposite two steps later. Quote the read back into the claim.

4. **A test that re-implements its subject is another copy of the rule.** Shipped inside the slice about copies of rules: it rebuilt a loader's candidate list and asserted on its own copy, so it would have passed with the loader deleted. And a pin must read the SOURCE — a mutant survived a pin that read the generated mirror, because the mirror lags until the next sync.

5. **A premise check verifies the claim it is pointed at, and nothing else.** It correctly refuted two issues' stated blockers and was silent about the one that actually held — a binary-position difference found only by executing the replacement. Smoke-test a consolidation before believing any analysis of it.

**The remaining work**, and it is deliberately two proof surfaces plus a structural tail:

- `#562`: the owner-inspection locator pin, with an observed 0/5 true-positive rate. **The DIRECTION is already decided and is not this goal's to re-open: option 1 — drop the locator pin, keep the source snapshot.** `#562`'s body records that as the operator's stated preference at filing time, and the predecessor briefly re-queued it as an open question, which was a decision being asked twice. What was missing was never the direction; it was the budget. A proof-surface DELETION touching ~35 `sha256` references plus a schema bump gets two rounds planned from the start. The premise check still runs — on whether the deletion's blast radius is what the issue measured — not on whether to delete.
- `#561`: two probes pin EQUALITY against a corpus ordinary work mutates, while a third pins the invariant and has never needed a refresh. The decision between the two styles belongs to D47's owner and should be taken deliberately.
- `#560`: the ready-path payload is owned only by tests requiring a clean worktree, so while any blocker is live NOTHING exercises it.
- The structural tail this run measured but did not spend: `issue_verify_closeout.py` at 351/360 with the next addition owing a split, and the renderer-versus-reference spelling split in `setup` (the renderer is gated against baking a model id into the contract while a reference instructs an agent to write exactly that).

**One inherited obligation that is not a slice.** The backlog stands at 28 open. The prompt-surface cluster (`#519`-`#532`) remains a measurement question and is still not this family's.

## Non-Goals

- **Do not build `#562` in one round.** Two goals refused it on budget grounds and
  both were right; claiming it here means paying the budget, not shrinking the
  work. Its build gets two delegated rounds from the start, and the round-2 slot
  is planned rather than earned.
- **Do not touch the freeze's SOURCE-SNAPSHOT half.** That half defends a
  genuinely external mutable dependency (issue bodies) and is sound. Only the
  owner-inspection locator pin is in question, and `#514`/`#515`/`#518` own the
  receipt it lives in.
- **Do not decide `#561` from the measurement alone.** Equality-versus-invariant
  is D47's owner's call; this goal's job is to put the choice in front of that
  owner with both costs measured, not to take it.
- Do not take the prompt-surface cluster (`#519`-`#532`). Still a measurement
  question, and still not this family's.
- Do not re-home the six issues the predecessor returned to the backlog
  unclaimed. They were released deliberately; re-adopting them without a premise
  check is how a plan grows past what it can reach.
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

- `#562`: the owner-inspection locator pin is REMOVED and the freeze's
  source-snapshot half still re-derives from raw backend responses. Proven by
  CONSTRUCTION — an edit that used to produce `stale_inspection` no longer does,
  and a tampered snapshot is still refused, so the half that defends an external
  mutable dependency is demonstrably intact rather than assumed to be.
- `#561` is put to its owner as a decision with both costs measured, or is closed
  with the measurement that makes the choice obvious. It is not silently adopted.
- `#560`: something exercises the ready path that does not require a clean
  worktree, so the payload stops being unowned whenever a blocker is live.
- Every slice that changes verdict logic gets TWO delegated review rounds, and the
  second round's findings are recorded whether or not they produced repairs.
- Each slice records its premise-check verdict BEFORE the build, and any slice
  that CONSOLIDATES or DELEGATES is smoke-tested against a real caller before the
  premise check's conclusion is believed.
- Verification cadence follows `## Active Operating Frame`. This section names no
  command and no boundary frequency on purpose.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin
  sync BEFORE validators.
- `check_dup_ratchet.py --summary` and `check_python_lengths.py --headroom` EARLY
  in each slice, not at the commit boundary. The predecessor hit three
  commit-boundary blocks and each forced a full aggregate re-run; every one was
  right and named a real second owner or a real module boundary.
- After ANY commit-gate rejection, run the aggregate (`run_slice_closeout.py`)
  rather than fixing one rejection at a time.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- **TWO delegated review rounds on any slice that changes verdict logic, budgeted
  as a plan-level COST.** The predecessor's measurement: eighteen blockers across
  ten rounds, and not one was in a first diagnosis. Round 2 reads the REPAIRS.
- **Ask of every repair what it did NOT inherit.** Half a layout, half an
  exception contract, half an owner — three of the predecessor's round-2 blockers
  were exactly that shape.
- **Mutate every REPAIR, not only the original code**, and pin the SOURCE rather
  than a generated mirror; a mutant survived a mirror-reading pin because the
  mirror lags until the next sync.
- **Smoke-test a consolidation before believing any analysis of it.** A premise
  check verifies the claim it is pointed at and nothing else.
- **Verify the reviewer boundary the moment a reviewer returns, BEFORE repairing.**
- For any claim about where a fact lives, quote the read back into the claim.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer AND
  a different channel than the push exit code.
- An issue's `CLOSED` state is a non-claim until `verify-closeout --expect-state
  CLOSED` reads it back through the adapter.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

Three slices, and the budget is deliberately front-loaded onto the largest one.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `#562`: DROP the owner-inspection locator pin, keep the source snapshot | Direction already decided by the operator at filing; two goals refused it on BUDGET, and the budget is planned here rather than borrowed from a tail slice | The pin removed with the source-snapshot half intact and re-derivable; a construction showing the old refusal no longer fires and the snapshot's own refusal still does; TWO delegated rounds recorded | planned |
| 2 | `#561`: equality-versus-invariant probe pins | The decision is D47's owner's, and it should be taken with both costs measured rather than by whoever next hits the red | The choice put to its owner with the measurement, or closed with the measurement that settles it | planned |
| 3 | `#560` plus bundle proof and closeout | Cheapest, and composition can drop what each slice proved alone | The ready path exercised without requiring a clean worktree; verification lock recorded; broad proof ONCE | planned |

NOT claimed, and named so the next session does not re-derive the decision:
`#563` (needs a decision on 3 non-English titles first), the prompt-surface
cluster, and the six issues the predecessor returned to the backlog unclaimed
when it closed at five of eleven rows.

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: **28 open issues** on 2026-08-08 via
  `gh issue list --repo corca-ai/charness --state open --limit 100 --json number`,
  down from 33 because the predecessor closed five. Rerun the command before
  reshaping scope; the reconciliation is a command, not an adjective.
- Claims: `#562` (the owner-inspection locator pin, 0/5 measured true positives —
  a proof-surface DELETION touching ~35 `sha256` references plus a schema bump,
  refused by two goals in a row on budget grounds and claimed here WITH the budget),
  `#561` (equality-versus-invariant probe pins, a decision D47's owner should take
  deliberately), and `#560` (the ready path is owned only by tests requiring a clean
  worktree, so while any blocker is live nothing exercises it). Three.
- Not claimed: `#563` (`check-title-slug-drift` reports clean over a scope excluding
  `charness-artifacts/goals`; widening it needs a decision on 3 non-English titles
  first or it lands red on day one). The prompt-surface cluster `#519`, `#520`,
  `#521`, `#523`, `#524`, `#525`, `#527`, `#531`, `#532` — still a measurement
  question and still not this family's. `#514`/`#515`/`#518` — consumer ownership,
  and the source-freeze receipt this goal's `#562` slice touches is theirs, so
  changing it needs their owner in the loop. `#539`, `#545` — provider/publication
  safety. `#530`, `#535`, `#554` — operator decisions carried forward. `#534` —
  BUILT green, then REFUTED and REVERTED by an earlier goal; re-scope from the
  refutation, never from the title. `#528`, `#542`, `#546`, `#547`, `#549`, `#550` —
  returned to the backlog UNCLAIMED when the `one-rule-one-owner` goal closed at
  five of eleven rows rather than carrying them into a plan nobody would reach.

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

### `#547`'s subject was deleted by slice 1, and this goal is not allowed to close it

- Decision: close `#547` as resolved-by-deletion, or re-scope it.
- Owner: operator.
- Why deferred: `#547` is "refreeze re-stamps every locator digest silently, so a
  one-file re-bind can launder unreviewed drift in the other 18". Slice 1 deleted
  the locator digests, so there is nothing left to re-stamp silently and the
  issue's subject no longer exists. But `#547` is one of the SIX issues the
  predecessor returned to the backlog unclaimed, and re-homing those without a
  premise check is a stated Non-Goal of this goal. Closing it would be adopting
  work this plan declined to claim, so the fact is recorded instead of acted on.
  Round 2 surfaced it; I confirmed the OPEN state through the adapter
  (`gh issue view 547` -> `OPEN`).
- Unblock action: confirm that `#562`'s deletion discharges `#547`, and either
  close it citing `#562` or say what remains in scope.
- Revisit trigger: the next goal that claims any of the six unclaimed issues, or
  any operator pass over the backlog recount.

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

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED. Slice 1 DELETES or re-shapes a proof
  surface — the owner-inspection half of the `#514`/`#515`/`#518` freeze receipt —
  which is a consequential change to something another issue family owns. It is
  claimed anyway because the measurement is complete and filed (6 of 20 locators
  changed in one day, five re-stamps, an observed 0/5 true-positive rate, and
  `refreeze` is one mechanical command that until the predecessor run recorded no
  basis), and because leaving it unclaimed a third time is itself a decision
  nobody is taking. The source-snapshot half is explicitly out of scope, and the
  slice's acceptance admits EITHER outcome — removal, or a required basis — so the
  goal does not presuppose the answer.
- Discuss before activation: RESOLVED. Closing the claimed issues rides the repo's
  standing close-on-floor approval, and the predecessor closed five that way with
  a delegated resolution critique and an adapter readback each time. Broad proof
  runs ONCE at the bundle boundary per `## Active Operating Frame`. Every
  proof-level non-claim is named in `## Agent Verification Plan`, and no push,
  release, tag, or Cautilus run is implied by activation; each stays per-request.

## Slice Log

### Slice 1: Slice 1 — `#562`: retire the owner-inspection locator content pin

- Objective: Delete the whole-file `sha256` content pin from the owner-inspection half of the issue source freeze, keeping locators as provenance and leaving the source-snapshot half's re-derivation and tamper refusal untouched. Direction was already the operator's stated preference at filing; what two prior goals refused was the budget, so two delegated review rounds were planned as a COST rather than earned.
- Why this approach: The pin used a whole-file content hash to stand for "the thing I relied on" — maximally sensitive, minimally specific. Measured over the `#514`/`#515`/`#518` freeze: 6 of 20 locators changed in roughly one day, 5 re-stamps, 0 of 5 refusals a true positive. Every refusal was incidental (a flag, a message string, a diagnostic thread). Worse, the remedy is one mechanical command, so the gate trained the see-`stale_inspection`-run-`refreeze` reflex that would fire on the day a locator's semantics genuinely changed — the wolf-crier shape the north star names. Narrowing the pin was rejected in favour of removal because the direction was already decided.
- Commits:
- What changed: `scripts/issue_source_freeze_lib.py`: `INSPECTION_SCHEMA` v1 -> v2; `file_sha256` replaced by `require_file`; new `verify_locators` as the single owner of every per-locator rule (`retired_locator_pin`, `malformed_locator`, `locator_escape` via `_require_locator_contained`, `missing_file`); new `load_inspection` naming the migration remedy for a v1 artifact; `inspection_identity` drops `sha256` and ADDS `purpose`, `non_claims`, and each locator `note`; module docstring rewritten. `scripts/validate_issue_source_freeze.py`: new `preflight` (read-only, runs before any write, owns the issue-set check, `require_inspection_identity=False` for the refreeze lane); `stamp_inspection` no longer stamps digests and calls the shared rules BEFORE writing; `run_freeze` and `run_refreeze` route through `preflight`; `refreeze` docstring corrected. Artifact `...-owner-inspection.json` migrated to v2 with all 20 locator digests dropped, `purpose` and two `non_claims` rewritten, 4 locator notes marked `HISTORICAL (pre-#562, no longer enforced)`, and the re-stamp figures reconciled. Freeze receipt and crosswalk re-stamped. NEW `tests/test_issue_source_owner_inspection.py` (13 tests) registered in `.agents/surfaces.json`. `docs/handoff.md` drops `#562` from the queued-decision list.
- Alternatives rejected: Narrowing the pin to a symbol or contract line (`#562` option 2) and downgrading to an advisory (option 3) were both rejected: the operator's direction was option 1, and re-opening it would have been the decision asked a third time. Ignoring a leftover `sha256` rather than refusing it was rejected — a dead field reads exactly like an enforced pin to a human skimming the artifact. Leaving the artifact prose unbound was rejected after round 2: prose is edited deliberately and rarely, so binding it costs nothing the file pin cost.
- Targeted verification: Premise check recorded BEFORE the build and smoke-tested against the real caller. CONSTRUCTION, all three re-proven against the final code: an incidental comment appended to an inspected file is now ACCEPTED (previously `REFUSED (stale_inspection) scripts/run-quality.sh is now a34e2ecc2224, inspected at 61920016ac36`); a tampered snapshot body is still `REFUSED (snapshot_not_rederivable)`; a deleted locator is still `REFUSED (missing_file)`. `source_snapshot_sha256` stayed `9eb2d417e03a` across every re-stamp, so the source half demonstrably did not move. The refreeze partial-write defect was proven by construction before repair — a refusing `refreeze --require-issues 514 515` mutated all three checked-in artifacts including the closeout-authorization crosswalk. 16 mutants run against SOURCE files (never the `plugins/` mirror); all 16 killed after repair. `run_slice_closeout.py --skip-broad-pytest` -> `Closeout verdict: completed`. 61 tests green in the two freeze modules.
- Test duplication pressure: `check_dup_ratchet.py --summary` run early and at the gate: `status: clean`, `new_code_family_count: 0`, `hard_block: false`; two advisory membership-REDUCTIONS only. `check_python_lengths.py --headroom` run early, and it drove a real design decision: `tests/test_issue_source_freeze.py` was at 792/800 gated lines, so the new tests went into a NEW module rather than appending — the advisory's own instruction, and the split follows the seam `#562` drew (content-pinned external source in the old file, unpinned locator provenance in the new one). `scripts/issue_source_freeze_lib.py` ends at 373/480.
- Critique: TWO delegated bounded-reviewer rounds, boundary fingerprint verified clean around each BEFORE any repair (`w-20260808T080751Z-45979`, `w-20260808T081659Z-66276`). Round 1 (7 findings) read the deletion: 1 BLOCKER — the artifact's `purpose` and `non_claims` still asserted the pin, in the region no identity covers; 1 HIGH — `stamp_inspection` (writer) held weaker rules than `verify_inspection` (reader) and `refreeze` wrote before refusing; 2 MEDIUM — no migration affordance for a v1 holder given `plugins/` ships this lib, and nothing pinned the v1-refusal DIRECTION; 3 LOW — receipt does not record the inspection generation (deferred), `require_file` lacked the containment its sibling has plus a bare `KeyError` path, and stale narration in `docs/handoff.md`. Round 2 read THE REPAIRS and found 5 more, confirming the plan's premise that blockers live in repairs: 1 HIGH — the partial-write CLASS was not fixed, only round 1's instance (proven by construction); 2 MEDIUM — `malformed_locator` guarded `path` but not `role`, so `inspection_identity` still raised a bare `KeyError` through all three subcommands, and finding 1 was corrected without its recurrence being prevented; 2 LOW — locator notes narrating the retired mechanism in the present tense with the re-stamp figures reading as a contradiction, and the migration remedy firing for a FORWARD version telling its holder to downgrade. Every round-2 finding was repaired. Round 2 also cleared five angles I would otherwise have had to trust: no `verify_locators` bypass, the `load_inspection` migration complete, `_require_locator_contained` correct on symlinks and nonexistent paths, no test passing for the wrong reason in the new module, and the deferred finding defensible for a REASON I had not identified — the inspection schema is already bound TRANSITIVELY because `inspection_identity` hashes `schema`, so a receipt field would be a second copy of a bound fact. Per the two-round cap, round-2 repairs are recorded as accepted-unreviewed. One process defect was mine, not a reviewer's: my first round-2 mutation harness passed an unquoted multi-path variable to pytest, which zsh does not word-split, so pytest received one nonexistent path and every mutant read as `killed`. Re-run correctly, three of nine had SURVIVED — the refreeze preflight deletion (my partial-write test's write was byte-identical and therefore invisible), the preflight's locator rules (shadowed by `stamp_inspection`'s redundant re-check), and the forward-version remedy (nothing asserted the negative). All three are now pinned.
- Off-goal findings: Recorded rather than actioned: (1) `#547` is OPEN and its subject — `refreeze` re-stamping every locator digest silently — no longer exists, since this slice deleted the digests. It is one of the six issues the predecessor returned to the backlog unclaimed, so re-homing it is a stated Non-Goal; it goes to the Operator Decision Queue instead of being silently closed. (2) The freeze receipt does not record which inspection schema generation it bound; DEFERRED with round 2's reason, which is stronger than the finding — the schema is already transitively bound through `inspection_identity`, so adding a field would duplicate a bound fact. (3) `docs/handoff.md:16` still tells a successor to claim `#562`; belongs to the closeout handoff refresh. (4) `tests/test_issue_source_freeze.py` remains at 792/800 with 8 lines of headroom; the next addition there owes the same split this slice took.
- Lessons carried forward: A DELETION is not a smaller change than an addition — it is an inheritance audit. The pin's removal had to re-provide file existence (its sole carrier), and two rounds found the writer holding weaker rules than the reader, a partial-write class the instance fix did not reach, and a `role` key the `path` guard did not cover. Second: a claim's TEETH and its APPEARANCE must be removed together. The blocker was prose in the one region no identity covered, and correcting it moved no identity at all — which is why the fix was to bind the prose, not just rewrite it. Third, and the sharpest for the next slice: a mutation harness is code, and mine reported nine false kills from one unquoted shell variable. A green mutant sweep must first prove its own baseline reports a real test COUNT, or it is measuring the harness rather than the subject.
- Metrics: No host token/time telemetry exposed to this session; not fabricated. Countable: 2 delegated review rounds, 12 findings (1 BLOCKER, 2 HIGH, 4 MEDIUM, 5 LOW), 16 source-level mutants all killed, 3 construction proofs, 61 tests green in the two freeze modules, 13 tests added, 3 checked-in artifacts re-stamped.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. TODO the repo's governing design standard, and what it says about THIS goal —
   which facets bear on its boundaries, where its teeth belong, and which
   irreversible boundaries it crosses. Read it while SHAPING, not at closeout:
   the standard is what tells you where a wrong answer escapes, and that is a
   Before-phase question. (The retro's `## North Star Alignment` asks the
   backward-looking half; this is the forward-looking one.)

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

## Plan Critique Findings

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

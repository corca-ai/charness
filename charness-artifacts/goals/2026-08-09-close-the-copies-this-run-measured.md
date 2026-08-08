# Achieve Goal: Close the copies this run measured, and the two proof surfaces it deliberately did not

Status: complete
Created: 2026-08-09
Activation: `/goal @charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: CLOSEOUT. All three slices reached; `#562` closed and verified.
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
- Slice 1 status: BUILT and PROVEN. Two delegated rounds run (12 findings; all
  repaired except TWO — the deliberately deferred receipt-schema field, and the
  `docs/handoff.md` staleness, recorded as off-goal and discharged at this closeout
  rather than in the slice), 16
  source-level mutants all killed, three construction proofs green,
  `run_slice_closeout.py --skip-broad-pytest` -> `Closeout verdict: completed`.
  `#562` is now CLOSED and read back through the adapter (see `Issue closeout:`).
- Slice 2 status: DONE. `#561`'s decision is measured and queued for D47's owner
  (the tax is paid entirely for a corpus COUNTER; every toll figure the deferral
  turns on is stable), and the third site's drift message is built and proven by
  construction. One delegated round, 9 findings, 7 repaired and 2 accepted with
  reasons. `#561` stays OPEN by design — it is a decision, not a defect.
- Slice 3 status: DONE. `#560`'s ready path is owned by a fixture that is ready by
  CONSTRUCTION, proven with the live repo blocked (`2 failed, 40 passed`, where it
  was `2 failed, 37 passed` with zero ready-path coverage), and the monkeypatch
  test no longer reads the live manifest. One delegated round; both of its blocking
  findings invalidated claims already written down as proven.
- Bundle boundary: DONE, and it earned its cost. Broad proof over `475c532f..HEAD`
  first returned `1 failed, 7913 passed` — one failure invisible from every slice
  gate: `test_issue_critique_observer` refused this run's OWN new resolution-critique
  artifact as `absent`, because it carried no `## Fresh-Eye Satisfaction` record.
  Repaired in `ac7b9ab2` by adding that section plus `## Reviewer Tier Evidence` and
  `## Boundary Ownership`. Final run under `--verification-lock`:
  `Closeout verdict: completed`, broad pytest PASS in 60.7s, with that run's plan
  recording `mode: verification-lock`.
- Next action: none — this goal is at its terminal flip. Successor:
  `charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md`.
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
| 1 | `#562`: DROP the owner-inspection locator pin, keep the source snapshot | Direction already decided by the operator at filing; two goals refused it on BUDGET, and the budget is planned here rather than borrowed from a tail slice | The pin removed with the source-snapshot half intact and re-derivable; a construction showing the old refusal no longer fires and the snapshot's own refusal still does; TWO delegated rounds recorded | done — `e6a4d67c`; pin retired, source half proven intact, TWO rounds recorded (12 findings) |
| 2 | `#561`: equality-versus-invariant probe pins | The decision is D47's owner's, and it should be taken with both costs measured rather than by whoever next hits the red | The choice put to its owner with the measurement, or closed with the measurement that settles it | done — `841d1ceb`; put to D47's owner with both costs measured, and the third site's drift message built |
| 3 | `#560` plus bundle proof and closeout | Cheapest, and composition can drop what each slice proved alone | The ready path exercised without requiring a clean worktree; verification lock recorded; broad proof ONCE | done — `2a545fe9` (build) and `ac7b9ab2` (closeout + bundle repair); ready path owned by construction, verification lock recorded, broad proof run ONCE |

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

Two items, both genuinely operator-only, neither blocking local progress.

### `#561`: equality-versus-invariant probe pins — D47's owner's call, both costs measured

- Decision: for each pinned field in the two inventory probes, keep the EQUALITY pin
  or replace it with an INVARIANT. This goal measured both costs and deliberately did
  not take the decision (`## Non-Goals`).
- Owner: D47's owner (operator).
- **Cost of the equality pin, measured.** Adding ONE ordinary markdown artifact to
  `charness-artifacts/quality/` reds 3 assertions across 2 files —
  `test_inventory_marker_rule_measurement.py::test_the_recorded_probe_still_matches_todays_tree`,
  `::test_the_recursive_variant_recorded_in_the_probe_is_reproducible`, and
  `test_a_declaration_is_not_its_own_corroboration.py::test_the_recorded_probe_still_matches_todays_tree`.
  Remediation spans the 9 surfaces `UPDATE_SURFACES` enumerates. The probe records 3
  refreshes already (2026-08-01, 2026-08-06, 2026-08-07). The third site, which pins an
  INVARIANT, stayed GREEN under the identical write and has never needed a refresh.
- **What actually moved, which is the decisive fact and was not in the issue.** Diffing
  both payloads across that same write, exactly one thing changed: the corpus COUNTER.
  `artifacts_scanned` 131 -> 132, `artifacts` 131 -> 132, `rows` 131 -> 132 entries, and
  `exemption_counts.not-claimed` 131 -> 132. Everything D47's decision actually rests on
  was STABLE — `citations_refused_by_the_marker_rule`,
  `artifacts_refused_by_the_marker_rule`, `field_mentions_carrying_a_value_marker`,
  `field_mentions_without_a_marker`, `field_mentions_presence_only`, `marker_kinds`,
  `floor`, `field_mention_residuals`, `label_value_residuals`.
  **So the entire re-record tax is being paid for a corpus-size counter, and the toll
  figures the deferral turns on do not move on their own.** That reframes the choice from
  "equality or invariant" to "which FIELDS get which pin", and a split is available that
  costs nothing D47 relies on: equality on the toll set, invariant or nothing on the
  counters.
- **Cost of dropping equality.** D47 quotes figures in prose, and the pin is the only
  forcing function that makes a corpus move reach that prose. The marker probe records
  that a transcribed number went stale for two refresh cycles even WITH the pin, so the
  forcing function is real but demonstrably not sufficient on its own.
- **Non-claim, and it bounds the recommendation.** Measured with ONE probe artifact that
  does not cite a declared inventory. An artifact that DOES cite one would additionally
  move the mention counts and possibly the refused set, so "the toll figures are stable"
  is a claim about incidental quality writes, which is the population that caused the 3
  refreshes — not a claim that they can never move.
- Unblock action: choose per-field. If the split above is wanted, name which fields keep
  equality; that is a follow-up slice, not a reinterpretation of this measurement.
- Revisit trigger: the next refresh of either probe, or any D47 movement.
- Already done, needing no decision (`#561` says so itself):
  `test_measure_evidence_residual.py` now has a drift message.

### `#560` is closable and its closeout floor was not run

- Decision: run `#560`'s closeout floor and close it, or state what remains open.
- Owner: operator.
- Why deferred: `#560`'s acceptance is MET and proven — the ready path is owned by a
  fixture that is ready by construction, demonstrated with the live repo blocked
  (`2 failed, 40 passed` where it was `2 failed, 37 passed` with zero ready-path
  coverage), three ready-path mutants killed by fixture tests in that window, and the
  monkeypatch test's live-manifest dependency removed. What was NOT done is the
  closeout FLOOR: a delegated resolution critique for `#560` specifically, a carrier
  with its classification ledger, and an adapter readback. This run spent its
  closeout budget on `#562` and cannot claim a floor it did not execute. The
  disposition review correctly refused the earlier wording ("not claimed for closure
  by this goal's plan") as a fact about the plan rather than a reason.
- Unblock action: run the `issue` closeout floor for `#560` (delegated resolution
  critique -> validate-closeout-draft -> close-with-comment -> verify-closeout), or
  record what is still open in it.
- Revisit trigger: the successor goal's activation, which inherits this queue.

### `#547`'s subject was deleted by slice 1, and this goal is not allowed to close it

- Decision: close `#547` as resolved-by-deletion, or re-scope it.
- Owner: operator.
- Why deferred: `#547` is "refreeze re-stamps every locator digest silently, so a
  one-file re-bind can launder unreviewed drift in the other 18". Slice 1 deleted the
  locator digests, so the issue's LITERAL subject no longer parses — but the delegated
  resolution critique found that its GENERALIZED form survived and this change WIDENED
  it, and the disposition review then caught this queue item describing only the
  deletion half. Both halves, stated: `stamp_inspection` still returns
  `{ok, stamped, inspection_identity}` and reports nothing about what MOVED, while
  `rebind_crosswalk` beside it does return `changed_fields`; and because
  `inspection_identity` now covers the locator SET and the artifact's PROSE, `refreeze`
  silently re-stamps strictly MORE than it did when `#547` was filed — including the
  `purpose` field that was slice 1's round-1 blocker. A deleted locator plus a
  rewritten `purpose` followed by `refreeze` prints `ok: true` and a new identity, the
  crosswalk rebinds, and `validate` is green. But `#547` is one of the SIX issues the
  predecessor returned to the backlog unclaimed, and re-homing those without a
  premise check is a stated Non-Goal of this goal. Closing it would be adopting
  work this plan declined to claim, so the fact is recorded instead of acted on.
  Round 2 surfaced it; I confirmed the OPEN state through the adapter
  (`gh issue view 547` -> `OPEN`).
- Unblock action: RE-SCOPE `#547` rather than close it. Its literal subject is
  discharged and its generalized form is live and WIDER than when filed, so the likely
  correct outcome is a re-scope to "`refreeze` reports no diff of what it re-stamped"
  — NOT a close citing `#562`. An earlier draft of this item invited that close; it was
  wrong, and the record now says which reading is which.
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

- Routing: impl — owns every slice's build: the freeze-lib deletion and its replacement rules, the residual drift message, and the bundle-ready fixture; selected from installed skill metadata because all three slices moved code, tests, and checked-in artifacts rather than only prose.
- Routing: quality — owns the verification posture: the early `check_dup_ratchet`/`check_python_lengths` reads that drove slice 1's module split, the changed-surface verify sets, and the broad-versus-slice gate cadence including the verification lock at the bundle boundary.
- Routing: charness:achieve — owns the goal lifecycle, the slice cadence, and the closeout floors for a three-slice run against three filed issues; selected from installed skill metadata at activation and recorded in the frame at slice 1.
- Routing: charness:issue — owns #562's resolution shape and closeout carrier: validate-closeout-draft, the delegated resolution critique before the close call, close-with-comment, and verify-closeout through the adapter.
- Routing: charness:retro — owns the after-action review, the sibling scan, and the recent-lessons refresh at closeout.
- Routing: charness:bounded-reviewer (typed agent) — owns every fresh-eye round: two on slice 1's verdict logic, one on slice 2, one on slice 3, and the resolution critique.
- Gather: n/a — no external URL, Slack, Notion, Docs, or Drive source became working context; every input was a checked-in artifact or a GitHub issue read through the repo's own adapter, which is not a gather source.
- Release: n/a — this run touched no version, no install manifest, and no release surface; the plugins/ mirror sync is a generated-export step the packaging validator owns, not a release.
- Issue closeout: #562 closed. Carrier: direct-commit (ac7b9ab2). DELEGATED resolution critique BEFORE the close call: charness-artifacts/critique/2026-08-09-issue-562-resolution-critique.md — nine findings, forcing four ledger rewordings (Siblings in both directions, Prevention narrowed, Behavior naming both directions, Debug Artifact to cite-only) plus three repairs riding the close commit. It is the FIFTH delegated round of this run and the ONLY one with no boundary fingerprint of its own — a gap stated rather than papered over. Proof: validate-closeout-draft -> draft_verified (re-run with the repo's OWN copy after the installed copy refused on helper-provenance drift), close-with-comment -> CLOSED, verify-closeout --classification bug --carrier direct-commit --commit-ref ac7b9ab2 --expect-state CLOSED -> verified. #561 and #560 are NOT close-intended, for two DIFFERENT reasons, because \"not claimed for closure by the plan\" is a fact about wording rather than a reason. #561: a DECISION for D47's owner, forbidden to this goal by a stated Non-Goal, correctly left open with both costs measured. #560: its acceptance is met and its build is proven, so it is CLOSABLE — what was NOT done is its closeout floor (a delegated resolution critique for #560, a carrier, an adapter readback), which this run did not run and therefore cannot claim. That floor IS the residual scope and it is recorded in the Operator Decision Queue. #564 and #565 were FILED by this run under the standing approval.
- Successor goal: charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md

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
- Commits: `e6a4d67c` — Retire the owner-inspection locator pin, and the halves its deletion nearly kept
- What changed: `scripts/issue_source_freeze_lib.py`: `INSPECTION_SCHEMA` v1 -> v2; `file_sha256` replaced by `require_file`; new `verify_locators` as the single owner of every per-locator rule (`retired_locator_pin`, `malformed_locator`, `locator_escape` via `_require_locator_contained`, `missing_file`); new `load_inspection` naming the migration remedy for a v1 artifact; `inspection_identity` drops `sha256` and ADDS `purpose`, `non_claims`, and each locator `note`; module docstring rewritten. `scripts/validate_issue_source_freeze.py`: new `preflight` (read-only, runs before any write, owns the issue-set check, `require_inspection_identity=False` for the refreeze lane); `stamp_inspection` no longer stamps digests and calls the shared rules BEFORE writing; `run_freeze` and `run_refreeze` route through `preflight`; `refreeze` docstring corrected. Artifact `...-owner-inspection.json` migrated to v2 with all 20 locator digests dropped, `purpose` and two `non_claims` rewritten, 4 locator notes marked `HISTORICAL (pre-#562, no longer enforced)`, and the re-stamp figures reconciled. Freeze receipt and crosswalk re-stamped. NEW `tests/test_issue_source_owner_inspection.py` (13 tests) registered in `.agents/surfaces.json`. `docs/handoff.md` drops `#562` from the queued-decision list.
- Alternatives rejected: Narrowing the pin to a symbol or contract line (`#562` option 2) and downgrading to an advisory (option 3) were both rejected: the operator's direction was option 1, and re-opening it would have been the decision asked a third time. Ignoring a leftover `sha256` rather than refusing it was rejected — a dead field reads exactly like an enforced pin to a human skimming the artifact. Leaving the artifact prose unbound was rejected after round 2: prose is edited deliberately and rarely, so binding it costs nothing the file pin cost.
- Targeted verification: Premise check recorded BEFORE the build and smoke-tested against the real caller. CONSTRUCTION, all three re-proven against the final code: an incidental comment appended to an inspected file is now ACCEPTED (previously `REFUSED (stale_inspection) scripts/run-quality.sh is now a34e2ecc2224, inspected at 61920016ac36`); a tampered snapshot body is still `REFUSED (snapshot_not_rederivable)`; a deleted locator is still `REFUSED (missing_file)`. `source_snapshot_sha256` stayed `9eb2d417e03a` across every re-stamp, so the source half demonstrably did not move. The refreeze partial-write defect was proven by construction before repair — a refusing `refreeze --require-issues 514 515` mutated all three checked-in artifacts including the closeout-authorization crosswalk. 16 mutants run against SOURCE files (never the `plugins/` mirror); all 16 killed after repair. `run_slice_closeout.py --skip-broad-pytest` -> `Closeout verdict: completed`. 61 tests green in the two freeze modules.
- Test duplication pressure: `check_dup_ratchet.py --summary` run early and at the gate: `status: clean`, `new_code_family_count: 0`, `hard_block: false`; two advisory membership-REDUCTIONS only. `check_python_lengths.py --headroom` run early, and it drove a real design decision: `tests/test_issue_source_freeze.py` was at 792/800 gated lines, so the new tests went into a NEW module rather than appending — the advisory's own instruction, and the split follows the seam `#562` drew (content-pinned external source in the old file, unpinned locator provenance in the new one). `scripts/issue_source_freeze_lib.py` ends at 373/480.
- Critique: TWO delegated bounded-reviewer rounds, boundary fingerprint verified clean around each BEFORE any repair (`w-20260808T080751Z-45979`, `w-20260808T081659Z-66276`). Round 1 (7 findings) read the deletion: 1 BLOCKER — the artifact's `purpose` and `non_claims` still asserted the pin, in the region no identity covers; 1 HIGH — `stamp_inspection` (writer) held weaker rules than `verify_inspection` (reader) and `refreeze` wrote before refusing; 2 MEDIUM — no migration affordance for a v1 holder given `plugins/` ships this lib, and nothing pinned the v1-refusal DIRECTION; 3 LOW — receipt does not record the inspection generation (deferred), `require_file` lacked the containment its sibling has plus a bare `KeyError` path, and stale narration in `docs/handoff.md`. Round 2 read THE REPAIRS and found 5 more, confirming the plan's premise that blockers live in repairs: 1 HIGH — the partial-write CLASS was not fixed, only round 1's instance (proven by construction); 2 MEDIUM — `malformed_locator` guarded `path` but not `role`, so `inspection_identity` still raised a bare `KeyError` through all three subcommands, and finding 1 was corrected without its recurrence being prevented; 2 LOW — locator notes narrating the retired mechanism in the present tense with the re-stamp figures reading as a contradiction, and the migration remedy firing for a FORWARD version telling its holder to downgrade. Every round-2 finding was repaired. Round 2 also cleared five angles I would otherwise have had to trust: no `verify_locators` bypass, the `load_inspection` migration complete, `_require_locator_contained` correct on symlinks and nonexistent paths, no test passing for the wrong reason in the new module, and the deferred finding defensible for a REASON I had not identified — the inspection schema is already bound TRANSITIVELY because `inspection_identity` hashes `schema`, so a receipt field would be a second copy of a bound fact. Per the two-round cap, round-2 repairs are recorded as accepted-unreviewed. One process defect was mine, not a reviewer's: my first round-2 mutation harness passed an unquoted multi-path variable to pytest, which zsh does not word-split, so pytest received one nonexistent path and every mutant read as `killed`. Re-run correctly, three of nine had SURVIVED — the refreeze preflight deletion (my partial-write test's write was byte-identical and therefore invisible), the preflight's locator rules (shadowed by `stamp_inspection`'s redundant re-check), and the forward-version remedy (nothing asserted the negative). All three are now pinned.
- Off-goal findings: Recorded rather than actioned: (1) `#547` is OPEN and its subject — `refreeze` re-stamping every locator digest silently — no longer exists, since this slice deleted the digests. It is one of the six issues the predecessor returned to the backlog unclaimed, so re-homing it is a stated Non-Goal; it goes to the Operator Decision Queue instead of being silently closed. (2) The freeze receipt does not record which inspection schema generation it bound; DEFERRED with round 2's reason, which is stronger than the finding — the schema is already transitively bound through `inspection_identity`, so adding a field would duplicate a bound fact. (3) `docs/handoff.md:16` still tells a successor to claim `#562`; belongs to the closeout handoff refresh. (4) `tests/test_issue_source_freeze.py` remains at 792/800 with 8 lines of headroom; the next addition there owes the same split this slice took.
- Lessons carried forward: A DELETION is not a smaller change than an addition — it is an inheritance audit. The pin's removal had to re-provide file existence (its sole carrier), and two rounds found the writer holding weaker rules than the reader, a partial-write class the instance fix did not reach, and a `role` key the `path` guard did not cover. Second: a claim's TEETH and its APPEARANCE must be removed together. The blocker was prose in the one region no identity covered, and correcting it moved no identity at all — which is why the fix was to bind the prose, not just rewrite it. Third, and the sharpest for the next slice: a mutation harness is code, and mine reported nine false kills from one unquoted shell variable. A green mutant sweep must first prove its own baseline reports a real test COUNT, or it is measuring the harness rather than the subject.
- Metrics: No host token/time telemetry exposed to this session; not fabricated. Countable: 2 delegated review rounds, 12 findings (1 BLOCKER, 2 HIGH, 4 MEDIUM, 5 LOW), 16 source-level mutants all killed, 3 construction proofs, 61 tests green in the two freeze modules, 13 tests added, 3 checked-in artifacts re-stamped.

### Slice 2: Slice 2 — `#561`: measure the pin choice for D47's owner, and close the third site's diagnostic gap

- Objective: Two separable halves. Put the equality-versus-invariant probe-pin choice to D47's owner with BOTH costs measured rather than taking it (a stated Non-Goal), and close the part `#561` itself says needs no decision: `test_measure_evidence_residual.py` reported a bare kind name on failure while its two siblings got `#536`'s rich drift message.
- Why this approach: `#536` made the recurring re-record cheaper and harder to get wrong; it never asked whether the equality pin is the right CLAIM. That question turns on numbers nobody had measured, and the goal's acceptance is explicit that this run measures and does not adopt. The message half is independent, cheaper, and was the concrete defect a reader actually hits.
- Commits: `841d1ceb` — Measure the probe-pin choice for its owner, and close the third site's silence
- What changed: `tests/probe_drift_support.py`: new `residual_floor_message` with its own `RESIDUAL_*` constants and a 5-entry `RESIDUAL_UPDATE_SURFACES`; `probe_drift_message` untouched. `tests/quality_gates/test_measure_evidence_residual.py`: 5 assertions now carry the message, including the exit-code one. `tests/test_probe_drift_message.py`: 6 new pins. The goal artifact's `## Operator Decision Queue` carries the `#561` decision packet.
- Alternatives rejected: Reusing `probe_drift_message` was rejected and the review confirmed it: its `UPDATE_SURFACES` names the marker probe, the floor probe, D47 and the inventory gate, none of which carry a residual figure, and its remedy (re-record) is the OPPOSITE of this site's. Deciding the pin question from the measurement was rejected as a stated Non-Goal — the measurement is put to the owner instead. Posting the measurement as a GitHub comment on `#561` was deferred: commenting is not in the repo's standing-approval list, and the operator reads the goal artifact.
- Targeted verification: MEASURED, not argued. Adding one ordinary markdown artifact to `charness-artifacts/quality/` reds 3 assertions across the 2 equality sites while the invariant site stays GREEN. Diffing both payloads across that write isolates what actually moves: ONLY the corpus counter (`artifacts_scanned`/`artifacts`/`rows`/`exemption_counts.not-claimed`, 131 -> 132). Every toll figure D47 rests on — the refused citations, the refused artifacts, the marker split, the floor, the residuals — stayed stable. CONSTRUCTION for the message half: a one-byte stub artifact placed in the corpus renders the full message, read back three times as it was corrected. 6 mutants on the repairs, all killed. Gate: `Closeout verdict: completed`; 25 tests green in the two message suites, 83 across all four probe suites.
- Test duplication pressure: No new test module needed: `tests/test_probe_drift_message.py` was at 312/800 and `tests/probe_drift_support.py` at 188/800, so both additions landed with wide headroom — the opposite of slice 1's constraint, and checked before writing rather than after. Dup ratchet clean at the gate.
- Critique: ONE delegated bounded round, boundary verified clean before repairing (`w-20260808T084443Z-149124`). Not two: this slice adds a MESSAGE and changes no verdict logic, so the two-round trigger does not fire — but one round was clearly owed, because a drift message is the exact artifact class this repo has twice shipped WORSE than what it replaced. The round earned it, returning 9 findings including 3 of that same class: the message named `kinds[*].count`, a key the residual probe does not have and which I had inherited from the INVENTORY probe's shape — an assertion about a file's contents made without opening it; the re-record list named ONE surface when the figures are transcribed in five, so a reader following it would leave the gate defending its floor with a number no probe reports AND hit an unwarned mirror-drift gate; and 'exits non-zero exactly when the invariant is broken' was false twice over, since the script uses a STRICT comparison (exit 1 when a minimum EQUALS the floor, which the gate itself passes) and also exits 1 on an empty corpus. Also real: one of the five messaged assertions compares the recorded probe to ITSELF, so 'drifted from the recorded measurement' was false for it and both remedy branches sent the reader to inspect a healthy live tree — it now has its own third branch. All repaired. Two findings accepted rather than fixed, with reasons: a bare `KeyError`/`TypeError` path if the measure script's `KINDS` are renamed or a kind empties (pre-existing, not what `#561` filed, and fixing it means restructuring the test rather than messaging it), and one assertion that is unreachable while the script keeps its exit contract (kept deliberately as belt-and-braces, now commented as such).
- Off-goal findings: The `#561` decision itself is now an Operator Decision Queue item, not a finding. Recorded there: the split the measurement suggests — equality on the toll set, invariant or nothing on the corpus counters — is the OWNER's to take, and it is a follow-up slice rather than a reinterpretation of this measurement.
- Lessons carried forward: The measurement reframed the question the issue asked. `#561` posed it as equality-versus-invariant; measuring showed the entire re-record tax is paid for a corpus-size COUNTER while every figure the deferral turns on is naturally stable. The real choice is per-FIELD, which neither the issue nor this goal's plan had seen. Second, and it repeats slice 1 exactly: my repair inherited the shape of the thing it was modelled on. Writing a residual message by analogy to the inventory message imported an inventory KEY NAME and an inventory-sized surface list into a probe that has neither. Analogy is how the first draft got written and also how it got three claims wrong. Third: the first version of this fix put the message on four assertions and left `assert code == 0` bare — and that is the ONLY one a stub artifact reaches, because the script exits 1 first. Construction caught it; reading the diff would not have.
- Metrics: No host token/time telemetry exposed; not fabricated. Countable: 1 delegated round, 9 findings (1 BLOCKER, 2 HIGH, 2 MEDIUM, 4 LOW), 7 repaired and 2 accepted with reasons, 6 mutants all killed, 3 construction reads of the rendered message, 6 pins added, 25 tests green in the two message suites.

### Slice 3: Slice 3 — `#560`: own the bundle ready path in a repo that is ready by construction

- Objective: Build the fixture the preflight contract had DECLARED as an acceptance check with nothing implementing it, so the bundle ready payload and render shape stop being unowned whenever a blocker is live. Keep the two live readiness tests, and point `#560`'s third gap — a monkeypatch test still reading the live manifest — at the fixture.
- Why this approach: After `#537` the ready payload was owned only by tests requiring a clean live worktree, so while any blocker was live NOTHING exercised the ready path — the state where a ready-path regression is most likely to be introduced and least likely to be noticed. Reproduced first, exactly as the issue describes: one probe file under `charness-artifacts/spec/` gives `2 failed, 37 passed`, and both failures ARE the readiness tests.
- Commits: `2a545fe9` — Own the bundle ready path in a repo that is ready by construction. The bundle-boundary repair to `tests/quality_gates/test_issue_critique_observer.py`'s subject (this run's own critique artifact gaining `## Fresh-Eye Satisfaction`) rode `ac7b9ab2`, the closeout carrier, not this commit.
- What changed: NEW `tests/quality_gates/bundle_ready_world.py` — the session fixture `bundle_ready_repo`, `build_bundle_ready_repo`, `_rewrite_shas`, and `_restamp_reviewed_binding`. `tests/conftest.py` registers it. `tests/quality_gates/test_final_bundle_preflight.py` gains 4 tests and retargets `test_final_bundle_private_error_and_render_branches` off the live manifest. `tests/quality_gates/test_closeout_bundle.py` gains the ready plan's `verification_lock` owner.
- Alternatives rejected: Forging a critique binding by hand was rejected — a durable artifact binds a packet by path, SHA-256, and reviewed-input identity, with the packet Markdown a deterministic rendering of its JSON, so hand-writing it would be a second implementation of the binding rule. The fixture copies the real triple and RE-STAMPS it with the real producers. Removing the live readiness tests was rejected: `is THIS repo ready right now` is a real question worth one failing test per surface.
- Targeted verification: CONSTRUCTION, the same probe the issue names: with the live repo blocked the run goes from `2 failed, 37 passed` to `2 failed, 40 passed` — the two live readiness tests still fail correctly and the fixture-owned ready-path tests pass. 3 ready-path mutants (dropping the closeout planned command, forcing never-ready, removing `reason_surface_ids`) were run WITH THE LIVE REPO BLOCKED and each was killed BY A FIXTURE TEST, which is coverage that was previously zero in that window. A separate four-way construction proved the re-stamp's value: spec diverged + not re-stamped -> `unbound_critique`; spec diverged + re-stamped -> `current`. 7 mutants total on this slice, all killed after repair. 44 tests green in the two suites; gate `Closeout verdict: completed`.
- Test duplication pressure: `bundle_ready_world.py` lands at 126/800 and the two suites at 384/800 and 393/800, all checked before writing. Dup ratchet clean at the gate. The fixture is session-scoped and read-only by contract; the review confirmed no test mutates it and the mirror render goes to a temp dir rather than the repo.
- Critique: ONE delegated bounded round, boundary verified clean before repairing (`w-20260808T090259Z-192061`). ONE and not two, and the reason is recorded rather than left silent: this slice adds TEST COVERAGE and a fixture and changes no verdict logic in any gate, validator, or renderer — the preflight and closeout-bundle libs are untouched — so the two-round trigger does not fire. The disposition review pushed back that the single round returned two BLOCKERS including a vacuous test, which is a proof surface that could not fail; that is accepted, and the round-1 repairs are recorded as ACCEPTED-UNREVIEWED under the same cap slice 1 used, rather than claimed as reviewed. It returned 11 findings and TWO were blocking, both of which invalidated claims I had already written down as proven. First: `test_the_fixture_stays_ready_while_this_repo_is_blocked` was VACUOUS. It probed the live repo with `--paths`, and `diagnostic = explicit_paths is not None` short-circuits the status line, so `!= ready` held for any repo in any state including a pristine one — the test could not fail, and its docstring asserted independence it never checked. Second, and worse because it was silent: the fixture's readiness DID depend on live bytes. `critique_inventory` verifies with `check_current=True`, which resolves the repo root by walking to the nearest `.git` and RECOMPUTES the reviewed-input identity there; under `sha256-v2` working-tree mode that digest reduces to the bytes of one file — the preflight contract spec, copied out of the live tree. The next amendment to that spec would have staled the fixture and reddened all three fixture tests beside the two live ones: a five-test fan-out for one cause, and zero ready-path coverage in exactly the window the fixture exists to cover. Both repaired — the vacuous test replaced by one asserting the plan carries the fixture's own base SHA (proven absent from the live repo), and the binding re-stamped with `build_reviewed_input_identity` and `render_markdown`. Also repaired: the module docstring implied the recomputed manifest identities exercise freshness when `verify_current=False` makes them inert, and implied a general independence the fixture does not have (mirror, surfaces, and source tree are copied, so drift there still travels); `_rewrite_shas` skipped 40-hex strings that are list ELEMENTS; `_declared` was a weaker second copy of the subject's markup stripper; and the seed inputs had no named guard. Accepted with reasons: the SHA collapse makes `validate_manifest`'s cross-field equalities vacuous inside the fixture (owned by `test_slice_manifest.py`, now named in the docstring so nobody credits the fixture with it), and `tmp_path_factory` rather than the content-addressed seed cache (one extra session clone against dozens already performed per test elsewhere). The round also cleared the retargeted monkeypatch test line by line — all four blocker codes still produced for their intended reasons — and confirmed no cross-test contamination and no assertion that would pass with its subject deleted.
- Off-goal findings: None new. The review's cost note — this fixture uses `tmp_path_factory` while `seeded_charness_git_repo` uses the content-addressed `seed_cache.get_or_build`, and the new `bundle-ready-*` prefix counts against `check_seed_fixture_budget.py`'s per-seed cap — is recorded here rather than filed, because the measurement that would justify a change (tree size, worker distribution) was not taken.
- Lessons carried forward: THIRD slice in a row where the repair was pinned and its WIRING was not. Slice 1: the stamp path's existence check. Slice 2: the exit-code assertion the failure actually reaches. Here: deleting `_restamp_reviewed_binding(repo)` from the builder survived the entire suite, because the fixture copies the spec byte for byte and the re-stamped digest equals the live one — the effect is invisible while everything agrees. Three instances is a pattern, not a coincidence: when a repair's effect is only visible in a state the suite cannot manufacture, the wiring needs its own pin. Second: a test that cannot fail is worse than no test, and the way this one hid was that its subject was a FLAG rather than a state — `--paths` forces `diagnostic` before any blocker is consulted. Third: 'independent of live state' was too coarse a claim. The fixture is independent of the artifact-path class and coupled to the mirror, surfaces, source tree, and one reviewed spec; saying which is what makes the docstring true.
- Metrics: No host telemetry exposed; not fabricated. Countable: 1 delegated round, 11 findings (2 BLOCKING, 4 further repaired, 5 accepted-with-reason or notes), 7 mutants all killed after repair, 2 multi-case constructions, 5 tests added, 44 green in the two suites.

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

Retro: charness-artifacts/retro/2026-08-08-close-the-copies-this-run-measured-retro.md
Host log probe: skipped: host-log-not-exposed: this session exposes no per-turn token, timing, or tool-call log to the agent, so `probe_host_logs.py` has no stream to read; every count in the retro and the slice log is a countable artifact (findings, mutants, tests, commits) rather than a host metric, and no token or duration figure is claimed anywhere in this goal.
Disposition review: charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured-disposition-review.md

## User Verification Instructions

## Auto-Retro

The retro surfaced three improvements. Each is dispositioned, none is prose-only:

Retro dispositions: issue #564 (recurs: three instances in THIS goal, one per slice, and the predecessor goal measured the adjacent half-repair form; the class is a repair whose only proof calls the repaired function directly) — the workflow improvement ("at least one mutant per repair deletes the CALL SITE rather than the body") is filed rather than applied, because it belongs in the goal TEMPLATE's verification plan and editing that template is a prompt-surface change this goal did not claim.
Retro dispositions: issue #565 (novel: no prior issue or retro names the harness-baseline shape; the adjacent known classes are about gate output, not about a verification harness that cannot fail) — the capability improvement (a repo-owned mutate-and-restore helper that refuses to report a kill unless the unmutated baseline first reported a passing test count) is filed rather than built, for the same scope reason plus the measured cost: three hand-authored harnesses in one run, one of which reported nine false kills.
Retro dispositions: applied: the memory improvement is IN this commit — `charness-artifacts/retro/recent-lessons.md` was refreshed from the durable retro by `persist_retro_artifact.py`, carrying the twice-measured finding that blockers live in repairs rather than in first diagnoses.
Structural follow-up: issue #564 (recurs: three instances in this goal, one per slice, and the predecessor goal measured the adjacent half-repair form; the transferable pattern is a repair whose only proof calls the repaired function directly)

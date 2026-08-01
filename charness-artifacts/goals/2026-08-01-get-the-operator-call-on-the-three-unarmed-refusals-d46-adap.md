# Achieve Goal: Get the operator call on the three unarmed refusals D46 (adapter-YAML), D47 (inventory value markers), D48 (release surfaces), then arm or record what the call decides

Status: complete
Created: 2026-08-01
Activation: `/goal @charness-artifacts/goals/2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: COMPLETE — all four slices ran, five bounded review rounds,
  three deferred decisions answered and recorded.
- Current slice: none. Slices 2 and 3 were reshaped by the operator's Q1/Q2
  answers after the plan critique broke the premise of the repairs both
  deferred-decision entries had named.
- Next action: none for this goal. The baton is in `docs/handoff.md`.
- Verification cadence: dup-ratchet at the FIRST edit to a gated file (not at the
  closeout aggregate — ten late hard-blocks last session); targeted pytest plus the
  owning validator at each commit boundary; the full serial suite plus a bounded
  fresh-eye round at each slice boundary; `./scripts/run-quality.sh` once at the
  bundle boundary. No push, no CI dispatch, no cautilus run.
- Slice review packet: intent, changed files with owning/generated surfaces,
  the D-entry text before and after, expected invariants, the executed proof
  commands and their output, non-claims, out-of-scope lines, and the open
  questions the slice did not settle.
- Second review round: OWED by slices 2 and 3 (both change verdict logic on a
  proof surface). Slice 1 changes reporting, not a verdict, so one round.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Get the operator call on the three unarmed refusals D46 (adapter-YAML), D47 (inventory value markers), D48 (release surfaces), then arm or record what the call decides

**Source handoff entry #2: Three unarmed refusals wait on an operator call**

> :
>    [D46](./deferred-decisions.md) adapter-YAML, [D47](./deferred-decisions.md)
>    inventory value markers, [D48](./deferred-decisions.md) release surfaces.
>    Each records its measured cost.

## Non-Goals

- Not a release: no plugin version bump, no publish, no tag.
- **Do not arm any of the three refusals as originally posed.** The operator's
  2026-08-01 call was: D46 stays deferred (warn, do not refuse), D47 and D48 take
  the better repair each entry already named instead of the binary arming.
- Do not rewrite the five frozen quality reviews that cite `inventory_nose_clones`
  / `inventory_doc_duplicates` to satisfy a later gate. That is the Goodhart move
  `validate_inventory_consumption.py`'s own docstring exists to refuse.
- Do not absorb adjacent handoff entries beyond the selected chunk: the sweep's
  remaining high rows (S15, S31, S36, S37, S111), the E-cluster, and issue #467
  stay out.
- Do not close sweep row S31 or S11. D47 and D48 both state they do not narrow
  those rows, and this goal does not change that.

## Boundaries

- In scope (D46, slice 1):
  [`skills/public/handoff/scripts/chunked_routing_issue_source.py`](../../skills/public/handoff/scripts/chunked_routing_issue_source.py)
  — the recorded consumer that reads `adapter["data"]` without checking `valid`
  or `warnings`.
- In scope (D48, slice 2):
  [`skills/public/release/scripts/current_release.py`](../../skills/public/release/scripts/current_release.py),
  [`skills/public/release/scripts/resolve_adapter.py`](../../skills/public/release/scripts/resolve_adapter.py),
  [`skills/public/release/references/adapter-contract.md`](../../skills/public/release/references/adapter-contract.md),
  [`.agents/release-adapter.yaml`](../../.agents/release-adapter.yaml), and the
  sync channel it must derive from
  ([`scripts/sync_root_plugin_manifests.py`](../../scripts/sync_root_plugin_manifests.py),
  whose JSON already carries `written_paths`).
- In scope (D47, slice 3):
  [`skills/public/quality/references/inventory-consumer-fields.json`](../../skills/public/quality/references/inventory-consumer-fields.json),
  [`scripts/validate_inventory_consumption.py`](../../scripts/validate_inventory_consumption.py),
  [`scripts/measure_inventory_consumption_floor.py`](../../scripts/measure_inventory_consumption_floor.py),
  and the declaration-coverage checkers that read the same JSON.
- In scope (all slices): [`docs/deferred-decisions.md`](../../docs/deferred-decisions.md)
  — each slice updates its own D-entry with the call and what stays open.
- Correction to the auto-draft: `docs/deferred-decisions.md` **exists**. The
  chunker's `MISSING` marker on `deferred-decisions.md` was a relative-link
  resolution artifact (the entry's links are `./deferred-decisions.md` from
  `docs/`), verified by direct `ls` before shaping. Nothing here is blocked on
  re-targeting.
- Portable per implementation-discipline: the release and quality repairs land in
  public skills consumed by other repos, so a derivation channel must be declared
  through the adapter seam, never hardcoded to this repo's own script names.
- SUPERSEDED by plan-critique B3/B4 — kept for provenance, not as instruction:
  slice 2 was to choose between (a) a sync listing mode and (b) a corroborator over
  the declared list. `written_paths` cannot name two of the four surfaces, and (b)
  closes only over-declaration while D48's recorded defect is disarm-by-deletion.
  The live question is Q2 in the Operator Decision Queue. The one part that still
  holds: `current_release.py` is a READ-only check and must never run the mutating
  `sync_command` to learn what sync writes.
- Stop conditions: (1) if a repair would require rewriting a frozen artifact, stop
  and record rather than rewrite; (2) if any slice's proof needs a push, remote CI,
  or a cautilus run, stop — those are out of scope this session; (3) slices 2 and 3
  do not start until Q1/Q2 are answered. The earlier "if the distinctiveness
  declaration turns out to reintroduce the self-declaration class, stop" condition
  is REMOVED: plan-critique B2 showed it was a fig leaf — the answer was already
  determinable before activation, the condition had no checkable form, and it sat
  after the largest slice's work would already be sunk. It is replaced by Q1, which
  decides the question up front instead of discovering it late.

## User Acceptance

- `docs/deferred-decisions.md` records the operator's 2026-08-01 call on all three
  entries, each stating what changed, what stays deferred, and what is still
  unproven — readable without this session's memory.
- D46: a consumer of the adapter contract now actually reads `valid`/`warnings`.
  Demonstrated by an executed check, not by prose: an **issue** adapter
  (`.agents/issue-adapter.yaml`, the adapter the blind consumer at
  `chunked_routing_issue_source.py:253-258` actually loads — NOT the handoff
  adapter, per plan-critique B5) carrying an uninterpretable line produces a
  visible warning on the chunker's issue-source path where today it produces
  silence. Shown by a pytest with an injected runner, not by a CLI run that would
  make a live `gh` call. The refusal stays unarmed, and nothing branches on
  `valid`.
- D48: an emptied or absent `required_release_surfaces` is now REFUSED rather than
  silently passing — the disarm-by-deletion path D48 actually recorded. Shown by
  executed `current_release.py` output on both an emptied and an intact adapter,
  with the four real surfaces still clean. The sync-derivation idea is withdrawn in
  D48 with the reason (`written_paths` names the plugin root as a directory, so two
  of the four surfaces never appear in it), so a later session does not retry it.
- D47: the hand-counted 51/169 and "5 checked-in reviews" are replaced by executed
  numbers from a marker-aware measurement, with the corpus denominator stated and
  `charness-artifacts/quality/history/` either covered or named as uncovered. The
  measurement names, by path and by field, which artifacts a marker rule would
  actually refuse. **Nothing is armed**, and D47 records why the distinctiveness
  repair it previously named cannot be built as described.
- Every claim above is backed by a command in `## Final Verification` with its
  actual output, and anything not executed is named as a non-claim.

## Agent Verification Plan

Low-cost, at each commit boundary:

- `python3 scripts/validate_inventory_consumption.py --repo-root . --artifact-path <p>`
  once per affected artifact (slice 3) — the gate validates ONE artifact per run
  (`DEFAULT_ARTIFACT_PATH` is the rolling pointer), so a single bare invocation
  cannot show five reviews passing (plan-critique M1)
- `python3 skills/public/release/scripts/current_release.py --repo-root .` (slice 2)
  — no `--json` flag exists; JSON is unconditional (plan-critique B6)
- the dup-ratchet gate at the FIRST edit to a gated file in each slice
- `python3 scripts/check_doc_authoring_preflight.py --path docs/deferred-decisions.md`
- the packaging/mirror sync check at any slice touching a mirrored surface, so
  `plugins/charness/` drift is caught by the slice that causes it rather than at
  slice 4 (plan-critique M2)
- targeted `pytest` for the touched test modules

At each slice boundary:

- the full serial test suite for the touched families
- one bounded fresh-eye review (typed `bounded-reviewer`, read-only, shared
  worktree, boundary fingerprint snapshot/verify around it)
- a SECOND bounded round reading the repairs for slices 2 and 3, because both
  change verdict logic on a proof surface

At the bundle boundary:

- `./scripts/run-quality.sh`
- NOT `python3 scripts/measure_inventory_consumption_floor.py` for D47's number:
  that script's own docstring states the 51/169 and five-review counts are NOT
  produced by it and were measured by hand, so re-running it would be
  self-confirming evidence (plan-critique B7). A marker-aware measurement has to
  be built, and it must reach `charness-artifacts/quality/history/` or say it
  does not (plan-critique M1).

Explicitly NOT part of this plan, and therefore non-claims: `git push`, any remote
CI dispatch, any `cautilus evaluate` run, and any release publish. Local green is
local green.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | D46: give the adapter warning a reader — surface `valid`/`warnings` on the `chunked_routing_issue_source.py:253-258` **issue**-adapter consumer that reads `adapter["data"]` blind; record the call in D46 | Cheapest slice, and it converts D46's own non-claim ("the warning is legibility, not teeth — nothing reads it today") into something with one real consumer, without arming the refusal the round-1 review rejected. Unaffected by the B1–B4 escalation | Pytest with an injected runner (not a CLI run, which makes a live `gh` call) showing an uninterpretable issue-adapter line surfacing where it was silent; `issue_source_diagnostic` carries it; mirror sync check; D46 updated | ready |
| 2 | D48 (RESHAPED by operator call, Q2): close only the disarm-by-deletion direction — make an EMPTY/absent `required_release_surfaces` a refusal rather than a silent pass in `current_release.py`; record the call and the withdrawn derivation idea in D48 | This is the direction D48 actually recorded (*"deleting those four adapter lines disarms it with nothing corroborating them"*), and unlike the sync-derivation it is buildable: no path→key map, no new self-declared adapter field, no drift-by-default toll on consumers | `current_release.py --repo-root .` before/after; a case where an emptied/absent declaration is now refused where it silently passed; the four declared surfaces still clean; mirror sync check; two bounded review rounds; D48 updated | ready |
| 3 | D47 (RESHAPED by operator call, Q1): MEASUREMENT-only — build the marker-aware measurement D47's own reopen trigger asks for, covering `charness-artifacts/quality/history/` too; replace the hand-counted 51/169 and "5 reviews" with executed numbers; record the B1 contradiction in D47. Arm nothing | The distinctiveness repair is unbuildable as named (B1) and the flag is a stronger self-declaration than the one D48 objects to (B2). A real measurement is what makes the NEXT call decidable, and it is the one move that neither pays the standing-red toll nor ships a measured-zero no-op as a repair | The new measurement's output with its corpus denominator stated; which artifacts and which fields a marker rule would actually refuse, by path; D47 updated with the executed numbers replacing the hand counts and with B1/B2 recorded; two bounded review rounds | ready |
| 4 | Closeout: bundle-boundary quality gate, final verification, critique, retro, commit | Repo contract treats critique, closeout, and commit as part of task-completing work | `./scripts/run-quality.sh` output, `check_goal_artifact.py` green, retro dispositions each `applied:` or `tracked issue`, commit | pending |

Discuss before activation: Resolved with the operator in the shaping transcript, all three items. (1) Proof-level non-claims — this goal runs no push, no remote CI dispatch, no cautilus evaluation and no publish, so every verdict it produces is local-only; resolved as accepted, and stated as a non-claim in the Agent Verification Plan rather than left implicit. (2) Verdict-logic change on two proof surfaces — slices 2 and 3 change what `current_release.py` and `validate_inventory_consumption.py` decide about other artifacts, so both owe a second bounded fresh-eye round reading the repairs; resolved and recorded in the Active Operating Frame. (3) Scope of the operator's call — the answer to all three deferred decisions was explicitly NOT to arm the refusal as posed; resolved and written into Non-Goals so a later session cannot read this goal as authorization to arm them. The three-decision bundle is deliberate: it is one operator decision session over three entries that share one closeout surface, and the alternative standalone chunks were presented and declined.

## Operator Decision Queue

All three of this goal's originating decisions were answered live, and the two
reshape questions the plan critique forced were answered before any code moved.
Nothing new was deferred to the operator during the run.

Remaining for a future call, recorded but NOT queued here because each already has
its own owning entry: D45's premise (see [issue #468](https://github.com/corca-ai/charness/issues/468)),
and the release resume gap named in D48.

### Q1 — RESOLVED 2026-08-01: measurement-only

- Decision: what slice 3 should actually do, given that per-field distinctiveness
  cannot both spare the five cited reviews and impose a real marker rule (B1), and
  that the flag is a stronger self-declaration than the one D48 objects to (B2).
- Owner: operator (repo owner). This is the same class of call D45 reserves to the
  owner: who pays a standing-red toll.
- Why deferred: the run did not stop on it — slice 1 is unaffected and can proceed
  — but slice 3 must not be executed against acceptance text now known to be
  unachievable.
- Unblock action: choose one — (a) reshape slice 3 into a MEASUREMENT-only slice
  that builds the marker-aware measurement D47's reopen trigger asks for, replaces
  the hand-counted 51/169 and the hand-counted five reviews with executed numbers
  covering `history/` too, records the B1 contradiction in D47, and arms nothing;
  (b) accept the standing red and arm the marker rule, rewriting nothing;
  (c) drop D47 from this goal and return it to the queue with B1/B2 recorded.
- **Answered: (a) measurement-only.** Slice 3 builds the marker-aware measurement,
  arms nothing, and records B1/B2 in D47. Rejected (b) arming, because the operator
  is not levying the standing-red toll; rejected (c) dropping it, because leaving
  D47's hand counts unreplaced means the next session re-derives them or trusts
  them.
- Revisit trigger: any future attempt to close D47, or the declaration file gaining
  per-field distinctiveness by another route.

### Q2 — RESOLVED 2026-08-01: close the disarm-by-deletion direction only

- Decision: what slice 2 should actually do, given that `written_paths` does not
  name two of the four declared surfaces (B3) and that a corroborator only closes
  over-declaration while D48's recorded defect is disarm-by-deletion (B4).
- Owner: operator (repo owner).
- Why deferred: same as Q1 — it blocks slice 2 only.
- Unblock action: choose one — (a) make the sync channel actually emit its surface
  set (a listing mode on the sync command, surfaced through the adapter seam),
  accepting that the adapter field is itself self-declared and saying so instead of
  claiming the class is broken; (b) close only the disarm-by-deletion direction —
  make an EMPTY `required_release_surfaces` a refusal rather than a silent pass,
  which is the direction D48 actually recorded; (c) drop D48 from this goal and
  return it to the queue with B3/B4 recorded.
- **Answered: (b) close only the disarm-by-deletion direction.** An empty or absent
  `required_release_surfaces` becomes a refusal instead of a silent pass. Rejected
  (a) the sync listing mode, because its new adapter field is itself self-declared,
  so it would cost the most and still not break the class it claims to break;
  rejected (c) dropping it, because the disarm path is buildable today.
- Revisit trigger: the sync command gaining a machine-readable list of what it
  writes, or a release published with a surface the declaration did not cover.

## Slice Log

### Slice 1: Slice 1 — D46: the adapter warning gets a reader

- Objective: Close the 'nothing reads it today' half of D46's non-claim by making the recorded blind consumer report the issue adapter's self-report, WITHOUT arming the refusal the operator kept deferred.
- Why this approach: D46's refusal cannot be armed honestly: the population it would judge is consumer-authored .agents/*-adapter.yaml that this repo has never seen, so its 0-uninterpreted-lines measurement proves arming is free here and proves nothing there. The consumer defect, by contrast, is a written-down fact with a local fix.
- Commits:
- What changed: skills/public/handoff/scripts/chunked_routing_issue_source.py (LAST_ISSUE_ADAPTER_REPORT + _adapter_report/_report_lines); parse_handoff_entries.py (payload emission); propose_merges.py and prepare_chunk_packet.py (forwarding); chunked_routing_cli.py (new shared entries_from_pipeline_payload + forward_carried_keys); tests/test_handoff_chunker_issue_source.py and tests/test_handoff_chunker_parse.py (11 tests); docs/deferred-decisions.md D46; charness-artifacts/quality/dup-review.json (2 classifications); generated mirror under plugins/charness/ re-synced and proven byte-identical.
- Alternatives rejected: Arming the refusal (rejected by the operator and by round-1 review of the prior slice: a colon-less line would turn a consumer's whole issue lane red). Branching on valid inside build_issue_entries (rejected: it would empty the issue backlog from pickup, indistinguishable from the documented trackerless fallback). Reporting warnings only (rejected after review: errors and warnings are disjoint in that loader, so valid:false would arrive with no diagnosis). Extracting a shared stage runner across all five pipeline CLIs (rejected: the per-stage skeleton is the pipeline's CLI contract, already accepted as intentional in the dup overlay; the genuinely extractable half was extracted instead).
- Targeted verification: pytest tests/test_handoff_chunker_*.py -> 138 passed. Real-loader test drives resolve_adapter.load_adapter over D46's own colon-less default_org line and asserts the D46-stamped warning. check_dup_ratchet.py: FAIL(3 families) at first edit -> extracted the shared half -> FAIL(2) -> both classified intentional against existing precedent 6ff3e380d6a8fcaf/0bc23ea0000c6cf9 -> OK, fixable_ceiling=0. sync_root_plugin_manifests.py re-run; diff -q proves all four mirrored files byte-identical.
- Test duplication pressure: 11 new tests in two existing modules; no new test file. The dup gate flagged the CLI-skeleton families as expected and was run at the FIRST edit to a gated file, not at the closeout aggregate (the recorded lesson that had failed to prevent itself twice).
- Critique: One bounded fresh-eye round (typed bounded-reviewer, read-only, fingerprint window w-20260801T070657Z, verdict clean). It found 7 defects, ALL folded: errors dropped from the report (the loader's only invalidity channel); the field dying at propose_merges, repeating recorded defect F3; the CLI emission untested; not-found boilerplate reported as signal; bool(valid) fabricating a false verdict and an errors-only shape reading as clean; a TypeError in reporting able to empty the backlog through the fallback except; and two over-claims in the D46 entry text. The unfaithful invalid-adapter fixture it caught (an errors-list message stubbed into warnings) was the reason the dropped-errors gap was invisible. Second round not owed: this surface reports, it does not render a verdict about other code.
- Off-goal findings:
- Lessons carried forward: A reviewer's finding that a FIXTURE is unfaithful to the real loader was worth more than any finding about the code: the fixture was what made the real gap invisible. And running the dup-ratchet at the first edit turned a would-be closeout hard-block into a mid-slice extraction that improved the design.
- Metrics:

### Slice 2: Slice 2 — D48: close disarm-by-deletion at the irreversible boundary

- Objective: Close the direction D48 actually recorded ('deleting those four adapter lines disarms it with nothing corroborating them') without levying the drift-by-default toll the operator refused.
- Why this approach: The entry's own named repair (derive the expected set from the sync command output) is unbuildable: the sync report names the plugin root as a DIRECTORY, so two of the four surfaces never appear in it, and the listing-mode variant hides the channel behind a new self-declared adapter field. Withdrawn in D48 with the reason so no future session retries it.
- Commits:
- What changed: current_release.py (absence_corroboration, undeclared_absent_surfaces, unpublished_release_surfaces, unconditional drift for present-but-corrupt surfaces, symmetric unknown-name warnings, contradiction warning, _declared_list scalar guard); resolve_adapter.py (new field); publish_release_preflight.py (new release_surface_blocker); publish_release_cli.py (delegates + exports); adapter-contract.md and adapter.example.yaml; docs/public-skill-dogfood.json; docs/deferred-decisions.md D48; 12 tests; the sync fixture; mirror re-synced.
- Alternatives rejected: Drift-by-default (refused by the operator: permanent red for a lane a consumer never published). Lane-asymmetry inference (built, then dropped: it invented publishing semantics the repo does not author, and the failing fixtures proved it). Overloading required_release_surfaces as the opt-out (built, then killed by round 1: that field means 'must exist', so it makes the absence drift — there was NO declaration that let a claude-only repo publish). Routing the run planner on it (built, then reverted: the planner runs BEFORE sync, so absence there is the ordinary fresh-checkout state). Gating the resume path (built, then reverted: every resume fixture uses a repo with no generated tree, so it is a contract change with its own blast radius — recorded as a known gap instead).
- Targeted verification: Executed before/after on a scenario worktree: OLD script on a repo with the codex plugin.json deleted AND the declaration deleted -> drift: [], i.e. a clean publish verdict over a missing surface; NEW -> absence_corroboration=uncorroborated and the publish blocker fires. Present-but-corrupt ({"version": half-written) with no declaration -> OLD drift: [], NEW drift: ['codex_plugin=<unreadable>']. charness itself: unchanged, not-applicable, drift: []. pytest quality_gates: 55 + 67 passed in the touched modules; the full quality_gates suite ran 4317 passed with only the failures this slice then fixed. dup-ratchet OK after two classifications and one recorded rotation.
- Test duplication pressure: 12 new tests in one existing module, no new file; the module stayed inside its length budget. One fixture was CORRECTED rather than added to: it wrote the claude marketplace as {version} while the real reader wants metadata.version, so every publish test had been silently exempt from that arm.
- Critique: TWO bounded fresh-eye rounds, both typed bounded-reviewer, both fingerprint-clean (windows w-20260801T072844Z, w-20260801T074707Z). Round 1 found 2 blockers + 4 minors, including that the remedy I shipped was unpublishable advice and that the disarm survived intact in the unreadable/no-version states a failed sync actually produces. Round 2 read the REPAIRS and found that my round-1 fix shipped the class it fixed: the unconditional corrupt-surface arm was UNEXEMPTABLE, and because the run planner has always routed on drift, it reintroduced through the back door the exact permanent-red toll the planner revert had just closed — for marketplace surfaces, which are per-repo files, so no corruption is even needed to trigger it. Round 2 also caught the refusal message still naming the wrong field, the scaffold example omitting the remedy, asymmetric typo warnings, and a stale public-skill-dogfood entry asserting the disarm was still open. Cap reached: round-2 repairs are recorded as accepted-unreviewed.
- Off-goal findings: publish_release_resume.py reaches create_release without any release-surface check — pre-existing for drift too, recorded in D48 as a known gap rather than half-shipped. The claude-marketplace fixture defect means prior publish-test greens over that surface were never real.
- Lessons carried forward: The two-round rule paid for itself twice over in one slice. Round 1 killed a remedy that could not be followed; round 2 killed a fix that recreated the original harm through a channel I had just finished closing elsewhere. Both times the tell was the same: I reasoned about what a consumer's tree WOULD look like instead of enumerating what the reader actually returns.
- Metrics:

### Slice 3: Slice 3 — D47: measure the marker rule instead of arming it

- Objective: Replace D47's hand counts with an executed, re-runnable measurement of what a value-marker rule would cost, and arm nothing.
- Why this approach: D47's own named repair — per-field distinctiveness in inventory-consumer-fields.json — cannot be built as described: the fields the corpus engages ARE the ordinary-English ones, so declaring them non-distinctive refuses the cited reviews while declaring them distinctive makes the rule apply to nothing and ship a measured-zero no-op as a repair. It is also a stronger self-declaration than the one D48 objects to. Measuring is what makes the next call real.
- Commits:
- What changed: scripts/measure_inventory_marker_rule.py (NEW); scripts/inventory_measurement_lib.py (NEW, extracted when the dup gate fired); scripts/measure_inventory_consumption_floor.py (uses the lib, docstring corrected); scripts/validate_inventory_consumption.py (arming comment corrected); charness-artifacts/probe/2026-08-01-inventory-marker-rule.json (NEW); tests/test_inventory_marker_rule_measurement.py (NEW, 14 tests); docs/deferred-decisions.md D47; two dup classifications; stale line refs in the sibling's test comments.
- Alternatives rejected: Building the distinctiveness declaration (rejected before it was written, by the plan critique). Arming the marker rule (rejected by the operator: the standing-red toll is the owner's to levy). Adding the measurement to the sibling script (rejected: a different rule deserves its own script, and the sibling is near its length budget).
- Targeted verification: Executed, recorded, and pinned: top level 105 artifacts / 169 presence-only mentions / 161 clearing the floor / 114 marked / 47 unmarked / 5 refused citations across 4 artifacts; recursive 123 / 252 / 244 / 179 / 65 / 7 citations across 5. Both variants recorded in the probe with _provenance and pinned against the live tree by the test suite. The presence-only total reproduces the sibling probe's 169 exactly, which is asserted as a test. 320 inventory/declaration tests pass; dup-ratchet OK; length gate clean.
- Test duplication pressure: 14 tests in one new module plus a probe record. The first version of the real-corpus test asserted total == marked + unmarked, which is how unmarked is COMPUTED — it could not fail for any implementation. Round 1 caught it; it now pins the recorded probe, the citation count, and the recursive variant.
- Critique: TWO bounded rounds, both fingerprint-clean. Round 1 found the measurement's central regex matched the GAP BETWEEN two code spans, so bare prose between two unrelated spans scored as marked — a one-way bias that inflated 'marked' and produced the tidy headline that the toll was smaller than D47 recorded. Correcting it moved unmarked 42 -> 47 and refusals 3 -> 4 artifacts. Round 1 also found that 169 was never a hand count (the sibling script produced it), so the comparison was apples-to-oranges, and that the tautological test pinned nothing. Round 2 read the repairs and found: my arming-comment 'repair' had silently not applied (the exact-string replace missed a line wrap) so the wrong numbers still shipped; my new claim that 'the hand count was substantially right' swapped units, since the hand count's 5 was REVIEWS and the executed 5 is CITATIONS across 4 ARTIFACTS — on the hand count's own unit the answer is 4; a comment asserted the exemption branch was 'live under --recursive' while the probe recorded beside it said measured-zero; and the gate skips on three exemption arms, not one. All folded. Round 2 is the cap: its repairs are accepted-unreviewed.
- Off-goal findings: markers_for still counts a field name inside a backticked PATH or flag as a citation, and does not model odd-backtick lines or fenced blocks; all three carry the same one-way bias as the repaired bug and are verified inert on today's corpus. Recorded in the probe and in D47 rather than repaired.
- Lessons carried forward: Two lessons, both about my own claims rather than the code. A string replace that does not match fails SILENTLY, so a 'repair' can be reported as done while the wrong number ships — round 2 caught exactly that. And when a corrected measurement lands near a number I expected, the temptation is to narrate agreement; here that meant swapping 'reviews' for 'citations' to make 5 equal 5, when the honest answer on the hand count's own unit was 4.
- Metrics:

## Context Sources

- Source: handoff entry #2 (Three unarmed refusals wait on an operator call) — see [docs/handoff.md](../../docs/handoff.md).
- The three entries themselves: [D46, D47, D48 in docs/deferred-decisions.md](../../docs/deferred-decisions.md).
  Read these first — each already carries its measured cost, its why-deferral-is-right
  argument, its non-claims, and the better repair this goal executes.
- [D45](../../docs/deferred-decisions.md) is the precedent all three cite for
  "the owner chooses whether to pay a standing-red toll, not the agent."
- The sweep that produced all three rows:
  [2026-07-28 evidence-surface triage sweep](../audit/2026-07-28-evidence-surface-triage-sweep.md)
  (S24 → D46, S10 → D47, S35 → D48).
- The goal whose closeout parked them:
  [2026-08-01 close-the-sweeps-remaining-high-rows-by-class](./2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md),
  whose `## Off-Goal Findings` records the D46 consumer defect slice 1 repairs.
- [charness-artifacts/retro/recent-lessons.md](../retro/recent-lessons.md) — required
  before changing repo operating contracts; slices 2 and 3 both change one.
- Chunker provenance: this artifact was auto-drafted from handoff chunk `chunk-c`
  (rank 1 of 3) and shaped by the achieve Before-phase in the same session.

## Interview Decisions

Four questions were asked; each is recorded with the family considered, the chosen
value, the rejected alternatives' reason, and the anti-anchoring probe result.

1. **D46 — warn, refuse, or the named better repair?**
   Family considered: {keep deferred and change nothing, keep deferred and repair
   the recorded consumer, do the malformed-vs-unsupported separation first, arm the
   refusal now}. **Chosen: keep deferred (warn, do not refuse) AND repair the
   recorded consumer defect.** Rejected: arming, because the population a refusal
   would judge is consumer-authored `.agents/*-adapter.yaml` that this repo has
   never seen and cannot enumerate, so the recorded 0-uninterpreted-lines
   measurement proves arming is free *here* and proves nothing *there*; also
   because round 1 could not yet separate "malformed" from
   "legal-but-unsupported-by-our-mini-parser". Rejected: the separation work
   itself, as the most expensive option for a refusal we are not arming. Rejected:
   change-nothing, because it leaves a defect the repo has already written down.
   Anti-anchoring: `axis: audited-repo` — this repo vs a consumer repo are two
   instances of the same axis, and the whole reason arming is wrong is that the
   value differs across it. The decision is deliberately scoped to the axis, not
   generalized from this repo's clean measurement.
2. **D47 — require a value marker?**
   Family considered: {arm the marker requirement, per-field distinctiveness
   declaration, keep deferred}. **Chosen: per-field distinctiveness declaration in
   `inventory-consumer-fields.json`.** Rejected: arming, because it refuses five
   checked-in reviews and the only remedies are rewriting frozen artifacts to
   satisfy a later gate (the Goodhart move the validator's own docstring refuses)
   or accepting a standing red — a toll that is the owner's to levy, per D45.
   Rejected: change-nothing, because the entry itself already names the better
   repair as available. Anti-anchoring: `axis: field-name distinctiveness` — the
   value that varies is per declared field (`scope`/`status` vs
   `package_dated_incident_count`), which is exactly why a single global marker
   rule over-anchors on the generic-name case.
3. **D48 — is absence drift without a declaration?**
   Family considered: {default to drift-on-absence, derive the expected set from
   the repo's own sync channel, keep declared-only}. **Chosen: derive/corroborate
   from the sync channel.** Rejected: drift-by-default, because every consumer that
   publishes only some surfaces goes permanently red for a surface it never meant
   to publish, with no local remedy but an exemption declaration — the same toll
   D45 refuses to levy unilaterally. Rejected: change-nothing, because the entry's
   standing non-claim (nothing checks that a declared surface is one sync actually
   produces) then survives untouched. Anti-anchoring: `axis: packaging channel` —
   `sync_command` is already an adapter field precisely because it varies per
   consumer repo, so the derivation must go through that seam and must not name
   `sync_root_plugin_manifests.py`.
4. **Post-critique reshape of slices 2 and 3 (asked after the plan critique broke
   the premise of two of the three choices above).** D47 family considered:
   {measurement-only, arm and accept the standing red, drop from this goal}.
   **Chosen: measurement-only.** D48 family considered: {close disarm-by-deletion
   only, build a sync listing mode, drop from this goal}. **Chosen: close
   disarm-by-deletion only.** Rejection reasons are recorded on Q1 and Q2 in the
   Operator Decision Queue. Anti-anchoring: `axis: audited-repo` for both — the
   reason neither original repair survives is that each rested on a channel this
   repo authors, and the reshaped moves were chosen precisely because they do not
   levy a toll on a consumer repo that never made the declaration.
5. **Mode — artifact-only or implementation-continuation?**
   Family considered: {shape and stop at draft, shape then execute}. **Chosen:
   shape then execute.** Rejected: artifact-only, because the operator answered the
   three calls in this session's interview and stopping at draft would leave those
   answers recorded only inside the goal, not in `docs/deferred-decisions.md` where
   the next session looks. Anti-anchoring: `single-point: operator present now` —
   the mode is a property of this invocation, not a system axis.

## Plan Critique Findings

Reviewer provenance: one bounded fresh-eye round, typed `bounded-reviewer`
(read-only: Read/Grep/Glob only, no exec, no spawn), parent-delegated, run in the
shared parent worktree with
[`reviewer_boundary_fingerprint.py`](../../skills/shared/scripts/reviewer_boundary_fingerprint.py)
snapshot/verify around it — window `w-20260801T065201Z-1242305`, verdict `clean`,
no drift. The reviewer read the plan, D45–D48, and all seven named in-scope
surfaces. Round 2 on the repaired plan is NOT owed here: this round produced plan
revisions, not proof-surface repairs; the second-round obligation attaches to
slices 2 and 3 when they change verdict logic.

**Blockers folded (parent-verified before folding, not taken on the reviewer's
word).** Each was re-checked against the source before the plan changed:

- **B5 — slice 1's acceptance named the wrong adapter.** The blind consumer at
  `chunked_routing_issue_source.py:253-258` loads the **issue** adapter
  (`.agents/issue-adapter.yaml`), matching D46's typo'd-`default_org` example.
  The handoff adapter is read on a different path, `load_issue_source_config`
  (`:175-197`), which calls `adapter_lib.load_yaml_file` rather than
  `load_yaml_file_report`, so uninterpreted lines are never computed there at all,
  and the body is wrapped in a blanket `except Exception: return config` that is
  load-bearing for the documented trackerless fallback. Verified by reading both
  call sites. Folded: User Acceptance now names the issue adapter, and slice 1's
  scope is pinned to the `:253-258` consumer.
- **B6 — `current_release.py` has no `--json` flag.** Verified: `main()` declares
  only `--repo-root` and prints JSON unconditionally. The plan's per-commit
  command would have exited 2 on every slice-2 run. Folded: the flag is dropped
  from the Agent Verification Plan.
- **B7 — the bundle-boundary re-run cannot replace D47's hand counts.**
  Verified against `measure_inventory_consumption_floor.py`'s own docstring: *"Two
  numbers cited in `docs/deferred-decisions.md` D47 are NOT produced here and were
  measured by hand: 51 of 169 field mentions carry no value marker, and arming a
  value-marker rule would refuse 5 checked-in reviews."* The script measures the
  residual-char floor, a different rule. Folded: slice 3 now has to BUILD the
  marker-aware measurement; re-running the existing script is explicitly not
  acceptable evidence.
- **M1 — the corpus glob cannot see three of the citing artifacts.** Verified:
  13 artifacts cite `inventory_nose_clones` / `inventory_doc_duplicates`, and
  three of them (`2026-06-06-quality-review.md`, `2026-06-11-quality-review.md`,
  `2026-06-25-retro-skill-quality-review.md`) live in
  `charness-artifacts/quality/history/`, outside the non-recursive `*.md` glob.
  Folded: slice 3 must pin the affected artifacts by path, and the measurement
  must cover `history/` or state that it does not.
- **M2 — generated plugin mirrors were absent from every slice's Boundaries.**
  All three slices touch mirrored surfaces under `plugins/charness/`. Folded into
  Boundaries and into the per-commit checks, so mirror drift is caught at the
  slice that causes it rather than at slice 4.
- **M3 — slice 1's one-round classification was only conditionally true.**
  Branching on `valid: false` would be a verdict (the whole issue backlog vanishes
  from pickup, indistinguishable from the trackerless fallback). Folded: slice 1
  is pinned to surfacing only, and any branch on `valid` promotes it to the
  two-round class.

**Blockers that break a premise, escalated rather than folded.** Two of the three
repairs the operator selected do not, on inspection, do what their deferred-decision
entry says they do. These were returned to the operator rather than silently
redesigned:

- **B1 — D47's named better repair cannot meet its own acceptance.** The plan
  promised both "the marker requirement applies only to non-distinctive names" and
  "the five cited reviews are NOT refused". Parent-verified as mutually exclusive:
  `inventory-consumer-fields.json` declares, for `inventory_nose_clones.py`,
  `["status", "advisory", "family_count", "families", "excludes", "ignore_file",
  "paths", "ranking", "scope", "notes"]` and, for `inventory_doc_duplicates.py`,
  a similarly generic set — and the corpus engages exactly the ordinary-English
  ones on incidental prose. Declaring them non-distinctive (the honest call)
  refuses the reviews; declaring them distinctive makes the marker rule apply to
  no field the corpus ever engages, i.e. a measured-zero no-op recorded in D47 as
  a repair. Either horn violates a stated acceptance bullet.
- **B2 — the stop condition guarding B1 is a fig leaf.** The distinctiveness flag
  is a strictly *stronger* self-declaration than the `required_release_surfaces`
  list D48 flags: it decides whether the gate can fire on a field at all, it lives
  inside the audited repo, and per B1 the agent has an incentive to set it the way
  that makes the slice green. "If it turns out to reintroduce the class, stop" is
  discovered rather than decided, has no checkable form, and sits after the
  largest slice's work is sunk.
- **B3 — D48's named derivation channel provably cannot produce the surface set.**
  Parent-verified in `sync_root_plugin_manifests.py:65-92`: `written_paths` carries
  the plugin root as a **directory** (`plugins/charness`) plus the root marketplace
  artifacts. Two of the four declared surfaces — `claude_plugin`
  (`plugins/charness/.claude-plugin/plugin.json`) and `codex_plugin` — never appear
  in it. `current_release.py`'s vocabulary is symbolic keys, not paths, so a
  derivation also needs a path→key map with nowhere portable to live.
- **B4 — the fallback option answers a different question than D48 asked.** A
  corroborator that "refuses a declaration the sync channel does not produce"
  checks only over-declaration. D48's recorded defect is the opposite direction:
  *"deleting those four adapter lines disarms it with nothing corroborating them."*
  An empty declaration has nothing to contradict, so the disarm-by-deletion path
  survives verbatim while the slice passes its own evidence bar. And option (a)'s
  new adapter field is itself a self-declared field in the same adapter, so slice 2
  cannot establish the "machine channel outside the audited surface" precedent the
  slice ordering rests on.

**Over-worry raised but not folded.**

- The worry that `resolve_target`'s three preconditions (empty target AND no git
  remote AND no `default_repo`) make slice 1's reproduction impossible is
  unfounded: those gate the typo's *effect*, not the warning's *visibility*, and
  `parse_handoff_entries.py:242` already writes `issue_source_diagnostic` into the
  CLI payload, so a surfacing channel exists without touching the caller. Recorded
  as a caveat instead: that payload key exists only under `--with-issues`, where
  `build_issue_entries` is called with no injected runner, so a CLI-level
  reproduction makes a live `gh` call while a pytest with an injected runner does
  not. Slice 1 should use the pytest.
- No divergence was found in the plan's *attribution* of the better repairs to
  D47 and D48, and none in its counts (169/105/5) or its `MISSING`-marker
  correction. The divergence is in what those repairs can actually do (B1, B3, B4),
  not in the citation.

The three consequential activation items and their resolutions are recorded in the
`Discuss before activation:` summary above the Operator Decision Queue.

## Off-Goal Findings

- **`publish_release_resume.py` reaches `create_release` with no release-surface
  check at all** — not `drift`, not the new corroboration arm. Pre-existing, so a
  surface deleted or corrupted between a failed publish and its resume reaches the
  irreversible boundary unchecked. Gating it was built and reverted: every resume
  fixture exercises a repo with no generated tree, so it is a contract change with
  its own blast radius. Recorded in D48 as a known gap. OPEN.
- **A test fixture misrepresented a release surface for months.**
  `release_publish_sync_root_plugin_manifests.py` wrote the claude marketplace as
  `{"version": ...}` while the real reader wants `metadata.version`, so that surface
  read as `no-version` and every publish test was silently exempt from its arm.
  REPAIRED in slice 2, and it means prior publish-test greens over that surface were
  never real.
- **`markers_for` still has one-way false positives** — a field name inside a
  backticked PATH or flag scores as a citation; odd-backtick lines and fenced blocks
  are unmodelled. All verified inert on today's corpus, all biased the same way as
  the bug slice 3 fixed. Recorded in the probe and D47. OPEN by decision (round 2 is
  the review cap).
- **D45's premise may carry the same defect D48 just found** — it names "moving the
  exemption to the adapter" as S31's correct repair, the same self-declaration
  channel, and both D46 and D48 cite it as precedent. Not verified. Filed as
  [#468](https://github.com/corca-ai/charness/issues/468).

## Coordination Cues

- Routing: handoff — selected from installed skill metadata for the pickup, which
  chunked the live backlog and drafted the goal; then achieve for the goal
  lifecycle, impl for each slice's code, quality for the bundle-boundary gate and
  the dup ratchet, critique for all five bounded review rounds, issue for the
  filing the retro's sibling scan produced, and retro for closeout. Chosen from
  installed skill metadata and the repo's Work Phase Map, not an inline
  phase-to-skill table.
- Release: n/a — this goal cut no release. It CHANGED release verdict logic
  (`current_release.py`, `publish_release_preflight.py`, a new adapter field), and
  those changes are proven by the release test modules and the bundle quality gate,
  but no version was bumped, no manifest was published, and no tag was cut. The next
  release will be the first to carry the new publish refusal.
- Gather: n/a — no external source was consulted; every input was repo-local
  (the deferred-decisions record, the sweep audit, the scripts under review).
- Issue closeout: n/a — this goal resolved no tracked issue. It OPENED one
  ([#468](https://github.com/corca-ai/charness/issues/468)) from the retro's sibling
  scan, which is a filing, not a closeout.

## Final Verification

**Self-verification, with what each command actually returned.**

- Bundle quality gate `./scripts/run-quality.sh`: **82 passed, 1 failed, 707.0s.**
  The single failure was `check-changed-line-mutation-coverage`, naming five files
  with uncovered changed lines. Four were this goal's and are now covered; the
  fifth, `inventory_ci_local_gate_parity.py`, is INHERITED — the gate's default
  base is the last pushed commit, and `7efa0240` from an earlier session changed
  it. Re-run scoped to this goal's own base (`8c3b3446`), the inherited file
  correctly disappears and exactly one line remained,
  `inventory_measurement_lib.py:99`, which the final slice covered. The confirming
  re-run after that slice returns `"ok": true` with `"blocking_targets": {}`.
- Targeted suites: 6570 collected repo-wide; the touched families all green —
  handoff/chunker 138, release+absent-input 122, inventory/declaration 320, the
  new measurement-lib module 10.
- `check_dup_ratchet.py`: OK, `fixable_ceiling=0`. It fired FOUR times during the
  run, at the first edit to a gated file each time, and each firing produced a real
  extraction (`forward_carried_keys`, `entries_from_pipeline_payload`,
  `cited_inventories`, `inventory_measurement_lib`) rather than a late hard-block.
  Five families were classified `intentional` against named precedent; one was
  recorded as a fingerprint rotation.
- Executed before/after proof for D48 on a scratch worktree, not asserted: with the
  codex `plugin.json` deleted AND the four declaration lines removed, the
  pre-slice script returned `drift: []` — a clean publish verdict over a missing
  surface — while the current one reports `absence_corroboration: uncorroborated`
  and the publish blocker fires. A present-but-truncated `plugin.json` with no
  declaration went from `drift: []` to `drift: ['codex_plugin=<unreadable>']`.
- Executed measurement for D47, recorded at
  [2026-08-01-inventory-marker-rule.json](../probe/2026-08-01-inventory-marker-rule.json)
  and pinned against the live tree.
- Boundary integrity: five `reviewer_boundary_fingerprint` windows opened and
  verified, all `clean`, no drift.

**Non-claims.** No `git push`, no remote CI dispatch, no `cautilus evaluate`, no
release publish, no version bump. Every verdict here is local. None of the three
refusals was armed. The D48 publish refusal has never run against a real publish —
it is proven by tests and by a scratch-worktree reproduction, not by a release.
`publish_release_resume.py` still reaches `create_release` with no surface check.
The D47 measurement's remaining false positives are verified inert on today's
corpus, not repaired.

Retro: charness-artifacts/retro/2026-08-01-three-unarmed-refusals-retro.md
Host log probe: skipped: host-log-not-exposed: the Claude session log exposes
thread-wide token snapshots, function calls and subagent spawns, but this goal
carries no `Host metric window:` line, so no per-goal scoped total can be derived
and the thread-wide figures are pressure, not this goal's cost.
Disposition review: charness-artifacts/retro/2026-08-01-three-unarmed-refusals-retro.md

## User Verification Instructions

1. **Read the three decisions and what changed.** `docs/deferred-decisions.md`
   D46, D47, D48 — each now carries the 2026-08-01 operator call, what shipped,
   what stays deferred, and a `Withdrawn, do not retry` note where the entry's own
   named remedy turned out to be unbuildable.
2. **Reproduce D48's closure yourself:**

   ```bash
   git worktree add /tmp/d48 HEAD && rm -f /tmp/d48/plugins/charness/.codex-plugin/plugin.json
   python3 -c "import re,pathlib;p=pathlib.Path('/tmp/d48/.agents/release-adapter.yaml');p.write_text(re.sub(r'required_release_surfaces:\n(- \w+\n)+','',p.read_text()))"
   python3 skills/public/release/scripts/current_release.py --repo-root /tmp/d48
   ```

   Expect `absence_corroboration: "uncorroborated"` with `drift: []` — the
   read-only call stays free, and the refusal is at publish.
3. **Re-run D47's measurement:**
   `python3 scripts/measure_inventory_marker_rule.py --repo-root .` — expect 5
   refused citations across 4 artifacts, matching the recorded probe.
4. **Check the review record:** the goal's `## Plan Critique Findings` and each
   slice's `Critique` field name what every round found, including the three
   findings that were about my claims rather than the code.

## Auto-Retro

Full retro: [2026-08-01-three-unarmed-refusals-retro.md](../retro/2026-08-01-three-unarmed-refusals-retro.md).

The run's dominant waste was building three things that had to be reverted, all in
slice 2 — lane inference, planner routing, the resume gate — each refuted by a fact
readable in one command before building. The run's most consequential finding was
that three of five review rounds caught defects in a CLAIM rather than in code: a
string-replace "repair" that silently never applied, a units swap that made two
different numbers look like agreement, and a comment asserting a branch was live
beside a probe recording zero.

Retro dispositions: applied: an in-process `main()` test path for the marker
measurement, so a render path proven only by subprocess stops reading as uncovered
to the changed-line gate; applied: the shared exemption ladder's four states are
now driven directly rather than left to a corpus that exercises one; applied: both
inventory declaration fields now warn on an unreadable name, so a discarded typo is
diagnosable; issue #468 for the transferable pattern.
Structural follow-up: issue #468 (novel: no prior entry records that a durable
record's named remedy is stored as prose and never re-verified against the channel
it reads; D47 and D48 are the first two measured instances, and D45 is the
unverified candidate).


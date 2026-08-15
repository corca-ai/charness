# 6.0.0 Release Scope

Status: in-progress
Date: 2026-08-15
Source: docs/handoff.md `## Next Session`, open issues #527-#632, owner scope
decision recorded in this session (wide scope, all four themes in one release).
Revision 2 — repaired from a bounded three-angle review plus counterweight; the
rulings are in `## Critique`.

## Problem

Shipped is `5.2.0`. `6.0.0` was prepared on 2026-08-14 and never published, and
the 2026-08-15 `--json` removal landed on top of it (`eae80f660`).

1. **The prepared release notes are false for the tree they would ship.** They
   say *"twelve public skill scripts still declare `--json`, and that is the
   convention"* and *"do not read this as 'the flag is gone repo-wide'"*.
   Measured on `eae80f660`: **zero** scripts declare their own `--json`.
   Remaining spellings are `gh --json` pass-through arguments, one `--json-path`
   in [proof_receipt](../../scripts/proof_receipt.py), and one suppressed
   `--json-out` in
   [inventory_doc_duplicates](../../skills/public/quality/scripts/inventory_doc_duplicates.py)
   — an inventory this contract's first revision itself got wrong, which is the
   class in miniature. A consumer following these notes under-migrates. The notes were
   repaired for four false claims on 08-14 and were stale again within one day.
2. **Nothing checks a release note against the tree it ships.** The existing
   narrative machinery (`audit_public_release_narrative.py`,
   `publish_release_narrative_gate.py`) checks artifact STRUCTURE — required
   headings — not claim-versus-tree. So problem 1 has no detector, and repairing
   the prose by hand is the move that has now failed twice.
3. **Fixes are stranded behind the publish.** #618-#627 are fixed in-repo and
   still reproduce for their reporters, because nothing installable changed.
   #608 belongs in this bucket too: it was filed 2026-08-12 and the claims-review
   pause it asks for shipped on 08-13/08-14. Their closability depends on the
   publish, not on more repair.

The owner chose the wide scope: the remaining live defect classes ship in the
same release rather than in a follow-up.

## Capability Contract

A maintainer publishes one `6.0.0` whose notes are **derived from the tree being
shipped** and held by a gate rather than by a reviewer's attention, through the
prepared-stop / claims-review / resume path that already ships. The release
carries the live defect classes still open after the migration: producer
scaffolds that overwrite another subject's record, the non-functional lesson
loop, the unheld docs-graph bar, the structural verification gaps, and two
operating-contract rules the session's own incidents earned. After publish,
issues #608 and #618-#627 close against executed proof.

## Current Slice

The whole release, sequenced S1-S7 below. Each S is its own commit and its own
`impl` -> `prove` closeout; the release executes only after S1-S6 are green.

## Sequence

Ordering is by dependency pressure, not by theme.

- **S1 — tooling that later slices are measured by.** #599 (`what-reads-this`),
  because every later slice deletes or rewires something. **And the release-notes
  generator plus its notes-versus-tree gate — built here, run at S7.** Those are
  two different times and the first revision of this contract conflated them:
  "notes go stale if authored early" constrains when they are GENERATED, not when
  the generator is WRITTEN. Written at S1, every later slice lands under it and
  the claim surfaces are captured as they change; written at S7, it would
  enumerate six slices' worth of claim surfaces from memory — the same
  false-completeness class it exists to prevent. Also #630 (`npm exec --no`).
- **S2 — the producer-scaffold class.** A scaffold resolving `write_artifact_path`
  to a record belonging to a **different subject than the invocation**. Three
  recorded instances: `quality` (#620), `debug` (#628), `retro`. See the Fixed
  Decision below for why the mechanism is subject identity and not date
  coherence.
- **S3 — lesson loop. BUILT 2026-08-15; two-round review in progress.** Refresh
  the #617 spec and close its debug interrupt, then the score outcome vocabulary,
  #631, #626, #627. (An earlier revision of this line said "DELIVERED" while
  round 1 was still open — a bounded reviewer flagged asserting completion in the
  governing contract ahead of the constraint that governs it.)
  Correction measured during the slice: the #617 capability shipped in
  `311844e23`, not `eae80f660` — the latter contains it but is the `--json`
  removal. `git log -S "def bundle_path"` is the check; the false attribution
  came from this contract and would have reached the release notes' commit
  citations unchallenged.
  What the slice found that the plan did not predict, stated as MEASURED rather
  than as first written: `archive_fallback_uncertainty` was hardcoded to `0` in
  selection policy v2, which REGRESSED the tenth presentation slot. Eleven
  snapshots show it — ten committed at HEAD plus this slice's own, still
  uncommitted. Four are `selection_policy_version: 1` and each carries
  `archive_fallback_uncertainty: 1` with ten `lesson_ids`; seven are v2 and carry
  `0` with nine. (Round 2 caught the word "committed" doing work it had not
  earned here, on a surface where `committed` means `git show HEAD:` elsewhere in
  this very repo.) A first draft of this entry claimed the slot "had never been
  filled by ANYTHING" for "the entire life of the ledger"; a bounded reviewer
  refuted it from those snapshots, and the same false sentence had reached four
  surfaces including this contract. It is the release's own defect class,
  committed inside the release that exists to stop it. The `archive` bucket
  proper HAS always been 0 — that part was true and is what #626 reported.
- **S4 — docs graph. BUILT 2026-08-15; two-round review in progress.** #629 at
  the handoff scaffold, then this repo's own `link_only_lines` count, then make
  `check_docs_graph.py` gate it. Re-measure before sizing the rewrite;
  `python3 scripts/check_docs_graph.py --repo-root .` and
  `awiki lint -root docs -recursive` both report the current figure, and every
  count checked into an older artifact disagrees with it. **Correction measured
  during the slice: those are NOT two independent channels.** The gate shells out
  to awiki and regex-reads its summary line, so it is the same observer read
  twice — the shape P4 refuses — and this contract's own revision said otherwise.
  A round-1 reviewer caught the same false sentence after it had been copied into
  the gate's source comment and into `docs/docs-graph-checks.md`. This is not the
  one-clause edit the first revision implied; see the Constraints entry.

  What the slice found that the plan did not predict, stated as MEASURED: the
  findings are two populations, not one. Reading each flagged source line put the
  list entries whose link line carried no descriptor in one group and links that
  landed alone inside hard-wrapped prose in the other, at roughly a third and two
  thirds. The first group was repaired; the bar is sized to the second, which is
  the population awiki's per-physical-line rule over-reports on. Both counts are
  scoped to what awiki flags — it models markdown pages inside its root, so a
  list entry whose only link is an external URL is in neither.

  **SCOPE EXTENSION, recorded rather than inferred from the diff.** The contract
  scoped the issue work to "#629 at the handoff scaffold", and the slice also
  added a blocking rule to `scripts/validate_handoff_artifact.py`: a
  `## References` entry must carry a descriptor on the link's own physical line.
  Reason: the scaffold placeholder alone does not bind — an author who deletes
  the TODO line is back to the shape #629 reports, and closing #629 on a
  placeholder would assert behavior the tree does not have, which
  `## Non-Goals` forbids. It is owned by SC13 below rather than left uncovered.
  It is also a BREAKING CHANGE for consumers: a `docs/handoff.md` that was legal
  in `5.2.0` and carries a bare `## References` link now fails the validator on
  upgrade. S7 must carry it in the release notes; the notes generator derives
  registered claim surfaces, and a new blocking validator rule is exactly the
  "claim surface nobody thought to derive" the Known Weaknesses name.

  **S4 review record.** Two rounds, three angle reviewers then two, all
  `parent-delegated` and read-only, on windows `s4-docs-graph-r1` and `-r2`; the
  r1 `reviewer_boundary_fingerprint verify` returned `parent-attributed` with
  every drift path declared, so no approval is quarantined. Round 1 found the
  unsynced export mirror, the false two-channel claim, an absence-of-one-metric
  branch that discarded another metric's observed failure, and a ratchet with no
  executable form. Round 2 read the repairs and found defects IN them — the
  ratchet's first fix was satisfiable by two in-place edits, the completeness
  guard could be narrowed to nothing through its own signature default, the
  `## References` scan ran to end of file rather than to the next heading, and
  one repaired sentence still presented an inferred claim as measured. Round-2
  repairs are **accepted-unreviewed** at the two-round cap.

  Carried, not fixed: the exported gate ships this repo's calibrated bar with
  neither the ratchet record nor the test that governs it, and its remedy text
  cites paths absent from an installed plugin. `--link-only-lines-bar` makes a
  consumer's own bar expressible; whether a repo-calibrated threshold should ship
  as a DEFAULT is left open rather than decided inside this slice.
- **S5 — structural umbrellas.** #586, then #584, #583, #582.
- **S6 — operating contract. BUILT 2026-08-15; two-round review in progress.**
  All four items landed. What the premise check changed, and what the slice
  measured that the plan did not predict, both recorded here rather than left in
  the diff:

  **The premise check narrowed SC11 and it was the largest correction.** The
  plan reads "the monitored-phase path for long-running children" as work to be
  built. It already ships: `scripts/subprocess_guard.run_monitored_phase` has
  three production callers, and the 2026-08-14 retro records that a first draft
  of it was a NEW `monitored_run.py` deleted for near-duplicating the existing
  owner. What was missing was not the path but its use at the one place that
  most needed it: `scripts/run_standing_pytest.py:467` ran the repo's LONGEST
  child on a bare `subprocess.run` — no session, no heartbeat, no group kill —
  which is exactly how two full-suite runs were lost to wrapper timeouts. So S6
  wires the existing owner rather than building a second one. Had the premise
  check not run, this slice would have shipped the duplicate the previous slice
  already deleted once.

  **A naive conversion would have been a regression, and the acceptance envelope
  is what caught it.** `run_monitored_phase` PIPES the child's output; pytest
  renders live progress across a multi-minute run. Swapping the call would have
  traded a watchable suite for a silent one — the same defect the guard's own
  docstring records the release helper committing in the other direction. The
  module docstring had already NAMED this as the third caller choice it
  deliberately did not solve; S6 solves it as `capture=False` on the existing
  primitive, keeping one owner. `timeout_seconds` stays `None` by default: the
  recorded loss was an untracked tree, not a missing bound, and a bound short
  enough to catch a hang is short enough to kill a healthy run.

  **SC11's second half is a run record, because monitoring alone does not reach
  it.** The heartbeat proves liveness to whoever is watching. When an agent's
  wrapper dies the transcript dies with it, so the outcome has to outlive the
  caller: `.charness/standing-pytest/last-run.json` <!-- reproduction-source -->,
  read back with `python3 scripts/run_standing_pytest.py --print-last-run`. The
  path is deliberately gitignored per-run local state, not a checked-in proof
  artifact — a record of the last run on THIS machine is not evidence about the
  repo. Best-effort by construction — telemetry must never be why a suite fails.

  **The exported-bar work grew one step past the ruling, recorded rather than
  inferred from the diff.** The ruling said source the bar from the ratchet
  record and fall to 0. Doing that left charness's own measured numbers (255,
  88, 167) written in prose inside the exported gate — which a test written for
  this slice caught, not a reviewer. The measurement narrative moved into the
  (unexported) record and the gate keeps the METHOD. Also recorded as a cost the
  ruling did not name: sourcing the bar removes one of the three edits a raise
  used to need, so the ratchet is one step shallower than S4 left it. Said in
  [docs-graph-checks.md](../../docs/docs-graph-checks.md) rather than left for a
  reader to discover.

  **What the suite caught that local tests did not.** The runner's new import
  broke the seeded quality-runner fixture (34 failures) and failed under
  `coverage run` from a foreign cwd (`coverage run <abspath>` puts the CWD on
  `sys.path`, not the script's directory). Both were repaired at the seam rather
  than by stubbing: a stub would have let the runner fall back to an unmonitored
  child with the harness still green.

  **SC10's proof is split by construction and the split is not a gap.** The
  suite proves what a CHECKOUT is; only a live probe can prove where a SPAWN
  went. Recorded at
  [2026-08-15-sc10-write-capable-worktree-isolation.json](../probe/2026-08-15-sc10-write-capable-worktree-isolation.json),
  which also states what it does NOT establish — including that the observed
  agent worktrees came from isolation-REQUESTED spawns, so a default spawn still
  shares the parent tree and the read-only hygiene rule still stands.

  **S6 review record.** Two rounds, four angle reviewers then two, all
  `parent-delegated` and read-only, on windows `s6-operating-contract-r1` and
  `-r2`; both `reviewer_boundary_fingerprint verify` runs returned
  `verdict: clean`, so no approval is quarantined. Round 1 returned two blockers,
  each of which INVERTED its item's intent: the standing runner's new session put
  the pytest tree outside any enclosing guard's process group (the runner is
  normally nested, so an outer timeout would have orphaned the tree it was meant
  to track), and `is_isolated_worktree` compared paths rather than indexes, so a
  subdirectory of the main worktree reported "isolated" while sharing the
  parent's index. It also found the exported docs-graph ratchet had become
  WEAKER for consumers — monotonicity lived only in a non-exported test — and
  that this slice's own "the bar appears nowhere in exported source" test would
  have fired on the ratchet's success direction.

  Round 2 read the repairs and found two more, both the fixed class recurring
  inside its own fix: the #633 repair moved the counter correctly but left a test
  docstring naming `completed_evaluation_count` beside assertions that did not
  check it (the refuted code still passed them — measured), and the isolation
  flag, newly given a production caller, was discarded on the `--prepare` path
  this contract names as the mechanism. Round-2 repairs are
  **accepted-unreviewed** at the two-round cap, and so is the write-capable-spawn
  rule added to `AGENTS.md` under the owner ruling below, which landed after the
  round-2 packet closed.

  Carried, not fixed: `ratchet_rows` enforces monotonicity over the rows PRESENT,
  so a consumer who rewrites the record to a single high row is accepted — the
  founding-row anchor that stops that for charness is a test, and tests are not
  exported. An outer SIGKILL still orphans the pytest tree by construction. Both
  are stated at their surfaces rather than left to be discovered.

  **Owner ruling 2026-08-15 (S6 closeout): SC10 CLOSES with a spawn-side rule.**
  The checkout-level mechanism ships as built, and `AGENTS.md` gains the
  instruction that write-capable spawns request their own worktree wherever the
  host offers one. Recorded as an instruction, not enforcement: charness cannot
  control host spawn placement, and the probe records what the host actually did
  rather than what was asked. **And: the gate-enforced ratchet monotonicity
  STAYS**, though it exceeds the literal text of the exported-bar ruling — it is
  covered by the no-grace-period ruling, and S7 owes it a release note because a
  consuming repo whose record rises is newly refused on upgrade.

  Original scope follows.

  **Worktree ISOLATION for write-capable subagents**
  (owner ruling 2026-08-15: "격리 잘 시키고"), replacing the retired
  no-mutating-git framing; plus a monitored-phase path for long-running children.
  S4 exercised the exposure this addresses: five write-capable subagents ran
  concurrently in the shared worktree under a prompt sentence forbidding mutating
  git ops — a prose rule, not enforcement. The read-only side is already covered
  on this host, since the `bounded-reviewer` type carries no Bash. Also carries
  the exported-bar default from the rulings below. **Plus
  [#633](https://github.com/corca-ai/charness/issues/633)** (owner ruling,
  2026-08-15): a disposition spelling `session_id: "none"` under any status other
  than `missing-start` parses, increments `completed_evaluation_count`, and skips
  every reconciler check. Pre-existing, found by an S3 bounded reviewer, and
  folded here rather than into S3 because repairing it changes the disposition
  GRAMMAR — a different proof surface than S3 touched, and S3 was already at its
  review cap. It lands before S7 so the release does not publish a lesson-loop
  gate with a known bypass while closing the lesson-loop issues that rest on it.
- **S6b — cost as a proof surface** (owner ruling, 2026-08-15, in this release).
  MEASURED during S5 and the reason this slice exists: `scripts/run_standing_pytest.py`
  runs the suite with xdist in **84s** (9403 tests) over **567 of 567** test files —
  zero uncovered — is budgeted (`pytest: 97500` on this profile) and BLOCKS via
  `check_runtime_budget.py`. The handoff instead prescribes
  `python3 -m pytest tests/ -q --no-header`, which takes **~22 minutes** for the same
  scope. **14.7x, and the fast path already existed, was measured, and was enforced.**
  S5 paid that cost three times without questioning it, because the handoff records
  "~22 minutes ... Budget it per slice" — a cost stated as a constant of nature rather
  than as a bar with a direction.

  The gap is NOT missing cost measurement. Measurement exists, is tuned, and blocks.
  Three things are missing, and each is the same shape as a defect this release already
  fixed elsewhere:

  1. **Nothing refuses a document that prescribes a command outside the measured
     universe.** `check_runtime_budget_universe` asks budget -> universe ("does every
     budgeted label exist"), never universe -> prescription ("is the expensive thing we
     tell sessions to run budgeted at all"). Same one-directional defect S5 repaired in
     the parity gate's `absent_by_design` check.
  2. **`validate_handoff_artifact.py` already blocks and already refuses prose** — it
     carries `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES` — so a superseded-command registry is
     the same mechanism in the same file, not new machinery. A bare-pytest regex is
     already checked in at `.agents/quality-adapter.yaml:23` for a different purpose.
  3. **No review angle asks about cost.** The handoff DID get fresh-eye review. The
     instruction passed because it is TRUE: that command really does re-prove the suite
     and ~22 minutes was really measured. Every angle this repo ships
     (`implementer-misread`, `overstated-acceptance`, `hidden-sequencing`) asks whether a
     claim matches the tree. None asks whether a dominated path was chosen. A dominated
     instruction is not a false one, so nothing caught it.

  **Consumer-facing half, which is the larger half.** What the quality skill exports
  today is the BUDGET apparatus (`check_runtime_budget.py`, `runtime_budget_lib.py`,
  `runtime_profile_lib.py`, `render_runtime_summary.py`), not the fast RUNNER. A
  consuming repo that simply runs `pytest` inherits the ledger and none of the speed, and
  nothing tells it so. The exported surface must either scaffold a standing-runner
  equivalent or render the verdict "the command your docs prescribe is outside your
  measured universe".

- **S7 — release execution.** Breaking changes S7 owes a release note, collected
  here so they are not re-derived from six slices of memory: the `## References`
  descriptor rule (S4/SC13), and from S6 the docs-graph gate's exported
  `link_only_lines` default of 0 plus its new refusal of a ratchet record whose
  bars rise — a consuming repo that inherited charness's 167 now inherits 0, and
  one whose record is non-monotonic is refused on upgrade. Both are exactly the
  "claim surface nobody thought to derive" the Known Weaknesses name.
  Reword the 8 blocking quantities the S1 lint finds
  in the prepared notes that have no registered claim surface to move into
  (owner ruling, 2026-08-15: reword rather than expand the registry — an ad-hoc
  quantity like "three coupled edits" is not derivable in principle, and a
  quantity nobody counted is the thing the mechanism exists to stop being
  written). Then write the classification ledger and commit it
  **before** the prepared release record. Run the S1 generator over the final
  tree, gate the notes, run the release critique (which the release skill places
  before the bump), `--execute` to the prepared stop, commit the claims-review
  artifact as the direct child of that record, `--resume` to publish, then close
  #608 and #618-#627.

## Fixed Decisions

- **The release notes are a derived surface, generated at S7 by a generator built
  at S1, and held by a gate.** The gate proves *notes == derivation*; it does not
  prove *derivation == truth*. That residual is real and stated rather than
  papered over. What the gate does catch is the recorded failure mode: notes
  committed at one time and contradicted by the tree at publish time, plus any
  hand-edit after generation.
- **The gate must fail in the OVER-claim direction, which is the direction that
  actually failed.** A check that only detects surfaces the notes fail to mention
  cannot see "twelve scripts still declare `--json`" written over a measured
  zero, because that sentence mentions the surface. The first revision specified
  only the omission direction and was therefore inert against its own Problem 1.
- **The authored narrative is contained, not trusted.** The false claims lived in
  authored prose, so exempting prose from derivation exempts the exact surface
  that failed. **Two severities, amended by owner ruling on 2026-08-15 after S1
  measured the original clause.** A bare QUANTITY — a digit run or a cardinal
  number word — is forbidden in the authored narrative outside a transclusion
  marker, and BLOCKS publish. The completeness words `only`, `all`, `every`,
  `none`, `still`, `repo-wide` are reported as ADVISORY and do not block.

  What overturned the original "all six are forbidden" clause: run against this
  repo's own `charness-artifacts/release/2026-08-14-v6.0.0-notes.md`, the
  refusing version produced 49 findings, among them
  *"...verified only after the release has been published"* from that note's own
  `## Evidence limits` and *"...can opt into the lesson lifecycle at all"*. A rule
  that refuses the wording which makes a note honest is one an operator disables,
  and the only disable available also disarms the derived-block arm that has a
  real recorded failure behind it. Number words stay in the BLOCKING arm because
  the recorded false sentence spells its quantity as `twelve`, so a digit-only
  rule would be inert against its own instance.

  Still a regex-shaped lint with an obvious negative case, not a prose parser.
  Building a prose claim-extractor is rejected: inside a release slice it produces
  an inert or unfalsifiable guard, and the human-reviewed claims list it would
  duplicate already ships as the claims-review pause.
- **The producer-scaffold class is fixed by SUBJECT IDENTITY, not date
  coherence.** The class is real and has three instances, but the mechanism named
  in revision 1 was wrong twice over. It is **inert** against #628: the
  overwriting artifact carries today's date under today's filename, which is
  precisely why #628 argued it is not #620 recurring. And it would **false-refuse
  correct behavior**: `scripts/scaffold_artifact_lib.py:167-169` records as a
  deliberate fact that "whether overwriting is acceptable differs by skill
  (`debug` continues an open investigation in place; `quality` must never
  overwrite a finished review)", and `scripts/validate_quality_artifact.py:532-538`
  records that the quality disposition "does NOT transfer, and re-deriving it
  here would reproduce #620". So: `scaffold_artifact_lib` gains a subject-identity
  FACT alongside its existing `write_target_facts` — does the existing target's
  subject key match the subject this invocation is for — and each family consumes
  it with its own key and its own policy. `debug` continuing its OWN open
  investigation stays a passing case. The quality date-coherence check stays
  family-scoped where it is.
- **#608 is not build work.** The pause it asks for ships:
  `skills/public/release/scripts/publish_release_execute.py:305-323` stops at
  `prepared-awaiting-claims-review` and never tags, pushes, or creates the
  release; `publish_release_resume.py` and `publish_release_claims_review.py`
  implement the resume;
  [test_release_publish](../../tests/quality_gates/test_release_publish.py)
  asserts an `--execute` run publishes nothing. It is fixed-and-unreleased, and closes at
  S7 with the rest. Revision 1 asserted the opposite from the issue text without
  reading the source — recurrence of `premise-not-checked-against-source`, the
  lesson this session was served at open.
- **The classification ledger commits before the prepared release record.** The
  claims-review artifact must be the direct child of that record with nothing
  else riding along (`publish_release_claims_review.py:387,432`), so the window
  between the prepared stop and the claims child is closed to other commits.
- **The `link_only_lines` bar is a ratchet.** It may only decrease without a
  recorded decision. Without that clause a slice can measure the count, declare
  the bar equal to it, and satisfy the criterion with zero work.
- **#626/#627 are redefined to their title scope and resolved in this release**
  (owner decision), and therefore close only if S3 delivers them.
- **The bump is major**, and `plan_release_run.py --part major` already computes
  `6.0.0` from `5.2.0` with `blockers: []`.

## Probe Questions

- **What is the smallest honest slice of #582/#583/#584?** All three are
  umbrellas whose members are CLOSED and whose class is declared LIVE. Probe:
  land one executable guard per umbrella, measure what it catches on the current
  tree, defer the rest with the measurement attached.
- **Is `link_only_lines` 0 reachable without damaging the docs?** Probe the
  twenty worst lines first. If the rewrite reads worse, the honest outcome is a
  ratcheted bar above 0, recorded with its rationale.
- **Does lifecycle promotion still belong to `quality`?** The 2026-08-12 ledger
  spec assigns it there and it was never wired. Confirm before wiring #626.
  `## Boundary Ownership` records the current assignment and its source; it is
  not a ruling that this probe is closed.
- **Does #612 survive `eae80f660`?** Its cited survived mutants are
  `print(json.dumps(...))` lines the migration deleted. Re-measure.

## Deferred Decisions

- **#527** (per-skill human-readable docs, maturity buckets, invocation locks) —
  a product-shape change, not a defect.
- **#528**, **#546** — real adapter/gate-honesty defects, cheap, and the first
  things to cut if S1-S6 runs long.
- **#550** and the ledger write transaction shared by four writers
  ([dup-review](../quality/dup-review.json) family `d3fea2dbc2463d22`) — refactors
  with no user-visible defect behind them.
- **#601**, **#605**.

## Non-Goals

- No new host support, no Cautilus evaluation, no push/tag/publish outside S7's
  explicit grant.
- No migration shim or `--json` deprecation window; that was executed in
  `eae80f660`.
- No prose claim-extractor for release notes.
- Not closing #628/#629/#631/#626/#627 unless S2/S4/S3 actually deliver them; a
  close asserts behavior, not intent.

## Deliberately Not Doing

- **Not repairing the 6.0.0 notes by hand.** That is the move that failed twice.
- **Not building a second claims-review pause.** One ships.
- **Not generalizing the quality date-coherence check across families.** It is
  inert against #628 and destructive to `debug`.
- **Not shipping the release before S6.** The owner chose wide scope with the
  stranded-fix cost stated and accepted.

## Constraints

- `mutate -> sync -> verify -> publish`. Slices touching exported source run
  `sync_root_plugin_manifests.py` before validators and stage the mirror.
- Verification claims use cache-free commands. Measured 2026-08-15: `ruff check .`
  was green while `ruff check --no-cache .` reported 180 `I001` — a false green
  that reached a checked-in retro as "Ruff clean". **Those repairs landed in
  `eae80f660`**; both `ruff check --no-cache .` and the narrower gate scope in
  [check-python-lint](../../scripts/check-python-lint.sh) are clean as of this
  revision, so S1 arms a flag over a green path, not a red one.
- **S4's docs-graph work is larger than "assert the count it already parses".**
  Written before the slice and left in the past tense it was measured in; the
  line numbers below are the PRE-SLICE tree, and reading them as live claims is
  what made this bullet worth re-tensing. The gated set WAS `GATED_METRICS` at
  `scripts/check_docs_graph.py:52`, not the docstring at `:12-18`. Adding a
  metric there without four other edits broke the gate:
  `BLOCK_FOR_METRIC[metric]` at `:248` raised `KeyError` swallowed into NOT-RUN
  by the blanket `except Exception` at `:184`, and `_UNREACHABLE_LABEL`/`_REMEDY`
  at `:296-297` were called from `main` at `:316` outside that guard and crashed
  uncaught. `:239` also computed failures as `> 0`, which is not a bar. And S4
  **reverses a deliberate decision**, not an oversight:
  `tests/test_docs_graph_gate.py:168`
  `test_link_only_lines_alone_do_not_fail_the_gate` was pinned at `:169-170` as
  "the deliberate scope decision, pinned so it cannot be widened by accident".
  Retract that rationale explicitly or the reversal is undocumented.
  **Delivered:** the bar is a required value, every failure path carries its
  block header, label, and remedy behind an import-time completeness guard, and
  the pin is retracted by name in the test file and in
  [docs-graph-checks](../../docs/docs-graph-checks.md). Two defects round 1
  found in the repair itself: the gate decided "some metric is missing" BEFORE
  judging the metrics awiki did print, so an observed over-bar count could
  resolve to a pass or to NOT-RUN; and "may only decrease" existed only in
  comments, leaving a red lane repairable by editing one literal. Present metrics
  are now judged first, and the bar is pinned to a dated ratchet record the tests
  parse. Round 2 then measured that the FIRST ratchet repair was itself weaker
  than the sentence describing it — with one row present, "never increases
  downward" is vacuous, so a raise needed two in-place edits and no test change.
  The founding row is now an anchor, the parse is bounded at the next heading,
  and the doc states what the mechanism actually buys. The retraction is written
  out by name in the test file; the docs page names the decision and the test it
  reverses.
- The full suite costs **~22 minutes** (9331 tests). Budget it per slice.
- Slices changing verdict logic on a proof surface owe the two-round bounded
  review: S1 (the notes gate), S2, S3, S4, S5. If the host blocks spawning,
  the honest record is `Critique: blocked <host-signal>`, and those slices reach
  S7 unproven rather than silently approved.
- Bounded reviewers run read-only in the shared worktree and never run index- or
  worktree-mutating git ops. Until S6, that is a detective control
  (`reviewer_boundary_fingerprint.py` snapshot/verify, a failed verify
  quarantines that review's approvals), not a preventive one.
- Push, tag, version bump, and publish each require an explicit phase-scoped
  grant at S7. A green gate is not one.

## Success Criteria

Each criterion names the slice that owns it. Coverage is asserted in
`## Slice Coverage`.

1. **(S1)** `what-reads-this` answers for a symbol, a path, and a config key, and
   declares the surfaces it did NOT scan alongside a zero result.
2. **(S1)** The notes gate fails a publish plan whose notes over-claim against the
   tree, and names the disagreeing surface.
3. **(S1)** The authored narrative cannot carry a bare quantity — a digit run or
   a cardinal number word — outside a transclusion marker. The six completeness
   words are reported as advisory and do not block (owner ruling, 2026-08-15).
4. **(S1)** `check-markdown.sh`'s `npm exec` fallback does not reach the registry
   (#630).
5. **(S2)** No scaffold family resolves a write path onto another subject's
   record, and `debug` continuing its own open investigation still succeeds.
6. **(S3)** A lesson that is read and then works can be recorded as such without
   declaring a recurrence, and a session scoring lessons from two origin retros
   satisfies `check_lesson_evaluation_continuity.py`.
7. **(S3)** The archive/resurrection/graduation slot is reached from its
   production caller, and the check fails when that caller is absent.
8. **(S4)** `check_docs_graph.py` renders a real verdict — not NOT-RUN, not an
   uncaught crash — when `link_only_lines` exceeds its ratcheted bar, and this
   repo is at or under that bar.
9. **(S5)** Each umbrella has one executable guard with a recorded measurement of
   what it catches on the current tree, and a stated remainder.
10. **(S6)** A write-capable subagent cannot reach the parent's worktree or index,
    because it does not share them: a write-capable spawn runs in its own
    worktree. **REWRITTEN by owner ruling 2026-08-15**, from "cannot run a
    worktree-mutating git op ... is refused with the rule named". The refusal
    framing is retired, not weakened by accident, and the reasons are recorded in
    the ruling below so it is not re-litigated.
11. **(S6)** A long-running child is monitored rather than lost to a wrapper
    timeout.
12. **(S7)** Both #608 and #618-#627 read back `CLOSED` from the provider via
    `verify-closeout --expect-state CLOSED`, over a complete classification
    ledger committed before the prepared release record.
14. **(S6b)** A repo-owned document cannot prescribe a command that a registry marks
    superseded, and the refusal names the replacement. This repo's own handoff is the
    first subject.
15. **(S6b)** The runtime-budget universe check answers BOTH directions: a prescribed or
    queued expensive command with no budget is reported, not just a budgeted label with
    no command.
16. **(S6b)** A critique/review run carries a cost-dominance angle — "is there a cheaper
    path to the same evidence?" — and it is exported to consuming repos rather than
    living only in this repo's review prompts.
13. **(S4)** A `## References` entry in a handoff artifact cannot carry a link
    with no descriptor on the link's own physical line, and the scaffold emits a
    stub that satisfies that rule unedited. Added 2026-08-15 with the scope
    extension recorded in the S4 entry; the rule shipped before the criterion
    existed, which is the ordering this entry exists to stop being invisible.

## Acceptance Checks

- Verification type: unit — (SC1) `what-reads-this` over a fixture returns every
  reference for each of the three input kinds, and a zero result is accompanied
  by the declared unscanned-surface list. Negative: a reference living only in a
  surface the tool cannot scan is reported as unscanned, never as zero.
- Verification type: unit — (SC2) the generator, given notes that assert a
  surface the tree does not have, produces a diff naming it; **and** given notes
  omitting a surface the tree has, produces a diff; and given generated notes
  over the same tree, produces none. The over-claim case is the one that must
  exist — it is the direction that failed twice.
- Verification type: integration — (SC2) the gate fails a publish plan whose
  committed notes disagree with the tree at publish time, including the case
  where the notes were correct when generated and the tree moved after.
- Verification type: unit — (SC3) the narrative lint REFUSES a bare digit and a
  hyphenated compound number word outside a transclusion marker, accepts the same
  text inside one, and reports each listed completeness word as advisory without
  failing. Negative: an advisory alone does not refuse a publish, and the
  honest-limits sentence from this repo's own notes passes.
- Verification type: integration — (SC4) the markdownlint fallback runs with no
  registry access available.
- Verification type: unit — (SC5) for every family the scaffold registry
  enumerates — not a hand-written list — a write path onto a record whose subject
  key differs from the invocation's is refused. Negative: `debug` invoked for
  investigation X resolves onto X's own open record and SUCCEEDS.
- Verification type: unit — (SC6) an outcome of `worked` records with no
  `recurrence-class` tag present; the four-value vocabulary round-trips; an
  outcome with no anchor is refused.
- Verification type: integration — (SC6) a session with score events citing two
  origin retros passes the continuity check, and a genuinely foreign score still
  fails it.
- Verification type: integration — (SC7) the resurrection slot is exercised
  **through its production caller**, and the test fails if that caller is removed.
  A direct call to the slot is not acceptance for this criterion — that is the
  #586 shape S5 exists to fix.
- Verification type: unit — (SC8) the gate exits with a rendered verdict when
  `link_only_lines` exceeds the bar, and the bar is a required value in the gate
  rather than a comment. Negative: a metric added to the gated set without its
  `BLOCK_FOR_METRIC`, `_UNREACHABLE_LABEL`, and `_REMEDY` entries fails loudly
  rather than degrading to NOT-RUN.
- Verification type: manual — (SC9) each umbrella guard's recorded measurement
  and stated remainder are checked in.
- Verification type: integration + recorded probe — (SC10) `charness worktree
  doctor` reports a prepared, separate worktree for a write-capable author, and
  `reviewer_boundary_fingerprint verify` over a window containing such a spawn
  returns no UNDECLARED drift in the parent tree. Negative: the same agent's
  `git add`/`commit` inside its OWN worktree still succeed, so isolation is not
  achieved by taking the shell away. **What cannot be automated, stated rather
  than papered over:** the spawn itself is issued by an agent, not by a script,
  and probe `2026-07-10-issue-430` recorded `no host-exposed automated spawn-denial
  probe surface found`. So the spawn landing in a separate worktree is proven by a
  RECORDED LIVE PROBE per host, on the same standing as envelope binding and
  result delivery, never by a suite assertion.
- Verification type: integration — (SC11) a child exceeding the wrapper timeout is
  still tracked to completion and its result retrievable.
- Verification type: unit — (SC13) the handoff validator REFUSES a `## References`
  list entry whose whole line is a markdown link, accepts a descriptor after the
  link and a phrase before it, and reports every offending entry in one pass.
  Negative: a descriptor WRAPPED onto the following line is still refused — that
  is the case that distinguishes the same-line rule from a same-entry one, and it
  is the shape this repo's own handoff carried. Plus: the scaffold's emitted stub
  passes the real validator unedited.
- Verification type: unit — (SC14) the handoff validator REFUSES an artifact whose body
  prescribes a registered superseded command, and the message names the replacement.
  Negative: an UNregistered slow command passes — the registry is a denylist, so its false
  negatives are real and must be stated rather than implied away. Plus: this repo's own
  `docs/handoff.md` passes only after its `pytest tests/` line is replaced.
- Verification type: integration — (SC15) a queued or prescribed command with no runtime
  budget entry is reported by the universe check. Negative: the existing budgeted-label
  direction still reports a budget naming a label that does not exist.
- Verification type: manual + exported-surface — (SC16) the cost-dominance angle appears
  in the shipped critique surface, and a consuming repo running the quality skill is told
  when its prescribed test command sits outside its own budgeted universe.
- Verification type: manual — (SC12) `verify-closeout --expect-state CLOSED`
  reads back #608 and each of #618-#627 from the provider after the publish, and
  the classification ledger commit precedes the prepared release record.

## Slice Coverage

| Slice | Criteria | Notes |
| --- | --- | --- |
| S1 | 1, 2, 3, 4 | tooling; generator built here, run at S7 |
| S2 | 5 | subject identity |
| S3 | 6, 7 | lesson loop |
| S4 | 8, 13 | docs graph; 13 is the recorded scope extension |
| S5 | 9 | umbrellas; the probe question bounds it |
| S6 | 10, 11 | operating contract |
| S6b | 14, 15, 16 | cost as a proof surface; measured in S5 |
| S7 | 12 | release execution and closes |

No slice may close without its criteria; no criterion is without a check above.

## Boundary Ownership

The release helper owns bump/sync/verify/prepared-stop/resume/publish — including
the claims-review pause, which already ships. The notes generator owns derived
claim surfaces; the narrative lint owns containing the authored prose around them.
`scaffold_artifact_lib` owns producing the subject-identity fact; each scaffold
family owns its own policy over that fact. `lesson_evaluation_continuity_lib.py`
owns score-source agreement. Lifecycle promotion is assigned to `quality` by the
2026-08-12 spec — recorded here as the current assignment, pending its probe
question, not as a ruling. `check_docs_graph.py` owns the `link_only_lines` bar.
The repo operating contract owns the subagent git rule; S6 must name the concrete
mechanism that refuses (hook, permission rule, or typed agent definition) because
whether SC10 is satisfiable on a given host depends on that choice.

## Owner Rulings

- **SC3's completeness-quantifier clause: RULED 2026-08-15 — the two-severity
  split is approved and the contract above is amended to match.** Bare quantities
  block; the six completeness words are advisory. What follows is the evidence the
  ruling rests on, kept because the original clause was owner-approved and the
  reasoning for overturning it should not be reconstructible only from a diff.

  As built, `lint_release_narrative.py` BLOCKS on bare quantities — digits and
  cardinal number words, which is the class the recorded false sentence belongs to
  via `twelve` — and reports the six words as `bare-completeness-word` at
  `severity: advisory`.

  Evidence that produced the split, measured rather than argued: run against
  this repo's own `charness-artifacts/release/2026-08-14-v6.0.0-notes.md`, the
  refusing version produced 49 findings. Among them was
  `"Public release visibility and installed-host readback are verified only
  after the release has been published"` — from that note's own
  `## Evidence limits` — and `"...can opt into the lesson lifecycle at all"`.
  Refusing the wording that makes a note honest is a rule an author disables,
  and the only disable available is `require_derived_release_claims: false`,
  which also disarms the derived-block arm that has a real recorded failure
  behind it. After the split the same note yields 8 blocking findings, every one
  an unmarked quantity claim about the tree, and `twelve` still blocks.

  A bounded round-2 reviewer ruled this a deviation to be recorded rather than a
  defensible reading, and noted correctly that the implementer's "you would need
  a prose parser" defence was already pre-empted: the Fixed Decision itself calls
  for "a regex-shaped lint with an obvious negative case, not a prose parser".
  The owner ruling did not adopt that defence either — it rests on the 49-finding
  measurement, not on the parser argument. **S1 now meets SC3 as amended.**

  Residual the split does NOT remove, and the second ruling that addresses it:
  of the 10 blocking findings on the prepared notes, only 2 map to a registered
  claim surface (`twelve` and `five`). The other 8 are resolved at S7 by
  REWORDING, not by expanding the registry — see the S7 entry in `## Sequence`.
  One of the 8 is a quotation of a past wrong claim rather than an assertion
  (`"zero failing probes"`); rewording covers it.

- **The claim and containment arms are never reached by a `--generate-notes`
  publish**, which supplies no notes file. SC2 and SC3 bind notes that are
  handed over, not the publish. Belongs with the known weaknesses below.

- **RULED 2026-08-15 after S4: BREAKING CHANGES ARE ALL ALLOWED, WITH NO
  GRACE PERIOD.** Getting the behavior right outranks compatibility for this
  major. This covers the `## References` descriptor rule (SC13) and anything S5
  or S6 lands in the same shape. S7 still owes each one a release note — the
  ruling removes the deprecation window, not the disclosure.

- **RULED 2026-08-15 after S4: NO RETROACTIVE SWEEPS OF THIS REPO'S OWN OLDER
  DOCS.** Correctness applies going forward; a slice does not owe a pass over
  existing pages to bring them up to a rule it just introduced. Two consequences
  recorded so a later reader does not read them as oversights. First, S4's
  wrapped-prose residual under the `link_only_lines` bar stays as it is, and the
  bar is the mechanism that keeps it from growing. Second, the descriptors S4
  authored are accepted on SAMPLED verification — roughly half were checked
  against their targets by a bounded reviewer, plus parent spot-checks — and a
  full re-verification pass before publish is explicitly NOT owed. What IS owed
  is a verification step attached to future delegated authoring, because nothing
  in the gate checks whether a descriptor is TRUE; it only checks the line is not
  bare. Stated as a known weakness rather than a closed one.

- **RULED 2026-08-15: S5 lands ONE executable guard per umbrella, and #582 is
  narrowed to a single member.** Order: #586 (the vocabulary-parity check its own
  body proposes), then #584's two computations, then #583 — whose rule must be
  decided before the guard, since #568's deletion disposition was already
  retracted — then #582 scoped to **#525 alone**, because `docs/readme-proof.md`
  already defines the concepts and lacks only a validator that reads it. Every
  other member defers WITH the measurement of what its guard catches attached,
  which is the form SC9 already requires. Rationale: #582's own body says it is
  "not one PR", and taking it whole leaves #618-#627's fixes stranded for several
  more sessions.

- **RULED 2026-08-15: SC10 IS ISOLATION, NOT REFUSAL.** Write-capable subagents
  spawn into their own worktree; the parent's tree and index become structurally
  unreachable rather than policed. What the ruling gives up, said plainly: there
  is no refusal message. A mutating git op SUCCEEDS — in a throwaway tree where it
  harms nothing.

  The three refusal mechanisms were measured and each fails for its own reason,
  recorded so S6 does not re-open them. **The typed agent definition** cannot
  satisfy the criterion at all: it works by removing Bash, so the same agent
  cannot run the `git add`/`commit` the negative clause requires to succeed — and
  its binding is host-dependent, with probe `2026-07-10-issue-430` recording a
  session where the reviewer held Bash, Edit, Write, and Agent and a shell probe
  executed. It remains correct for READ-ONLY reviewers, where "no shell at all" is
  the stronger property, and it bound on both S4 review rounds. **A host
  permission rule** is not charness's to ship: the setup skill, presets, and
  profiles declare no settings or permissions surface, so it would live in
  unversioned host-local config and reach no consuming repo, while matching git
  command strings is evaded by `git -C`, an alias, or `sh -c`. **A git hook**
  cannot cover the named commands — `checkout` and `stash` have no vetoing
  pre-hook and `reset` has no hook at all, so the very operations the old
  criterion enumerated are the ones git gives no veto for.

  Isolation is also the only candidate charness already owns and exports:
  `charness worktree prepare`/`doctor` and `.agents/worktree-adapter.yaml` ship
  today. The detective control stays as the backstop for anything still sharing
  the tree — `reviewer_boundary_fingerprint` snapshot/verify, which S4 ran across
  both review windows.

- **RULED 2026-08-15: cost becomes a proof surface, and it ships in THIS release.**
  Owner decision after S5 measured the gap. The ask was raised as "why do these speed
  problems keep recurring, and why can't an agent find slowness strange on its own", and
  the measurement answered it: the fast path existed and the operating instruction pointed
  away from it. So the ruling is NOT "add cost measurement" — that exists, is tuned, and
  blocks. It is: **make a dominated instruction refusable, and give review an angle that
  can see cost.** Scoped as S6b above, landing before S7.

  Recorded so it is not re-litigated: the reason fresh-eye review did not catch the
  handoff's prescription is that the prescription is TRUE. Review is aimed at falsity.
  A dominated-but-true instruction passes every angle this repo ships, which is why the
  remedy is a new angle plus a deterministic registry, not more review of the same kind.

  Also recorded: the consuming-repo half is the larger one. The quality skill exports the
  budget apparatus and not the fast runner, so a consumer inherits the ledger without the
  speed and is told nothing about it.

- **RULED 2026-08-15: the exported gate's `link_only_lines` bar defaults to 0,
  and the work lands in S6.** A consuming repo must not inherit a threshold
  measured on charness's own docs tree. Implementation shape: source the bar from
  the ratchet record in `docs/docs-graph-checks.md`, which is NOT exported, and
  fall to 0 when the record is absent — this also removes the duplicated literal.
  It is verdict logic on a proof surface, so it carries the two-round review, and
  S6 is its home because S6 already touches proof surfaces.

## Critique

- Interrupt Source: `lesson-presentation-compaction-2026-08-14`
- Seam Summary: lesson-session rendered output to repo-owned retro verdict
- Chosen Next Step: impl (S3, first item)
- Impl Status: allowed
- Impl Status Reason: **superseded 2026-08-15 by the S3 entry above.** As
  written this said the #617 capability "shipped in `eae80f660`" and that the
  debug artifact's `Resolution: open` holds `plan_risk_interrupt.py` at
  `status: blocked`. Both are wrong. `git log -S "def bundle_path"` puts the
  capability in `311844e23` (`eae80f660` merely contains it). And
  `risk_interrupt_lib` never reads `Resolution` at all — only
  `validate_debug_artifact.py` does. The planner blocks when the spec handoff is
  absent from the slice's changed paths or its `## Critique` fields do not parse
  and match the debug seam; it reports `handoff-recorded` once they do, which is
  why `plan_risk_interrupt.py --repo-root .` with no `--paths` still reads
  `blocked` today. Round 2 caught the correction re-endorsing a causal model the
  code does not implement, which is the same class round 1 was called for. Kept
  rather than deleted so a reader sees the corrected claim beside its predecessor.
- What Disproving Observation Is Resolved: the observation that lesson
  presentation survives only in active context is disproved by a checked-in
  bundle written by the current code path.
- Contract critique: **run, and it changed the contract.** Three bounded
  read-only angle reviewers (implementer-misread, overstated-acceptance,
  hidden-sequencing) plus a counterweight pass, all `parent-delegated`, on
  windows `release-scope-2026-08-15-r1` and `-cw`; both
  `reviewer_boundary_fingerprint verify` runs returned `verdict: clean`, so no
  approval is quarantined. 40 findings, 23 consolidated: **7 blockers repaired**
  in this revision (false #608 premise; unowned notes generator; omission-only
  gate direction; exempted narrative; date-coherence mechanism inert against
  #628 and destructive to `debug`; direct-call proof of a "production caller";
  ledger inside the forbidden commit window). **6 ruled over-worry and
  deliberately not acted on**: the distinct-channel check (already enforced by
  `issue_verify_closeout_body.py`), #599-first as severity inversion, the S6
  guard's exposure window (detective control exists), Boundary-Ownership versus
  probe, the `bar-recorded-as-prose` citation, and a ratchet firing on later
  slices. The remainder are carried as stated open risks in Constraints and
  Probe Questions.

S3 round-1 findings carried forward rather than fixed, each with why:

- **`session_id: "none"` bypasses every reconciler check, and is PRE-EXISTING.**
  `_validate_disposition_value` pins `"none"` only for `missing-start`, but
  `"none"` also fullmatches the session-id pattern, so
  `{"status":"effect-recorded","session_id":"none","score_event_count":7}` parses,
  increments `completed_evaluation_count`, and `continue`s past every check.
  Confirmed pre-existing by
  `git show HEAD:scripts/lesson_evaluation_continuity_lib.py | sed -n '494,498p'`,
  which prints the bypass at line 496 of the then-543-line file. On the shipped
  tree the two halves live apart: the grammar pin in
  `scripts/lesson_evaluation_continuity_lib.py` `_validate_disposition_value`, and
  the bypass in `scripts/lesson_evaluation_reconcile_lib.py` `reconcile_records` —
  a module S3 created by splitting, which is why the HEAD citation needs its own
  command rather than a line number on a file that no longer has one. Filed as
  [#633](https://github.com/corca-ai/charness/issues/633). Repairing it means changing the disposition
  GRAMMAR, a different proof surface than the one this slice touched, and doing it
  inside a slice already carrying two review rounds is how a repair ships
  unreviewed. Filed rather than folded in.
- **A score event in a session that no retro claims and that has no in-window
  receipt is reconciled by nothing.** `_reconcile_retro_row` runs per claiming
  retro and `unclaimed_receipted_sessions` iterates receipts, so that combination
  falls between them. Also pre-existing; same reason.
- **`foreign-score-source` is presently inert on this repo's real corpus**, because
  all twelve committed score events are legacy-scalar and legacy events are exempt
  by design. It arms the moment the first outcome event lands. Stated because a
  green gate here currently proves less than it will.
- **The `changed-an-action` counterfactual bar publishes its own bypass tokens** in
  the refusal message, so the cheapest repair available to a refused author is to
  append the word "otherwise". Accepted for now — the alternative is a refusal that
  does not say what it wants — and the spec's ten-session falsification measurement
  should count how many counterfactual clauses are one of the fixture strings.
- **The schema migration was an ad-hoc inline recompute, not a checked-in command.**
  Acceptable because the recomputed fields are DERIVED and the validator refuses any
  `lessons` block disagreeing with replay, so it is idempotent and independently
  checkable; the append-only lists were untouched. What is missing is a trace, which
  is why the recompute rule is stated here and in the commit rather than left to a diff.
- **`score_total`'s dynamic range shrank ~3x** (±1 valences replacing ±1..±3
  magnitudes) while `_uncertainty`'s exploration term is unchanged, so exploration now
  weighs relatively more in selection than when it was tuned. No gate will flag it.
  Accepted and recorded rather than retuned blind.

Known weaknesses, stated rather than hidden:

- The notes gate proves *notes == derivation*, never *derivation == truth*. A
  claim surface nobody thought to derive is invisible to it.
- S5 is the least bounded slice; its probe question is the stopping rule.
- Revision 1 of this contract asserted a false premise about #608 from the issue
  text without reading the source, which is the `premise-not-checked-against-source`
  lesson recurring in the same session it was served. Three of four reviewers
  found it independently.
- Wide scope means the stranded fixes stay stranded for the length of S1-S6.

## Canonical Artifact

This file is the living contract for the 6.0.0 release scope. Per-issue contracts
stay in their own artifacts — the
[#617 durable lesson-session bundle](./2026-08-14-issue-617-durable-lesson-session-bundle.md)
and the [lesson score outcome vocabulary](./2026-08-14-lesson-score-outcome-vocabulary.md)
are canonical for their slices and are referenced, not restated, here.

## First Implementation Slice

S1, in this order: the release-notes generator and its over-claim gate plus the
narrative-containment lint (built now, run at S7, so S2-S6 land under it), then
the `what-reads-this` command of #599, then #630. Commit, then S2.

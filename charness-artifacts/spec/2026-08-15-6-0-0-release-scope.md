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
- **S4 — docs graph.** #629 at the handoff scaffold, then this repo's own
  `link_only_lines` count, then make `check_docs_graph.py` gate it. Re-measure
  before sizing the rewrite; `python3 scripts/check_docs_graph.py --repo-root .`
  and `awiki lint -root docs -recursive` are two independent channels that agree
  on the current figure, and every count checked into an older artifact disagrees
  with it. This is not the one-clause edit the first revision implied; see the
  Constraints entry.
- **S5 — structural umbrellas.** #586, then #584, #583, #582.
- **S6 — operating contract.** No-mutating-git for write-capable subagents; a
  monitored-phase path for long-running children.
- **S7 — release execution.** Reword the 8 blocking quantities the S1 lint finds
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
  The gated set is `GATED_METRICS` at `scripts/check_docs_graph.py:52`, not the
  docstring at `:12-18`. Adding a metric there without four other edits breaks
  the gate: `BLOCK_FOR_METRIC[metric]` at `:248` raises `KeyError` swallowed into
  NOT-RUN by the blanket `except Exception` at `:184`, and
  `_UNREACHABLE_LABEL`/`_REMEDY` at `:296-297` are called from `main` at `:316`
  outside that guard and crash uncaught. `:239` also computes failures as
  `> 0`, which is not a bar. And S4 **reverses a deliberate decision**, not an
  oversight: `tests/test_docs_graph_gate.py:168`
  `test_link_only_lines_alone_do_not_fail_the_gate` is pinned at `:169-170` as
  "the deliberate scope decision, pinned so it cannot be widened by accident".
  Retract that rationale explicitly or the reversal is undocumented.
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
10. **(S6)** A write-capable subagent cannot run a worktree-mutating git op, while
    permitted git ops still succeed.
11. **(S6)** A long-running child is monitored rather than lost to a wrapper
    timeout.
12. **(S7)** Both #608 and #618-#627 read back `CLOSED` from the provider via
    `verify-closeout --expect-state CLOSED`, over a complete classification
    ledger committed before the prepared release record.

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
- Verification type: integration — (SC10) a write-capable subagent attempting
  `git stash`/`checkout`/`reset` in the shared worktree is refused with the rule
  named, exercised through the wired spawn path rather than by direct call.
  Negative: `git add`/`commit` by the same agent still succeed.
- Verification type: integration — (SC11) a child exceeding the wrapper timeout is
  still tracked to completion and its result retrievable.
- Verification type: manual — (SC12) `verify-closeout --expect-state CLOSED`
  reads back #608 and each of #618-#627 from the provider after the publish, and
  the classification ledger commit precedes the prepared release record.

## Slice Coverage

| Slice | Criteria | Notes |
| --- | --- | --- |
| S1 | 1, 2, 3, 4 | tooling; generator built here, run at S7 |
| S2 | 5 | subject identity |
| S3 | 6, 7 | lesson loop |
| S4 | 8 | docs graph |
| S5 | 9 | umbrellas; the probe question bounds it |
| S6 | 10, 11 | operating contract |
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

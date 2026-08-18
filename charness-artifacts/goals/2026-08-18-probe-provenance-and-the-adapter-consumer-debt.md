# Achieve Goal: A verdict may not claim more than its probe measured

Status: active
Created: 2026-08-18
Activation: `/goal @charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md`

This file is the living goal scratchpad. It is activated by the user's request after
the pre-implementation critique passes.

## Active Operating Frame

- Current disposition: ACTIVE, activated 2026-08-18. The pre-implementation critique ran
  on 2026-08-18 (four bounded angles plus a counterweight pass) and its blockers are
  folded below; reshape mid-run only through `## Discuss Before Activation`.
- Precondition DISCHARGED (logged outside the Slice Plan, not this goal's work): the
  standing-lane flake's BAR is repaired at `8527936fd` — the 10s load-sensitive deadline in
  `test_acquire_closes_session_on_sigterm_mid_render` is replaced by a liveness wait on the
  child's process state. Proven on the bound observable, not by a green run: against a
  child reaching its `open` line at 12s, HEAD~ raises `AssertionError` at 10.0s and HEAD
  passes at 12.1s. The standing lane is green at this tree (10156 passed, 72.6s), recorded
  as context, never as the proof. **Residual, matching the probe record's own non-claim
  rather than overrunning it**: a wall clock remains at `_HANG_BACKSTOP_SECONDS = 120`, so
  the load-dependent arm is rare and legible, not eliminated. No node is quarantined and
  there is NO expected-red baseline: any red in the standing lane stops the run, and a red
  on that node means investigate a hang.
- Slice 1 — the probe record: **COMPLETE at `ef37bcbaa`**. Both bounded rounds ran; round 1
  produced substantial repairs and round 2 found one of those repairs shipping the class it
  repaired. Round-2 repairs are ACCEPTED-UNREVIEWED under the two-round cap. Full ledger in
  `## Slice Log`.
- Slice 2 — the two readers: **COMPLETE**, held at REVIEW severity by operator ruling.
  Round 1 found three ways to land an unbacked close, a vacuous guard on the second release
  entrypoint, and a `consolidated` contract hole; all are repaired and pinned. Round-1
  repairs plus the severity downgrade are ACCEPTED-UNREVIEWED under the two-round cap.
  Full ledger in `## Slice Log`.
- Current slice: 3 — measure `what_reads_this.py`'s residual for the adapter-loader shape.
- Current slice intent: answer Open Question 3 on the surface that owns it, name the
  enumeration step in implementation-discipline's Change Discipline, and disposition `#599`.
  Paying down debt rows is slice 5 and is NOT in this intent.
- Next action: slice 3. GROUNDWORK ALREADY MEASURED, so do not re-derive it —
  `what_reads_this.py` takes only literal-name targets (`--symbol`/`--path`/`--config-key`)
  and cannot express the adapter-loader SHAPE (`_is_adapter_loader_name`: underscore-stripped,
  contains `CALL_TOKEN`, starts with `CALL_PREFIXES`), while the census already ships
  `consumer_files()` at module level, unprefixed and importable, doing exactly that AST
  enumeration. The answer is therefore documentation plus an implementation-discipline step,
  NOT a new capability — cheaper than the goal assumed.
- Push status: NO push grant this session. Everything lands locally; the ahead-of-origin
  count is expected and is not a defect to fix.
- Verification cadence: cheap deterministic checks at commit boundaries; the changed-line
  proof immediately after each slice commit; fresh-eye review at slice boundaries; broad
  and release-lane proof at the bundle boundary and at closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`; the broad
  standing lane and `-m release_only` are deferred to the bundle boundary and the final
  verification lock, which uses `--verification-lock`. The standing pytest lane is a
  high-confidence check, not a commit-boundary one.
- Slice review packet: before fresh-eye slice critique, provide intent, changed files and
  owning/generated surfaces, expected invariants, tests/proof, non-claims, out-of-scope
  lines, and reviewer questions.
- History boundary: keep this frame current; completed detail moves to `## Slice Log`,
  `## Operator Decision Queue`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Make a behavioral probe unable to claim more than it measured, at the two boundaries where
a wrong claim escapes — an issue close and a release publish — and then pay down the
adapter-consumer debt using that mechanism as the way each row is proven. The debt is not
the point; it is the corpus that proves the mechanism works on 45 real rows instead of on
one worked example.

## Problem

On 2026-08-18 three of one session's own measurements were refuted, each by a reviewer with
no execution capability. **Two of the three share one generator**: the probe's stimulus came
from the agent's model of the mechanism rather than from the source that defines the claim.
`#528` was probed with `deliberately_absent` as a YAML list when the vocabulary is a
mapping, so it measured the unfixed baseline. `#628` was probed with `--title "a different
cohort"` when the reported case is the scaffold run with no arguments. "The fix is absent"
and "the fixed branch was never entered" render identically, so a probe that measured
nothing reads exactly like a probe that measured a failure — and in one case that produced a
wrong report to the operator, in another a "verified" that preceded any distinct observer.

**The third refutation has a different generator and needs a different countermeasure.**
Round 2 found one of two entrypoints guarded, causing a harm the agent's own guard comment
described in words. No stimulus rule catches that: a verbatim stimulus and a base/HEAD pair
both come back green on the guarded entrypoint. Its countermeasure is *enumeration* — the
source retro's own Engelbart item names `consumer_files()`, run before the change rather
than after it. This goal carries both countermeasures and keeps them distinct, because
folding all three into one generator is how a remedy set covers two failures and reports
three.

Which rule catches which refutation, stated so the mechanism can be judged against it:

| Refutation | Caught by |
| --- | --- |
| `#528` — stimulus shape invented; base and HEAD render identically | Base/HEAD disagreement (Fixed Decision 2) |
| `#628` — probed under convenient conditions, not the reported ones | Quoted stimulus provenance bound to the source's conditions (Fixed Decisions 2 and 4) |
| Round 2 — one of two entrypoints guarded | Call-site enumeration (Fixed Decisions 5 and 7) |

**Correction, 2026-08-18, from slice 1's bounded review — row 2 overclaimed and the
mechanism does not do what this table said.** `Source conditions:` is a presence-only
field: it is required to be substantive and then it is compared to NOTHING. `#628`'s own
source is a GitHub issue body, the one source class `verify_source_quote` can never read,
so the refutation the quote mechanism is named after lives outside that mechanism's
reach. A stimulus that flatly contradicts the stated conditions still resolves
`evaluated`, and there is a test pinning that so it cannot be forgotten. The honest
reading of row 2 is: **the conditions and the stimulus are placed side by side in one
record for a distinct observer to compare.** That is a real P4 legibility tooth and it is
not a mechanical one.

**Row 3 needs the same two-part treatment, and giving row 2 the correction while blessing
row 3 was this very failure recurring one paragraph later.** Mechanised half, shipped: a
record that NAMES an unproven call site can no longer resolve `evaluated` — slice 1's review
found that answer was computed, printed, and then ignored by the verdict. Non-mechanised
half: call-site coverage is SELF-REPORTED, and the round-2 agent that produced this
refutation *believed* the file had one entrypoint. Such an author writes `none` in good
faith and the record resolves `evaluated`. Slice 1 catches only the author who already
knew. The countermeasure this table names for row 3 is enumeration (Fixed Decision 7,
`consumer_files()`), which is **slice 3 and unshipped**, so row 3 does not stand on slice 1
alone.

Row 1 stands, and understates itself: the `#528` shape is caught twice, by base==HEAD
disagreement and independently by the relative-indent preservation that refuses a
flattened-mapping quote.

The same review found the quote check crediting itself with `#528` in its own docstring,
which is the "remedy set covers two failures and reports three" failure this section warns
about, occurring inside the slice. `#528`'s countermeasure is the base/HEAD arm rule; the
quote makes a mismatch legible to a reviewer, and no more.

This repo already enforces the stimulus countermeasure on its TEST surface: a behavior test
carries a mutation that must be killed, and the reconciliation census carries a liveness
control so a row cannot pass by sharing no field with its probe. It does not enforce it on
the PROBE surface, and the probe surface is what closes issues and publishes releases.

Meanwhile the adapter-consumer census counts 45 rows of unpaid debt — 37
`accepted-risk-unguarded` plus 8 `no-version-validation` — and the count is compared to
nothing, so a 46th row lands green. Paying those rows down without the probe discipline
first would reproduce the 2026-08-18 error 45 times.

## Fixed Decisions

- **The probe record is a POPULATED EVIDENCE RECORD read at a boundary floor**, not a new
  gate that renders a verdict about other gates. The north star names a gate-that-checks-
  gates as the anti-pattern; the teeth here are the same ones it does license — a populated
  record and a distinct observer. "Not a meta-verdict" does not mean "not read by anything":
  `skills/public/issue/scripts/issue_closeout_rung1_floors.py` already ships
  `evaluate_source_preservation` (a verbatim `Source text:` / `Re-read obligation:` /
  `Source degraded reason:` presence floor) and `evaluate_behavioral_verdict` (the per-issue
  `Behavior #N:` reader). Those are the shape and the reader; slice 2 extends them.
- **Base-vs-HEAD disagreement is the minimum bar, and the disagreeing observable must be the
  one the claim rests on**, under the conditions the source names. Disagreement on *any*
  observable is not the countermeasure: it clears `#528` and passes `#628`, whose fix did
  change behavior on the convenient path while the reported case stayed broken. When base
  and HEAD agree on the bound observable, the honest output is that the probe measured
  nothing, never the result.
  **Per-arm disposition, measured in slice 1 and answering Open Question 1.** The rule
  survives, but only because the arms are dispositioned separately — collapsing them is
  how "base and HEAD differ" gets satisfied by a base that merely crashed. The arm alone
  does not decide; it is read against the claim's KIND (`change` / `existence` /
  `refusal`). Shipped in `scripts/probe_record_lib.py` and enumerated there:

  | Base arm | Disposition |
  | --- | --- |
  | `base-observed` | Compare. Differ → `evaluated`. Agree → `not-established` ("measured nothing"). Either capture empty → `not-established`. |
  | `base-absent` | Establishes an `existence` claim ("this surface now refuses"). Refuses a `change` claim: with no surface at base there is no prior behavior for a change to be measured against. **Still owes BOTH captures** — the HEAD reading IS the claim, and the base capture is the evidence the surface really is absent. Without that, relabelling a change claim as an existence claim on an absent base was a two-word bypass of this whole table, measured resolving `evaluated` with no observable in the record at all. |
  | `base-unrunnable` | Always `not-established`. **A base that could not run is not a base that disagreed** — this is the `#528` shape, where a crashed base "differs" from HEAD for a reason that has nothing to do with the fix. |
  | `base-not-applicable` | Reserved for a `refusal` claim. On any behavioral claim it is refused outright, because it is otherwise the escape hatch: declare no base applies while still claiming a flip. |

  A `refusal` claim resolves `not-configured` — the vocabulary's word for "there is
  genuinely no question here" — and never `evaluated`, so a recorded refusal cannot be
  read as evidence of a repair it never claimed. It owes a `Refusal reason:`, and it owes
  the `base-not-applicable` arm (the reservation runs both ways).
  The table gives each ARM's disposition, not the record's outcome: a differing arm still
  lands `not-established` on a duplicated field, an unverified quote, an unknown claim
  kind, or an unproven call site.
  **Shipped in three files, all of which slice 2 needs**: `scripts/probe_record_lib.py`
  (the judging half), `scripts/probe_record_parse.py` (the markdown grammar and the quote
  verification), and `scripts/check_probe_record.py` — the command surface, whose
  `--require-evaluated` mode is the tooth a floor calls. Default mode reports and exits 0
  by design, so a floor that calls it without the flag gates nothing.
- **A probe that measured nothing says so in the repo's existing typed vocabulary.**
  `scripts/boundary_probe_lib.py` already owns `evaluated` / `not-configured` /
  `not-established` plus `undetermined_reasons`, and carries an explicit comment that a
  further private spelling of "we could not tell" is how the concept drifts back apart. A
  base==HEAD probe resolves to `not-established` with an `undetermined_reasons` entry. Do
  not invent a new phrase.
  **Same words, OPPOSITE consumer rule — slice 2 must not copy the sibling's.**
  `boundary_probe_lib` keys its verdict on `hit`, and its own comment warns callers NOT to
  key on `state != PROBE_EVALUATED`, because there `evaluated`/`hit=False` is a real
  answer. A probe record inverts that deliberately: `evaluated` is reserved for "the
  measurement backs the claim", so the floors slice 2 writes MUST key on
  `state != evaluated`. Recorded here and not only in a docstring, because the shared
  vocabulary is exactly what would make a floor author reach for the sibling's rule.
- **Stimulus provenance is quoted, not summarized**: an issue body line, a spec docstring, or
  a shipped test fixture, reproduced verbatim, together with the conditions the source names.
- **A row's probe covers every adapter-payload call site in the file, or names the ones it
  leaves unproven.** The census's own stated blind class is that it classifies FILES, not
  call sites; a row flipped on one guarded site while a second still substitutes a charness
  default is the third 2026-08-18 refutation replicated once per row.
  **Disambiguated 2026-08-18 after slice 1's review found this decision and `## Behavioral
  Proof` pulling in opposite directions, and the code implementing the permissive one.**
  Naming an unproven site keeps the record COMPLETE, which is what this decision asks for;
  it does NOT make the claim established, which is what Behavioral Proof requires ("a row
  does not improve while an enumerated site is unproven"). Both hold once the two are kept
  apart: a record that honestly names an unprobed entrypoint is well-formed and resolves
  `not-established`. Before the repair it resolved `evaluated` and exited 0 under
  `--require-evaluated` — the third refutation passing the very mode built to stop it.
- **A verdict change with no probe record named at the frozen target is not a paid row.**
  `scripts/prepush_focused_changed_line_coverage.py` returns status `noop` exit 0 when no
  mutation-pool file changed, so a commit editing only `adapter-consumer-classification.json`
  passes this goal's own low-cost proof. A `noop` result on a debt commit is recorded as
  UNPROVEN for that row; it is not evidence.
- **The consumer census gains a pre-change query before it gains any new teeth, and the
  query's owner is measured rather than assumed.** `scripts/what_reads_this.py` already
  answers "what reads this?" for `--symbol` / `--path` / `--config-key`, with a
  `zero_result_caveat` and an `unscanned_surfaces` list, and its docstring names `#599`.
  Enumeration is cheap and prevents; refusal is expensive and only detects.
- **A census row may carry more than one defect class.** The 2026-08-18 seeding assumed one
  and mis-filed at least one row — `scripts/build_retro_lesson_selection_index.py` is both
  `accepted-risk-unguarded` and `no-version-validation` — which would have been repaid under
  the wrong remedy. Baseline pinned before the schema changes: 45 rows = 37 + 8, counted at
  goal creation under one-verdict-per-file, summing with the other classes to 121.
- **The no-increase seam covers the full per-verdict vector, not `accepted-risk-unguarded`
  alone**, and its baseline is generated, never hand-edited beside the increase it would
  authorize. Anchoring on one count creates a cheaper exit than fixing code: relabel the row
  to a witness-free verdict.

## Open Questions

- ~~Does the base-vs-HEAD rule survive contact with probes whose base does not build, or
  whose fix is a new file with no base at all?~~ **ANSWERED in slice 1**, before the rule
  was wired anywhere. It survives, conditioned on the claim kind; the per-arm disposition
  table is folded into Fixed Decision 2 and shipped in `scripts/probe_record_lib.py`.
  Two things the answering turned up that the question did not anticipate, both now
  mechanism rather than prose: a quote cited against a LIVING document rots the moment
  that document is edited, so a record may pin `Source revision:` and the quote is then
  read through `git show`; and a field value the markdown gate forces to WRAP was
  silently truncated to its first line, so an indented continuation is now part of the
  grammar. Both were found by writing the first real record, not by review.
- Is `safe-checks-errors` decidable by AST? **Baseline correction: it has no mechanical
  witness today at all.** `VERDICTS` maps it to `None`; only `guarded` carries a marker, and
  the gate's own failure text says so. The trial's falsifier is pre-registered: a witness
  phrased as "branches on `errors`/`valid` between the loader call and the first
  consequential read" must separate `skills/public/impl/scripts/survey_verification.py`
  (`accepted-risk-unguarded`) from `skills/public/quality/scripts/inventory_lint_ignores.py`
  (`safe-checks-errors`). **Stop rule: if it cannot, the trial's output is a recorded
  negative finding and the trial ends.** It does not escalate into designing a better
  witness, and the answer is not pre-decided here. Slice 4 records the result.
- Who owns the "who reads this producer" question for the adapter-loader *shape*
  (`_is_adapter_loader_name`, which a line-based scanner cannot express) — a shape/family
  target kind on `what_reads_this.py`, or exporting the census's `consumer_files()` as an
  importable helper? Slice 3 answers with the two files open, and dispositions `#599`.
- Is quality's same-day scaffold overwrite the defect `#628` reports, or the designed
  continue-in-place its debug sibling documents? This is an operator design call and Slice 6
  brings it to the queue rather than deciding it.

## Non-Goals

- Do not build a gate that inspects other gates' verdicts. If the probe record cannot be
  populated with captured observables, that is the finding; a meta-verdict is not.
- Do not convert the two-round review obligation's JUDGMENT half into automation. Whether a
  finding is the class under repair, whether a channel is genuinely distinct, and whether an
  accepted-risk reason is honest all stay human-language judgment.
- Do not pay the census debt down by editing verdict strings. Four of five verdicts are
  editable by the party reporting them, and a debt that falls without a behavior change is
  the failure this goal exists to make visible.
- Do not close `#628` inside this goal on a design call the operator has not made.
- Do not pre-decide the AST trial's answer. The likely discriminator is whether degradation
  was disclosed to a reader — human judgment, which the census docstring already says — but
  writing that conclusion into the plan deletes the measurement and re-ships the class this
  goal is about.
- Do not survey `hotl` proof packets. The source retro lists them as the third sibling and
  as NOT SURVEYED; they are considered and deferred here, not overlooked. Reopen trigger: a
  hotl packet supporting an irreversible boundary is found carrying a behavioral verdict
  with no stimulus provenance.

## Boundaries

- **Precondition — DISCHARGED 2026-08-18 at `8527936fd`**, by repair rather than by
  deselection, so no node id is quarantined and there is no expected-red baseline. The
  standing lane WAS red on a load-dependent flake in `tests/test_web_fetch_cleanup.py`,
  node id `test_acquire_closes_session_on_sigterm_mid_render`, which blocked pre-push and
  was [handoff](../../docs/handoff.md) Next Session item 1. Its 10s wall deadline is
  replaced by a liveness wait on the child's process state. **Residual, stated because the
  frame must not carry a stronger claim than the record it cites**: a wall clock still
  exists at `_HANG_BACKSTOP_SECONDS = 120`, so the test is not load-independent — the
  load-dependent arm is rare and legible rather than common and silent, which is what both
  the test comment and the probe record's own `## Non-claims` say. A red on that node is
  therefore a signal to investigate a hang, NOT an expected red to absorb.
  The work is logged outside the Slice Plan and is not counted as this goal's work.
- Issue close, release publish, and proof-surface authoring are irreversible boundaries.
  Each needs its own phase-scoped grant; none is inferred from a green gate.
- Every slice that changes verdict logic on a proof surface owes the second bounded review
  round over the repaired surface, capped at two rounds per triggering slice. A first round
  producing no repairs discharges the obligation.
- The census manifest is the row-level contract. A row's disposition changes only with a
  behavioral probe attached, **covering every call site in the file**. A probe that NAMES
  an unproven site is a complete, honest record and resolves `not-established`; it does not
  move the row. The earlier phrasing here offered "or naming the unproven ones" as an equal
  alternative, which is the permissive reading Fixed Decision 5's disambiguation exists to
  kill and which the code no longer implements.

## User Acceptance

- A probe supporting a close or a publish carries its stimulus verbatim with provenance and
  its base/HEAD pair, names the observable the claim rests on, and reports `not-established`
  when base and HEAD agree on that observable — demonstrated on at least one real close, not
  only in a fixture. **The named candidate is `#599`**: slice 3 lands on its territory, and
  if the loader-shape residual closes, `#599` closes under this discipline. If no
  phase-scoped grant arrives, or the residual does not close, acceptance records
  `real close: not demonstrated` as a stated non-claim rather than substituting a fixture or
  reaching for a different issue.
- The probe record is REQUIRED by the issue-closeout rung-1 floor and by the release
  publication floor — not merely produced. Proven by running each floor against a carrier
  missing the field and showing it refuses.
- `#599`'s question — "who reads this producer" for an adapter-loader symbol — is answerable
  before a shared output contract changes, from whichever surface slice 3 measures as its
  owner, and the implementation-discipline order names that step. The answer carries the
  census's blind class in its own output: a helper-mediated reader and a per-call-site
  distinction remain invisible.
- The per-verdict count vector cannot move in either direction without a named accept, whose
  baseline is generated rather than hand-edited beside the increase it authorizes.
  Demonstrated by two runs: one with a count artificially moved, showing non-zero exit; one
  with the accept named, showing exit 0.
- `accepted-risk-unguarded` falls from 37 to a stated N, and `no-version-validation` from 8
  to a stated N — or every unrepaired row carries a dated re-decision. A row is closed by a
  behavioral flip OR by a recorded refusal; a recorded-refusal row is NOT "paid down", stays
  in the debt count with a `cannot-wire` reason and the probe record id that established it,
  and is exempt by construction from the behavioral-flip and base/HEAD criteria.
- Every row paid down flips a behavioral assertion, not a string — measured by the row's
  probe record naming either the `guarded` structural marker or a shipped test node id that
  fails on the pre-repair tree and passes after. A `noop` changed-line result on a debt
  commit records the row UNPROVEN.

## Agent Verification Plan

### Low-Cost Checks

Ordered; the order is load-bearing.

- `python3 scripts/sync_root_plugin_manifests.py` before any test run.
- `python3 scripts/check_adapter_consumer_classification.py --repo-root .` at every commit
  boundary; the per-verdict count vector is the running measure. This gate is broad-only in
  the timing table, so the commit-boundary run is the agent's, and it is enforced at the
  bundle boundary.
- `python3 -m ruff check --no-cache scripts skills tests`.
- Commit, THEN
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  immediately after each slice commit and BEFORE the broad lane. A `noop`, `unproven`, or
  `partial` result on a debt commit is recorded as UNPROVEN for that row, not accepted.
- `python3 scripts/check_documented_command_flags.py --repo-root .` whenever a slice adds or
  documents a command flag. Note the gate reads DOCUMENTED invocations, so a command no doc
  invokes yet passes it vacuously; that is its shape, not a green to lean on.
- `python3 scripts/check_probe_record.py --repo-root . --record charness-artifacts/probe/2026-08-18-standing-lane-flake-bar.md --require-evaluated`
  at commit boundaries once slice 1 has landed. The shipped exemplar is what every later
  record is written by copying, and it resolves through a pinned revision, so an exemplar
  that quietly stopped resolving would teach the wrong shape to all of them.

### High-Confidence Checks

- `python3 scripts/run_standing_pytest.py` at slice and bundle boundaries, never at every
  commit. **No expected-red baseline: any red stops the run.** This line previously named a
  "quarantined node id" that never existed — the precondition flake was repaired, not
  deselected — and instructing a future session to absorb a red on exactly the node whose
  120s backstop is where a genuine hang would surface was the dangerous direction to be
  wrong in.
- `python3 -m pytest -q -m release_only`, mandatory for any slice-5 commit touching a release
  surface — release gates lead the severity order and the standing lane deselects them.
- `python3 skills/shared/scripts/reviewer_boundary_fingerprint.py snapshot` before each
  bounded review round and `verify` after; a failed verify quarantines that round's approvals.

### External Or Live Proof

- The `#599` close, if its grant arrives, and any release publish. Each needs its own
  phase-scoped grant and a distinct-channel hosted readback; neither is inferred from a
  green gate.

### Behavioral Proof

- Each debt row paid down is proven by running the real CLI in a temp repo under the
  conditions the row's `reason` names — not by reading the diff, and not under conditions
  chosen for convenience.
- Every such probe records its stimulus provenance and its base/HEAD pair, and names the
  observable the claim rests on. A probe that cannot show base and HEAD disagreeing **on
  that observable** does not count as evidence for the row.
- Every such probe covers every adapter-payload call site in the file, or names the sites it
  leaves unproven. A row does not improve while an enumerated site is unproven.
- A verdict change with no probe record named at the frozen target is not a paid row.

### Distinct-Observer Review

- Bounded read-only reviewers, briefed from PRIMARY sources — the issue body, the shipped
  spec, the row's own `reason` — for the CLAIM, plus the probe RECORD for the probe, with
  the explicit task: does the quoted stimulus match the cited source line, and is the
  differing observable the one the claim rests on? The agent's probe TRANSCRIPT is withheld;
  the RECORD is not, because a record no distinct observer reads is not evidence.
- The 2026-08-18 evidence is that a reviewer handed the agent's summary reviews the summary;
  the refutations came from reviewers that went to the code instead.

## Slice Plan

| # | Slice | Proves |
| --- | --- | --- |
| 1 | Probe record: quoted stimulus provenance + base/HEAD pair bound to a named observable, in `boundary_probe_lib`'s typed vocabulary, with the no-base and no-build arms answered | A probe that measured nothing says so, in the repo's existing words |
| 2 | Wire the record into its two readers: the issue-closeout rung-1 floor and the release publication floor | The record is required where a wrong claim escapes, not merely produced |
| 3 | Measure `what_reads_this.py`'s residual for the adapter-loader shape; close it on the surface that owns it; name the step in implementation-discipline's Change Discipline; disposition `#599` | The preventing query runs before the change, on the surface that already owns the question |
| 4 | Census: multi-class rows, no-increase seam over the full verdict vector with a generated baseline, AST witness trial with its falsifier pre-registered and its stop rule armed | The debt count cannot move in either direction without a named accept |
| 5 | Pay down the debt in severity order, release gates first, with a cost recount after the first five rows | 45 rows, each closed by a behavioral flip or a recorded refusal |
| 6 | Two-round bookkeeping as typed critique fields; `#628`'s design call to the operator queue | The obligation is recorded, not remembered |

Slice 5 carries a cost checkpoint after the first five rows: re-read the measured per-row
proof cost against what slice 1 predicted, and record it in the Slice Log. **Per the
operator's activation decision the checkpoint is a WARNING, not a stop** — the full 45-row
corpus stays the commitment. The residual risk this leaves live is recorded under
`## Discuss Before Activation`.

## Backlog Recount

- Counted: 22 open issues on 2026-08-18 via `gh issue list --repo corca-ai/charness --state open`.
  Three issues the source handoff names as closeable (`#629`, `#608`, `#528`) are already
  closed and are not in that list; `#628` is the only one of the four still open.
- Claims: `#599` (slice 3 measures and may close it under this goal's discipline, subject to
  a phase-scoped grant); `#628` (staged to the operator queue as a design call, explicitly
  NOT closed here).
- Not claimed: the remaining 20. `#668` (runtime bar) and `#546` sit in one file and are an
  operator ruling, not this goal's work. `#612`, `#605`, `#586`, `#587`, `#601`, `#637`,
  `#638`, `#639`, `#635`, `#634`, `#667`, `#669`, `#670`, `#550`, `#527` and the three
  umbrellas `#582`/`#583`/`#584` are outside the probe-provenance and adapter-consumer scope;
  none was verified as still true here, and counting is not re-verifying.

## Operator Decision Queue

- **DECIDED 2026-08-19 by the operator — the probe-record floor is held at REVIEW
  severity, not blocking, pending slice 5.** The floor was built blocking, as
  `## User Acceptance` bullet 2 specifies, and migrating the existing suite to it measured
  the cost: 67 failing tests across 15 files, a standing obligation on every
  verification-claiming close, and a new operator-facing flag on `publish_release`. The
  operator chose to wait for slice 5's report across 45 real rows before paying that
  standing. Implemented as ONE constant,
  `issue_probe_record_floor.PROBE_RECORD_SEVERITY = "review"`, read by every carrier and by
  the release side, so the two boundaries cannot drift apart on severity. Both severities
  are pinned by `test_the_severity_switch_is_the_only_thing_that_decides_vetoing`, so the
  flip after slice 5 is a proven one-line change. **Consequence recorded rather than
  softened: `## User Acceptance` bullet 2 is NOT satisfied and cannot be while this holds** —
  the floor is produced and read, not required. Revisit trigger: slice 5's five-row cost
  recount, then the whole-corpus report.
- **DECIDED 2026-08-19 by the operator — the `local-only-by-contract` escape stays.** A
  close may satisfy the floor with a typed disposition instead of a record. The escape is
  one line, and slice 2's review measured what that means: of the ~67 migrated tests, ZERO
  exercise the record-reading path — every one takes the disposition branch. So the floor's
  teeth on a claiming close rest on the rung-2 critique, not on the mechanism. Kept by
  ruling, and made VISIBLE rather than silent: `claim_rests_on_disposition` names every
  issue whose claim rests on a word rather than a measurement, and the carriers surface it
  as a REVIEW line. What was NOT kept is the genuine contradiction — a disposition
  asserting impossibility (`blocked-needs-operator`, `no-behavior-change`) beside a
  verification claim is refused, because one of the two statements is false.
- **DECIDED 2026-08-19 by the operator — Cautilus public-skill validation is skipped for
  this slice.** `run_slice_closeout.py` reports `issue` as `evaluator-required` and asks
  whether `evals/cautilus/scenarios.json` coverage should change. The operator ruled pass;
  the closeout is acknowledged with `--ack-cautilus-skill-review` and this record, not with
  a silent green. NOT done, and stated so: the consumer contract in
  `docs/public-skill-dogfood.json` is not refrozen, and no evaluator scenario was reviewed.
  Revisit trigger: before any release that publishes `issue`, `quality` or `release`.
- **DECIDED 2026-08-19 by the operator — push happens after the retro**, not before. Every
  commit in this run is local until then.
- Decision: does quality's same-day scaffold overwrite stay (continue-in-place, as debug
  documents) or go (the defect `#628` reports)? The families currently disagree.
  Owner: repo operator. Why deferred: it is a design call, not a defect fix, and closing
  `#628` either way is irreversible. Unblock action: rule on which family is correct.
  Revisit trigger: slice 6, or any further `#628` re-measurement.
- Decision: should the 14 per-skill `adapter-contract.md` files carry the version-containment
  rule, or is the runtime refusal — which names the file and the line to fix — the better
  channel? Owner: repo operator. Why deferred: does not block local progress.
  Revisit trigger: slice 5's release-gate rows.
- Decision: two seeded census verdicts are contestable and a ratchet would freeze the
  mis-seeding. `scripts/reconcile_usage_episodes_host_hooks.py` is `safe-not-consequential`
  for a raw `yaml.safe_load` with no version field, while `scripts/quality_label_universe.py`
  is `no-version-validation` (debt) for near-identical prose; the first row's reason adds
  that no resolver contract exists for that adapter at all, which may or may not be the
  distinction. Owner: repo operator, or slice 5's in-flight judgment with the code open.
  Why deferred: pre-litigating it in the spec expands the goal by a re-seeding pass.
  Revisit trigger: before slice 4 ratchets any baseline.

## Coordination Cues

- Routing: shaped by `achieve` Before-phase; pre-implementation critique by `critique`
  (spec-critique target). Slices route to `impl` + `prove`; `debug` before any bug-class fix;
  `quality` for the gate-contract changes in slice 4; `issue` for `#599`'s closeout and for
  off-goal findings; `retro` at closeout, bound to this goal.
- Gather: n/a — no external URL or source link enters this goal's working context.
- Release: slice 2 touches the release publication floor; any actual publish needs its own
  phase-scoped grant and a distinct-channel hosted readback.
- Issue closeout: `#599` via the `issue` closeout floor, not in bulk.

## Discuss Before Activation

Discuss before activation: resolved 2026-08-18 by the operator, on three consequential
decisions surfaced by the pre-implementation critique.

- **Real-close demonstration.** The acceptance bullet was unsatisfiable as written. Operator
  named `#599` as the candidate, with a stated non-claim as the fallback if no grant arrives
  or the residual does not close. Folded into `## User Acceptance` and `## Backlog Recount`.
- **Slice 5 unit.** The counterweight recommended a severity-led subset with a checkpoint
  empowered to end the slice early and hand the remainder to a successor goal. Operator chose
  to keep the full 45-row corpus with the checkpoint as a warning only. **Residual risk,
  recorded rather than resolved:** the counterweight's judgment was that "45 rows, each with
  a behavioral flip" is a commitment made before the per-row cost is known, and is the
  sentence that turns this goal into mechanical grinding. That risk stays live by operator
  decision; the 5-row cost recount is the early signal, and `## Discuss Before Activation` is
  where a mid-run re-scope would be renegotiated.
- **Boundary scope.** The Goal claimed two boundaries while no slice touched either floor.
  Operator chose to keep both and add the wiring slice; slice 2 now covers the issue-close
  floor and the release publication floor together. This adds a second irreversible boundary
  to the run — each still requires its own phase-scoped grant.

## Slice Log

Slices 1 and 2 are complete, each with the two bounded review rounds the proof-surface rule requires.

### Slice 1: Slice 1 — the probe record

- Objective: Make a behavioral probe unable to claim more than it measured, as a populated evidence record with a typed outcome: a claim and its KIND, the observable named before the measurement, a stimulus quoted verbatim with provenance and the conditions its source names, and a base/HEAD reading of that one observable. Answer Open Question 1's arms before the rule is wired anywhere. Wiring into the two floors is slice 2 and was deliberately excluded.
- Why this approach: The record is a separate artifact rather than carrier-body fields because the issue closeout floors read a carrier through `_strip_code_fences`, so verbatim stimulus and quoted source text — which need a fence to survive — are exactly the content those readers discard. `state` is imported from `boundary_probe_lib` rather than respelled, per Fixed Decision 3. One divergence is deliberate and recorded: base==HEAD resolves `not-established` here, where the sibling would call that `evaluated`/`hit=False`.
- Commits: `8527936fd` (precondition, outside the Slice Plan), `57cde798e` (slice 1), `d9d9bb89b` (round-1 review repairs), plus the round-2 repair commit.
- What changed: NEW `scripts/probe_record_lib.py` (judging: vocabulary, base arms, claim kinds, resolution), NEW `scripts/probe_record_parse.py` (reading: markdown grammar + quote verification; split out when the library crossed its 480-line limit, on the concept boundary `issue_closeout_rung1_floors` already names), NEW `scripts/check_probe_record.py` (the command surface; `--require-evaluated` is the gating mode a floor calls, default mode reports and exits 0 by design), NEW `tests/test_probe_record.py`, NEW `charness-artifacts/probe/2026-08-18-standing-lane-flake-bar.md` (the worked example, on real work rather than a fixture). Also `tests/test_web_fetch_cleanup.py` (precondition), `docs/handoff.md`, and `charness-artifacts/quality/dup-review.json` (two idiom families classified intentional).
- Alternatives rejected: Rejected: carrier-body fields (the fence-stripping readers destroy the verbatim content). Rejected: a fourth private spelling of "we could not tell" (Fixed Decision 3). Rejected: a probe RUNNER in this slice — the record is an evidence record, not a gate that re-derives, and a runner is slice 5's affordance. Rejected in round 1's fold: a path-token heuristic on `Call sites unproven:` to detect a named site — too clever, and it false-positived on the repo's own exemplar; the anchored `none` grammar with a dash-only separator does the job.
- Targeted verification: 64 tests, after round 2 (59 before). Mutation-proved rather than assumed for the call-site verdict gate: deleting the repaired lines fails `test_named_unproven_call_sites_block_the_claim` and passes everything else, which is what the pre-repair test could not do. 100% line coverage of BOTH modules MEASURED with coverage.py, not inferred from green — the first measurement found four uncovered branches that green tests had not reached. Changed-line proof `clean` (not `noop`) at both slice commits. Standing lane green at the slice boundary: 10215 passed in 75.8s, up exactly the 59 new tests from the 10156 baseline. `run_slice_closeout.py --skip-broad-pytest` green at each commit. Plugin mirror byte-identical for all three scripts. The precondition repair was proven on its bound observable rather than by a green run: against a child reaching its `open` line at 12s, the old loop raises `AssertionError` at 10.0s and the new one passes at 12.1s.
- Test duplication pressure: `check_dup_ratchet.py --summary` run at each commit boundary. Two new code families surfaced, both idiom-sized guard clauses spanning unrelated predicates (`if not x: return False` across four members, `if not x: return []` across six). Both classified `intentional` in `dup-review.json` with the per-member reasoning rather than baselined; `status: clean` after each. Note the first classification pass reordered the whole file by sorting on id — reverted, and the entry appended in place, because incidental churn in a review ledger hides the entry being added.
- Critique: TWO bounded review rounds, as the proof-surface rule requires; round 1 produced substantial repairs so round 2 was owed and ran. Round 1 (two reviewers, unnamed, `bounded-reviewer`, read-only) found the mechanism renderable `evaluated` by ALL THREE failure shapes it was built for. Every finding was re-measured by the parent before folding — each reproduced as a record exiting 0 under `--require-evaluated`, and all now exit 1. Blockers: `base-absent`+`existence` established the claim without reading either capture, so a record with NO observable sections passed; a record honestly NAMING an unprobed entrypoint still passed, because `covers_all_call_sites` was computed, printed and ignored by the verdict; the degraded-reason escape fired on any `unresolvable`, so a fabricated quote plus a one-letter path typo was accepted where the fabricated quote alone was refused; a quote flattened to column zero verified against a nested source — `#528`'s own mapping-vs-list confusion passing the check written for `#528`; an out-of-repo source ref read back `verified`; `Call sites unproven: TBD` passed completeness; the `none` separator class admitted `,` `;` `.` `-`, which continue a sentence; and captures differing only by a `base`/`head` label defeated base==HEAD — which the exemplar itself was teaching. Grammar defects: indented sub-lists parsed as phantom fields that stole the real field's value, repeated fields resolved first-wins so a record's own format EXAMPLE could win over the values a human reads, multi-token fence info strings cascaded into a whole-record mis-parse, and a four-backtick fence closed on its first inner three. Honesty defects: the quote check credited itself with `#528` in its own docstring AND its test encoded the same wrong model — the blind spot in the code and in its test being the same blind spot; the blind class both over- and under-claimed. Round 2 ran a code angle over the repaired surface plus a GOAL-CLAIMS audit, which found the artifact overclaiming in four places, including my own `#628` correction blessing row 3 in the same breath — the covered-two-reported-three failure recurring one paragraph after the correction that fixed it. Boundary fingerprint snapshot/verify around each round; round 1 verified `ok: true` / `parent-attributed` (only the declared parent commit). ROUND 2 WAS NOT CLEAN, and its blocker is the reason the two-round rule exists: repair 3 SHIPPED THE CLASS IT REPAIRED. Round 1 had closed a degraded-reason escape by gating it on a `local` flag, but the flag was derived from the PATH GRAMMAR, which requires a dot-extension -- so `Source ref: adapterTYPO.py` was refused while `Source ref: adapterTYPO` was excused, with a wholly fabricated quote, resolving `evaluated`. Deleting three characters was cheaper than the typo the repair had just closed, and an author hitting the "Fix the ref" refusal reached the escape by SHORTENING the thing they were told to fix; extension-less real files (`Makefile`, `LICENSE`) sat in the same excused bucket. `local` is now set from the POSITIVE nonlocal test. Round 2 also found repair 2 -- the call-site verdict gate, the countermeasure for the third 2026-08-18 refutation -- carrying NO test: its only test asserted two keys that were already true before the repair, so the four repaired lines could be deleted with all 59 tests green. A verdict change on a proof surface that the suite could not see is the class this repo keeps paying for; the test now asserts the state and the reason, and the mutant was run and KILLED rather than assumed. Third, `_ARM_LABEL_RE` replaced a whole-line arm banner with `""` instead of dropping the line, so the ASYMMETRIC paste (one transcript kept its banner, the other retyped) manufactured exactly the disagreement the strip prevents. Fourth, the CLI hand-built a second copy of the result shape whose single owner exists so no branch can omit a key -- and it had already drifted past `residual_judgment` and the `local` flag; there is now one construction site. Per the operating contract's two-round cap, these round-2 repairs are recorded as ACCEPTED-UNREVIEWED: no third round read them.
- Off-goal findings: None filed. Two facts measured that belong to later slices and are recorded rather than acted on: `what_reads_this.py` takes only literal-name targets (`--symbol`/`--path`/`--config-key`) and cannot express the adapter-loader SHAPE, while the census already ships `consumer_files()` at module level, unprefixed and importable — so Open Question 3's answer is documentation plus an implementation-discipline step, not a new capability. And `check_documented_command_flags.py` passes VACUOUSLY for the new CLI, because it reads documented invocations and no doc invokes it yet.
- Lessons carried forward: The two defects no reviewer found were found by WRITING THE FIRST REAL RECORD: a quote cited against a living document rots the moment that document is edited (hence `Source revision:` and `git show`), and a field value the markdown gate forces to wrap was silently truncated to its first line — the `line-anchored-ledger-fields` hazard re-shipped on a brand-new surface. Both argue for producing one real artifact before reviewing the mechanism that consumes it. Second: `green-test-is-not-covered-line` paid off twice — the coverage read found four unreached branches, and two repaired tests were passing on an EARLIER refusal than the one they were named for, which only re-running after the repair exposed. Third: for slice 2, `boundary_probe_lib` warns callers not to key on `state != PROBE_EVALUATED`; probe records invert that, so the floors MUST key on `state != evaluated`. Same words, opposite consumer rule. Fourth, and the sharpest: a repair round is itself a slice that can carry the class it repairs. Round 1's `local` gate and round 2's blocker are the same defect at two depths. The cheap detector is to ask, of every refusal added, "what is the CHEAPEST mutation that still gets past this?" -- for a path-shaped gate the answer was not a longer typo but a shorter one.
- Metrics: Per-record authoring cost, recorded because slice 5's checkpoint is specified to measure against what slice 1 predicted: the one worked example took roughly 15 minutes end to end — drafting, two resolver runs to fix a wrapped-field truncation and a call-site grammar miss, and one edit to drop the arm labels. Estimate for a debt row, which additionally needs the base/HEAD captures actually RUN in a temp repo under the row's stated conditions and a call-site enumeration per file: materially more than the worked example, and the 5-row recount is the first honest measurement. No host token/time telemetry is claimed here.

### Slice 2: Slice 2 — wire the record into its two readers

- Objective: Make the probe record REQUIRED where a wrong claim escapes rather than merely produced — the issue-closeout rung-1 floor and the release close-issue boundary — and prove each reacts to a carrier that omits it. Held at REVIEW severity by operator ruling before landing; the mechanism, the wiring and the proof are complete, the veto is not armed.
- Why this approach: The obligation is triggered by the CLAIM, not the classification, which is the goal's own thesis: a `Behavior #N:` line leading with a typed non-verifying status asserts no measurement and owes nothing, while one that says `confirmed via the CLI` asserts one and owes a record. Gating on classification instead would tax every honest non-verifying close for a claim it never made. The issue-side floor is a NEW sibling module rather than an addition to `issue_closeout_rung1_floors`, whose docstring states it never imports repo-internal `scripts/` — a property worth keeping, and `issue_resolution_critique` is the precedent for a sibling that reaches one.
- Commits: `dc26d4cca` (the floors and their wiring), `d8437e0c0` (mapping and branch coverage), plus the review-round repair commit and the severity downgrade.
- What changed: NEW `skills/public/issue/scripts/issue_probe_record_floor.py`, NEW `skills/public/release/scripts/release_closeout_floors.py` (holds BOTH release rung-1 floors; the behavioral-verdict floor moved here when `release_issue_closeout.py` crossed its 360-line gate), NEW `tests/quality_gates/test_probe_record_floor.py`. Wired into `issue_verify_closeout.py`, `issue_close_comment_floor.py`, and both release entrypoints in `release_issue_closeout.py`. Operator surface: `--close-issue-probe-record` on `publish_release`, threaded through publish and resume. Declared in `.agents/closeout-floor-matrix.json` with `closeout_floor_matrix_lib.py` taught the new floor's attribution. `issue_consolidated_closeout._TARGETED_CLAIM_NAMES` gained `probe record`. ~15 test files migrated.
- Alternatives rejected: Rejected: putting the floor in `issue_closeout_rung1_floors` (erodes its stated no-repo-import property). Rejected: classification-triggered obligation (taxes honest non-verifying closes). Rejected in round 1's fold: refusing EVERY disposition beside a claim — `local-only-by-contract` means 'verified locally and the contract accepts local', which is coherent with a claim rather than a contradiction; only impossibility-asserting dispositions are refused. Rejected: appending the probe advisory to the shared `review_advisory` list, whose own comment reserves it for the critique-skip line and whose tests assert that.
- Targeted verification: 10251 standing tests pass; `-m release_only` 102 pass; floor matrix `ok: true` across all 36 pairs, re-measured after the severity change; changed-line proof `clean`; dup ratchet clean; lengths, ergonomics and attention-state gates clean. The floor's reach is proven by INPUT BREAKAGE rather than by reading: the matrix deletes each floor's input per carrier and observes whether that carrier's own verdict flips and whether it attributes the refusal to that floor. Both severities are pinned by test, so the post-slice-5 flip is proven rather than hoped.
- Test duplication pressure: `check_dup_ratchet.py` run at each boundary. Two families I introduced were REAL and were fixed rather than classified — two near-identical cross-skill loaders inside one file, and two copies of the target-binding rule inside another. Seven idiom families remain, classified with per-member reasoning; the largest has ~130 pre-existing members and is the repo's own bootstrap convention.
- Critique: TWO bounded rounds. Round 1 found THREE ways to land a close or a publish asserting a verification nothing measured, all reproduced by the parent before folding. (1) `issues?\b` was mirrored from the sibling as a flat alternant and DROPPED the tracker-ref conjunct the sibling documents — so `Behavior #42: issues with the stale cache are gone; confirmed via a fresh checkout` led with an ordinary English word, owed nothing, and closed unbacked. The commonest way to start a bug sentence was a universal escape. (2) A typed disposition on the probe line discharged ANY claim, so the floor's refusal set never actually included 'a claim with no measurement'. (3) A record could live outside the repo, unreadable by the reviewer it exists for. Round 1 also found the second release entrypoint's guard VACUOUS: `--close-issue-behavior` defaults to `[]`, the probe floor is inert on silence by design, so the cheapest possible input reached `gh issue close` — the guard fired only when the caller volunteered something to check. And it found a contract hole: `consolidated`, the disposition whose whole point is claiming nothing about the defect, could carry a `Probe record:` line asserting the repair was measured, while the floor matrix had already declared that line a repair claim. The second round-1 reviewer enumerated all 31 migration sites and found ZERO weakened assertions, but measured that of ~67 migrated tests, ZERO exercise the record-reading path — every one takes the disposition branch — and found the resume lane hard-requiring a flag the primary lane never needed, which makes recovery stricter than the publish it recovers.
- Off-goal findings: None filed. Two facts recorded for later slices: the release PUBLICATION floor named in the frame (`publish_release_preflight.py`) is not where this landed — the wiring is the release CLOSE-ISSUE boundary, and a publish that closes no issue owes no record, which is defensible but is not what the acceptance sentence says. And the standing lane covers the matrix at one cell; the whole-grid observation is `slow_corpus` and the end-to-end gate is `release_only`, both deselected there.
- Lessons carried forward: The wiring reproduced the very class it answers, TWICE, and both were found by mechanisms this repo already had rather than by me. The closeout floor matrix read `inert` for `close-with-comment` — a file whose own comments name that asymmetry three times, mine being the fourth instance of a floor landing on `verify_closeout` and never reaching the carrier that mutates GitHub directly. And `ensure_release_issues_closed` reaches `gh issue close` with resume able to skip the preflight entirely; its own comment says so, beside an authorization call re-run for exactly that reason. Second lesson: a repair round is itself a slice that can carry the class it repairs — round 2 of slice 1 proved that, and round 1 of slice 2 proved it again when my `issues?\b` mirror dropped the conjunct the source it mirrored had documented. The cheap detector both times was asking 'what is the CHEAPEST mutation that still gets past this?' — for a path gate the answer was a SHORTER typo, for a status vocabulary it was an ordinary English word.
- Metrics: Migration cost measured rather than estimated: 67 failing tests across 15 files, from a starting point of zero. That figure is what the operator's REVIEW-severity ruling was made against. No host token/time telemetry is claimed.

## Context Sources

- [The design north star](../../docs/design-north-star.md) — P4, P5, and the proof-surface
  reading of the irreversible boundary. The governing standard, read first.
- [The operating contract](../../docs/conventions/operating-contract.md) — the two-round
  critique floor and the write-capable isolation rule.
- [The session retro](../retro/2026-08-18-adapter-version-containment-and-the-consumer-census.md) — the refuted measurements and their generators.
- [The closes critique](../critique/2026-08-18-closing-four-verified-resolved-issues.md) — the round that refuted one of them outright.
- [The census manifest](../../scripts/adapter-consumer-classification.json) and
  [its gate](../../scripts/check_adapter_consumer_classification.py) — the row-level debt and
  its stated blind class.
- [`what_reads_this.py`](../../scripts/what_reads_this.py) — the shipped answer to `#599`.
- [`boundary_probe_lib.py`](../../scripts/boundary_probe_lib.py) — the typed probe vocabulary
  a new spelling would fragment.
- [`issue_closeout_rung1_floors.py`](../../skills/public/issue/scripts/issue_closeout_rung1_floors.py) — the existing verbatim-provenance shape and the record's reader.

## Interview Decisions

- Rejected: a goal that only pays down the 45 rows. The retro's evidence is that paying them
  down without the probe discipline reproduces the error once per row.
- Rejected: a goal that only ships the probe discipline. A mechanism with one worked example
  is how this repo has repeatedly shipped rules that did not survive their second case.
- Chosen: the discipline first, the debt as its forcing corpus, in one goal so the mechanism
  is judged by whether it made 45 real proofs cheap.
- Rejected at critique time: splitting the goal, or re-scoping slice 5 to a subset. The
  counterweight judged the one-goal shape sound and recommended the subset; the operator kept
  the full corpus. Axis check: the 45-row figure is `single-point` — it is this repo's live
  census count, not a value that varies by host, provider, or profile.

## Plan Critique Findings

Pre-implementation critique ran 2026-08-18 before activation. Target reference:
spec-critique. Four bounded read-only angle reviewers (Minto/structure, Jackson/problem
framing, Weinberg/diagnostic + boundary ownership, Gawande/checklist), each briefed from
primary sources, plus one separate counterweight pass that triaged the collapsed list into
four bins. Fresh-Eye Satisfaction: parent-delegated. Packet consumed:
`charness-artifacts/critique/2026-08-18-111738-packet.md`.

**Blockers folded** (Act Before Ship — six, each verified against the cited file before folding):

- The base/HEAD bar did not discriminate the `#628` refutation it is named after. Folded into
  Fixed Decision 2, the Problem section's rule-to-refutation table, and Behavioral Proof.
- Slice 2 (now 3) proposed building `--impact` on the census gate when `what_reads_this.py`
  already ships that capability and names `#599`. Proposing a change without asking what
  already reads the question is the class this goal exists to fix. Folded into Fixed
  Decisions, Open Questions, and the Slice Plan.
- Slice 3 (now 4)'s AST trial was premised on a witness that does not exist —
  `safe-checks-errors` maps to `None` in `VERDICTS` — and its phrased witness is already
  falsified by the `survey_verification.py` / `inventory_lint_ignores.py` pair. Folded as a
  baseline correction, a pre-registered falsifier, and a stop rule.
- `prepush_focused_changed_line_coverage.py` returns `noop` exit 0 on a manifest-only commit,
  so the named per-slice proof and the verification lock were both blind to the verdict-string
  edit the Non-Goals forbid. Folded into Fixed Decisions, Low-Cost Checks, User Acceptance,
  and the Closeout Binding Plan.
- The census classifies FILES, not call sites, so a row could flip on one guarded site — the
  third 2026-08-18 refutation, replicated 45 times. Folded into Fixed Decisions and
  Behavioral Proof.
- The acceptance set did not bind the goal's work: all five bullets AS THEY THEN STOOD
  passed with zero rows repaid, the then-bullet-4 (a dup-ratchet precedent, since replaced)
  was already satisfied today because the gate refuses an empty `reason`, the
  real-close bullet was unsatisfiable, and the dup-ratchet precedent does not transfer (its
  accept validates an ID against a scanned universe with a regenerated baseline; a census
  verdict is authored). `## User Acceptance` was rewritten; the mis-named precedent was
  replaced by the required property.

**Over-worry raised but NOT folded**, with the reason each was rejected:

- *Pre-specify the probe record's path, format, and fields.* Rejected: that is slice 1's
  entire job, and the no-base/no-build arms are what determine the fields. Locking a schema
  before those arms are known turns slice 1 into a transcription task that cannot report its
  own negative. Named the most dangerous "fix" on the list.
- *Name the ratchet's baseline path and accept-flag spelling now.* Rejected: the property
  (generated baseline, not hand-editable beside the increase) is fixed; the path and flag are
  a design call that wants the code open. `boundary_bypass_ratchet_lib.py` is a precedent to
  read, not a template to copy sight-unseen.
- *Cost the two-round review obligation in a budget table.* Rejected: the obligation is
  contract-mandated by trigger, its executable half is already named in CLAUDE.md and the
  operating contract, and the cap is two rounds per triggering slice with a no-repair first
  round discharging it. A budget table adds length and changes nothing.
- *"Fixed Decision and Probe Question contradict each other."* Rejected on the merits: Fixed
  Decision 2 fixes the bar, Open Question 1 tests its edge arms. That is how a spec is written.
- *"`enumerate-consumers` in the phase-barrier list is a category error."* Rejected: the goal
  transcribes the retro's own capability item; Change Discipline is a defensible alternative
  home and the slice now names it, but this was never activation-blocking.
- *Terminology normalization pass.* Partially taken — `## Probe Questions` is renamed
  `## Open Questions` because it named design questions, not probes — but no review round is
  spent on the remaining overlap with `boundary_probe_lib`'s `PROBE_NOT_ESTABLISHED`.

**Deferred** (real, but not expanded into this goal's scope): the contestable seeded verdict
boundary between `reconcile_usage_episodes_host_hooks.py` and `quality_label_universe.py` is
recorded in `## Operator Decision Queue` with a revisit trigger before any baseline is
ratcheted. The exclusion of the 55 `safe-checks-errors` rows from the debt frame stays a
deliberate scope choice; Open Question 2's stop rule is what keeps it honest.

**Reviewer provenance**: bounded `bounded-reviewer` subagents (`Read`, `Grep`, `Glob`; no
execution), spawned unnamed, one angle each, with no nested spawns. Boundary fingerprint
snapshotted before the round. Every factual claim folded above was re-verified by the parent
against the cited file before it changed this artifact — the discipline this goal is about,
applied to its own critique.

## Closeout Binding Plan

- Reviewed inputs: the semantic set — the census manifest, the probe records produced by
  slices 1 and 5, `#599`'s carrier, and every issue or release carrier this goal touches.
- Frozen target: the commit that lands the final debt row or its recorded refusal.
- Fresh-eye: bounded read-only reviewers briefed from primary sources for the claim and from
  the probe RECORD for the probe, without the agent's probe transcript; two rounds on any
  slice that changed verdict logic.
- Verification lock: the per-row probe records — each naming the `guarded` structural marker
  or a shipped test node id — plus the census command's per-verdict count vector and the
  changed-line proof at the frozen target. The counts and the changed-line proof are
  corroborating, NOT load-bearing: both are blind to a verdict-string edit, which is why the
  per-row records lead.
- Terminal record: retro, packet, reviewer, lock, and status records are terminal evidence,
  not semantic inputs; a later semantic-input edit invalidates the lock and requires rebinding.
- Complete flip: only after a retro bound to this goal records, against the per-row records
  rather than against the counts, that no row was paid down by editing a verdict string.

## Off-Goal Findings

None yet.

## Final Verification

Not started.

## User Verification Instructions

Not started.

## Auto-Retro

Owed at completion, bound to this goal by its `Goal:` field.

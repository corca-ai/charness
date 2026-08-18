# Achieve Goal: A verdict may not claim more than its probe measured

Status: draft
Created: 2026-08-18
Activation: `/goal @charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md`

This file is the living goal scratchpad. It is activated by the user's request after
the pre-implementation critique passes.

## Active Operating Frame

- Current disposition: real draft/backlog awaiting activation. The pre-implementation
  critique ran on 2026-08-18 (four bounded angles plus a counterweight pass) and its
  blockers are folded below; reshape before activating if the acceptance boundary changes.
- Current slice: none. Slice 1 begins at activation.
- Current slice intent: not started. Once active, this names the reviewable-intent unit in
  progress and the commits it spans; critique and broad proof do not re-fire within one
  unchanged intent.
- Next action: activate with
  `/goal @charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md`.
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
- **A probe that measured nothing says so in the repo's existing typed vocabulary.**
  `scripts/boundary_probe_lib.py` already owns `evaluated` / `not-configured` /
  `not-established` plus `undetermined_reasons`, and carries an explicit comment that a
  further private spelling of "we could not tell" is how the concept drifts back apart. A
  base==HEAD probe resolves to `not-established` with an `undetermined_reasons` entry. Do
  not invent a new phrase.
- **Stimulus provenance is quoted, not summarized**: an issue body line, a spec docstring, or
  a shipped test fixture, reproduced verbatim, together with the conditions the source names.
- **A row's probe covers every adapter-payload call site in the file, or names the ones it
  leaves unproven.** The census's own stated blind class is that it classifies FILES, not
  call sites; a row flipped on one guarded site while a second still substitutes a charness
  default is the third 2026-08-18 refutation replicated once per row.
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

- Does the base-vs-HEAD rule survive contact with probes whose base does not build, or whose
  fix is a new file with no base at all? Slice 1 answers before the rule is wired anywhere,
  and writes the answer back into Fixed Decision 2 as a named disposition per arm.
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

- **Precondition, with a named owner and a stop condition**: the standing lane is red on a
  load-dependent flake in `tests/test_web_fetch_cleanup.py`, node id
  `test_acquire_closes_session_on_sigterm_mid_render`, which blocks pre-push. It is
  [handoff](../../docs/handoff.md) Next Session item 1. The activating session clears it —
  or deselects that node id with a recorded reason and a linked issue — before slice 1's
  first push; the work is logged outside the Slice Plan and is not counted as this goal's
  work. That node id is the expected-red baseline: any OTHER red in the standing lane stops
  the run rather than being absorbed. If it is still red at the first push boundary, the run
  lands locally, does not push, and hands the flake back as its own goal.
- Issue close, release publish, and proof-surface authoring are irreversible boundaries.
  Each needs its own phase-scoped grant; none is inferred from a green gate.
- Every slice that changes verdict logic on a proof surface owes the second bounded review
  round over the repaired surface, capped at two rounds per triggering slice. A first round
  producing no repairs discharges the obligation.
- The census manifest is the row-level contract. A row's disposition changes only with a
  behavioral probe attached, covering every call site in the file or naming the unproven ones.

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
  documents a command flag.

### High-Confidence Checks

- `python3 scripts/run_standing_pytest.py` at slice and bundle boundaries, never at every
  commit. Expected-red baseline is the one quarantined node id named in `## Boundaries`.
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

Not started.

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
- The acceptance set did not bind the goal's work: all five bullets passed with zero rows
  repaid, bullet 4 was already satisfied today because the gate refuses an empty `reason`, the
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

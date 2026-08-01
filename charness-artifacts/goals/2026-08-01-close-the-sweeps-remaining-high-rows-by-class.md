# Achieve Goal: Reproduce and disposition 9 of the sweep's remaining high rows, batched by repair shape — S24/S28/S35, S9/S10, S12/S13, S23/S2.

Status: active
Created: 2026-08-01
Activation: `/goal @charness-artifacts/goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: ACTIVE. All four slices complete; the midpoint
  goal-claims review ran and its findings are folded.
- Current slice: none — closeout is next.
- Next action: bundle proof (serial full pytest, `./scripts/run-quality.sh`,
  the armed changed-line lane over this goal's own range), then the closeout
  disposition review, then `retro` — in that order. **Slice 4's round 2 was
  never run and is an open gap**, not a discharge.
- **Corrected 2026-08-01 by the midpoint review:** an earlier version of this
  frame claimed "a floor up to 20 costs 0 new refusals" and put the negation
  sentence at 31 against a corpus p5 of 19. The recorded probe refutes all
  three: at `--floor 20` ten citations drop below their requirement and 46
  label values fall under the floor, the negation scores 18, and the corpus p5
  is 5. That claim was repaired in the code by slice 2's round 2 and left
  standing here — the same defect, in the artifact instead of the gate, which
  is exactly what the midpoint round exists to catch.
- Verification cadence: per commit, the installed git pre-commit hook lane plus
  the slice's own targeted pytest node ids. Per slice, reproduction control
  before repair, regression tests, one or two bounded fresh-eye review rounds,
  a checked-in critique artifact recording them, then the locked
  `run_slice_closeout.py` producer run — in that order. After slice 2, one
  bounded midpoint goal-claims review. Per bundle, one SERIAL full pytest run,
  the broad quality lane, the armed changed-line lane over this goal's own
  committed range, then the closeout disposition review, then `retro`.
- Slice review packet: intent, the row ids in the batch, changed files with
  owning/generated surfaces (including the plugin mirror), the reproduction
  control and its recorded pre-repair verdict, the measurement output when the
  repair refuses checked-in content, expected invariants, tests, non-claims,
  out-of-scope lines, and the questions the batch could not answer itself.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Reproduce and disposition 9 rows of the
[2026-07-28 evidence-surface triage sweep](../audit/2026-07-28-evidence-surface-triage-sweep.md)
— S2, S9, S10, S12, S13, S23, S24, S28, S35 — batched by REPAIR SHAPE rather
than one row at a time, so a shared repair is written once per batch.

**Provenance, stated before the defect summaries because it governs them: all
nine rows are `SUBAGENT-CONFIRMED`, which the sweep itself defines as "not to be
cited as proof without re-running."** Everything below is the sweep's CLAIM, not
this goal's finding. Each row is reproduced in the parent with a control before
any repair is written, and a row that does not reproduce is dispositioned as
REFUTED or returned to LEAD rather than repaired.

The four batches, with the sweep's claimed defect for each row:

- **Batch A — an absent or malformed input reads as a matching one.** S24 (a
  malformed `issue-adapter.yaml` returns `valid: true` and silently falls back
  to the hardcoded org), S28 (`--write-baseline` over a truncated/legacy
  baseline writes a new one with no delta confirmation), S35 (a missing codex
  plugin / marketplace surface produces no drift entry, so deleted reads
  identically to matching).
- **Batch B — a self-declaration decides whether the floor runs, and token
  presence stands in for engagement.** S9 (the artifact's own `Date:` line
  decides whether the inventory-consumption floor runs at all), S10 (field
  engagement is `\b<field>\b` presence, so an explicit negation plus five `n/a`
  stubs satisfies it).
- **Batch C — the same, in the closeout-delegation parser.** S12 (any PR
  number, runbook step number, or heading anchor in a delegated-proof item
  marks it RESOLVED, including one reading `— NOT DONE, still pending`), S13
  (an absent or blank `Closeout mode:` line yields empty `mode_tokens`, so a
  goal that visibly delegates external proof passes as standalone).
- **Batch D — two singletons with no siblings.** S23 (a failed verdict is
  claimed to still emit a `carrier-checked:` confirmation line), S2 (a stray
  unmatched backtick makes a real cross-line inline-code span report clean).

**These batch letters are this goal's own grouping and do NOT correspond to the
sweep table's `class` column** — the sweep's `(a)` is degenerate-input-returns-PASS
and its `(h)` is self-declared-field-decides-the-floor. Cross-reference by row
id, never by letter.

**Batching honesty:** batches B and C group by FILE, not by class, and that is
deliberate. S9/S10 live in one `main()` and S12/S13 in one parse function;
splitting them would put two independent repairs on the same function in
different slices, which is the collision the prior batch's round 2 caught (F3).
S13's shape is batch A's, and S9's is batch B's own — the file wins here, and
this sentence is the record that it was a choice.

**Source handoff entry #2: The sweep's high rows — 4 of 14 closed 2026-08-01, 9 left**

> S1/S26/S30/S32
>    went as ONE batch (all were "a zero denominator renders a PASS"), with the two
>    review rounds run three-abreast: 6 reviewers, 2 rounds, ~4 min wall-clock each.
>    That is the batching lever, now tested. Left:
>    S2/S9/S10/S12/S13/S23/S24/S28/S35, plus S31 (NARROWED, not closed — its arming
>    question is [D45](../../docs/deferred-decisions.md)) and S110-S113 as newer LEADs.
>    Batch by CLASS, not by file: the shared repair was written once.

(The D45 link in that quote is rebased to this file's location; the source
handoff writes it repo-doc-relative.)

## Non-Goals

- **S31 is explicitly out of scope** (operator decision, 2026-08-01). Its real
  repair — moving the exemption declaration out of the audited file into the
  adapter — is a contract change for every consumer repo, and
  [D45](../../docs/deferred-decisions.md) already records that it deserves its
  own slice. This goal does not narrow S31 further and does not arm
  `--require-evaluated-scope` in `run-quality.sh`; D45 stays deferred.
- **These 9 are not the sweep's whole remaining-high set, and this goal does not
  claim they are.** Also open at high severity and NOT in scope: S15 (PARTIAL —
  the pre-rule scope verdict discloses its basis but the self-declared `Created:`
  line still decides whether the floor runs), S36 and S37 (LEADs, never
  reproduced), S111 (PARENT-CONFIRMED, a glob-level empty denominator, separately
  owned), S31 above. S8 is already REFUTED and needs nothing.
- **S110–S113 are out of scope**, and the handoff's "newer LEADs" shorthand
  undersells them: S110 is a LEAD opened 2026-07-31, S113 a 2026-08-01 LEAD, but
  S111 and S112 are both PARENT-CONFIRMED (the sweep's strongest status).
- Not a release: no plugin version bump, no publish, no marketplace change.
- No push, no CI dispatch, no live `cautilus evaluate` run.
- Do not absorb adjacent handoff entries (the E-cluster, the disposition
  ledger, issue #467) beyond this chunk.

## Boundaries

- In scope, one file per row-GROUP (two files carry two rows each):
  `skills/public/issue/scripts/resolve_adapter.py` (S24),
  `skills/public/quality/scripts/dup_ratchet_rebaseline.py` (S28),
  `skills/public/release/scripts/current_release.py` (S35),
  `scripts/validate_inventory_consumption.py` (S9 **and** S10),
  `skills/public/achieve/scripts/goal_artifact_closeout_delegation.py`
  (S12 **and** S13), `skills/public/issue/scripts/issue_verify_closeout.py`
  (S23), `scripts/check_markdown_inline_code.py` (S2). Every one of the seven
  has a plugin mirror under `plugins/charness/`, so mirror sync is mandatory,
  not conditional. Tests and the sweep artifact's own rows are in scope too.
- **Also in scope, because this goal edits it: the sweep header's CLOSED count
  is wrong.** The header asserts 29 CLOSED; the table carries 33 rows whose
  status begins CLOSED (the 2026-07-31 group lists only S4 and S11 while the
  table shows S3/S4/S5/S7/S11/S21/S22). Reconcile the header to the table before
  writing this goal's own closures into it, or the new count inherits the drift.
- **Arming posture (operator decision, 2026-08-01): measure, then decide.**
  When a repair would newly refuse checked-in content, write a script that
  counts the actual refusals across the real corpus and record its output
  before choosing. A number that can be re-run decides; a sentence does not.
  This is the pattern that saved S3's floor after two thresholds defended only
  by prose had already died.
- Every changed file here renders a verdict about other code or artifacts, so
  each slice owes a bounded review round, and a SECOND round reading the
  repaired surface **whenever round 1 produced repairs**. A round 1 that
  produced none discharges the obligation and is recorded as such. Cap: two
  rounds; round-2 repairs ship accepted-unreviewed and are named in the critique
  artifact. Both rounds run BEFORE the locked `--produce-mutation-coverage`
  producer run — a round-2 repair after the producer invalidates the fingerprint.
- **Correction to the auto-draft:** `deferred-decisions.md` is NOT missing. The
  chunker resolved the source entry's relative link against the repo root; the
  file exists at [docs/deferred-decisions.md](../../docs/deferred-decisions.md).
- Portable per implementation-discipline: no host-specific assumption; plugin
  mirrors sync before validators run.
- Stop conditions, each with an observable trigger and a named output:
  - A repair that would require a consumer repo to change a file or field IT
    authors (adapter YAML, `.agents/` config, a workflow file), or would turn a
    consumer's lane red with no local remedy, stops at legible-plus-deferred:
    the diagnostic ships, the refusal does not, and the arming question is
    written into `docs/deferred-decisions.md` as a numbered entry. This is what
    made S31 its own slice.
  - A row that does not reproduce is marked `REFUTED (<reason>, 2026-08-01)` or
    returned to `LEAD` in the sweep table, with the exact control command and
    its observed output recorded inline, and the goal states it was not
    repaired. It is not silently dropped.
  - Concurrent pytest invocations are forbidden. S112 recorded 17 false
    failures and 21 false errors from exactly that, against a tree that is 6403
    passed when run serially.

## User Acceptance

- Every one of the 9 rows carries a disposition in the sweep table — CLOSED,
  NARROWED, OPEN, or REFUTED — with a reason. No row keeps an unchanged status
  and no explanation. The CLOSED count moves to (reconciled base) + N, where N
  is whatever actually closed and is stated at closeout; there is no fixed
  target number, because the stop conditions above permit a correct run that
  closes fewer than 9.
- For each closed row, the artifact names the reproduction control (the exact
  command and the pre-repair verdict, observed in the parent) and the
  regression test that fails without the repair.
- Each slice's review rounds are recorded in a checked-in
  `charness-artifacts/critique/2026-08-01-slice-N-*.md` naming reviewer
  provenance, delivery state, round-2 accepted-unreviewed repairs, and the
  `reviewer_boundary_fingerprint.py` snapshot/verify result. The goal artifact
  links them rather than restating them. (The prior goal's acceptance required
  this and none existed until closeout forced six retroactive writes — a
  self-report inside the artifact being judged, which is sweep row S11's own
  shape.)
- Where a repair was measured rather than argued, the measuring script is
  checked in and its recorded output linked, so the threshold can be re-run.
- Where a repair was deliberately left unarmed, the goal says so in the same
  place as the closures and files the arming question as a numbered deferred
  decision.
- The sweep header's CLOSED count agrees with its own table.
- `./scripts/run-quality.sh` passes at the end, and the full pytest suite
  passes in a serial run.

**Who reads these:** bullets 1, 2, 3 and 5 are claims about the ARTIFACT, not
the code, and no deterministic gate reads them (`check_doc_authoring_preflight.py`
is form-only and self-describes as an affordance, not a gate; there is no
deferred-decisions validator in this repo). The midpoint goal-claims review and
the closeout disposition review are their designated readers, diffing the
per-row claims against the owning records and the commits.

## Agent Verification Plan

**Low-cost, per commit** (cheap deterministic, run every time):

- the installed git pre-commit hook (its output is labelled
  `charness pre-commit:` — that string is a label, not a command); previewable
  with `python3 scripts/run_slice_closeout.py --predict-commit`.
- targeted `python3 -m pytest -q <node ids>` for the slice's own tests.
- `python3 scripts/check_doc_authoring_preflight.py --path <artifact>` when the
  sweep artifact or this goal is edited.

**Per slice** (higher cost, at the slice boundary), in this order:

1. a reproduction control recorded BEFORE the repair: the exact command, the
   exact observed pre-repair verdict, run in the parent worktree. A row that
   cannot be reproduced does not get repaired.
2. the repair, its regression tests (failing on the pre-repair code), and the
   plugin-mirror sync.
3. when the repair refuses checked-in content: a checked-in measuring script
   plus its recorded output over the real corpus.
4. bounded fresh-eye review round 1; round 2 reading the REPAIRED surface if
   round 1 produced repairs. Reviewers run read-only in the shared parent
   worktree, spawned as `bounded-reviewer`, unnamed, with
   `reviewer_boundary_fingerprint.py` snapshot/verify around each round.
   Batches A, B, C and D are mutually independent, so their round-1 reviews are
   spawned CONCURRENTLY and the parent works the next batch's reproduction
   controls while they run — 84.6 min of `sleep` against 50.5 min of review was
   the last session's largest measured lever.
5. one critique artifact per slice recording both rounds.
6. `python3 scripts/run_slice_closeout.py --verification-lock
   --produce-mutation-coverage` — last, because a round-2 repair after the
   producer invalidates the coverage fingerprint.

**Midpoint** (after the merged B/C slice, contract-triggered by a goal with 3+ slices): one
bounded goal-claims review reading this artifact's per-row claims against the
owning records and the commits — a different question from "is this repair
correct", answered by a different packet.

**Per bundle** (final stage), in this order:

- one SERIAL `python3 -m pytest -q` full-suite run. Never concurrent.
- `./scripts/run-quality.sh` (a bash script — do not invoke it with `python3`).
- after the bundle's final commit, with a clean mutation pool:
  `python3 scripts/prepush_focused_changed_line_coverage.py --base-sha <sha
  before this goal's first commit> --refuse-unestablished`. Honest scope: the
  flag refuses a dirty pool or an empty intersection; it does NOT cover changed
  pool files that map to no standing test — those return status `unproven` at
  exit 0. Record `unmapped_changed_pool_files` from the payload as a residual.
- the closeout disposition review, then fold its findings, then `retro` — in
  that order, not beside each other.

**Explicit non-claims at this planning stage:** no CI dispatch, no push, no live
`cautilus evaluate`, and no claim about consumer-repo behavior beyond what a
local run establishes.

**Expected duplication pressure — source side first.** Batch A writes one
`absent` / `unparseable` / `matching` distinction into three separate scripts,
which creates a new clone family by construction: extract a shared helper rather
than triplicate it, expect the dup-ratchet to fire on the REPAIR and not only on
the tests, and classify rather than re-baseline. On the test side, batches A and
B each add refusal tests across sibling surfaces with near-identical shapes;
prefer one parametrized test over three copy-pasted ones, and state per slice
whether new duplication is slice-local or accumulated suite debt.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | DONE — Batch A — an absent or malformed input must not read as a matching one: S24, S28, S35 | Three independent files with the cheapest reproductions and no cross-file coupling; nothing else in the goal depends on it, so it is the safest place to establish the reproduce-control-first rhythm | Three reproduction controls; one shared helper distinguishing `absent`, `unparseable`, and `matching`; regression tests per row; mirror sync; critique artifact | done — S28 CLOSED, S24 and S35 NARROWED |
| 2 | DONE — Batch B — S9 and S10 together in `validate_inventory_consumption.py` | **S9 strictly dominates S10**: the `artifact_date < ENFORCED_FROM_DATE` branch returns 0 at line ~117, before S10's engagement floor at ~146 ever runs. Repairing S10 alone leaves a floor that a backdated artifact never reaches, and repairing them in separate slices puts two edits on one `main()` after a review has already signed off on it | The backdated-vs-today control and the negation-plus-`n/a`-stub artifact; a measured count of checked-in quality artifacts that would newly fail, from a checked-in script; both repairs in one pass; critique artifact | done — S9 and S10 NARROWED |
| 3 | DONE — Batch C — S12 and S13 together in `goal_artifact_closeout_delegation.py` | Same file, same `parse_closeout_delegation` function, two simultaneous edits otherwise. **Ran WITH slice 2 rather than after it** — they are one class, so one reproduction pass and one pair of review rounds covered both; the midpoint review therefore lands after the merged B/C slice, not between them | The `— NOT DONE, still pending` control; the absent/blank `Closeout mode:` control; a distinct undeclared mode rather than a default to `standalone`; an explicit statement of whether the repair changes behavior for goals with NO `## Closeout Delegation` section, plus a run of the repaired validator against this goal artifact; critique artifact | done — S13 CLOSED, S12 NARROWED and its ROW corrected |
| 4 | DONE — Batch D — S23 and S2, two singletons | Last because neither unlocks nor is unlocked by anything. **S23 carried a REFUTE prediction that the reproduction FALSIFIED.** The `if ok else None` guard is real and predates the sweep, but it runs before `_fold_proof_mismatch`, which flips the verdict afterward. S23 reproduces and is CLOSED | S23: the failed-verdict control with its observed output, and either the second path or a `REFUTED (design posture, 2026-08-01)` disposition. S2: the stray-backtick control, a corrected span-pairing rule, and a run over the repo's real markdown corpus showing no new false positives; critique artifact | pending |

## Discuss before activation

RESOLVED — three consequential decisions were put to the operator in the
2026-08-01 shaping interview and answered there. They are recorded here so
activation is not a silent inheritance:

1. **Broad bundled scope — RESOLVED, approved.** Nine rows across seven files in
   four slices is a deliberately broad bundle; the operator chose no timebox and
   run-to-all-9-dispositioned over a single-class stop. The batching lever this
   depends on was measured on the prior batch, not assumed.
2. **Proof-level non-claims — RESOLVED, approved.** This goal will not push, will
   not dispatch CI, and will not run `cautilus`. It claims nothing about consumer
   repos. It also does NOT claim to close the sweep's remaining high rows: S15,
   S31, S36, S37 and S111 stay open by scope decision, and the goal title says
   "9 of".
3. **Arming posture — RESOLVED, approved: measure then decide, per row.** Where a
   repair would newly refuse checked-in content, the run proceeds with the repair
   legible-but-unarmed and files the arming question as a numbered deferred
   decision. It does NOT block waiting for the operator. The measurement output
   is what the operator later reads to arm or keep deferred.

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

Open at shaping time:

- Decision: whether a slice-2 arming that would newly refuse checked-in quality
  artifacts is paid for now (fix or exempt the artifacts) or stays deferred.
- Owner: operator.
- Why deferred: the measurement that decides it does not exist yet.
- Unblock action: read the slice-2 measurement output and answer arm / defer.
  Per decision 3 above the run does NOT wait — it ships the repair unarmed and
  continues.
- Revisit trigger: slice 2's measuring script producing a refusal count.

## Slice Log

### Slice 1: Slice 1 — batch A: an absent input is not a matching input (S24, S28, S35)

- Objective: Reproduce S24/S28/S35 in the parent with controls, then write the shared repair once: an absent, unreadable, or unparsed input must not render the same verdict as a matching one.
- Why this approach: Three independent files with the cheapest reproductions and no cross-file coupling, so it was the safest place to establish the reproduce-control-before-repair rhythm. All three reproduced; S24 reproduced STRONGER than the sweep claimed (the top-level-list case emitted no warning at all, because the isinstance(raw, dict) guard was unreachable — load_yaml always returns a dict).
- Commits: `faf355f5` (the slice), `5f99e842` (the operator-requested mid-run retro,
  `charness-artifacts/retro/2026-08-01-slice-1-absent-input-batch-retro.md` — the
  verification plan sequences `retro` last, so this one was out of order by request).
- Non-claim, producer step: the plan's step 6 specifies
  `run_slice_closeout.py --verification-lock --produce-mutation-coverage`. This slice ran
  `--skip-broad-pytest --ack-cautilus-skill-review` instead, so no mutation-coverage
  fingerprint was produced and the broad pytest proof is deferred to the bundle. The
  substitution is recorded rather than implied.
- Non-claim, fingerprint channel: `reviewer_boundary_fingerprint.py` snapshot opened each
  review window; the matching `verify` was NOT run for any of them, because the parent
  edits in-tree between rounds and `--parent-path` was not used. Integrity rests on
  `git status --porcelain`. The approvals are accepted with that residual, not quarantined.
- Boundaries reconciliation: the `## Boundaries` in-scope list named seven scripts. The
  run widened to the shared parse/report channel and its consumers; the per-slice
  `What changed` lists above are authoritative, and the midpoint review confirmed no
  Non-Goal was crossed.
- What changed: scripts/adapter_lib.py, scripts/simple_skill_adapter_lib.py, scripts/measure_adapter_yaml_uninterpreted.py (new), skills/public/issue/scripts/resolve_adapter.py, skills/public/quality/scripts/dup_ratchet_rebaseline.py, skills/public/release/scripts/{current_release,resolve_adapter}.py, skills/public/release/{references/adapter-contract.md,adapter.example.yaml}, .agents/release-adapter.yaml, docs/deferred-decisions.md (D46), docs/public-skill-dogfood.json, charness-artifacts/{audit/2026-07-28-evidence-surface-triage-sweep.md,probe/2026-08-01-adapter-yaml-uninterpreted.json,quality/dup-review.json,critique/2026-08-01-slice-1-absent-input-batch.md}, tests/quality_gates/test_absent_input_is_not_a_matching_input.py (new), plus the plugins/ mirrors.
- Alternatives rejected: Arming the S24 refusal (valid: false) was written, then WITHDRAWN: the goal's own stop condition routes a repair on a consumer-authored file to legible-plus-deferred, and refusing an adapter turns a consumer's whole issue lane red for a typo. A residual-length floor for engagement was NOT used here. Re-baselining the dup-ratchet was refused in favour of extracting three shared helpers and classifying two irreducible families.
- Targeted verification: Reproduction controls recorded before repair for all three rows. 38 new tests; 13 of the first cut failed against HEAD in a detached worktree. 160 targeted regression tests green. Parser behavior proven identical to HEAD across the 74 files git ls-files lists, by loading both module versions side by side. run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review: completed. Measurement recorded at charness-artifacts/probe/2026-08-01-adapter-yaml-uninterpreted.json with provenance.
- Test duplication pressure: Predicted and hit: the dup-ratchet hard-blocked four times as the repairs rotated fingerprints — exactly the closeout-boundary treadmill the 2026-08-01 retro named. Resolved by extracting _line_shape, _is_ignorable, _mapping_value, uninterpreted_warnings, parse_failure_error and one unified adapter payload builder; two remaining families classified intentional with reasoning, none re-baselined.
- Critique: charness-artifacts/critique/2026-08-01-slice-1-absent-input-batch.md — 5 bounded reviewers, 2 rounds. Round 1: 6 blockers (arming violated the stop condition; the measurement missed the governed population; a fourth drop site was uninstrumented; the S24 defect produces the S35 defect; expected-is-None suppressed all drift; --- became a false refusal). Round 2 read the REPAIRS and found 5 more, three CREATED by round 1: a document-marker skip that changed load_yaml's result, absent_surfaces still built from the None test it replaced, and a typed-refusal guard on one loader of two. Round-2 repairs ship accepted-unreviewed under the two-round cap.
- Off-goal findings: validate_inventory_consumption.py crashes with a traceback on relative_to when the artifact or consumer-fields path sits outside repo-root (three call sites) — a false RED, not a false green; found while reproducing S9. The handoff chunker's issue-source path reads adapter['data'] without checking valid or warnings (recorded in D46, not repaired).
- Lessons carried forward: S24 and S35 close as NARROWED, not CLOSED, and the sweep rows say what stays open. S35's own repair is an instance of the class the sweep catalogues — a self-declared adapter field decides whether the floor fires — and the closure admits it. Batch C's S12 only half-reproduces: the sweep's claim that a runbook step number or heading anchor marks a delegated proof RESOLVED is false; only #NNN matches.
- Metrics:

### Slice 2: Slices 2-3 — batches B and C: a declaration is not its own corroboration (S9, S10, S12, S13)

- Objective: Reproduce S9/S10/S12/S13 with controls, then repair one class in two files: what the audited content says about itself is not proof.
- Why this approach: Batches B and C were taken together because they are one class, and because their round-1 reviews could run concurrently while the parent worked the other batch. S9/S10 share a main(); S12/S13 share a parse function.
- Commits: `dac61db7`.
- Non-claim, producer step: ran `--skip-broad-pytest --ack-cautilus-skill-review`, not the
  plan's `--verification-lock --produce-mutation-coverage`. Same substitution as slice 1.
- Non-claim, fingerprint channel: snapshot only, `verify` not run, integrity from
  `git status --porcelain`. Accepted with the residual.
- What changed: scripts/validate_inventory_consumption.py, scripts/measure_inventory_consumption_floor.py (new), scripts/repo_path_display.py (new), scripts/control_plane_lib.py, scripts/disposition_form.py, skills/public/achieve/scripts/{goal_artifact_closeout_delegation,describe_goal_closeout_shape}.py, skills/public/achieve/references/{goal-artifact,lifecycle-after}.md, docs/{deferred-decisions,prescribed-skill-closeout-contract}.md, charness-artifacts/{audit,probe,quality/dup-review.json,critique}, tests/quality_gates/{test_a_declaration_is_not_its_own_corroboration.py (new),test_inventory_consumption.py}, plus mirrors.
- Alternatives rejected: Arming the value-marker rule for inventory engagement was measured (5 checked-in reviews refused) and DECLINED -> D47. Forking a fourth date channel rather than extending critique_enforcement_scope.observed_date was chosen because the default artifact is a rolling pointer with no filename date, and the reason is recorded in the critique rather than left implicit. Re-baselining the dup-ratchet was refused five times in favour of one real extraction (repo_path_display, which two surfaces had grown independently) plus four classifications.
- Targeted verification: Reproduction controls for all four rows before repair. 30 new tests plus 13 existing; 9 of the first cut failed against HEAD in a detached worktree. Corpus measurements: 0 of 105 quality artifacts newly refused (compared against HEAD's validator from a detached worktree), 0 of 145 goal artifacts refused, label-value corpus minimum 7 against a floor of 5. run_slice_closeout --skip-broad-pytest --ack-cautilus-skill-review: completed.
- Test duplication pressure: FIVE dup-ratchet hard-blocks at the closeout boundary this slice, after four in slice 1 and four last session. One produced a real extraction; four were classifications of rotated boilerplate. The retro's proposed improvement — run the dup gate at the first edit to a gated file — now has nine measured instances behind it.
- Critique: charness-artifacts/critique/2026-08-01-slice-2-3-declaration-corroboration.md — 4 reviewers, 2 rounds. Round 1 (10 blockers): S9's exploit survived on uncommitted files, the 'refuses a stub not a lie' comment was false for three shapes, a length floor cannot fix ordinary-word field names, and the measurement never measured the label floors. Round 2 (5 blockers, all on round 1's repairs, both reviewers independently finding the first): the comment defending the floor asserted a measurement the slice's own probe and test refute; a failed git status read as a clean tree; 'Corroborated by HEAD' was printed for bytes git never saw; the S13 refusal wrote to a key no consumer reads so the shape describer rendered the refused floor as SATISFIED; and the S12 negation guard refused items for words inside their own reason.
- Off-goal findings: goal_artifact_floor_grammar.parse_created_date is consumed by FIVE achieve floors with no corroboration at all — S15's family, and a one-helper repair since goal artifacts carry a filename date critique_enforcement_scope.observed_date already reads. Recorded, not repaired.
- Lessons carried forward: Only S13 CLOSED. S9, S10 and S12 are NARROWED, and S12's ROW is corrected: two of its three stated triggers never reproduced. The headline S12 class — a pointer is not the proof — is untouched, because a bare reference with no negation still resolves.
- Metrics:

### Slice 3: Slice 4 — batch D: a refused verdict states its refusal (S23, S2)

- Objective: Reproduce S23 and S2, then repair: a verdict that gets refused after its sentence was rendered must drop the sentence, and a checker whose span pairing is shifted must not report clean.
- Why this approach: Two singletons with no siblings and no cross-dependency; last because neither unlocks nor is unlocked by anything.
- Commits: pending — committed with this slice
- What changed: skills/public/issue/scripts/issue_verify_closeout.py, skills/public/release/scripts/release_issue_closeout_message.py, scripts/check_markdown_inline_code.py, tests/quality_gates/test_a_refused_verdict_states_its_refusal.py (new), the sweep rows, plus mirrors.
- Alternatives rejected: Closing S23 as REFUTED on the strength of the plan's prediction — falsified by the reproduction. Building a full CommonMark backtick stack for S2 so the reported line names the real span — declined as more machinery than the advisory check warrants, and recorded as the row's residual instead.
- Targeted verification: Reproduction controls before repair for both rows. 11 new tests; 4 of the first cut failed against HEAD in a detached worktree. Measured before adding S2's class: 0 files with an odd single-backtick count in the checker's own scope, 3 repo-wide all under the already-excluded charness-artifacts. run_slice_closeout --skip-broad-pytest --ack-cautilus-skill-review: completed.
- Test duplication pressure: No new dup-ratchet family this slice — the first in three. The two repairs touch unrelated files and neither adds a boilerplate shape.
- Critique: charness-artifacts/critique/2026-08-01-slice-4-a-refused-verdict-states-its-refusal.md — 2 reviewers, ONE round. Round 2 was NOT run and that is a recorded gap, not a discharge: round 1 produced repairs, and the two earlier slices each had round 2 catch defects round 1's repairs created.
- Off-goal findings: none beyond what slices 1-3 already recorded.
- Lessons carried forward: The plan's REFUTE prediction for S23 was wrong, and a round-1 reviewer reached the same wrong conclusion from the same evidence. Only the reproduction settled it. Round 1 also found the S23 class open one level up in the release carrier — the fix's own class, in a file the row never named.
- Metrics:

## Context Sources

- Source: handoff entry #2 (The sweep's high rows — 4 of 14 closed 2026-08-01,
  9 left) — see [docs/handoff.md](../../docs/handoff.md).
- The sweep itself, which owns each row's status vocabulary, its provenance
  tiers, and the what-this-does-NOT-close statements:
  [2026-07-28 evidence-surface triage sweep](../audit/2026-07-28-evidence-surface-triage-sweep.md).
- The immediately prior batch of this same shape (S1/S26/S30/S32, closed
  2026-08-01) and its critique
  [2026-08-01-sweep-s1-s26-s30-s32-zero-denominator-batch.md](../critique/2026-08-01-sweep-s1-s26-s30-s32-zero-denominator-batch.md)
  — the pattern this goal reuses, including its record of round 2 catching five
  further findings, three of them created or missed by round 1's own repairs.
- [D45](../../docs/deferred-decisions.md) — why S31 is out of scope here.
- [docs/conventions/operating-contract.md](../../docs/conventions/operating-contract.md)
  Critique Discipline — the second-round trigger and discharge rule, the
  midpoint goal-claims review, and the closeout disposition review.
- [docs/conventions/implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
  — the round-1 → round-2 → producer ordering and the mutation-coverage lock.
- [charness-artifacts/retro/recent-lessons.md](../retro/recent-lessons.md) and
  the [2026-08-01 session retro](../retro/2026-08-01-session-retro.md) — the
  concurrent-review lever, the dup-ratchet-at-closeout trap, and the
  disposition-review-then-retro ordering.
- S112 (concurrent pytest runners produce false failures) — the reason the
  bundle gate is specified as a serial run.

## Interview Decisions

- **S31 scope.** Family considered: exclude / include with the adapter-channel
  contract change / include but leave unarmed. Chosen: **exclude**. Rejected
  alternatives: including it makes a consumer-repo contract change ride along on
  a defect-repair goal, which D45 already argued against by name; including it
  unarmed would repeat the narrowing S26/S30 already did without closing
  anything new. `axis: host/consumer-repo` — the exemption channel varies per
  consuming repo, which is exactly why it belongs in an adapter and why it is
  not a single-point decision this goal can make.
- **Arming posture when a repair refuses checked-in content.** Family
  considered: always fail-closed / always legible-only / measure then decide.
  Chosen: **measure then decide**, per row. Rejected alternatives: always
  fail-closed risks a permanently red quality lane with no honest remediation
  (the trap D45 records for S31); always legible-only would leave several of the
  9 substantively open while reading as worked. `single-point: this is a
  repo-local posture for this repo's own corpus`, and each measurement is
  corpus-specific rather than a global threshold.
- **Timebox.** Family considered: none (macro outcome) / 3h / one class batch.
  Chosen: **none — run to all 9 rows dispositioned**. Rejected alternatives: a
  3h box would cut mid-batch given the review rounds; a single-batch stop was
  the shape of the last session and the lever it was testing is now proven.
  `single-point: operator's stated budget for this goal`.
- **Mode.** Not asked — the contract settles it: `/achieve` shapes and stops,
  `/goal` pursues. Assumed mode: implementation-continuation once activated.

## Plan Critique Findings

Three bounded read-only fresh-eye reviewers ran concurrently over the shaped
draft on 2026-08-01, before activation: scope/claim fidelity against the owning
records, verification sufficiency and command reality, and sequencing against
this repo's known repeat traps. All were spawned unnamed as `bounded-reviewer`
and returned their findings directly. They produced 6 + 5 + 6 blockers and 9
nits; the draft they read is not the draft above.

**Blockers folded into the plan:**

- The draft asserted nine defects as fact. All nine are `SUBAGENT-CONFIRMED`,
  which the sweep defines as not citable without re-running. `## Goal` now leads
  with provenance and frames every row as a claim to reproduce.
- **S23 does not reproduce at HEAD as written.** `issue_verify_closeout.py:293`
  reads `"line": ... if ok else None`, introduced 2026-07-20 in `18483dc9` —
  before the sweep. Verified in the parent with `git log -L`. Slice 4 now
  carries an explicit REFUTE prediction rather than a planned repair.
- "The 9 remaining high rows" was false: S15 (PARTIAL), S31 (OPEN), S36/S37
  (LEAD) and S111 (PARENT-CONFIRMED) are also open at high severity. Title and
  `## Non-Goals` corrected; verified by counting the table's own status column.
- The `29 → 38` acceptance arithmetic inherited a header/table drift: the header
  says 29 CLOSED, the table carries 33. Verified by counting. The fixed target
  is gone and reconciling the header is now in scope.
- The batch letters `(a)`–`(d)` collided with the sweep table's own `class`
  column, where the same letters mean different things. Relabelled A–D with an
  explicit cross-reference-by-row-id warning.
- `python3 scripts/run-quality.sh` would have died on a SyntaxError — it is a
  bash script. Corrected to `./scripts/run-quality.sh` in both places.
- The contract-mandated **midpoint goal-claims review** (trigger: 3+ slices) was
  absent, as was the closeout disposition review and the retro-after-disposition
  ordering. All three are now in the verification plan.
- The per-slice `run_slice_closeout.py --verification-lock
  --produce-mutation-coverage` step and its round-1 → round-2 → producer
  ordering constraint were absent.
- **The slice-1 → slice-2 unlock was invented.** S13's repair shares no module,
  helper, or fixture with batch A; the "absent != agreeing rule is reused"
  claim was an analogy dressed as a dependency, and it was the only stated
  reason to serialize. Deleted; batches are now declared mutually independent so
  their review rounds batch concurrently.
- **S9 strictly dominates S10 in the same `main()`** — S9's date branch returns
  0 before S10's engagement floor runs — so the draft's split (S10 in one slice,
  S9 two slices later) would have shipped an unreachable repair and then
  re-edited a reviewed file. S9 moved into batch B with S10; S13 stays with S12
  for the same file-collision reason, now stated as a deliberate exception to
  class-batching rather than hidden behind a re-class.
- Three acceptance bullets had no reader. Named the midpoint and closeout
  reviews as their designated readers, and added the per-slice critique artifact
  to acceptance — the criterion the prior goal left unmet for all five slices.

**Nits folded:** the round-2 discharge condition (a clean round 1 discharges the
obligation — the draft over-stated it as unconditional); `charness pre-commit`
is an output label, not a command; `--refuse-unestablished` does not cover
changed pool files that map to no test, and the gate needs a clean pool, so the
bundle step is now sequenced after the final commit with `unmapped_changed_pool_files`
recorded as a residual; the prior batch's round 2 found five findings, not two;
source-side dup-ratchet pressure from writing one distinction into three files;
both non-pytest stop conditions rewritten with observable triggers and named
outputs; the Operator Decision Queue no longer says "stop there" while the
timebox says run-to-completion; S110–S113 mis-described; the quoted D45 link
rebased for this file's directory.

**Raised and NOT folded (over-worry or out of scope):** none of the reviewers'
findings were classified as over-worry — every blocker and nit above was either
folded or, in S23's case, converted into a prediction the run will test. The one
item deliberately left as-is is the batch-B/C file-grouping itself: two reviewers
flagged it as contradicting "batch by CLASS not by file", and the plan keeps the
grouping while stating the contradiction openly, because the file-collision risk
it avoids was measured on the prior batch and the class-purity is not.

**Reviewer provenance:** three `bounded-reviewer` subagents, unnamed, read-only
(Read/Grep/Glob only), shared parent worktree, 2026-08-01. Worktree integrity
after the round: `git status --porcelain` showed only this untracked goal
artifact and HEAD unmoved at `7efa0240`. **Non-claim:** the
`reviewer_boundary_fingerprint.py` snapshot/verify pair was NOT correctly
established for this plan-critique round — the snapshot was captured with a
mis-shaped invocation and its verify was refused for missing keys, so integrity
here rests on the `git status` check above rather than on the fingerprint
channel. The slice reviews will use the tool correctly.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro

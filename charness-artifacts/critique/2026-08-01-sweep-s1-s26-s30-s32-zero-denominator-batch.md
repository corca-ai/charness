# Sweep S1 S26 S30 S32 zero denominator batch

Date: 2026-08-01

## Decision Under Review

Closing four triage-sweep rows that are one class — **a denominator that reached
zero rendering a PASS** — across three subsystems, with the review rounds BATCHED
across slices rather than run in series (the lever the 2026-08-01 retro measured
and the D44 slice left unspent).

## Failure Angles

- **The rows are stale and no longer reproduce.** All four were reproduced at HEAD
  before any edit, each with a control: S1 `build_per_file_floor_report([])` →
  `status: enforced`; S30 the identical workflow as `.yaml` → 0 scanned/exit 0 vs
  `.yml` → parity issue/exit 1; S26 an all-`uses:` job → exit 0 under
  `--require-canonical-gate-match`; S32 a typo'd glob → `ok` exit 0 vs the
  corrected glob → fail exit 1.
- **The repair invents a new refusal that breaks honest consumer repos.** It did,
  twice, and both were caught: `--require-canonical-gate-match` widened onto
  composite actions (split into its own flag), and the S32 refusal firing on a
  scope emptied by a deliberate exemption (caught by the repo's own test before
  any reviewer).
- **The repair carries the class it repairs.** It did, in three separate places —
  see F1, F2, F7.
- **The batch hides a row that is not actually closed.** S31 is not closed and is
  now marked OPEN with what changed; the arming question is D45.
- **North-star check.** No gate here gained a terminal green; each gained a value
  in the payload plus an opt-in refusal, and the two flags that would make this
  repo's own lane red are deliberately unwired and recorded rather than silently
  armed.

## Counterweight Pass

- **Real, and the pattern this repo keeps measuring:** every one of the three
  round-1 reviews found the repair reproducing its own class. S1 keyed on the
  INPUT row count, so an all-exempt or all-unmeasured population kept the identical
  green one bucket over. S26's repair still dropped a job-level
  `jobs.<id>.uses:` — and shipped a comment declaring that drop correct. Round 2
  then found a THIRD shape (an unparseable `steps:` value) still escaping.
- **Real, and only a second round could see it:** two independent round-1 repairs
  on the same file collided. The `owner` string added for "name the right key" and
  the `surface_globs: []` refusal added for "declared empty is not absent" meet in
  a branch where `scope_declared` is False by construction, so the newest refusal
  printed the contract-level key — a false statement with a remedy that would not
  clear the failure and would silently drop every other term's scope.
- **Real:** the docs contradicted the gates. `adapter-contract.md` said the
  language field is "advisory by default" while the gate now exits 1 on an unread
  declared scope, and `maintainer-local-enforcement.md` documented a `--workflow-glob`
  that is no longer singular. Both corrected; the parity doc gained the scope rules.
- **Real, and correctly refused as a code change:** the dup-ratchet hard-failed on
  three new families my edits created. Two were fixed by adopting the existing
  owner (`git_inventory_lib.visible_repo_files`) and extracting
  `add_workflow_glob_arg` / `resolve_workflow_globs`; the two remnants — argparse
  scaffolding and an import block — are classified `intentional` with reasoning,
  not accepted into the baseline.
- **Over-worry, correctly:** demanding an exit-code change for S1. `main` already
  refuses when nothing was measured, and the one remaining green-over-unestablished
  shape needs every entry of a fixed nine-file `TARGET_FILES` to be a sub-30-statement
  file. Recorded in the code rather than wired.
- **Over-worry, correctly:** arming `--require-evaluated-scope` in `run-quality.sh`.
  It would make this repo's lane permanently red with no honest remedy short of
  deleting a legitimate exemption — the owner's toll to choose (D45).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_coverage_lib.py | action: fix | note: round 1 — the S1 repair keyed status/measurement_scope on len(files), so an all-exempt or all-unmeasured population still self-declared `enforced` with empty violations; repaired with a `compared` counter and `files_received` alongside `files_evaluated`
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/ci_local_gate_parity_lib.py | action: fix | note: round 1 — a job-level `jobs.<id>.uses:` reusable-workflow call still fell through the `not steps` skip into no bucket (reproduced by execution: exit 0, all buckets empty), and the slice's own new comment declared that skip correct
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/inventory_ubiquitous_language.py | action: fix | note: round 2 — the `surface_globs: []` refusal named the CONTRACT-level key, because `scope_declared` is False for exactly that case; two independent round-1 repairs colliding, with a remedy that would not clear the failure
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/adapter-contract.md | action: fix | note: round 2 — the consumer contract said the language field is "advisory by default" while the gate now exits 1 on an unread declared scope; docs/public-skill-dogfood.json carried the same false claim. Both corrected with the full hard-fail list and remedies
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/inventory_ubiquitous_language.py | action: fix | note: round 2 — the exemption advisory told operators files "were removed by exemption_globs" when none were configured, a fabricated cause on the built-in discovery fallback that an unconfigured consumer repo hits
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/inventory_ci_local_gate_parity.py | action: fix | note: round 1 — `--require-canonical-gate-match` was widened onto composite-action jobs, leaving honest consumers a choice between dropping real teeth and misusing a gate-policy marker; split into `--require-established-gate-match`
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/ci_local_gate_parity_lib.py | action: fix | note: round 2 — a `steps:` value the loader could not parse (a YAML flow sequence, valid Actions syntax) still landed in no bucket; the S26 escape in a third shape
- F8 | bin: act-before-ship | evidence: moderate | ref: scripts/check_coverage.py | action: fix | note: round 2 — the extraction left dead locals whose unconditional subscript raised before the fail-closed caveat could print, making that repair dead at its only production call site; and the round-1 fixture change silently un-covered the POPULATED arm, so no test observed the line that ships on every real run
- F9 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/quality/dup-review.json | action: document | note: the dup-ratchet hard-failed on three families this slice created; two removed by adopting `git_inventory_lib.visible_repo_files` and extracting the shared option helper, two remnants classified `intentional` with reasoning rather than re-baselined
- F10 | bin: valid-but-defer | evidence: moderate | ref: docs/deferred-decisions.md | action: document | note: this repo's own parity gate evaluates ZERO jobs (both workflows self-exempt), so its green establishes nothing; made legible and pinned, arming deferred to the owner as D45
- F11 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/inventory_ubiquitous_language.py | action: defer | note: 348 code lines against a 360 hard limit, and scripts/check_coverage.py at 443 against 480 — both inside the advisory warn band. Splitting a module mid-defect-repair is the reactive churn the advisory itself warns against; owed at the next change that adds lines (the D33 precedent)
- F12 | bin: over-worry | evidence: strong | ref: scripts/check_coverage.py | action: defer | note: making S1 an exit-code refusal — `main` already refuses when nothing was measured, and the residual shape needs every entry of a fixed nine-file TARGET_FILES to be sub-30-statement; recorded in the docstring instead
- F13 | bin: over-worry | evidence: moderate | ref: scripts/run-quality.sh | action: defer | note: arming --require-evaluated-scope in the broad lane; it runs in consumer repos too, where an all-composite CI is honest and would be permanently red

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (Claude Code typed read-only agent, session-model inheritance per the per-host split)
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawns, run_in_background=true, three concurrent per round
- Host exposure state: applied
- Application state: host-confirmed: six reviewers returned findings inline across two rounds (round 1: a1d42971ff1f12369, a0a527d59e85f37a1, a4aea85128510dff6; round 2: a4cc4d8e57bc13eb3, a53c9dac11545f6fe, ae63317940809e087)
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Two rounds, three bounded read-only reviewers per round, all six
spawned CONCURRENTLY — the batching lever the 2026-08-01 retro named and the D44
slice could not test. Boundary proven independently of reviewer self-report:
`reviewer_boundary_fingerprint.py` snapshot before each round and `verify` after
returned `{"ok": true, "verdict": "clean", "drift": []}` for both windows
(`w-20260731T195048Z-397258`, `w-20260731T201027Z-434858`). Round-2 repairs are
**accepted-unreviewed** under the two-round cap.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each reviewer received an inline scope naming its files, the defect, the repair, and per-slice adversarial questions. Round-2 packets additionally named every round-1 finding and the repair made in response. -->

## Boundary Ownership

- Producer: three proof surfaces — `check_coverage_lib.build_per_file_floor_report` (per-file coverage floor verdict), `ci_local_gate_parity_lib.render_report` (CI/local parity verdict), `inventory_ubiquitous_language.build_inventory` (terminology verdict).
- Consumer: `run-quality.sh` and the commit-boundary gate plan, plus any agent or operator citing one of these greens as proof.
- Owning surface: the repo's empty-scope rule, owned by `tests/quality_gates/test_empty_scope_refusals.py` — a caller-NAMED scope resolving to nothing refuses; a DISCOVERED empty set stays a pass and must say so. All four rows were closed against that existing rule rather than a new per-gate invention.
- Verdict: owned-correctly

## Non-Claims

- **S31 is not closed.** The exemption is still granted by a comment inside the
  audited file. This batch made its consequence legible; it did not touch the
  self-declaration.
- The changed-line mutation gate reports UNPROVEN for this range (stale coverage),
  so no changed-line proof is claimed for these edits. The evidence is 4223 passing
  quality-gate tests including 17 new ones, plus reproduce-then-control runs for
  each row before repair.
- `--require-evaluated-scope` and the parity NOTE line are legibility, not teeth,
  in the broad lane; only the commit-boundary gate arms the new established-match
  flag, and only because it is a no-op on this repo today.
- Nine of the fourteen SUBAGENT-CONFIRMED high rows in the sweep remain untouched.

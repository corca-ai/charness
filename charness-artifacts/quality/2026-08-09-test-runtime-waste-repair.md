# Quality Review
Date: 2026-08-09
Title: Test Runtime Waste Repair

## Scope

Target boundary: local quality-run observability, test-owned subprocess and
temporary-directory lifecycle, post-July test growth value, and repeated stable
repo reads. Runner parallelism was measured but is not changed in this slice.
Generated SLOC stability is included after clean closeout reproduced a
self-measuring inventory loop.

Ambient repo findings: hosted CI publication, the approved release, and active
goal slices remain outside this local repair.

## Surface Contract Review

- semantic coverage: `partial` — local process cleanup, fixture-root isolation,
  focused runtime, and redirected progress are executed; hosted CI is unexamined.
- surface: quality runner transcript plus standing pytest fixtures and selectors
- owner: the runner owns progress; each test owns descendants and ambient scope.
- projections: root/plugin CLI checker copies and root/plugin quality runners
- state scope: dirty local slice and an identical patched disposable clone
- transitions: started, waiting, timed out, drained, explicitly cleaned, complete
- proof boundary: focused runtime/liveness assertions, structural inventory,
  standing tests, and full-run receipts
- unexamined axes: repaired-SHA hosted execution and unrelated test families

## Current Gates

- Redirected broad runs emit stderr `START`/`WAIT` before buffered phase output;
  the earlier zero-byte transcript failure is covered by the committed runner test.
- CLI probe tests retain real process-group escape and partial-output behavior,
  inject a test-only drain deadline, and stop/acknowledge every recorded detached holder.
- Synthetic economics fixtures resolve footprint scans to their own empty temp
  root unless a footprint test explicitly supplies a seeded root.
- Structural-waste inventory reports no duplicate discovery, broad scanner, or
  repeated stable-root read candidates.
- SLOC inventory excludes runtime state explicitly and removes only the exact
  resolved in-repo output report, so arbitrary output names cannot measure
  themselves or hide a legitimate same-suffix source file.
- Full read-only quality closes at 87 passed / 0 failed; changed-line coverage
  remains explicitly unproven only until the mutation-pool edit is committed.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`, plus focused pytest durations and an isolated patched-clone 16/12/8 worker cohort; receipts live under `/tmp/charness-runner-ab.LxTHBE`. <!-- reproduction-source -->
- runtime hot spots: prior detached-child cases cost 12.08s/12.06s and retry cost
  10.11s; repaired CLI module is 18 passed in 6.50s serial, with escape cases
  1.29s each. Ambient economics focus fell from 10.81s to 2.00s under xdist;
  standing samples are rendered by `render_runtime_summary.py`.
- coverage gate: focused changed tests pass; final branch changed-line proof is
  owned by slice closeout.
- evaluator depth: deterministic-gates-only; Cautilus is ask-before-run and adds
  no evidence for process liveness, file-scope identity, or runtime cost.

## Healthy

- Production timeout defaults and real failure semantics remain unchanged.
- Process state plus unique argv identity, exit acknowledgement, and resolved
  temp-root identity detect the two bugs directly; wall time is supporting
  evidence rather than the sole oracle.
- Five slow positive controls were removed only where stronger entrypoint
  siblings already kill the unconditional-failure mutant; the one unique
  export-safe whole-entrypoint control remains.
- Fingerprint multiplicity now names both algorithm versions explicitly instead
  of accidentally exercising default v2 twice and leaving v1 unproved.

## Weak

- Test production ratio is 1.21 (171,612/141,777), above the advisory 1.0 floor;
  current size alone does not prove further redundancy.
- A disposable clone fails `validate-maintainer-setup` because it intentionally
  lacks the source checkout's installed hook; every A/B arm carried the same
  86-pass/1-fail/1-unproven verdict set.

## Missing

- No mutation matrix was run for the July-to-current growth delta. The deletions
  are supported by exact stronger siblings and focused execution, not a global
  mutation-value claim.
- Hosted CI readback on the repaired SHA remains unavailable until push is
  explicitly approved.

## Deferred

- Runner scheduling/parallelism changes are deferred by operator direction and
  by measurement: worker 16 already won the exact cohort, so no repair premise
  remains for 12/8 or a new scheduler.
- Generic subprocess lifecycle frameworks and generic environment sanitizers
  are deferred; sibling search found only the bounded fixtures repaired here.
- A git-tracked-files SLOC contract is deferred: Tokei's pre-existing default
  omits hidden source generally, and issue #579 repairs self-contamination only.

## Advisory

- structural review result: command: `python3 skills/public/quality/scripts/inventory_structural_waste.py --repo-root . --detail`; repeated stable-root reads moved from four candidates to zero.
- prose review result: artifact: `charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md`; issues `#577`, `#578`, and `#579` plus its follow-up carry-forward bind the failures, ownership, and remote non-claim.
- growth review result: command: fresh AST-body/value audit; 514 test files / 7,391 functions / 167,672 LOC made the
  July audit stale, but a fresh AST-body/value review found only five proven
  deletions; distinct carrier/error-code boundaries remain.

## Delegated Review

- Delegated Review: executed — growth/value and contention reviewers identified
  bounded repairs; critique round 1 found unowned ordinary children and unsafe
  raw-PID cleanup; round 2 reproduced a late-registration cleanup race. All were
  repaired; the capped round-2 repair is accepted-unreviewed.
- Issue #579's first SLOC round rejected a basename-global exclusion; round 2
  rejected a suffix glob. Exact report-identity filtering plus six focused
  counterexamples is the capped round-2 repair, accepted-unreviewed.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  all three ran; lifecycle/scope repairs and proven duplicate controls were
  bundled, while scheduler changes were refuted by the isolated cohort.

## Commands Run

- Modified-test focus under xdist — 299 passed in 5.70s. <!-- reproduction-source -->
- CLI module serial durations — 18 passed in 6.35s; five repeated three-case
  race runs passed and post-run holder/`time.sleep(600)` scans returned none.
- Economics/discovery focus under xdist — 27 passed in 2.00s.
- Structural-waste inventory — zero findings; `git diff --check` passed.
- SLOC inventory — 6 focused tests pass in 1.35s; repeated canonical generation
  stays byte-identical across runtime telemetry mutation.
- Pre-critique patched-clone A/B, three measured runs per arm after warmup: worker 16 wall
  median 60.83s / pytest 54.9s; worker 12 69.98s / 64.2s; worker 8 89.25s / 83.5s.
- `bash scripts/run-quality.sh --read-only >log 2>&1` — the in-flight log was
  152 bytes with `START`/`WAIT`; final summary 87 passed, 0 failed, 1 expected
  dirty-tree UNPROVEN in 65.8s. The first attempt exposed corpus drift; three
  pinned-probe tests passed after the required synchronized refresh.

## Recommended Next Quality Moves

- active slice closeout — capability_needed=honest local proof; next_center=changed tests and generated projection; transformation=sync, full gate, mutation/changed-line consumer, and fresh-eye critique; proof_boundary=clean closeout ledger; enforcement_posture=existing-gate-reuse.
- passive further test deletion — capability_needed=mutation-kill evidence for another exact duplicate; next_center=post-July growth delta; transformation=remove only after a stronger sibling is identified; proof_boundary=mutant killed before and after; enforcement_posture=no-gate because suite size is not value evidence.

## History

- [Remote CI changed-line review](./2026-08-09-quality-review.md)
- [July pytest value audit](./history/2026-07-03-pytest-suite-test-value-audit.md)

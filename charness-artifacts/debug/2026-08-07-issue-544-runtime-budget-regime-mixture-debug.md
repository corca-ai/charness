# Issue #544 Runtime Budget Regime Mixture Debug
Date: 2026-08-07

## Problem

`#544` reports that runtime budgets in the `local-linux-x86_64-36cpu` profile
drift upward from machine contention rather than from code changes, that each
label therefore false-reds in turn, and that every repair is a ratchet because a
bar can only ever be raised. It names `check-secrets`, `check-markdown`,
`doc-duplicates`, `run-evals`.

## Correct Behavior

A runtime budget is a claim about one workload: the number a bar is compared
against must be a function of the code the label checks, not of how the gate was
invoked. A budget window must not pool structurally different work.

## Observed Facts

- **Standalone vs in-gate**, measured at `60b24a54`. `check-secrets.sh` alone
  **7,482 ms** vs in-gate 15,672–17,669 (bar 19,500); `check-markdown.sh` alone
  **4,899 ms** vs in-gate 13,996–15,469 (bar 17,000).
- **`check-markdown`'s twenty-sample window is bimodal, not drifting.** Thirteen
  samples at 13,996–15,469 ms and seven at 4,418–4,877 ms — 3.3x inside one
  window. Its standalone 4,899 ms sits with the fast population and nowhere near
  the slow one, so those are the same work under less competition, not a smaller
  scope.
- **The two populations are two run modes.** By timestamp bucket in the live store
  `.charness/quality/runtime-signals.json`: <!-- reproduction-source -->
  fast samples come from fourteen-label runs, slow from 70–85-label runs, and those
  fourteen are exactly `DOCS_ONLY_LABELS` in `.githooks/pre-push:60`.
- **All fourteen docs-only labels are mixtures**, not just the one the issue names
  — subset-vs-full medians span 2.10x to 4.78x. Three carry budgets: `check-markdown`
  (4,861 vs 14,908 ms), `check-spec-evidence-durability` (3,601 vs 8,204),
  `check-references-link-inventory` (142 vs 355). For the last the mixture pulls the
  median DOWN, so its bar is LOOSER than intended — the inverse failure, hiding a
  regression rather than manufacturing a false red.
- **A sample records nothing about its regime** — `record_quality_runtime.py`
  writes only `{timestamp, elapsed_ms, status}` — and enforcement compares the bar
  to that window's median (`runtime_budget_lib.py:158-165`).
- **The aggregate label already refuses to record under a filter** (`run-quality.sh`,
  `if [[ -z "$RUN_QUALITY_LABELS" ]]`); the per-gate path had no equivalent guard.
  That asymmetry is the defect.
- **The repo already fixed this class one level up.** `run-quality.sh` splits
  `pytest` from `pytest-release` — *"sized from the release mode's max"* — and
  splits the aggregate by mode. The per-gate labels never did.

## Reproduction

- At the recorder: record `check-markdown` at 15000 ms (full queue) and 4800 ms
  (docs-only subset). Before the fix both land in one window and the median is a
  function of their ratio; after, the second lands in `<profile>.docs-only`.
  Covered by `test_a_subset_run_never_enters_the_window_*`.
- End-to-end: the real fourteen-label subset filed its `check-markdown` sample
  (4,611 ms) into a new `local-linux-x86_64-36cpu.docs-only` profile and left the
  enforced window unchanged (n=20, median 14,376, min 4,418, max 15,469).

## Candidate Causes

- Machine contention drifting upward over time (the issue's stated cause).
- A self-reinforcing median rising with each retry (the issue's mechanism).
- Pooling of structurally different run regimes under one label.

## Hypothesis

- Falsifiable claim: one label's window mixes a ~85-gate full queue with a 14-gate
  docs-only subset differing up to 4.8x, so the enforcement median tracks the recent
  MIX not the code | disconfirmer: show the window is single-regime — that 4,418 ms
  and 14,039 ms differ by input size, not by subset.

## Verification

- Result: **confirmed**. The disconfirmer fails: the fourteen-label batch in the
  live archive `.charness/quality/history/runtime-signals-2026-08.jsonl` <!-- reproduction-source -->
  is exactly `DOCS_ONLY_LABELS`, and the standalone 4,899 ms sits with the fast band.
- Fix channel (tests): **ten mutants constructed, all ten killed** — collapsing
  `regime_scoped_profile` to the base, dropping its empty-slug guard, and using a
  separator-permitting slug regex; deleting `--runtime-regime`; deriving the regime
  from the environment instead of the structural fact; deleting the `export`;
  dropping each widening token; matching the first opt-in instead of composing
  both; and dropping the hook's `docs-only` naming. The `export` mutant initially
  SURVIVED because the test set the variable itself, so the child inherited it;
  rewritten to use the derived value, it now kills it. The counts in this section
  were themselves wrong once — round 2 caught a stale "four tests, three mutants"
  — so they are now stated from a re-run of the full set, not from memory.
- Verdict channel, distinct from the fix (CLI): `check_runtime_budget.py` exits 0
  after the live subset run with no profile configuration error — a regime profile
  carrying samples and no `budgets` block does not block the gate.

## Root Cause

The per-gate runtime sample records elapsed time, timestamp and status but nothing
about the run's concurrency regime, so one twenty-sample window pools a full-queue
run with a docs-only subset run whose measured cost differs by up to 4.8x. Both the
enforcement median and the sizing max are then read off a mixture whose composition
nobody controls, moving the number for reasons unrelated to the code.

## Invariant Proof

- Invariant: a sample from a run that is label-filtered, or that opts an extra
  gate into the main concurrent phase, must not enter the window the standard
  battery's bars are enforced against. Deliberately narrow: it does NOT say the
  profile key distinguishes gate sets — every ad hoc filter shares one `filtered`
  bucket that is itself a mixture, and variations INSIDE the standard battery (a
  conditionally queued gate, a mode dropping one) stay unregimed on purpose,
  because splitting the dominant sample population over a one-gate delta costs
  more evidence than it buys.
- Producer Proof: `run-quality.sh` derives the regime from the structural fact and
  passes it on; six runner tests, and six of the ten mutants below are its.
- Final-Consumer Proof: `check_runtime_budget.py` selects the unsuffixed profile
  on every automatic path and exits 0 against the live store after a regimed
  subset run. An operator naming a suffixed id explicitly still resolves it;
  without budgets that is a configuration error, not a no-op.
- Interface-Shape Sibling Scan: the aggregate label's filter guard is the same
  invariant one layer up; this slice makes the layers agree.
- Non-Claims: no claim that a regime bucket is itself budget-sized.

## Detection Gap

- Surface: the runtime budget gate | what did not fire: no assertion was written,
  though two cheap ones existed — the runner already ACTS on the filter fact for
  the aggregate label, and the store already records `min`/`max` per window, so a
  3.5x intra-window spread was readable with no new field | smallest change: record
  the partition, which this slice does. No refusal was added: there is no malformed
  input, only an unrecorded condition, and one would fire where nothing escapes.

## Sibling Search

- Mental model: a condition determining a measurement's meaning is known at record
  time then discarded, leaving a number nobody can attribute.
- Same-condition axis: `summarize_recent` medians over `fail`/`unestablished`
  samples and a failing gate exits early and reads fast | not fixed here | proof:
  status IS written per sample and dropped by the aggregator.
- Cross-file: `command_timing_log` ingest binds no profile, so bars labelled for one
  machine can be measured on another | not fixed here | proof: inert here, live in
  the exported skill.
- Unenforceable-bar axis: a budgeted label with no sample is a WARN and exits 0, so
  a bar can be permanently unenforceable | FILED as `#546` | proof: `missing_samples`
  is never consulted by `check_runtime_budget.main`.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: none
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

The partition is structural rather than advisory: a non-standard gate set cannot
record into the enforced window THROUGH THE RUNNER, because the regime is derived
from the structural fact, not a caller's opinion — an ambient
`CHARNESS_RUNTIME_REGIME` on a standard run is ignored, with a test pinning that
arm. The qualifier is load-bearing: a direct `record_quality_runtime.py` call
still writes wherever it is told. What this prevents is measured — it already
moved three budgeted labels' medians, in both directions.

**No bar is changed by this slice, and that is a decision.** The goal artifact
supplied a paste-ready re-derivation block; it is deliberately not pasted.
Re-deriving today would size every bar from a still-mixed window and raise every
one — the ratchet the issue complains about — to justify drift that does not exist
(`check-secrets` already returned to 15,679 ms from 17,669). The enforced windows
still hold pre-fix subset samples, seven of twenty for `check-markdown`; they age
out after twenty full-queue runs, and until then `--suggest-budgets` for the three
budgeted docs-only labels must not be committed. Nothing purges them: rewriting a
recorded measurement to make a window look clean would fabricate evidence.

Refuted from the issue, in full in the closeout carrier and the close comment:
the window is a fixed-size FIFO so retries do not ratchet the median; uncontended
samples already exist; bars demonstrably fall; and `check-secrets: 19500` was
judgment, not the 1.4x convention.

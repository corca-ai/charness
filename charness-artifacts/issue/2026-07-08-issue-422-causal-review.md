# Causal Review — corca-ai/charness#422 (2026-07-08)

Bounded fresh-eye causal reviewer (parent-delegated, high-leverage tier), run
before fix design per the issue skill bug-class contract.

- JTBD: When the scheduled mutation gate goes red because the sampler's
  coverage-baseline pytest fails, the posted regression comment must name the
  failing baseline nodeids as the blocking signal, so the operator does not
  chase the collateral StrykerJS-missing symptom.

- Classification confirmation: Agree — bug. The summary/comment pipeline
  produces an actively wrong diagnostic (misattribution), not a missing
  feature. Real-world divergence proven by four misattributed red runs
  (2026-07-06 → 2026-07-08) and ~3 days of wasted diagnosis.

- Root cause: substrate
  `charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md`
  ("Root Cause" + "Why the runs after the first one misled") — the sampler
  aborts via `raise SystemExit(...)` at `scripts/sample_mutation_files.py:200-203`
  when the baseline pytest fails (`run_test_coverage`,
  `scripts/mutation_sampling_lib.py:180-192`, `subprocess.run(check=True)` —
  output streams to the step log only, nothing captured). No manifest is
  written; `.github/workflows/mutation-tests.yml:195-200` still runs the
  summary step (`always()`), `scripts/check_mutation_score.py:249-257` exits 2
  on the missing cosmic-ray report WITHOUT writing `summary.md`, and the JS
  slice then owns the whole posted comment. Over-reach check passed: the
  misreport is observed in four posted comment bodies, not inferred.

- Debug artifact:
  charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md

- Invariant proof (workflow-boundary propagation): producer = `Select mutation
  sample` step (sampler stderr + exit 1). Signal = the failing baseline
  nodeids. Transport/mirror = manifest json/md + `summary.md` files. Final
  consumer = the issue-comment script (`mutation-tests.yml:216-260`), which
  reads ONLY `summary.md`/`sample.md` and falls back to generic text when
  absent — the failing-nodeid signal has NO transport surface today; it dies
  in the step log. Final-consumer proof from the four posted comment bodies.
  Non-claim: workflow_dispatch/PR paths not exercised in the substrate.

- Detection gap: no gate asserts "sampler abort ⇒ summary names the abort
  cause." Smallest change to fire: a unit test on the summary path covering
  the no-manifest case asserting the baseline-failure marker text appears.
  Over-reach check passed: the misreport actively posted a wrong cause 4
  times; a correctness assertion on the posted body is the smallest honest
  gate.

- Sibling search (single producer→comment pipeline; no keyword-only matches):
  1. `scripts/check_mutation_score.py:249-257` missing-report silent-absence —
     same bug, fix now — static scan only.
  2. `scripts/check_js_mutation_score.py:101-112` collapses "JS runner never
     ran" into "report missing" — same class, the exact posted symptom — same
     bug, fix now — local payload proof (posted comments).
  3. `run_js_mutation.py` timeout/no-coverage paths already write explicit
     blocking-signal lines (`check_js_mutation_score.py:89-93`) — intentional
     contrast, no action.
  4. Workflow comment fallback `'No mutation sample manifest was generated.'`
     (`mutation-tests.yml:240-241`) — same bug, fix now (where a sampler-abort
     marker would surface) — static scan only.

- Bundle vs Defer:
  1. CHEAP-NOW: sampler writes a minimal abort marker (failing nodeids + abort
     reason) on baseline-pytest failure before exiting 1.
  2. CHEAP-NOW: summary step distinguishes "no manifest ⇒ report sampler abort
     (read marker if present)" from "JS report missing".
  3. DEFER: unifying the JS-slice message taxonomy beyond what the marker fix
     requires.
  4. DEFER: workflow_dispatch/PR-path proof of the same misreport class.

- Fresh-Eye Satisfaction: parent-delegated. Reviewer tier: high-leverage
  requested; host default reviewer model spawn (no per-spawn tier fields
  exposed to confirm application).

# CI-Recoverable Gate Triage

The local-proof guardrail (`maintainer-local-enforcement.md`,
`inventory_ci_local_gate_parity.py`) biases hard toward proof that is reachable
locally: it flags CI steps a clone's pre-push gate does not run, so a required
failure can always appear locally first. That bias is correct, but on its own it
answers only one half of a gate-speed question. When a maintainer's goal is
"reduce the local pre-push wall-clock," the guardrail tends to keep every gate
local even when CI already re-runs the same proof — so the safe, CI-backstopped
speed wins (move a slow real-boundary gate or a network-flaky check to CI-only;
replace an overlapping local build with a cheaper superset and keep the
per-target build as the CI backstop) come from the operator working *against* the
skill's default, not from the skill.

`inventory_ci_recoverable_gates.py` is the explicit counterweight. It is advisory
only (always exit-zero, no blocking floor) and it never edits a gate.

## What it does

1. Builds the **cost-ranked gate universe** from the runtime report
   (`runtime_budget_lib.evaluate`): every budgeted gate plus every sampled hot
   spot, with wall-clock from the recent-median elapsed. Wall-clock comes from
   `.charness/quality/runtime-signals.json` or, when declared, a repo's existing
   `command_timing_log` (see `adapter-contract.md`). With no cost signal at all,
   there are no ranked gates to triage and the report says so.
2. Builds a **CI proof index** from the workflow `run:` steps (reusing
   `ci_local_gate_parity_lib` for workflow discovery and gate-policy reading).
3. For each ranked gate, matches its distinctive label token (word-boundary; a
   `ruff-check` label matches a CI `ruff check` step, a `check-doc-links` label
   matches `scripts/check_doc_links.py`; over-generic single words such as `node`
   are skipped) against the CI proof index.
4. Classifies each gate:
   - **candidate** — a CI step re-runs its proof. Reported with the matching CI
     step(s) and any gate-policy marker, ranked by wall-clock descending. This is
     a candidate to move *off the local hot path*, with CI as the backstop.
   - **keep-local** — no CI step re-runs its proof. Never recommended for moving.

## The safety gate

The lens **only** proposes moving a gate whose proof CI fully re-runs. A gate CI
does not re-run is `keep-local`, full stop — moving it would lose required proof,
which is exactly the failure the local-proof guardrail exists to prevent. The
counterweight narrows the guardrail's blind spot; it does not weaken it.

## Honest limits (advisory-interpretation contract)

Matching is token-identity, so it cannot prove two invocations exercise the same
proof — different flags, scope, or inputs can diverge — it cannot see a CI step
gated behind an `if:`/path filter that would skip the gate for the change in
hand, and it matches a token that merely appears in non-executing text (an
`echo`, a config read like `cat pytest.ini`, or a comment) rather than a step
that runs the proof. A match is a **candidate to confirm**, not a proven
equivalence. Before
moving a gate off the local hot path, answer the interpretation question the
report prints: *does the matched CI step actually re-run THIS gate's full proof
for the changes that reach main, so moving it loses no required signal?*

## Use

```bash
python3 "$SKILL_DIR/scripts/inventory_ci_recoverable_gates.py" --repo-root . --json
python3 "$SKILL_DIR/scripts/inventory_ci_recoverable_gates.py" --repo-root .
```

Output keys: `candidates` (ranked, with `ci_steps` + `ci_gate_policies`),
`keep_local`, `gates_considered`, `commands_source`, and the `interpretation`
block. The lens is read-only and exit-zero; it informs the
`CI/Local Gate Parity` / `Runtime Signals` sections of the quality artifact, it
does not gate the run.

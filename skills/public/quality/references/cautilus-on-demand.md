# Cautilus On-Demand

This repo treats Cautilus as eval-only per corca-ai/cautilus#32: `cautilus evaluate fixture`, `cautilus evaluate observation`, and `cautilus evaluate skill-experiment` are the only supported live surfaces (cautilus 0.15.4 renamed the legacy `eval test/evaluate` topic; `skill-experiment` is the subagent-spawning skill-clone evaluator). The adapter is in `run_mode: ask`, which means a live cautilus run is never the default closeout path — deterministic gates own closeout when no log-backed behavior proof is requested.

The repeated trap is calling `cautilus evaluate fixture` against the legacy route-only fixture (`evals/cautilus/whole-repo-routing.fixture.json`) on the strength of an ambiguous user phrase plus the cautilus binary being on PATH. The fixture is a deterministic sentinel; running it as live proof produces a false closeout signal. To prevent that, every `cautilus evaluate ...` invocation must go through the planner first.

## Planner Consult Contract

Before invoking `cautilus evaluate fixture`, `cautilus evaluate observation`, or `cautilus evaluate skill-experiment`, consult the proof planner:

```bash
python3 scripts/plan_cautilus_proof.py --repo-root . --json
```

Interpret the output as follows:

- `next_action: "none"` → do not invoke cautilus. Deterministic gates own this closeout. Refuse and continue with the regular validators.
- `must_ask_before_running: true` and `run_mode: "ask"` → cautilus may only run when an explicit log-backed behavior proof request exists. The request must name a specific failing-prompt, transcript, operator-log, issue-log, or regression-log file. Without that file path, refuse.
- `status: "ready-for-validation"` and an explicit log-backed request → cautilus may run. Pair the run with the named behavior-source artifact and record both in `charness-artifacts/cautilus/latest.md`.

Routine review wording — "run quality", "validate this", "verify the prompt change" — is not a live cautilus request. Generic closeout, prompt-affecting diffs, or skill-surface edits do not by themselves require cautilus; they are owned by deterministic validators.

## Repo-Owned Wrapper

The repo-local entrypoint for cautilus invocations is `scripts/run_cautilus_eval.py`. The wrapper enforces the planner consult contract and refuses with exit code 2 when the gate is unsatisfied. Call it instead of bare `cautilus evaluate fixture/observation/skill-experiment`:

```bash
python3 scripts/run_cautilus_eval.py --mode fixture --justification-log <path-to-failing-log> -- <extra cautilus args>
```

Valid `--mode` values: `fixture` (forwards to `cautilus evaluate fixture`), `observation` (forwards to `cautilus evaluate observation`), and `skill-experiment` (forwards to `cautilus evaluate skill-experiment`, the subagent-spawning skill-clone evaluator).

The wrapper refuses when:

- the planner returns `next_action: "none"` and no `--justification-log` is provided,
- the planner returns `must_ask_before_running: true` and no `--justification-log` is provided,
- the `--justification-log` path does not exist, is empty, is smaller than 32 bytes, has no `- source-kind: <kind>` line, or declares a `source-kind` outside `failing-prompt`, `transcript`, `operator-log`, `issue-log`, `regression-log`.

The line-shape requirement aligns the wrapper with the `## Behavior Source` invariant in `charness-artifacts/cautilus/latest.md`: a trivial throwaway file does not satisfy the contract, and a file that merely contains the marker word as a substring does not either; the log must declare what kind of behavior proof it is via a structured line such as `- source-kind: failing-prompt`.

## What This Page Owns

This is the contract anchor for cautilus invocations during ordinary task work. Behavior-proof artifact shape is owned by `scripts/validate_cautilus_proof.py` and the `## Behavior Source` / `## Commands Run` / `## Regression Proof` sections in `charness-artifacts/cautilus/latest.md`. Broader Cautilus surfaces (claim discovery, optimize, review-learning, `evaluate live`, Agent orchestration) remain disabled by repo policy and are not unlocked by this contract.

# Cautilus skill-experiment usage-validation harness

Prove a charness skill change with a **real** `claude -p` run scored by cautilus,
not a routing sentinel. Cautilus `evaluate skill-experiment` is a **deterministic
scorer** (cautilus `internal/runtime/skill_clone_experiment.go`): it does not read
the transcript — it reads each arm's host-captured `output.sourceRefs` /
`output.text` / `status` from a `cautilus.skill_clone_experiment_input.v1` JSON and
computes a source-coverage delta against the declared obligations.

## Data flow (three roles, do not conflate)

1. **Capture** — run the eval runner's `claude_code` backend at two skill refs
   (baseline vs variant). Each pass persists a natural stream-json
   `transcript.jsonl` (`scripts/agent-runtime/run-local-eval-test.mjs`, which
   captures `--output-format stream-json`). The transcript's tool calls are the
   evidence of which source files the agent actually read.
2. **Extract** — `scripts/agent-runtime/extract-skill-experiment-input.mjs` parses
   the two transcripts + this directory's `spec.json` into the
   `skill_clone_experiment_input.v1` JSON cautilus scores. `output.sourceRefs`
   comes from the agent's `Read`/`Edit`/`Write` tool calls, relativized against
   the transcript's own init `cwd`.

   ```bash
   node scripts/agent-runtime/extract-skill-experiment-input.mjs \
     --spec evals/cautilus/skill-experiment/spec.json \
     --baseline-transcript <baseline>/transcript.jsonl \
     --variant-transcript  <variant>/transcript.jsonl \
     --baseline-workspace-root <baseline-worktree> \
     --variant-workspace-root  <variant-worktree> \
     --output <runs>/input.v1.json
   ```

3. **Score** — the repo-owned wrapper enforces the eval-only contract. The
   transcript justification-log and the extracted input are **two files with two
   roles**: the markdown log satisfies the wrapper's `source-kind: transcript`
   gate; the JSON is what cautilus actually reads.

   ```bash
   python3 scripts/run_cautilus_eval.py --mode skill-experiment \
     --justification-log <runs>/justification.md \
     -- --input <runs>/input.v1.json --output <runs>/report.json
   ```

   The raw `transcript.jsonl` alone does **not** satisfy the gate — it has no
   `- source-kind:` line. Author a small markdown log (see
   `justification-log.template.md`).

## Eval-only / ask-before-run

`cautilus evaluate skill-experiment` is gated. Consult
`python3 scripts/plan_cautilus_proof.py --repo-root . --json` (read-only) first and
record its verbatim output. The planner is hardcoded to `next_action: none` /
`must_ask_before_running: true`; the wrapper proceeds **only** when a real
`--justification-log` is supplied, printing a note. Authorization is the operator's
explicit one-run approval plus that transcript log — never a planner green. A
second run re-enters the operator decision queue. Full contract:
[`skills/public/quality/references/cautilus-on-demand.md`](../../../skills/public/quality/references/cautilus-on-demand.md).

## Verdict

The report's `promotion_recommendation` is `promote` / `revise` / `discard`. A
clean `promote` requires `isolation.productionSkillTouched: false` declared
explicitly in `spec.json` (the scorer treats an undeclared isolation as unsafe and
downgrades to `revise`). One single-scenario run proves the chain emits a real
verdict but is **not** a power-bearing A/B — the variance lives in the stochastic
upstream capture, while the scorer itself is deterministic.

---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete quality moves instead of only complaining about what is missing."
---
# Quality

Use this for a quality question that spans more than one narrow bug or test.
Quality improves the system that produces correctness: concepts, behavior proof,
security and supply chain, skill drift, runtime risk, and operator sustainability.

Gates are evidence, not the judgment. Length, duplicate, and pressure heuristics are smell sensors; the first quality move is usually to delete, merge, split ownership, extract a helper, or narrow an interface. A gate earns its cost from
the claim and its affected consumers.

## Consumer-repo health

When this skill is used in a consuming repository, the primary quality question
is whether the repository can reach correct changes with less friction. Treat
its existing gates, hooks, validators, wrappers, mirrors, and generated reports
as suspects, not as requirements. For each one, map the claim, inputs, owner,
runtime cost, and failure value. Then recommend one of:

- keep one canonical owner;
- delete or merge a duplicate;
- narrow an over-broad local check;
- move an expensive confidence check to CI or an explicit release phase; or
- leave an explicit non-claim when the capability is unavailable or out of scope.

Do this reduction pass before proposing a new rule. A healthy recommendation
names what disappears and why, what remains sufficient, and what risk the
non-claim leaves. A green result from a duplicate gate is not evidence that the
duplicate belongs in the repository.

## What this skill does not run

These authoring-repo-only checks are not consumer-repo health gates:

- packaging and export;
- skill contracts;
- presets, profiles, and integrations; and
- this repo's pointer freshness.

They live in the authoring repository's `tools/`.

## Fast path

Quality is not a request to run every available check. For a narrow question or
ordinary implementation, inspect the affected owner, run the smallest focused
check that answers the question, and stop. Do not invoke the planner, broad
suite, mutation, artifact scaffold, dogfood, or fresh-eye review merely because
`quality` was selected. Expand only when the claim crosses a release,
proof-surface, external, security, or genuinely repo-wide boundary, and state
the additional claim each expanded check buys.

## Bootstrap

For a repo-wide question or an adapter/gate change, resolve `$SKILL_DIR` per
`../../shared/references/bootstrap-resolution.md` and run the planner before
broad gates or fixes. A narrow quality question does not need this block.
Missing binary handling follows `../../shared/references/binary-preflight.md`
when a selected command actually needs the binary.

```bash
# Required Tools: rg
# First consumer declaration: set `universes:` for this repository's file families.
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/bootstrap_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/plan_quality_run.py" --repo-root .
# For a target-skill review, add: --target-skill <skill-id>
rg --files <affected-root>
git status --short
```

Do not migrate an adapter, create a quality artifact, or install a hook merely
to answer a focused question. `bootstrap_adapter.py --migrate` and artifact
commands are explicit boundaries, not defaults.

### Setup boundary

When `setup` is proposing an operating surface, consume its quality snapshot
and bootstrap plan rather than inventing parallel gates. `configured` means the
quality adapter is present and valid; it does not mean the repo is green, and
`plan-only` or `unconfigured` remains an explicit non-verdict. `quality` owns
the adapter, exact gate commands, ratchets, and final quality verdict; setup may
describe the approved plan and its fast staged/related-file hook scope but must
not install tools, register hooks, or migrate gates without approval.

## Workflow

1. Restate the quality question and its scope.
2. For a narrow question, identify the owning command or module and run one
   focused check. Reuse the default core lane only when the changed surface has
   cross-module consumers. This is the normal completion path.
3. For repo-wide questions or adapter/gate changes, run `plan_quality_run.py`;
   pass `--target-skill <skill-id>` only when a target skill is actually in
   scope. Treat `declared-only`, `unreachable`, `missing`, and `not-run` as
   non-verdicts; planner routing proves reachability, not success.
4. Run applicable `gate_packets` as report-first evidence after reading only the
   planner reads needed by the selected claim. Use `trust_model`, `cost_tier`,
   `parallel_group`, and `run_when` to choose the cheapest sufficient set and
   parallelize independent work; they are selection hints, not an obligation to
   execute every packet. Before a broad gate, state the claim, affected consumer
   closure, and minimum sufficient proof. A failure does not widen the scope or
   justify an unrelated rerun. Inspect a changed validator and one cheap
   negative control only when the validator itself is the claim.
5. If a planner emits `structural_review_packet`, answer it only for the
   affected target. Separate target-skill findings, ambient failures,
   opportunistic repairs, and non-claims; name the capability before proposing a
   gate or helper. Open `on_demand_reads` only when a concrete finding matches
   its trigger.
6. Classify findings by enforcement tier and recommend deletion, merge,
   ownership split, helper extraction, interface narrowing, advisory,
   existing-gate reuse, or deferral before proposing a new floor. Lesson memory,
   when present, is optional ledger/selection data and does not create another
   evaluator or artifact workflow.
7. Decide whether the review needs durable findings. For a repo-wide review that
   does, scaffold and validate one quality artifact with
   `scaffold_quality_artifact.py` and `validate_quality_artifact.py`. A focused
   question may report in chat and reuse an existing artifact; it does not create
   a progress mirror.
8. If writing a quality artifact, `resolve_quality_artifact.py --repo-root .
   --intent record` names a dated record and `--intent current` names an explicit
   rolling summary. Do NOT trust the scaffold payload's `write_artifact_path`
   without reading its `write_artifact_effect` and `write_artifact_subject_match`:
   only `match` permits the
   write. `unknown` and `routed` require using the named
   `refused_write_artifact_path`; never silently replace an unrelated record.
   never silently replace it when the target is not the current review.
   The resolver owns `refresh_current_pointer_command` and
   `update_current_pointer_after_write`. Validate once with
   `validate_quality_artifact.py`, fixing all reported violations together. Fill
   the `## Surface Contract Review` packet only when that surface is in scope.
9. Use bounded fresh-eye review only for an explicit operator request or a
   release, proof-surface, external, security, deletion, or other irreversible
   boundary. When selected, apply host-exposed `reviewer_tiers.high-leverage`
   fields through the shared policy. Ordinary implementation, docs, tests,
   cleanup, and narrow quality questions do not require it or a boundary
   fingerprint. Use
   `../../shared/references/fresh-eye-subagent-review.md` when that exceptional
   trigger fires.

## Invariants

- Passing gates are evidence, not success by themselves.
- Less is more in verification: a check is justified by the claim and required
  consumer closure, not by the fact that the repository already has the check.
  Record omitted checks as bounded non-claims, and do not pay for unrelated
  reruns merely because one verifier failed.
- Invoking `quality` does not imply a planner, full suite, mutation run, durable
  artifact, or reviewer. One focused proof is enough when the claim is narrow;
  mutation and other expensive confidence checks belong to an explicit release
  or proof-surface phase.
- A declaration is not execution: an adapter-derived command remains `not-run`
  until its selected receipt records otherwise. Do not turn declaration metadata
  into a green result.
- When the next quality move is repo-local, deterministic, and low-risk,
  implement it in the same turn unless review-only was requested.
- Do not move local proof to CI unless another channel fully reruns the same
  proof. If a required check is omitted, name the concrete non-claim.
- Open `references/prompt-asset-policy.md` when prompt-sensitive output matters or `prompt_asset_policy.source_globs` is configured.
- Final summaries must retain Weak, Missing, Advisory, delegated-review status,
  and active Recommended Next Quality Moves when those findings exist; a green
  gate does not erase them. The final user-facing answer must not silently omit `Weak`, `Missing`, `Advisory`, delegated-review status, or active `Recommended Next Quality Moves` findings.

## References

- `references/index.md`

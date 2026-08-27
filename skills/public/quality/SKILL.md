---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete quality moves instead of only complaining about what is missing."
---
# Quality

Use this when the task is overall quality posture, not one narrow bug or isolated
test. Quality improves the system that produces correctness: concepts,
behavior proof, security and supply chain, skill drift, runtime risk, and
operator sustainability.

Gates are evidence packets, not the judgment. Prefer deterministic enforcement
when code can own the concern, but read the evidence through the quality lenses
before fixing. Length, duplicate, and pressure heuristics are smell sensors; the
win is delete, merge, split ownership, extract a helper, or narrow an interface.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then
run the planner before broad gates or fixes. Missing binary handling follows
`../../shared/references/binary-preflight.md`.

```bash
# Required Tools: rg
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/bootstrap_adapter.py" --repo-root .
# A conflict is preserved by default; authorize a named rewrite only when intended:
python3 "$SKILL_DIR/scripts/bootstrap_adapter.py" --repo-root . --migrate
python3 "$SKILL_DIR/scripts/resolve_quality_artifact.py" --repo-root . --intent record
python3 "$SKILL_DIR/scripts/plan_quality_run.py" --repo-root .
# For a target-skill review, add: --target-skill <skill-id>
rg --files .
git status --short
```

Bootstrap is lifecycle-aware: normalized-equivalent adapters are silent
no-ops, conflicts preserve the existing adapter and emit exact requested
surfaces plus a next action, and `--migrate` is the explicit rewrite boundary
that retains existing comments.

### Setup boundary

When `setup` is proposing an operating surface, consume its quality snapshot
and bootstrap plan rather than inventing parallel gates. `configured` means the
quality adapter is present and valid; it does not mean the repo is green, and
`plan-only` or `unconfigured` remains an explicit non-verdict. `quality` owns
the adapter, exact gate commands, ratchets, and final quality verdict; setup may
describe the approved plan and its fast staged/related-file hook scope but must
not install tools, register hooks, or migrate gates without approval.

## Workflow

1. Restate the quality question and scope.
2. Run `plan_quality_run.py`; when the quality question names a target skill,
   pass `--target-skill <skill-id>` so the planner anchors the structural packet.
   Read `declaration_lifecycle` before treating any configured preset, command,
   product surface, canonical document, or skill path as covered. `declared-only`,
   `unreachable`, `missing`, and `not-run` are explicit non-verdicts. Execute the
   adapter-derived `gate_packets`; planner routing proves reachability, not success.
3. Read every planner `required_reads` entry before broad gates. The planner
   `brief` carries the load-bearing classification, automation-promotion, and
   maintainer-local-enforcement discipline plus the inventory-dispatch routing
   index (concern area -> focused inventories + detail_refs) inline; apply it
   directly and open a brief `detail_ref` only when its trigger fires, rather
   than reading those docs up front.
4. Run applicable `gate_packets` as report-first evidence. Use each packet's
   `trust_model`, `cost_tier`, `parallel_group`, and `run_when` to decide what
   can be trusted directly, what can run in parallel, and what needs judgment
   because false positives or false negatives are expected. Before a broad
   gate, state the claim, affected consumer closure, and minimum sufficient
   proof. A failing gate does not by itself widen the scope. When the gate or
   validator changed, or its result suggests over-checking or a false green,
   inspect its own contract and a cheap negative control separately before
   rerunning unrelated subject checks. Use content-addressed subject,
   verifier, and input identities with the critique retry helper and its
   canonical `scope-too-broad` / `verifier-defect` / `subject-defect` terms;
   a new receipt label alone never permits a retry.
5. When the planner emits `structural_review_packet`, answer it before broad
   recommendations. Separate target-skill findings, ambient repo gate failures,
   opportunistic repairs, and non-claims; record a `structural review result:`
   line when consuming skill-ergonomics inventory.
   For skill-design findings, name the capability or capability failure before
   proposing a gate, helper, or wording change.
6. Open `on_demand_reads` only when a concrete gate, inventory, source, or
   operator finding matches its trigger.
7. Classify findings by enforcement tier and posture, then recommend the next
   concrete quality move: cleanup, deletion, merge, ownership split, helper
   extraction, interface narrowing, advisory, existing-gate reuse, or a
   candidate floor that has passed the north-star and floor-addition-restraint
   checks.
   When the repo declares a lesson evaluator, "could this prose be a validator
   instead" is the same question on its recorded lessons, and it belongs here
   rather than in `retro`: a retro sees one session, and promoting a lesson is a
   multi-session claim about the always-loaded contract surface. Read the
   evaluator's lifecycle evidence and judge each lesson as graduate, rewrite in
   place, or strengthen its binding to a step. Judge on ANCHORS — the recorded
   moment where a lesson changed or failed to change an action — never on
   recurrence count, which selects the loudest lesson rather than the one whose
   prose is the problem. A lesson with no anchored evidence is undetermined, not
   a candidate. Graduation stays a proposal behind review; archive and
   resurrection stay explicit reviewed events, and no score value triggers
   either automatically.
8. Scaffold the quality artifact FIRST with
   `scaffold_quality_artifact.py --repo-root .` (it emits the artifact contract as
   a JSON payload whose `template` already passes the validator) and fill real
   findings into that `template` instead of hand-writing the section format. Use
   the payload as the artifact contract: write to fit its `size_budget.max_words` on the first pass
   and heed `size_budget.guidance` on the judgment-heavy sections, rather than
   writing long and then trimming to fit against a ceiling the validator only
   reveals at the end. The scaffold resolves the WRITE TARGET by subject: it
   follows the current pointer only while that pointer's record is THIS review —
   same slug, same date — and otherwise routes to this review's own dated record,
   naming what it declined as `refused_write_artifact_path` and emitting a
   `refresh_current_pointer_command` to run when
   `update_current_pointer_after_write` is true. Do NOT read the scaffold payload's
   `write_artifact_path` as safe on its own: read `write_artifact_subject_match`
   first, because only `match` says the record at that path is THIS review's.
   `unknown` means the target carries no dated name to check — a `latest.md` that is
   a real file, or a first run with no pointer yet — and `routed` means the payload
   declined the pointer's record and picked this one, naming what it declined as
   `refused_write_artifact_path`. With `match` and `write_artifact_effect:
   overwrite_existing_content` together, today's review already exists — append to
   it, or pass a distinct `--subject`, and never silently replace it.
   `resolve_quality_artifact.py --repo-root . --intent record` still names a record
   path directly, and `--intent current` is for an explicitly rolling-summary edit. Validate once with
   `validate_quality_artifact.py` — it
   reports every remaining violation in one pass, so fix them together rather than
   iterating one error at a time.
   Fill the `## Surface Contract Review` packet for the affected surface, or keep
   its explicit `not-in-scope` disposition; routed gate output alone is not
   semantic coverage. The packet must name the surface, canonical owner,
   projections, state scope, transitions, proof boundary, and unexamined axes.
9. Run bounded fresh-eye review after initial inventory and before broad
   recommendations when the quality contract calls for it; use the
   high-leverage tier in `../../shared/references/fresh-eye-subagent-review.md`
   and host field `reviewer_tiers.high-leverage` when available. For an
   untyped reviewer that shares the parent tree, run the rail-1
   snapshot/verify commands from that reference's Enforcement section. Typed
   read-only and isolated reviewers do not need this extra fingerprint.

## Invariants

- Passing gates are evidence, not success by themselves.
- Less is more in verification: a check is justified by the claim and required
  consumer closure, not by the fact that the repository already has the check.
  Record omitted checks as bounded non-claims, and do not pay for unrelated
  reruns merely because one verifier failed.
- A declaration is not execution: every adapter-derived command remains `not-run`
  until a later receipt records otherwise, and preset lineage remains metadata
  unless a concrete gate route reconciles it.
- When the next quality move is repo-local, deterministic, and low-risk,
  implement it the same turn unless review-only was requested.
- If you stop short of an obvious repo-owned deterministic gate, name the
  unresolved enforcement gap.
- Do not stop at producer-side validators alone when the risk is public-skill
  routing or durable artifact behavior. Use
  `suggest_public_skill_dogfood.py --repo-root . --skill-id <skill-id>` to select
  one realistic case, then execute its consumer path or record the concrete
  unavailable channel; a scaffolded row alone is not consumer proof.
- Before invoking any `cautilus evaluate ...` subcommand, consult the planner-consult contract in `references/cautilus-on-demand.md` and route the call through the repo-owned wrapper instead of bare `cautilus evaluate`.
- Do not move local proof to CI unless another channel fully reruns the same
  proof.
- Final summaries and artifacts must not hide `Weak`, `Missing`, `Advisory`,
  `Delegated Review`, or active `Recommended Next Quality Moves` because a final
  gate passed.
- The final user-facing answer must not silently omit `Weak`, `Missing`, `Advisory`, delegated-review status, or active `Recommended Next Quality Moves` findings.
- Open `references/prompt-asset-policy.md` when prompt-sensitive output matters or `prompt_asset_policy.source_globs` is configured.

## References

- `references/index.md`

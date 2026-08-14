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
   because false positives or false negatives are expected.
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
   the payload as the artifact contract: write to fit its `size_budget.max_lines` on the first pass
   and heed `size_budget.guidance` on the judgment-heavy sections, rather than
   writing long and then trimming to fit against a ceiling the validator only
   reveals at the end. Take the WRITE TARGET from a different script: the
   scaffold's own `write_artifact_path` is the CURRENT POINTER, not the record to
   write. Run `resolve_quality_artifact.py --repo-root . --intent record` for a
   fresh review, write the path it returns as `write_artifact_path`, then run its
   emitted `refresh_current_pointer_command` when
   `update_current_pointer_after_write=true`; keep `--intent current` only for
   an explicitly rolling-summary edit. Do NOT write to the scaffold payload's
   `write_artifact_path`: it is `latest.md`, or that symlink's target — the
   PREVIOUS review's dated file. Writing there either overwrites that review, or
   (when the pointer dangles) files today's review under the previous review's
   DATE; both are wrong, so the prohibition holds regardless of what
   `write_artifact_effect` says on the scaffold payload. `create_new_file` there is
   not a green light. Use `write_artifact_effect` on the
   `--intent record` payload instead: `overwrite_existing_content` there means
   today's review already exists, so append to it or pass an explicit distinct
   `--slug`, never silently replace it. Validate once with
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
   and host field `reviewer_tiers.high-leverage` when available. For
   shared-tree reviewers, run the rail-1 snapshot/verify commands from that
   reference's Enforcement section: snapshot before spawning, verify after
   each reviewer returns.

## Invariants

- Passing gates are evidence, not success by themselves.
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

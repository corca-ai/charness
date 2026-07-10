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
python3 "$SKILL_DIR/scripts/resolve_quality_artifact.py" --repo-root . --intent current
python3 "$SKILL_DIR/scripts/plan_quality_run.py" --repo-root . --json
# For a target-skill review, add: --target-skill <skill-id>
rg --files .
git status --short
```

## Workflow

1. Restate the quality question and scope.
2. Run `plan_quality_run.py`; when the quality question names a target skill,
   pass `--target-skill <skill-id>` so the planner anchors the structural packet.
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
8. Scaffold the quality artifact FIRST with
   `scaffold_quality_artifact.py --repo-root .` (it emits the artifact contract as
   a JSON payload whose `template` already passes the validator) and fill real
   findings into that `template` instead of hand-writing the section format. Use
   the payload as the artifact contract: write to fit its `size_budget.max_lines` on the first pass
   and heed `size_budget.guidance` on the judgment-heavy sections, rather than
   writing long and then trimming to fit against a ceiling the validator only
   reveals at the end. Validate once with `validate_quality_artifact.py` — it
   reports every remaining violation in one pass, so fix them together rather than
   iterating one error at a time.
9. Run bounded fresh-eye review after initial inventory and before broad
   recommendations when the quality contract calls for it; use the
   high-leverage tier in `../../shared/references/fresh-eye-subagent-review.md`
   and host field `reviewer_tiers.high-leverage` when available. For
   shared-tree reviewers, run the rail-1 snapshot/verify commands from that
   reference's Enforcement section: snapshot before spawning, verify after
   each reviewer returns.

## Invariants

- Passing gates are evidence, not success by themselves.
- When the next quality move is repo-local, deterministic, and low-risk,
  implement it the same turn unless review-only was requested.
- If you stop short of an obvious repo-owned deterministic gate, name the
  unresolved enforcement gap.
- Do not stop at producer-side validators alone when the risk is public-skill routing or durable artifact behavior; scaffold one consumer-side dogfood case with `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>`.
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

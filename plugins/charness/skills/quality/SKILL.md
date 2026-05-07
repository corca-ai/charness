---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete next gates instead of only complaining about what is missing."
---
# Quality

Use this when the task is overall quality posture, not one narrow bug or one
isolated test. `quality` covers concept integrity, behavior proof, security and
supply-chain posture, documentation drift, skill maintenance drift, and
operator sustainability.

Default to inspecting the system that produces quality, running existing gates,
and making concrete next gates or cleanups. Prefer deterministic enforcement
over repeated prose when a linter, validator, test, hook, script, or command
can own the concern. Use concept review when unresolved boundary, ownership, or
architecture is the real issue. Length, duplicate, and pressure heuristics are
structural smell sensors; the win is delete, merge, split ownership, extract a
helper, or narrow an interface.

`quality` may also install or refresh deterministic, low-risk repo-local
quality posture. Review posture and bootstrap posture remain one public concept.

## Bootstrap

Resolve the adapter first, then re-derive the current source, spec, artifact,
and gate surface before trusting a prior review.

Key references for the frequent path are `references/bootstrap-escalations.md`,
`references/inventory-dispatch.md`, `references/skill-ergonomics.md`, and
`references/skill-quality.md`.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/bootstrap_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/resolve_quality_artifact.py" --repo-root . --intent current
rg --files .
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
git status --short
```

If the adapter is missing, continue with inferred defaults. Scaffold or refresh
one when the repo already has stable gate commands, installed command groups,
concept paths, preset lineage, or deferred setup worth recording.

Use `references/bootstrap-escalations.md` for missing validation tools,
reader-facing Markdown preview, evaluator-backed behavior proof, artifact
write-path handling, and other non-default bootstrap paths.
When writing the quality artifact, edit the resolved `write_artifact_path`, not
`latest.md` by habit.

## Workflow

1. Restate the quality question: scope, likely wrong boundary or ownership
   seam, and whether read-only constraints downgrade conclusions.
2. Detect the current gate and source surface.
   - enumerate source, specs, docs, adapters, skill surfaces, and commands
     before letting the previous quality artifact define scope
   - use `references/inventory-dispatch.md` to choose focused inventories for
     CLI/operator surfaces, docs/readability, skills, runtime/economics,
     source hygiene, security/supply chain, coverage/eval depth, and adapter
     policy
   - when skills are in scope, run skill ergonomics inventory; when
     public-skill or durable artifact behavior is in scope, scaffold one
     consumer-side dogfood case with
     `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>`
   - when validators pin prose or support-skill routing is implicit, inspect
     whether the gate proves a behavior contract or only freezes wording and
     whether `find-skills` can surface the support seam from task language
3. Run the meaningful gates that already exist.
   - prefer repo-native commands over hypothetical recommendations
   - run executable-spec overlap or cost guards before proposing more spec
     coverage
   - for standing-test economics, inspect duplicated proof, runner isolation,
     startup cost, and hot spots before pruning tests or widening budgets
   - before reporting runtime trends, prefer
     `$SKILL_DIR/scripts/render_runtime_summary.py`; if structured samples are
     missing, report that as the next gate instead of inventing numbers
4. Inspect four quality lenses.
   - `concept`: does the repo still match its claimed architecture and
     ownership model
   - `behavior`: do tests, evals, checks, probes, and command surfaces prove
     falsifiable behavior without making the test surface unmaintainable
   - `security`: are code, secret, dependency, and supply-chain risks covered
     by repo-local proof or honestly deferred
   - `operability`: are setup, CI, hooks, docs, install/update flows, runtime
     budgets, and maintenance surfaces honest enough to sustain the bar
5. Classify each finding by enforcement tier first.
   - `AUTO_EXISTING`: an existing deterministic gate owns it
   - `AUTO_CANDIDATE`: a low-noise invariant could own it with a clear
     structural failure response
   - `NON_AUTOMATABLE`: judgment, ownership, or product context decides it
6. Classify posture as `healthy`, `weak`, `missing`, or `defer`.
7. Propose concrete next quality moves.
   - tag each recommended next gate as `active` or `passive`
   - name the exact seam, command family, setup, or deletion/merge/split move
   - implement clear repo-owned automation unless the user asked for review only
   - do not leave dual implementations, duplicated proof, or stale command
     surfaces in an unpriced "keep both for safety" state
8. Run bounded fresh-eye review after initial inventory and before broad
   recommendations. Report exactly `Delegated Review: executed|blocked|not_applicable`.
   Blocked requires a concrete host or tool signal; use
   `../../shared/references/fresh-eye-subagent-review.md`.
9. End with a quality posture summary that does not hide `Weak`, `Missing`,
   `Advisory`, delegated-review status, or active recommended next gates just
   because the implemented slice or final gate passed.

## Load-Bearing Anchors

These phrases stay in core because validators and consumer prompts use them as
routing anchors; references carry the detail.

- The prior quality artifact is history; a fresh 5-minute reader can misclassify as absent an invariant that is merely scattered, so do not dismiss that as reader noise.
- For evaluator-backed behavior closeout, prompt regression, baseline compare, or operator reading test, use `quality` before downgrading to HITL. Generic review, closeout, or "run quality" wording is not enough to run an evaluator.
- When the next quality move is repo-local, deterministic, and low-risk, prefer implementing that gate in the same turn; when the automatable move is already clear and repo-owned, implement it in the same turn unless review-only was requested. If you stop short of an obvious repo-owned deterministic gate, name the unresolved enforcement gap.
- Do not stop at producer-side validators alone when the risk is public-skill routing or durable artifact behavior; scaffold one consumer-side dogfood case with `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>`.
- Skill review uses `$SKILL_DIR/scripts/inventory_skill_ergonomics.py`, skill ergonomics, mode/option pressure, trigger overlap, undertrigger risk, taste policing, and repeated prose ritual checks.
- CLI/operator review uses `$SKILL_DIR/scripts/inventory_cli_ergonomics.py`, flat help-list, multiple archetype schema namespaces, `$SKILL_DIR/scripts/inventory_cli_side_effect_probes.py`, option-looking positional rejection, mutating command probes, and command-docs drift gate checks.
- Docs/spec review uses `$SKILL_DIR/scripts/inventory_entrypoint_docs_ergonomics.py`, entrypoint-doc ergonomics, smart agent/operator can infer safely, doc-set dogma, ordinary Markdown uses the markdown preview seam, and executable specs use the rendered Specdown report.
- Public-spec review uses `$SKILL_DIR/scripts/inventory_public_spec_quality.py`; ask what proof is duplicated at the wrong layer before adding more specs, and surface total source-guard rows, top specs, brittle count, and next action category together.
- Runtime review uses `$SKILL_DIR/scripts/inventory_standing_gate_verbosity.py`, `$SKILL_DIR/scripts/inventory_standing_test_economics.py`, standing-gate-verbosity.md, file/process/startup cost, runner isolation/process mode, verbose-on-demand escape hatch, quiet failure output must still name the failing unit, top-N runtime hot spots, serial fallback, runtime_budget_profiles, Pytest Economics, and bounded test-ratio posture.
- Source hygiene review uses `$SKILL_DIR/scripts/inventory_dual_implementation.py`, free safety oracle checks, `$SKILL_DIR/scripts/inventory_lint_ignores.py`, lint suppressions start to accumulate, lint suppression pressure, growing lint suppressions, retained policy-level ignores, and concrete revisit conditions.
- Language baselines stay explicit: For Python, default to `ruff check` as the standing lint path, include `C90`, and choose exactly one type checker (`mypy` or `pyright`). For JavaScript/TypeScript, default to `eslint`, use `tsc --noEmit` when TypeScript is present, and turn on a `complexity` rule.
- This is a routing default, not a veto against good deterministic enforcement; do not over-apply it to standing threshold gates such as coverage floors, runtime budgets, or other already-honest enforced limits.
- prefer the smaller production surface first when the same confidence gap can be closed by shrinking production branches/interfaces or adding more tests.
- Watch stale gate wiring and hidden network/external-repo work in maintainer-local enforcement.
- when prompt-sensitive output matters or `prompt_asset_policy.source_globs` is configured, inspect prompt/content bulk. `prompt_asset_roots: []` only means no canonical asset root is declared, not that inline prompt/content bulk inventory should be skipped. The final user-facing answer must not silently omit `Weak`, `Missing`, `Advisory`, delegated-review status, or active `Recommended Next Gates` findings.
- Do not treat a passing length, duplicate, or pressure heuristic as the goal; delete, merge, split ownership, extract a helper, or narrow the interface.
- Run a bounded fresh-eye reviewer after initial inventory and before broad recommendations.

## Output Shape

Use the sections that match the scope, without reducing quality to one score:

- `Scope`, `Concept Risks`, `Current Gates`, `Runtime Signals`,
  `Standing Test Economics`, `Coverage and Eval Depth`,
  `Maintainer-Local Enforcement`, `Enforcement Triage`, `Healthy`, `Weak`,
  `Missing`, `Deferred`, `Advisory`, `Delegated Review`, `Commands Run`,
  `Recommended Next Gates`

## Guardrails

- Do not split bounded repo-local quality setup into another public concept.
- Do not recommend gates the repo cannot realistically run without saying why.
- Do not treat a passing metric or green gate as the goal; name the structural
  simplification or ownership clarification.
- Do not leave automatable rules as prose-only guidance.
- Do not treat a passing final local gate as sufficient when clones lack a
  repo-owned pre-push path and no documented no-hook waiver exists.
- Do not give generic "add tests" or "improve security" advice without the
  seam and next setup.
- Do not dismiss fresh-eye misreads when scattered evidence or undeclared
  enforcement is the real gap.
- Do not stop at producer-side validators when public-skill routing or durable
  artifact behavior is the risk; run or name a consumer prompt and artifact.

## References

- `references/adapter-contract.md`
- `references/adapter-gate-review.md`
- `references/automation-promotion.md`
- `references/bootstrap-escalations.md`
- `references/bootstrap-posture.md`
- `references/brittle-source-guards.md`
- `references/cli-ergonomics-smells.md`
- `references/coverage-floor-exemptions.txt`
- `references/coverage_floor_inventory.py`
- `references/coverage-floor-policy.md`
- `references/dual-implementation-parity.md`
- `references/entrypoint-docs-ergonomics.md`
- `references/executable-spec-economics.md`
- `references/find_inline_prompt_bulk.py`
- `references/gate-classification.md`
- `references/installable-cli-probes.md`
- `references/inventory-dispatch.md`
- `references/lint-ignore-discipline.md`
- `references/maintainer-local-enforcement.md`
- `references/operability-signals.md`
- `references/prompt-asset-policy.md`
- `references/proposal-flow.md`
- `references/public-spec-layering.md`
- `references/quality-lenses.md`
- `references/sample-presets.md`
- `references/security-overview.md`
- `references/security-npm.md`
- `references/security-pnpm.md`
- `references/security-uv.md`
- `references/skill-quality.md`
- `references/skill-ergonomics.md`
- `references/standing-gate-verbosity.md`
- `references/startup-probes.md`
- `references/validate_spec_pytest_references.py`
- `../../shared/references/fresh-eye-subagent-review.md`

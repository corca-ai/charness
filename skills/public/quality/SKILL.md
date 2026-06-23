---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete next gates instead of only complaining about what is missing."
---
# Quality

Use this when the task is overall quality posture, not one narrow bug or
isolated test. `quality` covers concept integrity, behavior proof, security and
supply-chain posture, docs drift, skill drift, agent production runtime risk,
and operator sustainability.

Default to inspecting the system that produces quality, running existing gates,
and making concrete next gates or cleanups. Prefer deterministic enforcement
over repeated prose when a linter, validator, test, hook, script, or command
can own the concern. Use concept review when unresolved boundary, ownership, or
architecture is the real issue. Length, duplicate, and pressure heuristics are
structural smell sensors; the win is delete, merge, split ownership, extract a
helper, or narrow an interface.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then
resolve the adapter and re-derive the source, spec, artifact, and gate surface
before trusting a prior review.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/bootstrap_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/resolve_quality_artifact.py" --repo-root . --intent current
python3 "$SKILL_DIR/scripts/plan_quality_run.py" --repo-root .
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
When writing the quality artifact, run the scaffold helper
`python3 "$SKILL_DIR/scripts/scaffold_quality_artifact.py" --repo-root .` for a
validator-passing skeleton; edit its resolved `write_artifact_path`, not `latest.md`.

## Workflow

1. Restate the quality question: scope, likely wrong boundary or ownership seam, and whether read-only constraints downgrade conclusions.
2. Detect the current gate and source surface.
   - enumerate source, specs, docs, adapters, skill surfaces, and commands
     before letting the previous quality artifact define scope
   - after the planner primer, use `references/inventory-dispatch.md` to choose
     focused inventories for CLI/operator surfaces, docs/readability, skills,
     runtime/economics, source hygiene, security/supply chain, coverage/eval
     depth, and adapter policy
   - when skills are in scope, run skill ergonomics inventory; when
     public-skill or durable artifact behavior is in scope, scaffold one
     consumer-side dogfood case with
     `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>`
   - when validators pin prose or support-skill routing is implicit, inspect
     whether the gate proves a behavior contract or only freezes wording and
     whether `find-skills` can surface the support seam from task language
   - treat migration-time exact-prose guards as temporary bridges; when `inventory_skill_ergonomics.py` is cited, closeout uses `prose review result:` to record judgment separately from script fields
3. Run `plan_quality_run.py`, read its `required_primer_refs`, and obey its
   report-first phase barriers before broad gates or fixes.
4. Run the meaningful gates that already exist.
   - prefer repo-native commands over hypothetical recommendations
   - resolve and run the Charness package-root validator `validate_usage_episodes.py` and report `report_usage_episodes.py`; `no_adapter`, `disabled`, and `no_records` are skipped warnings, not product-success proof or failures
   - keep exit-zero attention states visible with `validate_attention_state_visibility.py`; new skipped/advisory states need warning output, artifact-visible status, or an explicit local-noop declaration
   - run executable-spec overlap or cost guards before proposing more spec
     coverage
   - for standing-test economics, testability, or affected-test-selection questions, inspect duplicated proof, duplicate discovery, broad scanner waste, runner isolation, startup cost, hot spots, and structural seams before pruning tests, widening budgets, or adding observation tools; use `references/testability-and-selection.md`
   - before reporting runtime trends, prefer
     `$SKILL_DIR/scripts/render_runtime_summary.py`; if structured samples are
     missing, report that as the next gate instead of inventing numbers
   - Before invoking any `cautilus evaluate ...` subcommand, consult the planner-consult contract
     at `references/cautilus-on-demand.md`; refuse on `next_action: "none"` (or
     `must_ask_before_running: true` without a named failing-log path), and
     route the call through the repo-owned wrapper instead of bare `cautilus evaluate`.
     Supported modes are `fixture`, `observation`, `skill-experiment`; for
     recommend-only behavior tests use `references/behavior-testing.md`.
5. Inspect four quality lenses; the lens detail and named-expert defaults live in `references/quality-lenses.md`.
   - `concept`: does the repo still match its claimed architecture and
     ownership model
   - `behavior`: do tests, evals, checks, probes, and command surfaces prove
     falsifiable behavior without making the test surface unmaintainable
   - `security`: are code, secret, dependency, and supply-chain risks covered
     by repo-local proof or honestly deferred
   - `operability`: are setup, CI, hooks, docs, install/update flows, runtime
     budgets, and maintenance surfaces honest enough to sustain the bar (detail: `references/operability-signals.md`)
6. Classify each finding by enforcement tier first: `AUTO_EXISTING`,
   `AUTO_CANDIDATE`, or `NON_AUTOMATABLE`.
7. Classify posture as `healthy`, `weak`, `missing`, or `defer`.
8. Propose concrete next quality moves.
   - tag each recommended next gate as `active` or `passive`
   - name the exact seam, command family, setup, or deletion/merge/split move
   - implement clear repo-owned automation unless the user asked for review only
   - do not leave dual implementations, duplicated proof, or stale command
     surfaces in an unpriced "keep both for safety" state
   - When the next quality move is repo-local, deterministic, and low-risk,
     implement it the same turn unless review-only was requested.
     If you stop short of an obvious repo-owned deterministic gate, name the
     unresolved enforcement gap.
9. Run a bounded fresh-eye reviewer after initial inventory and before broad recommendations
   as `high-leverage`, applying host-exposed
   `reviewer_tiers.high-leverage` fields. Report exactly
   `Delegated Review: executed|blocked|not_applicable`. Blocked requires a concrete
   host or tool signal; use `../../shared/references/fresh-eye-subagent-review.md`.
10. End with a quality posture summary. The final user-facing answer must not silently omit `Weak`, `Missing`, `Advisory`, delegated-review status, or active `Recommended Next Gates` findings just because the implemented slice or final gate passed.

## Routing

Detailed inventory routing — CLI/operator, docs/spec, skills, runtime/test
economics, source hygiene, behavior/evaluator and Cautilus, boundary-bypass and
duplicate ratchets, language lint baselines, agent-production-runtime, and
coverage/eval — lives in `references/inventory-dispatch.md`. Reach for a focused
inventory only when the quality question brings that surface into scope; the
judgment that governs every route is in `## Workflow` and `## Guardrails`.

## Output Shape

- `Scope`, `Concept Risks`, `Current Gates`, `Runtime Signals`, `Standing Test Economics`, `Testability and Selection`, `Coverage and Eval Depth`, `Maintainer-Local Enforcement`, `CI/Local Gate Parity`, `Enforcement Triage`, `Healthy`, `Weak`, `Missing`, `Deferred`, `Advisory`, `Delegated Review`, `Commands Run`, `Recommended Next Gates`

## Guardrails

- Do not split bounded repo-local quality setup into another public concept.
- Do not recommend gates the repo cannot realistically run without saying why.
- Do not treat a passing length, duplicate, or pressure heuristic as the goal, and do not treat a passing metric or green gate as the goal; delete, merge, split ownership, extract a helper, or narrow the interface.
- When the same confidence gap can be closed by shrinking production branches/interfaces rather than adding more tests, prefer the smaller production surface first.
- Do not leave automatable rules as prose-only guidance.
- Do not treat a passing local gate as sufficient when clones lack a repo-owned pre-push path (no no-hook waiver), or when CI appends required `run:` steps or `CI-only` gates after it; required proof must be reachable locally. See `references/maintainer-local-enforcement.md`. The CI-recoverability lens is the bounded counterweight (not a loophole): it proposes moving a gate off-local only when CI fully re-runs that proof; see `references/ci-recoverable-gate-triage.md`. Watch stale gate wiring and hidden network/external-repo work in maintainer-local enforcement.
- Do not give generic "add tests" or "improve security" advice without the seam and next setup.
- The prior quality artifact is history; a fresh 5-minute reader can misclassify as absent an invariant that is merely scattered, so do not dismiss fresh-eye misreads as reader noise when scattered evidence or undeclared enforcement is the real gap.
- Do not stop at producer-side validators alone when the risk is public-skill routing or durable artifact behavior; scaffold or name one consumer-side dogfood case and artifact.
- Inspect inline prompt/content inventory when prompt-sensitive output matters or `prompt_asset_policy.source_globs` is configured; routing in `references/inventory-dispatch.md`.
- Do not write size, runtime, or cost numbers that did not come from a command run this turn; label estimates explicitly. See `references/proposal-flow.md`.
- Do not propose a new enforcement gate for an advisory cost before checking `git log -S`, `grep -rn`, and `pyproject.toml` markers for an existing convention; if one is ignored, the recommendation is the routing fix. See `references/proposal-flow.md`.

## References

- `references/adapter-contract.md`
- `references/adapter-gate-review.md`
- `references/agent-production-runtime.md`
- `references/attention-state-visibility.json`
- `references/automation-promotion.md`
- `references/bootstrap-escalations.md`
- `references/bootstrap-posture.md`
- `references/brittle-source-guards.md`
- `references/boundary-bypass-ratchet.md`
- `references/boundary-bypass-payload.example.json`
- `references/cautilus-on-demand.md`
- `references/behavior-testing.md`
- `references/ci-recoverable-gate-triage.md`
- `references/cli-ergonomics-smells.md`
- `references/coverage-floor-exemptions.txt`
- `references/coverage_floor_inventory.py`
- `references/coverage-floor-policy.md`
- `references/dual-implementation-parity.md`
- `references/dup-ratchet.md`
- `references/entrypoint-docs-ergonomics.md`
- `references/executable-spec-economics.md`
- `references/find_inline_prompt_bulk.py`
- `references/gate-classification.md`
- `references/installable-cli-probes.md`
- `references/inventory-consumer-fields.json`
- `references/inventory-dispatch.md`
- `references/lint-ignore-discipline.md`
- `references/maintainer-local-enforcement.md`
- `references/mutation-testing.md`
- `references/operability-signals.md`
- `references/prompt-asset-policy.md`
- `references/proposal-flow.md`
- `references/public-spec-layering.md`
- `references/quality-lenses.md`
- `references/quality-signal-scorecard.md`
- `references/security-overview.md`
- `references/security-npm.md`
- `references/security-pnpm.md`
- `references/security-uv.md`
- `references/skill-quality.md`
- `references/skill-ergonomics.md`
- `references/standing-doc-provenance.md`
- `references/standing-gate-verbosity.md`
- `references/testability-and-selection.md`
- `references/unit-test-quality.md`
- `references/validate_spec_pytest_references.py`
- `../../shared/references/agent-assessment-invariant.md`
- `../../shared/references/fresh-eye-subagent-review.md`
- `../../shared/references/external-capability-proof-ladder.md`

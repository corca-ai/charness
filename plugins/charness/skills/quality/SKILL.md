---
name: quality
description: "Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete next gates instead of only complaining about what is missing."
---
# Quality

Use this when the task is overall quality posture, not only one narrow bug or one isolated test. `quality` covers concept integrity review, test confidence, security and supply-chain posture, skill and maintenance drift, and documentation drift. The job is to understand the current quality surface, run the meaningful gates that already exist, and propose the missing ones concretely. Use Gerald Weinberg-style systems thinking when the question crosses code, tests, docs, operators, and local process: inspect the whole system producing quality, not only the last failed check. `quality` may also install or refresh the repo-local quality posture when the next move is deterministic setup work instead of only review. Keep that inside the same public concept: review posture and bootstrap posture are two states of `quality`, not separate skills. When the next quality move is repo-local, deterministic, and low-risk, prefer implementing that gate in the same turn.
Deterministic gates should define pass/fail authority wherever possible. If a concern can be enforced by a linter, validator, test, hook, or script, promote it into that gate instead of leaving it as repeated prose advice. Maintainer-local enforcement counts when the repo depends on it; if the final stop-before-finish gate has no checked-in hook, installer, or documented no-hook policy, name that as a missing enforcement gap. Use concept review instead when the real problem is unresolved boundary or ownership design. See `references/maintainer-local-enforcement.md` and `references/quality-lenses.md`. Treat length, duplicate, and pressure heuristics as structural smell sensors, not goals in themselves. When one of those signals fires, look first for the structural move it points at: delete dead surface, merge competing copies, split ownership, extract a repeated helper, or narrow an interface. Do not call a cosmetic shrink-to-fit edit a quality win if the underlying design pressure is still present.
This is a routing default, not a veto against good deterministic enforcement. For length, duplicate, and pressure signals, default to concept-review advisory first; if the repo can state one explicit low-noise invariant and a failure implies a clear structural response, the same seam may still graduate to `AUTO_CANDIDATE` or `AUTO_EXISTING`. Do not generalize this caution to standing threshold gates such as coverage floors, runtime budgets, or other already-honest enforced limits.
When the repo lacks concrete lint defaults, prefer explicit language baselines over taste-driven tool sprawl. For Python, default to `ruff check` as the standing lint path, include `C90`/mccabe for complexity, and choose exactly one type checker (`mypy` or `pyright`). For JavaScript/TypeScript, default to `eslint` and, when TypeScript is present, `tsc --noEmit`; if `eslint` is the standing linter, turn on a `complexity` rule instead of relying only on file/function length. Treat `B`, `UP`, `SIM`, `deptry`, `knip`, `shellcheck`, `lychee`, `secretlint`, or `gitleaks` as repo-surface-driven escalations, not mandatory first-day defaults. See `references/sample-presets.md` and the shipped `python-quality` / `typescript-quality` presets.

## Bootstrap

Resolve the adapter first, then inspect the current quality surface. Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

If the repo already has repo-owned quality commands or needs a first-pass installed posture, bootstrap the adapter and capture deferred setup in a machine-readable report:

```bash
python3 "$SKILL_DIR/scripts/bootstrap_adapter.py" --repo-root .
```

When stronger local proof depends on a missing validation tool, reuse the shared recommendation/install payload instead of inventing prose-only install advice. If an existing gate is blocked only by a missing validation binary, treat that as setup work: name the missing binary and verify command, install when the user already asked for installation or local closeout, otherwise ask, then rerun the blocked gate.

```bash
python3 "$SKILL_DIR/scripts/list_tool_recommendations.py" --repo-root .
```

For evaluator-backed review, closeout, or operator reading test work, run that validation recommendation route before downgrading to HITL or same-agent manual review.
For task-completing quality reviews, run a bounded multi-lens delegated review
before final closeout. Use at least `gate-design`, `adapter-policy`, and
`operator-signal` lenses unless the adapter narrows them. Report
`Delegated Review: executed`, `blocked`, or `not_applicable`; a blocked state
needs a concrete host/tool signal and must not be replaced with a same-agent
pass.
When reader-facing Markdown needs rendered readability proof instead of source-only review, bootstrap or execute the repo-local markdown preview seam:

```bash
python3 "$SKILL_DIR/scripts/list_tool_recommendations.py" --repo-root . --recommendation-role runtime --next-skill-id quality
python3 "$SKILL_DIR/scripts/bootstrap_markdown_preview.py" --repo-root .
python3 "$SKILL_DIR/scripts/bootstrap_markdown_preview.py" --repo-root . --execute
```

Keep `latest.md` short and current; move older review detail into sibling `history/*.md` archives when today's posture starts getting buried. If the adapter is missing and the repo only needs a blank scaffold instead of detected bootstrap, scaffold one directly:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root . --preset-id portable-defaults
```

The prior quality artifact is history, not the authoritative universe. Re-derive the current source, spec, and gate surface before trusting what the last artifact happened to mention.

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
# 1. fresh inventory before the prior artifact can anchor scope
rg --files .
# 2. current quality artifact and adjacent contracts
sed -n '1,220p' <resolved-quality-artifact> 2>/dev/null || true
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
rg --files docs skills
# 3. repo signals and maintainer-local enforcement surface
rg -n "eslint|ruff|mypy|pyright|tsc|pytest|vitest|jest|coverage|deptry|knip|audit|sast|owasp|threat|architecture|concept|markdownlint|secretlint|shellcheck|lychee|gitleaks|trufflehog|pre-push|prepush|githook|husky|simple-git-hooks|lefthook|core\.hooksPath|actions/checkout|actions/setup-node|actions/setup-go|actions/setup-python|actions/cache|actions/github-script|check-github-actions" .
git config --get core.hooksPath || true
find .git/hooks -maxdepth 1 -type f 2>/dev/null | sort
# 4. current repo state
git status --short
```

If the adapter is missing, use inferred defaults and continue; scaffold one when the repo already has stable gate commands worth recording. Prefer `bootstrap_adapter.py` when the adapter should record installed command groups, inferred concept paths, preset lineage, or deferred setup in one pass.

## Workflow

1. Restate the current quality question: what the user wants checked or improved, whether the scope is repo-wide, one seam, or one proposed change, and which concept boundary or ownership seam is most likely to be wrong.
2. Detect the current gate surface.
   - independently enumerate the current source, spec, and gate inventory before letting the previous quality artifact define scope
   - local executable gates already present
   - if the repo ships an installable CLI, bootstrap command, or operator-facing command surface, inspect whether help, command discovery, binary health, install/readiness, local discoverability, canonical-target vs multi-target lifecycle ownership, and cleanup ownership are separated honestly
   - when README, docs, or public-spec prose readability is part of the review, run the markdown preview seam or leave an explicit bootstrap payload instead of treating raw Markdown as equivalent proof
   - when CLI ergonomics are in scope, inventory flat help-list and cross-archetype schema smells with `$SKILL_DIR/scripts/inventory_cli_ergonomics.py`
   - when a standing local gate exists, inventory quiet-default vs verbose-on-demand posture with `$SKILL_DIR/scripts/inventory_standing_gate_verbosity.py`
   - when the repo may keep one shipped implementation beside a historical or alternate runtime path, inventory likely dual-implementation parity smells with `$SKILL_DIR/scripts/inventory_dual_implementation.py`, then decide whether the relationship is parity-enforced, canonical-plus-legacy, or intentional divergence
   - when first-touch operator/developer/agent docs are in scope, inventory entrypoint-doc ergonomics with `$SKILL_DIR/scripts/inventory_entrypoint_docs_ergonomics.py`
   - when public executable specs are in scope, inventory reader-facing public-spec drift and proof-layering overlap with `$SKILL_DIR/scripts/inventory_public_spec_quality.py`; see `references/public-spec-layering.md`
   - when fixed-string source guards touch prose, inventory hard-wrap fragility with `$SKILL_DIR/scripts/inventory_brittle_source_guards.py`; see `references/brittle-source-guards.md`
   - when lint suppressions start to accumulate, inventory lint suppression pressure with `$SKILL_DIR/scripts/inventory_lint_ignores.py`; blanket or file-level ignores should be explicit review targets, not invisible background debt
   - inspect first-touch docs such as README and operator docs for drift against install, update, doctor, reset, or uninstall behavior when those commands exist; when the CLI surface is stable, prefer a deterministic command-docs drift gate over repeated prose review
   - executable-spec frameworks, adapter depth, and overlap controls when the repo keeps acceptance checks in specs
   - if evaluator-backed review or prompt-sensitive output matters, inspect whether prompt/content bulk stays in checked-in assets or is still embedded inline in source files
   - inventory adapter/gate design with `$SKILL_DIR/scripts/inventory_adapter_gate_design.py`
     when the review touches adapter policy, recommendation queues,
     acknowledgements, or brittle gate promotion; see
     `references/adapter-gate-review.md`
   - when skills are in scope, inventory skill ergonomics explicitly with `$SKILL_DIR/scripts/inventory_skill_ergonomics.py` instead of leaving concise-core, progressive-disclosure, or branching-pressure review as vague prose
   - when public-skill behavior or routing is in scope, scaffold one consumer-side dogfood case with `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>` so the review names prompt, repo shape, expected artifact, and acceptance evidence explicitly
   - when the adapter defines `prompt_asset_roots` or `prompt_asset_policy`, re-derive prompt/content bulk inventory from the current tree instead of trusting prior review prose
   - if the repo keeps standing coverage floors, tag seams within `coverage_fragile_margin_pp` as `FRAGILE` instead of burying near-miss risk in prose
   - for blind-spot prevention, apply `references/coverage-floor-policy.md`: adapter-owned `coverage_floor_policy`, real unfloored-file inventory, and `Covered by pytest:` reference validation when those notes exist
   - maintainer-local enforcement for the final stop-before-finish gate: a checked-in hook, installer, or explicit no-hook policy, and whether the next move is review-only or a bounded bootstrap/install pass
3. Run the meaningful gates that already exist.
   - prefer repo-native commands over hypothetical recommendations
   - if the repo has executable-spec overlap or cost guards, run those before proposing more spec coverage
   - when a standing gate already exists, prefer compact default phase output plus a verbose-on-demand escape hatch over always-on chatter; see `references/standing-gate-verbosity.md`
   - when a hot spot becomes the standing single dominator, define a `runtime_budgets` entry in the adapter and call `$SKILL_DIR/scripts/check_runtime_budget.py` from the repo's standing gate; budgets fail on recent-median drift, report latest-sample spikes separately, and should expose top-N runtime hot spots so unbudgeted slow phases are still visible
4. Inspect four quality lenses.
   - `concept`: does the repo still match its claimed architecture and ownership model
   - before proposing a new gate for length, duplicate, or pressure findings, ask which structural question the signal is exposing: delete, merge, split ownership, extract a helper, or narrow the interface
   - `behavior`: do tests, evals, checks, and command-surface probes say something falsifiable about real behavior, and does the repo-owned test code stay maintainable
   - when dual-implementation smell is real, treat it as `weak` until the repo proves one honest contract: parity harness, canonical side plus deletion/wrapper plan, or intentional divergence backed by an assertion
   - if a fresh 5-minute reader could misread a present invariant as absent, treat that as a quality gap in declaration or gating rather than dismissing the reader
   - when the same confidence gap could be closed either by shrinking production branches/interfaces or by adding more tests, prefer the smaller production surface first if behavior and signal both improve
   - when executable specs exist, classify smoke vs behavior using the adapter's `specdown_smoke_patterns`, report the ratio, and treat bounded test-ratio posture as a named positive pattern when the repo constrains both under-testing and test-surface inflation
   - ask not only what proof is missing, but which proof is duplicated at the wrong layer now that a public executable contract exists
   - `security`: are there meaningful code, secret, or supply-chain risks
   - `operability`: are setup, CI, install/update docs, and maintenance surfaces honest enough to sustain the quality bar
   - make skill ergonomics explicit: concise `SKILL.md` core, progressive disclosure honesty, unnecessary mode/option pressure, trigger overlap/undertrigger risk, and prose ritual that should become a helper script
   - when the repo keeps major entrypoint docs, include entrypoint-doc ergonomics review: concise first-touch ownership, progressive disclosure into deeper owners, duplicate pressure between nearby entry docs, whether one canonical README-first bootstrap would be clearer than a separate install manual, and whether the prose overexplains branches a smart agent/operator can infer safely
   - make evaluator depth explicit: smoke only, maintained evaluator-backed, or still smoke plus HITL
   - if stronger local proof depends on an external binary or support tool, state whether it is currently installed and healthy, then surface the exact install and post-install verification path instead of vague prose
5. Classify each issue by enforcement tier first: `AUTO_EXISTING`, `AUTO_CANDIDATE`, or `NON_AUTOMATABLE`.
6. Classify gaps: `healthy`, `weak`, `missing`, or `defer`.
7. Propose the next quality moves concretely.
   - for missing or weak gates, name the exact setup or command family to add
   - tag every recommended next gate as `active` or `passive`; passive entries require an explicit reason such as future-tool dependency, broader product decision, or runtime budget tradeoff
   - prefer the smallest gate that materially improves confidence
   - keep standing-test economics runner-neutral in the public skill body: ask which standing proof is duplicated, which slices belong in `standing` vs `ci_only` vs `on_demand`, and what dominates critical-path wall time without hardcoding one runner family
   - before adding or tightening a gate around length, duplicate, or pressure signals, ask whether deleting code/docs, merging duplicated proof, splitting ownership, or extracting a helper is the cheaper and clearer fix
   - do not force one stack's tooling when the repo does not use that stack
   - when the problem is automatable, prefer a deterministic gate over prose
   - for every new `AUTO_CANDIDATE`, state the structural question it protects, why the invariant is low-noise enough to automate, and what concrete structural action a failure should trigger; otherwise keep it advisory or `NON_AUTOMATABLE`
   - when the automatable move is already clear and repo-owned, implement it in the same turn unless the user asked to stay review-only
   - when an agent-facing CLI needs latency proof, prefer adapter-owned `startup_probes` plus standing `runtime_budgets` over prose-only advice
   - when the next deterministic move is to install or refresh the repo-local quality surface itself, prefer the bootstrap posture and leave a machine-readable deferred-setup report
   - if executable specs are slow or overlapping, delete duplicates, move detail into unit-level checks, or add a direct adapter before widening the spec bar
   - when dual-implementation smell is real, recommend exactly one next contract: add a parity harness, pick one side canonical and delete or wrap the other, or document intentional divergence with a test that asserts it
   - do not leave "keep both for safety" as an unpriced middle state
8. Run one fresh-eye premortem on the drafted report using `references/fresh-eye-premortem.md`. Run the capability check in `../premortem/references/subagent-capability-check.md` before reporting the canonical fresh-eye subagent path as blocked: attempt the bounded setup, resolve availability uncertainty, and cite the concrete host signal. If the host still cannot provide subagents, stop and leave the host-side contract gap visible instead of substituting a local pass.
9. End with a quality posture summary: what ran, which runtime hot spots dominate, whether coverage is standing-gated, whether evaluator-backed depth exists, what the current bar proves and still does not prove, and the next best gate or cleanup.

- `Scope`, `Concept Risks`, `Current Gates`, `Runtime Signals`, `Standing Test Economics`, `Coverage and Eval Depth`, `Maintainer-Local Enforcement`, `Enforcement Triage`, `Healthy`, `Weak`, `Missing`, `Deferred`, `Advisory`, `Delegated Review`, `Commands Run`, `Recommended Next Gates`
- Do not reduce quality to one aggregate score.
- Do not split quality bootstrap into a second public concept when the work is still bounded repo-local quality setup.
- Do not recommend gates the repo cannot realistically run without saying why.
- Do not treat a passing length, duplicate, or pressure heuristic as the goal; the goal is the structural simplification or ownership clarification that made the heuristic quiet again.
- Do not ignore runtime drift just because a gate still passes functionally.
- Do not treat `pytest-xdist`, worker pools, or other parallel runners as present because a package is expected; prove the active command is actually using the parallel path or surface the serial fallback.
- Do not ask only what proof is missing when executable public specs land; ask what is duplicated at the wrong layer too.
- Do not wait for operator follow-up before stating current runtime hot spots, coverage-gate presence or absence, and evaluator-depth status when the repo signals are available.
- Keep runner-specific naming such as `Pytest Economics` or `Vitest Hotspots` in the repo adapter or repo-owned artifact, not in the portable public skill body.
- Do not treat slow or broad executable specs as automatically strong quality when they mostly duplicate cheaper deterministic coverage.
- Do not leave an automatable quality rule as prose-only guidance when a linter, validator, test, hook, or script could own it.
- Do not normalize growing lint suppressions as harmless cleanup debt; inventory them and ask whether structure should absorb the rule instead.
- Do not promote a heuristic to a hard gate unless the invariant is clear, false positives are low, and the expected structural response to failure is obvious.
- If you stop short of an obvious repo-owned deterministic gate, name that as an unresolved enforcement gap explicitly.
- Do not treat a passing final local gate as sufficient posture when clones have no repo-owned way to run it before push and no documented no-hook waiver.
- Do not propose generic "add more tests" or "improve security" without naming the actual seam, the next concrete setup, or whether the test surface now needs a maintainability gate.
- Do not dismiss a fresh-eye misread of a present invariant as reader noise when the real problem is undeclared enforcement or scattered evidence.
- Do not treat inline prompt/content bulk as automatically wrong; flag it as advisory inventory unless the repo already made it a standing local policy.
- If a gate already exists, prefer tightening or reusing it before adding a new parallel tool.
- Do not let whole-worktree scans fail on gitignored runtime artifacts unless the gate explicitly exists to validate that machine-local state.
- Do not stop at producer-side validators alone when the risk is public-skill routing or durable artifact behavior; run one realistic consumer prompt and name the expected artifact.
- Preserve these review anchors: stale gate wiring, free safety oracle, taste policing, doc-set dogma, and multiple archetype schema namespaces.

## References

- `references/adapter-contract.md`
- `references/adapter-gate-review.md`
- `references/coverage-floor-exemptions.txt`
- `references/coverage_floor_inventory.py`
- `references/coverage-floor-policy.md`
- `references/find_inline_prompt_bulk.py`
- `references/fresh-eye-premortem.md`
- `references/prompt-asset-policy.md`
- `references/maintainer-local-enforcement.md`
- `references/quality-lenses.md`
- `references/installable-cli-probes.md`
- `references/startup-probes.md`
- `references/skill-quality.md`
- `references/skill-ergonomics.md`
- `references/entrypoint-docs-ergonomics.md`
- `references/cli-ergonomics-smells.md`
- `references/standing-gate-verbosity.md`
- `references/dual-implementation-parity.md`
- `references/proposal-flow.md`
- `references/gate-classification.md`
- `references/automation-promotion.md`
- `references/bootstrap-posture.md`
- `references/operability-signals.md`
- `references/brittle-source-guards.md`
- `references/lint-ignore-discipline.md`
- `references/sample-presets.md`
- `references/executable-spec-economics.md`
- `references/public-spec-layering.md`
- `references/security-overview.md`
- `references/security-npm.md`
- `references/security-pnpm.md`
- `references/security-uv.md`
- `references/validate_spec_pytest_references.py`

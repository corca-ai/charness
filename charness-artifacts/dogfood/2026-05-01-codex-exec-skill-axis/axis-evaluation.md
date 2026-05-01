# Codex Exec Skill Axis Evaluation

Date: 2026-05-01

Scope: read-only dogfood of `charness:init-repo` and `charness:quality` through `codex exec` against `/home/ubuntu/charness` and `/home/ubuntu/ceal`, followed by bounded fresh-eye subagent review of whether the intended axes were actually covered.

## Capture Note

The four `codex exec` runs were started with `-o` output paths under `charness-artifacts/dogfood/2026-05-01-codex-exec-skill-axis/`. During the Charness `quality` run, a review-only validator unexpectedly created dogfood output, and the run removed the whole `charness-artifacts/dogfood/` subtree as self-generated cleanup. As a result, the final `-o` writes for `charness-quality.md` and `ceal-quality.md` failed with `No such file or directory`, and the earlier init-repo output files were also removed.

This document is the durable recovered record from the terminal output plus fresh-eye review. The target repos ended with clean `git status --short`.

## Source Contracts Checked

- `init-repo` is an evaluator-required, adapter-required public skill. Its dogfood expectation includes routing to `init-repo`, naming or refreshing `charness-artifacts/init-repo/latest.md` when durable state is persisted, and handling repo context without asking the user to restate it.
- `quality` is hitl-recommended and adapter-required. Its dogfood expectation includes routing to `quality`, producing maintainer-reviewable output, running or naming repo-owned quality gates, attempting bounded subagent review or recording a concrete blocked signal, checking fixture economics, parallel critical path, duplicated proof, runtime profile policy, and using a realistic consumer prompt when public-skill routing or artifact behavior is at risk.
- The current Cautilus/evaluator design is asymmetric: `init-repo` is in the evaluator-required scenario profile; `quality` has route-focused Cautilus cases and richer reviewed dogfood evidence, but is not in the evaluator-required tier.

## Codex Exec Run Records

### Charness `init-repo`

Mode: review-only dogfood. No edits, artifact write, commit, or task-completing normalization.

Commands and surfaces:

- Read `find-skills`, `init-repo` `SKILL.md`, and init-repo references.
- Ran `init-repo` `resolve_adapter.py`, `inspect_repo.py`, `render_skill_routing.py --json`.
- Ran `git status --short`, `git diff --stat`, `validate_adapters.py`, and `validate_current_pointer_freshness.py`.
- Inspected `AGENTS.md`, `CLAUDE.md`, `README.md`, `.agents/init-repo-adapter.yaml`, handoff/operator/convention/artifact/docs, `docs/readme-proof.md`, public dogfood/validation docs, quality/retro artifacts, and init-repo tests.

Reported coverage:

- Checked repo mode detection: `NORMALIZE`.
- Checked AGENTS/CLAUDE host policy: adequate; `CLAUDE.md` symlinks to `AGENTS.md`.
- Checked default operating surfaces: present, with `docs/roadmap.md` intentionally null by adapter.
- Checked skill routing: partial; `AGENTS.md` has `find-skills` startup guidance but not the generated literal `## Skill Routing` block. Adapter acknowledges the custom routing surface.
- Checked artifact/state policy: partial; no `charness-artifacts/init-repo/latest.md` exists despite dogfood expectation.
- Checked delegated-review policy: adequate in Charness `AGENTS.md`; no task-completing spawn was needed for this read-only run.
- Checked operator takeover: partial; docs exist but quality posture still flags README/operator proof layering.
- Checked adapter fit and handoff-to-quality boundary.

Proposals captured:

- Keep `init-repo` narrow; route deeper proof/gate posture to `quality`.
- Decide whether Charness should actually carry `charness-artifacts/init-repo/latest.md`, because dogfood expectations imply it.

### Ceal `init-repo`

Mode: review-only dogfood. No edits, artifact refresh, commit, or task-completing normalization.

Commands and surfaces:

- Read `find-skills`, `init-repo` `SKILL.md`, and relevant references.
- Ran `init-repo` `resolve_adapter.py`, `inspect_repo.py`, `render_skill_routing.py`, and find-skills adapter resolution.
- Inspected `AGENTS.md`, `CLAUDE.md`, `README.md`, roadmap/operator/troubleshooting/admin docs, handoff/lesson/quality/init-repo artifacts, `.agents/init-repo-adapter.yaml`, and `package.json`.

Reported coverage:

- Checked repo mode detection: `NORMALIZE`.
- Checked AGENTS/CLAUDE host policy: partial. Ceal has premortem delegation wording, but not a dedicated `## Subagent Delegation` section and not explicit task-completing `init-repo`/`quality` scope.
- Checked default operating surfaces, skill routing, artifact/state policy, operator takeover, and handoff to quality.
- Checked adapter fit: partial/stale relative to newer delegated-review expectation.

Findings captured:

- Add a dedicated `## Subagent Delegation` section covering task-completing `init-repo` and `quality`.
- Refresh `charness-artifacts/init-repo/latest.md`; it claimed ok while current inspector reported `needs_normalization`.
- No broad scaffold/rewrite was recommended.

### Charness `quality`

Mode: review-only dogfood. No intentional edits or commits. Full `run-quality.sh` was skipped because it records runtime samples.

Commands and surfaces:

- Read `find-skills`, `quality` `SKILL.md`, quality artifact, adapter, scripts, docs, and tests.
- Ran quality adapter resolution, tool recommendations, runtime summary, runtime budget, quality artifact validation, maintainer setup validation, public skill validation, adapter validation, supply-chain check, secret check, coverage JSON, test ratio, test completeness, and focused pytest for quality runner/skill ergonomics/runtime budget.
- Ran quality inventories: CLI ergonomics, standing gate verbosity, adapter gate design, skill ergonomics, entrypoint docs ergonomics, public spec quality, lint ignore pressure, gitignore scan hygiene, dual implementation, and prompt bulk.
- Targeted pytest passed: 27 tests.

Reported coverage:

- Checked current gate surface, repo-owned gates, concept/architecture integrity, behavior/test confidence, security/supply chain, docs/operator drift, skill ergonomics, runtime economics, adapter/gate design, maintainer-local enforcement, advisory inventories, active vs passive next gates, and delegated review.
- Correctly classified several areas as partial/advisory rather than enforced: docs/operator proof, skill ergonomics, adapter phrase-detector policy, public-spec drift, coverage/eval depth, and active/passive next gates.

Findings captured:

- The broad quality axes were considered, but not all are standing gates.
- Skipping `./scripts/run-quality.sh --review` was defensible for read-only dogfood, but it means the exact integrated review gate was not executed.
- README/operator proof remains partial and should not be presented as fully proven.
- The dogfood validator needs a dry-run/read-only mode; this run created and removed the output directory used by `codex exec -o`.

### Ceal `quality`

Mode: review-only dogfood. No edits, artifact refresh, commit, or delegated review.

Commands and surfaces:

- Read `find-skills`, `quality` `SKILL.md`, Ceal memory/docs, adapter, quality artifact, package/workflow/hook/script/spec surfaces, official skill files, and log metadata.
- Ran quality adapter resolution, `npm run --silent lint:coverage-floor`, `lint:secrets`, doc link check, `lint:spec-assumptions`, `lint:skills:inventory`, `lint:log-policies`, `lint:lockfile`, `lint:test-ratio`, quality inventories, runtime budget, and runtime summary.
- Skipped write-prone or broad commands: find-skills canonical capability refresh, bootstrap writers, full lint, pre-push runner, full spec budget, and networked audit.

Reported coverage:

- Checked gate surface, named repo-owned gates, behavior/test confidence, coverage/eval depth, security/supply chain, docs/operator drift, adapter/gate design, maintainer-local enforcement, and advisory inventories.
- Classified concept/architecture integrity, skill ergonomics, runtime economics, and active/passive next gates as partial.
- Delegated review was missed.

Findings captured:

- Runtime economics are documented and logged, but the adapter has no `runtime_budgets`; `check_runtime_budget.py` therefore cannot prove enforced runtime health.
- Skill ergonomics scan misses repo skills by default because the adapter does not declare skill paths.
- Coverage posture is useful but noisy; promotion work should stay selective.

## Fresh-Eye Review Results

Subagents:

- `019de1f8-e357-7523-a615-3fd38f70db6f`: init-repo axis review.
- `019de1f8-e38f-71b1-8d08-37810da8cb0d`: quality axis review.

Findings:

1. Both `init-repo` runs were valid read-only dogfood, but they did not prove task-completing normalization. The missing proof is artifact write/refresh, closeout/commit behavior, and bounded reviewer execution for task-completing normalization.
2. Charness `init-repo` artifact/state coverage is incomplete, not failed. The missing `charness-artifacts/init-repo/latest.md` matters because the dogfood registry expects that path when the skill persists durable state.
3. Ceal `init-repo` correctly found a stale artifact and delegated-review policy gap. The rule is hidden under `### Premortem Gate` and does not explicitly authorize task-completing `init-repo`/`quality`.
4. Charness delegated-review policy is adequate: it has a dedicated `## Subagent Delegation` section, explicit user-delegation wording, task-completing `init-repo`/`quality` scope, and host-block reporting.
5. Charness skill routing should stay partial: adapter acknowledgement suppresses drift, but does not prove the exact default generated routing block.
6. Operator takeover was checked shallowly in both init-repo runs. Inspecting docs is enough for a partial read-only pass, but not full command-tier synthesis proof.
7. Charness `quality` coverage is credible but must be qualified. It considered broad axes; skipping the integrated `run-quality.sh --review` means it did not execute the exact canonical review gate end-to-end.
8. Ceal `quality` is not acceptable as a completed quality run because delegated review was missed rather than marked `executed`, `blocked`, or `not_applicable` with a concrete host signal.
9. Ceal `quality` overclaimed runtime-economics coverage if read as runtime health. With empty adapter `runtime_budgets`, the runtime budget command proves no configured enforcement.
10. Ceal `quality` covered many meaningful slices, but not the full meaningful gate surface end-to-end.

## Verdict

The skills are designed to look beyond gate scripts. The contracts require deterministic repo inventory, adapter inspection, operating-surface review, quality lenses, advisory inventories, and bounded subagent review for task-completing quality/normalization work.

The `codex exec` dogfood runs mostly exercised the deterministic inspection axes, but the runs did not uniformly exercise the delegated-review and durable-artifact axes:

- Charness `init-repo`: mostly covered for read-only inspection; incomplete for durable init-repo artifact proof and exact skill-routing surface.
- Ceal `init-repo`: covered enough to find real gaps; not complete until dedicated subagent delegation policy and stale init-repo artifact are fixed.
- Charness `quality`: broad axes were considered; outcome should say "considered/inventoried, some advisory or partial" rather than "fully enforced".
- Ceal `quality`: not complete because delegated review was missed; runtime and skill-ergonomics axes are partial.

## Recommended Next Moves

1. In Ceal, add a dedicated `## Subagent Delegation` section to `AGENTS.md` and explicitly authorize task-completing `init-repo` and `quality` bounded reviewers.
2. In Ceal, rerun/refresh `charness-artifacts/init-repo/latest.md` after the policy fix so the artifact no longer claims ok against stale inspection.
3. In Ceal quality, either add adapter-owned `runtime_budgets`/startup probes and skill paths, or make the artifact wording explicit that runtime economics and skill ergonomics are advisory/manual for now.
4. In Charness, decide whether `charness-artifacts/init-repo/latest.md` is an expected current pointer for this repo; either create/refresh it through the skill path or adjust the dogfood expectation for this repo shape.
5. Add a dry-run/read-only mode, or a safer output-dir exclusion, for public skill dogfood validation so review-only `codex exec -o` runs cannot delete their own evidence directory.
6. Future `codex exec` dogfood prompts should require a `Delegated Review: executed|blocked|not_applicable` line and forbid cleanup of the caller-provided output directory.

## Verification

- `codex exec` runs completed for all four repo/skill pairs.
- Two bounded fresh-eye subagents reviewed the recovered results.
- Final `git status --short` was clean in `/home/ubuntu/charness` and `/home/ubuntu/ceal` before this evaluation document was added.

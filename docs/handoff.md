# charness Handoff

## Workflow Trigger

- 다음 세션이 repo operating contract, prompt/skill surface, export sync, 또는 checked-in artifact policy를 건드리면 이 handoff부터 읽고 `impl`로 이어간다.
- 반복 실수 방지는 [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를 함께 읽는다.

## Current State

- startup에는 `charness:find-skills` 1회가 필수이고, durable capability inventory는 [charness-artifacts/find-skills/latest.md](../charness-artifacts/find-skills/latest.md)와 `latest.json`이 owning surface다.
- [AGENTS.md](../AGENTS.md)는 craken-style compact entry다. 매 세션 즉시 필요한 Start Here / Subagent Delegation / Phase Rules만 inline이고, 세부 운영 규칙은 [docs/conventions/](./conventions/)가 owner다. 관련 `cautilus` proof는 [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)와 `.cautilus/runs/20260428T000000000Z-eval-migration/`이 owner다.
- README-first thin bootstrap contract가 이제 public skill/reference/helper/adapters/control-plane까지 맞춰졌다. default surface는 더 이상 `INSTALL.md`/`UNINSTALL.md`를 전제하지 않고, repo-owned next step은 README Quick Start + `doctor --next-action` 류 surface가 owner다.
- README rewrite slice가 landing됐다. top-level [README.md](../README.md)는 value + Quick Start + operating model 중심으로 얇게 유지하고, command-by-command surface는 generated [docs/cli-reference.md](./cli-reference.md)로 분리한다. owner는 [scripts/render_cli_reference.py](../scripts/render_cli_reference.py), [.agents/command-docs.yaml](../.agents/command-docs.yaml), [tests/quality_gates/test_command_docs_gate.py](../tests/quality_gates/test_command_docs_gate.py)다.
- install/update bootstrap은 이제 [packaging/bootstrap-python.json](../packaging/bootstrap-python.json) + [packaging/bootstrap-requirements.txt](../packaging/bootstrap-requirements.txt)를 owner로 둔 repo-local Python runtime contract를 쓴다. [init.sh](../init.sh)와 [charness](../charness)는 global `jsonschema`/`packaging` 전제를 두지 않고 managed checkout 아래 runtime helper를 먼저 맞춘다.
- control plane의 supported install-ownership story에서 `brew`는 제거됐다. integration manifests, provenance/update helpers, locks, tests, plugin export, current cautilus proof까지 같은 계약으로 맞춰졌다.
- install/doctor는 이제 host install 상태와 repo onboarding 상태를 분리해서 본다. consumer repo에서 `charness doctor`를 돌리면 host action이 끝난 뒤에는 `repo_onboarding`으로 `init-repo` next step을 surface할 수 있고, `create-skill` / `init-repo`는 semantic skill change 전에 dogfood/scenario/proof carrier를 먼저 고르게 됐다.
- `premortem`과 `quality`/`handoff`의 fresh-eye loop는 subagent가 canonical이 아니라 mandatory다. bounded capability probe 뒤에도 spawn이 안 되면 same-agent fallback으로 대체하지 말고 concrete host signal을 남긴 채 stop한다.
- `init-repo` 기본 AGENTS guidance와 checked-in [AGENTS.md](../AGENTS.md) 모두 repo-mandated bounded fresh-eye subagent review를 "already delegated" 규칙으로 surface한다. second-message 대기를 금지하고, host spawn restriction을 explicit blocker로 남긴다.
- [`docs/handoff.md`](./handoff.md)는 rolling pointer다. gate 수치, transient pre-push timing, release 상태, dogfood evidence, 긴 history는 owning artifact로 보내고 여기에는 next action을 바꾸는 사실만 남긴다.
- artifact policy는 이제 `history-default, latest optional` 쪽으로 재분류 중이다. 기준 owner는 [docs/artifact-policy.md](./artifact-policy.md)와 [charness-artifacts/spec/artifact-history-default-reclassification.md](../charness-artifacts/spec/artifact-history-default-reclassification.md)다.
- checked-in plugin export가 걸린 source를 바꾸면 validator보다 먼저 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 sync한다.
- machine-local discovery output인 `.agents/charness-discovery/`는 checked-in surface가 아니다. support/integration dry-run은 `python3 scripts/sync_support.py --repo-root . --json`와 `python3 scripts/update_tools.py --repo-root . --json`로 확인하고, generated local stubs는 drift로 커밋하지 않는다.
- prompt-affecting surface는 [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml)의 `run_mode: auto|ask|adaptive`와 planner가 owning contract다. Current proof seam은 `cautilus.evaluation_input.v1` + `cautilus eval test/evaluate`다.
- Cautilus는 generic review/closeout/검증 trigger가 아니다. Prompt/instruction behavior regression, evaluator-backed behavior review, baseline compare, or operator reading test intent가 있을 때만 실행 proof 후보로 올리고, ordinary closeout은 checked proof artifact validation부터 닫는다.
- Quality closeout에서 `Weak`, `Missing`, `Advisory`, delegated-review status, active next gates를 최종 응답에서 숨기지 않는다. `prompt_asset_roots: []`는 canonical asset root 미선언일 뿐 inline prompt/content bulk inventory opt-out이 아니다.
- #78 quality lesson landed: quiet standing gates must keep failure output actionable, and public-spec source-guard pressure must surface as a rollup with top offenders/action categories rather than broad advisory background.
- quality/runtime 숫자와 current review posture는 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), release/version truth는 [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)와 `python3 skills/public/release/scripts/current_release.py --repo-root .`가 owner다.
- `narrative` intent-preserving rewrite widening은 `v0.5.0`으로 release됐다. 다음 dogfood는 다른 repo에서 이 release를 실제로 써 보고 issue 형태의 misses를 모으는 단계다.
- agent-facing CLI prep/execute 아티팩트 분리 결정 렌즈가 `create-cli` (primary) + `impl` (crossref)에 landing됐다 ([#48](https://github.com/corca-ai/charness/issues/48) scope a). Spec은 [charness-artifacts/spec/issue-48-prep-execute-lens.md](../charness-artifacts/spec/issue-48-prep-execute-lens.md). Probe Q1/Q2/Q3는 post-landing 관찰 대상이다.
- 크로스-레포 이슈 작성 hygiene (`why/what > how`)는 `narrative` reference로 landing됐다. high-leverage truth-surface rewrite와 adapter-missing stop rule도 함께 `narrative` 쪽에 들어갔다.
- AGENTS.md craken refactor가 landing됐다. [AGENTS.md](../AGENTS.md)는 37 lines, `CLAUDE.md -> AGENTS.md` symlink가 host alias이며, [.agents/surfaces.json](../.agents/surfaces.json)은 `CLAUDE.md`를 repo markdown + prompt-behavior surface로 본다. Spec/HITL owner는 [charness-artifacts/spec/agents-md-craken-refactor.md](../charness-artifacts/spec/agents-md-craken-refactor.md)와 [charness-artifacts/hitl/2026-04-25-agents-md-craken-refactor.md](../charness-artifacts/hitl/2026-04-25-agents-md-craken-refactor.md)다.
- clean temp clone first-move dogfood가 2026-04-26에 실행됐다. Cautilus runner와 direct `claude -p`/`codex exec`는 `quality`/`init-repo` 라우팅을 대체로 기대대로 잡았고, direct `codex exec quality`가 `./charness --version` state-cache write 실패를 찾아 `write_version_state()` non-fatal cache write fix로 닫았다. Cautilus eval migration은 [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md) proof로 landing됐고, README proof ledger의 current owner는 [docs/readme-proof.md](./readme-proof.md)와 [specs/readme-proof.spec.md](../specs/readme-proof.spec.md)다.
- tokei integration이 self-application까지 닫혔다. [integrations/tools/tokei.json](../integrations/tools/tokei.json)이 manifest이고, `check_test_production_ratio --engine tokei`는 SLOC 측정을 줄 수 있다. `quality`의 `inventory_sloc.py`는 `run-quality.sh`의 advisory phase로 wired돼서 매 quality run마다 [charness-artifacts/quality/sloc-inventory/latest.json](../charness-artifacts/quality/sloc-inventory/latest.json)을 갱신한다. `splitlines` engine도 `IGNORED_DIRS`에 `.artifacts`를 더해 honest해졌고 (ratio 0.63 vs tokei 0.58), `DEFAULT_MAX_RATIO=1.0`은 그대로 통과한다.
- charness가 ship한 manifest는 사용자 리포에서도 자동 노출된다. discovery 흐름 (`quality`/`narrative` `list_tool_recommendations`, `find-skills` `list_capabilities`)은 plugin-shipped manifest를 fallback으로 머지하고, 같은 `tool_id` 충돌 시 user 우선이다. 사용자 리포가 의존성을 명시하고 싶으면 [integrations/tools/dependencies.json](../integrations/tools/dependencies.json) (스키마는 같은 디렉토리)에 staging하면 추천 payload에 `staged: true|false`로 노출된다. seeding 헬퍼는 `python3 skills/public/init-repo/scripts/seed_dependencies.py --repo-root . --from-recommendations`이고, `charness install <tool> --execute --add-dependency`도 자동 staging한다. tests는 `CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS=1` autouse fixture로 fallback을 끈다.

## Next Session

1. README proof ledger를 `../cautilus/bin/cautilus claim discover` output과 연결한다. Discovery output은 `cautilus.claim_proof_plan.v1` 계획이지 verdict가 아니므로, stable acceptance criteria와 direct evidence ref를 별도로 확정한다.
2. `git status --short`를 먼저 본다.
3. read-only blocker는 no-write routing eval + workspace-write workflow proof로 분리한다. routing eval에서 `find-skills` artifact write를 요구하지 말고, 실제 artifact/state write는 별도 workspace-write dogfood로 증명한다.
4. README-specific Cautilus fixtures를 추가해 Quick Start `init-repo`, normal prompt routing, quality route claims를 current `cautilus eval test` proof와 연결한다.
5. README/help text를 다시 건드리면 먼저 `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md`로 command reference를 재생성하고, export surface가 걸리면 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`를 validator보다 먼저 끝낸다.
6. public skill, handoff, validator, 또는 other prompt surface를 건드리면 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)와 [docs/public-skill-dogfood.json](./public-skill-dogfood.json)을 읽고 `impl`로 이어간다.
7. tokei follow-ups: 다음 두 SKILL.md wiring은 모두 deferred다 — `quality` SKILL.md 본문에서 [inventory_sloc.py](../skills/public/quality/scripts/inventory_sloc.py)를 참조하는 한 줄, 그리고 `init-repo` SKILL.md 본문에서 [seed_dependencies.py](../skills/public/init-repo/scripts/seed_dependencies.py)를 참조하는 한 줄. `cautilus` refactor가 끝나고 [validate_cautilus_proof.py](../scripts/validate_cautilus_proof.py)/[plan_cautilus_proof.py](../scripts/plan_cautilus_proof.py)/[.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml)의 `eval_test_command` 명령 surface가 cautilus 0.12+로 정렬되면 한 슬라이스로 묶어 cautilus regression proof와 함께 commit한다.
8. 새 `inventory-sloc` quality phase는 ~96ms로 빠르지만 아직 runtime budget에 등록 안 됐다. 다음 슬로우-게이트 패스 때 다른 unbudgeted hot spot과 묶어 등록한다 ([charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)의 budget-sweep 함정 패턴).
9. quality phase write-policy를 adapter spec으로 끌어올린다. 현재 [scripts/run-quality.sh](../scripts/run-quality.sh)의 `inventory-sloc` 분기와 [.githooks/pre-push](../.githooks/pre-push)의 `env CHARNESS_QUALITY_READ_ONLY=1`은 이번 세션에서 dirty-after-push 문제를 잠시 막은 ad-hoc fix다. 진짜 layer는 [.agents/quality-adapter.yaml](../.agents/quality-adapter.yaml)이 phase list와 각 phase의 write-policy (`writes_git_tracked_artifact` 등)를 표면하고, charness-shipped runner가 adapter를 봐서 read-only/full mode를 분기하는 것이다. 사용자 리포가 자기 runner를 만들든 charness 가 ship한 generic gate runner를 invoke하든 동일 adapter 해석으로 같은 mode 분리가 된다. 이 슬라이스가 들어오면 `CHARNESS_QUALITY_READ_ONLY` env는 deprecate하고 i 가 정의하는 mode-전달 mechanism (CLI flag든 정식 env든)으로 흡수한다. 작업 범위: quality-adapter schema/validator 확장, [scripts/run-quality.sh](../scripts/run-quality.sh)가 adapter를 해석하도록 리팩터, [.githooks/pre-push](../.githooks/pre-push)가 새 mode-전달 surface로 호출, [skills/public/init-repo](../skills/public/init-repo) seeding이 새 필드를 알도록, preset 들에 default write-policy 채움. 표준 env 컨벤션 (`CHARNESS_GATE_MODE=read-only` 같은 generalization) 단계는 i 안에서 흡수되므로 별도 슬라이스로 두지 않는다.

## Discuss

- 이 [docs/handoff.md](./handoff.md)와 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)의 freshness validator를 현재 stale-claim check 너머 어디까지 확장할지는 아직 열려 있다.
- `cautilus` planner가 아직 `goal`을 사실상 `preserve`로만 둔다. named-anchor/reasoning-frame change를 언제 `improve` + compare path로 올릴지는 dogfood를 더 봐야 한다.
- README, CLI reference, operator docs 사이 overlap을 얼마나 더 줄일지는 아직 열려 있다. 지금은 top-level story vs generated command reference 분리까지 닫았고, consumer-repo dogfood에서 실제 탐색 마찰을 본 뒤 더 줄일지 결정한다.
- Cautilus claim discovery output을 checked artifact로 둘지, 아니면 Specdown report build 때 생성되는 transient proof-plan input으로 둘지는 아직 열려 있다.
- release artifact가 GitHub release creation/public verification state를 얼마나 자세히 닫아야 하는지는 helper contract 차원에서 한 번 더 볼 가치가 있다.
- `Discuss`는 unresolved decision만 남기고, metrics/history/closed proof는 owning artifact로 계속 밀어내는 방향을 유지한다.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)
- [charness-artifacts/spec/readme-proof-cautilus-eval-migration.md](../charness-artifacts/spec/readme-proof-cautilus-eval-migration.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [docs/public-skill-dogfood.json](./public-skill-dogfood.json)

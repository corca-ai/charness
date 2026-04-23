# charness Handoff

## Workflow Trigger

- 다음 세션이 repo operating contract, prompt/skill surface, export sync, 또는 checked-in artifact policy를 건드리면 이 handoff부터 읽고 `impl`로 이어간다.
- 반복 실수 방지는 [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를 함께 읽는다.

## Current State

- startup에는 `charness:find-skills` 1회가 필수이고, durable capability inventory는 [charness-artifacts/find-skills/latest.md](../charness-artifacts/find-skills/latest.md)와 `latest.json`이 owning surface다.
- `init-repo`의 checked-in `Skill Routing` 계약은 이제 compact-only다. [AGENTS.md](../AGENTS.md)에는 긴 스킬 카탈로그를 복사하지 않고 startup `find-skills` bootstrap만 남긴다. 관련 `cautilus` proof는 [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)와 `.cautilus/runs/20260422T131049094Z-run/`이 owner다.
- README-first thin bootstrap contract가 이제 public skill/reference/helper/adapters/control-plane까지 맞춰졌다. default surface는 더 이상 `INSTALL.md`/`UNINSTALL.md`를 전제하지 않고, repo-owned next step은 README Quick Start + `doctor --next-action` 류 surface가 owner다.
- install/update bootstrap은 이제 [packaging/bootstrap-python.json](../packaging/bootstrap-python.json) + [packaging/bootstrap-requirements.txt](../packaging/bootstrap-requirements.txt)를 owner로 둔 repo-local Python runtime contract를 쓴다. [init.sh](../init.sh)와 [charness](../charness)는 global `jsonschema`/`packaging` 전제를 두지 않고 managed checkout 아래 runtime helper를 먼저 맞춘다.
- control plane의 supported install-ownership story에서 `brew`는 제거됐다. integration manifests, provenance/update helpers, locks, tests, plugin export, current cautilus proof까지 같은 계약으로 맞춰졌다.
- install/doctor는 이제 host install 상태와 repo onboarding 상태를 분리해서 본다. consumer repo에서 `charness doctor`를 돌리면 host action이 끝난 뒤에는 `repo_onboarding`으로 `init-repo` next step을 surface할 수 있고, `create-skill` / `init-repo`는 semantic skill change 전에 dogfood/scenario/proof carrier를 먼저 고르게 됐다.
- `premortem`과 `quality`/`handoff`의 fresh-eye loop는 subagent가 canonical이 아니라 mandatory다. bounded capability probe 뒤에도 spawn이 안 되면 same-agent fallback으로 대체하지 말고 concrete host signal을 남긴 채 stop한다.
- `init-repo` 기본 AGENTS guidance와 checked-in [AGENTS.md](../AGENTS.md) 모두 이제 repo-mandated bounded fresh-eye subagent review를 "already delegated" 규칙으로 surface한다. second-message 대기를 금지하고, host spawn restriction을 explicit blocker로 남긴다.
- [`docs/handoff.md`](./handoff.md)는 rolling pointer다. gate 수치, release 상태, dogfood evidence, 긴 history는 owning artifact로 보내고 여기에는 next action을 바꾸는 사실만 남긴다.
- artifact policy는 이제 `history-default, latest optional` 쪽으로 재분류 중이다. 기준 owner는 [docs/artifact-policy.md](./artifact-policy.md)와 [charness-artifacts/spec/artifact-history-default-reclassification.md](../charness-artifacts/spec/artifact-history-default-reclassification.md)다.
- checked-in plugin export가 걸린 source를 바꾸면 validator보다 먼저 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 sync한다.
- prompt-affecting surface는 [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml)의 `run_mode: auto|ask|adaptive`와 planner가 owning contract다. `adaptive`는 기본 자동 proof + short scenario review 쪽이고, explicit ask는 maintained scenario registry mutation 같은 더 비싼 follow-up에 남긴다. visible proof owner는 [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)다.
- quality/runtime 숫자와 current review posture는 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), release/version truth는 [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)와 `python3 skills/public/release/scripts/current_release.py --repo-root .`가 owner다.
- `narrative` intent-preserving rewrite widening은 `v0.5.0`으로 release됐다. 다음 dogfood는 다른 repo에서 이 release를 실제로 써 보고 issue 형태의 misses를 모으는 단계다.
- agent-facing CLI prep/execute 아티팩트 분리 결정 렌즈가 `create-cli` (primary) + `impl` (crossref)에 landing됐다 ([#48](https://github.com/corca-ai/charness/issues/48) scope a). Spec은 [charness-artifacts/spec/issue-48-prep-execute-lens.md](../charness-artifacts/spec/issue-48-prep-execute-lens.md). Probe Q1/Q2/Q3는 post-landing 관찰 대상이다.
- 크로스-레포 이슈 작성 hygiene (`why/what > how`)는 `narrative` reference로 landing됐다. high-leverage truth-surface rewrite와 adapter-missing stop rule도 함께 `narrative` 쪽에 들어갔다.

## Next Session

1. `git status --short`를 먼저 본다.
2. 다른 repo dogfood를 바로 한다면 `python3 scripts/plan_cautilus_proof.py --repo-root . --json`보다 먼저 clean temp workspace에서 실제 consumer repo를 열고, 설명 없이 `quality` 또는 `init-repo`만 불렀을 때 README-first/bootstrap-less default와 delegated bounded-subagent rule이 기대대로 surface되는지 본다.
3. prompt-affecting slice를 이어받으면 `python3 scripts/plan_cautilus_proof.py --repo-root . --json`로 proof 종류와 `next_action`을 먼저 본다. `adaptive`에서는 scenario review 자체보다 [evals/cautilus/scenarios.json](../evals/cautilus/scenarios.json) mutation이 필요한지 여부를 따로 본다.
4. 다른 repo dogfood 결과가 생겼으면 vague 회고로 흘리지 말고 eval candidate 또는 issue로 바로 정규화한다.
5. public skill, handoff, validator, 또는 other prompt surface를 건드리면 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)와 [docs/public-skill-dogfood.json](./public-skill-dogfood.json)을 읽고 `impl`로 이어간다.
6. export surface가 걸린 변경이면 sync를 먼저 끝내고 그 다음 validator와 quality gate를 돌린다.
7. rolling pointer freshness를 더 조일 다음 slice면 prose를 더 추가하지 말고 deterministic validator를 우선 검토한다.
8. derived memory / smoothing 작업을 이어받으면 [charness-artifacts/spec/derived-memory-smoothing.md](../charness-artifacts/spec/derived-memory-smoothing.md)를 먼저 읽고, quality EWMA, [debug seam-risk index](../charness-artifacts/debug/seam-risk-index.json), [retro lesson selection index](../charness-artifacts/retro/lesson-selection-index.json)는 source-linked/advisory로 유지한다. [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) 자동 재작성은 별도 digest policy가 먼저다.
9. release를 이어받으면 `current_release.py`로 checked-in surface를 먼저 읽고, actual publish는 `publish_release.py` helper 경로를 쓴다.

## Discuss

- 이 [docs/handoff.md](./handoff.md)와 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)의 freshness validator를 현재 stale-claim check 너머 어디까지 확장할지는 아직 열려 있다.
- `cautilus` planner가 아직 `goal`을 사실상 `preserve`로만 둔다. named-anchor/reasoning-frame change를 언제 `improve` + compare path로 올릴지는 dogfood를 더 봐야 한다.
- release artifact가 GitHub release creation/public verification state를 얼마나 자세히 닫아야 하는지는 helper contract 차원에서 한 번 더 볼 가치가 있다.
- `Discuss`는 unresolved decision만 남기고, metrics/history/closed proof는 owning artifact로 계속 밀어내는 방향을 유지한다.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [docs/public-skill-dogfood.json](./public-skill-dogfood.json)

# charness Handoff

## Workflow Trigger

- 다음 세션이 repo operating contract, prompt/skill surface, export sync, 또는 checked-in artifact policy를 건드리면 이 handoff부터 읽고 `impl`로 이어간다.
- 반복 실수 방지는 [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를 함께 읽는다.

## Current State

- startup에는 `charness:find-skills` 1회가 필수이고, durable capability inventory는 [charness-artifacts/find-skills/latest.md](../charness-artifacts/find-skills/latest.md)와 `latest.json`이 owning surface다.
- `premortem`과 `quality`/`handoff`의 fresh-eye loop는 subagent가 canonical이 아니라 mandatory다. bounded capability probe 뒤에도 spawn이 안 되면 same-agent fallback으로 대체하지 말고 concrete host signal을 남긴 채 stop한다.
- [`docs/handoff.md`](./handoff.md)는 rolling pointer다. gate 수치, release 상태, dogfood evidence, 긴 history는 owning artifact로 보내고 여기에는 next action을 바꾸는 사실만 남긴다.
- checked-in plugin export가 걸린 source를 바꾸면 validator보다 먼저 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 sync한다.
- prompt-affecting surface를 바꾸면 `cautilus instruction-surface test --repo-root .`로 preserve proof를 다시 보고, visible proof owner는 [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)다.
- quality/runtime 숫자와 current review posture는 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), release/version truth는 [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)와 `python3 skills/public/release/scripts/current_release.py --repo-root .`가 owner다.
- agent-facing CLI prep/execute 아티팩트 분리 결정 렌즈가 `create-cli` (primary) + `impl` (crossref)에 landing됐다 ([#48](https://github.com/corca-ai/charness/issues/48) scope a). Spec은 [charness-artifacts/spec/issue-48-prep-execute-lens.md](../charness-artifacts/spec/issue-48-prep-execute-lens.md). Probe Q1/Q2/Q3는 post-landing 관찰 대상이다.
- 크로스-레포 이슈 작성 hygiene (`why/what > how`)의 홈 결정은 [#49](https://github.com/corca-ai/charness/issues/49)로 분리되어 probe 대기 중이다. 후보는 `narrative` / `handoff` / `announcement` / 신규 reference이며, 홈 확정 전 구현 텍스트 작성 금지다.

## Next Session

1. `git status --short`를 먼저 본다.
2. [#49](https://github.com/corca-ai/charness/issues/49) pickup이면 후보 4개 스킬의 SKILL.md를 먼저 읽어 홈 fit을 비교한 뒤 `spec`으로 진입한다. 홈 확정 전 가이드 텍스트를 쓰지 않는다.
3. public skill, handoff, validator, 또는 other prompt surface를 건드리면 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)와 [docs/public-skill-dogfood.json](./public-skill-dogfood.json)을 읽고 `impl`로 이어간다.
4. export surface가 걸린 변경이면 sync를 먼저 끝내고 그 다음 validator와 quality gate를 돌린다.
5. rolling pointer freshness를 더 조일 다음 slice면 prose를 더 추가하지 말고 deterministic validator를 우선 검토한다.
6. release를 이어받으면 `current_release.py`로 checked-in surface를 먼저 읽고, actual publish는 `publish_release.py` helper 경로를 쓴다.

## Discuss

- 이 [docs/handoff.md](./handoff.md)와 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)의 freshness를 어느 수준까지 deterministic validator로 올릴지 아직 열려 있다.
- `Discuss`는 unresolved decision만 남기고, metrics/history/closed proof는 owning artifact로 계속 밀어내는 방향을 유지한다.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [docs/public-skill-dogfood.json](./public-skill-dogfood.json)

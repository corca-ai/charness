[English README](./README.md)

# charness

`charness`는 저장소 소유 에이전트 작업을 위한 휴대 가능한 Corca 하니스 레이어입니다.

이 프로젝트는 퍼블릭 워크플로 스킬, 서포트 스킬, 프로파일, 프리셋,
통합 매니페스트, 저장소 소유 검증 흐름을 하나의 일관된 하니스 표면으로
묶어 줍니다. 그래서 호스트는 각 프롬프트 표면마다 운영 관습을 다시 만들
필요 없이, 하나의 공통 표면을 채택할 수 있습니다.

저장소에 개념 정리, 구현, 검토, 핸드오프, 릴리스 같은 반복적인 에이전트
작업이 있고, 그 워크플로를 Claude Code, Codex, 또는 인접한 호스트
표면들 사이에서 휴대 가능하게 유지하고 싶다면 `charness`가 맞습니다.

일반적인 작업 세션은 이제 capability map에서 시작합니다.
먼저 `charness:find-skills`를 실행하고, 그 다음 현재 작업에 맞는 퍼블릭
스킬이나 지원 capability를 고릅니다.

## 대상 사용자

- Claude Code, Codex, 또는 인접한 호스트 표면 전반에서 저장소 소유
  에이전트 워크플로 또는 스킬 팩을 유지보수하는 팀
- 호스트별 프롬프트 번들 대신 휴대 가능한 워크플로 개념을 원하는
  메인테이너
- 외부 도구의 런타임 소유자까지 되지 않으면서 install, update, doctor,
  support-sync 경계를 원하는 운영자

## 빠른 시작

에이전트에게 `charness` 설치를 맡길 때는 설치 절차를 말로 풀지 말고,
설치 계약 문서를 직접 넘기는 편이 맞습니다.

```md
Read and follow: https://raw.githubusercontent.com/corca-ai/charness/main/INSTALL.md

Install charness on this machine.
Then verify the setup with `charness init` and `charness doctor`.
This repo should work in Claude Code and Codex.
After installation, use `charness update` for refreshes.
```

설치 후 운영자 기준의 기본 경로는 짧습니다.

- `charness init`: managed local install surface를 부트스트랩하거나 새로 고침
- `charness doctor`: 현재 호스트 상태를 검사하고 `next_action` 확인
- `charness update`: 나중에 설치된 `charness` 표면 새로 고침
- `charness update all`: 추적 중인 외부 도구와 번들 서포트 스킬까지 함께 새로 고침

[INSTALL.md](./INSTALL.md)가 여전히 정식 설치 계약입니다.
README는 진입면이지, 전체 운영 매뉴얼은 아닙니다.

## 스킬 맵

퍼블릭 스킬은 사용자에게 직접 드러나는 워크플로 개념입니다.
서포트 스킬과 통합은 특수 도구를 어떻게 사용할지 하니스에 가르치되,
그 도구 자체를 제품 철학으로 만들지 않습니다.

### 퍼블릭 스킬

`init-repo`는 저장소의 초기 운영 표면을 만들거나 정규화해야 할 때 쓰는
특수 진입점입니다. 단순히 구현 단계 중 하나가 아닙니다.

나머지 퍼블릭 표면은 의도 기준으로 이렇게 묶입니다.

- 일을 구체화하기: `ideation`, `spec`, `gather`
- 만들고 고치기: `impl`, `debug`, `premortem`
- 품질 높이기: `quality`, `retro`
- 경계를 넘는 소통:
  `announcement` 사람 -> 조직,
  `narrative` 사람 -> 사람,
  `handoff` 에이전트 -> 에이전트,
  `hitl` 에이전트 -> 사람
- 하니스 운영하기: `find-skills`, `create-skill`, `create-cli`, `release`

`gather`는 매번 독립된 단계라기보다 `ideation`, `spec`, `impl` 안에서
필요할 때 끼어드는 지원 동작인 경우가 많습니다.

### 서포트 스킬과 통합

서포트 스킬은 여러 워크플로가 공유하는 비공개 tool-use 지식입니다.
특수 도구를 일관되게 쓰도록 하니스를 돕습니다.

현재 로컬 서포트 예시는 다음과 같습니다.

- `web-fetch`
- `gather-slack`
- `gather-notion`

통합은 install, update, detect, healthcheck, readiness, sync 동작에 대한
외부 소유 경계를 설명합니다.

현재 통합 예시는 다음과 같습니다.

- `agent-browser`
- `specdown`
- `cautilus`
- `gws-cli`

README에서 `cautilus`는 여기 소개되는 편이 맞습니다.
즉 퍼블릭 워크플로 개념이 아니라, `charness`가 연동할 수 있는
upstream-owned support binary / skill surface로 다뤄야 합니다.

프로파일과 프리셋도 이 스킬 표면 곁에 놓이는 기본 번들과
호스트/저장소별 설정 경계이지, 사용자에게 직접 드러나는 워크플로 개념은
아닙니다.

## 예시 흐름

### 새 저장소 또는 아직 얇은 운영 표면

저장소의 기본 모양부터 잡아야 할 때 흔한 경로입니다.

1. `ideation`으로 시작하고, 외부 맥락이 개념을 더 날카롭게 만들 때만
   `gather`를 끼웁니다.
2. 개념이 충분히 구체화되면, 적절한 저장소를 만들거나 그 저장소로
   들어가서 `init-repo`를 실행합니다.
3. `init-repo`가 [AGENTS.md](./AGENTS.md)나 운영 표면을 크게 바꿨다면,
   이어서 작업하기 전에 새 세션을 여는 편이 좋습니다.
4. `spec`으로 현재 실행 가능한 계약을 잡습니다.
5. 첫 실제 슬라이스는 `impl`로 옮깁니다.
6. 버그에는 `debug`, 사전 실패 검토에는 `premortem`, 다음 문제가
   단순 구현이 아니라 품질 향상이라면 `quality` / `retro`를 끌어옵니다.

### 기존 저장소에서 "이거 구현해줘"

이미 운영 표면이 갖춰진 저장소에서 사용자가 그냥 구현을 요청할 때 흔한
경로입니다.

1. 세션이 현재 capability map으로 시작되도록 `find-skills`부터 실행합니다.
2. 작업이 이미 충분히 구체적이면 바로 `impl`로 갑니다.
3. 계약 자체를 먼저 잡아야 할 때만 `spec`을 끼웁니다.
4. 작업이 원인 추적으로 바뀌면 `debug`를 사용합니다.
5. 비자명한 변경에 사전 실패 검토가 필요하면 `premortem`을 사용합니다.
6. `quality`와 `retro`는 사람과 에이전트의 품질을 높이는 별도 루프로
   보고, 단순 구현 뒤 정리 단계로만 취급하지 않습니다.
7. 슬라이스에 따라 소통/메타 스킬도 자연스럽게 끼워 넣습니다:
   `narrative`, `announcement`, `handoff`, `hitl`, `release`,
   `create-skill`, `create-cli`

## 경계

각 표면의 소유권은 분명하게 유지합니다.

- README는 첫 진입 오리엔테이션 표면
- [INSTALL.md](./INSTALL.md), [UNINSTALL.md](./UNINSTALL.md),
  [docs/host-packaging.md](./docs/host-packaging.md)는 설치 및 패키징 진실 소유
- [docs/operator-acceptance.md](./docs/operator-acceptance.md)는
  운영자 인수인계 체크리스트 소유
- [docs/control-plane.md](./docs/control-plane.md)와 통합 매니페스트는
  외부 도구 계약 소유
- [docs/support-skill-policy.md](./docs/support-skill-policy.md)는
  public skill / support skill / integration 경계 설명
- [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)는
  현재 dogfood 품질 뷰이며 README 대체물이 아님

`charness`는 하나의 managed bundle로 설치됩니다.
부분 설치된 퍼블릭 스킬 메뉴처럼 다루면 안 되며, 스킬 실행 자체도
install/update 상태를 직접 바꾸지 않는 read-only 성격을 유지해야 합니다.

체크인된 설치 표면은 여전히 `plugins/charness/` 아래에 있고,
[packaging/charness.json](./packaging/charness.json)에서
`python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 생성됩니다.

## 다음에 읽을 문서

- managed host surface 설치/새로 고침:
  [INSTALL.md](./INSTALL.md), [docs/host-packaging.md](./docs/host-packaging.md)
- public/support 경계 판단:
  [docs/support-skill-policy.md](./docs/support-skill-policy.md),
  [docs/public-skill-validation.md](./docs/public-skill-validation.md)
- 현재 rollout / takeover 상태:
  [docs/operator-acceptance.md](./docs/operator-acceptance.md),
  [docs/handoff.md](./docs/handoff.md)
- 현재 품질 상태:
  [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)
- 이 저장소 자체를 작업할 때:
  [docs/development.md](./docs/development.md)

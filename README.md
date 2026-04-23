# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://www.corca.ai/).

Most agent frameworks get noisier as repositories grow. `charness` goes the
other way: it keeps the public workflow surface small, pushes repo-specific
rules into adapters and checks, and keeps install, update, and discovery
legible to both humans and agents.

`charness` combines public workflow skills, repo-local adapters, support
integrations, and a managed install/update path into one system for teams that
want agents to do more real work without turning every repository into a
one-off prompt maze.

// 2번째, 3번째 문단의 역할이 약간 중복되는 느낌. 후자를 없애거나 바꾼다면?

## Quick Start

// (pre-requisite로 python 설치해야 한다고 표시)

Install `charness` binary:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
~/.local/bin/charness doctor --next-action
``` // PATH 자동 입력 안되나? 

<코멘트>
내 의도는 '설치 후에는 에이전트에게 이렇게 말해라'지, '인스톨을 에이전트에게 시켜라'는 아니었음. 임의의 링크에 존재하는 외부 파일을 읽게 하는 걸 싫어하는 거니까 md나 sh나 마찬가지로 막힐 염려가 있음.
예를 들면 이런 느낌.

```md
Run `charness doctor --next-action` and follow the instruction.
```

그런데 생각해보니 다른 바이너리와 달리 charness는 init 이 전부 아닌가? 다음 액션 할 게 있긴 한가? 아 init-repo를 시키는 게 필요하긴 한데...

'init-repo 후에는 agents.md 를 통해, 당신의 프롬프팅 패턴대로 쓰면 charness 스킬이 알아서 발동된다' 같은 말을 넣고 싶음.
</코멘트>

Once the binary is available, these are the main commands users and agents will
keep seeing: // 여기부터는 가치 있음. 단, '설치하면 새 세션부터 클로드 코드와 코덱스에서 쓸 수 있다' 도 포함하고 싶음

- `charness init` to bootstrap or refresh the managed local install surface // 이거 이미 charness-init.sh 가 부트스트랩 한 거 아닌가? 그러면 리프레시만 남겨야 하지 않나? 
- `charness doctor` to inspect current host state and read `next_action`
- `charness update` to refresh the installed surface later
- `charness update all` when you also want tracked external tools and bundled
  support skills refreshed in the same pass
- `charness reset` when you need to remove host plugin state while keeping the
  managed checkout and CLI
- `charness uninstall` when you want the host-facing uninstall path while
  preserving the source checkout and CLI unless explicit delete flags are passed

// help 도 있고 다른 명령어도 있는데 왜 얘기 안했지? 대표만 얘기하고, help 써라 + 나머지는 CLI 레퍼런스 문서로 뺀다면 이해가 가지만 지금은 아님.

## Core Concepts

These are the core concepts `charness` uses to tackle common problems plugin
developers run into.

// 모든 스킬은 링크가 SKILL.md로 걸려야 함. 스킬별 자세한 내용은 아래 [Skill Map](링크) 참고하라고 하기.

### 1. Less Is More

// 지금 살짝 핀트가 다른 느낌. 두 가지 철학임.
// 에이전트는 이미 충분히 똑똑하다. How를 자세히 쓸 필요 없다. 어떤 문서가 왜 존재하는지 기술하기만 하면 알아서, 점진적으로 잘 찾아갈 것이다. (progressive disclosure 단어 언급해야 함) 
// 모드와 옵션은 게으른 디자인의 산물이다. 강한 디폴트를 두고, 내가 옳다고 믿는 선택을 밀어붙인다.

If you assume the agent is weak, the system grows extra modes, options,
explanations, and ceremony until users have to learn the framework before they
can use it. `charness` assumes a smart agent, prefers strong defaults and a
small public interface, and moves deeper rules into adapters, helpers, and
repo-owned checks only when they are actually needed.

Connected areas: `find-skills`, `init-repo`, `quality`, `create-skill`. // 각 섹션에서 이 문장은 이렇게 뗀다.

### 2. Human-Code-AI Symbiosis

// 첫 문장은 "인간, 코드, AI가 잘 하는 일이 다르다." 로 간단히 쓴다. 

Automation gets brittle when people, deterministic checks, and AI all try to
do the same job badly instead of each doing what they are best at. Humans keep
judgment, authority, physical action, and external-machine control. Code keeps
the deterministic gates. AI handles exploration, drafting, implementation, and
synthesis. Connected areas: `impl`, `quality`, `hitl`, validators, hooks.

### 3. Shared Logic, Local Growth // 요거 좀 더 강하게 써야 하나 싶은데... '로컬 그로스' 단어가 약한 느낌. 그냥 위치는 여기로 두되, 9랑 합치는 게 나을것 같음. 9를 더 강조해서(제목도 9로). 고정된 스냅샷이 아니라 어댑티브해야 하며, 계속 자라나야 한다.

A skill written directly from one team's habits often works in one repository
and feels wrong everywhere else. `charness` keeps shared workflow concepts
public, then lets each repository define its own docs, rules, checks, and
operating patterns through adapters. Connected areas: public skills, adapters,
`create-skill`, `narrative`.

### 4. Agents Are First-Class Users // 제목은 의도대로인데 내용은 핀트가 좀 다름. 우리가 만드는 도구는 모두 에이전트가 (이제는 인간보다도 더 자주) 사용할 것을 고려해야 한다. CLI와 스크립트를 쥐어주고, 바이너리/스크립트 호출 결과가 그 도구들이 다음 할 일을 안내해주고. 바이너리를 조합형으로 만들고, 그 사용법을 스킬로 안내해주고 등.

If install, update, and health checks only make sense to a human operator,
agents end up guessing local state and repeating recovery work every session.
`charness` ships as both plugin and CLI so the same path can install it,
verify readiness, update it later, and tell both people and agents what to do
next. Connected areas: install / update / doctor flows, `release`,
`find-skills`.

### 5. Concepts First, Tools Second // 내용은 의도가 맞는데 왜 잘 강조가 안 된 느낌이지? 서포트 스킬 예시가 없어서 그런가? '인간/에이전트가 알아야 할 스킬'과, '스킬을 사용하기 위해 사용하는 스킬'(agent-browser, markdown-preview, specdown, cautilus 등 검증 도구, web-fetch 같은 보조 도구 등)을 구분한다. 후자는 사람이/에이전트가 직접 알 필요가 없다.. 이런 느낌.

When public skills mix user-facing workflow ideas with tool-specific
instructions, every tool change becomes a workflow rewrite. `charness` keeps
workflow concepts in public skills and pushes tool-specific know-how into
support skills and integrations. Connected areas: `gather`, support skills,
integrations.

### 6. Quality Makes Autonomy Trustworthy // 더 강조 필요. 코드 품질이 AI 시대에도 중요한 이유에 대해 언급해야 함. 프리트레이닝된 데이터에서 더 좋은 데이터를 가져오기 때문이고, 에이전트가 좋은 길로 갈 수 있게 도와주는 게 있음. 이게 무엇들을 체크하는지 좀 더 구체적으로 얘기해도 좋을듯.

As repositories get larger and agents work longer, weak code, tests, design,
docs, skills, or binaries become the first place trust breaks down.
`charness` treats quality as a system-wide trust problem, not just a code-style
problem. Connected areas: `init-repo`, `quality`, `debug`, `premortem`.

### 7. Communication Depends On Who Speaks To Whom // 제품이 가치를 가지려면 에이전트-개발자-조직이 사이에 정보가 흘러야 한다. 그런데 누가 누구에게 말하냐에 따라 무엇을 어떻게 말하느냐가 달라진다. 요런 느낌으로. 제목도 바꿔야 할지도?

Work only stays alive when it can move between people and agents, but the
right format changes depending on who is talking to whom. `charness` treats
communication as part of the system and separates announcement, narrative,
handoff, and HITL review accordingly. Connected areas: `announcement`,
`narrative`, `handoff`, `hitl`.

### 8. Expert Tacit Knowledge Becomes Workflow // 전문가의 이름을 직접 언급함으로써 에이전트를 좋은 공간으로 끌고갈 수 있음을 강조.

Great debugging and review often live inside a few experts' heads, so teams
keep relearning the same patterns by trial and error. `charness` turns that
tacit knowledge into reusable workflow patterns, sometimes with sparse anchors
that recall the right move faster than extra prose. Connected areas: `debug`,
`quality`, `narrative`, `find-skills`, adjacent skills.

### 9. The System Should Get Smarter With Use // Auto-retro 더 설명 필요. retro가 retrospective라는 것도 일반 사용자 모를 것.

Repeated mistakes and good decisions are wasted if they disappear when the
session ends. `charness` keeps lessons alive through retro, auto-retro,
adapters, validators, and durable artifacts so both people and agents can
improve the system while using it. Connected areas: `retro`, `quality`,
`handoff`.

## Skill Map

The concepts above show up in the skill map below.

Public skills are user-facing workflow concepts. Support skills and
integrations teach the harness how to use specialized tools without turning
those tools into the product's philosophy.

### Public Skills

`init-repo` is a special entrypoint for repos that still need their initial
operating surface created or normalized. It is not just another implementation
step.

For the rest of the surface, the public skills group by intent:

- shape the work: `gather`, `ideation`, `spec`
- build and repair: `impl`, `debug`, `premortem`
- raise quality: `quality`, `retro`
- communicate across boundaries:
  `announcement` person -> organization,
  `narrative` person -> person,
  `handoff` agent -> agent,
  `hitl` agent -> person
- operate the harness: `find-skills`, `create-skill`, `create-cli`, `release`

`gather` is often a supporting move inside `ideation`, `spec`, or `impl`, not
necessarily a standalone stage in every workflow.

### Support Skills And Integrations // markdown-preview 빠졌는데? 왜 빠졌지? 또 빠진 거 없나?

Support skills are non-public tool-use knowledge shared by multiple workflows.
They teach the harness how to use specialized tools consistently. // 다른 스킬을 더 잘 쓸 수 있게 보조해주는 스킬이다. 퍼블릭 스킬 surface에 드러나지 않는다. 강조

Current local support examples include: // 왜 'examples'지? 실제로 설치 같이 되고 쓰는 거 아닌가?

- `web-fetch`
- `gather-slack`
- `gather-notion`

Integrations describe external ownership boundaries for install, update,
detect, healthcheck, readiness, and sync behavior.

Current integration examples include:

- `agent-browser`
- `specdown`
- `cautilus`
- `gws-cli`

This is where `cautilus` belongs in the README: as an upstream integration
boundary and evaluator-facing support tool, not as a public workflow concept. // 코틸러스가 왜 강조되는 거지? 그럴 필요 없음. 다른 것과 동일함.

Profiles and presets stay alongside this skill surface as default bundles and
host/repo-specific configuration seams rather than user-facing workflow
concepts. // 이 얘기 뭔지 잘 모르겠음.

## Example Flows // 요거 퀵스타트 다음에 올려야 확 와닿지 않을까? 압도 안 되게. 어떻게 쓰면 된다. 아니면 아예 퀵스타트 섹션 안에 넣던가. 그리고 나는 오토 라우팅을 원함. 웬만하면 유저가 쓰던 대로만 쓰면 알아서 스킬이 발동되어야 함(URL이 보이면 gather 한다 등). 지금은 스킬명이 너무 강조되어 있어서 그걸 유저가 불러야 하는 것처럼 보임. 뉴 리포 / existing repo 는 내 의도대로임. 어쨌든 init-repo 이후에는 계속 쓰던대로 쓰면 된다. find-skills 에 대한 안내가 agents.md 에 필수로 들어갈 거고, 이후는 알아서 작동하는 것. find-skills 를 유저가 직접 쓸 필요는 전혀 없음. 이렇게 되면 훨씬 짧게 쓸 수 있을 것 같은데.

### New Repo Or Thin Operating Surface

This is the common path when the repo shape still needs to be established.

1. Start with `ideation` and let `gather` pull in outside context only when it
   sharpens the concept.
2. Once the concept is concrete enough, create or move into the right repo and
   run `init-repo`.
3. If `init-repo` changes [AGENTS.md](./AGENTS.md) or the operating surface materially,
   prefer starting a fresh session before continuing.
4. Use `spec` to turn the direction into the current executable contract.
5. Move into `impl` for the first real slice.
6. Bring in `debug` for bugs, `premortem` for before-the-fact review, and
   `quality` / `retro` when the next problem is quality improvement rather than
   raw implementation.

### Existing Repo, "Implement This"

This is the common path when the repo already has an operating surface and the
user simply wants work done.

1. Start with `find-skills` once so the current capability inventory is explicit, then route to the durable work skill from repo context, [AGENTS.md](./AGENTS.md), and installed skill metadata.
2. Go straight to `impl` when the task is already concrete enough.
3. Pull in `spec` only when the contract still needs to be shaped.
4. Use `debug` when the slice turns into root-cause work.
5. Use `premortem` when a non-trivial change needs a before-the-fact failure
   review.
6. Treat `quality` and `retro` as separate quality-raising loops for people
   and agents, not only as post-implementation cleanup.
7. Fold in communication or meta skills when the slice needs them:
   `narrative`, `announcement`, `handoff`, `hitl`, `release`,
   `create-skill`, or `create-cli`.

## Boundaries // 이거랑 다음 섹션은 그냥 합쳐서 '더 알아보기' 같은 느낌으로.

Keep the surface ownership clear:

- the README is the first-touch orientation surface
- [docs/host-packaging.md](./docs/host-packaging.md) owns packaging truth and
  the generated host-layout contract
- [docs/operator-acceptance.md](./docs/operator-acceptance.md) owns the
  operator-facing takeover checklist
- [docs/control-plane.md](./docs/control-plane.md) and integration manifests
  own external tool contracts
- [docs/support-skill-policy.md](./docs/support-skill-policy.md) explains the
  public-skill vs support-skill vs integration boundary
- [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)
  is the current dogfood quality view, not a replacement for the README

`charness` installs as one managed bundle. It should not be treated as a menu
of partially installed public skills, and skill execution itself should stay
read-only with respect to install/update state.

The checked-in install surface still lives under `plugins/charness/` and is
generated from [packaging/charness.json](./packaging/charness.json) via
`python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

## Read This Next

- install or refresh the managed host surface:
  the Quick Start above and [docs/host-packaging.md](./docs/host-packaging.md)
- pick the right public/support boundary:
  [docs/support-skill-policy.md](./docs/support-skill-policy.md) and
  [docs/public-skill-validation.md](./docs/public-skill-validation.md)
- understand current rollout and takeover state:
  [docs/operator-acceptance.md](./docs/operator-acceptance.md) and
  [docs/handoff.md](./docs/handoff.md)
- inspect current quality posture:
  [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)
- work on this repo itself:
  [docs/development.md](./docs/development.md)

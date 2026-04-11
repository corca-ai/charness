# charness Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `impl`로 이어서, 먼저 [skills/public/init-repo/SKILL.md](/home/ubuntu/charness/skills/public/init-repo/SKILL.md), [docs/public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md), [INSTALL.md](/home/ubuntu/charness/INSTALL.md), [UNINSTALL.md](/home/ubuntu/charness/UNINSTALL.md), [README.md](/home/ubuntu/charness/README.md), [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md), [docs/operator-acceptance.md](/home/ubuntu/charness/docs/operator-acceptance.md), [plugins/charness/.codex-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.codex-plugin/plugin.json), [.agents/plugins/marketplace.json](/home/ubuntu/charness/.agents/plugins/marketplace.json)을 읽고 `init-repo` dogfood/eval 필요성과 남은 Codex install proof를 같이 본다.
- 이 머신에서는 `~/.agents/skills` source-checkout symlink가 이미 제거돼 있으니, 다시 생기지 않았는지만 짧게 확인한다.
- Claude local proof는 끝났다. 실제 local path는 `--plugin-dir /absolute/path/to/charness/plugins/charness`이고, parent `plugins/`를 주면 skill discovery proof가 되지 않는다.
- Codex는 repo-scoped marketplace와 machine-local `~/.agents/plugins/marketplace.json` 둘 다 `exec` 경로로는 install/discovery proof가 약하니, interactive session 또는 다른 머신에서 실제 install/discovery proof를 이어서 본다.

## Current State

- `charness`는 portable Corca harness product로 정리됐고, public/support/profile/integration 경계는 현재 taxonomy 기준으로 고정됐다.
- public skill `narrative`가 추가돼 source-of-truth doc alignment와 audience-facing brief derivation이 `announcement`와 분리됐다.
- public skill `init-repo`가 추가돼 greenfield bootstrap과 partial repo operating-surface normalization을 `README.md`, `AGENTS.md`, `CLAUDE.md` symlink policy, `docs/roadmap.md`, `docs/operator-acceptance.md` 기준으로 다루게 됐다.
- `init-repo`는 blanket `lychee` ignore를 기본 템플릿으로 넣지 않는다. external link 검사는 optional escalation으로 두고, broad ignore는 실제 필요가 확인된 뒤에만 좁게 추가한다.
- repo-owned release/install surface는 `plugins/charness` 아래 checked-in plugin bundle로 정리돼 있고, root marketplace files는 그 install surface만 advertise한다.
- Ceal-era migration surface는 정리됐다. tracked tree에는 `Ceal`, `interview`, `concept-review`, `test-improvement`, `entity-stage-design`, `workbench` 같은 legacy naming이 남아 있지 않다.
- `master-plan`은 더 이상 기본 운영 표면이 아니다. 기존 `docs/master-plan.md` 파일은 제거했고, planning 문서는 필요할 때만 명시적으로 만들며 기본 경로에서는 `docs/operator-acceptance.md`와 선택적 `docs/roadmap.md`를 본다.
- 이 머신의 `~/.agents/skills` source-checkout symlink는 제거됐다.
- Claude local dogfood는 exported plugin root 기준으로 확인됐다. `claude --plugin-dir /tmp/.../plugins/charness` debug log에서 `Loaded 14 skills from plugin charness`가 찍혔고, `/gather` 호출로 `TITLE:charness` 응답까지 확인했다.
- Claude local docs는 parent `plugins/` 경로를 가리키고 있었고, 그 경로는 plugin root가 아니라서 skill discovery proof가 되지 않았다. 이번 세션에서 관련 문서를 `plugins/charness` 기준으로 고친다.
- root [INSTALL.md](/home/ubuntu/charness/INSTALL.md)와 [UNINSTALL.md](/home/ubuntu/charness/UNINSTALL.md)를 추가해 agent-readable 설치 계약을 README에서 분리했다.
- `.agents/skills`는 checked-in 기본 install surface가 아니다. 이 repo는 root [.agents/plugins/marketplace.json](/home/ubuntu/charness/.agents/plugins/marketplace.json)과 [plugins/charness](/home/ubuntu/charness/plugins/charness)만 source of truth로 유지하고, source checkout public skills를 별도 symlink로 노출하지 않는다.
- `init-repo`에는 greenfield/partial state inspection eval이 추가됐고, `python3 scripts/run-evals.py --repo-root .`에서 통과했다.
- Codex `exec`는 `/tmp` exported consumer root, exported plugin root, repo root 비교 기준으로 local marketplace install proof를 제공하지 못했다. exported roots에서는 curated builtin/plugin skill만 보였고, repo root에서는 checked-in plugin 대신 source checkout `skills/`를 직접 읽었다.
- `scripts/install-machine-local.py`를 추가했다. source checkout에서 이 스크립트를 돌리면 `~/.agents/plugins/charness`로 exported install surface를 쓰고 `~/.agents/plugins/marketplace.json`에 Codex personal marketplace entry를 merge한다.
- 이 머신에서 `python3 scripts/install-machine-local.py --repo-root .`를 실제로 돌려 `~/.agents/plugins/charness`와 `~/.agents/plugins/marketplace.json`를 만들었다. marketplace `source.path`는 `./.agents/plugins/charness`다.
- `INSTALL.md`, `README.md`, `docs/host-packaging.md`는 machine-local `~/.agents` install을 preferred operator path로 설명하도록 갱신했다.
- 마지막 repo 검증은 `python3 scripts/validate-packaging.py --repo-root .`, `python3 scripts/check-doc-links.py`, `./scripts/check-markdown.sh`, `./scripts/check-secrets.sh`, `python3 -m py_compile scripts/install-machine-local.py plugins/charness/scripts/install-machine-local.py`, `./scripts/run-quality.sh` 통과와 machine-local export 생성이다.

## Next Session

1. 다른 머신 또는 실제 interactive Codex에서 `~/.agents/plugins/marketplace.json` 기준 machine-local marketplace discovery/install visibility를 확인한다.
2. 가능하면 `charness@local` enable state가 어떤 config surface에 저장되는지 실제 host output으로 확인한다.
3. repo-scoped `.agents/plugins/marketplace.json` development path와 machine-local `~/.agents` operator path를 둘 다 유지할지 다시 판단한다.
4. `init-repo` state inspection eval만으로 충분한지 보고, 필요하면 full doc-scaffold dogfood를 하나 더 추가한다.
5. Codex proof와 추가 `init-repo` dogfood 결과를 바로 이 handoff나 별도 durable artifact에 남긴다.

## Discuss

- Codex의 실제 public install proof는 여전히 가장 불확실한 표면이다. 최소한 이 머신의 `codex exec`는 repo marketplace dogfood 증거로 쓰기 어렵다.
- Claude는 shipped surface proof가 나왔다. 남은 일은 corrected local path가 문서와 generated surface에 반영됐는지 유지하는 것이다.
- machine-local install helper는 이제 추가됐다. 남은 질문은 helper가 충분한지보다, Codex interactive host가 `~/.agents/plugins/marketplace.json`를 어떻게 expose하고 enable state를 어디에 쓰는지다.

## References

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [AGENTS.md](/home/ubuntu/charness/AGENTS.md)
- [README.md](/home/ubuntu/charness/README.md)
- [INSTALL.md](/home/ubuntu/charness/INSTALL.md)
- [UNINSTALL.md](/home/ubuntu/charness/UNINSTALL.md)
- [docs/public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md)
- [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md)
- [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json)
- [plugins/charness/.claude-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.claude-plugin/plugin.json)
- [plugins/charness/.codex-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.codex-plugin/plugin.json)
- [.claude-plugin/marketplace.json](/home/ubuntu/charness/.claude-plugin/marketplace.json)
- [.agents/plugins/marketplace.json](/home/ubuntu/charness/.agents/plugins/marketplace.json)
- [skills/public/narrative/SKILL.md](/home/ubuntu/charness/skills/public/narrative/SKILL.md)
- [skills/public/announcement/SKILL.md](/home/ubuntu/charness/skills/public/announcement/SKILL.md)
- [skills/public/release/SKILL.md](/home/ubuntu/charness/skills/public/release/SKILL.md)
- [plugins/charness/skills/gather/SKILL.md](/home/ubuntu/charness/plugins/charness/skills/gather/SKILL.md)
- [plugins/charness/support/gather-notion/SKILL.md](/home/ubuntu/charness/plugins/charness/support/gather-notion/SKILL.md)
- [plugins/charness/support/gather-slack/SKILL.md](/home/ubuntu/charness/plugins/charness/support/gather-slack/SKILL.md)

# charness Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `impl`로 이어서, 먼저 [charness](/home/ubuntu/charness/charness), [INSTALL.md](/home/ubuntu/charness/INSTALL.md), [UNINSTALL.md](/home/ubuntu/charness/UNINSTALL.md), [README.md](/home/ubuntu/charness/README.md), [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md), [docs/operator-acceptance.md](/home/ubuntu/charness/docs/operator-acceptance.md), [docs/public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md), [skills/public/init-repo/SKILL.md](/home/ubuntu/charness/skills/public/init-repo/SKILL.md), [skills/public/release/SKILL.md](/home/ubuntu/charness/skills/public/release/SKILL.md)을 읽고 Codex post-install update behavior proof를 먼저 본다.
- 이 머신에서는 `~/.agents/skills` source-checkout symlink가 이미 제거돼 있으니, 다시 생기지 않았는지만 짧게 확인한다.
- Claude local proof는 끝났다. historical proof path는 `--plugin-dir /absolute/path/to/charness/plugins/charness`였고, parent `plugins/`를 주면 skill discovery proof가 되지 않았다. 이제 primary Claude path는 `charness init`가 marketplace add/install을 수행하는 global install이다.
- Codex는 managed `~/.agents/plugins/marketplace.json`를 source로 쓰되, operator-facing plugin root는 `~/.codex/plugins/charness`로 둔다. marketplace policy는 `AVAILABLE`로 두고, `exec`만으로는 install/discovery proof가 약하니 interactive session 또는 다른 머신에서 실제 visibility proof를 이어서 본다.
- Retro 2026-04-11: `INSTALLED_BY_DEFAULT`를 `~/.agents/plugins/marketplace.json`에 넣으면 다음 세션에서 plugin이 바로 세션 skill로 올라올 것이라고 가정한 건 과했다. 공식 문서는 personal marketplace가 Plugin Directory source가 된다고 설명하고, 실제 install은 `~/.codex/plugins/cache/...`에 생기며 enable state는 `~/.codex/config.toml`에 남는다고 구분한다. `~/.codex/plugins/charness`는 source plugin root일 뿐, cache/config 흔적이 없으면 host install은 아직 안 된 신호로 취급해야 한다.

## Current State

- `charness`는 portable Corca harness product로 정리됐고, public/support/profile/integration 경계는 현재 taxonomy 기준으로 고정됐다.
- public skill `narrative`가 추가돼 source-of-truth doc alignment와 audience-facing brief derivation이 `announcement`와 분리됐다.
- public skill `init-repo`가 추가돼 greenfield bootstrap과 partial repo operating-surface normalization을 `README.md`, `AGENTS.md`, `CLAUDE.md` symlink policy, `docs/roadmap.md`, `docs/operator-acceptance.md` 기준으로 다루게 됐다.
- `init-repo`는 blanket `lychee` ignore를 기본 템플릿으로 넣지 않는다. external link 검사는 optional escalation으로 두고, broad ignore는 실제 필요가 확인된 뒤에만 좁게 추가한다.
- repo-owned release/install surface는 `plugins/charness` 아래 checked-in plugin bundle로 정리돼 있고, root marketplace files는 compatibility artifact로만 남긴다.
- Ceal-era migration surface는 정리됐다. tracked tree에는 `Ceal`, `interview`, `concept-review`, `test-improvement`, `entity-stage-design`, `workbench` 같은 legacy naming이 남아 있지 않다.
- `master-plan`은 더 이상 기본 운영 표면이 아니다. 기존 `docs/master-plan.md` 파일은 제거했고, planning 문서는 필요할 때만 명시적으로 만들며 기본 경로에서는 `docs/operator-acceptance.md`와 선택적 `docs/roadmap.md`를 본다.
- 이 머신의 `~/.agents/skills` source-checkout symlink는 제거됐다.
- Claude local dogfood는 exported plugin root 기준으로 확인됐다. `claude --plugin-dir /tmp/.../plugins/charness` debug log에서 `Loaded 14 skills from plugin charness`가 찍혔고, `/gather` 호출로 `TITLE:charness` 응답까지 확인했다.
- root executable [charness](/home/ubuntu/charness/charness)를 추가했다. `init`, `update`, `doctor`, `reset`, `uninstall`를 제공하고, checkout 기반 bootstrap일 때 `~/.local/bin/charness`에 자기 자신을 설치한다.
- root bootstrap script [init.sh](/home/ubuntu/charness/init.sh)를 추가했다. 공식 first-run entrypoint는 이제 `./init.sh`이고, 이 스크립트가 managed checkout `~/.agents/src/charness`를 만들거나 재사용한 뒤 `charness init`를 호출한다.
- `./charness init`는 managed install surface를 만든다: `~/.codex/plugins/charness`, `~/.agents/plugins/marketplace.json`, `~/.local/bin/charness`, optional `~/.local/bin/claude-charness`, plus Claude user-scope marketplace/plugin install.
- official installed CLI source는 이제 managed checkout `~/.agents/src/charness`만 허용한다. repo 밖에서 쓰는 `charness`는 `~/.local/share/charness/install-state.json`을 통해 그 managed checkout을 기억한다. non-managed `--repo-root`는 proof/development path로만 남고 `--skip-cli-install`이 필요하다.
- `charness tool doctor|install|update|sync-support`가 추가됐다. external integration lifecycle는 thin CLI에서 직접 호출할 수 있고, 결과는 `integrations/locks/*.json`과 `skills/support/generated/`에 agent-readable state로 남는다.
- `.agents/skills`는 checked-in 기본 install surface가 아니다. 이 repo는 thin CLI가 관리하는 `~/.codex/plugins/charness` source plugin root와 `~/.agents/plugins/marketplace.json`를 operator install anchor로 쓰고, source checkout public skills를 별도 symlink로 노출하지 않는다.
- `INSTALL.md`, `README.md`, `UNINSTALL.md`, `docs/host-packaging.md`, `docs/operator-acceptance.md`는 marketplace 설치를 primary path에서 내리고 thin CLI managed install을 공식 경로로 설명하도록 갱신했다.
- `skills/public/release/*`와 `scripts/plugin_preamble.py`도 `charness update` / Claude restart 기준으로 갱신했다.
- `scripts/run-evals.py`에 managed CLI install smoke가 추가됐다.
- 마지막 repo 검증은 managed CLI smoke 포함 `./scripts/run-quality.sh` 통과와 temp-home managed install eval이다.
- Retro 2026-04-11 #3: `./charness init --repo-root /checkout`로 CLI를 설치해도 이후 `/home/ubuntu` 같은 repo 밖에서 `charness update`와 `charness doctor`를 실행할 수 있다고 착각했다. 실제로는 installed CLI가 managed checkout 기본값 `~/.agents/src/charness`만 찾았고, 그 경로가 없으면 `update`는 `missing source checkout`로 실패하고 `doctor`는 traceback을 냈다. 이제 CLI는 마지막 successful `init`/`update`의 source checkout을 `~/.local/share/charness/install-state.json`에 기억하고, source가 없을 때도 `doctor`가 `missing-source` guidance를 내도록 고쳤다.
- Claude local marketplace update dogfood는 끝났다. temp checkout에서 `0.0.1-update-test -> 0.0.2-update-test`로 버전을 올리고 `charness update`를 돌렸을 때 `~/.claude/plugins/cache/corca-charness-update-test/charness/...` install path와 installed version이 같이 올라갔다.
- 이 머신의 Codex는 이제 실제 host install 상태다. `~/.codex/config.toml`에는 `[plugins."charness@local"] enabled = true`가 있고, cache manifest는 `~/.codex/plugins/cache/local/charness/local/.codex-plugin/plugin.json`에 생긴다.
- Retro 2026-04-11 #2: Codex host install이 끝난 뒤에도 source plugin root만 새 버전으로 덮어쓰고 `codex exec`를 새 프로세스로 띄우는 것만으로는 cache manifest version이 바뀌지 않았다. source는 `0.0.3-codex-test`로 올라갔지만 cache는 `0.0.0-dev`에 남았고, 원복 뒤에도 cache는 그대로였다. 즉 현재 증거로는 `charness update` + restart만으로 Codex installed cache가 자동 갱신된다고 말할 수 없다.
- control-plane principle도 정리됐다. manual-only tool install/update라도 CLI 출력과 lock state에 다음 operator step이 남아야 하고, support sync는 가능하면 generated artifact를 남긴다.

## Next Session

1. 실제 interactive Codex에서 installed `charness`를 source update 뒤 어떻게 refresh해야 cache가 갱신되는지 확인한다. restart만으로 되는지, Plugin Directory 재-install/re-enable이 필요한지 proof를 만든다.
2. 새 `charness tool install/update/doctor` surface를 실제 다른 머신 또는 temp-home workflow로 한 번 더 dogfood한다. 특히 manual-mode tool(`cautilus`, `specdown`, `gws-cli`)에서 남는 lock/install guidance shape를 점검한다.
3. `charness reset`이 Codex/Claude host state를 충분히 clean하게 지우는지 다른 머신에서도 확인한다.
4. `charness` single-file publish/bootstrap 경로를 어떻게 노출할지 결정한다.
5. Codex proof와 추가 dogfood 결과를 바로 이 handoff나 별도 durable artifact에 남긴다.

## Discuss

- Codex의 실제 interactive update proof가 가장 불확실한 표면이다. install 자체는 이 머신에서 끝났지만, 최소한 `codex exec` 새 프로세스만으로는 installed cache refresh proof가 되지 않았다.
- Claude global install은 이제 primary path로 정리됐다. `claude-charness` wrapper는 fallback/proof 경로라 문서와 runtime hint가 다시 drift하지 않게 봐야 한다.
- thin CLI는 들어갔고 managed path는 하나로 정리됐다. 남은 질문은 publish/bootstrap UX와 interactive Codex visibility proof다.

## References

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [AGENTS.md](/home/ubuntu/charness/AGENTS.md)
- [README.md](/home/ubuntu/charness/README.md)
- [INSTALL.md](/home/ubuntu/charness/INSTALL.md)
- [UNINSTALL.md](/home/ubuntu/charness/UNINSTALL.md)
- [charness](/home/ubuntu/charness/charness)
- [docs/public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md)
- [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md)
- [docs/operator-acceptance.md](/home/ubuntu/charness/docs/operator-acceptance.md)
- [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json)
- [plugins/charness/.claude-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.claude-plugin/plugin.json)
- [plugins/charness/.codex-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.codex-plugin/plugin.json)
- [.claude-plugin/marketplace.json](/home/ubuntu/charness/.claude-plugin/marketplace.json)
- [.agents/plugins/marketplace.json](/home/ubuntu/charness/.agents/plugins/marketplace.json)
- [skills/public/init-repo/SKILL.md](/home/ubuntu/charness/skills/public/init-repo/SKILL.md)
- [skills/public/release/SKILL.md](/home/ubuntu/charness/skills/public/release/SKILL.md)
- [skills/public/narrative/SKILL.md](/home/ubuntu/charness/skills/public/narrative/SKILL.md)

# charness Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `impl`로 이어서, 먼저 [charness](../charness), [INSTALL.md](../INSTALL.md), [UNINSTALL.md](../UNINSTALL.md), [README.md](../README.md), [docs/host-packaging.md](host-packaging.md), [docs/operator-acceptance.md](operator-acceptance.md), [docs/public-skill-validation.md](public-skill-validation.md), [skills/public/init-repo/SKILL.md](../skills/public/init-repo/SKILL.md), [skills/public/release/SKILL.md](../skills/public/release/SKILL.md)을 읽고 "install succeeds"가 아니라 "upstream skill/plugin payload change가 `charness update` 뒤 host-visible installed copy까지 실제 전파되는가"를 먼저 본다.
- 이 머신의 `~/.agents/skills` source-checkout symlink는 2026-04-12에 다시 확인했을 때 실제로 남아 있었고, 이후 다시 제거했다. 이제 `charness init/update/reset/uninstall`가 symlink일 때 자동 제거하므로 다음 세션에서는 재발 여부만 짧게 확인하면 된다.
- `~/.local/share/charness/host-state.json`이 있으면 `last_update` 또는 `last_doctor` snapshot부터 보고, interactive Codex restart 전후 차이를 proof source로 쓴다.
- Claude local proof는 끝났다. historical proof path는 `--plugin-dir /absolute/path/to/charness/plugins/charness`였고, parent `plugins/`를 주면 skill discovery proof가 되지 않았다. 이제 primary Claude path는 `charness init`가 marketplace add/install을 수행하는 global install이다.
- Codex는 managed `~/.agents/plugins/marketplace.json`를 source로 쓰되, operator-facing plugin root는 `~/.codex/plugins/charness`로 둔다. marketplace policy는 `AVAILABLE`로 두고, install/discovery 자체는 이미 확인됐으니 남은 proof는 interactive session 또는 다른 머신에서 "`charness update` 뒤 upstream payload change가 installed cache/visible skills까지 반영되는가"에 집중한다.
- Retro 2026-04-11: `INSTALLED_BY_DEFAULT`를 `~/.agents/plugins/marketplace.json`에 넣으면 다음 세션에서 plugin이 바로 세션 skill로 올라올 것이라고 가정한 건 과했다. 공식 문서는 personal marketplace가 Plugin Directory source가 된다고 설명하고, 실제 install은 `~/.codex/plugins/cache/...`에 생기며 enable state는 `~/.codex/config.toml`에 남는다고 구분한다. `~/.codex/plugins/charness`는 source plugin root일 뿐, cache/config 흔적이 없으면 host install은 아직 안 된 신호로 취급해야 한다.

## Current State

- `charness`는 portable Corca harness product로 정리됐고, public/support/profile/integration 경계는 현재 taxonomy 기준으로 고정됐다.
- public skill `narrative`가 추가돼 source-of-truth doc alignment와 audience-facing brief derivation이 `announcement`와 분리됐다.
- public skill `init-repo`가 추가돼 greenfield bootstrap과 partial repo operating-surface normalization을 `README.md`, `AGENTS.md`, `CLAUDE.md` symlink policy, `docs/roadmap.md`, `docs/operator-acceptance.md` 기준으로 다루게 됐다.
- `init-repo`는 blanket `lychee` ignore를 기본 템플릿으로 넣지 않는다. external link 검사는 optional escalation으로 두고, broad ignore는 실제 필요가 확인된 뒤에만 좁게 추가한다.
- repo-owned release/install surface는 `plugins/charness` 아래 checked-in plugin bundle로 정리돼 있고, root marketplace files는 compatibility artifact로만 남긴다.
- Ceal-era migration surface는 정리됐다. tracked tree에는 `Ceal`, `interview`, `concept-review`, `test-improvement`, `entity-stage-design`, `workbench` 같은 legacy naming이 남아 있지 않다.
- `master-plan`은 더 이상 기본 운영 표면이 아니다. 기존 `docs/master-plan.md` 파일은 제거했고, planning 문서는 필요할 때만 명시적으로 만들며 기본 경로에서는 `docs/operator-acceptance.md`와 선택적 `docs/roadmap.md`를 본다.
- 이 머신의 `~/.agents/skills` source-checkout symlink는 2026-04-12에 다시 제거했고, charness CLI도 같은 잔재를 자동 정리하도록 보강했다.
- Claude local dogfood는 exported plugin root 기준으로 확인됐다. `claude --plugin-dir /tmp/.../plugins/charness` debug log에서 `Loaded 14 skills from plugin charness`가 찍혔고, `/gather` 호출로 `TITLE:charness` 응답까지 확인했다.
- root executable [charness](../charness)를 추가했다. `init`, `update`, `doctor`, `reset`, `uninstall`를 제공하고, standalone binary만 있어도 `charness init`가 managed checkout `~/.agents/src/charness`를 내부 clone으로 bootstrap할 수 있다.
- root bootstrap script [init.sh](../init.sh)를 추가했다. 이 스크립트는 checkout convenience wrapper이고, 내부적으로 managed checkout `~/.agents/src/charness`를 만들거나 재사용한 뒤 `charness init`를 호출한다.
- `./charness init`는 managed install surface를 만든다: `~/.codex/plugins/charness`, `~/.agents/plugins/marketplace.json`, `~/.local/bin/charness`, optional `~/.local/bin/claude-charness`, plus Claude user-scope marketplace/plugin install.
- official installed CLI source는 이제 managed checkout `~/.agents/src/charness`만 허용한다. repo 밖에서 쓰는 `charness`는 `~/.local/share/charness/install-state.json`을 통해 그 managed checkout을 기억한다. non-managed `--repo-root`는 proof/development path로만 남고 `--skip-cli-install`이 필요하다.
- `charness tool doctor|install|update|sync-support`가 추가됐다. external integration lifecycle는 thin CLI에서 직접 호출할 수 있고, 결과는 `integrations/locks/*.json`과 `skills/support/generated/`에 agent-readable state로 남는다.
- tool control-plane은 GitHub latest-release probe도 포함한다. `specdown`은 실제 latest release `v0.47.2`를 잡았고, `cautilus`는 current GitHub latest-release endpoint 기준으로 `no-release`(`http 404`)로 기록된다.
- tool control-plane은 이제 install provenance도 lock/doctor output에 남긴다. `gws-cli`처럼 실제 설치 경로가 `npm`으로 판별되면 `charness tool update --dry-run`이 `npm install -g @googleworkspace/cli@latest` 같은 package-manager route로 승격된다. `specdown`처럼 provenance가 plain `path`면 release metadata를 붙인 manual guidance로 남는다.
- public skill `create-cli`가 추가됐다. repo-owned CLI를 만들거나 손볼 때 command surface, install/update UX, machine-readable state, quality gate를 한 묶음으로 다루는 기본 참고 skill이다.
- `create-cli` references는 `cautilus` 배포 메모를 반영해 release-first install contract, installer가 OS package manager를 직접 만지지 않는 원칙, provenance-aware update routing을 기본 guidance로 포함한다.
- checked-in plugin export는 더 이상 machine-local `integrations/locks/*.json`를 복사하지 않는다. export surface에는 `lock.schema.json`, `README.md`, `.gitkeep`만 남는다.
- `.githooks/pre-push`는 이제 `sync_root_plugin_manifests.py`를 먼저 돌리고, `plugins/charness` 또는 root marketplace artifacts에 drift가 생기면 push를 막은 뒤에만 `./scripts/run-quality.sh`를 실행한다.
- `.agents/skills`는 checked-in 기본 install surface가 아니다. 이 repo는 thin CLI가 관리하는 `~/.codex/plugins/charness` source plugin root와 `~/.agents/plugins/marketplace.json`를 operator install anchor로 쓰고, source checkout public skills를 별도 symlink로 노출하지 않는다.
- `INSTALL.md`, `README.md`, `UNINSTALL.md`, `docs/host-packaging.md`, `docs/operator-acceptance.md`는 marketplace 설치를 primary path에서 내리고 thin CLI managed install을 공식 경로로 설명하도록 갱신했다.
- `skills/public/release/*`와 `scripts/plugin_preamble.py`도 `charness update` / Claude restart 기준으로 갱신했다.
- `scripts/run-evals.py`에서는 historical current-repo smokes를 줄였다. `managed-cli-install`, `packaging-valid`, `packaging-export`는 더 직접적인 standing CLI tests/validators가 같은 seam을 이미 증명하므로 제거됐고, 남은 eval은 bootstrap/adapter/portability contract 위주로 유지한다.
- 마지막 repo 검증은 managed CLI smoke 포함 `./scripts/run-quality.sh` 통과와 temp-home managed install eval이다.
- public skill authoring contract도 보강됐다. `AGENTS.md`와 `create-skill`은 이제 sparse real-person anchor를 `SKILL.md` core의 의도적 retrieval technique로 취급하되, 행동 규칙에 연결되고 사실충실해야 하며 selection logic은 core에, nuance와 payload는 `references/`에 두라고 명시한다.
- `ideation/spec/impl/handoff`는 Christopher Alexander-style sequence discipline을 core behavior로 갖고, `ideation`은 Saras Sarasvathy effectuation, `spec/impl`은 Kent Beck + John Ousterhout, `retro`는 named expert lens를 선호하되 direct counterfactual lens도 허용하는 쪽으로 정리됐다.
- `charness init`와 `charness update`는 이제 `~/.local/share/charness/host-state.json`에 post-command doctor snapshot을 남긴다. `charness doctor --write-state`로도 interactive restart 전후 proof snapshot을 수동 기록할 수 있다.
- installed `charness` CLI는 이제 `~/.local/share/charness/version-state.json`에 current version provenance와 cached latest-release check를 남긴다. `charness version --check`가 explicit refresh surface고, interactive installed-CLI runs는 24시간 TTL cache를 써서 non-fatal update notice를 낼 수 있다.
- 다른 머신 Claude Code dogfood에서 standalone `charness` binary만으로 manual clone 없이 `charness init` / `charness update`가 성공했다. `~/.agents/src/charness`, `~/.codex/plugins/charness`, `~/.agents/plugins/marketplace.json`도 기대한 위치에 생겼고, Claude visibility는 실제로 확인됐다.
- `charness update`는 이제 installed CLI self-refresh도 실제로 수행한다. 이전에는 PATH의 installed CLI가 자기 자신을 다시 복사하려 해 stale binary가 남을 수 있었는데, 이제 managed checkout의 [`charness`](../charness)를 `~/.local/bin/charness`로 다시 설치한다. temp-home standalone proof에서 `doctor --write-state`와 update 후 CLI sentinel refresh를 다시 확인했다.
- 같은 dogfood 보고서의 `charness doctor --write-state` 미지원은 최신 `main`을 pull하기 전 installed PATH binary로 실행했을 가능성이 높다. 현재 `main`에는 installed CLI self-refresh fix가 들어갔지만, 그 이전 설치자는 `~/.agents/src/charness/charness update`를 한 번 직접 실행해 PATH binary를 회복시켜야 할 수 있다.
- Retro 2026-04-12 #1: installed CLI update seam을 내가 늦게 잡은 이유는 source checkout과 managed checkout state는 계속 보고 있었지만, "old PATH binary가 update 뒤 새 checkout binary로 실제 교체되는가"를 별도 계약 seam으로 분리하지 않았기 때문이다. 앞으로 install/update 작업에서는 source checkout, managed checkout, installed PATH binary를 따로 검증하고, 새 플래그 추가 뒤에는 "이전 설치자 recovery"까지 명시적으로 확인해야 한다.
- Retro 2026-04-11 #3: `./charness init --repo-root /checkout`로 CLI를 설치해도 이후 `/home/ubuntu` 같은 repo 밖에서 `charness update`와 `charness doctor`를 실행할 수 있다고 착각했다. 실제로는 installed CLI가 managed checkout 기본값 `~/.agents/src/charness`만 찾았고, 그 경로가 없으면 `update`는 `missing source checkout`로 실패하고 `doctor`는 traceback을 냈다. 이제 CLI는 마지막 successful `init`/`update`의 source checkout을 `~/.local/share/charness/install-state.json`에 기억하고, source가 없을 때도 `doctor`가 `missing-source` guidance를 내도록 고쳤다.
- Claude local marketplace update dogfood는 끝났다. temp checkout에서 `0.0.1-update-test -> 0.0.2-update-test`로 버전을 올리고 `charness update`를 돌렸을 때 `~/.claude/plugins/cache/corca-charness-update-test/charness/...` install path와 installed version이 같이 올라갔다.
- 이 머신의 Codex는 이제 실제 host install 상태다. `~/.codex/config.toml`에는 `[plugins."charness@local"] enabled = true`가 있고, cache manifest는 `~/.codex/plugins/cache/local/charness/local/.codex-plugin/plugin.json`에 생긴다.
- Retro 2026-04-11 #2: Codex host install이 끝난 뒤에도 source plugin root만 새 버전으로 덮어쓰고 `codex exec`를 새 프로세스로 띄우는 것만으로는 cache manifest version이 바뀌지 않았다. source는 `0.0.3-codex-test`로 올라갔지만 cache는 `0.0.0-dev`에 남았고, 원복 뒤에도 cache는 그대로였다. 즉 현재 증거로는 `charness update` + restart만으로 Codex installed cache가 자동 갱신된다고 말할 수 없다.
- control-plane principle도 정리됐다. manual-only tool install/update라도 CLI 출력과 lock state에 다음 operator step이 남아야 하고, support sync는 가능하면 generated artifact를 남긴다.

## Next Session

1. 실제 interactive Codex에서 upstream skill/plugin payload를 의도적으로 바꾼 뒤 `charness update`가 그 변경을 installed cache와 visible skill surface까지 전파하는지 확인한다. restart만으로 되는지, Plugin Directory 재-install/re-enable이 필요한지 proof를 만든다.
   - 가능하면 restart 전 `host-state.json:last_update` 또는 `charness doctor --write-state` snapshot과, restart 뒤 새 `last_doctor` snapshot을 비교해 proof를 남긴다.
2. 새 `charness tool install/update/doctor` surface를 실제 다른 머신 또는 temp-home workflow로 한 번 더 dogfood한다. 특히 provenance-aware route가 있는 tool(`gws-cli`, brew-installed `specdown`, brew-installed `gh`)과 manual-only tool(`cautilus`, release-installed `specdown`)에서 남는 lock/install guidance shape를 점검한다.
   - 현재 local proof는 `/home/ubuntu/charness` working tree에서 `--repo-root .`를 명시해 돌렸다. installed CLI default는 여전히 managed checkout을 보므로, unpushed local changes를 proof할 때는 그 차이를 의식한다.
3. `charness reset`이 Codex/Claude host state를 충분히 clean하게 지우는지 다른 머신에서도 확인한다.
4. standalone `charness` binary 배포/bootstrap 경로를 어떻게 노출할지 결정한다.
5. Codex proof와 추가 dogfood 결과를 바로 이 handoff나 별도 durable artifact에 남긴다.

## Discuss

- Codex의 실제 interactive update propagation proof가 가장 불확실한 표면이다. install 자체는 이 머신에서 끝났고 plugin visibility도 어느 정도 확인됐지만, 최소한 `codex exec` 새 프로세스만으로는 upstream payload change가 installed cache/visible skills까지 반영된다는 proof가 되지 않았다.
- Claude global install은 이제 primary path로 정리됐다. `claude-charness` wrapper는 fallback/proof 경로라 문서와 runtime hint가 다시 drift하지 않게 봐야 한다.
- thin CLI는 들어갔고 managed path는 하나로 정리됐다. 남은 질문은 standalone binary distribution UX와 interactive Codex update propagation proof다.

## References

- [docs/handoff.md](handoff.md)
- [AGENTS.md](../AGENTS.md)
- [README.md](../README.md)
- [INSTALL.md](../INSTALL.md)
- [UNINSTALL.md](../UNINSTALL.md)
- [charness](../charness)
- [docs/public-skill-validation.md](public-skill-validation.md)
- [docs/host-packaging.md](host-packaging.md)
- [docs/operator-acceptance.md](operator-acceptance.md)
- [packaging/charness.json](../packaging/charness.json)
- [plugins/charness/.claude-plugin/plugin.json](../plugins/charness/.claude-plugin/plugin.json)
- [plugins/charness/.codex-plugin/plugin.json](../plugins/charness/.codex-plugin/plugin.json)
- [.claude-plugin/marketplace.json](../.claude-plugin/marketplace.json)
- [.agents/plugins/marketplace.json](../.agents/plugins/marketplace.json)
- [skills/public/init-repo/SKILL.md](../skills/public/init-repo/SKILL.md)
- [skills/public/release/SKILL.md](../skills/public/release/SKILL.md)
- [skills/public/narrative/SKILL.md](../skills/public/narrative/SKILL.md)

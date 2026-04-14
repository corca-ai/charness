# charness Handoff

## Workflow Trigger

- 다음 세션이 support-tool follow-up이면 먼저 [docs/support-tool-followup.md](support-tool-followup.md)를 읽는다. `create-cli` probe-layer slice, `find-skills` recommendation helper first slice, `quality` installable-CLI probe-contract posture(`#10`), `quality` executable-spec / fragile-margin pass(`#13`), shared recommendation/install payload의 `quality` 재사용 seam, `init-repo` probe-surface follow-on(`#11`), `quality` blind-spot / anti-anchoring / premortem follow-on(`#14`), `quality` code-reduction-first / adapter-driven gate pattern follow-on(`#6`), `impl` truth-surface sync closeout(`#8`), `impl` autonomous-continuation default(`#7`), `handoff` diary anti-pattern hygiene(`#15`)은 landed 상태다. 다음 후보 둘은 비교적 분명하다: support-tool-adjacent로는 verifier-selection helper / changed-surface-to-validator mapper, public-skill follow-up으로는 `retro` `#16` fresh-eye misread trigger. 각 slice마다 public skill source-of-truth 수정과 `charness` dogfood를 함께 끝내야 한다.
- verification command 선택은 아직 부분적으로 수동이다. `git push`를 verifier로 승격하는 방향은 기각됐고, 대신 future follow-on은 repo-owned verifier bundle / hook entrypoint detector / changed-surface-to-validator mapper 쪽으로 가야 한다. 관련 맥락은 [docs/support-tool-followup.md](support-tool-followup.md)의 `Verification Selection Note`에 남겨 뒀다.
- 다음 세션에서 이 문서를 멘션하면 `impl`로 이어서, 먼저 [charness](../charness), [INSTALL.md](../INSTALL.md), [UNINSTALL.md](../UNINSTALL.md), [README.md](../README.md), [docs/host-packaging.md](host-packaging.md), [docs/operator-acceptance.md](operator-acceptance.md), [docs/public-skill-validation.md](public-skill-validation.md), [skills/public/init-repo/SKILL.md](../skills/public/init-repo/SKILL.md), [skills/public/release/SKILL.md](../skills/public/release/SKILL.md)을 읽고 "install succeeds"가 아니라 "upstream skill/plugin payload change가 `charness update` 뒤 host-visible installed copy까지 실제 전파되는가"를 먼저 본다.
- 이 머신의 `~/.agents/skills` source-checkout symlink는 2026-04-12에 다시 확인했을 때 실제로 남아 있었고, 이후 다시 제거했다. 이제 `charness init/update/reset/uninstall`가 symlink일 때 자동 제거하므로 다음 세션에서는 재발 여부만 짧게 확인하면 된다.
- `~/.local/state/charness/host-state.json`이 있으면 `last_update` 또는 `last_doctor` snapshot부터 보고, interactive Codex restart 전후 차이를 proof source로 쓴다.
- Claude local proof는 끝났다. historical proof path는 `--plugin-dir /absolute/path/to/charness/plugins/charness`였고, parent `plugins/`를 주면 skill discovery proof가 되지 않았다. 이제 primary Claude path는 `charness init`가 marketplace add/install을 수행하는 global install이다.
- Codex는 managed `~/.agents/plugins/marketplace.json`를 source로 쓰되, operator-facing plugin root는 `~/.codex/plugins/charness`로 둔다. marketplace policy는 `AVAILABLE`로 두고, install/discovery와 cache refresh 자체는 이미 확인됐으니 남은 proof는 interactive session 또는 다른 머신에서 "`charness update` 뒤 visible skill surface가 어떤 최소 refresh step에서 따라오는가"에 집중한다.
- 다른 머신 Codex dogfood에서는 cache refresh 자체는 확인됐지만, restart만으로 visible skill surface까지 따라오는지는 아직 분리 기록이 부족하다. 현재 `main`의 `charness init`/`update`는 모두 same `plugin/install` seam을 타므로, 남은 proof는 "clean installed baseline에서 upstream-visible payload delta를 만든 뒤 restart-only -> Plugin Directory re-enable -> Plugin Directory reinstall 중 어느 단계가 실제로 필요했는가"를 순서대로 남기는 것이다.
- `update-probe` 실험은 종료 단계다. 다음 proof는 `0.0.3-update-probe`가 설치된 다른 머신에서 `main`의 `0.0.4-dev`로 `charness update`한 뒤, Codex cache refresh와 visible skill disappearance가 각각 어느 단계에서 반영되는지 기록하는 것이다.
- Retro 2026-04-11: `INSTALLED_BY_DEFAULT`를 `~/.agents/plugins/marketplace.json`에 넣으면 다음 세션에서 plugin이 바로 세션 skill로 올라올 것이라고 가정한 건 과했다. 공식 문서는 personal marketplace가 Plugin Directory source가 된다고 설명하고, 실제 install은 `~/.codex/plugins/cache/...`에 생기며 enable state는 `~/.codex/config.toml`에 남는다고 구분한다. `~/.codex/plugins/charness`는 source plugin root일 뿐, cache/config 흔적이 없으면 host install은 아직 안 된 신호로 취급해야 한다.

## Current State

- `charness`는 portable Corca harness product로 정리됐고, public/support/profile/integration 경계는 현재 taxonomy 기준으로 고정됐다.
- public skill `narrative`가 추가돼 source-of-truth doc alignment와 audience-neutral brief skeleton derivation이 `announcement`의 audience/channel adaptation과 분리됐다.
- public skill `quality`는 이제 review posture뿐 아니라 explicit bootstrap posture도 가진다. [`bootstrap_adapter.py`](../skills/public/quality/scripts/bootstrap_adapter.py)가 `.agents/quality-adapter.yaml`을 idempotent하게 채우고 `installed/inferred/deferred` 상태를 JSON으로 남긴다.
- public skill `quality`는 이제 installable CLI probe-contract posture도 explicit하게 가진다. help / binary health / install-readiness / local discoverability를 구분해서 보게 했고, missing external tool이 deeper proof를 막으면 exact install + verify route를 같이 surface하라고 명시했다.
- public skill `quality`는 이제 executable-spec smoke-vs-behavior classification과 fragile coverage-floor tagging도 adapter-owned knobs로 가진다. `.agents/quality-adapter.yaml`에는 `specdown_smoke_patterns`와 `coverage_fragile_margin_pp`가 들어가고, `specdown-quality` preset은 sensible default patterns를 seed한다.
- public skill `quality`는 이제 blind-spot 방지도 explicit하게 가진다. `.agents/quality-adapter.yaml`에는 `coverage_floor_policy`와 `spec_pytest_reference_format`가 들어가고, bootstrap은 이전 `quality.md`를 authoritative scope로 취급하지 않으며 workflow는 fresh-eye premortem을 한 번 요구한다.
- public skill `quality`는 이제 code-reduction-first와 adapter-driven gate pattern도 explicit하게 가진다. 같은 confidence gap을 production-surface 축소로 닫을 수 있으면 test inflation보다 그쪽을 먼저 택하게 했고, bounded test-ratio posture, focused-gate evidence drift after seam refactors, checked-in hook + installer + extra binary install path의 positive pattern을 named guidance로 올렸다.
- public skill `impl`은 이제 user-visible slice closeout에서 truth-surface sync checkpoint도 explicit하게 가진다. adapter에 `truth_surfaces`를 둘 수 있고, capability / install surface / supported integration / honest stage claim이 바뀐 뒤엔 `README.md` 같은 durable docs가 stale해졌는지 확인하거나, update가 불필요한 이유를 closeout에 남기게 했다.
- public skill `impl`은 이제 user가 autonomous continuation을 명시했을 때의 stop condition도 explicit하게 가진다. commit / verification / contract sync는 default stop point가 아니라 continuation checkpoint로 취급하고, real decision / irreversible side effect / missing stronger-proof permission-or-setup / unresolved evidence conflict일 때만 멈추게 했다.
- public skill `handoff`는 이제 dated `This Session (<date>)` diary stacking anti-pattern을 explicit하게 금지한다. 기본 hygiene gate를 대략 200줄로 두고, handoff가 그보다 커지거나 dated session section이 여러 개 쌓였으면 prune-or-spill pass를 먼저 하게 했고, spill target reference도 추가했다.
- development/proof-only install surface도 정리됐다. operator install contract는 [`INSTALL.md`](../INSTALL.md)에 남기고, non-managed `--repo-root` proof path와 `charness update --repo-root . --no-pull` dogfood path는 [`docs/development.md`](development.md)로 분리했다.
- `quality` references에는 generic [`coverage-floor-inventory.py`](../skills/public/quality/references/coverage-floor-inventory.py), [`coverage-floor-exemptions.txt`](../skills/public/quality/references/coverage-floor-exemptions.txt), [`validate-spec-pytest-references.py`](../skills/public/quality/references/validate-spec-pytest-references.py)가 추가됐다. 이 reference posture는 glob-based quality-gate discovery, lefthook/CI meta-check, contradiction fail-fast, exemption-path existence, 그리고 "pytest-reference validator는 collection만 증명하고 behavior binding은 증명하지 않는다"는 honesty note를 같이 남긴다.
- shared recommendation/install payload는 이제 `find-skills`뿐 아니라 `quality`에서도 실제로 재사용된다. `skills/public/quality/scripts/list_tool_recommendations.py --repo-root .`가 blocking validation tool만 추려서 why/install/verify/next-skill 맥락을 같이 준다.
- public skill `init-repo`가 추가돼 greenfield bootstrap과 partial repo operating-surface normalization을 `README.md`, `AGENTS.md`, `CLAUDE.md` symlink policy, `docs/roadmap.md`, `docs/operator-acceptance.md` 기준으로 다루게 됐다. 이제 `PARTIAL` 안에서도 one-missing-surface targeted repair를 따로 감지하고, `operator-acceptance`는 기존 repo checks와 takeover steps에서 합성하는 기준을 가진다.
- `init-repo`는 이제 [`synthesize_operator_acceptance.py`](../skills/public/init-repo/scripts/synthesize_operator_acceptance.py)로 functional-check style Markdown specs와 repo-owned command surface에서 `docs/operator-acceptance.md` 초안을 실제로 합성할 수 있다.
- public skill `init-repo`는 이제 installable surface가 있는 repo에서 `README.md` / `INSTALL.md`가 작은 explicit probe surface를 가지도록 가이드한다. 새 [`probe-surface.md`](../skills/public/init-repo/references/probe-surface.md)가 install/update path, binary healthcheck, machine-readable discovery, readiness, local discoverability를 필요한 경우에만 이름 붙이게 한다.
- GitHub Actions workflow drift용 repo-owned checker `python3 scripts/check-github-actions.py --repo-root .`가 추가됐고, `init-repo`는 Node 24-ready first-party action majors baseline을 reference로 유지한다.
- `init-repo`는 blanket `lychee` ignore를 기본 템플릿으로 넣지 않는다. external link 검사는 optional escalation으로 두고, broad ignore는 실제 필요가 확인된 뒤에만 좁게 추가한다.
- repo-owned release/install surface는 `plugins/charness` 아래 checked-in plugin bundle로 정리돼 있고, root marketplace files는 compatibility artifact로만 남긴다.
- Ceal-era migration surface는 정리됐다. tracked tree에는 `Ceal`, `interview`, `concept-review`, `test-improvement`, `entity-stage-design`, `workbench` 같은 legacy naming이 남아 있지 않다.
- `master-plan`은 더 이상 기본 운영 표면이 아니다. 기존 `docs/master-plan.md` 파일은 제거했고, planning 문서는 필요할 때만 명시적으로 만들며 기본 경로에서는 `docs/operator-acceptance.md`와 선택적 `docs/roadmap.md`를 본다.
- 이 머신의 `~/.agents/skills` source-checkout symlink는 2026-04-12에 다시 제거했고, charness CLI도 같은 잔재를 자동 정리하도록 보강했다.
- Claude local dogfood는 exported plugin root 기준으로 확인됐다. `claude --plugin-dir /tmp/.../plugins/charness` debug log에서 `Loaded 14 skills from plugin charness`가 찍혔고, `/gather` 호출로 `TITLE:charness` 응답까지 확인했다.
- root executable [charness](../charness)를 추가했다. `init`, `update`, `doctor`, `reset`, `uninstall`를 제공하고, standalone binary만 있어도 `charness init`가 managed checkout `~/.agents/src/charness`를 내부 clone으로 bootstrap할 수 있다.
- root bootstrap script [init.sh](../init.sh)를 추가했다. 이 스크립트는 checkout convenience wrapper이고, 내부적으로 managed checkout `~/.agents/src/charness`를 만들거나 재사용한 뒤 `charness init`를 호출한다.
- `./charness init`는 managed install surface를 만든다: `~/.codex/plugins/charness`, `~/.agents/plugins/marketplace.json`, `~/.local/bin/charness`, optional `~/.local/bin/claude-charness`, plus Claude user-scope marketplace/plugin install.
- `./charness init`는 Codex CLI가 있는 머신에서는 official app-server `plugin/install`도 바로 시도한다. 따라서 zero-state init의 happy path는 source export에 멈추지 않고 `~/.codex/config.toml` / `~/.codex/plugins/cache/...` install marker까지 포함한다. Codex CLI가 없는 머신에서는 `doctor`가 `host-unavailable`로 정직하게 보고한다.
- official installed CLI source는 이제 managed checkout `~/.agents/src/charness`만 허용한다. repo 밖에서 쓰는 `charness`는 `~/.local/state/charness/install-state.json`을 통해 그 managed checkout을 기억한다. non-managed `--repo-root`는 proof/development path로만 남고 `--skip-cli-install`이 필요하다.
- `charness tool doctor|install|update|sync-support`가 추가됐다. external integration lifecycle는 thin CLI에서 직접 호출할 수 있고, 결과는 `integrations/locks/*.json`, repo-local `skills/support/generated/` symlink, user cache support materialization에 agent-readable state로 남는다.
- tool control-plane은 GitHub latest-release probe도 포함한다. `specdown`은 실제 latest release `v0.47.2`를 잡았고, `cautilus`도 현재 GitHub latest-release endpoint에서 `v0.2.3`을 잡는다.
- tool control-plane은 이제 install provenance도 lock/doctor output에 남긴다. `gws-cli`처럼 실제 설치 경로가 `npm`으로 판별되면 `charness tool update --dry-run`이 `npm install -g @googleworkspace/cli@latest` 같은 package-manager route로 승격된다. `specdown`처럼 provenance가 plain `path`면 release metadata를 붙인 manual guidance로 남는다.
- public skill `create-cli`가 추가됐다. repo-owned CLI를 만들거나 손볼 때 command surface, install/update UX, machine-readable state, quality gate를 한 묶음으로 다루는 기본 참고 skill이다.
- machine-local capability resolution seam이 추가됐다. `charness capability resolve|doctor|env`는 `~/.config/charness/capability-profiles.json`과 `~/.config/charness/repo-bindings.json`을 읽어 repo-local logical capability를 machine-local profile과 provider manifest/support capability로 연결한다.
- capability first-use 온보딩도 추가됐다. `charness capability init`가 machine-local scaffold를 만들고, `charness capability explain <skill-id>`가 public skill별 logical capability expectation을 보여준다.
- `announcement` adapter는 이제 `delivery_capability`를 받을 수 있다. `delivery_kind: human-backend`일 때 reusable private backend access는 token path 대신 logical capability id로 연결한다.
- installed CLI machine-local state는 이제 `~/.local/state/charness/` 아래에 모인다. `install-state.json`, `host-state.json`, `version-state.json`이 여기로 이동했고, capability config는 state가 아니라 config layer에 남긴다.
- `create-cli` references는 `cautilus` 배포 메모를 반영해 release-first install contract, installer가 OS package manager를 직접 만지지 않는 원칙, provenance-aware update routing을 기본 guidance로 포함한다.
- checked-in plugin export는 더 이상 machine-local `integrations/locks/*.json`를 복사하지 않는다. export surface에는 `lock.schema.json`, `README.md`, `.gitkeep`만 남는다.
- `.githooks/pre-push`는 이제 `sync_root_plugin_manifests.py`를 먼저 돌리고, `plugins/charness` 또는 root marketplace artifacts에 drift가 생기면 push를 막은 뒤에만 `./scripts/run-quality.sh`를 실행한다.
- `.agents/skills`는 checked-in 기본 install surface가 아니다. 이 repo는 thin CLI가 관리하는 `~/.codex/plugins/charness` source plugin root와 `~/.agents/plugins/marketplace.json`를 operator install anchor로 쓰고, source checkout public skills를 별도 symlink로 노출하지 않는다.
- `INSTALL.md`, `README.md`, `UNINSTALL.md`, `docs/host-packaging.md`, `docs/operator-acceptance.md`는 marketplace 설치를 primary path에서 내리고 thin CLI managed install을 공식 경로로 설명하도록 갱신했다.
- `skills/public/release/*`와 `scripts/plugin_preamble.py`도 `charness update` / Claude restart 기준으로 갱신했다.
- `scripts/run-evals.py`에서는 historical current-repo smokes를 줄였다. `managed-cli-install`, `packaging-valid`, `packaging-export`는 더 직접적인 standing CLI tests/validators가 같은 seam을 이미 증명하므로 제거됐고, 남은 eval은 bootstrap/adapter/portability contract 위주로 유지한다.
- 2026-04-14 closeout에서는 `quality` `#10`, `#13`, `#14`, `#6` source-of-truth 변경, dogfood artifact 갱신, checked-in plugin export sync, 그리고 [`skills/public/find-skills/scripts/list_capabilities.py`](../skills/public/find-skills/scripts/list_capabilities.py) file-length gate fix까지 포함해 `./scripts/run-quality.sh`가 다시 초록으로 돌아왔다.
- `#14` 댓글에서 나온 non-blocking follow-up도 handoff에 남긴다: warn-band growth pressure, floor-lowering snapshot, specdown case-count floor는 아직 설계 note 상태다. 현 slice의 기준은 blind-spot policy/generalization을 landed로 만드는 것이었고, 이 세 항목은 future design slot로 남긴다.
- public skill authoring contract도 보강됐다. `AGENTS.md`와 `create-skill`은 이제 sparse real-person anchor를 `SKILL.md` core의 의도적 retrieval technique로 취급하되, 행동 규칙에 연결되고 사실충실해야 하며 selection logic은 core에, nuance와 payload는 `references/`에 두라고 명시한다.
- `ideation/spec/impl/handoff`는 Christopher Alexander-style sequence discipline을 core behavior로 갖고, `ideation`은 Saras Sarasvathy effectuation, `spec/impl`은 Kent Beck + John Ousterhout, `retro`는 named expert lens를 선호하되 direct counterfactual lens도 허용하는 쪽으로 정리됐다.
- `charness init`와 `charness update`는 이제 `~/.local/state/charness/host-state.json`에 post-command doctor snapshot을 남긴다. `charness doctor --write-state`로도 interactive restart 전후 proof snapshot을 수동 기록할 수 있다.
- installed `charness` CLI는 이제 `~/.local/state/charness/version-state.json`에 current version provenance와 cached latest-release check를 남긴다. `charness version --check`가 explicit refresh surface고, interactive installed-CLI runs는 24시간 TTL cache를 써서 non-fatal update notice를 낼 수 있다.
- 다른 머신 Claude Code dogfood에서 standalone `charness` binary만으로 manual clone 없이 `charness init` / `charness update`가 성공했다. `~/.agents/src/charness`, `~/.codex/plugins/charness`, `~/.agents/plugins/marketplace.json`도 기대한 위치에 생겼고, Claude visibility는 실제로 확인됐다.
- `charness update`는 이제 installed CLI self-refresh도 실제로 수행한다. 이전에는 PATH의 installed CLI가 자기 자신을 다시 복사하려 해 stale binary가 남을 수 있었는데, 이제 managed checkout의 [`charness`](../charness)를 `~/.local/bin/charness`로 다시 설치한다. temp-home standalone proof에서 `doctor --write-state`와 update 후 CLI sentinel refresh를 다시 확인했다.
- `charness update`는 이제 enabled local Codex plugin refresh뿐 아니라 missing local install recovery에도 같은 official `codex app-server` `plugin/install` seam을 재사용한다. local temp-home smoke에서는 `init` first install과 `update` refresh 둘 다 current manifest version cache를 실제로 materialize하는 것까지 확인했다. 남은 질문은 interactive Codex session이 그 refreshed cache를 restart만으로 visible skills에 반영하는지다.
- `cautilus` integration도 installed CLI 기준 host-like temp-home proof가 늘었다. manual install guidance + latest-release metadata + `skills/support/generated/cautilus` materialization, 그리고 fake `cautilus` binary가 있을 때 `tool doctor`가 `doctor_status=ok` / `support_state=upstream-consumed`로 가는 것까지 자동 테스트로 확인한다.
- 주의: 이 머신에서는 `cautilus`가 Homebrew cellar에는 있었지만 brew bin dir가 current PATH에 없어 `doctor`/`command -v` 기준으로는 `missing`처럼 보였다. 즉 현재 tool detection/provenance는 PATH에 강하게 의존하고, non-PATH package-manager install visibility는 별도 follow-up 후보로 남는다.
- 같은 dogfood 보고서의 `charness doctor --write-state` 미지원은 최신 `main`을 pull하기 전 installed PATH binary로 실행했을 가능성이 높다. 이번 incident의 핵심 lesson은 "checkout version"과 "실제로 실행 중인 installed CLI capability"를 분리해서 봐야 한다는 점이다. 이 seam은 public docs보다 handoff/operator acceptance와 structured `update --json` proof에만 좁게 남겨 둔다.
- Retro 2026-04-12 #1: installed CLI update seam을 내가 늦게 잡은 이유는 source checkout과 managed checkout state는 계속 보고 있었지만, "old PATH binary가 update 뒤 새 checkout binary로 실제 교체되는가"를 별도 계약 seam으로 분리하지 않았기 때문이다. 앞으로 install/update 작업에서는 source checkout, managed checkout, installed PATH binary를 따로 검증하고, 새 플래그 추가 뒤에는 "이전 설치자 recovery"까지 명시적으로 확인해야 한다.
- Retro 2026-04-11 #3: `./charness init --repo-root /checkout`로 CLI를 설치해도 이후 `/home/ubuntu` 같은 repo 밖에서 `charness update`와 `charness doctor`를 실행할 수 있다고 착각했다. 실제로는 installed CLI가 managed checkout 기본값 `~/.agents/src/charness`만 찾았고, 그 경로가 없으면 `update`는 `missing source checkout`로 실패하고 `doctor`는 traceback을 냈다. 이제 CLI는 마지막 successful `init`/`update`의 source checkout을 `~/.local/state/charness/install-state.json`에 기억하고, source가 없을 때도 `doctor`가 `missing-source` guidance를 내도록 고쳤다.
- Claude local marketplace update dogfood는 끝났다. temp checkout에서 `0.0.1-update-test -> 0.0.2-update-test`로 버전을 올리고 `charness update`를 돌렸을 때 `~/.claude/plugins/cache/corca-charness-update-test/charness/...` install path와 installed version이 같이 올라갔다.
- 이 머신의 Codex는 이제 실제 host install 상태다. `~/.codex/config.toml`에는 `[plugins."charness@local"] enabled = true`가 있고, cache manifest는 `~/.codex/plugins/cache/local/charness/local/.codex-plugin/plugin.json`에 생긴다.
- Retro 2026-04-11 #2: Codex host install이 끝난 뒤에도 source plugin root만 새 버전으로 덮어쓰고 `codex exec`를 새 프로세스로 띄우는 것만으로는 cache manifest version이 바뀌지 않았다. source는 `0.0.3-codex-test`로 올라갔지만 cache는 `0.0.0-dev`에 남았고, 원복 뒤에도 cache는 그대로였다. 즉 현재 증거로는 `charness update` + restart만으로 Codex installed cache가 자동 갱신된다고 말할 수 없다.
- control-plane principle도 정리됐다. manual-only tool install/update라도 CLI 출력과 lock state에 다음 operator step이 남아야 하고, support sync는 가능하면 generated artifact를 남긴다.

## Next Session

0. support-tool follow-up을 이어갈 때는 [docs/support-tool-followup.md](support-tool-followup.md)를 먼저 읽고, 여기서 정한 issue triage와 dogfood acceptance를 그대로 따른다. 특히 `create-cli`, `quality`, `find-skills`/recommendation flow 변경은 모두 skill 수정 + `charness` repo dogfood까지 한 slice로 묶는다.
   - `quality` `#10`, `#13`, `#14`, `#6`, recommendation/install payload의 `quality` 재사용, `init-repo` `#11`, `impl` `#8`, `#7`, `handoff` `#15`는 landed 상태다. open public-skill follow-up으로는 `retro` `#16`이 있고, support-tool-adjacent slice로는 verifier-selection helper / changed-surface-to-validator mapper가 남아 있다.
1. 실제 interactive Codex에서 clean installed baseline을 유지한 채 upstream skill/plugin payload를 의도적으로 바꾼 뒤 `charness update`가 refreshed cache를 visible skill surface까지 언제 반영하는지 확인한다. 다음 proof는 `update-only + restart-only -> Plugin Directory re-enable -> Plugin Directory reinstall` 순서로 최소 필요 refresh step을 분리 기록해야 한다.
   - 가능하면 update 전 `charness doctor --write-state` snapshot과, restart/re-enable/reinstall 각 단계 뒤 새 snapshot을 비교해 proof를 남긴다. visible skill delta가 가장 판정이 쉬우면 임시 probe skill 추가/제거를 사용해도 된다.
2. 새 `charness tool install/update/doctor` surface를 실제 다른 머신 또는 temp-home workflow로 한 번 더 dogfood한다. 특히 provenance-aware route가 있는 tool(`gws-cli`, brew-installed `specdown`, brew-installed `gh`)과 manual-only tool(`cautilus`, release-installed `specdown`)에서 남는 lock/install guidance shape를 점검한다.
   - temp-home 자동 proof는 이제 installed CLI 기준 `cautilus` support sync + doctor ok까지 포함한다. 남은 인간 proof는 실제 다른 머신에서 real `cautilus` binary install/update 경로와 generated support surface가 함께 맞는지 보는 것이다.
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
- [docs/capability-resolution.md](capability-resolution.md)
- [packaging/charness.json](../packaging/charness.json)
- [plugins/charness/.claude-plugin/plugin.json](../plugins/charness/.claude-plugin/plugin.json)
- [plugins/charness/.codex-plugin/plugin.json](../plugins/charness/.codex-plugin/plugin.json)
- [.claude-plugin/marketplace.json](../.claude-plugin/marketplace.json)
- [.agents/plugins/marketplace.json](../.agents/plugins/marketplace.json)
- [skills/public/init-repo/SKILL.md](../skills/public/init-repo/SKILL.md)
- [skills/public/release/SKILL.md](../skills/public/release/SKILL.md)
- [skills/public/narrative/SKILL.md](../skills/public/narrative/SKILL.md)

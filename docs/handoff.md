# charness Handoff

## Workflow Trigger

- 다음 세션이 artifact output policy, skill adapter contract, plugin export, 또는 checked-in artifact 경로를 이어받는다면 이 handoff부터 읽는다.
- 반복 실수 방지는 [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를 함께 읽는다.

## Current State

- Public artifacts는 `charness-artifacts/<skill>/`, hidden runtime state는 `.charness/<skill>/`를 쓴다. 일반 current pointer는 `latest.md`, durable record는 `YYYY-MM-DD-<slug>.md` 규칙이고 [`docs/handoff.md`](./handoff.md)만 rolling canonical 예외다.
- [`AGENTS.md`](../AGENTS.md) now requires one `charness:find-skills` call at the start of each
  task-oriented session so the session begins with a current capability map of
  public skills, support skills, synced support surfaces, and integrations.
- `find-skills` now actually persists that capability map to
  [`charness-artifacts/find-skills/latest.md`](../charness-artifacts/find-skills/latest.md) and `latest.json`; unchanged
  inventories keep the previous generated timestamp instead of rewriting the
  current pointer on every run.
- 현재 quality gate는 aggregate `60.0%` + per-file `85.0%` coverage floor, test/source ratio 상한 `1.00`, recent-median runtime budget(`pytest` 40s, `check-secrets` 5s, `check-coverage` 15s, `run-evals` 5s, `specdown` 8s)을 enforce한다.
- 가장 최근 review proof 기준 control-plane coverage는 `98.0%` (`1196/1221`), test/source ratio는 `0.54` (`11279/20721`), standing pytest는 `321 passed`, eval은 `19` scenario pass, review gate는 `38 passed, 0 failed, 50.3s`다.
- `run-quality.sh`는 `specdown run -quiet -no-report`를 포함하고, `.githooks/pre-push`는 export sync 뒤 canonical quality gate를 강제한다.
- `charness task`는 작업 리포의 `.charness/tasks/*.json`에 claim/submit/abort/status를 남긴다. 이 리포의 runtime state에는 `sah-task-envelope`와 `doctor-next-action` record가 있어 `charness task status <task-id>`로 이어받을 수 있다.
- `charness update`와 `charness update all`은 이제 기본 stdout에서 long JSON 대신 human summary를 내고, full payload는 `--json` opt-in일 때만 stdout으로 내보낸다. 진행 visibility가 필요한 phase line은 human mode에서는 stdout, JSON mode에서는 stderr로 보낸다.
- Checked-in plugin export는 source 변경 뒤 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 맞춘다.
- `.claude/worktrees/`는 host-generated runtime 흔적으로 보고 `.gitignore`에서 무시한다. `.claude/*.yaml` 같은 repo-owned adapter/config 후보까지 통째로 숨기지는 않는다.
- [`docs/public-skill-dogfood.json`](./public-skill-dogfood.json)는 현재 17개 public skill 전체를 커버하는 reviewed consumer dogfood registry다.
- Packaging/plugin release surface는 checked-in version surface를 source of truth로 본다. 다음 publish slice도 `python3 skills/public/release/scripts/current_release.py --repo-root .`로 현재 버전을 먼저 읽고, 실제 release boundary는 `python3 skills/public/release/scripts/publish_release.py --repo-root . --part <patch|minor|major> --execute` helper로 닫는다.
- 2026-04-18 UTC release surface is now `0.4.0`, and GitHub release `v0.4.0` is live. The release helper also now creates the tag before pushing and uses one `git push <remote> <branch> <tag>` transaction, so pre-push quality should no longer rerun just because branch and tag were pushed separately.
- `#33`/`#34` 방향의 public spec boundary 정리는 반영됐다. `spec`은 public executable contract vs implementation guard를 명시하고, `quality`는 proof layering inventory plus actionable `move_down` / `delete_or_merge` / `keep_if_integration_value` recommendation payload를 갖는다.
- `quality` public skill은 이번 slice에서 structure-first routing을 더 명시했다. 길이/중복/pressure signal은 기본적으로 concept-review advisory로 보고, explicit low-noise invariant와 clear structural response가 있을 때만 `AUTO_CANDIDATE`/`AUTO_EXISTING`로 올린다. 이 caution은 coverage floor나 runtime budget 같은 standing threshold gate까지 일반화하지 않는다.
- 2026-04-17 quality review 기준 남은 advisory pressure는 [`AGENTS.md`](../AGENTS.md)/[`README.md`](../README.md)/[`UNINSTALL.md`](../UNINSTALL.md) entrypoint ergonomics, `init-repo`/`retro`/`spec`의 mode-pressure wording, 그리고 `quality` SKILL core의 `long_core`다.
- `#35`의 첫 구현 뒤 hardening도 들어갔다. `render_markdown_preview.py`는 unsupported `backend`를 upfront reject하고, manifest에 `backend_version`, `git_head`, per-file `source_sha256`를 남긴다. repo-local scope는 [`.agents/markdown-preview.yaml`](../.agents/markdown-preview.yaml) 같은 config search path로 열어뒀고, 현재 이 repo에는 scaffolded config가 checked in 되어 있다. preview output은 `.artifacts/markdown-preview/` 아래 machine-local runtime artifact로 본다. 2026-04-17 현재 `glow`는 `charness tool install --repo-root . glow`로 로컬 설치 완료됐고, preview helper는 `backend: glow` rendered artifact를 생성한다.
- `premortem` public skill contract은 이제 canonical subagent path를 요구한다. host가 subagent를 못 주면 같은-agent 로컬 패스로 약화하지 말고 canonical path unavailable로 stop해야 한다.
- `quality`의 fresh-eye premortem reference도 같은 방향으로 맞췄다. explicit subagent allowance가 없으면 same-agent local fallback을 equivalent로 취급하지 않는다.
- 2026-04-18 기준 `cautilus` latest release는 `v0.5.5`이고 로컬 설치본도 `0.5.5`다. `instruction-surface evaluate`는 `cautilus.instruction_surface_inputs.v1` 입력을 받아 `cautilus.instruction_surface_summary.v1`를 정상 출력한다.
- `charness` now ships checked-in instruction-surface wiring for `cautilus`: [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml), [evals/cautilus/instruction-surface-cases.json](../evals/cautilus/instruction-surface-cases.json), and [scripts/agent-runtime/run-local-instruction-surface-test.mjs](../scripts/agent-runtime/run-local-instruction-surface-test.mjs) plus its support helpers are all present.
- 2026-04-18 UTC `Cautilus v0.5.5` 검증은 green이다. `cautilus instruction-surface test --repo-root .`가 `recommendation=accept-now`로 끝났고, checked-in bootstrap case는 이제 `bootstrapHelper=find-skills`, `workSkill=impl` expectation으로 통과한다. compact no-bootstrap implementation은 `impl`, contract-shaping은 `spec`으로 유지된다.
- `python3 scripts/run-evals.py --repo-root .`도 `v0.5.5`에서 20 scenario pass다. 즉 기존 maintained consumer path는 released binary에서 regression 없이 유지되고, `find-skills -> impl` false mismatch도 사라졌다.
- Prompt-affecting repo changes now have a checked-in closeout rule: [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md) is the current visible proof artifact, [scripts/validate-cautilus-proof.py](../scripts/validate-cautilus-proof.py) enforces that prompt-affecting slices refresh it, and [`./scripts/run-quality.sh`](../scripts/run-quality.sh) now includes `validate-cautilus-proof`.
- 2026-04-18 UTC A/B smoke: `cautilus workspace prepare-compare --repo-root . --baseline-ref HEAD~1 --output-dir /tmp/cautilus-compare-smoke` prepared baseline/candidate worktrees successfully. `cautilus mode evaluate` also ran with that compare setup, but current adapter command templates still consume `baseline_ref` rather than directly using the prepared baseline/candidate repos, so the compare workspace path is proven as operator workflow but not yet a deeper charness adapter contract.
- `find-skills` now supports a direct validation/runtime recommendation query via `list_capabilities.py --recommendation-role <runtime|validation> --next-skill-id <skill-id>`, and the `cautilus` integration manifest now limits `supports_public_skills` to the checked validation routes `impl`, `quality`, and `spec`.
- `public-skill-validation` policy is now explicit that deeper skill-contract meaning belongs to on-demand `cautilus`/HITL proof, while repo-owned standing gates stay deterministic. `premortem` remains `hitl-recommended` + `adapter-free`, not a standing evaluator-required skill.
- `specdown` now has an explicit second role as a viewer for the latest checked on-demand validation artifacts. Public executable contract pages remain the SoT for reader-facing contract claims, but checked artifacts such as [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md) stay the source of truth for on-demand runs.
- `charness` now also ships a named `cautilus` adapter for long-context conversation proposal generation: [.agents/cautilus-adapters/chatbot-proposals.yaml](../.agents/cautilus-adapters/chatbot-proposals.yaml) runs [scripts/eval_cautilus_chatbot_proposals.py](../scripts/eval_cautilus_chatbot_proposals.py) against [evals/cautilus/chatbot-scenario-proposal-inputs.json](../evals/cautilus/chatbot-scenario-proposal-inputs.json) and writes the current pointer to [charness-artifacts/cautilus/chatbot-proposals/latest.md](../charness-artifacts/cautilus/chatbot-proposals/latest.md). This is the first repo-owned seam for multi-turn skill-trigger proposal generation; it is not yet a compare-backed benchmark.
- 2026-04-18 UTC packet expansion widened that long-context proposal surface from 4 to 11 checked-in follow-up patterns. The packet now covers `retro`, `quality`, `premortem`, `find-skills`, `handoff`, `init-repo`, `narrative`, `spec`, `debug`, `release`, and `hitl` boundary corrections as proposal-mining inputs.
- Current `cautilus scenario propose` behavior appears to emit only the top `5` proposals by default even when the checked-in packet carries more candidates. The repo-owned runner now records both `candidate_keys` and `omitted_candidate_keys` so breadth is still visible in the checked current pointer.
- `charness` now also ships a compare-backed named adapter at [.agents/cautilus-adapters/chatbot-benchmark.yaml](../.agents/cautilus-adapters/chatbot-benchmark.yaml). It compares baseline and candidate worktrees via [scripts/eval_cautilus_chatbot_compare.py](../scripts/eval_cautilus_chatbot_compare.py) and writes the current pointer to [charness-artifacts/cautilus/chatbot-benchmark/latest.md](../charness-artifacts/cautilus/chatbot-benchmark/latest.md). This surface is the first honest A/B benchmark for the long-context proposal packet.
- The newest benchmark slice shows the current top-five cap now favoring `hitl`, `release`, `debug`, `spec`, and `narrative`; `find-skills`, `handoff`, and `init-repo` remain in the checked packet but are currently omitted by product ranking.
- `gather` now has an explicit browser-mediated private SaaS contract. The public skill and references now require official API/export first, then `agent-browser` fallback, and name first-class auth/bootstrap plus remote/headless degradation honestly. The `agent-browser` integration manifest now advertises `gather` runtime support, and the `find-skills` current pointer updated accordingly.

## Next Session

1. `git status --short`를 먼저 확인한다.
2. public-spec executable proof 약점은 이번 slice에서 정리됐다. `inventory_public_spec_quality.py`는 실제 `run:shell` fence를 읽고, [`specs/index.spec.md`](../specs/index.spec.md)/[`specs/tool-doctor.spec.md`](../specs/tool-doctor.spec.md)는 direct CLI proof로 바뀌어 현재 flagged spec이 없다.
3. release를 이어받는 다음 세션은 먼저 `python3 skills/public/release/scripts/current_release.py --repo-root .`로 checked-in version surface를 확인하고, 새 publish slice라면 `publish_release.py` helper를 기본 경로로 쓴다. bump만 하고 push-only 상태에서 멈추지 않는다.
4. 다음 pickup의 first move는 `gather`를 long-context packet에 넣는 것이다. [charness#40](https://github.com/corca-ai/charness/issues/40) blocker는 이미 닫혔다.
5. `markdown-preview`는 helper-only 상태가 아니다. `quality`에는 bootstrap/execute seam이 이미 있고, `narrative` docs도 rendered Markdown review를 workflow seam으로 언급한다. 현재 판단으로는 `announcement` explicit 연결은 우선순위가 낮고, 정말 남은 질문은 `docs:preview`류 별도 command surface가 실제 필요한지다.
6. CLI UX follow-up을 이어가면 `update`에 맞춘 human-first default / `--json` opt-in / stderr progress pattern을 `init` 같은 나머지 long-running lifecycle commands에도 확대할지 판단한다. 이번 slice는 `update`와 `update all`만 바꿨다.
7. Agent Harness Guide adaptation을 이어가면 [charness-artifacts/spec/agent-harness-guide-adaptation.md](../charness-artifacts/spec/agent-harness-guide-adaptation.md)를 읽고 `Slice 1`부터 시작한다. 첫 범위는 [`docs/harness-composition.md`](./harness-composition.md), [`docs/artifact-policy.md`](./artifact-policy.md), 최소 handoff cross-link다.
8. Dogfood 개선은 registry 확장보다 reviewed case 강화가 다음 move다. `hitl` 또는 `ideation`처럼 policy-heavy한 case 하나를 골라 실제 consumer prompt replay와 stronger acceptance evidence를 추가한다.
9. sah/specdown lesson line을 이어가면 task envelope와 doctor `next_action`을 실제 멀티에이전트 세션에서 dogfood한 뒤 필요하면 task list/status summary만 다듬는다. 반복 setup/JSON 추출이 두세 번 생기기 전에는 specdown adapter를 만들지 않는다.
10. source가 checked-in plugin export에 들어가는 파일이면 focused managed-checkout 테스트 전에 export sync를 먼저 실행한다. 이번 slice에서도 [`plugins/charness/README.md`](../plugins/charness/README.md) drift가 packaging/managed-install pytest를 바로 깨뜨렸으니, root README 계열 변경 뒤에는 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`를 먼저 습관화한다.
11. long-context skill-trigger work를 이어가면 `cautilus adapter resolve --repo-root . --adapter-name chatbot-proposals`와 `python3 scripts/eval_cautilus_chatbot_proposals.py --repo-root . --json`부터 시작한다. proposal-mining surface와 compare/A/B benchmark surface는 이제 둘 다 checked-in 상태다.
12. 다음 long-context 후보 확장은 이제 `gather`다. 새 contract가 landed 했으니, private SaaS browser-fallback correction pattern을 checked-in packet으로 승격하면 된다.
13. `gather` scenario는 single-point route test보다 correction-heavy arc로 쓰는 게 맞다. 최소한 아래 세 포인트를 한 시나리오 안에서 잡는다:
    `owner guidance에서 너무 일찍 멈추지 말 것`
    `official API/export를 browser보다 먼저 볼 것`
    `browser fallback은 honest하게 허용하되 auth/bootstrap이 없으면 clean stop할 것`
14. `gather` scenario wording은 `find-skills`와 흔들리지 않게 source URL 또는 clear acquisition intent를 prompt에 넣는 편이 낫다. capability discovery처럼만 보이면 `find-skills`로 오염될 수 있다.
15. benchmark를 다시 생성할 때는 `cautilus workspace prepare-compare --repo-root . --baseline-ref <ref> --output-dir <tmp>` 또는 `git worktree add --detach <tmp> <ref>`로 baseline을 준비한 뒤, `python3 scripts/eval_cautilus_chatbot_compare.py --repo-root . --baseline-repo <baseline> --candidate-repo <candidate> --output-dir charness-artifacts/cautilus/chatbot-benchmark`를 실행한다.

## Discuss

- stale artifact를 언제 삭제/아카이브할지, 아니면 `superseded_by` frontmatter만 도입할지 아직 정책으로 잠그지 않았다.
- singleton 성격이 강한 스킬도 dated record를 항상 남길지, 일부는 current pointer만 둘지는 dogfood 후 다시 본다.
- `find-skills/latest.md`와 `latest.json`는 현재 판단으로 hidden runtime state가 아니라 semi-fixed dogfood/current-pointer evidence로 유지하는 편이 맞다. 이 repo 자체가 charness skill surface를 소비하므로, current capability inventory를 checked-in visible artifact로 두는 편이 더 honest하다.

## References

- [AGENTS.md](../AGENTS.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [public-skill-dogfood.md](./public-skill-dogfood.md)

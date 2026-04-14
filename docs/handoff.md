# charness Handoff

## Workflow Trigger

- 다음 세션이 support-tool / external tool follow-up이면 먼저
  [docs/support-tool-followup.md](support-tool-followup.md)를 읽는다.
  `#10`, `#11`, `#13`, `#14`, `#6`, `#7`, `#8`, `#15`, `#16`, `#17`,
  `#18`, `#19`, `#20`, `#21`, `#23`, `#22`는 landed 상태다.
- 최근 repeat trap은
  [skill-outputs/retro/recent-lessons.md](../skill-outputs/retro/recent-lessons.md)
  에 축약해 두므로, install/update/export/support work 전엔 handoff와 함께
  먼저 훑는다.
- verification command 선택은 더 이상 wholly manual이 아니다.
  `python3 scripts/select_verifiers.py --repo-root .`가
  `.agents/surfaces.json`을 통해 changed-surface 기준 smallest verifier
  bundle을 고른다.
- `charness update` 이후 visible skill propagation proof는 완료됐다.
  standing gate가 아니라 on-demand regression만 유지한다.

## Current State

- `charness`는 thin CLI + checked-in plugin export + managed checkout 모델로
  정리됐다. primary operator path는 `charness init/update/reset/uninstall`이다.
- 열린 GitHub 이슈는 `#24` 하나다. 지금 구현은 directionally right지만
  close가 과했다. 다음 work는 이 이슈를 제대로 닫는 쪽이 가장 자연스럽다.
- support-tool control plane은 `tool doctor|install|update|sync-support`를
  제공하고, lock state / generated support / discovery stub / doctor
  next-step까지 agent-readable state를 남긴다.
- `find-skills`는 synced support skill과 external integration entry를
  cross-link한다. `cautilus`는 intent trigger, discovery stub,
  repo-followup command까지 연결돼 있다.
- `narrative`, `find-skills`, `announcement` bootstrap은 richer truth
  surface, first-run artifact path, does-not-do boundary를 더 직접 말한다.
- `retro` self-improvement의 첫 배치는 landed 상태다.
  `probe_host_logs.py`, `refresh_recent_lessons.py`,
  `seed_retro_memory.py`, `persist_retro_artifact.py`까지 있다.
- `quality`는 skill ergonomics와 CLI ergonomics smells를 advisory inventory로
  본다. `inventory_skill_ergonomics.py`, `inventory_cli_ergonomics.py`가 있다.
- `narrative`는 이제 multi-use-case repo에서 scenario block guidance를
  explicit하게 가진다. `scenario_surfaces` / `scenario_block_template` adapter
  fields를 지원하고, main use-case docs에서 fixture-first scenario cards와
  coined-jargon first-use inline definition을 유도한다.
- `retro`는 이제 configured repeat-trap seam에서 bounded auto-trigger를
  지원한다. `check_auto_trigger.py`가 adapter의
  `auto_session_trigger_surfaces` / `auto_session_trigger_path_globs`를 읽고,
  `impl` / `retro`는 그 결과를 짧은 session retro trigger로 사용한다.
- `release`는 이제 release-time real-host proof를 별도 seam으로 다룬다.
  `check_real_host_proof.py`가 changed surface를 보고 human-run checklist가
  필요한지 판정하고, charness는 `cautilus` install/doctor/sync-support smoke를
  adapter-owned checklist로 들고 간다.
- `spec`는 이제 core에서 `premortem` 용어를 직접 쓰고, bounded fresh-eye
  review를 요구한다.
- `premortem`은 이제 standalone public skill이다. angle selection,
  counterweight triage, `Deliberately Not Doing` memory를 one seam으로
  가져간다.
- `spec`와 `narrative`는 이제 rejected alternatives를 durable doc에 남기는
  쪽으로 정리됐다. `quality`는 dual-implementation parity를 weak heuristic +
  explicit human review lens로 본다.
- 다만 `#24`는 아직 fully done이 아니다. 남은 gap은:
  `premortem`의 counterweight pass가 실제 reusable subroutine으로 caller
  skill들에 더 분명히 연결되지 않았고, quality parity도 아직 weak heuristic
  이상으로는 못 간다.
- hidden support source-of-truth도 넓어졌다.
  `skills/support/specdown/`, `skills/support/agent-browser/`는 이제
  authoritative tree에 포함된다.
- 현재 standing concern은 install/update propagation이 아니라
  `quality`가 skill ergonomics를 얼마나 explicit하게 review contract로
  올릴지다. 자세한 구현 계약은
  [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)에
  있다.
- 최신 weekly retro와 compact lesson digest는
  [skill-outputs/retro/weekly-2026-04-14.md](../skill-outputs/retro/weekly-2026-04-14.md),
  [skill-outputs/retro/recent-lessons.md](../skill-outputs/retro/recent-lessons.md)에
  갱신돼 있다. 이번 세션의 핵심 교훈은 multi-surface sequencing miss를 더
  일찍 막는 것이다.

## Next Session

1. 먼저
   [skill-outputs/retro/recent-lessons.md](../skill-outputs/retro/recent-lessons.md)를
   읽고, omission-prone seam을 먼저 체크한다. 특히 new public skill 추가 시
   `docs/public-skill-validation.json`과 checked-in plugin export sync를 함께
   본다.
2. 가장 자연스러운 다음 작업은 `#24`를 실제로 마무리하는 일이다.
   `premortem` counterweight prompt/template 구체화,
   `impl`/`release`가 standalone `premortem`을 더 명시적으로 invoke하게 만들기,
   quality parity detection의 honest-but-stronger contract 찾기가 남아 있다.
3. 그 다음 follow-on으로는 public-skill policy omission을 더 일찍 잡는
   guard를 추가하는 일이 좋다.
   예: `run-slice-closeout.py` / `select_verifiers.py`가
   `docs/public-skill-validation.json`을 explicit surface로 다루게 하거나,
   새 public skill이 validation partition에 빠지면 더 빨리 실패시키는
   narrower check.
4. support-tool dogfood를 이어간다면 새 `tool doctor/install/sync-support`
   surface를 다른 머신에서 한 번 더 확인한다. 특히 real binary install이
   PATH/non-PATH일 때 next-step honesty가 유지되는지 본다.
5. `quality` ergonomics를 advisory에서 stronger gate로 올릴지 다시 결정한다.
6. 추가 retro를 남길 때는 ad hoc 파일 쓰기 대신
   `skills/public/retro/scripts/persist_retro_artifact.py`를 사용한다.

## Discuss

- `#24`는 reopened 상태다. directionally right한 첫 slice는 landed지만,
  counterweight reusable step과 caller-skill integration은 아직 부족하다.
- ideal flow는 prose가 초반 행동을 좋게 유도하고 deterministic gate가
  omission/drift를 backstop하는 구조다. 지금 charness는 그 방향이지만, 몇몇
  omission-prone seam은 아직 broad gate에서 늦게 드러난다.

## References

- [docs/support-tool-followup.md](support-tool-followup.md)
- [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)
- [skill-outputs/retro/recent-lessons.md](../skill-outputs/retro/recent-lessons.md)

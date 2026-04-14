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
- 열린 GitHub 이슈는 `#24` 하나다. skill body 기준 남아 있던 contract gap은
  이번 세션에서 좁혔다. `premortem` caller contract, `impl`/`release`의
  standalone invocation, `quality`의 stronger parity triage를 정리했다.
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
  보지만, lowest-noise ergonomics 일부는 standing gate로 승격되기 시작했다.
  `inventory_skill_ergonomics.py`, `inventory_cli_ergonomics.py`가 있고,
  `validate-skills.py`는 oversized core와 public skill의 repeated fenced
  ritual without scripts를 막는다.
- higher-noise ergonomics는 repo-wide default gate로 올리지 않았다.
  대신 quality adapter의 `skill_ergonomics_gate_rules` opt-in seam과
  `validate_skill_ergonomics.py`를 추가해, repo가 원할 때만
  `mode_option_pressure_terms` 같은 규칙을 fail-closed 할 수 있게 했다.
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
- `#24`의 핵심 contract gap은 이제 skill body에서 닫혔다.
  `premortem`은 caller-consumable four-bin triage를 explicit하게 정의하고,
  `impl`/`release`는 standalone invocation을 명시하며, `quality`는
  dual-implementation을 parity harness / canonicalization / intentional
  divergence 중 하나로 triage하도록 요구한다.
- hidden support source-of-truth도 넓어졌다.
  `skills/support/specdown/`, `skills/support/agent-browser/`는 이제
  authoritative tree에 포함된다.
- 현재 standing concern은 install/update propagation이 아니라
  `quality` ergonomics에서 무엇을 standing gate로 더 올릴지와, public-skill policy
  omission을 지금의 direct fail message 이상으로 더 구조적으로 좁힐지다. 자세한 구현 계약은
  [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)에 있다.
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
2. `select_verifiers.py` / `run-slice-closeout.py`는 이제
   `docs/public-skill-validation.json`과 `skills/public/**`에서
   `validate-public-skill-validation.py`를 바로 고르고,
   `validate-public-skill-validation.py`는 누락 skill을 어느 bucket에 넣어야
   하는지 직접 말한다. 다음 로컬 follow-on은 public-skill omission을
   helper/autofix 수준으로 더 기계화할지 결정하는 일이다.
3. support-tool dogfood를 이어간다면 새 `tool doctor/install/sync-support`
   surface를 다른 머신에서 한 번 더 확인한다. 특히 real binary install이
   PATH/non-PATH일 때 next-step honesty가 유지되는지 본다.
4. ergonomics follow-on의 가장 자연스러운 후보는
   `skill_ergonomics_gate_rules`에 둘 다음 opt-in rule을 고르는 일이다.
   현재는 `mode_option_pressure_terms`만 지원하고, trigger overlap은 여전히
   advisory다.
5. 추가 retro를 남길 때는 ad hoc 파일 쓰기 대신
   `skills/public/retro/scripts/persist_retro_artifact.py`를 사용한다.

## Discuss

- `#24`는 reopened 상태지만, repo-local skill contract 기준으로는 핵심
  follow-up이 landed했다. 남은 일은 issue close 자체보다 public-skill
  omission을 helper/autofix 수준으로 더 기계화할지와,
  `skill_ergonomics_gate_rules`에 둘 다음 opt-in rule을 정하는 일이다.
- ideal flow는 prose가 초반 행동을 좋게 유도하고 deterministic gate가
  omission/drift를 backstop하는 구조다. 지금 charness는 그 방향이지만, 몇몇
  omission-prone seam은 아직 broad gate에서 늦게 드러난다.

## References

- [docs/support-tool-followup.md](support-tool-followup.md)
- [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)
- [skill-outputs/retro/recent-lessons.md](../skill-outputs/retro/recent-lessons.md)

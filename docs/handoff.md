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
- `#24`는 repo-local contract 기준으로 닫혔다. `premortem` caller contract,
  `impl`/`release`의 standalone invocation, `quality`의 stronger parity
  triage, public-skill omission helper, opt-in ergonomics gate seam까지
  landed했다.
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
  Bootstrap ritual without scripts를 막는다.
- higher-noise ergonomics는 repo-wide default gate로 올리지 않았다.
  대신 quality adapter의 `skill_ergonomics_gate_rules` opt-in seam과
  `validate_skill_ergonomics.py`를 추가해, repo가 원할 때만
  `mode_option_pressure_terms`, `progressive_disclosure_risk` 같은 규칙을
  fail-closed 할 수 있게 했다.
  canonical quality path는 이제 root wrapper
  `scripts/validate-skill-ergonomics.py`를 통해 이 opt-in gate를 함께 돈다.
  invalid `skill_ergonomics_gate_rules`는 bootstrap이 더 이상 조용히 `[]`로
  되돌리지 않고, adapter repair를 요구하며 멈춘다.
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
- 현재 standing concern은 install/update propagation이 아니라
  trigger overlap처럼 higher-noise ergonomics를 계속 advisory로 둘지와,
  support-tool real-host dogfood cadence를 얼마나 자주 가져갈지다.

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
   하는지 직접 말한다. `scripts/suggest-public-skill-validation.py`는
   missing skill별 bucket choice를 machine-readable helper로 준다.
   `validate-packaging.py`도 policy file이 있을 때 이 검사를 같이 수행하므로
   checked-in plugin export 경로에서도 drift가 늦게 빠지지 않는다.
3. support-tool dogfood를 이어간다면 새 `tool doctor/install/sync-support`
   surface를 다른 머신에서 한 번 더 확인한다. 특히 real binary install이
   PATH/non-PATH일 때 next-step honesty가 유지되는지 본다.
4. ergonomics follow-on은 trigger overlap 같은 higher-noise rule을 계속
   advisory로 둘지, 더 나은 opt-in heuristic이 생겼는지 다시 보는 일이다.
   현재는 `mode_option_pressure_terms`, `progressive_disclosure_risk`를
   지원하고, trigger overlap은 advisory다. fail-closed now vs advisory only는
   [skills/public/quality/references/skill-ergonomics.md](../skills/public/quality/references/skill-ergonomics.md)에
   분리해 뒀다.
5. 추가 retro를 남길 때는 ad hoc 파일 쓰기 대신
   `skills/public/retro/scripts/persist_retro_artifact.py`를 사용한다.

## Discuss

- `#24`는 closed-ready 상태였고, 이번 세션에서 helper/gate/dogfood까지
  묶어서 실제 close 기준으로 정리했다. 남은 일은 trigger overlap처럼
  higher-noise ergonomics를 계속 advisory로 둘지, support-tool real-host
  dogfood를 어느 cadence로 반복할지에 가깝다.
- public-skill validation tier는 현재 metadata/routing layer이지, skill별로
  서로 다른 standing CI mode가 이미 존재한다는 뜻은 아니다. maintained
  evaluator가 landed하기 전까지 `evaluator-required`도 smoke + targeted HITL로
  읽어야 한다.

## References

- [docs/support-tool-followup.md](support-tool-followup.md)
- [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)
- [skill-outputs/retro/recent-lessons.md](../skill-outputs/retro/recent-lessons.md)

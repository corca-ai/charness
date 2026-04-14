# charness Handoff

## Workflow Trigger

- 다음 세션이 support-tool / external tool follow-up이면 먼저
  [docs/support-tool-followup.md](support-tool-followup.md)를 읽는다.
  `#10`, `#11`, `#13`, `#14`, `#6`, `#7`, `#8`, `#15`, `#16`, `#17`,
  `#18`, `#19`, `#20`, `#21`은 landed 상태다.
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
- support-tool control plane은 `tool doctor|install|update|sync-support`를
  제공하고, lock state / generated support / discovery stub / doctor
  next-step까지 agent-readable state를 남긴다.
- `find-skills`는 synced support skill과 external integration entry를
  cross-link한다. `cautilus`는 intent trigger, discovery stub,
  repo-followup command까지 연결돼 있다.
- `narrative`, `find-skills`, `announcement` bootstrap은 richer truth
  surface, first-run artifact path, does-not-do boundary를 더 직접 말한다.
- `retro` self-improvement work는 지금 네 slice가 landed 상태다.
- `retro` self-improvement work의 첫 배치는 사실상 landed 상태다.
  - `probe_host_logs.py`: Claude/Codex local log metric availability probe
  - `refresh_recent_lessons.py`: durable retro -> recent-lessons digest refresh
  - `seed_retro_memory.py`: init-repo retro memory seam scaffold
  - `persist_retro_artifact.py`: durable retro write 시 digest 자동 refresh
- `quality`는 이제 skill ergonomics를 explicit lens로 본다.
  `inventory_skill_ergonomics.py`가 concise core / progressive disclosure /
  mode-pressure / prose-ritual risk를 advisory inventory로 surface한다.
- `quality`는 이제 CLI ergonomics smells도 advisory inventory로 본다.
  `inventory_cli_ergonomics.py`가 flat help-list와 cross-archetype schema
  leakage를 surface한다.
- `spec`는 이제 core에서 `premortem` 용어를 직접 쓰고, bounded fresh-eye
  review를 요구한다.
- hidden support source-of-truth도 넓어졌다.
  `skills/support/specdown/`, `skills/support/agent-browser/`는 이제
  authoritative tree에 포함된다.
- 현재 standing concern은 install/update propagation이 아니라
  `quality`가 skill ergonomics를 얼마나 explicit하게 review contract로
  올릴지다. 자세한 구현 계약은
  [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)에
  있다.

## Next Session

1. retro self-improvement follow-up을 이어간다면 먼저
   [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)를
   읽고, 다음 slice를 truly behavioral follow-on으로 고른다.
   예: ergonomics를 advisory에서 stronger gate로 올릴지, bounded
   post-closeout retro trigger를 둘지.
2. open issue follow-up을 이어간다면 `#22`부터 본다. `narrative`가
   multi-use-case repo에서 scenario-block template
   (`what you bring / input CLI / input for agent / what happens / what comes
   back / next action`)와 coined-jargon first-use guidance를 explicit하게
   다루게 하는 게 다음 자연스러운 slice다.
3. support-tool dogfood를 이어간다면 새 `tool doctor/install/sync-support`
   surface를 다른 머신에서 한 번 더 확인한다. 특히 real binary install이
   PATH/non-PATH일 때 next-step honesty가 유지되는지 본다.
4. 추가 retro를 남길 때는 ad hoc 파일 쓰기 대신
   `skills/public/retro/scripts/persist_retro_artifact.py`를 사용한다.

## Discuss

- `support-backed`와 `recommendation_role`은 같은 층위가 아니다.
  discoverability가 중요해도 모든 권장 tool이 support skill이어야 하는
  것은 아니다.
- Codex/Claude host-log metric은 asymmetric하다. Claude는 token count까지,
  Codex는 default local log 기준 duration/turn/tool-call까지만 현재 proof가
  있다.
- PATH에 없는 package-manager install은 여전히 follow-up seam이다.
  이 머신에서 `cautilus`는 brew cellar에는 있었지만 current PATH에 없어
  `doctor` 기준 `missing`처럼 보였다.

## References

- [AGENTS.md](../AGENTS.md)
- [README.md](../README.md)
- [INSTALL.md](../INSTALL.md)
- [UNINSTALL.md](../UNINSTALL.md)
- [charness](../charness)
- [docs/retro-self-improvement-spec.md](retro-self-improvement-spec.md)
- [docs/support-tool-followup.md](support-tool-followup.md)
- [docs/operator-acceptance.md](operator-acceptance.md)
- [docs/public-skill-validation.md](public-skill-validation.md)
- [skill-outputs/retro/recent-lessons.md](../skill-outputs/retro/recent-lessons.md)

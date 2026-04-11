# charness Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `impl`로 이어서, 먼저 [plugins/charness/.claude-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.claude-plugin/plugin.json), [plugins/charness/.codex-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.codex-plugin/plugin.json), [.claude-plugin/marketplace.json](/home/ubuntu/charness/.claude-plugin/marketplace.json), [.agents/plugins/marketplace.json](/home/ubuntu/charness/.agents/plugins/marketplace.json)을 읽고 shipped plugin surface가 현재 source of truth와 맞는지 다시 확인한다.
- 그다음 이 머신의 `~/.agents/skills` 아래 public skill symlink를 제거하고, checkout leakage 없이 정식 plugin install surface만 보이도록 만든 뒤 dogfood를 시작한다.
- Claude는 shared marketplace install 또는 `--plugin-dir` path에서 `plugins/charness`만 source로 보이게 하고 `/skills` discovery와 실제 skill runtime을 확인한다.
- Codex는 root marketplace가 가리키는 `./plugins/charness` 기준으로 discover/install visibility를 확인하고, 가능하면 same-checkout update model까지 본다.

## Current State

- `charness`는 portable Corca harness product로 정리됐고, public/support/profile/integration 경계는 현재 taxonomy 기준으로 고정됐다.
- public skill `narrative`가 추가돼 source-of-truth doc alignment와 audience-facing brief derivation이 `announcement`와 분리됐다.
- repo-owned release/install surface는 `plugins/charness` 아래 checked-in plugin bundle로 정리돼 있고, root marketplace files는 그 install surface만 advertise한다.
- Ceal-era migration surface는 정리됐다. tracked tree에는 `Ceal`, `interview`, `concept-review`, `test-improvement`, `entity-stage-design`, `workbench` 같은 legacy naming이 남아 있지 않다.
- [docs/master-plan.md](/home/ubuntu/charness/docs/master-plan.md)는 post-migration 기준의 현재 계획으로 다시 썼고, 옛 migration map은 삭제했다.
- 현재 tracked worktree는 clean이다.
- 마지막 검증은 `./scripts/run-quality.sh` 기준 `84 passed`, `Ran 16 eval scenario(s).`였다.

## Next Session

1. 현재 머신의 `~/.agents/skills`에서 `charness` public skill symlink가 남아 있는지 확인하고 제거한다.
2. Claude와 Codex가 source checkout이 아니라 shipped plugin bundle만 보도록 상태를 만든다.
3. Claude부터 dogfood한다.
   - 설치 surface가 `plugins/charness`인지 확인
   - `/skills`에 public skill만 보이는지 확인
   - `gather`, `narrative`, `release` 중 최소 1개 이상을 실제로 호출해 support/runtime seam까지 본다
4. Codex를 dogfood한다.
   - root `.agents/plugins/marketplace.json`이 `./plugins/charness`를 가리키는지 확인
   - plugin discovery 또는 install visibility를 본다
   - 가능하면 restart 후 same-checkout update model도 확인한다
5. formal install 결과를 바로 이 handoff나 별도 durable artifact에 남긴다.

## Discuss

- Codex의 실제 public install proof는 여전히 가장 불확실한 표면이다.
- Claude는 install/discovery proof가 더 앞서 있지만, 이제는 symlink leakage 없이 shipped surface만으로 다시 확인해야 한다.
- formal install dogfood에서 friction이 반복되면 그때 install/update helper script를 추가한다. 지금은 README와 checked-in packaging surface만으로 버틸 수 있는지 먼저 본다.

## References

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [AGENTS.md](/home/ubuntu/charness/AGENTS.md)
- [README.md](/home/ubuntu/charness/README.md)
- [docs/master-plan.md](/home/ubuntu/charness/docs/master-plan.md)
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

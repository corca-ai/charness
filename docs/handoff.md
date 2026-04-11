# charness Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `impl`로 이어서, 먼저 [README.md](/home/ubuntu/charness/README.md), [docs/host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md), [docs/operator-acceptance.md](/home/ubuntu/charness/docs/operator-acceptance.md), [plugins/charness/.codex-plugin/plugin.json](/home/ubuntu/charness/plugins/charness/.codex-plugin/plugin.json), [.agents/plugins/marketplace.json](/home/ubuntu/charness/.agents/plugins/marketplace.json)을 읽고 남은 Codex install proof만 이어서 본다.
- 이 머신에서는 `~/.agents/skills` source-checkout symlink가 이미 제거돼 있으니, 다시 생기지 않았는지만 짧게 확인한다.
- Claude local proof는 끝났다. 실제 local path는 `--plugin-dir /absolute/path/to/charness/plugins/charness`이고, parent `plugins/`를 주면 skill discovery proof가 되지 않는다.
- Codex는 exported consumer root와 plugin root 둘 다에서 `exec` 경로로는 local marketplace/plugin discovery가 잡히지 않았으니, interactive session 또는 다른 머신에서 실제 install/discovery proof를 이어서 본다.

## Current State

- `charness`는 portable Corca harness product로 정리됐고, public/support/profile/integration 경계는 현재 taxonomy 기준으로 고정됐다.
- public skill `narrative`가 추가돼 source-of-truth doc alignment와 audience-facing brief derivation이 `announcement`와 분리됐다.
- repo-owned release/install surface는 `plugins/charness` 아래 checked-in plugin bundle로 정리돼 있고, root marketplace files는 그 install surface만 advertise한다.
- Ceal-era migration surface는 정리됐다. tracked tree에는 `Ceal`, `interview`, `concept-review`, `test-improvement`, `entity-stage-design`, `workbench` 같은 legacy naming이 남아 있지 않다.
- [docs/master-plan.md](/home/ubuntu/charness/docs/master-plan.md)는 post-migration 기준의 현재 계획으로 다시 썼고, 옛 migration map은 삭제했다.
- 이 머신의 `~/.agents/skills` source-checkout symlink는 제거됐다.
- Claude local dogfood는 exported plugin root 기준으로 확인됐다. `claude --plugin-dir /tmp/.../plugins/charness` debug log에서 `Loaded 14 skills from plugin charness`가 찍혔고, `/gather` 호출로 `TITLE:charness` 응답까지 확인했다.
- Claude local docs는 parent `plugins/` 경로를 가리키고 있었고, 그 경로는 plugin root가 아니라서 skill discovery proof가 되지 않았다. 이번 세션에서 관련 문서를 `plugins/charness` 기준으로 고친다.
- Codex `exec`는 `/tmp` exported consumer root, exported plugin root, repo root 비교 기준으로 local marketplace install proof를 제공하지 못했다. exported roots에서는 curated builtin/plugin skill만 보였고, repo root에서는 checked-in plugin 대신 source checkout `skills/`를 직접 읽었다.
- 마지막 repo 검증은 `./scripts/run-quality.sh` 통과와 Claude exported-plugin smoke/runtime proof다.

## Next Session

1. 문서 수정 후 regenerated plugin surface와 root marketplace가 여전히 source of truth와 일치하는지 다시 확인한다.
2. 다른 머신 또는 실제 interactive Codex에서 root `.agents/plugins/marketplace.json` 기준 local marketplace discovery/install visibility를 확인한다.
3. 가능하면 restart 후 same-checkout update model까지 본다.
4. Codex proof 결과를 바로 이 handoff나 별도 durable artifact에 남긴다.

## Discuss

- Codex의 실제 public install proof는 여전히 가장 불확실한 표면이다. 최소한 이 머신의 `codex exec`는 repo marketplace dogfood 증거로 쓰기 어렵다.
- Claude는 shipped surface proof가 나왔다. 남은 일은 corrected local path가 문서와 generated surface에 반영됐는지 유지하는 것이다.
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

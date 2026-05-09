# charness Handoff

## Workflow Trigger

- 다음 세션의 첫 행동은 [Next Session](#next-session) item 1을 시도하는 것이다. handoff 자체는 모든 task-oriented 세션이 무조건 읽는 pickup pointer다 ([AGENTS.md](../AGENTS.md) Start Here).
- repo operating contract, prompt/skill surface, export sync, 또는 checked-in artifact policy를 건드리면 [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를 같이 읽고 `impl`로 이어간다.

## Current State

- [AGENTS.md](../AGENTS.md)는 craken-style compact entry, 세부 운영 규칙은 [docs/conventions/](./conventions/)가 owner. handoff 본 파일은 rolling pointer — gate 수치, dogfood evidence, 긴 history는 owning artifact로 보내고 next action을 바꾸는 사실만 남긴다.
- `critique`/`quality`/`handoff`의 fresh-eye loop는 mandatory subagent다. spawn 불가 시 same-agent fallback 금지, host signal 남기고 stop. `init-repo`/`AGENTS.md`가 "already delegated"로 surface한다 (second-message 대기 금지).
- prompt-affecting surface는 [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml) `run_mode`가 owner. 현재 `disabled`(전면 재작업 중) — Cautilus 바이너리/평가 안 돌리고, deterministic gate + adapter-disabled proof validator가 closeout을 맡는다.
- checked-in plugin export가 걸린 source를 바꾸면 validator 전에 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 sync. 같은 원칙으로 README/help text를 건드리면 먼저 `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md`.
- charness가 ship한 manifest는 사용자 리포에서도 자동 fallback 노출 (`tool_id` 충돌 시 user 우선). 사용자 리포는 [integrations/tools/dependencies.json](../integrations/tools/dependencies.json)에 staging.
- worktree readiness contract land — `.agents/worktree-adapter.yaml`로 prepare/doctor 등록, `impl`/`hitl` bootstrap이 `charness worktree doctor --json`을 non-fatal probe로 호출. owner는 [scripts/worktree_doctor_lib.py](../scripts/worktree_doctor_lib.py) + [docs/worktree-prepare.md](./worktree-prepare.md).
- artifact policy는 `history-default, latest optional` 재분류 중. owner는 [docs/artifact-policy.md](./artifact-policy.md).
- quality/runtime 숫자는 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), release truth는 [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)와 `python3 skills/public/release/scripts/current_release.py --repo-root .`가 owner.
- **#135 PR 2 (Leg 2 emit + Leg 1 inventory) land** (commit `77d87b7`). [scripts/t_events_emit_lib.py](../scripts/t_events_emit_lib.py)가 retro persist hook에서 `(source: ...)` cite를 lesson_cited 이벤트로 emit (real-content backtick form 가드 포함). [.agents/t-events-adapter.yaml](../.agents/t-events-adapter.yaml)이 charness self-config; `.charness/t-events/`는 gitignored 런타임. Leg 1: [charness-artifacts/skill-t-mechanism/inventory.{md,json}](../charness-artifacts/skill-t-mechanism/inventory.md) (18 row × 4 column, byte-deterministic) + validator [scripts/validate_skill_t_inventory.py](../scripts/validate_skill_t_inventory.py).
- 기 closed durable architecture (narrative widening v0.5.0, AGENTS.md craken refactor, worktree readiness, #108/#109/#115/#116/#122–#127/#128–#134/#135 PR 1)는 owning [charness-artifacts/spec/](../charness-artifacts/spec/) + [charness-artifacts/release/](../charness-artifacts/release/) + [charness-artifacts/retro/](../charness-artifacts/retro/) 아티팩트가 보유 (issue/PR 번호 grep으로 reload).

## Next Session

1. **다음 first move = #135 PR 3 (Leg 3 Engelbart anchor entry + `applies_when` scope wiring)**. spec [charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md](../charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md) Leg 3이 owner. PR 2가 `applies_when` 어휘를 [integrations/t-events/event.schema.json](../integrations/t-events/event.schema.json)에 박아놨다 (`lam-critique` / `system-improving-itself`). 이후 sequencing: PR 4 parallel (Leg 4 operator-T doc), PR 5 (Leg 6 `init-repo` → `setup` rename + `seed_t_events_adapter.py`).
2. read-only blocker no-write seam landed; 남은 작업은 (a) workspace-write workflow proof carrier 정의 (`--sandbox workspace-write` dogfood) (b) Cautilus adapter re-enable 후 routing eval에 `--read-only` 와이어링. spec은 [charness-artifacts/spec/readme-proof-cautilus-eval-migration.md](../charness-artifacts/spec/readme-proof-cautilus-eval-migration.md). README-specific Cautilus fixtures + README proof ledger + `cautilus claim discover` 연결은 모두 Cautilus re-enable 후.
3. public skill, handoff, validator, prompt surface를 건드리면 [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)와 [docs/public-skill-dogfood.json](./public-skill-dogfood.json)을 읽고 `impl`로 이어간다.
4. Active deferred follow-ups:
    - **#135 PR 3 follow-up — `skill_invoked`/`anchor_invoked` emit point.** Leg 3 anchor entry land 후 critique skill에서 `anchor_invoked` 한 번 emit이 자연스러운 dogfood. `skill_invoked`는 charness CLI 또는 host-injected hook 결정 후.
    - **Title-slug `--strict` CI/pre-push wiring (#131 follow-up)** — [check_title_slug_drift.py](../scripts/check_title_slug_drift.py)는 advisory-only ship됨; 다음 슬라이스에서 wiring.
    - **Cautilus rework 풀린 뒤** — Slice A-D shared reference (`agent-assessment-invariant.md`, `closeout-discipline.md`)와 7개 skill 추가 contract에 대한 [evals/cautilus/scenarios.json](../evals/cautilus/scenarios.json) coverage 검토 + `agent_choice`/`provider_roundtrip` proof level 채우기. tokei follow-ups (`quality`/`init-repo` SKILL.md wiring 두 줄)도 cautilus regression proof와 같이 한 슬라이스로 묶는다.
    - **Defensive runtime layer (critique이 Valid-but-Defer)** — `issue` 두-콜 retry runtime fixture (#126), `issue_tool.py validate-body --external-source` 런타임 린터 (#127), `.charness/issue/` durable session-state (#126의 더 강한 형태). dogfood 누적 후 발화.
5. 새 `inventory-sloc` quality phase (~96ms)는 runtime budget에 미등록 — 다음 슬로우-게이트 패스 때 다른 unbudgeted hot spot과 묶어 등록. quality phase write-policy 일반화 (adapter `quality_phases` dispatch / `CHARNESS_GATE_MODE`)는 두 번째 artifact-writing phase가 들어올 때.

## Discuss

- handoff/quality freshness validator를 stale-claim check 너머 어디까지 확장할지 — 열려 있다.
- `cautilus` planner의 `goal`을 `preserve`에서 `improve`+compare path로 언제 올릴지 — dogfood 더 봐야 한다.
- README/CLI reference/operator docs overlap을 더 줄일지 — consumer-repo dogfood로 탐색 마찰 본 뒤 결정.
- Cautilus claim discovery output을 checked artifact로 둘지 transient proof-plan input으로 둘지 — 열려 있다.
- release artifact가 GitHub release creation/public verification state를 얼마나 닫아야 하는지 — helper contract 차원에서 한 번 더 본다.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)
- [charness-artifacts/spec/readme-proof-cautilus-eval-migration.md](../charness-artifacts/spec/readme-proof-cautilus-eval-migration.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [docs/public-skill-dogfood.json](./public-skill-dogfood.json)

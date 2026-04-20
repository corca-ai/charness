# Cautilus Dogfood
Date: 2026-04-20

## Trigger

- slice: bound unowned process seams after issues `#41` and `#42`, including
  timeout discipline for public `resolve_adapter` CLIs and repo-owned
  `agent-browser` runtime hygiene / cleanup surfaces
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice adds stronger process and runtime guardrails, but it should
  not change the maintained public instruction routing contract

## Prompt Surfaces

- `skills/public/debug/references/adapter-contract.md`
- `skills/public/debug/references/document-seams.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `pytest -q tests/test_subprocess_guard.py tests/test_script_timeout.py tests/test_agent_browser_runtime_guard.py tests/test_gather_google_workspace.py tests/control_plane/test_integrations_validation.py tests/control_plane/test_sync_support.py tests/charness_cli/test_tool_lifecycle.py`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in surface still preserves the maintained
  `find-skills -> impl` path, compact direct implementation still routes to
  `impl`, and direct contract-shaping still routes to `spec`

## Follow-ups

- keep pushing timeout and lifecycle ownership into repo-owned helpers instead
  of leaving raw subprocess calls and daemon recovery as prose-only guidance
- if another long-lived runtime seam lands, require doctor-visible hygiene and
  scripted recovery from the first integration slice

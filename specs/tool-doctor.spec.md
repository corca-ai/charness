---
type: spec
workdir: .
---

# CLI Operator Contracts

`charness` operator-facing commands must leave structured continuation state
without confusing health, readiness, ownership, or the next operator action.

This spec intentionally starts with one stable behavior. It delegates the
fixture-heavy branch assertions to the focused pytest e2e instead of copying
that setup into shell or creating a specdown adapter too early.

## `specdown` Binary Contract, Task Envelope, And Doctor Next Action

The `specdown` integration is both a support-skill source in this repo and an
external binary managed through the tool control plane. The binary side should
remain `integration-only`: doctor checks the installed command and release
metadata, but support sync should not pretend there is a generated support
surface for this manifest.

The repo-local task envelope should provide the sah-inspired claim, submit, and
abort loop as structured state under `.charness/tasks/` without introducing a
queue or scheduler.

The root `doctor` command should emit a single primary `next_action` while
retaining host-specific `next_steps`, so operator automation can act on the
first meaningful host move without losing Codex/Claude detail.

```run:shell
# Verify stable CLI operator contracts in one pytest process
pytest -q tests/charness_cli/test_tool_lifecycle.py::test_tool_doctor_reports_specdown_binary_contract_without_support_sync tests/charness_cli/test_task_envelope.py tests/charness_cli/test_doctor_next_action.py::test_charness_doctor_prints_primary_next_action
```

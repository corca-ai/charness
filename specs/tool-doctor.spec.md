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

## `specdown` Binary Contract And Task Envelope

The `specdown` integration is both a support-skill source in this repo and an
external binary managed through the tool control plane. The binary side should
remain `integration-only`: doctor checks the installed command and release
metadata, but support sync should not pretend there is a generated support
surface for this manifest.

The repo-local task envelope should provide the sah-inspired claim, submit, and
abort loop as structured state under `.charness/tasks/` without introducing a
queue or scheduler.

```run:shell
# Verify stable CLI operator contracts in one pytest process
pytest -q tests/charness_cli/test_tool_lifecycle.py::test_tool_doctor_reports_specdown_binary_contract_without_support_sync tests/charness_cli/test_task_envelope.py
```

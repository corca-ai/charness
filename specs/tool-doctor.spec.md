---
type: spec
workdir: .
---

# External Tool Operator Contract

`charness tool doctor` must report external tool readiness without confusing
binary health, support-skill materialization, install provenance, release
metadata, or the next operator action.

This spec intentionally starts with one stable behavior. It delegates the
fixture-heavy branch assertions to the focused pytest e2e instead of copying
that setup into shell or creating a specdown adapter too early.

## `specdown` Binary Contract

The `specdown` integration is both a support-skill source in this repo and an
external binary managed through the tool control plane. The binary side should
remain `integration-only`: doctor checks the installed command and release
metadata, but support sync should not pretend there is a generated support
surface for this manifest.

```run:shell
# Verify the specdown tool doctor e2e contract
pytest -q tests/charness_cli/test_tool_lifecycle.py::test_tool_doctor_reports_specdown_binary_contract_without_support_sync
```

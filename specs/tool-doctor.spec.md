---
type: spec
workdir: .
---

# CLI Operator Contracts

`charness` operator-facing commands must leave structured continuation state
without confusing health, readiness, ownership, or the next operator action.

This spec keeps proof at the operator-facing command boundary. Fixture-heavy
branch coverage still belongs in pytest, but the current shipped CLI contract
should remain readable and executable here.

## `specdown` Binary Contract, Task Envelope, And Doctor Next Action

The `specdown` integration consumes an upstream support skill and remains an
external binary managed through the tool control plane. Doctor checks the
installed command and release metadata, and it should report the support source
as upstream-consumed until sync materializes the installed plugin support
surface.

```run:shell
python3 ./charness tool doctor --repo-root . --json specdown | python3 -c "import json,sys; payload=json.load(sys.stdin); doctor=payload['results']['specdown']['doctor']; assert doctor['support_state']=='upstream-consumed'; assert doctor['detect']['results'][0]['command']=='specdown version'; assert doctor['healthcheck']['results'][0]['command']=='specdown run -help'"
```

The repo-local task envelope should provide the sah-inspired claim, submit, and
abort loop as structured state under `.charness/tasks/` without introducing a
queue or scheduler.

```run:shell
python3 ./charness task --repo-root . --json status missing-slice | python3 -c "import json,sys; payload=json.load(sys.stdin); assert payload['event']=='rejected'; assert payload['status']=='missing'; assert payload['task_path']=='.charness/tasks/missing-slice.json'"
```

The root `doctor` command should emit a single primary `next_action` while
retaining host-specific `next_steps`, so operator automation can act on the
first meaningful host move without losing Codex/Claude detail.

```run:shell
python3 ./charness doctor --repo-root . --json | python3 -c "import json,sys; payload=json.load(sys.stdin); action=payload['next_action']; assert isinstance(action, dict) and action['kind']; assert action['message']; assert isinstance(payload['next_steps'], dict) and payload['next_steps']"
```

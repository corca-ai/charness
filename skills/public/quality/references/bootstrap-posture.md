# Bootstrap Posture

Use the bootstrap posture when `quality` should leave the repo in a better
installed state, not only produce review notes.

The bootstrap helper should:

- write or refresh `<repo-root>/.agents/quality-adapter.yaml` idempotently
- preserve explicit operator-owned command groups when they already exist
- infer concept paths and preset lineage from the repo surface
- avoid materializing language-specific defaults, such as pytest reference
  patterns, unless that language family is detected or explicitly selected
- record `installed`, `inferred`, `preserved`, or `deferred` status per field
- emit a machine-readable deferred-setup report when automation stops short

Default report path:

- `.charness/quality/bootstrap.json`

The report is repo state when committed, so paths in it must be repo-root
relative. Use absolute paths only for transient stdout diagnostics.

Status meanings:

- `installed`: the repo already had a repo-owned command or helper and the
  adapter now records it explicitly
- `inferred`: the helper derived a safe default from current repo signals
- `preserved`: the adapter already carried an explicit value and bootstrap left
  it intact
- `augmented`: an existing explicit value was kept and extended with newly
  discovered safe defaults
- `deferred`: bootstrap found no honest automatic value and left the operator a
  concrete next step instead
- `deliberately-absent`: the adapter declared this field absent on purpose, so
  bootstrap left it out instead of refilling it from a default

## Declaring a field deliberately absent

An absent field cannot say why it is absent. `field not in adapter` reads the same
whether the operator never set it or deliberately cut it, so a helper that defaults
on absence refills both — and a repo that removed a gate it does not have gets it
back, pointing at files that do not exist.

`deliberately_absent` maps a field name to the reason it is gone:

```yaml
deliberately_absent:
  coverage_floor_policy: this repo uses neither lefthook nor CI
  security_commands: no repo-owned security helper exists here
```

Bootstrap then leaves those fields out of the adapter and drops the matching
deferred-setup prompt. The reason lives in the same field as the signal on purpose:
the adapter is re-serialized from data, so a rationale kept in a YAML comment is
destroyed by the same rewrite it was meant to explain.

Rules:

- every declared field needs a non-empty reason; a reasonless absence is
  indistinguishable from an oversight
- a field cannot be both declared absent and set
- structural fields (`version`, `repo`, `language`, `output_dir`, `preset_id`,
  `customized_from`) cannot be declared absent
- quote a reason containing a space followed by `#`, or YAML reads the rest of the
  line as a comment and the truncated reason is what gets written back
  (`security_commands: "dropped, see the tracked issue"`)
- the field is hand-authored; bootstrap never invents it
- an adapter without the field behaves exactly as it did before the field existed

## What a declaration means at resolution time

Adapter *resolution* still fills unset fields from repo defaults — changing that would
alter what every field means at resolution time and break consumers that index them.
So a resolved adapter carries the default value alongside the declaration, plus:

- `deliberately_absent` — the declaration itself, so it survives resolution
- `deliberately_absent_unasserted_paths` — the resolved path values the repo does
  **not** claim exist. Keys are `<field>.<key>` for a mapping (dotted for nesting) and
  `<field>[<index>]` for a list, so a consumer parsing them must expect both shapes.
  A value counts as a path when it contains `/` or ends in a file extension AND has no
  whitespace — the whitespace clause is what keeps a cron expression and a regex out
- a warning naming those paths, because a resolved default that names a file the repo
  does not have is what sends the next session hunting for it

Only fields whose default names a filesystem path get the path treatment; thresholds,
rule names, and markers assert nothing about the filesystem and are left alone.

**A consumer about to premise anything on a resolved value asks first:**

```python
from scripts.quality_adapter_lib import is_deliberately_absent

if not is_deliberately_absent(data, "coverage_floor_policy"):
    ...  # safe to treat the resolved paths as this repo's real surface
```

Do not read a resolved default for a declared-absent field as this repo's own
declaration.

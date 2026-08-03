# Bootstrap Posture

Use the bootstrap posture when `quality` should leave the repo in a better
installed state, not only produce review notes.

The bootstrap helper should:

- write or refresh `<repo-root>/.agents/quality-adapter.yaml` idempotently
- preserve explicit operator-owned command groups when they already exist
- infer concept paths and preset lineage from the repo surface
- avoid materializing language-specific defaults, such as pytest reference
  patterns, unless that language family is detected or explicitly selected
- record `installed`, `inferred`, `preserved`, `augmented`, `deferred`, or
  `deliberately-absent` status per field (all six are defined below)
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
- `augmented`: an existing explicit value was kept and added to. Two ways to get
  here. The field-level one: newly discovered safe defaults were appended (this is
  how `preset_lineage` reports a merge). The SUB-KEY one: the adapter kept a policy
  block — `coverage_floor_policy`, `prompt_asset_policy`, `mutation_testing` — but
  did not set every key inside it, so the merge refilled the rest from the preset.
  **A kept-but-partial block is `augmented`, never `preserved`.** It used to report
  `preserved` while the merge was refilling, which asserted the opposite of what
  happened; the report now names the refilled sub-keys in `refilled_subkeys` and in
  the customization warning. A sub-key counts as refilled when it is absent, blank,
  or written with a type the merge does not accept — all three are the operator's
  value being silently discarded, and only the first looks like a deletion. That
  three-way rule is `coverage_floor_policy` and `prompt_asset_policy`, whose merges are
  permissive. **`mutation_testing` validates most of its sub-keys instead**: a blank or
  wrong-typed SCALAR (`score_break:`), and a blank or wrong-typed LEAF inside a nested
  block (`report_paths:` → `summary_md:`), are bootstrap ERRORS rather than silent
  refills. The one spelling it does accept silently is a blank nested BLOCK header
  (`report_paths:` with nothing under it), which refills the whole block and reports it.
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
- `refilled_subkeys` — `{<field>: [<sub-key>, ...]}` for every kept-but-partial
  policy block, emitted alongside the `augmented` status. Only present when a rewrite
  actually refilled something, so its absence means nothing was refilled, not that the
  key was forgotten. A NESTED block the operator partially wrote reports its refilled
  leaves dotted (`report_paths.sample_md`); a nested block refilled WHOLE reports its
  block name alone, because naming every leaf under it says less, not more.
  **Look for this in the BOOTSTRAP report (`.charness/quality/bootstrap.json`), not on
  a resolved adapter** — unlike the other entries in this section it is an account of
  one rewrite, not a declaration that survives resolution.
  **Two dotted namespaces live in this file and they are not the same.**
  `refilled_subkeys` leaves are FIELD-RELATIVE (`report_paths.sample_md`, under a
  `mutation_testing` key) and are a report granularity only — nothing parses them back
  into a key path. `deliberately_absent_unasserted_paths` keys below are
  FIELD-PREFIXED (`<field>.<key>`) and ARE parsed by consumers. Neither is a
  `deliberately_absent` declaration vocabulary; declaring a single sub-key absent
  remains impossible.

**`deliberately_absent` names whole FIELDS only.** There is no way to declare a
single sub-key absent on purpose: the closest available move is to drop the whole
block and declare the field, which keeps it out of the adapter FILE and marks its
paths unasserted — resolution still supplies the default value to consumers. Dropping
the block without the declaration is worse than doing nothing: the field becomes
non-explicit and the next bootstrap refills all of it.

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

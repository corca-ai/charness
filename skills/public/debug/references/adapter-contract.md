# Debug Adapter Contract

The debug adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `<repo-root>/.agents/debug-adapter.yaml`.

## Fields

Required shared core:

- `version`
- `repo`
- `language`
- `output_dir`

Optional shared provenance:

- `preset_id`
- `preset_version`
- `customized_from`

Optional size budget:

- `max_artifact_words` — raw FILE words the debug artifact may occupy.
  Omit it to keep the validator's shipped default. Both the gate and the
  scaffold's `size_budget.max_words` forecast resolve the same value, so raising
  it never leaves the author writing to a stale number. Must be a positive
  integer; a refused value is an adapter error and leaves the default enforced.
  When the scaffold cannot reach the gate's resolver at all (a cross-tree
  version skew), it forecasts the shipped default and says so in
  `size_budget.source`, rather than presenting a stale number as resolved.
- `max_artifact_lines` — RETIRED on 2026-08-19 and now an adapter ERROR, not a
  silently ignored key. A line count charged for the author's wrap width rather
  than the reading load it named: across 146 checked-in debug artifacts the
  180-line cap admitted between 276 and 1487 words. No automatic conversion
  exists, so restate the bar in `max_artifact_words`.
  There is no upper bound: the ceiling is this repo's to set.

## Artifact Rule

The durable debug artifact filename is fixed:

- `latest.md`

Default path:

- `<repo-root>/charness-artifacts/debug/latest.md`

Dated debug records should use `<repo-root>/charness-artifacts/debug/YYYY-MM-DD-<slug>.md`.

To change the location, override `output_dir` in the adapter.

To scaffold the canonical artifact body and validator hint from the repo root:

```bash
python3 "$SKILL_DIR/scripts/scaffold_debug_artifact.py" --repo-root .
```

Use the returned `validator_command` instead of assuming the consumer repo has a
local `<plugin-dir>/scripts/gates/validate_debug_artifact.py`. Installed Charness layouts keep that
validator under the plugin or managed checkout, not under every target repo.

## Validator Contract

The scaffold helper, skill body, and validator share one current artifact
schema. The current schema includes `Seam Risk` and `Interrupt Decision` before
`Prevention`.

Which artifact that schema governs is decided by ROLE, not by filename: the
current pointer (`latest.md`), plus the dated record it designates when the
pointer is a symlink or a byte copy. Both pointer layouts are supported, so one
file reached by two names gets one verdict rather than two.

Every OTHER dated record is durable debug memory, not mutable current state.
The validator checks their core debug sections and ordering, but it tolerates
legacy extra sections so older records do not block a new investigation. When
any artifact fails validation, the validator names the offending artifact path.

Some older materialized skill packs used a hyphenated validator filename. New
scaffold output should use the emitted `validator_command` as the canonical
command instead of hardcoding either spelling.

## Example

```yaml
version: 1
repo: my-repo
language: en
output_dir: charness-artifacts/debug
preset_id: portable-defaults
customized_from: portable-defaults
```

## Design Rules

- keep artifact location in the adapter, not in the skill body
- use one durable debug artifact path per repo by default
- if the repo already has a better incident or debug-note surface, point
  `output_dir` there instead of hardcoding that choice into `SKILL.md`

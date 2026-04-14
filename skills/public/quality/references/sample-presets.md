# Sample Presets

`quality` ships sample presets for common repo families.

Current shipped samples:

- `typescript-quality`
- `python-quality`
- `specdown-quality`
- `monorepo-quality`

These presets are examples of vocabulary and default command surfaces, not
mandatory hidden behavior.

The adapter should still record the actual commands and the preset lineage.

- `preset_id` remains the primary bootstrap seed for the current adapter
- `preset_lineage` may include multiple sample presets when the repo honestly
  spans more than one family
- bootstrap should prefer honest multi-family lineage over pretending one
  sample preset fully explains the repo
- `specdown-quality` should also seed executable-spec-specific adapter defaults
  such as `specdown_smoke_patterns`; `coverage_fragile_margin_pp` defaults to
  `1.0` unless the repo needs a stricter or looser threshold

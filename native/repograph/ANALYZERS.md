# External analyzer results

`repograph` accepts captured provider documents through
`--analyzer-result`. The input contract is `repograph.analyzer_result.v1`.
The result is declarative: `repograph` never starts an analyzer.

## `analyzer_result.v1`

The document has these fields:

| Field | Shape | Meaning |
| --- | --- | --- |
| `schema` | string | Exactly `repograph.analyzer_result.v1`. |
| `analyzer` | `{name, version}` | Provider identity and provider version. |
| `source` | `{commit}` or `{digest}` | Exactly one source identity. |
| `scope` | `{paths}` or `{globs}` | Exactly one declared path set. Globs use the graph's Python-compatible matcher. |
| `modules` | `[{id}]` | External modules owned by this provider result. |
| `imports` | `[{source, target, module?, line?}]` | Typed imports claims. Endpoints are `{kind: file, path}` or `{kind: external-module, id}`. |
| `exclusions` | `[{path, reason}]` | Provider exclusions, which remain unestablished claims. |
| `parse_conditions` | `[{path, kind, detail}]` | Typed provider parse observations. |
| `completeness` | `complete`, `partial`, or `failed` | Whether the declared scope was fully analyzed. |

The JSON boundary uses `serde(deny_unknown_fields)` on every object. The
endpoint, parse-condition, and completeness enums have no catch-all variant.
Invalid values therefore become typed `analyzer-parse-failure` conditions.

An imports edge is retained only when every file endpoint is both in the
declared scope and in the current snapshot, and at least one endpoint is an
external module. Existing Charness-owned skill, adapter, mirror, and command
targets are protected; a rejected claim is a `scope-violation` and is not
merged. Partial or failed results, incompatible schema versions, zero-module
results, exclusions, and parse conditions produce `unestablished` records.
Multiple result files are ingested in flag order. Overlapping declared scopes
produce a `scope-conflict` record.

## rev-dep mapping

The fixture in `fixtures/analyzers/rev_dep.json` uses this small captured
rev-dep-shaped representation:

| rev-dep output | `analyzer_result.v1` |
| --- | --- |
| `tool` | `analyzer.name` |
| `tool_version` | `analyzer.version` |
| `source` | `source` |
| `scope.files` | `scope.paths` |
| `modules[].name` | `modules[].id` |
| `modules[].imports[].file` | `imports[].source = {kind: file, path}` |
| `modules[].name` | `imports[].target = {kind: external-module, id}` |
| `modules[].imports[].specifier` | `imports[].module` |
| `modules[].imports[].line` | `imports[].line` |
| `excluded[].file` and `excluded[].reason` | `exclusions[].path` and `exclusions[].reason` |
| `conditions[].file`, `conditions[].status`, `conditions[].message` | `parse_conditions[].path`, `parse_conditions[].kind`, `parse_conditions[].detail` |
| `status` | `completeness` |

`adapt_rev_dep` applies this mapping to a captured document. The expected
projection is `fixtures/analyzers/expected/rev_dep_ingestion.json`.

No live rev-dep producer is exercised here. This lane proves the provider
mechanism and the mapping against a hand-written fixture only.

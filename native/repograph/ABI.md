# repograph command ABI

> Status: frozen at v1 by the ratified issue #745 go verdict, 2026-08-28.
> Source: the `repograph` release binary built from this crate.

This document freezes the machine-facing CLI contract for `parse-corpus`,
`export-safe`, `match-surfaces`, and `standalone-targets`, and records the
additive topology commands (`graph`, `classify`, `changed`, `carriers`). A reportable run
emits one UTF-8 JSON document on stdout and diagnostics on stderr. The
command-specific inventory, manifest, and path errors below identify the
failure cases that emit diagnostics without a report. JSON member order is not
significant; array ordering rules are part of the ABI.

The examples below are real captures from the release binary built with:

```bash
cargo build --release --offline
```

The parse-corpus example is explicitly abridged. Its counts and retained
entries come from the complete captured document; omitted entries are marked
outside the JSON block. The other examples retain the complete document from
their respective captures, with whitespace formatted for readability.

## Common command-line rules

The executable accepts one required command name:

```text
repograph <parse-corpus|export-safe|match-surfaces|standalone-targets|graph|classify|changed|carriers> [options]
```

`--help` and `-h` print the command usage and exit 0. An unknown command,
unknown option, unexpected positional argument, or missing option value is a
usage error and exits 2. There is no `--` option terminator. A value beginning
with `-` is treated as a missing value by the option parsers.

For commands that acquire an inventory, the inventory is established exactly
once per process. Without `--file-list`, the binary runs this command with
`--repo-root` as its working directory:

```text
git ls-files -z --cached --others --exclude-standard
```

With `--file-list`, the file is read relative to the process current directory
as NUL-separated, UTF-8, repository-relative paths. Empty NUL records are
ignored. Absolute paths and paths containing a `..` component are rejected. A
supplied file list prevents the Git listing. `listing` is `"git"` or
`"file-list"` on a successful inventory, and `"unestablished"` in
inventory-error reports.

The `--repo-root` and `--file-list` options are not repeatable in the semantic
sense: if supplied more than once, the last value wins. Their defaults and
command-specific exceptions are documented below.

## `parse-corpus`

### `parse-corpus` input

Usage:

```text
repograph parse-corpus [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]...
```

| Argument or flag | Contract |
| --- | --- |
| command | Required literal `parse-corpus`. |
| `--repo-root PATH` | Repository root. Default: the process current directory. |
| `--file-list PATH` | Optional NUL-separated inventory file. Default: acquire one Git snapshot. |
| `--exclude-prefix PREFIX` | Repeatable path prefix filter. Default when omitted: `plugins/`. Supplying it at least once replaces the default with the supplied prefixes, in supplied order. |
| `--help`, `-h` | Print usage and exit 0. |
| positional arguments | Not accepted. |

The command selects inventory paths whose spelling ends in `.py`, case
sensitive, and does not start with any exclusion prefix. It does not require a
selected path to be a regular file before attempting to read it. Duplicate
paths in an injected file list remain duplicate records in this command.

Each selected file is parsed as Python targeting Python 3.10. Parsing is
panic-safe per file, so one failure does not prevent the other selected files
from appearing in the report. The first parser error takes precedence over an
unsupported-syntax result if both are present.

### `parse-corpus` output schema

Schema id: `repograph.parse_corpus.v1`.

| Field | JSON type | Meaning |
| --- | --- | --- |
| `schema` | string | Always `repograph.parse_corpus.v1`. |
| `repo_root` | string | The supplied or default root, as represented by the CLI; this command does not canonicalize it. |
| `listing` | string | Inventory source: `git` or `file-list`. |
| `files_total` | integer | Number of selected `.py` records. |
| `parsed` | integer | Number of records whose `status` is `parsed`. |
| `failed` | integer | `files_total - parsed`; all non-`parsed` statuses. |
| `files` | array of objects | One entry for every selected record, including unreadable and failed records. |

Each `files` object has this schema:

| Field | JSON type | Meaning |
| --- | --- | --- |
| `path` | string | Inventory path, relative to `repo_root`. |
| `status` | string | One of `parsed`, `parse-error`, `unsupported-syntax`, `panicked`, or `unreadable`. |
| `detail` | string | `ok` for parsed files; otherwise a typed, human-readable detail with the parser location or read failure when available. |

`files` is sorted by repository path using UTF-8 byte order. A parsed detail is
exactly `"ok"`. Parse errors and unsupported syntax include line, column, and
byte offset. A panic is reported as `panicked: ...`; invalid UTF-8 and read
failures are `unreadable: ...`.

An inventory failure occurs before the report is constructed: it emits the
diagnostic on stderr and no JSON document on stdout.

Real capture, abridged. The command exited 3 because the complete `files`
array contained 17 records, including four failures:

Capture command, run from `native/repograph`:

```bash
target/release/repograph parse-corpus --repo-root fixtures \
  --file-list fixtures/file-list.nul
```

```json
{
  "schema": "repograph.parse_corpus.v1",
  "repo_root": "fixtures",
  "listing": "file-list",
  "files_total": 17,
  "parsed": 13,
  "failed": 4,
  "files": [
    {
      "path": "direct_script.py",
      "status": "parsed",
      "detail": "ok"
    },
    {
      "path": "dynamic_imports.py",
      "status": "parsed",
      "detail": "ok"
    },
    {
      "path": "empty.py",
      "status": "parsed",
      "detail": "ok"
    },
    {
      "path": "non_utf8.py",
      "status": "unreadable",
      "detail": "unreadable: invalid-utf8 at byte 0"
    }
  ]
}
```

Omitted from this abridged capture: … 13 additional `files` entries, including
the remaining parsed files, a dangling-link read error, and two parse errors.

### `parse-corpus` exit semantics

| Exit | Meaning for `parse-corpus` |
| --- | --- |
| 0 | The report was emitted and every selected record parsed successfully. Zero selected `.py` files is a successful zero-scope report with `files_total`, `parsed`, and `failed` all zero. |
| 1 | Unused by this command. Parse failures are exit 3. |
| 2 | CLI usage error. |
| 3 | Inventory could not be established, or any selected file was `parse-error`, `unsupported-syntax`, `panicked`, or `unreadable`. The report still includes every selected record that could be processed. |
| 70 | Internal `repograph` failure, including a top-level panic or an output failure. |

## `export-safe`

### `export-safe` input

Usage:

```text
repograph export-safe [--repo-root PATH] [--file-list PATH]
```

| Argument or flag | Contract |
| --- | --- |
| command | Required literal `export-safe`. |
| `--repo-root PATH` | Repository root. Default: the process current directory. |
| `--file-list PATH` | Optional NUL-separated inventory file. Default: acquire one Git snapshot. |
| `--help`, `-h` | Print usage and exit 0. |
| positional arguments | Not accepted. |

The selected universe is the existing-file intersection of the inventory and
these four non-recursive patterns:

```text
scripts/*.py
skills/public/*/scripts/*.py
skills/support/*/scripts/*.py
skills/shared/scripts/*.py
```

The `*` in these inventory patterns does not cross `/`. Selected paths are
deduplicated by path and sorted lexically before analysis. The command reports
all violations, not only the first one.

The violation detector reports these `kind` values:

| Kind | Meaning |
| --- | --- |
| `forbidden-from-import` | A `from` import whose module is exactly `skills.public` or starts with `skills.public.`. |
| `forbidden-import` | An `import` statement containing an imported name equal to or below `skills.public`. |
| `forbidden-import-repo-module` | A bare `import_repo_module` call with a supported `__file__` or `Path(__file__)` first argument, and a forbidden string module name in the positional or named second argument. |
| `forbidden-asset-path` | An export-rooted `REPO_ROOT` division resolving to `skills/public` or below, either as one string literal (backslashes normalized for matching) or as `"skills" / "public"` path segments. |

An export-rooted path expression recognizes `REPO_ROOT` through division,
attribute, and call chains. If the file also probes another layout through an
export-rooted `... / "skills" / <non-public> ...` expression, asset-path
violations are suppressed for that file. Import violations are never
suppressed by this escape hatch.

### `export-safe` output schema

Schema id: `repograph.export_safe.v1`.

| Field | JSON type | Meaning |
| --- | --- | --- |
| `schema` | string | Always `repograph.export_safe.v1`. |
| `repo_root` | string | The supplied or default root; this command does not canonicalize it. |
| `listing` | string | `git`, `file-list`, or `unestablished` for an inventory-error report. |
| `files_total` | integer | Number of selected files, equal to `analyzed_files + unestablished.length`. Zero for an inventory-error report. |
| `analyzed_files` | integer | Selected files parsed and read successfully for analysis. |
| `violations` | array of objects | All detected violations, sorted by path, line, kind, then source. |
| `unestablished` | array of objects | Typed per-file or inventory failures that prevent a pass. Empty for an established analysis. |

Each `violations` object has `path` (string, inventory path), `line` (integer,
one-based source line), `kind` (string, one of the four values above), and
`source` (string, the source line with a trailing CR removed).

Each `unestablished` object has `path` (string), `status` (string), and
`detail` (string). A per-file status is one of the parse statuses from
`parse-corpus`; an inventory failure uses path `"<inventory>"` and status
`"inventory"`. A zero-scope report uses path `"<scope>"`, status
`"zero-scope"`, and detail `"no export-safe Python files were selected"`.
Per-file `unestablished` entries are sorted by path.

Real capture, with all fields and violations retained:

Capture command, run from `native/repograph`:

```bash
printf 'scripts/forbidden_import_repo_module.py\0' |
  target/release/repograph export-safe --repo-root fixtures/export_safe \
  --file-list /dev/stdin
```

```json
{
  "schema": "repograph.export_safe.v1",
  "repo_root": "fixtures/export_safe",
  "listing": "file-list",
  "files_total": 1,
  "analyzed_files": 1,
  "violations": [
    {
      "path": "scripts/forbidden_import_repo_module.py",
      "line": 1,
      "kind": "forbidden-import-repo-module",
      "source": "first = import_repo_module(__file__, \"skills.public.first\")"
    },
    {
      "path": "scripts/forbidden_import_repo_module.py",
      "line": 2,
      "kind": "forbidden-import-repo-module",
      "source": "second = import_repo_module(script_file=Path(__file__), module_name=\"skills.public.second\")"
    },
    {
      "path": "scripts/forbidden_import_repo_module.py",
      "line": 3,
      "kind": "forbidden-import-repo-module",
      "source": "third = import_repo_module(Path(__file__), \"skills.public.third\")"
    }
  ],
  "unestablished": []
}
```

This captured command exited 1 because violations were found. An inventory
failure still emits this schema with `listing: "unestablished"` and an
`<inventory>` entry before exiting 3.

### `export-safe` exit semantics

| Exit | Meaning for `export-safe` |
| --- | --- |
| 0 | The report was emitted, at least one file was selected and established, and no violations were found. |
| 1 | The report was emitted with one or more violations and no unestablished entries. |
| 2 | CLI usage error. |
| 3 | Inventory failure, zero selected files, or any selected file could not be established due to a parse, unsupported-syntax, panic, or read failure. Unestablished results take precedence over violation exit 1. |
| 70 | Internal `repograph` failure, including a top-level panic or an output failure. |

## `match-surfaces`

### `match-surfaces` input

Usage:

```text
repograph match-surfaces [--repo-root PATH] [--surfaces PATH] [--path PATH]...
```

| Argument or flag | Contract |
| --- | --- |
| command | Required literal `match-surfaces`. |
| `--repo-root PATH` | Root used to resolve a relative manifest path. Default: the process current directory. |
| `--surfaces PATH` | Surfaces manifest. Default: `.agents/surfaces.json`. If repeated, the last value wins. |
| `--path PATH` | Repeatable changed repository path. Default: no paths. Values are appended in occurrence order before normalization and first-occurrence deduplication. |
| `--help`, `-h` | Print usage and exit 0. |
| positional arguments | Not accepted. |

This command does not acquire a Git inventory. It reads the manifest and uses
only the paths supplied by `--path`. Relative manifest paths are joined to
`--repo-root`; absolute manifest paths are used as given.

Changed paths and manifest patterns normalize by splitting on `/`, dropping
empty and `.` components, and joining the remainder with `/`. An absolute path
or a normalized path beginning with `../` is rejected. Embedded components
such as `one/../two` are retained. An empty normalized path becomes `.`.

The manifest must be a JSON object with numeric `version` equal to 1, a
non-empty `surfaces` array, and unique surface IDs. Each surface requires
non-empty string `surface_id` and `description`, plus string arrays
`source_paths`, `derived_paths`, `sync_commands`, `verify_commands`, and
`notes`. Optional `generated_markdown` entries require string
`source_path`, `derived_path`, `generator`, and `sync_command`. Recursive
extension patterns must be paired with their non-recursive sibling because
matching uses non-recursive-fnmatch-safe patterns. A generated-markdown entry's
source and derived paths must match the corresponding surface patterns.

Matching uses case-sensitive POSIX `fnmatch` semantics. `*` crosses `/` for
this command; `?` and bracket character classes are also supported. A path
matches a surface when it matches any source or derived pattern.

### `match-surfaces` output schema

Schema id: `repograph.match_surfaces.v1`.

| Field | JSON type | Meaning |
| --- | --- | --- |
| `schema` | string | Always `repograph.match_surfaces.v1`. |
| `changed_paths` | array of strings | Normalized, first-occurrence-deduplicated `--path` values. |
| `matched_surfaces` | array of objects | Surfaces matched by at least one changed source or derived path, in manifest declaration order. |
| `sync_commands` | array of strings | Matched-surface sync commands, flattened in surface/manifest order and deduplicated by first occurrence. |
| `verify_commands` | array of strings | Matched-surface verify commands, flattened in surface/manifest order and deduplicated by first occurrence. |
| `unmatched_paths` | array of strings | Normalized changed paths that matched no source or derived pattern, in changed-path order. |

Each `matched_surfaces` object has:

| Field | JSON type | Meaning |
| --- | --- | --- |
| `surface_id` | string | Manifest surface identifier. |
| `description` | string | Manifest description. |
| `matched_source_paths` | array of strings | Changed paths matching this surface's source patterns, in changed-path order. |
| `matched_derived_paths` | array of strings | Changed paths matching this surface's derived patterns, in changed-path order. |
| `source_paths` | array of strings | The surface's normalized source patterns, in manifest order. |
| `derived_paths` | array of strings | The surface's normalized derived patterns, in manifest order. |
| `sync_commands` | array of strings | This surface's sync commands, in manifest order. |
| `verify_commands` | array of strings | This surface's verify commands, in manifest order. |
| `notes` | array of strings | This surface's notes, in manifest order. |

Real capture, with duplicate input and case-sensitive unmatched input:

Capture command, run from `native/repograph`:

```bash
target/release/repograph match-surfaces \
  --repo-root fixtures/match_surfaces --surfaces surfaces.json \
  --path dir/sub/nested.py --path dir/file.py --path dir/file.py \
  --path Case/File.py --path case/file.py --path CASE/File.py \
  --path out/generated.md
```

```json
{
  "schema": "repograph.match_surfaces.v1",
  "changed_paths": [
    "dir/sub/nested.py",
    "dir/file.py",
    "Case/File.py",
    "case/file.py",
    "CASE/File.py",
    "out/generated.md"
  ],
  "matched_surfaces": [
    {
      "surface_id": "first",
      "description": "first declaration",
      "matched_source_paths": ["dir/sub/nested.py", "dir/file.py"],
      "matched_derived_paths": ["out/generated.md"],
      "source_paths": ["dir/*.py", "dir/**/*.py"],
      "derived_paths": ["out/*.md", "out/**/*.md"],
      "sync_commands": ["shared-sync", "first-sync"],
      "verify_commands": ["shared-verify", "first-verify"],
      "notes": ["first note"]
    },
    {
      "surface_id": "second",
      "description": "second declaration",
      "matched_source_paths": ["Case/File.py"],
      "matched_derived_paths": ["case/file.py"],
      "source_paths": ["Case/*.py"],
      "derived_paths": ["case/*.py"],
      "sync_commands": ["shared-sync", "second-sync"],
      "verify_commands": ["shared-verify", "second-verify"],
      "notes": ["second note"]
    }
  ],
  "sync_commands": ["shared-sync", "first-sync", "second-sync"],
  "verify_commands": ["shared-verify", "first-verify", "second-verify"],
  "unmatched_paths": ["CASE/File.py"]
}
```

The captured command exited 0. With no `--path`, the valid-manifest result is
also exit 0 with all five output arrays empty. Invalid or unreadable manifest
JSON, invalid manifest structure, duplicate IDs, or a rejected path emits
diagnostics on stderr and exits 3 without a report document.

### `match-surfaces` exit semantics

| Exit | Meaning for `match-surfaces` |
| --- | --- |
| 0 | A valid manifest was loaded and the report was emitted, including a zero-path report. |
| 1 | Unused; this is a pure-report command and has no violation verdict. |
| 2 | CLI usage error. |
| 3 | The manifest could not be read or validated, or a changed path could not be normalized within the repository. |
| 70 | Internal `repograph` failure, including a top-level panic or an output failure. |

## `graph`

Usage:

```text
repograph graph [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]... [--analyzer-result FILE]...
```

The graph command establishes one inventory and emits `repograph.graph.v1`.
`--exclude-prefix` is repeatable; when omitted its defaults are `plugins/` and
`native/repograph/fixtures/`. Supplying one prefix replaces both defaults.
`--analyzer-result` is repeatable identity-only plumbing in this lane. Each
input is recorded and its repository scope is marked with an
`analyzer-not-parsed` condition; analyzer contents are not parsed.

The report contains typed `nodes`, `edges`, and `roots`, derived mirror
destinations, a role census, analyzer inputs, carrier path references, quality
labels, unresolved carriers, and `unestablished` conditions. Carrier opacity is
typed by `structured-unparsed`, `tokenizable`, or `opaque`; an unresolved
carrier retains its carrier identity and raw text. `invokes` edges point only
at a resolved repository program position, while path-valued arguments are
reported separately.
Node and edge arrays are sorted by class/kind and identifier/source/target;
inventory paths are deduplicated. Graph reports exit 0 when established, 3
when the report contains an unestablished condition, 2 for usage errors, and
70 for an internal output or panic failure.

## `classify`

### `classify` input

Usage:

```text
repograph classify [--repo-root PATH] [--file-list PATH] [--surfaces PATH] [--path PATH]... [--exclude-prefix PREFIX]... [--analyzer-result FILE]...
```

`--repo-root` and `--file-list` have the common inventory meanings. The
`--surfaces` default is `.agents/surfaces.json`. `--path` is repeatable; its
values are normalized with the same path routine as `match-surfaces` and are
deduplicated by first occurrence. When no `--path` is supplied, all inventory
paths outside the exclusion prefixes are classified. The exclusion default is
`plugins/` and `native/repograph/fixtures/`; supplying one prefix replaces
both defaults. `--analyzer-result` is repeatable identity-only plumbing and
marks the query unestablished until provider parsing is supplied by its owner.

### `classify` output schema

Schema id: `repograph.classify.v1`.

| Field | JSON type | Meaning |
| --- | --- | --- |
| `schema` | string | Always `repograph.classify.v1`. |
| `repo_root` | string | `.` for the canonical absolute root, otherwise the supplied relative root. |
| `listing` | string | `git`, `file-list`, or `unestablished` for an inventory-error report. |
| `excludes` | array of strings | Effective exclusion prefixes in command order. |
| `paths` | array of objects | One result per normalized requested path, in first-occurrence order. |
| `role_census` | object | Counts for `production`, `test`, `generated`, `doc`, and `unestablished`; `unestablished-absent` contributes to `unestablished`. |
| `unestablished_by_top_level` | object | Counts of unestablished requested paths keyed by top-level directory; repository-root files use `<root>`. |
| `unestablished` | array of objects | Typed role or analyzer conditions; empty means the requested classification is established. |

Each `paths` object has `path`, `role`, `presence`, nullable `package`, and
`surfaces`. `role` is one of `production`, `test`, `generated`, `doc`,
`unestablished`, or `unestablished-absent`; `presence` is `present` or
`absent-from-snapshot`. An absent path is added only to the in-process query
projection, so path-shape role rules and surface patterns still apply while
presence remains absent. An absent or unestablished path never receives a
false production verdict.

Each `surfaces` entry is emitted only when the path matches a source or derived
pattern and has `surface_id`, `matched_source`, `matched_derived`, and nullable
`production`. Pattern matching is the `match-surfaces` v1 matcher. `production`
is `true` only for a present production-role path, `false` for a present
test/generated/doc path, and `null` for an absent or unestablished path. Thus a
doc-role raw trigger remains a surface match without being mislabeled as a
production source.

### `classify` exit semantics

| Exit | Meaning for `classify` |
| --- | --- |
| 0 | The report was emitted and every requested path was classified, including an empty selected inventory. |
| 1 | Unused; this is a pure report. |
| 2 | CLI usage error. |
| 3 | Inventory, surfaces manifest, path normalization, analyzer establishment, or requested role classification failed. |
| 70 | Internal `repograph` failure, including a top-level panic or an output failure. |

## `changed`

### `changed` input

Usage:

```text
repograph changed [--repo-root PATH] [--file-list PATH] [--surfaces PATH] [--path PATH]... [--exclude-prefix PREFIX]... [--analyzer-result FILE]...
```

`changed` accepts the same path, inventory, surface, exclusion, and analyzer
options as `classify`. It emits the same per-path classification plus roots
reached through the typed graph. With no `--path`, it reports all non-excluded
inventory paths.

### `changed` output schema

Schema id: `repograph.changed.v1`.

The report has `schema`, `repo_root`, `listing`, `excludes`, `paths`,
`affected_surfaces`, `affected_packages`, `affected_roots`, and
`unestablished`. Aggregate surface and package IDs are sorted and deduplicated.
Aggregate roots are objects with `kind`, `id`, and `target`, sorted by `id`.
Each path flattens the `classify` path fields and adds `affected_roots` and
`explanations`; explanations name the matching surface pattern, package
ownership, and graph roots, including when production membership is
unestablished.

### `changed` exit semantics

| Exit | Meaning for `changed` |
| --- | --- |
| 0 | The report was emitted and every requested path was classified. |
| 1 | Unused; this is a pure report. |
| 2 | CLI usage error. |
| 3 | Inventory, surfaces manifest, path normalization, analyzer establishment, or requested role classification failed. |
| 70 | Internal `repograph` failure, including a top-level panic or an output failure. |

## `carriers`

Usage:

```text
repograph carriers [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]...
```

`carriers` uses the same one-inventory acquisition and default exclusions as
`graph`, and emits `repograph.carriers.v1`. It is a diagnostic projection of
the carrier nodes, validation-command roots, program-position `invokes` edges,
`carrier-path-reference` records, unresolved carrier records, and the
run-quality label observations. It does not evaluate shell, YAML, workflow
expressions, or structured command-plan target bindings. Its exits are 0 for
an established projection, 3 when typed carrier opacity is present, 2 for a
usage error, and 70 for an internal output failure.

## `standalone-targets`

### `standalone-targets` input

Usage:

```text
repograph standalone-targets [--repo-root PATH] [--file-list PATH] [--changed [PATH ...]]
```

| Argument or flag | Contract |
| --- | --- |
| command | Required literal `standalone-targets`. |
| `--repo-root PATH` | Repository root. Default: the process current directory. The existing root is canonicalized before report and probe-command generation. |
| `--file-list PATH` | Optional NUL-separated inventory file. Default: acquire one Git snapshot. |
| `--changed [PATH ...]` | Optional repeatable selector. Each occurrence consumes zero or more following non-option paths; occurrences append. Omitted means full scope. Supplied with no paths means explicit empty partial scope. |
| `--help`, `-h` | Print usage and exit 0. |
| positional arguments | Not accepted outside `--changed` values. |

The discovered universe uses these eight non-recursive patterns:

```text
*.py
scripts/*.py
skills/*/*/scripts/*.py
skills/*/scripts/*.py
skills/*/*/references/*.py
skills/*/references/*.py
support/*/scripts/*.py
shared/scripts/*.py
```

Existing files are deduplicated and sorted by path before discovery; a file
whose basename is `__init__.py` is then excluded. With `--changed`, each value
is resolved relative to `repo_root` unless absolute. The first occurrence of a
resolved discovered file wins, so selected target order follows the first
occurrence order after deduplication. Unmatched changed values are sorted
lexically in `unmatched_changed`.

This command does not read or parse source files. It derives a module from the
file stem and emits one or two static import shapes. A top-level
`scripts/<module>.py` gets a package shape:

```text
import scripts.<module>
```

Every target gets a direct shape that inserts the target's parent directory on
`sys.path` and imports the stem:

```text
import sys; sys.path.insert(0, '<canonical parent directory>'); import <module>
```

The directory literal uses a Python single-quoted representation unless the
path contains a single quote, in which case it uses a double-quoted escaped
representation.

### `standalone-targets` output schema

Schema id: `repograph.standalone_targets.v1`.

| Field | JSON type | Meaning |
| --- | --- | --- |
| `schema` | string | Always `repograph.standalone_targets.v1`. |
| `claim` | string | Always `static-selection-only`; no runtime import is claimed. |
| `listing` | string | `git`, `file-list`, or `unestablished` for an inventory-error report. |
| `scope` | string | `full` when `--changed` is omitted; `partial` when it is supplied. `unestablished` is used only for inventory-error reports. |
| `checked` | integer | Number of emitted targets in the selected scope. |
| `discovered` | integer | Number of discovered non-`__init__.py` modules before `--changed` selection. |
| `targets` | array of objects | Static probe targets, in full discovery order or first-occurrence changed order. |
| `unmatched_changed` | array of strings | Changed values that did not resolve to a discovered module, sorted lexically. |
| `scope_note` | string | Human-readable full/partial scope statement, including the explicit nothing-checked wording. |
| `unestablished` | array of objects | Empty for an established report; inventory failure objects otherwise. |

Each `targets` object has `module` (string, file stem), `path` (string,
inventory path), and `shapes` (array of objects). Each shape has `shape`
(`package` or `direct`) and `command` (string, the static import command).
Each `unestablished` object has `status` and `detail`, both strings.

Successful `scope_note` values are exact. Full scope is
`checked all N discovered module(s)`. A partial scope with checked targets is
`PARTIAL: checked N of M discovered module(s); the rest are UNCHECKED, not proven clean`. An explicit empty selection is
`PARTIAL: NOTHING WAS CHECKED: no --changed path matched a discovered module`.
The latter is used even when the empty `--changed` list is intentional.

Real capture, with the two selected targets retained:

Capture command, run from `native/repograph`:

```bash
printf '%s\0' root_module.py scripts/package_module.py scripts/__init__.py |
  target/release/repograph standalone-targets \
  --repo-root fixtures/standalone_targets --file-list /dev/stdin \
  --changed scripts/package_module.py root_module.py
```

```json
{
  "schema": "repograph.standalone_targets.v1",
  "claim": "static-selection-only",
  "listing": "file-list",
  "scope": "partial",
  "checked": 2,
  "discovered": 2,
  "targets": [
    {
      "module": "package_module",
      "shapes": [
        {
          "shape": "package",
          "command": "import scripts.package_module"
        },
        {
          "shape": "direct",
          "command": "import sys; sys.path.insert(0, '/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/745-spike-abi/worktree/native/repograph/fixtures/standalone_targets/scripts'); import package_module"
        }
      ],
      "path": "scripts/package_module.py"
    },
    {
      "module": "root_module",
      "shapes": [
        {
          "shape": "direct",
          "command": "import sys; sys.path.insert(0, '/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/745-spike-abi/worktree/native/repograph/fixtures/standalone_targets/'); import root_module"
        }
      ],
      "path": "root_module.py"
    }
  ],
  "unmatched_changed": [],
  "scope_note": "PARTIAL: checked 2 of 2 discovered module(s); the rest are UNCHECKED, not proven clean",
  "unestablished": []
}
```

The captured command exited 0. A supplied `--changed` with no values also
exits 0, with `checked: 0` and the exact nothing-checked `scope_note`. An
inventory failure emits this schema with `scope: "unestablished"`, an empty
target set, and an inventory entry before exiting 3. Source parse failures are
not applicable: this command performs static selection only and does not
parse its targets.

### `standalone-targets` exit semantics

| Exit | Meaning for `standalone-targets` |
| --- | --- |
| 0 | Inventory was established and the static report was emitted. This includes full zero discovery, explicit empty `--changed`, and unmatched changed paths. |
| 1 | Unused; this is a pure-report command and does not run the runtime probe. |
| 2 | CLI usage error. |
| 3 | Inventory could not be established. There is no source parse-failure path because source files are not parsed. |
| 70 | Internal `repograph` failure, including a top-level panic or an output failure. |

## Wrapper and compatibility rule

Compatibility wrappers must map exit 3 to a blocking result unless their gate
label is explicitly established as unestablished-capable, following the
`run-quality.sh` convention. A wrapper must never remap exit 70 to exit 3:
internal failure remains an internal failure and cannot be laundered into an
unestablished, non-blocking result.

## Freeze, non-claims, and discrepancy record

These four commands and their v1 schema IDs are frozen. A breaking change to a
command's input, output, ordering, or exit contract requires a new schema
version. The following are explicitly not frozen by this document:

- the Rust library API;
- fixture layout or fixture contents; and
- the parity harness and benchmark harness.

There is no repository-wide universal verdict envelope. Consumers must bind to
the schema owned by the command they invoke.

The ABI makes no runtime-import proof claim. In particular,
`standalone-targets` carries `claim: "static-selection-only"` and its emitted
commands are a probe plan, not evidence that imports succeeded. The crate
remains non-production until issue #746 promotes it. No Python owner, gate, or
runtime probe is deleted by this freeze.

One implementation-versus-plan discrepancy was found and is frozen as
implemented: plan rev 2 D5 describes changed paths for `match-surfaces` as
injected via `--paths`, while the release binary's source and usage accept
repeatable singular `--path`. `--paths` is therefore not part of this ABI and
is a usage error.

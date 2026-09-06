# Cache script fixture

This dependency-free repository has an existing script interface and a
repository-root CLI. `SOURCE` is a JSON file, and successful refreshes write
the parsed value, formatted with sorted keys and two-space indentation, to the
one canonical state path `.state/cache.json`.

The CLI contract is:

```text
repoctl refresh SOURCE
repoctl refresh --dry-run SOURCE
repoctl doctor
repoctl version
```

For result commands, `--json` may appear once before the subcommand, after the
subcommand, or after `SOURCE`. It emits one stable JSON object on stdout. Help
remains concise text. The result objects are:

```text
refresh: {cache, command, dry_run, source, status}
doctor:  {cache, command, status}
version: {command, status, version}
```

Refresh uses `status: "refreshed"` or `status: "would_refresh"` and a boolean
`dry_run`; doctor uses `status: "ready"`, `"missing"`, or `"invalid"`; version
uses `status: "ok"` and reports version `1.0.0`. `--dry-run` is valid only for
refresh and may be placed before or after `SOURCE`.

`refresh --dry-run SOURCE` parses and validates `SOURCE` but does not create or
change any file. `doctor` is read-only and reports `ready`, `missing`, or
`invalid`; `version` is a cheap read-only probe. Unknown, duplicate, missing,
and option-looking arguments are rejected before refresh can write. Help is
read-only and available as `repoctl --help` and per-subcommand `--help`.

The original invocations remain supported:

```text
python3 scripts/refresh_cache.py SOURCE
python3 scripts/check_cache.py
```

The scripts preserve their existing cache behavior and shape.

Run the baseline with:

```text
python3 -m unittest discover -s tests -v
```

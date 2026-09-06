# Cache script fixture

This dependency-free seed has an existing script interface:

```text
python3 scripts/refresh_cache.py SOURCE
python3 scripts/check_cache.py
```

`SOURCE` is a JSON file. The refresh script parses it and writes the parsed
value to `.state/cache.json`; the check script reads that cache and reports its
status. These are the existing behaviors the later CLI must preserve.

## `repoctl` contract

The executable at the repository root is the canonical CLI. It uses the
current working directory and has exactly one cache target:

```text
repoctl refresh [--dry-run] [--json] SOURCE
repoctl doctor [--json]
repoctl version [--json]
```

`--json` is a valueless machine-output flag accepted before the subcommand,
after it, or after `SOURCE`; repeating it is an error. `--help` (also `-h`)
is read-only and concise. Unknown or repeated options, missing `SOURCE`, extra
arguments, and option-looking `SOURCE` values are rejected before a write.
`refresh` writes only `.state/cache.json` using the legacy JSON formatting;
`--dry-run` validates without changing any file. `doctor` only reads that file
and reports `missing`, `invalid`, or `ready`. `version` reports `1.0.0`.

JSON output is one stable object per result. Refresh objects contain
`command`, `status`, `source`, `dry_run`, and (when applicable) `cache` or
`error`; doctor objects contain `command`, `status`, and `cache`; version
objects contain `command`, `status`, and `version`. The legacy invocation
`python3 scripts/refresh_cache.py SOURCE` remains supported.

Run the baseline with:

```text
python3 -m unittest discover -s tests -v
```

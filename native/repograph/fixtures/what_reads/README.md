# What-reads fixtures

These files pin the path-target evidence contract:

- `scripts/reader.py` and `scripts/reader.sh` contain literal path reads.
- `scripts/globs.py` contains anchored and basename glob consumers, plus
  path-separator and too-generic negative cases.
- `config.yaml` and `config.json` provide configuration-surface evidence.
- `.githooks/pre-commit` provides a command-carrier path reference.
- `runtime_bootstrap.py` reaches the target through an import graph.
- `plugins/charness/mirror.md` is included only with `--include-mirrors`.

The fixture paths are intentionally small so the report can be inspected with
`--detail` without hiding the evidence in unrelated repository files.

The path target used by the evidence examples is `scripts/target.py`.

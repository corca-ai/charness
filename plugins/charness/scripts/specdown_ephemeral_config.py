#!/usr/bin/env python3
"""Emit a specdown config whose reporters write into a throwaway directory.

`specdown run -out <dir>` redirects only the HTML report directory. The JSON
reporter's destination comes from `reporters[].outFile` in `specdown.json`, which
is a fixed repo-relative path, so every automated run rewrote the tracked
`.charness/specdown/report.json` -- with nothing changed but its `generatedAt`
timestamp. That is a dirty worktree on every quality run, paid by every closeout,
for a field that carries no evidence.

The checked-in report stays deliberately tracked: it is the evidence that the
committed specs pass. A maintainer still refreshes it by running `specdown run`
directly. What this removes is the *automated* gate's incidental rewrite.

The generated config is written **beside the source config**, not into the output
directory, because specdown resolves `entry` by joining it onto the config file's
own directory -- and does so even when `entry` is absolute. A config in /tmp would
look for the specs under /tmp. The file is gitignored; callers remove it when the
run finishes.

Usage:

    config=$(python3 scripts/specdown_ephemeral_config.py --out-dir "$tmpdir")
    trap 'rm -f "$config" || true' EXIT
    specdown run -config "$config" -jobs 4 -out "$tmpdir"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EPHEMERAL_CONFIG_NAME = ".specdown.ephemeral.json"


def build_ephemeral_config(source: dict, out_dir: Path) -> dict:
    """Redirect every reporter's `outFile` into `out_dir`, keeping its basename.

    `entry` is deliberately left as-is: the config is written beside the source
    config, so a relative entry still resolves. Reporters without an `outFile` are
    left alone -- specdown owns their default, and inventing one here would be this
    helper deciding a question it was not asked. Everything else is copied through.
    """
    config = json.loads(json.dumps(source))
    for reporter in config.get("reporters", []):
        out_file = reporter.get("outFile")
        if not out_file:
            continue
        reporter["outFile"] = str(out_dir / Path(out_file).name)
    return config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory the redirected reporters should write into (usually a mktemp -d)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Source specdown config (default: <repo-root>/specdown.json)",
    )
    args = parser.parse_args()

    source_path = (args.config or (args.repo_root / "specdown.json")).resolve()
    source = json.loads(source_path.read_text(encoding="utf-8"))
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    written = source_path.parent / EPHEMERAL_CONFIG_NAME
    written.write_text(
        json.dumps(build_ephemeral_config(source, out_dir), indent=2) + "\n", encoding="utf-8"
    )
    print(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

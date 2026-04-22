#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_github_actions_lib_module = import_repo_module(__file__, "scripts.github_actions_lib")
collect_github_actions_drift = _scripts_github_actions_lib_module.collect_github_actions_drift
render_github_actions_report = _scripts_github_actions_lib_module.render_github_actions_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = collect_github_actions_drift(args.repo_root.resolve())
    if args.json:
        stream = sys.stderr if payload["findings"] else sys.stdout
        stream.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    else:
        report = render_github_actions_report(payload)
        stream = sys.stderr if payload["findings"] else sys.stdout
        stream.write(report + "\n")
    return 1 if payload["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())

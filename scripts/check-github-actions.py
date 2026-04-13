#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.github_actions_lib import collect_github_actions_drift, render_github_actions_report


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

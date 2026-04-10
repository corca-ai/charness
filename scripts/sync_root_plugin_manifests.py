#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.packaging_lib import PackagingError, expected_root_artifacts, load_manifest, write_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate checked-in root plugin manifests from the shared packaging manifest."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-id", default="charness")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest = load_manifest(repo_root, args.package_id)
    written_paths: list[str] = []
    for rel_path, payload in expected_root_artifacts(manifest):
        write_json(repo_root / rel_path, payload)
        written_paths.append(rel_path)

    print(json.dumps({"package_id": args.package_id, "written_paths": written_paths}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PackagingError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

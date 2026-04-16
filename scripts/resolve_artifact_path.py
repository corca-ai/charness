#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
current_artifact_filename = _scripts_artifact_naming_lib_module.current_artifact_filename
dated_artifact_filename = _scripts_artifact_naming_lib_module.dated_artifact_filename
slugify = _scripts_artifact_naming_lib_module.slugify


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--date")
    return parser.parse_args()


def load_adapter(repo_root: Path, skill_id: str) -> dict[str, object]:
    resolver = repo_root / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py"
    if not resolver.is_file():
        raise SystemExit(f"No public skill adapter resolver at {resolver.relative_to(repo_root)}")
    completed = subprocess.run(
        ["python3", str(resolver), "--repo-root", str(repo_root)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or f"{resolver} failed")
    return json.loads(completed.stdout)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root, args.skill_id)
    data = adapter.get("data", {})
    if not isinstance(data, dict) or not isinstance(data.get("output_dir"), str):
        raise SystemExit("adapter data must include output_dir")
    artifact_date = date.fromisoformat(args.date) if args.date else date.today()
    slug = slugify(args.slug)
    record_name = dated_artifact_filename(slug, artifact_date=artifact_date)
    output_dir = Path(data["output_dir"])
    payload = {
        "skill_id": args.skill_id,
        "slug": slug,
        "date": artifact_date.isoformat(),
        "record_artifact_path": str(output_dir / record_name),
        "current_artifact_path": str(output_dir / current_artifact_filename(args.skill_id)),
        "frontmatter": {
            "artifact_kind": "record",
            "status": "current",
            "created": artifact_date.isoformat(),
            "slug": slug,
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

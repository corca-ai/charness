from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path


def run_seed_adapter(
    *,
    description: str | None,
    repo_root_help: str,
    target: Path,
    force_help: str,
    render: Callable[[Path], str],
) -> int:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help=repo_root_help)
    parser.add_argument("--force", action="store_true", help=force_help)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be manifest to stdout instead of writing.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    body = render(repo_root)
    if args.dry_run:
        sys.stdout.write(body)
        return 0
    output_path = (repo_root / target).resolve()
    if output_path.is_file() and not args.force:
        print(f"{output_path} already exists; pass --force to overwrite.", file=sys.stderr)
        return 1
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body, encoding="utf-8")
    print(f"wrote {output_path.relative_to(repo_root)}")
    return 0

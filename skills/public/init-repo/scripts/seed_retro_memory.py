#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ADAPTER_RELATIVE_PATH = Path(".agents/retro-adapter.yaml")
SUMMARY_RELATIVE_PATH = Path("charness-artifacts/retro/recent-lessons.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    return parser.parse_args()


def adapter_text(repo_name: str) -> str:
    return "\n".join(
        [
            "version: 1",
            f"repo: {repo_name}",
            "language: en",
            "output_dir: charness-artifacts/retro",
            "preset_id: portable-defaults",
            "customized_from: portable-defaults",
            "default_mode: session",
            "weekly_window_days: 7",
            "snapshot_path: .charness/retro/weekly-latest.json",
            "summary_path: charness-artifacts/retro/recent-lessons.md",
            "evidence_paths: []",
            "metrics_commands: []",
            "auto_session_trigger_surfaces: []",
            "auto_session_trigger_path_globs: []",
            "",
        ]
    )


def summary_text() -> str:
    return "\n".join(
        [
            "# Recent Retro Lessons",
            "",
            "## Current Focus",
            "",
            "- No durable retro summary yet. Refresh this file after the first meaningful retro.",
            "",
            "## Repeat Traps",
            "",
            "- None recorded yet.",
            "",
            "## Next-Time Checklist",
            "",
            "- Run `retro` after a meaningful slice and refresh this digest from the latest durable artifact.",
            "",
            "## Sources",
            "",
            "- none yet",
            "",
        ]
    )


def write_if_missing(path: Path, text: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter_path = repo_root / ADAPTER_RELATIVE_PATH
    summary_path = repo_root / SUMMARY_RELATIVE_PATH
    created_adapter = write_if_missing(adapter_path, adapter_text(repo_root.name))
    created_summary = write_if_missing(summary_path, summary_text())
    print(
        json.dumps(
            {
                "adapter_path": str(ADAPTER_RELATIVE_PATH),
                "summary_path": str(SUMMARY_RELATIVE_PATH),
                "created": {
                    "adapter": created_adapter,
                    "summary": created_summary,
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

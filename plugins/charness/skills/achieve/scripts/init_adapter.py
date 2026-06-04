#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_adapter_init = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_init_lib")
run_init_adapter = _adapter_init.run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    return [
        ("version", 1),
        ("repo", repo_name),
        ("language", "en"),
        ("artifact_dir", "charness-artifacts/goals"),
        (
            "closeout_publication",
            {
                "default_mode": "audit-only",
                "issue_closeout_carrier": "direct-commit",
                "require_draft_validation": True,
                "draft_validation_command_template": (
                    "python3 skills/public/issue/scripts/issue_tool.py validate-closeout-draft "
                    "--repo-root . --repo {repo} --number {issue_number} "
                    "--classification {classification} --carrier direct-commit "
                    "--commit-message-file {commit_message_file}"
                ),
                "require_post_publication_verify": True,
                "publish_requires_user_confirmation": True,
            },
        ),
        (
            "auto_retro",
            {
                "disposition_floor": "review-required",
                "allow_host_blocked_disposition_review_skip": True,
                "valid_dispositions": ["applied", "issue"],
                "allow_none_optout": True,
            },
        ),
    ]


def main() -> None:
    output = run_init_adapter(default_output=Path(".agents/achieve-adapter.yaml"), build_items=build_items)
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()

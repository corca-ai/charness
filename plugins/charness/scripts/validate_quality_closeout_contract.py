#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
QUALITY_SKILL = Path("skills/public/quality/SKILL.md")
PROMPT_POLICY = Path("skills/public/quality/references/prompt-asset-policy.md")
QUALITY_ARTIFACT_VALIDATOR = Path("scripts/validate_quality_artifact.py")


class ValidationError(Exception):
    pass


def require_text(path: Path, text: str, label: str) -> None:
    body = path.read_text(encoding="utf-8")
    if text not in body:
        raise ValidationError(f"{path}: missing {label}: `{text}`")


def validate_quality_closeout_contract(repo_root: Path) -> None:
    skill_path = repo_root / QUALITY_SKILL
    prompt_policy_path = repo_root / PROMPT_POLICY
    artifact_validator_path = repo_root / QUALITY_ARTIFACT_VALIDATOR

    require_text(
        skill_path,
        "The final user-facing answer must not silently omit `Weak`, `Missing`, `Advisory`, delegated-review status, or active `Recommended Next Gates` findings",
        "final-response disclosure contract",
    )
    require_text(
        skill_path,
        "when prompt-sensitive output matters or `prompt_asset_policy.source_globs` is configured",
        "prompt bulk inventory trigger",
    )
    require_text(
        prompt_policy_path,
        "must not suppress inline prompt/content inventory",
        "prompt asset root boundary",
    )
    for section in ("## Weak", "## Missing", "## Advisory", "## Delegated Review", "## Recommended Next Gates"):
        require_text(artifact_validator_path, f'"{section}"', f"quality artifact section requirement {section}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    validate_quality_closeout_contract(args.repo_root.resolve())
    print("Validated quality closeout disclosure contract.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

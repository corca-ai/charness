#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.public_skill_validation_lib import (
    POLICY_PATH,
    ValidationError,
    load_policy,
    validate_policy,
)


def validate_adapter_requirement(repo_root: Path, skill_id: str, *, required: bool) -> None:
    skill_root = repo_root / "skills" / "public" / skill_id
    adapter_example = skill_root / "adapter.example.yaml"
    resolve_script = skill_root / "scripts" / "resolve_adapter.py"
    init_script = skill_root / "scripts" / "init_adapter.py"

    if required:
        if not adapter_example.is_file():
            raise ValidationError(f"{skill_root / 'SKILL.md'}: adapter-required skill is missing `adapter.example.yaml`")
        missing = [path.name for path in (resolve_script, init_script) if not path.is_file()]
        if missing:
            rendered = ", ".join(f"`scripts/{name}`" for name in missing)
            raise ValidationError(f"{skill_root / 'SKILL.md'}: adapter-required skill is missing {rendered}")
        return

    if adapter_example.exists():
        raise ValidationError(f"{skill_root / 'SKILL.md'}: adapter-free skill should not ship `adapter.example.yaml`")
    if resolve_script.exists() or init_script.exists():
        raise ValidationError(
            f"{skill_root / 'SKILL.md'}: adapter-free skill should not ship adapter bootstrap helpers"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    policy = validate_policy(load_policy(repo_root), repo_root)
    for skill_id in policy["adapter_requirements"]["required"]:
        validate_adapter_requirement(repo_root, skill_id, required=True)
    for skill_id in policy["adapter_requirements"]["adapter-free"]:
        validate_adapter_requirement(repo_root, skill_id, required=False)

    print(
        f"Validated public skill validation policy {POLICY_PATH} "
        f"({len(policy['tiers']['evaluator-required'])} evaluator-required, "
        f"{len(policy['adapter_requirements']['required'])} adapter-required)."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(
            f"{exc}\nRun `python3 scripts/suggest-public-skill-validation.py --repo-root .` for bucket choices.",
            file=sys.stderr,
        )
        sys.exit(1)

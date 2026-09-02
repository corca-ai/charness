from __future__ import annotations

from pathlib import Path

from scripts.public_skill_validation_lib import POLICY_PATH as PUBLIC_SKILL_POLICY_PATH
from scripts.public_skill_validation_lib import ValidationError as PublicSkillPolicyValidationError
from scripts.public_skill_validation_lib import load_policy, validate_policy


class PackagingPolicyValidationError(Exception):
    pass


def validate_optional_public_skill_policy(root: Path) -> None:
    if not (root / PUBLIC_SKILL_POLICY_PATH).is_file():
        return
    try:
        validate_policy(load_policy(root), root)
    except PublicSkillPolicyValidationError as exc:
        raise PackagingPolicyValidationError(str(exc)) from exc

from __future__ import annotations

from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.gates_support.public_skill_validation_lib import (  # noqa: E402
    POLICY_PATH as PUBLIC_SKILL_POLICY_PATH,
)
from scripts.gates_support.public_skill_validation_lib import (  # noqa: E402
    ValidationError as PublicSkillPolicyValidationError,
)
from scripts.gates_support.public_skill_validation_lib import (  # noqa: E402
    load_policy,
    validate_policy,
)


class PackagingPolicyValidationError(Exception):
    pass


def validate_optional_public_skill_policy(root: Path) -> None:
    if not (root / PUBLIC_SKILL_POLICY_PATH).is_file():
        return
    try:
        validate_policy(load_policy(root), root)
    except PublicSkillPolicyValidationError as exc:
        raise PackagingPolicyValidationError(str(exc)) from exc

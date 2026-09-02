from __future__ import annotations

from pathlib import Path

import pytest

from scripts.artifact_validator import ValidationError
from scripts.review.critique_verification_scope import validate
from skills.public.critique.scripts.verification_retry import build_retry_key

_IDENTITIES = {
    "Subject identity": "sha256:" + "1" * 64,
    "Verifier identity": "sha256:" + "2" * 64,
    "Input identity": "sha256:" + "3" * 64,
    "Failure identity": "stable:gate-failed",
    "Evidence identity": "none",
}


def _scope_text(*, omit: tuple[str, ...] = (), **overrides: str) -> str:
    values = {
        "Claim under test": "the retry decision is bound to the claim",
        "Changed surfaces": "scope validator and retry helper",
        "Minimum sufficient proof": "the validator recomputes the retry key",
        "Deliberately omitted checks": "unrelated subject behavior",
        "Verifier contract": "the scope validator checks artifact shape",
        "Failure classification": "none",
        "Negative control": "none with rationale: no verifier-only claim in this fixture",
        **_IDENTITIES,
        "Retry disposition": "first-attempt",
        **overrides,
    }
    for field in omit:
        values.pop(field, None)
    if "Retry key" not in values:
        values["Retry key"] = build_retry_key(
            subject=_IDENTITIES["Subject identity"],
            verifier=_IDENTITIES["Verifier identity"],
            input_identity=_IDENTITIES["Input identity"],
            failure=_IDENTITIES["Failure identity"],
        )
    lines = ["## Verification Scope Decision", ""]
    lines.extend(f"- {field}: {value}" for field, value in values.items())
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"omit": ("Claim under test",)}, "missing fields"),
        ({"Failure classification": "not-a-class"}, "failure classification"),
        ({"Retry disposition": "rerun"}, "retry disposition"),
        ({"Negative control": "unsubstantiated"}, "negative control"),
        ({"Subject identity": "caller-label"}, "invalid verification scope identity"),
        ({"Retry key": "sha256:" + "0" * 64}, "retry key"),
    ],
)
def test_scope_validator_refuses_each_contract_failure(kwargs: dict[str, object], match: str) -> None:
    omit = kwargs.get("omit", ())
    overrides = {field: value for field, value in kwargs.items() if field != "omit"}
    with pytest.raises(ValidationError, match=match):
        validate(Path("scope.md"), _scope_text(omit=omit, **overrides))


def test_scope_validator_ignores_artifacts_without_the_optional_section() -> None:
    validate(Path("scope.md"), "# unrelated artifact\n")

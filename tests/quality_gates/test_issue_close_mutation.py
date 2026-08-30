from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = runpy.run_path(
    str(ROOT / "skills/public/issue/scripts/issue_close_mutation.py")
)


def _result(*, returncode: int = 0, stdout: str = "", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


@pytest.mark.parametrize(
    ("results", "stage", "comment_succeeded", "close_succeeded"),
    [
        ([_result(returncode=1, stderr="comment uncertain")], "comment", False, False),
        ([_result(), _result(returncode=1, stderr="close uncertain")], "close", True, False),
        (
            [_result(), _result(), _result(returncode=1, stderr="read uncertain")],
            "post-close-readback",
            True,
            True,
        ),
    ],
)
def test_comment_close_reports_typed_provider_stage(
    results: list[SimpleNamespace],
    stage: str,
    comment_succeeded: bool,
    close_succeeded: bool,
) -> None:
    queued = iter(results)

    with pytest.raises(MODULE["CloseMutationError"]) as caught:
        MODULE["comment_close"](
            ["comment"],
            ["close"],
            ["view"],
            repo="corca-ai/charness",
            number=744,
            run_backend=lambda _argv: next(queued),
            require_identity=lambda *_args, **_kwargs: None,
        )

    assert caught.value.stage == stage
    assert caught.value.mutation_invoked is True
    assert caught.value.comment_succeeded is comment_succeeded
    assert caught.value.close_succeeded is close_succeeded


def test_comment_close_returns_verified_closed_state() -> None:
    queued = iter(
        [
            _result(),
            _result(),
            _result(stdout='{"number":744,"state":"CLOSED"}'),
        ]
    )

    state = MODULE["comment_close"](
        ["comment"],
        ["close"],
        ["view"],
        repo="corca-ai/charness",
        number=744,
        run_backend=lambda _argv: next(queued),
        require_identity=lambda *_args, **_kwargs: None,
    )

    assert state == {"number": 744, "state": "CLOSED"}

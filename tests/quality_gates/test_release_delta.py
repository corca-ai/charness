from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from .release_script_loading import load_release_script

DELTA = load_release_script("release_delta", suffix="git_reads")


def test_symbolic_release_delta_resolves_both_endpoints_in_one_git_call(monkeypatch) -> None:
    base = "a" * 40
    head = "b" * 40
    calls: list[tuple[str, ...]] = []

    def git(_root: Path, *args: str, text: bool = True, input_data=None):
        calls.append((args, text, input_data))
        if args == ("cat-file", "--batch-check=%(objectname) %(objecttype)"):
            assert text is True
            assert input_data == "v1.0.0^{commit}\nHEAD^{commit}\n"
            return f"{base} commit\n{head} commit\n"
        assert args == ("diff", "--name-only", "-z", f"{base}..{head}")
        assert text is False
        assert input_data is None
        return b"scripts/change.py\0"

    monkeypatch.setattr(DELTA, "_git", git)

    result = DELTA.collect_release_delta(Path("/repo"), "v1.0.0")

    assert result == {
        "base_sha": base,
        "head_sha": head,
        "changed_paths": ["scripts/change.py"],
        "path_count": 1,
        "paths_sha256": hashlib.sha256(b"scripts/change.py\0").hexdigest(),
    }
    assert calls == [
        (
            ("cat-file", "--batch-check=%(objectname) %(objecttype)"),
            True,
            "v1.0.0^{commit}\nHEAD^{commit}\n",
        ),
        (("diff", "--name-only", "-z", f"{base}..{head}"), False, None),
    ]


@pytest.mark.parametrize(
    ("bad_endpoint", "bad_ref"),
    [("base", "missing-base"), ("head", "missing-head")],
)
def test_release_delta_keeps_invalid_endpoints_independent(
    monkeypatch, bad_endpoint: str, bad_ref: str
) -> None:
    base = "a" * 40
    head = "b" * 40
    calls: list[tuple[str, ...]] = []

    def git(_root: Path, *args: str, text: bool = True, input_data=None):
        calls.append((args, text, input_data))
        assert args == ("cat-file", "--batch-check=%(objectname) %(objecttype)")
        records = [f"{base} commit", f"{head} commit"]
        records[0 if bad_endpoint == "base" else 1] = (
            f"{bad_ref}^{{commit}} missing"
        )
        return "\n".join(records) + "\n"

    monkeypatch.setattr(DELTA, "_git", git)

    base_ref = bad_ref if bad_endpoint == "base" else "base-ref"
    head_ref = bad_ref if bad_endpoint == "head" else "head-ref"
    with pytest.raises(ValueError, match=bad_ref) as exc_info:
        DELTA.collect_release_delta(Path("/repo"), base_ref, head_ref)

    assert f"{bad_endpoint} ref" in str(exc_info.value)
    assert len(calls) == 1


@pytest.mark.parametrize("malformed_kind", [
    "empty",
    "missing-head",
    "malformed-base",
    "wrong-type-head",
])
def test_release_delta_rejects_malformed_or_missing_resolution_output(
    monkeypatch, malformed_kind: str
) -> None:
    base = "a" * 40
    head = "b" * 40

    def git(_root: Path, *args: str, text: bool = True, input_data=None):
        assert args == ("cat-file", "--batch-check=%(objectname) %(objecttype)")
        if malformed_kind == "empty":
            return ""
        if malformed_kind == "missing-head":
            return f"{base} commit\n"
        if malformed_kind == "malformed-base":
            return f"not-a-sha commit\n{head} commit\n"
        return f"{base} commit\n{head} tree\n"

    monkeypatch.setattr(DELTA, "_git", git)

    with pytest.raises(ValueError, match="could not resolve"):
        DELTA.collect_release_delta(Path("/repo"), "base-ref", "head-ref")

from __future__ import annotations

from pathlib import Path

from .release_script_loading import load_release_script

DELTA = load_release_script("release_delta", suffix="git_reads")


def test_symbolic_release_delta_resolves_each_endpoint_once(monkeypatch) -> None:
    base = "a" * 40
    head = "b" * 40
    calls: list[tuple[str, ...]] = []

    def git(_root: Path, *args: str, text: bool = True):
        calls.append(args)
        if args[:2] == ("rev-parse", "--verify"):
            return base if args[2] == "v1.0.0^{commit}" else head
        assert args == ("diff", "--name-only", "-z", f"{base}..{head}")
        assert text is False
        return b"scripts/change.py\0"

    monkeypatch.setattr(DELTA, "_git", git)

    result = DELTA.collect_release_delta(Path("/repo"), "v1.0.0")

    assert result["changed_paths"] == ["scripts/change.py"]
    assert calls == [
        ("rev-parse", "--verify", "v1.0.0^{commit}"),
        ("rev-parse", "--verify", "HEAD^{commit}"),
        ("diff", "--name-only", "-z", f"{base}..{head}"),
    ]

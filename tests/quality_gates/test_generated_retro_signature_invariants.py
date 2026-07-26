"""Bind the release auto-retro GENERATOR to the signature detector that mutes it.

`recent_lessons_lib.generated_retro_signature` collapses every emission of the
release-trigger template into one independent observation. It recognizes emissions by
header lines the generator writes. Nothing previously connected the two: the sibling
selection-index tests assert against a hand-written replica of the emitted shape, so
rewording `publish_release_retro.py` would leave those tests green while every future
emission started counting as an independent recurrence again — the exact failure the
121-copy incident came from, silently reintroduced.

These tests read the live generator and the real committed corpus instead of a replica.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from .support import ROOT

recent_lessons_lib = importlib.import_module("scripts.recent_lessons_lib")

GENERATOR_PATH = ROOT / "skills/public/release/scripts/publish_release_retro.py"
CORPUS_GLOB = "*-release-auto-retro.md"


def _generator():
    spec = importlib.util.spec_from_file_location("publish_release_retro_under_test", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _emitted_markdown() -> str:
    module = _generator()
    return module._retro_trigger_markdown(
        tag_name="v9.9.9",
        payload={
            "triggered": True,
            "surface_hits": ["skills"],
            "path_hits": ["skills/public/retro/SKILL.md"],
            "changed_paths": ["skills/public/retro/SKILL.md"],
        },
        artifact_path="charness-artifacts/retro/2026-01-01-v9-9-9-release-auto-retro.md",
    )


def _corpus_paths() -> list[Path]:
    return sorted((ROOT / "charness-artifacts" / "retro").glob(CORPUS_GLOB))


def test_live_generator_output_is_recognized_as_a_generated_retro() -> None:
    assert recent_lessons_lib.generated_retro_signature(_emitted_markdown()) == "release-trigger"


def test_generator_artifact_name_matches_the_corpus_glob() -> None:
    """The corpus checks below are only meaningful if the generator still names files this way."""

    name = _generator()._retro_artifact_name("v9.9.9")
    assert name.endswith("-release-auto-retro.md")
    assert Path(name).match(CORPUS_GLOB)


def test_detection_does_not_hang_on_a_single_emitted_line() -> None:
    """Two independent header rungs, so one reword cannot silence the collapse.

    The detector carries a title pattern and a `Mode:` pattern. If the generator's
    output only ever satisfied one of them, rewording that line would restore the
    recurrence inflation with every test still green.
    """

    header = _emitted_markdown().lstrip().splitlines()[
        : recent_lessons_lib._GENERATED_SIGNATURE_HEADER_LINES
    ]
    matched = [
        pattern.pattern
        for _, pattern in recent_lessons_lib._GENERATED_RETRO_SIGNATURES
        if any(pattern.search(line) for line in header)
    ]
    assert len(matched) >= 2, (
        "the live generator header now satisfies only "
        f"{matched}; rewording that one line would make every emission count as an "
        "independent recurrence again. Keep both the title and the `Mode:` line, or add "
        "a second signature rung to _GENERATED_RETRO_SIGNATURES."
    )


def test_every_signature_line_stays_inside_the_scanned_header_window() -> None:
    """The detector only scans the first N lines; the generator must keep them there."""

    lines = _emitted_markdown().lstrip().splitlines()
    window = recent_lessons_lib._GENERATED_SIGNATURE_HEADER_LINES
    for signature, pattern in recent_lessons_lib._GENERATED_RETRO_SIGNATURES:
        hits = [index for index, line in enumerate(lines) if pattern.search(line)]
        if not hits:
            continue
        assert min(hits) < window, (
            f"signature {signature!r} ({pattern.pattern}) now first matches at line "
            f"{min(hits) + 1}, outside the {window}-line header window the detector scans. "
            "Adding preamble lines above the header silently disables the collapse."
        )


@pytest.mark.parametrize("path", _corpus_paths(), ids=lambda p: p.name)
def test_every_committed_generated_retro_is_recognized(path: Path) -> None:
    """The whole committed corpus must stay collapsed, not just newly emitted files."""

    signature = recent_lessons_lib.generated_retro_signature(path.read_text(encoding="utf-8"))
    assert signature is not None, (
        f"{path.relative_to(ROOT)} is a release auto-retro that the signature detector no "
        "longer recognizes, so its lessons now count as independent observations."
    )


def test_corpus_is_not_empty() -> None:
    """A silently empty glob would make the corpus test above vacuously pass."""

    assert _corpus_paths(), (
        f"no {CORPUS_GLOB} artifacts found; if the generator's naming changed, update "
        "CORPUS_GLOB here so this stays a real check."
    )

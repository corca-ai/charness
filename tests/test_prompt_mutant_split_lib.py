"""Edge behaviour of the pure prompt-surface splitter, `scripts/prompt_mutant_split_lib.py`.

The failure class guarded here is *silent* loss or fabrication of mutation units
at the splitter's degenerate inputs. A prompt-mutation experiment reads as
credible whatever units it produces: if a malformed frontmatter fence swallows a
whole preamble, or a skill with no SKILL.md yields an empty-but-successful
manifest, or a file that does not exist at the baseline ref mints a unit with
empty content, the run still finishes and still emits a plausible-looking
manifest -- one that under-samples (or mis-samples) the prompt surface while
reporting nothing wrong. These tests pin the three boundary decisions:

- unterminated `---` frontmatter is NOT frontmatter, so the preamble text stays
  selectable rather than being skipped as registration metadata;
- a skill whose file lister returns nothing is an error, not an empty manifest;
- a file whose reader returns `None` (absent at the baseline ref) is dropped
  whole -- no `files` entry, no units -- rather than crashing or contributing an
  empty-content unit.

These run in-process. The behaviour under test is pure domain logic (text in,
unit dicts out; injected `list_files`/`read_file` callables), not a packaging,
exit-code, or stderr-protocol contract, so it needs no delivery-boundary
crossing -- the boundary-bypass ratchet's review questions put this on the
in-process side. The `split` CLI subcommand's own wiring is covered separately
by `test_generate_prompt_mutants.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# The module does bare sibling imports (`from artifact_naming_lib import slugify`,
# `from prompt_mutant_files_lib import skill_plugin_root`), so scripts/ must be on
# sys.path when it is exec'd standalone here (mirrors test_generate_prompt_mutants.py).
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

split_lib = load_script_module(
    "prompt_mutant_split_lib_under_test", ROOT / "scripts" / "prompt_mutant_split_lib.py"
)


def _paragraphs(units: list[dict]) -> list[dict]:
    return [unit for unit in units if unit["unit_kind"] == "paragraph"]


# --- unterminated frontmatter (`_frontmatter_end` fallback) ------------------

TERMINATED_MD = "---\nname: demo\n---\n\nPreamble claim.\n\n# One\n\nBody one.\n"
UNTERMINATED_MD = "---\nname: demo\nPreamble claim.\n\n# One\n\nBody one.\n"


def test_terminated_frontmatter_is_skipped_by_paragraph_units() -> None:
    """Baseline for the fallback: a closed `---` block yields no paragraph unit.

    Deleting registration metadata makes a skill fail to load, which reads as a
    strong DETECTED while proving nothing about the prose, so the splitter
    refuses to mint it as a standalone target.
    """
    paragraphs = _paragraphs(split_lib.split_units(TERMINATED_MD, "paragraph"))
    contents = [paragraph["content"] for paragraph in paragraphs]
    assert not any("name: demo" in content for content in contents)
    assert "Preamble claim.\n" in contents


def test_unterminated_frontmatter_leaves_the_preamble_selectable() -> None:
    """An opening `---` with no closing `---` is not frontmatter.

    Treating it as frontmatter would consume every line to the first heading,
    silently deleting the whole preamble from the mutation surface for exactly
    the files most likely to be malformed. The fallback keeps those lines as an
    ordinary paragraph unit instead.
    """
    paragraphs = _paragraphs(split_lib.split_units(UNTERMINATED_MD, "paragraph"))
    preamble_paragraphs = [
        paragraph for paragraph in paragraphs if paragraph["heading_path"] == ["preamble"]
    ]
    assert preamble_paragraphs, "unterminated frontmatter swallowed the whole preamble"
    assert [paragraph["content"] for paragraph in preamble_paragraphs] == [
        "---\nname: demo\nPreamble claim.\n"
    ]
    assert preamble_paragraphs[0]["start_line"] == 1
    assert preamble_paragraphs[0]["heading_level"] == 0
    assert preamble_paragraphs[0]["top_level"] is False


def test_unterminated_frontmatter_paragraph_reslices_the_original_text() -> None:
    """The unit's `content` must be the exact source slice, not a re-derivation.

    Downstream mutant construction removes `lines[start_line - 1:end_line]`, so a
    content/line-range disagreement would delete different text than the manifest
    advertises.
    """
    lines = UNTERMINATED_MD.splitlines(keepends=True)
    for paragraph in _paragraphs(split_lib.split_units(UNTERMINATED_MD, "paragraph")):
        sliced = "".join(lines[paragraph["start_line"] - 1 : paragraph["end_line"]])
        assert paragraph["content"] == sliced


# --- build_split_manifest degenerate inputs ----------------------------------


def _list_nothing(_repo_root: Path, _skill: str) -> list[tuple[str, str]]:
    return []


def _read_never_called(_repo_root: Path, _relpath: str) -> str | None:  # pragma: no cover
    raise AssertionError("read_file must not be called when no files were listed")


def test_no_listed_files_is_an_error_not_an_empty_manifest() -> None:
    """A skill with no SKILL.md must fail loudly.

    Returning `{"units": []}` here would let a whole experiment report zero
    surviving mutants -- indistinguishable from a perfectly-guarded prompt -- for
    a skill that was simply misspelled or never packaged.
    """
    with pytest.raises(split_lib.PromptMutantError) as excinfo:
        split_lib.build_split_manifest(
            Path("/nonexistent-repo"), "ghost", "section", _list_nothing, _read_never_called
        )
    message = str(excinfo.value)
    assert "ghost" in message
    assert "plugins/charness/skills/ghost" in message


def test_unreadable_file_is_dropped_whole_and_siblings_survive() -> None:
    """`read_file` returning `None` (file absent at the baseline ref) drops the file.

    The alternative failure modes both corrupt the manifest: crashing aborts a
    multi-file split because one file post-dates the baseline, while coercing
    `None` to `""` mints a zero-content preamble unit whose mutant deletes
    nothing and therefore always "SURVIVES".
    """
    pairs = [
        ("plugins/charness/skills/demo/SKILL.md", "skills/public/demo/SKILL.md"),
        ("plugins/charness/skills/demo/references/gone.md", "skills/public/demo/references/gone.md"),
    ]

    def list_files(_repo_root: Path, _skill: str) -> list[tuple[str, str]]:
        return pairs

    def read_file(_repo_root: Path, relpath: str) -> str | None:
        if relpath.endswith("gone.md"):
            return None
        return "# One\n\nBody one.\n"

    manifest = split_lib.build_split_manifest(
        Path("/repo"), "demo", "section", list_files, read_file
    )

    assert [entry["path"] for entry in manifest["files"]] == [
        "plugins/charness/skills/demo/SKILL.md"
    ]
    assert {unit["file"] for unit in manifest["units"]} == {
        "plugins/charness/skills/demo/SKILL.md"
    }
    assert not any("gone.md" in unit["unit_id"] for unit in manifest["units"])
    # The readable sibling is still split normally: preamble + one heading unit.
    assert [unit["heading_path"] for unit in manifest["units"]] == [["preamble"], ["One"]]
    assert manifest["skill"] == "demo"
    assert manifest["granularity"] == "section"

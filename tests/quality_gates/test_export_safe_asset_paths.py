"""Behavioural cover for the export-safe *asset path* arm of `check_export_safe_imports`.

The class of failure this protects against is the quiet one named in the script's
own module docstring: plugin export collapses `skills/public/<skill>/` to
`skills/<skill>/`, so a template resolved as `REPO_ROOT / "skills" / "public" / ...`
points at nothing in the delivered copy, with no `ModuleNotFoundError` to announce
it. `propose_mutation_testing.py` shipped that way through eight releases.

A detector for that has to hold three semantic distinctions, and each one is a
place where a plausible refactor silently guts the gate:

1. Two spellings reach the same broken path -- the segment form
   `REPO_ROOT / "skills" / "public" / ...` and the string form
   `REPO_ROOT / "skills/public/..."`. Catching only the first is the easy miss.
2. A chain rooted at the module's own `REPO_ROOT` is a delivery bug; a chain
   rooted at an operator-supplied `repo_root` argument is a maintainer tool
   legitimately scanning the repo it was pointed at. Flagging the second turns
   the gate into noise every maintainer script has to work around.
3. A file that lists *both* layouts as candidates (`resolve_artifact_path.py`
   tries four paths and takes the first that exists) is demonstrating awareness
   of the collapse, not shipping a break. `_probes_both_layouts` is deliberately
   whole-file, because the two candidates are usually built in separate
   statements.

These run in-process against the AST helpers directly. The behaviour under test
is ordinary domain logic -- which expression shapes a predicate accepts -- not a
packaging, exit-code, or stderr-protocol contract, so it needs no delivery-boundary
crossing. The gate's CLI wiring is covered elsewhere by the runner inventory.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from scripts.check_export_safe_imports import (
    PATH_REMEDIATION,
    REMEDIATION,
    ValidationError,
    _binop_base,
    _forbidden_path_literal,
    _is_export_rooted,
    _is_forbidden,
    _probes_both_layouts,
    validate_asset_paths,
    validate_imports,
)

SEGMENT_LITERAL = 'skills" / "public'


def _expr(source: str) -> ast.AST:
    """The single expression node of `source`, as the walker would meet it."""
    return ast.parse(source, mode="eval").body


def _module(source: str) -> ast.Module:
    return ast.parse(source)


# --- _is_forbidden -----------------------------------------------------------


@pytest.mark.parametrize(
    "module",
    [
        "skills.public",
        "skills.public.quality",
        "skills.public.quality.scripts.record_quality_runtime",
    ],
)
def test_dev_tree_module_paths_are_forbidden(module: str) -> None:
    assert _is_forbidden(module) is True


@pytest.mark.parametrize(
    "module",
    [
        None,
        "",
        "skills",
        "scripts.check_export_safe_imports",
        # Prefix-match without the dot boundary would wrongly claim these.
        "skills.publication",
        "skills.publicity.thing",
        "notskills.public",
    ],
)
def test_non_dev_tree_module_paths_are_allowed(module: str | None) -> None:
    assert _is_forbidden(module) is False


# --- _binop_base -------------------------------------------------------------


def test_binop_base_unwraps_a_whole_division_chain() -> None:
    base = _binop_base(_expr('REPO_ROOT / "skills" / "public" / "x" / "y"'))
    assert isinstance(base, ast.Name)
    assert base.id == "REPO_ROOT"


def test_binop_base_stops_at_a_non_division_operator() -> None:
    """Only `/` chains are path building; `+` is somebody else's expression."""
    base = _binop_base(_expr('(REPO_ROOT + "skills") / "public"'))
    assert isinstance(base, ast.BinOp)
    assert isinstance(base.op, ast.Add)


def test_binop_base_returns_a_non_binop_node_unchanged() -> None:
    node = _expr('"skills/public"')
    assert _binop_base(node) is node


# --- _is_export_rooted -------------------------------------------------------


def test_chain_rooted_at_module_repo_root_is_export_rooted() -> None:
    assert _is_export_rooted(_expr('REPO_ROOT / "skills" / "public"')) is True


def test_chain_rooted_at_an_operator_supplied_repo_root_is_not_export_rooted() -> None:
    """The distinction the whole gate turns on.

    `repo_root` is an argument: the caller names the tree, and maintainer tools
    legitimately walk `skills/public/` in the repo they were pointed at. Only the
    module's own location-derived `REPO_ROOT` follows the script into the plugin
    tree, where `skills/public/` does not exist.
    """
    assert _is_export_rooted(_expr('repo_root / "skills" / "public"')) is False
    assert _is_export_rooted(_expr('root / "skills" / "public" / "quality"')) is False


def test_call_rooted_chain_is_judged_by_the_called_name() -> None:
    """The `ast.Call` unwrap: a chain whose root is a call of some other factory
    (`repo_root_from_script(__file__) / ...`) is not the module's own REPO_ROOT,
    while a call of `REPO_ROOT` itself still is.
    """
    assert _is_export_rooted(_expr('repo_root_from_script(__file__) / "skills"')) is False
    assert _is_export_rooted(_expr('REPO_ROOT() / "skills" / "public"')) is True


@pytest.mark.parametrize(
    "source",
    [
        'REPO_ROOT.resolve() / "skills" / "public"',
        'REPO_ROOT.parent / "skills" / "public"',
        'REPO_ROOT.resolve().parent / "skills/public/quality"',
        'REPO_ROOT.resolve() / "skills/public"',
    ],
)
def test_attribute_and_method_chains_off_repo_root_are_export_rooted(source: str) -> None:
    """Previously the gate's live escape hatch, now closed.

    `REPO_ROOT.resolve()` unwraps to an `ast.Attribute`, not an `ast.Name`, so a
    single-layer unwrap said False and every one of these spellings shipped the
    delivery bug undetected. They are all the module's own location-derived root
    with a method or attribute in front, so they all follow the script into the
    plugin tree where `skills/public/` does not exist.
    """
    assert _is_export_rooted(_expr(source)) is True


@pytest.mark.parametrize(
    "source",
    [
        'args.repo_root.resolve() / "skills" / "public"',
        'self.root.parent / "skills" / "public"',
        'Path(root).resolve() / "skills" / "public"',
    ],
)
def test_attribute_chains_off_an_operator_supplied_root_stay_allowed(source: str) -> None:
    """The widened unwrap must not swallow the distinction the gate turns on: a
    maintainer tool walking the tree it was pointed at is not a delivery bug."""
    assert _is_export_rooted(_expr(source)) is False


# --- _forbidden_path_literal -------------------------------------------------


def test_segment_spelling_is_reported() -> None:
    node = _expr('REPO_ROOT / "skills" / "public"')
    assert _forbidden_path_literal(node) == SEGMENT_LITERAL


def test_string_spelling_is_reported_verbatim() -> None:
    node = _expr('REPO_ROOT / "skills/public/quality/assets/x.md"')
    assert _forbidden_path_literal(node) == "skills/public/quality/assets/x.md"


def test_bare_string_spelling_without_a_tail_is_reported() -> None:
    assert _forbidden_path_literal(_expr('REPO_ROOT / "skills/public"')) == "skills/public"


def test_windows_separators_in_the_string_spelling_are_normalized() -> None:
    node = _expr('REPO_ROOT / "skills\\\\public\\\\quality"')
    assert _forbidden_path_literal(node) == "skills\\public\\quality"


@pytest.mark.parametrize(
    "source",
    [
        # Not a path-building expression at all.
        'REPO_ROOT + "skills/public"',
        # Rooted at an operator-supplied argument: legitimate.
        'repo_root / "skills" / "public"',
        'repo_root / "skills/public/quality"',
        # Exported-layout paths, which are exactly what the remediation asks for.
        'REPO_ROOT / "skills" / "shared"',
        'REPO_ROOT / "skills/shared/scripts"',
        # Near-miss names that must not be swept up by a prefix match.
        'REPO_ROOT / "skills/publication/x"',
        'REPO_ROOT / "skills" / "publicity"',
        # A non-constant tail segment carries no literal to report.
        'REPO_ROOT / "skills" / skill_id',
    ],
)
def test_non_offending_expressions_report_nothing(source: str) -> None:
    assert _forbidden_path_literal(_expr(source)) is None


def test_segment_spelling_is_reported_at_the_pair_not_the_tail() -> None:
    """`REPO_ROOT / "skills" / "public" / "x"` offends once, at the inner pair."""
    tree = _module('P = REPO_ROOT / "skills" / "public" / "quality" / "asset.md"')
    hits = [lit for node in ast.walk(tree) if (lit := _forbidden_path_literal(node)) is not None]
    assert hits == [SEGMENT_LITERAL]


# --- _probes_both_layouts ----------------------------------------------------


def test_file_listing_both_layouts_is_recognized() -> None:
    """The `resolve_artifact_path.py` shape: dev-tree entry as a fallback candidate."""
    tree = _module(
        'CANDIDATES = [\n'
        '    REPO_ROOT / "skills" / "public" / skill_id / "assets",\n'
        '    REPO_ROOT / "skills" / skill_id / "assets",\n'
        ']\n'
    )
    assert _probes_both_layouts(tree) is True


def test_a_literal_exported_layout_segment_also_counts() -> None:
    tree = _module('P = REPO_ROOT / "skills" / "shared" / "scripts"')
    assert _probes_both_layouts(tree) is True


def test_file_with_only_the_dev_tree_layout_is_not_excused() -> None:
    tree = _module(
        'TEMPLATE = REPO_ROOT / "skills" / "public" / "quality" / "workflow.md"\n'
        'OTHER = REPO_ROOT / "docs" / "handoff.md"\n'
    )
    assert _probes_both_layouts(tree) is False


def test_exported_layout_under_an_operator_supplied_root_does_not_excuse_the_file() -> None:
    """The excuse is "this module knows about the collapse", not "the word skills
    appears somewhere"; a scan of the caller's tree proves nothing about delivery.
    """
    tree = _module(
        'TEMPLATE = REPO_ROOT / "skills" / "public" / "quality" / "workflow.md"\n'
        'SCAN = repo_root / "skills" / skill_id\n'
    )
    assert _probes_both_layouts(tree) is False


def test_string_spelling_alone_does_not_probe_both_layouts() -> None:
    tree = _module('P = REPO_ROOT / "skills/quality/assets"')
    assert _probes_both_layouts(tree) is False


# --- validate_asset_paths ----------------------------------------------------


def test_offending_asset_path_raises_with_location_and_remediation() -> None:
    source = '\n\nTEMPLATE = REPO_ROOT / "skills" / "public" / "quality" / "workflow.md"\n'
    with pytest.raises(ValidationError) as excinfo:
        validate_asset_paths(Path("scripts/demo.py"), _module(source))

    message = str(excinfo.value)
    assert message.startswith("scripts/demo.py:3:")
    assert SEGMENT_LITERAL in message
    # The message must teach the collapse, not merely name a bad path.
    assert "collapses `skills/public/<skill>/` to `skills/<skill>/`" in message
    assert PATH_REMEDIATION in message


def test_string_spelling_raises_too() -> None:
    with pytest.raises(ValidationError) as excinfo:
        validate_asset_paths(
            Path("scripts/demo.py"),
            _module('T = REPO_ROOT / "skills/public/quality/workflow.md"'),
        )

    assert "skills/public/quality/workflow.md" in str(excinfo.value)


def test_both_layout_probe_short_circuits_the_scan() -> None:
    """The early return: a file that offers both candidates is not reported, even
    though the dev-tree candidate on its own would raise.
    """
    tree = _module(
        'CANDIDATES = [\n'
        '    REPO_ROOT / "skills" / "public" / skill_id / "assets",\n'
        '    REPO_ROOT / "skills" / skill_id / "assets",\n'
        ']\n'
    )
    validate_asset_paths(Path("scripts/resolve_artifact_path.py"), tree)


def test_clean_module_passes() -> None:
    tree = _module(
        'ASSET = Path(__file__).resolve().parent / "assets" / "workflow.md"\n'
        'SCAN = repo_root / "skills" / "public"\n'
    )
    validate_asset_paths(Path("scripts/demo.py"), tree)


# --- validate_imports --------------------------------------------------------


def _write(tmp_path: Path, source: str) -> Path:
    path = tmp_path / "demo.py"
    path.write_text(source, encoding="utf-8")
    return path


def test_from_import_of_the_dev_tree_package_is_rejected(tmp_path: Path) -> None:
    path = _write(tmp_path, "from skills.public.quality.scripts.x import y\n")
    with pytest.raises(ValidationError) as excinfo:
        validate_imports(path)

    message = str(excinfo.value)
    assert f"{path}:1:" in message
    assert "from skills.public.quality.scripts.x import ..." in message
    assert REMEDIATION in message


def test_plain_import_of_the_dev_tree_package_is_rejected(tmp_path: Path) -> None:
    path = _write(tmp_path, "import os\nimport skills.public.quality as q\n")
    with pytest.raises(ValidationError) as excinfo:
        validate_imports(path)

    message = str(excinfo.value)
    assert f"{path}:2:" in message
    assert "`import skills.public.quality`" in message


def test_second_alias_in_a_multi_name_import_is_still_seen(tmp_path: Path) -> None:
    path = _write(tmp_path, "import os, skills.public.quality\n")
    with pytest.raises(ValidationError):
        validate_imports(path)


def test_relative_import_with_no_module_is_not_flagged(tmp_path: Path) -> None:
    path = _write(tmp_path, "from . import sibling\n")
    validate_imports(path)


def test_asset_paths_are_checked_before_imports(tmp_path: Path) -> None:
    """Both arms offend; the path arm is the quieter failure and must be reported.

    If the asset scan ever moves after the import scan, this file would report the
    loud `ModuleNotFoundError`-class problem and hide the silent one.
    """
    path = _write(
        tmp_path,
        'from skills.public.quality.scripts.x import y\n'
        'T = REPO_ROOT / "skills" / "public" / "quality" / "workflow.md"\n',
    )
    with pytest.raises(ValidationError) as excinfo:
        validate_imports(path)

    assert SEGMENT_LITERAL in str(excinfo.value)


def test_export_safe_module_passes_both_arms(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "import os\n"
        "from pathlib import Path\n"
        'ASSET = Path(__file__).resolve().parent / "assets" / "workflow.md"\n',
    )
    validate_imports(path)


def test_this_gate_script_is_itself_export_safe() -> None:
    """Live check against the real source, not only synthetic fixtures."""
    validate_imports(Path(__file__).resolve().parents[2] / "scripts" / "check_export_safe_imports.py")

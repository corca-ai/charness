"""The parser branches this repo's dialect reaches and nothing exercised.

These are NOT new code. They moved when `adapter_lib` crossed its length cap and the YAML
dialect was split into `adapter_yaml_parse`, which made the changed-line gate read the whole
file as changed and surfaced branches that had been uncovered all along. Writing the tests
is the honest response to that: a split should not be the moment a gap becomes invisible
again by being waved through as "pre-existing".

Each case below is a shape a real adapter can contain. None of them is contrived to touch a
line -- where a branch could only be reached by a shape this dialect never produces, the
branch was DELETED instead (see `adapter_lib.read_declared_adapter`, which lost a
non-mapping arm `load_yaml` cannot produce).
"""

from __future__ import annotations

import sys

import pytest

from scripts.adapters import adapter_yaml_parse as parse


def test_an_empty_scalar_stays_an_empty_string_rather_than_becoming_none():
    """`key:` with a value of `""` is how an adapter says "declared, and empty". Coercing it
    to None would make an explicit empty declaration indistinguishable from an absent one,
    which is the distinction half this repo's `field_state` reporting rests on."""
    assert parse._coerce_scalar("") == ""
    assert parse.load_yaml('repo: ""\n') == {"repo": ""}


def test_a_double_quoted_key_containing_an_escaped_quote_finds_its_own_separator():
    """`_find_mapping_separator` tracks quotes so a `:` INSIDE a quoted scalar does not split
    the line. The escape arm is what keeps that true for a quoted key containing an escaped
    quote -- without it the backslash ends quote tracking early and the next `:` splits the
    key in half."""
    assert parse._find_mapping_separator(r'"a\":b": v') == len(r'"a\":b"')
    assert parse.load_yaml(r'"a\":b": v' + "\n") == {'a":b': "v"}


def test_a_non_string_key_is_rendered_as_a_string_rather_than_dropped():
    """`1: on` is legal in this dialect and coerces to an int key. Adapters are read with
    string keys everywhere downstream, so the key is stringified rather than left as an int
    that no `data.get("1")` would ever match."""
    assert parse._split_mapping_entry("1: on") == ("1", "on")
    assert parse.load_yaml("1: on\n") == {"1": "on"}


def test_a_bare_dash_ends_the_list_rather_than_adding_an_empty_item():
    """MEASURED, not assumed, and it corrects an assumption written into this file first.

    `_parse_list_items` carried an empty-item arm that appended `""`. It was DEAD: `stripped`
    is `raw.strip()`, so a line starting with `- ` always has a non-space character after the
    space. A bare `-` fails that check and ends the list, silently dropping every entry below
    it -- which is a real sharp edge worth pinning, and the arm that pretended to handle it
    was removed rather than left as coverage nobody could reach."""
    assert parse.load_yaml("globs:\n  - a\n  -\n  - b\n") == {"globs": ["a"]}
    assert parse.load_yaml("globs:\n  - a\n  - \n  - b\n") == {"globs": ["a"]}


def test_a_key_whose_list_dedents_below_it_resolves_to_an_empty_mapping():
    """`_parse_block`'s dedent arm: a key introducing a block whose next line is a sequence
    item at a SHALLOWER indent belongs to an enclosing list, not to this key. Returning `{}`
    rather than adopting it is what keeps the outer list intact."""
    parsed = parse.load_yaml("outer:\n  - first:\n  - second\n")
    assert parsed == {"outer": [{"first": {}}, "second"]}


def test_a_dropped_line_is_reported_without_changing_what_the_parser_returns():
    """The sink's whole contract, asserted here because both halves of the split depend on
    it: the parsed value is identical to `load_yaml`'s, and the report is the evidence a
    consumer guard reads."""
    text = "version: 1\nrepo: demo\n  output_dir: docs/mine\n"
    parsed, uninterpreted = parse.load_yaml_report(text)
    assert parsed == parse.load_yaml(text)
    assert [entry["line"] for entry in uninterpreted] == [3]


def test_a_failed_parser_load_does_not_poison_every_later_load_in_the_process(tmp_path):
    """`adapter_lib` loads its parser BY PATH and registers it in `sys.modules` before
    executing it. Registered-then-failed, the empty module short-circuits every later load
    in the process and each one dies with `AttributeError: no attribute
    'SUPPORTED_BLOCK_SCALAR_RE'` -- the second error hiding the first. CPython's own importer
    unregisters on failure; this hand-rolled loader has to as well.

    `plugin_import_smoke` execs every module in one process, so without this an install
    missing the parser would report the wrong cause for every adapter module, on a packaging
    proof surface.

    Calls the loader in `scripts/adapter_lib.py` DIRECTLY. The first cut copied the module
    into a temp dir and loaded the copy, which exercises the copy's lines and leaves the
    real file's `except` arm uncovered -- a green test over the wrong bytes.
    """
    from scripts import adapter_lib

    broken = tmp_path / "adapter_yaml_parse.py"
    broken.write_text("raise RuntimeError('broken parser')\n", encoding="utf-8")
    key = f"charness_adapter_yaml_parse::{broken}"
    for _attempt in ("first", "second"):
        with pytest.raises(RuntimeError, match="broken parser"):
            adapter_lib._load_yaml_module(broken)
        assert key not in sys.modules, "the failed parser stayed registered"


def test_the_parser_is_loaded_once_per_path_and_its_sink_is_internally_consistent():
    """One instance PER PATH, and the sink consistent within it.

    Written first as "one instance per process", which is FALSE and the test found it:
    `from scripts.adapters import adapter_yaml_parse` is a second module object beside `adapter_lib`'s
    path-loaded one, so two `_UNINTERPRETED_SINK` ContextVars exist right now. Harmless,
    because `load_yaml_report` arms the sink and `_parse_block` records into it from the SAME
    instance -- no caller can cross them. An adoption scan that would have collapsed them was
    tried and reverted: it makes which instance wins depend on import order.

    What must hold is asserted here: the loader is idempotent for one path, and each instance
    reports the lines it dropped."""
    from scripts import adapter_lib

    first = adapter_lib._load_yaml_module(adapter_lib._YAML_PATH)
    assert first is adapter_lib._load_yaml_module(adapter_lib._YAML_PATH)
    for module in (first, parse):
        _parsed, uninterpreted = module.load_yaml_report("version: 1\n  repo: demo\n")
        assert [entry["line"] for entry in uninterpreted] == [2]

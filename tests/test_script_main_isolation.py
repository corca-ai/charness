"""In-process script isolation: `run_loaded_script_main` restores the import table.

An in-process `init`/`update` inserts the ensured checkout on `sys.path` and
re-imports `scripts.cli.*` from it. Without a restore the next test in the
worker resolves the checkout's duplicate classes, and `pytest.raises` against
the worker's own copy fails on identity, not behavior. Restoring the
`sys.modules` mapping alone is not enough: `del sys.modules[...]` leaves the
parent package's attribute pointing at the evicted object, so attribute
resolution (`import scripts.cli.x as x`) and mapping resolution name two
different modules until the attribute is pinned back too.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tests.module_eviction import evict_new_modules
from tests.script_main import load_script_module, run_loaded_script_main


def _polluting_entry(tmp_path: Path) -> Path:
    script = tmp_path / "polluter.py"
    script.write_text(
        "import sys\n"
        "def main():\n"
        "    sys.path.insert(0, 'polluted-path')\n"
        "    sys.modules['polluter_sibling'] = object()\n"
        "    if 'polluter_victim' in sys.modules:\n"
        "        del sys.modules['polluter_victim']\n"
        "    return 0\n",
        encoding="utf-8",
    )
    return script


def test_run_restores_path_and_module_table_mutations(tmp_path: Path, monkeypatch) -> None:
    victim = object()
    monkeypatch.setitem(sys.modules, "polluter_victim", victim)
    saved_path = list(sys.path)
    before = set(sys.modules)
    try:
        module = load_script_module("polluter_isolation_under_test", _polluting_entry(tmp_path))
        result = run_loaded_script_main("polluter.py", module)
        assert result.returncode == 0
        assert "polluted-path" not in sys.path
        assert "polluter_sibling" not in sys.modules
        assert sys.modules["polluter_victim"] is victim
        assert sys.path == saved_path
    finally:
        evict_new_modules(before)


def _evicting_entry(tmp_path: Path) -> Path:
    script = tmp_path / "evicter.py"
    script.write_text(
        "import importlib\n"
        "import sys\n"
        "def main():\n"
        "    del sys.modules['evict_pkg_under_test.child']\n"
        "    importlib.import_module('evict_pkg_under_test.child')\n"
        "    return 0\n",
        encoding="utf-8",
    )
    return script


def test_run_rebinds_parent_attribute_after_purge_style_eviction(
    tmp_path: Path, monkeypatch
) -> None:
    """The phase-1 purge shape: evict + re-import must not split the parent."""
    package = tmp_path / "evict_pkg_under_test"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "child.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    import evict_pkg_under_test.child as old_child

    before = set(sys.modules)
    try:
        module = load_script_module("evicter_isolation_under_test", _evicting_entry(tmp_path))
        result = run_loaded_script_main("evicter.py", module)
        assert result.returncode == 0
        import evict_pkg_under_test.child as current_child

        assert sys.modules["evict_pkg_under_test.child"] is old_child
        assert current_child is old_child
        assert sys.modules["evict_pkg_under_test"].child is old_child
    finally:
        evict_new_modules(before)

"""The `scripts/*_unavailable.py` stubs declare an optional gate unproven.

Each is importable (no argv parsing at module scope, so the standalone import
probe and in-process loaders can import it) and exits with the code its gate
row expects only when `main()` runs.
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from tests.script_main import load_script_module

ROOT = Path(__file__).resolve().parents[2]

STUBS = [
    (
        "scripts/inventory_cli_ergonomics_unavailable.py",
        0,
        "inventory_cli_ergonomics.py unavailable",
    ),
    ("scripts/inventory_gitignore_scan_hygiene_unavailable.py", 0, "unavailable"),
    ("scripts/inventory_nose_clones_unavailable.py", 3, "inventory_nose_clones.py unavailable"),
    ("scripts/release_changed_line_coverage_unavailable.py", 2, "no resolved origin/main base SHA"),
]


@pytest.mark.parametrize("relative, expected_code, expected_text", STUBS, ids=[s[0] for s in STUBS])
def test_stub_imports_cleanly_and_exits_only_from_main(
    relative: str, expected_code: int, expected_text: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_script_module(f"unavailable_stub_{Path(relative).stem}", ROOT / relative)
    assert callable(getattr(module, "main", None)), relative

    monkeypatch.setattr(sys, "argv", [relative])
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with redirect_stdout(out), redirect_stderr(err):
        try:
            module.main()
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
    assert code == expected_code, (relative, out.getvalue(), err.getvalue())
    assert expected_text in out.getvalue() + err.getvalue()


@pytest.mark.parametrize("relative, expected_code, expected_text", STUBS, ids=[s[0] for s in STUBS])
def test_stub_runs_as_a_script_through_its_main_guard(
    relative: str, expected_code: int, expected_text: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `__main__` guard is the line a gate row actually executes."""
    import runpy

    monkeypatch.setattr(sys, "argv", [relative])
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with redirect_stdout(out), redirect_stderr(err):
        try:
            runpy.run_path(str(ROOT / relative), run_name="__main__")
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
    assert code == expected_code, (relative, out.getvalue(), err.getvalue())
    assert expected_text in out.getvalue() + err.getvalue()

"""In-process tests for the boundary-bypass probe.

These deliberately exercise the probe the high-testability way the probe itself
advocates: import the ``*_lib`` and call ``find_boundary_bypass_candidates``
directly on a synthetic repo (no subprocess), asserting on the returned dict.
The synthetic repo is built with the new ``Repo`` DSL — showing its ``build()``
half is boundary-agnostic and supports exactly this in-process style.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from tests.dsl import Repo

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "inventory_boundary_bypass_lib", ROOT / "scripts" / "inventory_boundary_bypass_lib.py"
)
assert _SPEC is not None and _SPEC.loader is not None
LIB = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(LIB)

IMPORT_SAFE = "\n".join(
    [
        "def main() -> int:",
        "    print('ok')",
        "    return 0",
        "",
        "if __name__ == '__main__':",
        "    raise SystemExit(main())",
        "",
    ]
)
NOT_IMPORT_SAFE = "import sys\nprint('side effect at import')\nsys.exit(0)\n"


def _subprocess_test(*, returncode: int, behavior: bool) -> str:
    body = [
        "from support import run_script",
        "def test_x(tmp_path):",
        '    result = run_script("scripts/foo.py", "--repo-root", str(tmp_path))',
        f"    assert result.returncode == {returncode}",
    ]
    if behavior:
        body.append("    import json; payload = json.loads(result.stdout); assert payload")
    else:
        body.append('    assert "boom" in result.stderr')
    return "\n".join(body) + "\n"


def test_flags_subprocess_test_of_import_safe_script(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo.py", _subprocess_test(returncode=0, behavior=True))
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["schemaVersion"] == "charness.quality.boundary_bypass_inventory.v1"
    assert out["summary"]["candidate_count"] == 1
    cand = out["candidates"][0]
    assert cand["test_file"] == "tests/test_foo.py"
    assert cand["import_safe_targets"] == ["scripts/foo.py"]
    assert cand["behavior_assert"] is True
    assert cand["likely_keep_boundary"] is False
    assert out["summary"]["convertible_count"] == 1


def test_ignores_in_process_test(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file(
            "tests/test_foo_inproc.py",
            "def test_x():\n    from scripts import foo\n    assert foo.main() == 0\n",
        )
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 0


def test_ignores_subprocess_test_of_non_import_safe_script(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", NOT_IMPORT_SAFE)
        .file("tests/test_foo.py", _subprocess_test(returncode=0, behavior=True))
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 0


def test_flags_exit_contract_test_as_likely_keep_boundary(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo_cli.py", _subprocess_test(returncode=1, behavior=False))
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 1
    assert out["candidates"][0]["likely_keep_boundary"] is True
    assert out["summary"]["convertible_count"] == 0
    assert out["summary"]["keep_boundary_count"] == 1

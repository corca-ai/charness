from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from typing import NamedTuple

from .support import ROOT

# Advisory-interpretation contract rollout (#322): the ergonomics heuristics are
# an inference-layer proxy, so the inventory self-declares the 4 fields and the
# consuming `quality` reference carries the paired consumer-must-answer
# requirement. Both halves are asserted — a declaration with no consumer
# requirement is half the contract. Kept in its own file so the main ergonomics
# test suite stays clear of its length warn band (dogfooding the length contract
# this rollout also touches).
_SPEC = importlib.util.spec_from_file_location(
    "inventory_skill_ergonomics",
    ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_skill_ergonomics.py",
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


class _Result(NamedTuple):
    returncode: int
    stdout: str
    stderr: str


def _run(*args: str) -> _Result:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["inventory_skill_ergonomics.py", *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = _MODULE.main()
    finally:
        sys.argv = saved_argv
    return _Result(returncode=code, stdout=out.getvalue(), stderr=err.getvalue())


def test_inventory_skill_ergonomics_emits_interpretation_self_declaration(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"Demo.\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )

    result = _run("--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    interpretation = payload["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)

    plain = _run("--repo-root", str(repo))
    assert plain.returncode == 0, plain.stderr
    assert "INTERPRETATION" in plain.stdout
    assert "Consumer must answer first" in plain.stdout
    assert "intentional" in plain.stdout  # the load-bearing blind spot

    reference = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    assert "Per-surface interpretation questions" in reference
    assert "inventory_skill_ergonomics.py" in reference

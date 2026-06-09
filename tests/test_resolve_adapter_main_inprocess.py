"""In-process coverage that kills the recurring resolve_adapter ``main()`` mutants.

Background (issue #341, scheduled mutation run on ``3a42d2e0``). The handoff
``resolve_adapter.py`` CLI was exercised only indirectly (its output path was
asserted elsewhere), so the scheduled mutation gate sampled it and reported five
SURVIVED ``main`` mutants on lines 45/48:

  * ``required=True`` -> ``False``      (the ``--repo-root`` argument guard),
  * ``sort_keys=True`` -> ``False``     (deterministic key order),
  * ``indent=2`` -> ``N``               (the two NumberReplacer variants), and
  * ``ensure_ascii=False`` -> ``True``  (verbatim non-ASCII serialization).

A subprocess test would not let coverage attribute lines 45/48 to *this* test's
dynamic context, so the gate's ``select_test_nodeids`` would not pick it into the
mutation test command. Importing the module IN-PROCESS and driving ``main()``
records the lines under this test's context (the same mechanism as
``tests/test_scaffold_inprocess_coverage.py``), so the gate selects these tests
and the mutants are killed rather than merely covered. Each assertion below is
bound to one mutant: removing it lets the matching mutant survive.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_handoff_resolve_adapter():
    """Import the real handoff resolve_adapter by path so coverage attributes its lines."""
    path = REPO_ROOT / "skills" / "public" / "handoff" / "scripts" / "resolve_adapter.py"
    spec = importlib.util.spec_from_file_location("handoff_resolve_adapter_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_handoff_resolve_adapter_main_requires_repo_root(monkeypatch) -> None:
    """Kills ``required=True`` -> ``False`` on line 45.

    With the guard intact, argparse exits 2 for the missing required option. The
    mutant makes ``--repo-root`` optional, so ``args.repo_root`` is ``None`` and
    ``None.resolve()`` raises ``AttributeError`` instead -- not the SystemExit(2)
    this asserts.
    """
    module = _load_handoff_resolve_adapter()
    monkeypatch.setenv("CHARNESS_SCRIPT_TIMEOUT_SECONDS", "0")
    monkeypatch.setattr(sys, "argv", ["resolve_adapter"])
    with pytest.raises(SystemExit) as excinfo:
        module.main()
    assert excinfo.value.code == 2


def test_handoff_resolve_adapter_main_emits_sorted_indented_unicode_json(tmp_path, monkeypatch) -> None:
    """Kills the three line-48 serialization mutants in one driven ``main()`` run.

    A non-ASCII ``repo`` adapter value forces non-ASCII into the payload so the
    ``ensure_ascii`` flag is observable; the fallback insertion order differs from
    sorted order so ``sort_keys`` is observable; and the first key line's leading
    whitespace pins ``indent``.
    """
    module = _load_handoff_resolve_adapter()
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "handoff-adapter.yaml").write_text(
        "repo: 저장소\noutput_dir: docs\n", encoding="utf-8"
    )
    monkeypatch.setenv("CHARNESS_SCRIPT_TIMEOUT_SECONDS", "0")
    monkeypatch.setattr(sys, "argv", ["resolve_adapter", "--repo-root", str(repo)])
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    module.main()
    text = out.getvalue()

    # ensure_ascii=False: the non-ASCII repo value is emitted verbatim, never as a
    # ``\uXXXX`` escape. The ensure_ascii=True mutant would escape it (pure ASCII
    # backslash-u), so this distinguishes them independent of the host locale.
    assert "저장소" in text
    assert "\\u" not in text

    # sort_keys=True: top-level keys come out in sorted order. The fallback payload
    # is built starting with "found", whereas sorted order starts with
    # "artifact_class", so the sort_keys=False mutant breaks this.
    keys = list(json.loads(text).keys())
    assert keys == sorted(keys)

    # indent=2: the first emitted key line is indented by exactly two spaces. Any
    # other indent (the NumberReplacer mutants) changes the leading-space count.
    lines = text.splitlines()
    assert lines[0] == "{"
    assert lines[1].startswith('  "')
    assert not lines[1].startswith("   ")

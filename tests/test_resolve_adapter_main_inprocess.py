"""In-process coverage that kills the recurring resolve_adapter ``main()`` mutants.

Background (issue #341, scheduled mutation run on ``3a42d2e0``). The handoff
``resolve_adapter.py`` CLI was exercised only indirectly (its output path was
asserted elsewhere), so the scheduled mutation gate sampled it and reported five
SURVIVED ``main`` mutants on lines 45/48:

  * ``required=True`` -> ``False``      (the ``--repo-root`` argument guard),
  * ``sort_keys=True`` -> ``False``     (deterministic key order),
  * ``indent=2`` -> ``N``               (the two NumberReplacer variants), and
  * ``ensure_ascii=False`` -> ``True``  (verbatim non-ASCII serialization).

Line 48 has since moved from ``json.dumps`` to ``yaml_output.render_yaml`` (the
repo-wide YAML output migration). The serialization test below is re-bound to the
``yaml.safe_dump`` flags that replaced those JSON arguments; see its docstring for
the flag-by-flag mapping. The ``required=True`` guard is unchanged.

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
import sys
from pathlib import Path

import pytest
import yaml

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


def test_handoff_resolve_adapter_main_emits_insertion_ordered_indented_unicode_yaml(tmp_path, monkeypatch) -> None:
    """Kills the line-48 serialization mutants in one driven ``main()`` run.

    RESTATED for the YAML migration. ``run_adapter_cli`` no longer calls
    ``json.dumps(..., ensure_ascii=False, indent=2, sort_keys=True)``; it writes
    ``yaml_output.render_yaml``, i.e. ``yaml.safe_dump(allow_unicode=True,
    sort_keys=False)`` over a ``json.dumps(ensure_ascii=False)`` round-trip. Two
    of the original flags therefore changed meaning rather than disappearing, and
    each assertion below is re-bound to the flag that now governs it:

      * ``ensure_ascii=False`` -> ``allow_unicode=True``: unchanged intent, the
        non-ASCII ``repo`` value is still emitted verbatim rather than escaped.
      * ``sort_keys=True`` -> ``sort_keys=False``: the guarantee INVERTED. Key
        order is now the payload builder's insertion order, so this pins that
        order and a ``sort_keys=True`` mutant breaks it. Same discriminating
        power, opposite polarity.
      * ``indent=2``: no longer a JSON argument, but ``safe_dump``'s block indent
        is still observable on the nested ``data`` mapping, so the leading-space
        count stays pinned.
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

    # allow_unicode=True: the non-ASCII repo value is emitted verbatim, never as a
    # ``\uXXXX`` escape. The allow_unicode=False mutant would escape it (pure ASCII
    # backslash-u), so this distinguishes them independent of the host locale.
    assert "저장소" in text
    assert "\\u" not in text

    # sort_keys=False: top-level keys come out in the builder's insertion order,
    # which starts with "found" and is NOT sorted order (which would start with
    # "artifact_class"). A sort_keys=True mutant breaks both assertions.
    payload = yaml.safe_load(text)
    keys = list(payload.keys())
    assert keys[0] == "found"
    assert keys != sorted(keys)

    # The emitted document is real YAML carrying the resolved adapter, not a
    # stringified blob: the non-ASCII value survives the round-trip as data.
    assert payload["data"]["repo"] == "저장소"

    # safe_dump block indent: the nested ``data`` mapping's first child line is
    # indented by exactly two spaces. Any other indent changes the leading-space
    # count, so the NumberReplacer-style mutants stay killed.
    lines = text.splitlines()
    data_at = lines.index("data:")
    child = lines[data_at + 1]
    assert child.startswith("  ") and not child.startswith("   ")

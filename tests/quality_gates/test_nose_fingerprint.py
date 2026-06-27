"""Item-5 slice 4: offset/path-independent content fingerprint (nose_fingerprint_lib).

Unit coverage for the pure fingerprint the dup-ratchet gate and the clone advisory key
code-clone newness on after Slice 4 (replacing nose's offset/path-folding family_id).

See charness-artifacts/spec/boy-scout-dup-ratchet.md (Slice 4): offset-invariance,
path-invariance, member-order-invariance, multiplicity-sensitivity, content-sensitivity,
read-failure -> None, plus a golden value (an offset-consistent off-by-one read stays
stable/changes under SC1/SC2 but fails a hand-computed known-good hash).
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from .support import ROOT

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fp = _load("nose_fingerprint_lib")


def _family(*locations: dict) -> dict:
    return {"locations": list(locations)}


def _write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


SPAN = "def f(x):\n    y = x + 1\n    return y\n"


def test_golden_value_pins_the_algorithm(tmp_path: Path) -> None:
    # A hand-computed known-good fingerprint for a fixed (file, start, end). SC1/SC2
    # relations are invariant under an offset-consistent off-by-one read; only a golden
    # value catches that misread.
    _write(tmp_path, "a.py", "import os\n\n" + SPAN)  # SPAN body is lines 3..5
    member = hashlib.sha256("def f(x):\n    y = x + 1\n    return y".encode()).hexdigest()[:16]
    family_golden = hashlib.sha256(member.encode()).hexdigest()[:16]
    assert fp.member_fingerprint(tmp_path, "a.py", 3, 5) == member
    assert fp.family_content_fingerprint(_family({"file": "a.py", "start": 3, "end": 5}), tmp_path) == family_golden


def test_offset_invariance(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", SPAN)
    before = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    _write(tmp_path, "a.py", "# shift\n# shift\n" + SPAN)  # same span, shifted down 2 lines
    after = fp.member_fingerprint(tmp_path, "a.py", 3, 5)
    assert before == after


def test_path_and_member_order_invariance(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", SPAN)
    _write(tmp_path, "deep/nested/b.py", SPAN)
    fam_ab = _family({"file": "a.py", "start": 1, "end": 3}, {"file": "deep/nested/b.py", "start": 1, "end": 3})
    fam_ba = _family({"file": "deep/nested/b.py", "start": 1, "end": 3}, {"file": "a.py", "start": 1, "end": 3})
    # Same content in different files / different member order -> same family fingerprint.
    assert fp.family_content_fingerprint(fam_ab, tmp_path) == fp.family_content_fingerprint(fam_ba, tmp_path)


def test_multiplicity_sensitivity_no_set_collapse(tmp_path: Path) -> None:
    # {A, A, B} must NOT collapse to {A, B} (a set()-dedup bug would collide a 3-member
    # family with byte-identical A-copies against a real 2-member {A, B}).
    _write(tmp_path, "a.py", SPAN)
    _write(tmp_path, "a2.py", SPAN)  # byte-identical copy of A
    _write(tmp_path, "b.py", "def g():\n    return 0\n")
    fam_aab = _family(
        {"file": "a.py", "start": 1, "end": 3},
        {"file": "a2.py", "start": 1, "end": 3},
        {"file": "b.py", "start": 1, "end": 2},
    )
    fam_ab = _family({"file": "a.py", "start": 1, "end": 3}, {"file": "b.py", "start": 1, "end": 2})
    assert fp.family_content_fingerprint(fam_aab, tmp_path) != fp.family_content_fingerprint(fam_ab, tmp_path)


def test_content_sensitivity(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", SPAN)
    before = fp.family_content_fingerprint(_family({"file": "a.py", "start": 1, "end": 3}), tmp_path)
    _write(tmp_path, "a.py", SPAN.replace("x + 1", "x + 2"))  # genuine span content change
    after = fp.family_content_fingerprint(_family({"file": "a.py", "start": 1, "end": 3}), tmp_path)
    assert before != after


def test_read_failure_degrades_to_none(tmp_path: Path) -> None:
    assert fp.member_fingerprint(tmp_path, "missing.py", 1, 3) is None
    _write(tmp_path, "a.py", SPAN)
    assert fp.member_fingerprint(tmp_path, "a.py", 1, 99) is None  # out-of-range span
    assert fp.member_fingerprint(tmp_path, "a.py", 0, 3) is None  # bad start
    # Malformed location fields degrade to None (never a partial/garbage hash).
    assert fp.member_fingerprint(tmp_path, None, 1, 3) is None  # non-str file
    assert fp.member_fingerprint(tmp_path, "", 1, 3) is None  # empty file
    assert fp.member_fingerprint(tmp_path, "a.py", True, 3) is None  # bool start (not a real int)
    assert fp.member_fingerprint(tmp_path, "a.py", 1, False) is None  # bool end
    assert fp.member_fingerprint(tmp_path, "a.py", "1", 3) is None  # non-int start
    # A family with any unreadable member -> whole family None (whole-gate degrade signal).
    fam = _family({"file": "a.py", "start": 1, "end": 3}, {"file": "missing.py", "start": 1, "end": 3})
    assert fp.family_content_fingerprint(fam, tmp_path) is None
    assert fp.family_content_fingerprint({"locations": [{"file": "a.py", "start": 1, "end": 3}, "not-a-dict"]}, tmp_path) is None
    assert fp.family_content_fingerprint({"locations": []}, tmp_path) is None
    assert fp.family_content_fingerprint({}, tmp_path) is None

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
import io
import textwrap
import tokenize
from pathlib import Path

import pytest

from .support import ROOT
from .seeding_support import load_module

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    return load_module(f"{name}_inproc", SCRIPTS / f"{name}.py")


fp = _load("nose_fingerprint_lib")


def _family(*locations: dict) -> dict:
    return {"locations": list(locations)}


def _write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


SPAN = "def f(x):\n    y = x + 1\n    return y\n"


def test_golden_value_pins_the_v1_algorithm(tmp_path: Path) -> None:
    # A hand-computed known-good v1 (rstrip-only) fingerprint for a fixed (file,
    # start, end); algo="1" is requested explicitly since v2 is now the default for
    # a .py member. SC1/SC2 relations are invariant under an offset-consistent
    # off-by-one read; only a golden value catches that misread.
    _write(tmp_path, "a.py", "import os\n\n" + SPAN)  # SPAN body is lines 3..5
    member = hashlib.sha256("def f(x):\n    y = x + 1\n    return y".encode()).hexdigest()[:16]
    family_golden = hashlib.sha256(member.encode()).hexdigest()[:16]
    assert fp.member_fingerprint(tmp_path, "a.py", 3, 5, algo="1") == member
    assert (
        fp.family_content_fingerprint(_family({"file": "a.py", "start": 3, "end": 5}), tmp_path, algo="1")
        == family_golden
    )


def _v2_reference_normalize(text: str) -> str:
    """Independent re-implementation of v2 token-aware normalization (dedent + drop
    comment/whitespace-structure tokens + join with a single space), written
    directly against stdlib ``tokenize`` rather than calling into ``fp`` — so this
    guards against a silent drift in the module's own normalization, not merely a
    second call to the same code."""
    dedented = textwrap.dedent(text)
    tokens = tokenize.generate_tokens(io.StringIO(dedented).readline)
    drop = {
        tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
        tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER,
    }
    return " ".join(tok.string for tok in tokens if tok.type not in drop)


def test_golden_value_pins_the_v2_algorithm(tmp_path: Path) -> None:
    # Same fixed span as the v1 golden test, but for the default (v2) algorithm: a
    # hand-computed known-good hash guards silent normalization drift (e.g. a
    # changed join separator or a token type accidentally kept/dropped).
    _write(tmp_path, "a.py", "import os\n\n" + SPAN)  # SPAN body is lines 3..5
    normalized = _v2_reference_normalize("def f(x):\n    y = x + 1\n    return y\n")
    member = hashlib.sha256(normalized.encode()).hexdigest()[:16]
    family_golden = hashlib.sha256(member.encode()).hexdigest()[:16]
    assert fp.FINGERPRINT_ALGO_VERSION == "2"
    assert fp.member_fingerprint(tmp_path, "a.py", 3, 5) == member  # default algo
    assert fp.family_content_fingerprint(_family({"file": "a.py", "start": 3, "end": 5}), tmp_path) == family_golden


# --------------------------------------------------------------------------- #
# Algo v2: token/comment-aware normalization (S4-Defer-1 resolution)
# --------------------------------------------------------------------------- #
def test_v2_in_place_comment_edit_is_stable(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", SPAN)
    before = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    _write(tmp_path, "a.py", "def f(x):\n    y = x + 1  # add one\n    return y\n")
    after = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    assert before == after


def test_v2_internal_whitespace_edit_is_stable(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", SPAN)
    before = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    _write(tmp_path, "a.py", "def f(x):\n    y   =   x + 1\n    return y\n")
    after = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    assert before == after


def test_v2_real_code_edit_rotates(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", SPAN)
    before = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    _write(tmp_path, "a.py", SPAN.replace("x + 1", "x + 2"))  # a genuine identifier/literal change
    after = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    assert before != after


def test_v2_falls_back_to_v1_for_non_python_member(tmp_path: Path) -> None:
    # A .mjs member always uses v1 rstrip-only normalization regardless of the
    # requested algo (accepted, documented v2 gap — see the module docstring).
    text = "function f(x) {\n  const y = x + 1;  // comment\n  return y;\n}\n"
    _write(tmp_path, "a.mjs", text)
    lines = text.splitlines()
    v1_expected = hashlib.sha256(fp.normalize_span(lines[0:4]).encode()).hexdigest()[:16]
    assert fp.member_fingerprint(tmp_path, "a.mjs", 1, 4) == v1_expected  # default algo, still v1 for .mjs


def test_v2_falls_back_to_v1_when_span_does_not_tokenize(tmp_path: Path) -> None:
    # An unbalanced-bracket fragment is not standalone-parseable Python; tokenize
    # legitimately raises (TokenError), and the member falls back to v1 rstrip-only
    # rather than crashing or degrading the whole family.
    fragment_lines = ["def f(x):", "    y = (x + 1", "    return y"]
    _write(tmp_path, "a.py", "\n".join(fragment_lines) + "\n")
    v1_expected = hashlib.sha256(fp.normalize_span(fragment_lines).encode()).hexdigest()[:16]
    assert fp.member_fingerprint(tmp_path, "a.py", 1, 3) == v1_expected


@pytest.mark.parametrize("algo", ["1", "2"], ids=["v1", "v2"])
def test_multiplicity_sensitivity_no_set_collapse(tmp_path: Path, algo: str) -> None:
    # {A, A, B} must NOT collapse to {A, B} under either fingerprint algorithm.
    _write(tmp_path, "a.py", SPAN)
    _write(tmp_path, "a2.py", SPAN)  # byte-identical copy of A
    _write(tmp_path, "b.py", "def g():\n    return 0\n")
    fam_aab = _family(
        {"file": "a.py", "start": 1, "end": 3},
        {"file": "a2.py", "start": 1, "end": 3},
        {"file": "b.py", "start": 1, "end": 2},
    )
    fam_ab = _family({"file": "a.py", "start": 1, "end": 3}, {"file": "b.py", "start": 1, "end": 2})
    assert fp.family_content_fingerprint(fam_aab, tmp_path, algo=algo) != fp.family_content_fingerprint(
        fam_ab, tmp_path, algo=algo
    )


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


# --------------------------------------------------------------------------- #
# family_member_hashes + fingerprint_from_member_hashes (schema v3: the gate
# baseline stores per-family member hashes, not just the family fingerprint).
# --------------------------------------------------------------------------- #
def test_family_member_hashes_sorted_duplicate_preserving_and_matches_fingerprint(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", SPAN)
    _write(tmp_path, "a2.py", SPAN)
    _write(tmp_path, "b.py", "def g():\n    return 0\n")
    fam = _family(
        {"file": "b.py", "start": 1, "end": 2},
        {"file": "a.py", "start": 1, "end": 3},
        {"file": "a2.py", "start": 1, "end": 3},
    )
    member_hashes = fp.family_member_hashes(fam, tmp_path)
    assert member_hashes == sorted(member_hashes)  # sorted
    a_hash = fp.member_fingerprint(tmp_path, "a.py", 1, 3)
    assert member_hashes.count(a_hash) == 2  # duplicate-preserving (a.py and a2.py are identical)
    assert fp.fingerprint_from_member_hashes(member_hashes) == fp.family_content_fingerprint(fam, tmp_path)


def test_family_member_hashes_none_on_unreadable_member(tmp_path: Path) -> None:
    fam = _family({"file": "a.py", "start": 1, "end": 3}, {"file": "missing.py", "start": 1, "end": 3})
    assert fp.family_member_hashes(fam, tmp_path) is None


def test_v2_block_nesting_variant_spans_collide_by_design(tmp_path: Path) -> None:
    # v2 drops INDENT/DEDENT (block-nesting structure, not whitespace noise -- see
    # the module docstring), so an identical body statement run hashes the SAME
    # whether it sits at top level or one level deeper inside an if/for/etc. This is
    # deliberate: nose's own family grouping already clusters such block-nesting
    # variants into one family (block-insensitive near-duplicate matching), so the
    # fingerprint only needs to be a stable identity for members nose already
    # decided belong together -- it is never asked to distinguish members nose
    # itself treats as interchangeable. The migration tool's collision assertion
    # (distinct v2 fingerprints == distinct nose family ids) is the backstop that
    # fails closed if this v2/nose alignment ever breaks.
    _write(tmp_path, "top_level.py", "x = 1\ny = 2\n")
    _write(tmp_path, "nested.py", "if cond:\n    x = 1\n    y = 2\n")
    top_level = fp.member_fingerprint(tmp_path, "top_level.py", 1, 2)
    nested_body = fp.member_fingerprint(tmp_path, "nested.py", 2, 3)  # the body only, not the `if` line
    assert top_level == nested_body

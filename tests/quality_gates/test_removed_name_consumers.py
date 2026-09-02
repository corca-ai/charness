from __future__ import annotations

from pathlib import Path

import yaml

from runtime_bootstrap import import_repo_module

from .repo_shapes import install_committed_repo
from .support import ROOT, run_script

_removed = import_repo_module(ROOT / "scripts/gates_support/removed_name_consumers.py", "scripts.gates_support.removed_name_consumers")

# The real incident, transcribed. `LINK_RE` moved out of `check_doc_links.py` into
# a shared module — a correct refactor — while `check_doc_authoring_preflight.py`
# still read it as `_doc_links.LINK_RE`. That consumption is a dynamic attribute
# access on a module object returned by `import_repo_module`, so ruff and the
# import graph both see nothing, and the commit-boundary gates do not run the
# broad suite. The slice shipped a red suite.
MODULE_BEFORE = 'import re\nLINK_RE = re.compile(r"x")\n\n\ndef other():\n    return 1\n'
MODULE_AFTER = "import re\n\n\ndef other():\n    return 1\n"
CONSUMER = (
    "from runtime_bootstrap import import_repo_module\n"
    '_doc_links = import_repo_module(__file__, "scripts.gates.check_doc_links")\n\n\n'
    "def collect(text):\n    return _doc_links.LINK_RE.findall(text)\n"
)


def seeded_repo(path: Path, files: dict[str, str]) -> Path:
    return install_committed_repo(path, files)


def test_removed_name_consumers_on_one_tree(tmp_path: Path) -> None:
    repo = seeded_repo(
        tmp_path / "repo",
        {
            "scripts/gates/check_doc_links.py": MODULE_BEFORE,
            "scripts/gates/check_doc_authoring_preflight.py": CONSUMER,
            "scripts/lonely.py": "VALUE = 1\n",
            "scripts/owner_token.py": "TOKEN = 1\n",
            "scripts/unrelated.py": "class X:\n    TOKEN = 2\n\n\ndef f(x):\n    return x.TOKEN\n",
            "scripts/state.py": "def _helper(x):\n    return x\n",
            "scripts/user.py": "import state\n\n\ndef go(v):\n    return state._helper(v)\n",
            "scripts/self_ref.py": "TOKEN = 1\n\n\ndef f(o):\n    return o.TOKEN\n",
            "scripts/owner_shared.py": "SHARED = 1\n",
            "scripts/reader_shared.py": "import owner_shared\n\n\ndef f():\n    return owner_shared.SHARED\n",
            "scripts/portable.py": "def helper(x):\n    return x\n",
            "scripts/reader_try.py": "import portable\n\n\ndef f(v):\n    return portable.helper(v)\n",
            "scripts/m.py": "NON_CLAIMS = ()\n",
            "tests/test_uses.py": "from scripts.m import NON_CLAIMS\n\n\ndef test_x():\n    assert NON_CLAIMS == ()\n",
            "scripts/notes_src.py": "TOKEN = 1\n",
            "scripts/notes.py": '"""Moved out of notes_src.py.\nTOKEN now lives elsewhere."""\n',
            "scripts/pair.py": "A, B = 1, 2\n",
            "scripts/reader_pair.py": "import pair\n\n\ndef f():\n    return pair.A\n",
            "scripts/typed.py": "COUNT: int = 1\n",
            "scripts/reader_typed.py": "import typed\n\n\ndef f():\n    return typed.COUNT\n",
        },
    )
    (repo / "scripts" / "gates" / "check_doc_links.py").write_text(MODULE_AFTER, encoding="utf-8")
    (repo / "scripts" / "lonely.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "owner_token.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "state.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "self_ref.py").write_text(
        '"""Notes for self_ref.py."""\n\n\ndef f(o):\n    return o.TOKEN\n', encoding="utf-8"
    )
    (repo / "scripts" / "owner_shared.py").write_text(
        "from shared import SHARED as _moved\n\n\ndef get():\n    return _moved\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "portable.py").write_text(
        "try:\n    from fast import helper\nexcept ImportError:\n    def helper(x):\n        return x\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "m.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "notes_src.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "pair.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "typed.py").write_text("", encoding="utf-8")

    paths = [
        "scripts/gates/check_doc_links.py",
        "scripts/lonely.py",
        "scripts/owner_token.py",
        "scripts/state.py",
        "scripts/self_ref.py",
        "scripts/owner_shared.py",
        "scripts/portable.py",
        "scripts/m.py",
        "scripts/notes_src.py",
        "scripts/pair.py",
        "scripts/typed.py",
    ]
    report = _removed.build_report(repo, paths, "HEAD")

    assert report["removed"]["scripts/gates/check_doc_links.py"] == ["LINK_RE"]
    assert report["consumers"]["scripts/gates/check_doc_links.py"] == {
        "scripts/gates/check_doc_authoring_preflight.py": ["LINK_RE"]
    }
    assert report["removed"]["scripts/lonely.py"] == ["VALUE"]
    assert "scripts/lonely.py" not in report["consumers"]
    assert "scripts/owner_token.py" not in report["consumers"]
    assert report["consumers"]["scripts/state.py"] == {"scripts/user.py": ["_helper"]}
    assert report["removed"]["scripts/self_ref.py"] == ["TOKEN"]
    assert "scripts/self_ref.py" not in report["consumers"]
    assert "SHARED" in report["removed"]["scripts/owner_shared.py"]
    assert report["consumers"]["scripts/owner_shared.py"] == {
        "scripts/reader_shared.py": ["SHARED"]
    }
    assert not report["removed"].get("scripts/portable.py")
    assert report["consumers"]["scripts/m.py"] == {"tests/test_uses.py": ["NON_CLAIMS"]}
    assert "scripts/notes_src.py" not in report["consumers"]
    assert report["removed"]["scripts/pair.py"] == ["A", "B"]
    assert report["consumers"]["scripts/pair.py"] == {"scripts/reader_pair.py": ["A"]}
    assert report["removed"]["scripts/typed.py"] == ["COUNT"]


def test_import_alias_is_retained_as_a_module_level_binding() -> None:
    baseline = "VALUE = 1\n"
    current = (
        "from scripts.old_module import added_diff_lines as _added_diff_lines\n"
        "\n"
        "def report():\n"
        "    return _added_diff_lines\n"
    )

    assert _removed.removed_names(baseline, current) == ["VALUE"]





def test_the_advisory_writes_to_stderr_and_names_the_readers(tmp_path: Path, capsys) -> None:
    """stdout carries the closeout's one YAML document; an advisory there breaks it."""
    repo = seeded_repo(
        tmp_path / "repo",
        {
            "scripts/gates/check_doc_links.py": MODULE_BEFORE,
            "scripts/gates/check_doc_authoring_preflight.py": CONSUMER,
        },
    )
    (repo / "scripts" / "gates" / "check_doc_links.py").write_text(MODULE_AFTER, encoding="utf-8")

    _removed.advise_removed_name_consumers(repo, ["scripts/gates/check_doc_links.py"], against="HEAD")

    captured = capsys.readouterr()
    assert "check_doc_authoring_preflight.py" in captured.err
    assert "LINK_RE" in captured.err
    assert "Deleting the name is fine" in captured.err
    assert captured.out == ""


def test_the_advisory_is_silent_with_no_readers(tmp_path: Path, capsys) -> None:
    repo = seeded_repo(tmp_path / "repo", {"scripts/lonely.py": "VALUE = 1\n"})
    (repo / "scripts" / "lonely.py").write_text("", encoding="utf-8")

    _removed.advise_removed_name_consumers(repo, ["scripts/lonely.py"], against="HEAD")

    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == ""


def test_the_mirror_is_not_reported_when_the_source_is(tmp_path: Path, capsys) -> None:
    """A `plugins/` copy is generated; reporting it doubles every finding.

    The mirror must genuinely BE a removal with a reader, otherwise the filter is
    never exercised — the first version of this test seeded no mirror at all and
    survived deleting the filter.
    """
    module = "V = 1\n"
    reader = 'import x\n\n\ndef f():\n    return x.V\n'
    repo = seeded_repo(
        tmp_path / "repo",
        {
            "scripts/x.py": module,
            "scripts/reader.py": reader,
            "plugins/charness/scripts/x.py": module,
        },
    )
    (repo / "scripts" / "x.py").write_text("", encoding="utf-8")
    (repo / "plugins" / "charness" / "scripts" / "x.py").write_text("", encoding="utf-8")

    _removed.advise_removed_name_consumers(
        repo, ["scripts/x.py", "plugins/charness/scripts/x.py"], against="HEAD"
    )

    err = capsys.readouterr().err
    assert "scripts/x.py lost V" in err
    assert "plugins/" not in err


def test_the_cli_separates_a_clean_tree_from_an_unexamined_one(tmp_path: Path) -> None:
    """A clean zero and "could not compare" must not print the same thing.

    Asserting `consumer_count == 0` against the real repo is satisfied by a
    `build_report` that returns nothing at all, so the discriminating assertion is
    the uncomparable count against a base that does not resolve.
    """
    repo = seeded_repo(tmp_path / "repo", {"scripts/x.py": "V = 1\n"})

    result = run_script(
        "scripts/gates_support/removed_name_consumers.py",
        "--repo-root", str(repo),
        "--against", "no-such-ref",
        "--paths", "scripts/x.py",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["removed"] == {}
    assert payload["uncomparable_count"] == 1
    assert "scripts/x.py" in payload["uncomparable"]


# --- Branch coverage the changed-line mutation lane named -----------------------


def test_unparsable_source_yields_no_names_rather_than_crashing() -> None:
    """A half-written file mid-slice must not take the closeout down."""
    assert _removed.module_level_names("def broken(:\n") == set()


def test_a_deleted_file_reports_every_name_it_defined(tmp_path: Path) -> None:
    """Deleting the file removes every name, which is the useful answer, not an error."""
    repo = seeded_repo(
        tmp_path / "repo",
        {
            "scripts/gone.py": "A = 1\nB = 2\n",
            "scripts/reader.py": "import gone\n\n\ndef f():\n    return gone.A\n",
        },
    )
    (repo / "scripts" / "gone.py").unlink()

    report = _removed.build_report(repo, ["scripts/gone.py"], "HEAD")

    assert report["removed"] == {"scripts/gone.py": ["A", "B"]}
    assert report["consumers"]["scripts/gone.py"] == {"scripts/reader.py": ["A"]}


def test_an_unreadable_scan_candidate_is_skipped_not_fatal(tmp_path: Path) -> None:
    """A binary or permission-denied file in the scan set must not stop the sweep."""
    repo = seeded_repo(tmp_path / "repo", {"scripts/owner.py": "TOKEN = 1\n"})
    broken = repo / "scripts" / "broken.py"
    broken.write_bytes(b"\xff\xfe\x00owner TOKEN")
    (repo / "scripts" / "owner.py").write_text("", encoding="utf-8")

    report = _removed.build_report(repo, ["scripts/owner.py"], "HEAD")

    assert report["removed"] == {"scripts/owner.py": ["TOKEN"]}


def test_the_cli_prints_both_branches(tmp_path: Path, capsys, monkeypatch) -> None:
    """Clean and found both carry the skipped state; a silent success reads as unrun.

    The retired prose branches said "No module-level names removed" or named the
    module and its readers. Both are payload keys now — an empty versus a populated
    `removed`/`consumers` — and `skipped` rides in both so an empty result never
    reads as a check that did not run.
    """
    import sys as _sys

    repo = seeded_repo(
        tmp_path / "repo",
        {
            "scripts/owner.py": "TOKEN = 1\n",
            "scripts/reader.py": "import owner\n\n\ndef f():\n    return owner.TOKEN\n",
        },
    )

    monkeypatch.setattr(
        _sys, "argv", ["removed_name_consumers.py", "--repo-root", str(repo), "--paths", "scripts/owner.py"]
    )
    assert _removed.main() == 0
    clean = yaml.safe_load(capsys.readouterr().out)
    assert clean["removed"] == {}
    assert clean["consumers"] == {}
    assert clean["skipped"] == {"reason": "uncomparable", "path_count": 0}

    (repo / "scripts" / "owner.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        _sys, "argv", ["removed_name_consumers.py", "--repo-root", str(repo), "--paths", "scripts/owner.py"]
    )
    assert _removed.main() == 0
    found = yaml.safe_load(capsys.readouterr().out)
    assert found["removed"] == {"scripts/owner.py": ["TOKEN"]}
    assert found["consumers"]["scripts/owner.py"] == {"scripts/reader.py": ["TOKEN"]}
    assert found["consumer_count"] == 1
    assert found["skipped"] == {"reason": "uncomparable", "path_count": 0}


def test_the_cli_says_so_when_a_removal_has_no_reader(tmp_path: Path, capsys, monkeypatch) -> None:
    """A removal nobody reads is distinguishable from nothing having been removed.

    The retired prose said "no candidate reader found". The payload states the same
    fact as a PAIR: a populated `removed` beside a `consumers` map with no entry for
    that module, and `consumer_count == 0`. Asserting the absence alone would also
    hold for a run that removed nothing, so the removal is asserted with it.
    """
    import sys as _sys

    repo = seeded_repo(tmp_path / "repo", {"scripts/lonely.py": "VALUE = 1\n"})
    (repo / "scripts" / "lonely.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        _sys, "argv", ["removed_name_consumers.py", "--repo-root", str(repo), "--paths", "scripts/lonely.py"]
    )

    assert _removed.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["removed"] == {"scripts/lonely.py": ["VALUE"]}
    assert "scripts/lonely.py" not in payload["consumers"]
    assert payload["consumer_count"] == 0


def test_a_permission_denied_scan_candidate_is_skipped(tmp_path: Path) -> None:
    """An unreadable file in the scan set must not stop the sweep."""
    repo = seeded_repo(
        tmp_path / "repo",
        {
            "scripts/owner.py": "TOKEN = 1\n",
            "scripts/locked.py": "import owner\n\n\ndef f():\n    return owner.TOKEN\n",
        },
    )
    (repo / "scripts" / "owner.py").write_text("", encoding="utf-8")
    locked = repo / "scripts" / "locked.py"
    locked.chmod(0o000)
    try:
        report = _removed.build_report(repo, ["scripts/owner.py"], "HEAD")
    finally:
        locked.chmod(0o644)

    assert report["removed"] == {"scripts/owner.py": ["TOKEN"]}
    assert report["consumers"] == {}


def test_an_unreadable_module_is_uncomparable_not_a_removal(tmp_path: Path) -> None:
    """A file that exists but cannot be read is UNEXAMINED — reporting every name
    as removed would be a fabricated finding."""
    repo = seeded_repo(tmp_path / "repo", {"scripts/owner.py": "TOKEN = 1\n"})
    owner = repo / "scripts" / "owner.py"
    owner.chmod(0o000)
    try:
        report = _removed.build_report(repo, ["scripts/owner.py"], "HEAD")
    finally:
        owner.chmod(0o644)

    assert report["removed"] == {}
    assert report["uncomparable"]["scripts/owner.py"] == "unreadable in the worktree"

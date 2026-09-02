from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]
CHECKER = load_script_module(
    "check_staged_test_boundaries_for_test",
    ROOT / "scripts" / "hooks" / "check_staged_test_boundaries.py",
)


def analyze(source: str, *ranges: tuple[int, int]) -> dict[str, object]:
    return CHECKER._analyze_source("tests/test_demo.py", source.encode(), list(ranges))


def test_direct_process_spawn_on_changed_line_needs_a_reason() -> None:
    report = analyze(
        "import subprocess\n\ndef test_it():\n    subprocess.run(['python3', 'tool.py'])\n",
        (4, 4),
    )

    assert report["findings"] == [
        {
            "line": 4,
            "callee": "subprocess.run",
            "kinds": ["direct-process-spawn"],
            "git_operations": [],
            "declared": False,
            "marker_seen": False,
            "reasons": [],
        }
    ]


def test_boundary_marker_requires_a_nonempty_reason() -> None:
    declared = analyze(
        "import pytest, subprocess\n\n@pytest.mark.boundary_contract(reason='argv delivery')\n"
        "def test_it():\n    subprocess.run(['python3'])\n",
        (5, 5),
    )
    empty = analyze(
        "import pytest, subprocess\n\n@pytest.mark.boundary_contract(reason='')\n"
        "def test_it():\n    subprocess.run(['python3'])\n",
        (5, 5),
    )

    assert declared["findings"][0]["declared"] is True
    assert declared["findings"][0]["reasons"] == ["argv delivery"]
    assert empty["findings"][0]["declared"] is False
    assert empty["findings"][0]["marker_seen"] is True


def test_git_repository_construction_is_classified_through_helpers_and_processes() -> None:
    helper = analyze(
        "def test_it(repo):\n    _git(repo, 'init', '-q')\n",
        (2, 2),
    )["findings"][0]
    process = analyze(
        "import subprocess\n\ndef test_it():\n    subprocess.run(['git', 'clone', 'a', 'b'])\n",
        (4, 4),
    )["findings"][0]

    assert helper["kinds"] == ["git-repository-construction"]
    assert helper["git_operations"] == ["init"]
    assert process["kinds"] == ["direct-process-spawn", "git-repository-construction"]
    assert process["git_operations"] == ["clone"]


def test_unchanged_process_call_is_outside_the_advisory_scope() -> None:
    report = analyze(
        "import subprocess\n\ndef test_it():\n    subprocess.run(['python3'])\n    value = 1\n",
        (5, 5),
    )

    assert report["findings"] == []


def test_known_process_helper_is_visible_without_following_indirection() -> None:
    report = analyze(
        "def test_it():\n    run_script('scripts/tool.py')\n",
        (2, 2),
    )

    assert report["findings"][0]["kinds"] == ["process-helper-boundary"]


def test_changed_ranges_keep_only_python_test_files() -> None:
    diff = b"""diff --git a/tests/test_a.py b/tests/test_a.py
--- a/tests/test_a.py
+++ b/tests/test_a.py
@@ -1 +1,2 @@
diff --git a/scripts/tool.py b/scripts/tool.py
--- a/scripts/tool.py
+++ b/scripts/tool.py
@@ -3 +3 @@
"""

    assert CHECKER._changed_ranges(diff) == {"tests/test_a.py": [(1, 2)]}


def test_scan_uses_the_staged_scope_and_reports_tradeoffs(monkeypatch) -> None:
    monkeypatch.setattr(
        CHECKER,
        "_staged_diff",
        lambda _root: b"+++ b/tests/test_a.py\n@@ -0,0 +1,2 @@\n",
    )
    monkeypatch.setattr(
        CHECKER,
        "_staged_blobs",
        lambda _root, paths: {
            path: b"import subprocess\nsubprocess.run(['python3'])\n" for path in paths
        },
    )

    report = CHECKER.scan_staged_tests(ROOT)

    assert report["staged_test_files"] == 1
    assert report["undeclared_call_count"] == 1
    assert any("False positives" in note for note in report["notes"])
    assert any("one git cat-file --batch" in note for note in report["notes"])


def test_batch_blob_reader_uses_one_git_process_for_all_paths(monkeypatch, tmp_path) -> None:
    calls: list[str] = []
    payload = b"abc\ndefg"
    output = b"one blob 3\nabc\ntwo blob 4\ndefg\n"

    def fake_run(command, **kwargs):
        calls.append(command)
        assert kwargs["shell"] is True
        input_path = Path(shlex.split(command)[-1])
        assert input_path.read_bytes() == b":tests/test_a.py\n:tests/test_b.py\n"
        return subprocess.CompletedProcess(command, 0, output.decode(), "")

    monkeypatch.setattr(CHECKER, "run_process", fake_run)

    blobs = CHECKER._staged_blobs(tmp_path, ["tests/test_a.py", "tests/test_b.py"])

    assert blobs == {"tests/test_a.py": payload[:3], "tests/test_b.py": payload[4:]}
    assert len(calls) == 1
    assert shlex.split(calls[0])[:3] == ["git", "cat-file", "--batch"]

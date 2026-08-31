from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from runtime_bootstrap import import_repo_module

from .support import ROOT, _load_script_module, run_script

_BOUNDARY = _load_script_module(
    "tests.quality_gates.reviewer_boundary_fingerprint_for_parity",
    ROOT / "skills/shared/scripts/reviewer_boundary_fingerprint.py",
)


def seeded_repo(path: Path) -> Path:
    """Copy an immutable HEAD-bearing seed instead of rebuilding Git per test."""
    from .repo_shapes import install_committed_repo

    return install_committed_repo(path, {"seed.txt": "seed\n"})


def write_review_snapshot(repo: Path, *, captured: dict[str, str] | None = None) -> Path:
    """Write the parity input contract without rebuilding a Git state.

    Snapshot capture has one real boundary E2E below. The parity matrix only
    tests how an already-captured immutable seed is consumed, so rebuilding a
    repository and invoking the capture CLI for every case adds no signal.
    """
    snapshot_dir = repo / ".charness" / "reviewer-boundary"
    blob_dir = snapshot_dir / "blobs"
    blob_dir.mkdir(parents=True, exist_ok=True)
    source_blobs: dict[str, str] = {}
    for path, source in (captured or {}).items():
        key = hashlib.sha256(source.encode()).hexdigest()
        (blob_dir / key).write_text(source, encoding="utf-8")
        source_blobs[path] = key
    snapshot = {"head": _parity._current_head(repo), "source_blobs": source_blobs}
    snapshot_path = snapshot_dir / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
    return snapshot_path

_parity = import_repo_module(ROOT / "scripts/parity_harness.py", "scripts.parity_harness")

# The real narrowing this harness exists for, reduced to its two versions.
# `LINK_RE`'s character classes match newlines, so scanning the joined text finds
# a prose-wrapped link and scanning line-by-line does not. That one-line change
# was the round-1 repair for a false positive, and it opened a false negative that
# no existing test covered -- because nothing had ever named "wrapped links" as a
# property. Built from the shipped defect, not from an invented one.
BASELINE_SCAN = '''
import re
LINK_RE = re.compile(r"\\[[^\\]]+\\]\\(([^)]+)\\)")

def scan(lines):
    text = "\\n".join(lines)
    return LINK_RE.findall(text)
'''

REPAIRED_SCAN = '''
import re
LINK_RE = re.compile(r"\\[[^\\]]+\\]\\(([^)]+)\\)")

def scan(lines):
    return [target for line in lines for target in LINK_RE.findall(line)]
'''

WRAPPED_LINK = ["See the [agent assessment", "invariant](../../../scripts/runtime_bootstrap.py) for the rule."]


def test_the_real_narrowing_is_reported_as_repair_shaped() -> None:
    """`scan`'s signature is identical; only its body changed. That pair is the whole signal."""
    assert _parity.repair_shaped_functions(BASELINE_SCAN, REPAIRED_SCAN) == ["scan"]


def test_the_real_narrowing_diverges_on_a_wrapped_link() -> None:
    """Naming the function is not enough — the harness must show the behaviour that moved."""
    baseline = _parity.load_module_from_source(BASELINE_SCAN, "parity_baseline_scan")
    current = _parity.load_module_from_source(REPAIRED_SCAN, "parity_current_scan")

    divergences = _parity.compare_callables(baseline.scan, current.scan, [(WRAPPED_LINK,)])

    assert len(divergences) == 1
    assert "runtime_bootstrap.py" in divergences[0]["baseline"][1]
    assert divergences[0]["current"][1] == repr([])


def test_an_unwrapped_link_does_not_diverge() -> None:
    """Proves the harness reports a DIFFERENCE, not merely that two modules were loaded."""
    baseline = _parity.load_module_from_source(BASELINE_SCAN, "parity_baseline_same")
    current = _parity.load_module_from_source(REPAIRED_SCAN, "parity_current_same")

    divergences = _parity.compare_callables(
        baseline.scan, current.scan, [(["See [x](./a.md) here."],)]
    )

    assert divergences == []


def test_a_new_function_is_not_repair_shaped() -> None:
    """A function with no prior behaviour has no complement to preserve."""
    assert _parity.repair_shaped_functions("def a():\n    return 1\n", "def a():\n    return 1\n\ndef b():\n    return 2\n") == []


def test_a_changed_signature_is_not_repair_shaped() -> None:
    """A changed signature is LOUD — every caller is forced to update, so the radius gets walked."""
    assert _parity.repair_shaped_functions("def a(x):\n    return x\n", "def a(x, y):\n    return x\n") == []


def test_an_unchanged_function_is_not_repair_shaped() -> None:
    assert _parity.repair_shaped_functions("def a(x):\n    return x\n", "def a(x):\n    return x\n") == []


def test_a_nested_helper_is_reported_together_with_its_enclosing_function() -> None:
    """A closure a repaired function delegates to is exactly where a narrowing hides.

    Both names are reported, and that is correct rather than noisy: editing the
    closure necessarily changes the enclosing function's body too, and the reader
    needs the outer name to know which public surface moved.
    """
    before = "def outer(x):\n    def inner(y):\n        return y\n    return inner(x)\n"
    after = "def outer(x):\n    def inner(y):\n        return y or 0\n    return inner(x)\n"

    assert _parity.repair_shaped_functions(before, after) == ["outer", "outer.inner"]


def test_a_raise_becoming_a_return_is_a_divergence_not_a_crash() -> None:
    """An exception is an OUTCOME. A gate that stopped refusing is the narrowing that matters most."""
    baseline = _parity.load_module_from_source(
        "def check(v):\n    raise ValueError('refused')\n", "parity_baseline_raise"
    )
    current = _parity.load_module_from_source("def check(v):\n    return None\n", "parity_current_raise")

    divergences = _parity.compare_callables(baseline.check, current.check, [(1,)])

    assert len(divergences) == 1
    assert divergences[0]["baseline"][0] == "raise"
    assert divergences[0]["current"][0] == "return"


def test_loading_a_baseline_does_not_leak_into_sys_modules() -> None:
    """Both versions define the same names; a leak would let one silently shadow the other."""
    name = "parity_leak_probe"
    _parity.load_module_from_source("VALUE = 1\n", name)

    assert name not in sys.modules


def test_a_baseline_that_cannot_load_is_a_usage_error_not_a_silent_pass() -> None:
    try:
        _parity.load_module_from_source("def broken(:\n", "parity_broken")
    except _parity.ParityError:
        return
    raise AssertionError("a syntactically broken baseline must refuse, not load empty")


def test_uncomparable_paths_are_reported_rather_than_dropped(tmp_path: Path) -> None:
    """A path with no baseline is not "no repairs" — conflating them is the silent-zero shape."""
    repo = seeded_repo(tmp_path / "repo")
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "fresh.py").write_text("def a():\n    return 1\n", encoding="utf-8")

    result = run_script(
        "scripts/parity_harness.py",
        "--repo-root",
        str(repo),
        "--against",
        "review-snapshot",
        "--paths",
        "scripts/fresh.py",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["files"] == {}
    assert "scripts/fresh.py" in payload["uncomparable"]


def test_the_snapshot_captures_python_source_so_a_repair_has_a_baseline(tmp_path: Path) -> None:
    """End-to-end: the reviewer-boundary snapshot is what makes an in-slice baseline exist at all.

    Commit-ranged tooling cannot supply this. A function created earlier in the
    same slice is simply NEW at commit granularity, so the version the reviewer
    read is the only honest baseline for its repair — and until this capture,
    nothing in the repo recorded it.
    """
    repo = seeded_repo(tmp_path / "repo")
    target = repo / "scripts" / "gate.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def verdict(x):\n    return bool(x)\n", encoding="utf-8")

    snapshot = run_script(
        "skills/shared/scripts/reviewer_boundary_fingerprint.py", "snapshot", "--repo-root", str(repo)
    )
    assert snapshot.returncode == 0, snapshot.stderr

    # The repair: same signature, narrowed body.
    target.write_text("def verdict(x):\n    return False\n", encoding="utf-8")

    result = run_script(
        "scripts/parity_harness.py",
        "--repo-root",
        str(repo),
        "--against",
        "review-snapshot",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["files"] == {"scripts/gate.py": ["verdict"]}


def test_verify_does_not_overwrite_the_captured_baseline(tmp_path: Path) -> None:
    """Capturing at verify time would record the REPAIRED source and destroy the baseline."""
    repo = seeded_repo(tmp_path / "repo")
    target = repo / "scripts" / "gate.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def verdict(x):\n    return bool(x)\n", encoding="utf-8")
    run_script("skills/shared/scripts/reviewer_boundary_fingerprint.py", "snapshot", "--repo-root", str(repo))

    target.write_text("def verdict(x):\n    return False\n", encoding="utf-8")
    run_script(
        "skills/shared/scripts/reviewer_boundary_fingerprint.py",
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        str(repo / ".charness" / "reviewer-boundary" / "snapshot.json"),
    )

    baseline = _parity.source_at_review_snapshot(repo, "scripts/gate.py")
    assert baseline is not None
    assert "return bool(x)" in baseline


# --- Round-1 findings, each pinned by the case that produced it -------------------


def test_same_named_methods_in_two_classes_do_not_collide() -> None:
    """Flat `node.name` keys made repairing `A.run` INVISIBLE — `B.run` overwrote it."""
    before = "class A:\n    def run(self, x):\n        return 1\nclass B:\n    def run(self, x):\n        return 2\n"
    after = "class A:\n    def run(self, x):\n        return 99\nclass B:\n    def run(self, x):\n        return 2\n"

    assert _parity.repair_shaped_functions(before, after) == ["A.run"]


def test_adding_a_same_named_method_is_not_reported_as_a_repair() -> None:
    """The other half of the collision: ADDING `B.helper` read as repairing `A.helper`."""
    before = "class A:\n    def helper(self, x):\n        return 1\n"
    after = before + "class B:\n    def helper(self, x):\n        return 2\n"

    assert _parity.repair_shaped_functions(before, after) == []


def test_a_decorator_change_with_an_untouched_body_is_repair_shaped() -> None:
    """The quietest same-signature behaviour change there is, and it was invisible."""
    before = "def f(x):\n    return x\n"
    after = "import functools\n@functools.lru_cache\ndef f(x):\n    return x\n"

    assert _parity.repair_shaped_functions(before, after) == ["f"]


def test_two_different_generators_are_not_reported_as_identical() -> None:
    """The harness's own FALSE GREEN: calling a generator function runs no body.

    Both calls returned `<generator object ... at 0x...>`; CPython reused the
    freed address often enough that two completely different generators compared
    EQUAL and the harness reported "0 divergences" for a function it never ran —
    intermittently, which is worse than always. `iter_doc_lines`, cited in this
    module's own docstring as a verified surface, is a generator.
    """
    yields = _parity.load_module_from_source(
        "def gen(n):\n    for i in range(n):\n        yield i\n", "parity_gen_yields"
    )
    empty = _parity.load_module_from_source("def gen(n):\n    return\n    yield\n", "parity_gen_empty")

    assert len(_parity.compare_callables(yields.gen, empty.gen, [(3,)])) == 1
    same = _parity.load_module_from_source(
        "def gen(n):\n    for i in range(n):\n        yield i\n", "parity_gen_same"
    )
    assert _parity.compare_callables(yields.gen, same.gen, [(3,)]) == []


def test_a_stale_snapshot_from_another_commit_is_not_read(tmp_path: Path) -> None:
    """A durable snapshot kept answering for LATER slices, so the advisory could
    announce a bounded review that never happened. Binding to HEAD discards it."""
    repo = seeded_repo(tmp_path / "repo")
    target = repo / "scripts" / "gate.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def verdict(x):\n    return bool(x)\n", encoding="utf-8")
    write_review_snapshot(repo, captured={"scripts/gate.py": target.read_text(encoding="utf-8")})
    assert _parity.captured_paths(repo) == ["scripts/gate.py"]

    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-m", "land"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    assert _parity.captured_paths(repo) == []
    assert _parity.source_at_review_snapshot(repo, "scripts/gate.py") is None


def test_a_file_clean_at_snapshot_time_is_reported_uncomparable_not_clean(tmp_path: Path) -> None:
    """The common case: a reviewer reads COMMITTED code and the parent repairs it.

    Such a file is never captured, so a captured-only default printed a reassuring
    zero for exactly the repair class this tool exists to catch.
    """
    repo = seeded_repo(tmp_path / "repo")
    target = repo / "scripts" / "shipped.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def verdict(x):\n    return bool(x)\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-m", "ship"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    write_review_snapshot(repo)

    target.write_text("def verdict(x):\n    return False\n", encoding="utf-8")
    result = run_script("scripts/parity_harness.py", "--repo-root", str(repo))

    payload = yaml.safe_load(result.stdout)
    assert payload["files"] == {}
    assert "scripts/shipped.py" in payload["uncomparable"]


def test_the_snapshot_blobs_are_not_reported_as_reviewer_drift(tmp_path: Path) -> None:
    """The capture made the boundary tool report a violation it caused itself.

    In a repo without a `.gitignore` entry for `.charness/`, every written blob
    appeared as `untracked-added` on the next verify — an unattributable
    `ok: false`, which is how a parent learns to discount a real one.
    """
    repo = seeded_repo(tmp_path / "repo")
    assert not (repo / ".gitignore").exists()
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "dirty.py").write_text("x = 1\n", encoding="utf-8")

    run_script(
        "skills/shared/scripts/reviewer_boundary_fingerprint.py",
        "snapshot",
        "--repo-root",
        str(repo),
    )
    verify = run_script(
        "skills/shared/scripts/reviewer_boundary_fingerprint.py",
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        str(repo / ".charness" / "reviewer-boundary" / "snapshot.json"),
    )

    payload = yaml.safe_load(verify.stdout)
    assert payload["ok"] is True, payload["drift"]
    assert payload["drift"] == []
    assert verify.returncode == 0


def test_a_snapshot_written_at_the_repo_root_does_not_report_its_own_blobs(tmp_path: Path) -> None:
    """`--out <repo-root>/snapshot.json` puts blobs at `<repo>/blobs/` — the most
    visible place — and the round-1 repair's `directory == "."` guard skipped the
    drop exactly there, leaving the original blocker reachable through a flag."""
    repo = tmp_path / "repo"
    repo.mkdir()
    key = "a" * 64
    other = "b" * 64
    snapshot = {
        "untracked": {
            "snapshot.json": "self",
            f"blobs/{key}": "captured",
            f"blobs/{other}": "unrelated",
        },
        "source_blobs": {"scripts/dirty.py": key},
    }
    _BOUNDARY._drop_self(snapshot, str(repo), str(repo / "snapshot.json"))

    assert "snapshot.json" not in snapshot["untracked"]
    assert f"blobs/{key}" not in snapshot["untracked"]
    assert snapshot["untracked"] == {f"blobs/{other}": "unrelated"}


def test_a_destroyed_baseline_is_reported_as_lost_not_as_never_captured(tmp_path: Path) -> None:
    """Evidence destruction must not read as "this path was simply not captured"."""
    repo = seeded_repo(tmp_path / "repo")
    target = repo / "scripts" / "gate.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def verdict(x):\n    return bool(x)\n", encoding="utf-8")
    write_review_snapshot(repo, captured={"scripts/gate.py": target.read_text(encoding="utf-8")})
    for blob in (repo / ".charness" / "reviewer-boundary" / "blobs").glob("*"):
        blob.unlink()
    target.write_text("def verdict(x):\n    return False\n", encoding="utf-8")

    payload = yaml.safe_load(run_script("scripts/parity_harness.py", "--repo-root", str(repo)).stdout)

    assert "LOST baseline" in payload["uncomparable"]["scripts/gate.py"]


def test_a_returned_file_handle_is_not_consumed_or_collapsed() -> None:
    """`hasattr(__next__)` also matches file handles; iterating one consumed it AND
    erased the `name=` repr, so two DIFFERENT handles compared equal."""
    baseline = _parity.load_module_from_source(
        "def openit(p):\n    return open(p, 'w')\n", "parity_handle_a"
    )
    current = _parity.load_module_from_source(
        "def openit(p):\n    return open(p + '.other', 'w')\n", "parity_handle_b"
    )

    with tempfile.TemporaryDirectory() as tmp:
        divergences = _parity.compare_callables(baseline.openit, current.openit, [(f"{tmp}/x",)])

    assert len(divergences) == 1


def test_hex_returning_functions_are_still_compared() -> None:
    """Normalising every `0x…` token erased legitimate hex DATA, not just addresses."""
    baseline = _parity.load_module_from_source("def fmt(n):\n    return hex(n)\n", "parity_hex_a")
    current = _parity.load_module_from_source("def fmt(n):\n    return hex(n * 2)\n", "parity_hex_b")

    assert len(_parity.compare_callables(baseline.fmt, current.fmt, [(42,)])) == 1


def test_a_generator_that_raises_midway_keeps_its_prefix() -> None:
    """Discarding the yielded prefix made "yields then raises" and "raises at once" equal."""
    late = _parity.load_module_from_source(
        "def gen(n):\n    yield 1\n    yield 2\n    raise ValueError('x')\n", "parity_gen_late"
    )
    early = _parity.load_module_from_source(
        "def gen(n):\n    raise ValueError('x')\n    yield\n", "parity_gen_early"
    )

    assert len(_parity.compare_callables(late.gen, early.gen, [(1,)])) == 1


def test_a_name_defined_twice_in_one_scope_does_not_collapse() -> None:
    """Qualifying by scope was not enough: an import-fallback pair, `@property` +
    `@x.setter`, and `@overload` stubs all define one name twice, legitimately."""
    before = "try:\n    pass\nexcept ImportError:\n    def run(a):\n        return 1\ndef run(a):\n    return 2\n"
    after = "try:\n    pass\nexcept ImportError:\n    def run(a):\n        return 99\ndef run(a):\n    return 2\n"

    assert _parity.repair_shaped_functions(before, after) != []


def test_a_renamed_file_keeps_both_sides_so_its_baseline_is_findable(tmp_path: Path) -> None:
    """A rename-plus-repair reported two unexaminable paths and lost the baseline.

    Keeping BOTH sides of the rename is what lets the moved file still resolve
    against the blob the reviewer's snapshot captured under its old name.
    """
    repo = seeded_repo(tmp_path / "repo")
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "old.py").write_text("def verdict(x):\n    return bool(x)\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-m", "ship"],
        cwd=repo, check=True, capture_output=True,
    )
    subprocess.run(["git", "mv", "scripts/old.py", "scripts/new.py"], cwd=repo, check=True, capture_output=True)

    paths = _parity.changed_python_paths(repo)

    assert "scripts/new.py" in paths
    assert "scripts/old.py" in paths


def test_a_non_ascii_path_is_not_silently_dropped(tmp_path: Path) -> None:
    """Line-oriented porcelain C-quotes non-ASCII paths, so they stopped ending in `.py`."""
    repo = seeded_repo(tmp_path / "repo")
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "caf\u00e9.py").write_text("x = 1\n", encoding="utf-8")

    assert "scripts/caf\u00e9.py" in _parity.changed_python_paths(repo)


# --- Branch coverage the changed-line mutation lane named -----------------------


def _run_cli(monkeypatch, capsys, *args: str) -> tuple[int, str]:
    monkeypatch.setattr(sys, "argv", ["parity_harness.py", *args])
    code = _parity.main()
    return code, capsys.readouterr().out


def test_a_snapshot_recording_another_head_is_discarded(tmp_path: Path) -> None:
    from .repo_shapes import install_committed_repo

    install_committed_repo(
        tmp_path,
        {
            ".charness/reviewer-boundary/snapshot.json": json.dumps(
                {"head": "0" * 40, "source_blobs": {"scripts/x.py": "abc"}}
            ),
            "seed.txt": "s\n",
        },
        message="s",
    )

    assert _parity.snapshot_payload(tmp_path) == {}


def test_unparsable_source_refuses_rather_than_reporting_no_repairs() -> None:
    """A parse failure must not read as "nothing was repaired"."""
    try:
        _parity.repair_shaped_functions("def ok():\n    return 1\n", "def broken(:\n")
    except _parity.ParityError as exc:
        assert "cannot parse" in str(exc)
        return
    raise AssertionError("a broken current source must refuse")


def test_three_definitions_of_one_name_each_get_their_own_key() -> None:
    """The ordinal loop: two collisions need `#2` AND `#3`, not one shared suffix."""
    body = "def f(x):\n    return {}\n"
    before = body.format(1) + body.format(2) + body.format(3)
    after = body.format(1) + body.format(2) + body.format(99)

    assert _parity.repair_shaped_functions(before, after) == ["f#3"]


def test_a_module_spec_that_cannot_be_built_refuses(monkeypatch) -> None:
    monkeypatch.setattr(_parity.importlib.util, "spec_from_loader", lambda *a, **k: None)
    try:
        _parity.load_module_from_source("VALUE = 1\n", "parity_no_spec")
    except _parity.ParityError as exc:
        assert "module spec" in str(exc)
        return
    raise AssertionError("a missing spec must refuse")


def test_an_endless_generator_is_truncated_at_the_cap(monkeypatch) -> None:
    """The cap bounds ITEMS, which is what stops an infinite generator hanging the run."""
    monkeypatch.setattr(_parity, "ITERATOR_MATERIALISE_CAP", 5)
    endless = _parity.load_module_from_source(
        "def gen():\n    n = 0\n    while True:\n        yield n\n        n += 1\n", "parity_endless"
    )

    rendered = _parity.outcome(endless.gen, ())

    assert "truncated at 5" in rendered[1]


def test_changed_python_paths_degrades_to_empty_outside_a_repo(tmp_path: Path) -> None:
    assert _parity.changed_python_paths(tmp_path / "not-a-repo") == []


def test_an_unreadable_worktree_path_is_uncomparable_not_clean(tmp_path: Path) -> None:
    repo = seeded_repo(tmp_path / "repo")
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "gone.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-m", "add"],
        cwd=repo, check=True, capture_output=True,
    )
    (repo / "scripts" / "gone.py").unlink()

    report = _parity._render_repairs(repo, ["scripts/gone.py"], "HEAD")

    assert "scripts/gone.py" in report["uncomparable"]


def test_the_cli_prints_both_branches_against_a_committed_ref(tmp_path: Path, monkeypatch, capsys) -> None:
    """The payload has a clean branch and a repairs branch; both carry the skipped label.

    The retired rendering said "No repair-shaped function changes" or named the
    repaired functions, and appended `skipped: N uncomparable path(s)` either way.
    Those three facts are payload keys now: `files` (empty versus named),
    `next_step` (None versus the INTENDED-delta obligation, which only the repairs
    branch owes), and `skipped`, which keeps the WORD that marks those paths as
    unexamined rather than leaving a bare count to read as data.
    """
    repo = seeded_repo(tmp_path / "repo")
    target = repo / "scripts" / "gate.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def verdict(x):\n    return bool(x)\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-m", "ship"],
        cwd=repo, check=True, capture_output=True,
    )

    code, clean = _run_cli(monkeypatch, capsys, "--repo-root", str(repo), "--against", "HEAD")
    clean_payload = yaml.safe_load(clean)
    assert code == 0
    assert clean_payload["files"] == {}
    assert clean_payload["next_step"] is None
    assert clean_payload["skipped"].startswith("skipped:")

    target.write_text("def verdict(x):\n    return False\n", encoding="utf-8")
    code, repairs = _run_cli(monkeypatch, capsys, "--repo-root", str(repo), "--against", "HEAD")
    repairs_payload = yaml.safe_load(repairs)

    assert code == 0
    assert repairs_payload["files"] == {"scripts/gate.py": ["verdict"]}
    assert repairs_payload["skipped"].startswith("skipped:")
    assert "INTENDED delta" in repairs_payload["next_step"]


def test_a_snapshot_that_is_not_an_object_is_discarded(tmp_path: Path) -> None:
    """A truncated or hand-edited snapshot must not be read as a valid baseline."""
    snapshot_dir = tmp_path / ".charness" / "reviewer-boundary"
    snapshot_dir.mkdir(parents=True)
    (snapshot_dir / "snapshot.json").write_text("[]", encoding="utf-8")

    assert _parity.snapshot_payload(tmp_path) == {}


def test_a_truncated_status_field_is_skipped(tmp_path: Path, monkeypatch) -> None:
    """`git status -z` fields shorter than `XY path` carry no path to keep."""

    class _Proc:
        returncode = 0
        stdout = "??\0 M scripts/real.py\0"

    monkeypatch.setattr(_parity.subprocess, "run", lambda *a, **k: _Proc())

    assert _parity.changed_python_paths(tmp_path) == ["scripts/real.py"]


def test_the_entrypoint_reports_a_parity_error_on_stderr(tmp_path: Path) -> None:
    """Covers the `__main__` block: a ParityError must exit 1 with a message, not a traceback."""
    repo = seeded_repo(tmp_path / "repo")
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "broken.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-m", "ship"],
        cwd=repo, check=True, capture_output=True,
    )
    (repo / "scripts" / "broken.py").write_text("def broken(:\n", encoding="utf-8")

    result = run_script(
        "scripts/parity_harness.py", "--repo-root", str(repo), "--against", "HEAD",
        "--paths", "scripts/broken.py",
    )

    assert result.returncode == 1
    assert "cannot parse" in result.stderr

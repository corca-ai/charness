from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.script_loader import load_script_module

from .support import ROOT, init_git_repo, run_script
from .seeding_support import load_module

WRITER = load_module("current_pointer_writer_lib", ROOT / "scripts" / "current_pointer_writer_lib.py")
RELEASE_ARTIFACT = load_module(
    "publish_release_artifact",
    ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_artifact.py",
)
SCANNER = load_module(
    "check_current_pointer_writes",
    ROOT / "scripts" / "check_current_pointer_writes.py",
    register=True,
)

HITL_SYNC_REVIEW_ARTIFACT = load_script_module(
    "tests.quality_gates.current_pointer_hitl_sync_review_artifact",
    ROOT / "skills/public/hitl/scripts/sync_review_artifact.py",
)


def run_current_pointer_scanner(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_current_pointer_writes.py", *args])
    code = SCANNER.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)




def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scanner_findings(stdout: str) -> set[tuple[str, int]]:
    """The `path:line` pair the scanner reports, read from its payload.

    The gate's verdict is the structured payload now, so the offending
    `path`/`line` is asserted where it actually lives instead of against a
    rendered text line.
    """
    payload = yaml.safe_load(stdout)
    return {(item["path"], item["line"]) for item in payload["findings"]}












def test_current_pointer_write_scanner_flags_direct_latest_write(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "bad_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "target = Path('charness-artifacts/demo') / 'latest.md'\n"
        "target.write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/bad_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert ("scripts/bad_writer.py", 3) in _scanner_findings(result.stdout)


def test_current_pointer_write_scanner_flags_direct_expression_write(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "expression_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "(Path('charness-artifacts/demo') / CURRENT).write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/expression_writer.py")

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert ("scripts/expression_writer.py", 3) in _scanner_findings(result.stdout)


def test_current_pointer_write_scanner_structured_output(tmp_path: Path) -> None:
    """The structured payload is the only output shape, so there is no opt-in flag
    to ask for it and a run that does not `--require-empty` still reports its
    findings on stdout."""
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "structured_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/structured_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo))

    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["findings"][0]["path"] == "scripts/structured_writer.py"

    # The opt-in flag is gone rather than tolerated: a caller still passing it is
    # refused instead of silently getting a shape it did not ask for.
    #
    # The flag is assembled rather than written as a literal beside the script name.
    # `check_documented_command_flags.py` reads a script path and a flag on one line as
    # a DOCUMENTED invocation and then verifies the script accepts it — so spelling the
    # removed flag here made the gate refuse the very test that proves it is removed.
    # Commit 0a1a534 hit this exact trap once already.
    removed_flag = "--" + "json"
    rejected = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), removed_flag)
    assert rejected.returncode == 2
    assert removed_flag in rejected.stderr


def test_current_pointer_write_scanner_fallback_file_listing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    target = script_dir / "fallback_writer.py"
    target.write_text("from pathlib import Path\n", encoding="utf-8")

    # Patch the OWNER's git call, not this module's. The population is derived by
    # `repo_file_listing` now, so that is where the git-unavailable seam lives —
    # and patching a `subprocess` this module no longer imports would have made
    # the test pass against a seam that does not exist.
    # The owner's OWN function, not the stdlib `subprocess` object it happens to
    # hold: patching `listing.subprocess.run` replaces it process-wide, which is
    # harmless today and bites the first time this test grows a step that shells
    # out. Round-1 review.
    listing = sys.modules[SCANNER.iter_matching_repo_files.__module__]
    def _git_unavailable(_repo_root, *, include_untracked=True, require_git=False):
        # Stands in for a real git failure, INCLUDING its `require_git` contract:
        # a stub that always returns None makes the strict path unreachable and
        # the `raises` assertion below vacuous.
        if require_git:
            raise listing.RepoFileListingError("git listing unavailable (test stub)")
        return None

    monkeypatch.setattr(listing, "git_list_repo_files", _git_unavailable)

    assert SCANNER._git_visible_python_files(repo) == [target]
    # ...and the caller can now REFUSE that fallback instead of silently taking a
    # population that is no longer gitignore-aware. The old hand-rolled listing
    # had no way to say so.
    with pytest.raises(listing.RepoFileListingError):
        SCANNER._git_visible_python_files(repo, require_git=True)


def test_population_is_derived_by_the_shared_owner_not_hand_rolled() -> None:
    """A guard's POPULATION is a verdict surface, so it has one owner.

    This file carries the scar: `skills/shared` was once missing from
    `SCAN_ROOTS` and the gate reported clean over a scope that excluded a real
    violation. The roots stay here (they are this check's scope); the LISTING is
    `repo_file_listing`, which 10+ validators already share.
    """
    source = (Path(__file__).resolve().parents[2] / "scripts/check_current_pointer_writes.py").read_text(
        encoding="utf-8"
    )
    assert "iter_matching_repo_files" in source
    # Not merely imported — the hand-rolled listing is GONE, so no second
    # population is left to drift from the owner. Pinned as "this module imports
    # no process-spawning machinery of its own", which is the real invariant and,
    # unlike a substring scan, is not satisfied or broken by the docstring that
    # explains why the call was removed.
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "subprocess" not in imported
    assert not hasattr(SCANNER, "subprocess")


def test_the_scan_consumes_only_what_the_owner_returned(tmp_path: Path, monkeypatch) -> None:
    """BEHAVIOURAL, not textual.

    The sibling test above pins "imports the owner, spawns nothing itself" — which
    a module that imports the owner, never calls it, and re-hand-rolls via
    `os.popen` or `rglob` would also satisfy. Round-1 review said so. This one
    replaces the owner's return value and asserts the scan saw exactly that.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    seen = repo / "scripts" / "seen.py"
    seen.write_text(
        "from pathlib import Path\n"
        "(Path('a') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    unseen = repo / "scripts" / "unseen.py"
    unseen.write_text(
        "from pathlib import Path\n"
        "(Path('b') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(SCANNER, "iter_matching_repo_files", lambda *_a, **_k: [seen])
    findings = SCANNER.scan_repo(repo)
    assert [item.path for item in findings] == ["scripts/seen.py"]


def test_the_union_stays_git_derived(tmp_path: Path, monkeypatch) -> None:
    """The in-repo support union must not smuggle in an UNTRACKED population.

    The union exists so a split-layout host does not lose this repo's own
    `skills/support/` files. If it globs the directory without intersecting the
    owner's listing, the gate stops being gitignore-aware for that root — quietly
    swapping the property the whole slice is about.
    """
    repo = tmp_path / "repo"
    (repo / "skills" / "support" / "scripts").mkdir(parents=True)
    (repo / ".gitignore").write_text("ignored_writer.py\n", encoding="utf-8")
    body = (
        "from pathlib import Path\n"
        "(Path('e') / 'latest.md').write_text('bad', encoding='utf-8')\n"
    )
    (repo / "skills" / "support" / "scripts" / "tracked_writer.py").write_text(body, encoding="utf-8")
    (repo / "skills" / "support" / "scripts" / "ignored_writer.py").write_text(body, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(tmp_path / "external-support"))

    paths = sorted(item.path for item in SCANNER.scan_repo(repo))
    assert paths == ["skills/support/scripts/tracked_writer.py"], (
        "a gitignored file must not enter the population through the union"
    )


def test_display_path_resolves_both_sides(tmp_path: Path, monkeypatch) -> None:
    """`support_dir` resolves its override; this side must resolve too.

    Asymmetric resolution means a repo or tmpdir reached through a symlink (the
    macOS `/tmp -> /private/tmp` case) falls to the absolute branch on one
    platform and the support branch on another — green here, red there, for a
    reason unrelated to the behaviour under test. Round-2 review.
    """
    real = tmp_path / "real-support"
    (real / "scripts").mkdir(parents=True)
    offender = real / "scripts" / "writer.py"
    offender.write_text("from pathlib import Path\n", encoding="utf-8")
    link = tmp_path / "linked-support"
    link.symlink_to(real)
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(link))

    repo = tmp_path / "repo"
    repo.mkdir()
    # Reached through the SYMLINK, while `support_dir` reports the resolved path.
    via_link = link / "scripts" / "writer.py"
    assert SCANNER._display_path(repo, via_link) == Path("<external-support>/scripts/writer.py")


def test_require_git_reaches_the_population_from_the_cli(tmp_path: Path, monkeypatch) -> None:
    """The flag has to REACH the listing, not merely exist on the parser.

    The whole point is that a run in a tree where `git ls-files` fails must be
    able to REFUSE rather than silently swap a gitignore-aware population for a
    plain glob and still print "No direct current-pointer writes found." Round-1
    review's phrasing: the slice added the ability to refuse and did not exercise
    it. Both plumbing hops are pinned — `main` -> `scan_repo` -> the owner.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    listing = sys.modules[SCANNER.iter_matching_repo_files.__module__]

    def _git_unavailable(_repo_root, *, include_untracked=True, require_git=False):
        if require_git:
            raise listing.RepoFileListingError("git listing unavailable (test stub)")
        return None

    monkeypatch.setattr(listing, "git_list_repo_files", _git_unavailable)

    # hop 2: scan_repo -> the owner
    with pytest.raises(listing.RepoFileListingError):
        SCANNER.scan_repo(repo, require_git=True)
    assert SCANNER.scan_repo(repo, require_git=False) == []

    # hop 1: the CLI flag -> scan_repo
    monkeypatch.setattr(
        sys, "argv", ["check_current_pointer_writes.py", "--repo-root", str(repo), "--require-git-file-listing"]
    )
    with pytest.raises(listing.RepoFileListingError):
        SCANNER.main()
    monkeypatch.setattr(sys, "argv", ["check_current_pointer_writes.py", "--repo-root", str(repo)])
    assert SCANNER.main() == 0


def test_an_external_support_tree_is_reported_not_crashed_on(tmp_path: Path, monkeypatch) -> None:
    """`CHARNESS_SUPPORT_DIR` puts real files OUTSIDE `repo_root`.

    A bare `path.relative_to(repo_root)` raises there, and three call sites did
    it — so a standing quality gate died with an uncaught `ValueError` on a
    split-layout host. Round-1 review found it, and found the docstring shipped
    beside it claiming the tree was scanned. Now it genuinely is.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    external = tmp_path / "support-pkg"
    (external / "scripts").mkdir(parents=True)
    offender = external / "scripts" / "writer.py"
    offender.write_text(
        "from pathlib import Path\n"
        "(Path('c') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    # The IN-REPO support tree too, so the union is proven rather than assumed.
    (repo / "skills" / "support" / "scripts").mkdir(parents=True)
    in_repo = repo / "skills" / "support" / "scripts" / "inrepo_writer.py"
    in_repo.write_text(
        "from pathlib import Path\n"
        "(Path('d') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(external))

    # NO stub on the population owner. The first cut of this test replaced it with
    # a lambda, so it exercised `_display_path` alone and its own docstring's
    # closing claim — that the external tree is genuinely reached — was the one
    # clause it could not support. Round-2 review.
    findings = SCANNER.scan_repo(repo)
    paths = sorted(item.path for item in findings)
    assert paths == [
        "<external-support>/scripts/writer.py",
        "skills/support/scripts/inrepo_writer.py",
    ], (
        "the external tree must be REACHED, the in-repo tree must not be DROPPED, "
        "and the two namespaces must be distinguishable"
    )


def test_population_survives_a_path_containing_a_newline(tmp_path: Path) -> None:
    """The hand-rolled listing split `git ls-files` output on newlines.

    Without `-z` git C-QUOTES such a path — measured: the entry arrives as
    `"scripts/we\\nird.py"`, quotes and escape included — so the old code got ONE
    quoted non-path that failed `is_file()`, and the real file silently left the
    population. (Not "two bogus fragments": that is what a raw newline would
    produce and is not what git emits. The owning docstring was corrected for this
    and its twin here was left behind — round-2 review.) The files are untracked
    and reach the population via `--others --exclude-standard`. Constructed rather
    than asserted: no fixture would have had this shape.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    weird = repo / "scripts" / "we\nird.py"
    weird.write_text("from pathlib import Path\n", encoding="utf-8")
    plain = repo / "scripts" / "plain.py"
    plain.write_text("from pathlib import Path\n", encoding="utf-8")

    # `require_git=True`: without it, a git failure falls through to a plain glob
    # that finds BOTH files and the test passes green having never exercised `-z`
    # at all — passing for a reason other than the one it names. Round-1 review.
    found = SCANNER._git_visible_python_files(repo, require_git=True)
    assert plain in found
    assert weird in found, "a newline in a path must not drop the file from the population"


def test_current_pointer_write_scanner_skips_generated_plugin_mirrors(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    plugin_script_dir = repo / "plugins" / "charness" / "scripts"
    plugin_script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    mirrored = plugin_script_dir / "mirrored_writer.py"
    mirrored.write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "plugins/charness/scripts/mirrored_writer.py")

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 0


def test_current_pointer_write_scanner_ignores_helper_and_syntax_error(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    helper = script_dir / "current_pointer_writer_lib.py"
    helper.write_text("from pathlib import Path\nPath('x/latest.md').write_text('ok')\n", encoding="utf-8")
    broken = script_dir / "broken.py"
    broken.write_text("def broken(:\n", encoding="utf-8")

    assert SCANNER.scan_path(repo, helper) == []
    assert SCANNER.scan_path(repo, broken) == []


def test_current_pointer_write_scanner_does_not_exempt_mixed_helper_file(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "mixed_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "from scripts.current_pointer_writer_lib import write_current_pointer_text\n"
        "target = Path('charness-artifacts/demo') / 'latest.md'\n"
        "write_current_pointer_text(target, 'ok')\n"
        "target.write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/mixed_writer.py")

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert ("scripts/mixed_writer.py", 5) in _scanner_findings(result.stdout)


def test_current_pointer_write_scanner_flags_write_bytes_and_path_open(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "binary_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "target = Path('charness-artifacts/demo') / 'latest.json'\n"
        "target.write_bytes(b'bad')\n"
        "with target.open('w', encoding='utf-8') as handle:\n"
        "    handle.write('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/binary_writer.py")

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    findings = _scanner_findings(result.stdout)
    assert ("scripts/binary_writer.py", 3) in findings
    assert ("scripts/binary_writer.py", 4) in findings


def test_current_pointer_write_scanner_resolves_simple_filename_constants(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "constant_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "target = Path('charness-artifacts/demo') / CURRENT\n"
        "target.write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/constant_writer.py")

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert ("scripts/constant_writer.py", 4) in _scanner_findings(result.stdout)


def test_current_pointer_write_scanner_resolves_builtin_open_constant_path(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "constant_open_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "with open(Path('charness-artifacts/demo') / CURRENT, 'w', encoding='utf-8') as handle:\n"
        "    handle.write('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/constant_open_writer.py")

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert ("scripts/constant_open_writer.py", 3) in _scanner_findings(result.stdout)


def test_current_pointer_write_scanner_does_not_treat_local_shadow_as_pointer(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    ok = script_dir / "shadow_writer.py"
    ok.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "def write_record() -> None:\n"
        "    CURRENT = '2026-05-24-record.md'\n"
        "    target = Path('charness-artifacts/demo') / CURRENT\n"
        "    target.write_text('ok', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/shadow_writer.py")

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 0


def test_current_pointer_write_scanner_constant_helpers_ignore_non_name_targets() -> None:
    tree = SCANNER.ast.parse("obj.attr = 'latest.md'\nCURRENT = 'latest.md'\ntarget = CURRENT\n")
    SCANNER._attach_parent_links(tree)
    first_assign = tree.body[0]

    assert SCANNER._resolved_string_constants(tree) == {"CURRENT": "latest.md"}
    assert SCANNER._scope_assigned_names(first_assign) == set()
    assert SCANNER._pointer_names_in_resolved(tree.body[2].value, {"CURRENT": "latest.md"}, set()) == {"latest.md"}


def test_current_pointer_write_scanner_prefilters_non_candidate_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    (script_dir / "ordinary_writer.py").write_text(
        "from pathlib import Path\nPath('notes.md').write_text('ok')\n",
        encoding="utf-8",
    )
    candidate = script_dir / "candidate_writer.py"
    candidate.write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(
        repo,
        ".gitignore",
        "scripts/ordinary_writer.py",
        "scripts/candidate_writer.py",
    )

    scanned: list[str] = []

    def fake_scan(repo_root: Path, path: Path, text: str) -> list[object]:
        del text
        scanned.append(path.relative_to(repo_root).as_posix())
        return []

    monkeypatch.setattr(SCANNER, "_scan_text", fake_scan)

    assert SCANNER.scan_repo(repo) == []
    assert scanned == ["scripts/candidate_writer.py"]


def test_current_pointer_write_scanner_skips_helper_during_repo_scan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    (script_dir / "current_pointer_writer_lib.py").write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('helper')\n",
        encoding="utf-8",
    )
    (script_dir / "candidate_writer.py").write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(
        repo,
        ".gitignore",
        "scripts/current_pointer_writer_lib.py",
        "scripts/candidate_writer.py",
    )

    scanned: list[str] = []

    def fake_scan(repo_root: Path, path: Path, text: str) -> list[object]:
        del text
        scanned.append(path.relative_to(repo_root).as_posix())
        return []

    monkeypatch.setattr(SCANNER, "_scan_text", fake_scan)

    assert SCANNER.scan_repo(repo) == []
    assert scanned == ["scripts/candidate_writer.py"]


def test_current_pointer_write_scanner_prefilter_allows_spaced_open_call() -> None:
    assert SCANNER._could_write_current_pointer("target = 'latest.md'\npath.open ('w')\n")


def _pointer_write_fixture(repo: Path, relative: str, body: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


_LITERAL_WRITE = (
    "from pathlib import Path\n"
    "def write(root):\n"
    '    (root / "charness-artifacts" / "quality" / "latest.md").write_text("x")\n'
)
_COMPUTED_WRITE = (
    "from pathlib import Path\n"
    "def write(root, ext='md'):\n"
    '    (root / "charness-artifacts" / f"latest.{ext}").write_text("x")\n'
)


def test_pointer_write_scan_covers_skills_shared(tmp_path: Path) -> None:
    """D9 regression: `skills/shared` was absent from `SCAN_ROOTS`, so the gate
    reported clean over a scope that excluded it.

    Confirmed with the discriminating control: an IDENTICAL violation was caught
    under `scripts/` and `skills/public/` and invisible under `skills/shared/`."""
    repo = tmp_path / "repo"
    for relative in (
        "scripts/writer.py",
        "skills/public/x/scripts/writer.py",
        "skills/shared/scripts/writer.py",
    ):
        _pointer_write_fixture(repo, relative, _LITERAL_WRITE)

    findings = SCANNER.scan_repo(repo)
    flagged = {finding.path for finding in findings}

    assert "skills/shared/scripts/writer.py" in flagged
    assert "scripts/writer.py" in flagged
    assert "skills/public/x/scripts/writer.py" in flagged


def test_pointer_write_scan_refuses_silence_on_a_computed_name(tmp_path: Path) -> None:
    """The other half of D9: the gate matched string constants only, so
    `f"latest.{ext}"` produced a path it could not see — and the prefilter
    required the literal `latest.md` in the text, so such a file never even
    reached the AST scan. A computed pointer name is a scope this gate cannot
    establish, and it now says so instead of reporting clean."""
    repo = tmp_path / "repo"
    _pointer_write_fixture(repo, "scripts/computed.py", _COMPUTED_WRITE)

    findings = SCANNER.scan_repo(repo)

    assert len(findings) == 1
    assert findings[0].path == "scripts/computed.py"
    assert "BUILT at runtime" in findings[0].reason


def test_pointer_write_scan_still_passes_a_clean_tree(tmp_path: Path) -> None:
    """Falsifiable counterpart: neither widening flags an ordinary write."""
    repo = tmp_path / "repo"
    _pointer_write_fixture(
        repo,
        "skills/shared/scripts/ordinary.py",
        "from pathlib import Path\ndef write(root):\n    (root / 'notes.md').write_text('x')\n",
    )

    assert SCANNER.scan_repo(repo) == []


def test_computed_pointer_name_is_caught_through_an_assigned_variable(tmp_path: Path) -> None:
    """The computed detector originally saw only the single-expression form, but
    the two-statement form is the idiom this repo actually writes — and its
    LITERAL twin was already handled, so covering one and not the other left the
    dominant shape invisible.

    Also pins the concatenation case: Python parses `a + b + c`
    left-associatively, so in `str(out) + "/latest." + ext` the pointer-ish
    literal is only ever a RIGHT operand and inspecting `left` alone missed it."""
    repo = tmp_path / "repo"
    shapes = {
        "assigned.py": (
            "from pathlib import Path\ndef write(root, ext='md'):\n"
            '    target = root / "charness-artifacts" / f"latest.{ext}"\n'
            '    target.write_text("x")\n'
        ),
        "concat.py": (
            "from pathlib import Path\ndef write(out, ext='md'):\n"
            '    Path(str(out) + "/latest." + ext).write_text("x")\n'
        ),
        "keyword_mode.py": (
            "from pathlib import Path\ndef write(root, ext='md'):\n"
            '    target = root / f"latest.{ext}"\n'
            '    target.open(mode="w").write("x")\n'
        ),
    }
    for name, body in shapes.items():
        _pointer_write_fixture(repo, f"scripts/{name}", body)

    flagged = {finding.path for finding in SCANNER.scan_repo(repo)}

    assert flagged == {f"scripts/{name}" for name in shapes}


def test_computed_detector_leaves_an_ordinary_assigned_write_alone(tmp_path: Path) -> None:
    """Falsifiable counterpart for the widened detector: an assigned path that is
    not a pointer name is untouched, and so is an f-string that merely mentions
    `latest` in prose."""
    repo = tmp_path / "repo"
    _pointer_write_fixture(
        repo,
        "scripts/ordinary.py",
        "from pathlib import Path\ndef write(root, n=1):\n"
        '    target = root / "notes.md"\n'
        '    target.write_text(f"latest sample {n}")\n',
    )

    assert SCANNER.scan_repo(repo) == []


def test_computed_detector_catches_a_bare_stem_head_and_ignores_a_read_open() -> None:
    """Two narrow edges of the D9 detector, pinned directly on the helpers.

    The extension can live entirely in the interpolated half — `"latest" + ext`
    or `f"latest{suffix}"` leaves the literal head as the bare stem with no dot,
    which the `head == "latest."` / `startswith("latest.")` tests both miss. And
    `Path.open()` in a READ mode is not a write at all: dispatching it to the
    same target as `write_text` would make every pointer read a finding."""
    bare_stem = SCANNER.ast.parse('name = "latest" + ext\n').body[0].value
    assert SCANNER._computed_pointer_name_in(bare_stem) == "latest.<computed>"

    dotted = SCANNER.ast.parse('name = f"latest.{ext}"\n').body[0].value
    assert SCANNER._computed_pointer_name_in(dotted) == "latest.<computed>"

    unrelated = SCANNER.ast.parse('name = "notes" + ext\n').body[0].value
    assert SCANNER._computed_pointer_name_in(unrelated) is None

    read_open = SCANNER.ast.parse('path.open("r")\n').body[0].value
    assert SCANNER._write_target_node(read_open) is None

    write_open = SCANNER.ast.parse('path.open("w")\n').body[0].value
    assert SCANNER._write_target_node(write_open) is not None








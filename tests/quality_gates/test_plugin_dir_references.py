from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

from .support import ROOT

_check = import_repo_module(ROOT / "scripts/check_plugin_dir_references.py", "scripts.check_plugin_dir_references")


def run_check(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_plugin_dir_references.py", *args])
    try:
        returncode = _check.main()
    except _check.ValidationError as exc:
        print(str(exc), file=sys.stderr)
        returncode = 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def write(repo: Path, rel: str, body: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_a_reference_resolving_in_the_package_passes(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/skills/hitl/scripts/check_chunk_contract.py", "# shipped\n")
    write(repo, "skills/shared/references/x.md", "See `<plugin-dir>/skills/hitl/scripts/check_chunk_contract.py`.\n")

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0
    assert "Validated" in result.stdout


def test_the_kind_flattened_spelling_is_refused(tmp_path: Path, monkeypatch, capsys) -> None:
    """The A3 defect class: `skills/public/<skill>/` is the AUTHORING layout.

    The exporter flattens the kind level away, so a `<plugin-dir>/skills/public/...`
    reference names nothing a consumer installed. This is the exact mistake the
    placeholder exists to make checkable.
    """
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/skills/hitl/scripts/check_chunk_contract.py", "# shipped\n")
    write(
        repo,
        "skills/shared/references/x.md",
        "See `<plugin-dir>/skills/public/hitl/scripts/check_chunk_contract.py`.\n",
    )

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "skills/public/hitl" in result.stderr


def test_a_dangling_target_is_refused(tmp_path: Path, monkeypatch, capsys) -> None:
    """`<repo-root>/` can never have this property; that is the whole point of adopting this one."""
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/README.md", "# pkg\n")
    write(repo, "skills/shared/references/x.md", "See `<plugin-dir>/scripts/gone.py`.\n")

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "scripts/gone.py" in result.stderr


def test_a_fenced_example_is_not_resolved(tmp_path: Path, monkeypatch, capsys) -> None:
    """A doc TEACHING the placeholder must be able to show a shape that does not resolve."""
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/README.md", "# pkg\n")
    write(
        repo,
        "docs/guide.md",
        "Wrong:\n\n```text\n<plugin-dir>/skills/public/hitl/scripts/x.py\n```\n",
    )

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_a_sentence_ending_period_is_not_part_of_the_target(tmp_path: Path, monkeypatch, capsys) -> None:
    """The un-backticked case is the only one the strip actually reaches.

    The first version of this test used a BACKTICKED reference followed by a
    comma — both outside the capture already — so it passed with the strip
    deleted. This one fails without it.
    """
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/shared/scripts/x.py", "# shipped\n")
    write(repo, "docs/guide.md", "The helper lives at <plugin-dir>/shared/scripts/x.py.\n")

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_a_repo_without_a_plugin_package_says_so_rather_than_passing_silently(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A consumer or temp repo has nothing to resolve against.

    Printing "nothing was resolved" instead of a bare success is the difference
    between a checked tree and an unchecked one — the silent-zero shape this
    goal's whole class came from.
    """
    repo = tmp_path / "repo"
    write(repo, "docs/guide.md", "See `<plugin-dir>/scripts/whatever.py`.\n")

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0
    assert "nothing was resolved" in result.stdout


def test_the_mirror_copy_of_a_doc_is_not_scanned_twice(tmp_path: Path, monkeypatch, capsys) -> None:
    """The generated copy carries the same references; reporting it doubles every finding.

    A guard for this was written and was DEAD: no entry in `DOC_GLOBS` can match a
    path under `plugins/`, so the glob anchoring is what does the work. The guard
    is gone and the property is asserted where it actually lives — the doc set —
    rather than by a test that passed with the guard deleted.
    """
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/README.md", "# pkg\n")
    write(repo, "plugins/charness/shared/references/x.md", "See `<plugin-dir>/scripts/gone.py`.\n")
    write(repo, "skills/shared/references/ok.md", "no references here\n")

    scanned = {
        path.relative_to(repo).as_posix()
        for path in _check.iter_matching_repo_files(repo, _check.DOC_GLOBS)
    }
    assert not any(path.startswith("plugins/") for path in scanned), scanned

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_a_renamed_package_is_still_resolved_against(tmp_path: Path, monkeypatch, capsys) -> None:
    """The package name is manifest-derived. A hardcoded `plugins/charness` made a
    rename exit 0 with "nothing was resolved" — every reference silently unchecked
    while the run read green, which is the exact class this gate closes."""
    repo = tmp_path / "repo"
    write(repo, "plugins/renamed/scripts/x.py", "# shipped\n")
    write(repo, "skills/shared/references/a.md", "See `<plugin-dir>/scripts/x.py`.\n")

    ok = run_check(monkeypatch, capsys, "--repo-root", str(repo))
    assert ok.returncode == 0, ok.stderr
    assert "renamed" in ok.stdout

    write(repo, "skills/shared/references/b.md", "See `<plugin-dir>/scripts/gone.py`.\n")
    refused = run_check(monkeypatch, capsys, "--repo-root", str(repo))
    assert refused.returncode == 1


def test_a_target_escaping_the_package_root_is_refused(tmp_path: Path, monkeypatch, capsys) -> None:
    """`plugin_root / "/etc/hostname"` is `/etc/hostname` under pathlib, and a `..`
    that climbs out and back in still resolves — both named paths outside the
    installed package and both used to PASS."""
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/README.md", "# pkg\n")
    write(repo, "skills/shared/references/a.md", "See `<plugin-dir>/../charness/README.md`.\n")

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "escapes-package-root" in result.stderr


def test_an_absolute_target_is_refused(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/README.md", "# pkg\n")
    write(repo, "skills/shared/references/a.md", "See `<plugin-dir>//etc/hostname`.\n")

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "escapes-package-root" in result.stderr


def test_a_templated_target_is_skipped_and_COUNTED(tmp_path: Path, monkeypatch, capsys) -> None:
    """Truncating at the first `<` left the target `skills/`, which exists — so the
    canonical teaching lines were reported as validated on a prefix. Skipping is
    right; skipping SILENTLY is what made it a false green."""
    repo = tmp_path / "repo"
    write(repo, "plugins/charness/skills/hitl/x.py", "# shipped\n")
    write(repo, "skills/shared/references/a.md", "Write `<plugin-dir>/skills/<skill>/scripts/x.py`.\n")

    result = run_check(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0
    assert "1 templated" in result.stdout


def test_the_live_tree_resolves(monkeypatch, capsys) -> None:
    """Pins the adoption: every `<plugin-dir>/` reference this repo ships must resolve."""
    result = run_check(monkeypatch, capsys, "--repo-root", str(ROOT))

    assert result.returncode == 0, result.stderr

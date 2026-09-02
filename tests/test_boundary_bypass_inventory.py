"""In-process tests for the boundary-bypass probe.

These deliberately exercise the probe the high-testability way the probe itself
advocates: import the ``*_lib`` and call ``find_boundary_bypass_candidates``
directly on a synthetic repo (no subprocess), asserting on the returned dict.
The synthetic repo is built with the new ``Repo`` DSL — showing its ``build()``
half is boundary-agnostic and supports exactly this in-process style.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

from tests.dsl import Repo

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "inventory_boundary_bypass_lib", ROOT / "scripts" / "gates" / "inventory_boundary_bypass_lib.py"
)
assert _SPEC is not None and _SPEC.loader is not None
LIB = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(LIB)

IMPORT_SAFE = "\n".join(
    [
        "def main() -> int:",
        "    print('ok')",
        "    return 0",
        "",
        "if __name__ == '__main__':",
        "    raise SystemExit(main())",
        "",
    ]
)
NOT_IMPORT_SAFE = "import sys\nprint('side effect at import')\nsys.exit(0)\n"
IMPORT_SAFE_INTERNAL_BOUNDARY = "\n".join(
    [
        "import subprocess",
        "",
        "def main() -> int:",
        "    subprocess.run(['git', 'status'], check=False)",
        "    return 0",
        "",
        "if __name__ == '__main__':",
        "    raise SystemExit(main())",
        "",
    ]
)


def _subprocess_test(*, returncode: int, behavior: bool) -> str:
    body = [
        "from support import run_script",
        "def test_x(tmp_path):",
        '    result = run_script("scripts/foo.py", "--repo-root", str(tmp_path))',
        f"    assert result.returncode == {returncode}",
    ]
    if behavior:
        body.append("    import json; payload = json.loads(result.stdout); assert payload")
    else:
        body.append('    assert "boom" in result.stderr')
    return "\n".join(body) + "\n"


def test_flags_subprocess_test_of_import_safe_script(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo.py", _subprocess_test(returncode=0, behavior=True))
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["schemaVersion"] == "charness.quality.boundary_bypass_inventory.v2"
    assert out["call_site_fingerprint_algo_version"] == "1"
    assert out["summary"]["candidate_count"] == 1
    cand = out["candidates"][0]
    assert cand["test_file"] == "tests/test_foo.py"
    assert cand["import_safe_targets"] == ["scripts/foo.py"]
    assert cand["clean_inprocess_targets"] == ["scripts/foo.py"]
    assert cand["internal_boundary_targets"] == []
    assert cand["behavior_assert"] is True
    assert cand["likely_keep_boundary"] is False
    assert len(cand["call_site_member_hashes"]) == 1
    assert out["summary"]["convertible_count"] == 1
    assert out["summary"]["internal_boundary_count"] == 0


def test_call_site_fingerprint_ignores_test_path_and_retains_duplicate_members(tmp_path: Path) -> None:
    """A move is identity-neutral; repeated identical spawn calls remain visible."""
    body = _subprocess_test(returncode=0, behavior=True)
    moved = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/renamed/test_foo.py", body)
        .build(tmp_path / "moved")
    )
    duplicated = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo.py", body.replace(
            "    assert result.returncode == 0",
            "    second = run_script(\"scripts/foo.py\", \"--repo-root\", str(tmp_path))\n"
            "    assert result.returncode == 0\n"
            "    assert second.returncode == 0",
        ))
        .build(tmp_path / "duplicated")
    )

    moved_members = LIB.find_boundary_bypass_candidates(moved)["candidates"][0]["call_site_member_hashes"]
    duplicated_members = LIB.find_boundary_bypass_candidates(duplicated)["candidates"][0]["call_site_member_hashes"]

    assert len(moved_members) == 1
    assert duplicated_members == [moved_members[0], moved_members[0]]
    assert LIB.call_site_content_fingerprint(moved_members) != LIB.call_site_content_fingerprint(duplicated_members)


def test_call_site_fingerprint_excludes_non_candidate_spawn_calls(tmp_path: Path) -> None:
    """An unrelated non-import-safe spawn must not rotate the candidate key."""
    clean = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("scripts/not_a_candidate.py", NOT_IMPORT_SAFE)
        .file("tests/test_foo.py", _subprocess_test(returncode=0, behavior=True))
        .build(tmp_path / "clean")
    )
    mixed = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("scripts/not_a_candidate.py", NOT_IMPORT_SAFE)
        .file(
            "tests/test_foo.py",
            _subprocess_test(returncode=0, behavior=True).replace(
                "    assert result.returncode == 0",
                "    noise = run_script('scripts/not_a_candidate.py')\n"
                "    assert result.returncode == 0\n"
                "    assert noise.returncode == 0",
            ),
        )
        .build(tmp_path / "mixed")
    )

    clean_candidate = LIB.find_boundary_bypass_candidates(clean)["candidates"][0]
    mixed_candidate = LIB.find_boundary_bypass_candidates(mixed)["candidates"][0]

    assert mixed_candidate["import_safe_targets"] == clean_candidate["import_safe_targets"] == ["scripts/foo.py"]
    assert mixed_candidate["call_site_member_hashes"] == clean_candidate["call_site_member_hashes"]


def test_syntax_invalid_spawn_source_yields_no_ast_backed_candidate(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo.py", "from support import run_script\nrun_script('scripts/foo.py'\n")
        .build(tmp_path)
    )

    assert LIB.find_boundary_bypass_candidates(repo)["candidates"] == []


def test_yaml_stdout_parse_counts_as_behavior_assertion(tmp_path: Path) -> None:
    test_body = _subprocess_test(returncode=0, behavior=False).replace(
        'assert "boom" in result.stderr',
        "import yaml; payload = yaml.safe_load(result.stdout); assert payload",
    )
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo.py", test_body)
        .build(tmp_path)
    )

    candidate = LIB.find_boundary_bypass_candidates(repo)["candidates"][0]

    assert candidate["behavior_assert"] is True
    assert candidate["likely_keep_boundary"] is False


def test_yaml_stderr_parse_is_not_behavior_assertion(tmp_path: Path) -> None:
    test_body = _subprocess_test(returncode=1, behavior=False).replace(
        'assert "boom" in result.stderr',
        "import yaml; payload = yaml.safe_load(result.stderr); assert payload",
    )
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo.py", test_body)
        .build(tmp_path)
    )

    candidate = LIB.find_boundary_bypass_candidates(repo)["candidates"][0]

    assert candidate["behavior_assert"] is False
    assert candidate["likely_keep_boundary"] is True


def test_ignores_in_process_test(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file(
            "tests/test_foo_inproc.py",
            "def test_x():\n    from scripts import foo\n    assert foo.main() == 0\n",
        )
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 0


def test_ignores_subprocess_test_of_non_import_safe_script(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", NOT_IMPORT_SAFE)
        .file("tests/test_foo.py", _subprocess_test(returncode=0, behavior=True))
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 0


def test_flags_exit_contract_test_as_likely_keep_boundary(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo_cli.py", _subprocess_test(returncode=1, behavior=False))
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 1
    assert out["candidates"][0]["likely_keep_boundary"] is True
    assert out["summary"]["convertible_count"] == 0
    assert out["summary"]["keep_boundary_count"] == 1


def test_ignores_script_path_named_only_in_assertion_string(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("scripts/bar.py", NOT_IMPORT_SAFE)
        .file(
            "tests/test_foo.py",
            "\n".join(
                [
                    "from support import run_script",
                    "def test_x():",
                    "    result = run_script('scripts/bar.py')",
                    "    assert 'scripts/foo.py' not in result.stderr",
                    "",
                ]
            ),
        )
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 0


def test_ignores_script_path_passed_as_data_argument_to_spawned_command(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/release_changed_line_coverage.py", IMPORT_SAFE_INTERNAL_BOUNDARY)
        .file("skills/public/setup/scripts/inspect_repo.py", IMPORT_SAFE)
        .file(
            "tests/test_release.py",
            "\n".join(
                [
                    "from support import run_script",
                    "def test_x():",
                    "    result = run_script(",
                    "        'scripts/release_changed_line_coverage.py',",
                    "        '--paths',",
                    "        'skills/public/setup/scripts/inspect_repo.py',",
                    "    )",
                    "    assert result.returncode == 0",
                    "",
                ]
            ),
        )
        .build(tmp_path)
    )

    out = LIB.find_boundary_bypass_candidates(repo)

    assert out["summary"]["candidate_count"] == 1
    cand = out["candidates"][0]
    assert cand["import_safe_targets"] == ["scripts/release_changed_line_coverage.py"]
    assert cand["clean_inprocess_targets"] == []
    assert cand["internal_boundary_targets"] == ["scripts/release_changed_line_coverage.py"]


def test_finds_spawn_command_passed_by_keyword_argument(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file(
            "tests/test_foo.py",
            "\n".join(
                [
                    "import subprocess",
                    "def test_x():",
                    "    result = subprocess.run(args=['python3', 'scripts/foo.py'], capture_output=True)",
                    "    assert result.returncode == 0",
                    "    import json; assert json.loads(result.stdout or '{}') == {}",
                    "",
                ]
            ),
        )
        .build(tmp_path)
    )

    out = LIB.find_boundary_bypass_candidates(repo)

    assert out["summary"]["candidate_count"] == 1
    assert out["candidates"][0]["clean_inprocess_targets"] == ["scripts/foo.py"]


def test_read_text_alone_is_not_behavior_assertion(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file(
            "tests/test_foo.py",
            "\n".join(
                [
                    "from support import run_script",
                    "def test_x(tmp_path):",
                    "    result = run_script('scripts/foo.py')",
                    "    assert result.returncode == 1",
                    "    assert 'boom' in result.stderr",
                    "    assert (tmp_path / 'out.txt').read_text() == 'ok'",
                    "",
                ]
            ),
        )
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 1
    assert out["candidates"][0]["behavior_assert"] is False
    assert out["candidates"][0]["likely_keep_boundary"] is True
    assert out["summary"]["convertible_count"] == 0


def test_flags_internal_boundary_targets_and_excludes_from_convertible_count(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE_INTERNAL_BOUNDARY)
        .file("tests/test_foo.py", _subprocess_test(returncode=0, behavior=True))
        .build(tmp_path)
    )
    out = LIB.find_boundary_bypass_candidates(repo)
    assert out["summary"]["candidate_count"] == 1
    assert out["summary"]["convertible_count"] == 0
    assert out["summary"]["internal_boundary_count"] == 1
    cand = out["candidates"][0]
    assert cand["import_safe_targets"] == ["scripts/foo.py"]
    assert cand["clean_inprocess_targets"] == []
    assert cand["internal_boundary_targets"] == ["scripts/foo.py"]


def test_inventory_boundary_bypass_cli_summary_omits_full_candidates(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file("tests/test_foo.py", _subprocess_test(returncode=0, behavior=True))
        .build(tmp_path)
    )
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "inventory_boundary_bypass_cli_under_test",
        ROOT / "scripts" / "gates" / "inventory_boundary_bypass.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(
        sys,
        "argv",
        ["inventory_boundary_bypass.py", "--repo-root", str(repo), "--summary"],
    )

    assert module.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)

    assert "candidates" not in payload
    assert payload["summary"]["candidate_count"] == 1
    assert payload["clean_inprocess_samples"] == [
        {
            "test_file": "tests/test_foo.py",
            "clean_inprocess_targets": ["scripts/foo.py"],
        }
    ]
    assert payload["summary_note"] == "summary is triage output; drop --summary for full candidate attribution"

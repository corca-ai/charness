from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# Both modules do bare sibling imports (`from prompt_mutant_lib import ...` /
# `from artifact_naming_lib import slugify`), so scripts/ must be on sys.path
# when they are exec'd standalone here (mirrors test_skill_efficiency_ab.py).
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

lib = load_script_module("prompt_mutant_lib_under_test", ROOT / "scripts" / "prompt_mutant_lib.py")
cli = load_script_module("generate_prompt_mutants_under_test", ROOT / "scripts" / "generate_prompt_mutants.py")


# --- splitter ----------------------------------------------------------------

FIXTURE_MD = (
    "Preamble line 1.\n"
    "Preamble line 2.\n"
    "\n"
    "# One\n"
    "Intro to one.\n"
    "\n"
    "## Sub A\n"
    "Body A line 1.\n"
    "Body A line 2.\n"
    "\n"
    "### Sub A Detail\n"
    "Body detail.\n"
    "\n"
    "## Sub B\n"
    "Body B.\n"
    "\n"
    "# Two\n"
    "Intro to two.\n"
    "\n"
    "## Sub C\n"
    "Body C.\n"
)


def test_split_units_produces_one_unit_per_heading_plus_preamble() -> None:
    units = lib.split_units(FIXTURE_MD)
    # preamble + One, Sub A, Sub A Detail, Sub B, Two, Sub C = 7
    assert len(units) == 7
    assert units[0]["heading_path"] == ["preamble"]
    assert units[0]["heading_level"] == 0
    titles = [u["heading_path"][-1] for u in units[1:]]
    assert titles == ["One", "Sub A", "Sub A Detail", "Sub B", "Two", "Sub C"]
    levels = [u["heading_level"] for u in units[1:]]
    assert levels == [1, 2, 3, 2, 1, 2]


def test_split_units_top_level_flags_match_nesting() -> None:
    units = lib.split_units(FIXTURE_MD)
    by_title = {u["heading_path"][-1]: u for u in units[1:]}
    assert units[0]["top_level"] is True  # preamble
    assert by_title["One"]["top_level"] is True
    assert by_title["Two"]["top_level"] is True
    # Nested under One/Sub A/Two respectively -- never top-level.
    assert by_title["Sub A"]["top_level"] is False
    assert by_title["Sub A Detail"]["top_level"] is False
    assert by_title["Sub B"]["top_level"] is False
    assert by_title["Sub C"]["top_level"] is False


def test_split_units_heading_path_chains_reflect_ancestry() -> None:
    units = lib.split_units(FIXTURE_MD)
    by_title = {u["heading_path"][-1]: u for u in units[1:]}
    assert by_title["Sub A"]["heading_path"] == ["One", "Sub A"]
    assert by_title["Sub A Detail"]["heading_path"] == ["One", "Sub A", "Sub A Detail"]
    assert by_title["Sub B"]["heading_path"] == ["One", "Sub B"]
    assert by_title["Sub C"]["heading_path"] == ["Two", "Sub C"]


def test_split_units_section_boundaries_fold_deeper_headings_into_parent() -> None:
    # "### Sub A Detail" stays INSIDE the "## Sub A" unit's own content (it is
    # not stopped by a deeper heading), but ALSO gets its own standalone unit.
    units = lib.split_units(FIXTURE_MD)
    by_title = {u["heading_path"][-1]: u for u in units[1:]}
    sub_a = by_title["Sub A"]["content"]
    assert "## Sub A" in sub_a and "### Sub A Detail" in sub_a and "Body detail." in sub_a
    assert "## Sub B" not in sub_a and "Body B." not in sub_a  # stops at the next <=2 heading

    detail = by_title["Sub A Detail"]["content"]
    assert "### Sub A Detail" in detail and "Body detail." in detail
    assert "Body A line 1." not in detail  # its own span only, not Sub A's intro
    assert "## Sub B" not in detail


def test_split_units_lossless_reassembly_over_top_level_units() -> None:
    # The lossless invariant: concatenating a file's TOP-LEVEL units (preamble
    # + the units not nested inside another unit) reproduces the file exactly.
    units = lib.split_units(FIXTURE_MD)
    assert lib.reassemble_top_level(units) == FIXTURE_MD


def test_split_units_lossless_reassembly_no_headings() -> None:
    text = "just some text\nwith no headings at all\n"
    units = lib.split_units(text)
    assert len(units) == 1  # whole file is one preamble unit
    assert units[0]["content"] == text
    assert lib.reassemble_top_level(units) == text


def test_build_unit_id_is_stable_and_deterministic() -> None:
    entries_a = lib.units_for_file("skills/x/SKILL.md", FIXTURE_MD)
    entries_b = lib.units_for_file("skills/x/SKILL.md", FIXTURE_MD)
    ids_a = [e["unit_id"] for e in entries_a]
    ids_b = [e["unit_id"] for e in entries_b]
    assert ids_a == ids_b  # same input -> same ids, every time
    assert len(ids_a) == len(set(ids_a))  # unique within one file
    for entry in entries_a:
        assert entry["unit_id"].startswith("skills/x/SKILL.md#")
        digest_suffix = entry["unit_id"].rsplit("@", 1)[-1]
        assert len(digest_suffix) == 10
        assert digest_suffix == entry["content_sha256"][:10]


def test_build_unit_id_changes_when_content_changes() -> None:
    changed = FIXTURE_MD.replace("Body A line 1.", "Body A line 1 EDITED.")
    id_before = lib.units_for_file("f.md", FIXTURE_MD)[2]["unit_id"]  # "Sub A" entry
    id_after = lib.units_for_file("f.md", changed)[2]["unit_id"]
    assert id_before != id_after


def test_build_split_manifest_rejects_unknown_granularity() -> None:
    with pytest.raises(lib.PromptMutantError):
        lib.build_split_manifest(
            Path("/tmp"), "x", "paragraph", lambda *_a: [], lambda *_a: None
        )


# --- generator (git-plumbing fixture repo) -----------------------------------


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _skill_md(section_a_body: str) -> str:
    return (
        "# X Skill\n"
        "\n"
        "## Section A\n"
        f"{section_a_body}\n"
        "## Section B\n"
        "Content B.\n"
    )


def _build_fixture_repo(tmp_path: Path, *, public_section_a_body: str = "Content A.\n") -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    plugin_dir = repo / "plugins" / "charness" / "skills" / "x"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "SKILL.md").write_text(_skill_md("Content A.\n"), encoding="utf-8")
    public_dir = repo / "skills" / "public" / "x"
    public_dir.mkdir(parents=True)
    (public_dir / "SKILL.md").write_text(_skill_md(public_section_a_body), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    baseline_sha = _git(repo, "rev-parse", "HEAD")
    return repo, baseline_sha


def _section_a_unit_id(repo: Path, baseline_sha: str) -> str:
    units_by_id, _ = lib.collect_baseline_units(repo, baseline_sha, "x")
    matches = [uid for uid, u in units_by_id.items() if u["heading_path"][-1] == "Section A"]
    assert len(matches) == 1
    return matches[0]


def test_generate_removes_unit_from_plugin_mirror_tree(tmp_path: Path) -> None:
    # The F1 blocker test: the unit must be ABSENT from plugins/... in the
    # mutant tree -- the tree the capture harness actually resolves.
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    assert len(result["units"]) == 1
    mutant_sha = result["units"][0]["mutant_sha"]
    mutated = _git(repo, "show", f"{mutant_sha}:plugins/charness/skills/x/SKILL.md")
    assert "Section A" not in mutated and "Content A." not in mutated
    assert "## Section B" in mutated and "Content B." in mutated  # sibling section untouched


def test_generate_mutates_identical_public_sibling(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Content A.\n")
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    record = result["units"][0]
    assert record["public_mutated"] is True
    assert "skills/public/x/SKILL.md" in record["files_mutated"]
    mutated_public = _git(repo, "show", f"{record['mutant_sha']}:skills/public/x/SKILL.md")
    assert "Section A" not in mutated_public and "Content A." not in mutated_public


def test_generate_leaves_differing_public_sibling_untouched(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Totally different wording.\n")
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    record = result["units"][0]
    assert record["public_mutated"] is False
    assert record["files_mutated"] == ["plugins/charness/skills/x/SKILL.md"]
    mutated_public = _git(repo, "show", f"{record['mutant_sha']}:skills/public/x/SKILL.md")
    assert "Totally different wording." in mutated_public  # unchanged


def test_generate_commit_message_is_neutral_and_uniform(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    mutant_sha = result["units"][0]["mutant_sha"]
    message = _git(repo, "show", "-s", "--format=%s", mutant_sha)
    assert message == "chore: snapshot"
    parent = _git(repo, "show", "-s", "--format=%P", mutant_sha)
    assert parent == baseline_sha


def test_generate_ref_exists_and_manifest_records_full_sha(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    record = result["units"][0]
    assert record["mutant_ref"].startswith("refs/prompt-mutants/x/")
    ref_sha = _git(repo, "rev-parse", record["mutant_ref"])
    assert ref_sha == record["mutant_sha"]
    assert len(record["mutant_sha"]) == 40  # full SHA, not abbreviated -- refs may be deleted later


def test_generate_is_idempotent(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    first = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    second = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    assert first["units"][0]["mutant_sha"] == second["units"][0]["mutant_sha"]
    assert first["units"][0]["mutant_ref"] == second["units"][0]["mutant_ref"]


def test_generate_default_selects_every_unit(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    units_by_id, _ = lib.collect_baseline_units(repo, baseline_sha, "x")
    result = lib.generate_mutants(repo, "x", baseline_sha, None)
    assert {u["unit_id"] for u in result["units"]} == set(units_by_id.keys())


def test_generate_rejects_unknown_unit_id(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    with pytest.raises(lib.PromptMutantError):
        lib.generate_mutants(repo, "x", baseline_sha, ["not-a-real-unit-id"])


def test_generate_never_touches_shared_worktree_or_index(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    lib.generate_mutants(repo, "x", baseline_sha, None)
    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, check=True
    ).stdout
    assert status == ""  # no working-tree or index change (#258 hygiene)


def test_cleanup_deletes_refs_and_reports_them(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    result = lib.generate_mutants(repo, "x", baseline_sha, None)
    created_refs = {u["mutant_ref"] for u in result["units"]}
    deleted = lib.cleanup_mutant_refs(repo, "x")
    assert set(deleted) == created_refs
    assert lib.list_mutant_refs(repo, "x") == []
    for ref in created_refs:
        rc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", ref], capture_output=True, text=True
        ).returncode
        assert rc != 0  # ref is gone


# --- CLI: split/generate/cleanup end-to-end + --help + granularity ----------


def _write_skill_fixture(root: Path, skill: str) -> None:
    plugin_dir = root / "plugins" / "charness" / "skills" / skill
    (plugin_dir / "references").mkdir(parents=True)
    (plugin_dir / "SKILL.md").write_text(FIXTURE_MD, encoding="utf-8")
    (plugin_dir / "references" / "extra.md").write_text("# Extra\nRef body.\n", encoding="utf-8")
    public_dir = root / "skills" / "public" / skill
    (public_dir / "references").mkdir(parents=True)
    (public_dir / "SKILL.md").write_text(FIXTURE_MD, encoding="utf-8")


def test_cli_split_prints_manifest_with_files_and_units(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _write_skill_fixture(tmp_path, "y")
    rc = cli.main(["split", "--repo-root", str(tmp_path), "--skill", "y"])
    assert rc == 0
    manifest = json.loads(capsys.readouterr().out)
    assert manifest["skill"] == "y"
    assert manifest["granularity"] == "section"
    assert [f["path"] for f in manifest["files"]] == [
        "plugins/charness/skills/y/SKILL.md",
        "plugins/charness/skills/y/references/extra.md",
    ]
    assert manifest["files"][0]["public_sibling"] == "skills/public/y/SKILL.md"
    assert manifest["files"][1]["public_sibling"] is None  # no public references/ sibling
    skill_md_units = [u for u in manifest["units"] if u["file"].endswith("SKILL.md")]
    assert len(skill_md_units) == 7  # preamble + 6 headings, matches FIXTURE_MD
    for unit in manifest["units"]:
        assert set(unit) == {
            "unit_id", "file", "public_sibling", "heading_path", "heading_level",
            "start_line", "end_line", "content_sha256",
        }


@pytest.mark.parametrize("argv", [[], ["split"], ["generate"], ["cleanup"]])
def test_cli_help_exits_zero_for_every_subcommand(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main([*argv, "--help"])
    assert excinfo.value.code == 0


def test_cli_split_unknown_granularity_errors(tmp_path: Path) -> None:
    _write_skill_fixture(tmp_path, "y")
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["split", "--repo-root", str(tmp_path), "--skill", "y", "--granularity", "paragraph"])
    assert excinfo.value.code != 0


def test_cli_generate_writes_manifest_and_cleanup_reports_deletion(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    out_path = tmp_path / "mutants.json"
    rc = cli.main(
        ["generate", "--repo-root", str(repo), "--skill", "x", "--baseline-ref", baseline_sha, "--out", str(out_path)]
    )
    assert rc == 0
    manifest = json.loads(out_path.read_text(encoding="utf-8"))
    assert manifest["skill"] == "x"
    assert manifest["baseline_sha"] == baseline_sha
    assert len(manifest["units"]) >= 1
    for record in manifest["units"]:
        assert len(record["mutant_sha"]) == 40

    rc = cli.main(["cleanup", "--repo-root", str(repo), "--skill", "x"])
    assert rc == 0
    assert lib.list_mutant_refs(repo, "x") == []

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


PARAGRAPH_FIXTURE_MD = (
    "Preamble para one.\n"
    "\n"
    "Preamble para two, line 1.\n"
    "Preamble para two, line 2.\n"
    "\n"
    "# One\n"
    "Claim A.\n"
    "\n"
    "Claim B.\n"
    "\n"
    "```bash\n"
    "echo first\n"
    "\n"
    "echo after blank line inside fence\n"
    "```\n"
    "\n"
    "## Sub A\n"
    "Sub A only paragraph.\n"
)


def _paragraphs(units: list[dict]) -> list[dict]:
    return [u for u in units if u["unit_kind"] == "paragraph"]


def test_paragraph_granularity_keeps_every_section_unit() -> None:
    """The coarse arm stays selectable: paragraph granularity ADDS finer units, it
    does not replace the section ones. A caller that only knew about sections before
    sees exactly what it saw."""
    sections_only = lib.split_units(PARAGRAPH_FIXTURE_MD)
    with_paragraphs = lib.split_units(PARAGRAPH_FIXTURE_MD, "paragraph")

    assert all(u["unit_kind"] == "section" for u in sections_only)
    kept = [u for u in with_paragraphs if u["unit_kind"] == "section"]
    assert kept == sections_only


def test_paragraph_units_split_on_blank_lines_but_not_inside_fences() -> None:
    """A blank line inside a fenced code block is content. Splitting there would
    build a mutant that deletes half a code block -- a malformed-markdown arm, which
    proves nothing about whether the prose was load-bearing."""
    paragraphs = _paragraphs(lib.split_units(PARAGRAPH_FIXTURE_MD, "paragraph"))
    contents = [u["content"] for u in paragraphs]

    assert "Preamble para one.\n" in contents
    assert "Preamble para two, line 1.\nPreamble para two, line 2.\n" in contents
    assert "Claim A.\n" in contents
    assert "Claim B.\n" in contents
    fenced = [c for c in contents if c.startswith("```bash")]
    assert len(fenced) == 1, contents
    assert "echo after blank line inside fence" in fenced[0]


def test_paragraph_units_exclude_the_heading_line() -> None:
    """A paragraph unit that swallowed its heading would, when applied, delete the
    heading and reparent every following paragraph into the previous section."""
    paragraphs = _paragraphs(lib.split_units(PARAGRAPH_FIXTURE_MD, "paragraph"))
    assert not any(u["content"].lstrip().startswith("#") for u in paragraphs)
    sub_a = [u for u in paragraphs if u["heading_path"][-1] == "Sub A"]
    assert [u["content"] for u in sub_a] == ["Sub A only paragraph.\n"]


def test_paragraph_units_carry_their_owning_section_path() -> None:
    """A paragraph is located by the section it argues inside. Nested headings make
    this non-trivial: a paragraph under `## Sub A` must not be attributed to `# One`,
    whose section span also contains it."""
    paragraphs = _paragraphs(lib.split_units(PARAGRAPH_FIXTURE_MD, "paragraph"))
    by_content = {u["content"]: u["heading_path"] for u in paragraphs}

    assert by_content["Preamble para one.\n"] == ["preamble"]
    assert by_content["Claim A.\n"] == ["One"]
    assert by_content["Sub A only paragraph.\n"] == ["One", "Sub A"]


def test_paragraph_units_are_exact_line_slices_and_never_overlap() -> None:
    """The whole pipeline re-slices the original text at these boundaries to build a
    mutant, so an off-by-one produces a mutant that deletes the wrong text while
    still looking plausible. Overlap would let two arms claim the same line."""
    lines = PARAGRAPH_FIXTURE_MD.splitlines(keepends=True)
    paragraphs = _paragraphs(lib.split_units(PARAGRAPH_FIXTURE_MD, "paragraph"))

    spans = sorted((u["start_line"], u["end_line"]) for u in paragraphs)
    for unit in paragraphs:
        sliced = "".join(lines[unit["start_line"] - 1 : unit["end_line"]])
        assert sliced == unit["content"], unit
    for (_, prev_end), (next_start, _) in zip(spans, spans[1:]):
        assert prev_end <= next_start - 1, spans


def test_paragraph_granularity_preserves_the_lossless_tiling_proof() -> None:
    """`reassemble_top_level` is the splitter's core invariant. Paragraph units are
    additional finer entries, so they must stay out of the flat tiling or
    reassembly would emit every line twice."""
    units = lib.split_units(PARAGRAPH_FIXTURE_MD, "paragraph")
    assert lib.reassemble_top_level(units) == PARAGRAPH_FIXTURE_MD
    assert all(not u["top_level"] for u in _paragraphs(units))


def test_paragraph_units_get_distinct_stable_ids() -> None:
    """Two paragraphs in one section share a heading path, so the content digest is
    what separates their unit ids -- and identical prose in different sections must
    still be independently selectable."""
    entries = lib.units_for_file("a/SKILL.md", PARAGRAPH_FIXTURE_MD, "paragraph")
    ids = [e["unit_id"] for e in entries]
    assert len(ids) == len(set(ids)), ids
    again = lib.units_for_file("a/SKILL.md", PARAGRAPH_FIXTURE_MD, "paragraph")
    assert [e["unit_id"] for e in again] == ids


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
    """`paragraph` used to be the rejected value here; it is implemented now, so the
    guard is exercised with a value that is still unimplemented. The guard itself
    stays load-bearing: `build_split_manifest` is a public entry point that callers
    reach without argparse's `choices` in front of it."""
    with pytest.raises(lib.PromptMutantError):
        lib.build_split_manifest(
            Path("/tmp"), "x", "sentence", lambda *_a: [], lambda *_a: None
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


def test_generate_builds_a_mutant_from_a_paragraph_unit(tmp_path: Path) -> None:
    """`split --granularity paragraph` is useless if the next pipeline stage cannot
    consume what it mints. Without granularity threaded through `generate`, every
    paragraph unit id comes back `unknown unit id` -- a flag that advertises
    selection handles no arm can be built from."""
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Content A.\n")
    units_by_id, _ = lib.collect_baseline_units(repo, baseline_sha, "x", "paragraph")
    paragraphs = {
        uid: u for uid, u in units_by_id.items() if u["unit_kind"] == "paragraph"
    }
    target_id, target = next(
        (uid, u) for uid, u in paragraphs.items() if u["content"] == "Content A.\n"
    )

    result = lib.generate_mutants(repo, "x", baseline_sha, [target_id], None, "paragraph")

    assert len(result["units"]) == 1
    unit = result["units"][0]
    baseline_text = (repo / "plugins" / "charness" / "skills" / "x" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    mutated = _git(repo, "show", f"{unit['mutant_sha']}:plugins/charness/skills/x/SKILL.md")
    # Exactly the paragraph, nothing else: an off-by-one here builds a plausible
    # mutant that removes the wrong text.
    assert mutated + "\n" == baseline_text.replace(target["content"], "", 1)


def test_generate_mutates_the_public_sibling_for_paragraph_units_too(tmp_path: Path) -> None:
    """The public sibling is split to match the unit under mutation. Split at section
    granularity, a paragraph's content hash can never equal a public SECTION unit's,
    so every paragraph arm would silently report `public_mutated: False` and leave the
    text readable in the captured workspace's public copy."""
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Content A.\n")
    units_by_id, _ = lib.collect_baseline_units(repo, baseline_sha, "x", "paragraph")
    target_id = next(
        uid
        for uid, u in units_by_id.items()
        if u["unit_kind"] == "paragraph" and u["content"] == "Content A.\n"
    )

    result = lib.generate_mutants(repo, "x", baseline_sha, [target_id], None, "paragraph")

    unit = result["units"][0]
    assert unit["public_mutated"] is True
    assert "skills/public/x/SKILL.md" in unit["files_mutated"]


def test_collect_baseline_units_refuses_duplicate_unit_ids(tmp_path: Path) -> None:
    """`unit_id` is file + heading path + content digest, so two byte-identical
    paragraphs in one section collide. A silent dict overwrite would drop an arm and
    quietly shrink the experiment, reporting a smaller denominator as if complete."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    plugin_dir = repo / "plugins" / "charness" / "skills" / "x"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "SKILL.md").write_text(
        "# X\n\n## Section A\nRepeated note.\n\nRepeated note.\n",
        encoding="utf-8",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    baseline_sha = _git(repo, "rev-parse", "HEAD")

    with pytest.raises(lib.PromptMutantError) as excinfo:
        lib.collect_baseline_units(repo, baseline_sha, "x", "paragraph")
    assert "duplicate unit id" in str(excinfo.value)


def test_split_units_rejects_an_unimplemented_granularity() -> None:
    """Validated in the splitter itself, not only in `build_split_manifest`: the
    `generate` path and library callers reach `split_units` directly, and silently
    falling back to section behaviour would run an experiment at the wrong
    granularity and emit a plausible-looking manifest."""
    with pytest.raises(lib.PromptMutantError):
        lib.split_units(FIXTURE_MD, "sentence")


def test_paragraph_units_skip_yaml_frontmatter(tmp_path: Path) -> None:
    """Removing frontmatter does not remove a claim -- it makes the skill fail to
    register, so the arm reads as a strong DETECTED while proving nothing about
    whether any prose was load-bearing."""
    text = "---\nname: x\ndescription: y\n---\n\nReal preamble claim.\n\n# One\nBody.\n"
    paragraphs = _paragraphs(lib.split_units(text, "paragraph"))
    contents = [u["content"] for u in paragraphs]

    assert "Real preamble claim.\n" in contents
    assert not any("name: x" in c for c in contents)
    assert not any(c.lstrip().startswith("---") for c in contents)


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
    assert "replacement_content_sha256" not in record
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


def test_generate_rewrites_unit_and_identical_public_sibling(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Content A.\n")
    unit_id = _section_a_unit_id(repo, baseline_sha)
    replacement_text = "## Replacement A\nReplacement body.\n"
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id], replacement_text)
    record = result["units"][0]
    assert record["operator_kind"] == "rewrite"
    assert record["replacement_content_sha256"] == lib.unit_content_sha256(replacement_text)
    assert record["public_mutated"] is True
    assert "skills/public/x/SKILL.md" in record["files_mutated"]

    expected_plugin = (
        "# X Skill\n"
        "\n"
        "## Replacement A\n"
        "Replacement body.\n"
        "## Section B\n"
        "Content B."
    )
    mutated_plugin = _git(repo, "show", f"{record['mutant_sha']}:plugins/charness/skills/x/SKILL.md")
    assert mutated_plugin == expected_plugin
    mutated_public = _git(repo, "show", f"{record['mutant_sha']}:skills/public/x/SKILL.md")
    assert mutated_public == expected_plugin


def test_generate_rewrite_adds_boundary_newline_when_replacement_lacks_one(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Content A.\n")
    unit_id = _section_a_unit_id(repo, baseline_sha)
    replacement_text = "## Replacement A\nReplacement body."
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id], replacement_text)
    record = result["units"][0]
    applied_text = replacement_text + "\n"
    assert record["replacement_content_sha256"] == lib.unit_content_sha256(applied_text)

    mutated_plugin = _git(repo, "show", f"{record['mutant_sha']}:plugins/charness/skills/x/SKILL.md")
    assert "Replacement body.\n## Section B" in mutated_plugin


def test_generate_leaves_ambiguous_public_duplicate_untouched(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Content A.\n")
    duplicate_public = (
        "# X Skill\n"
        "\n"
        "## Section A\n"
        "Content A.\n"
        "\n"
        "## Section A\n"
        "Content A.\n"
        "\n"
        "## Section B\n"
        "Content B.\n"
    )
    (repo / "skills" / "public" / "x" / "SKILL.md").write_text(duplicate_public, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "duplicate public")
    baseline_sha = _git(repo, "rev-parse", "HEAD")
    unit_id = _section_a_unit_id(repo, baseline_sha)

    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id], "## Replacement A\n")
    record = result["units"][0]
    assert record["public_mutated"] is False
    assert record["files_mutated"] == ["plugins/charness/skills/x/SKILL.md"]
    mutated_public = _git(repo, "show", f"{record['mutant_sha']}:skills/public/x/SKILL.md")
    assert mutated_public.count("## Section A") == 2


def test_generate_rewrites_only_plugin_when_public_differs(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path, public_section_a_body="Totally different wording.\n")
    unit_id = _section_a_unit_id(repo, baseline_sha)
    replacement_text = "## Replacement A\nReplacement body.\n"
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id], replacement_text)
    record = result["units"][0]
    assert record["operator_kind"] == "rewrite"
    assert record["public_mutated"] is False
    assert record["files_mutated"] == ["plugins/charness/skills/x/SKILL.md"]
    mutated_public = _git(repo, "show", f"{record['mutant_sha']}:skills/public/x/SKILL.md")
    assert "Totally different wording." in mutated_public


def test_generate_rewrite_is_idempotent(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    replacement_text = "## Replacement A\nReplacement body.\n"
    first = lib.generate_mutants(repo, "x", baseline_sha, [unit_id], replacement_text)
    second = lib.generate_mutants(repo, "x", baseline_sha, [unit_id], replacement_text)
    assert first["baseline_snapshot_sha"] == second["baseline_snapshot_sha"]
    assert first["units"][0]["mutant_sha"] == second["units"][0]["mutant_sha"]
    assert first["units"][0]["replacement_content_sha256"] == second["units"][0]["replacement_content_sha256"]


def test_generate_snapshot_commits_are_parentless_and_metadata_identical(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    record = result["units"][0]
    baseline_snapshot_sha = result["baseline_snapshot_sha"]
    mutant_sha = record["mutant_sha"]

    baseline_tree = _git(repo, "rev-parse", f"{baseline_sha}^{{tree}}")
    baseline_snapshot_tree = _git(repo, "rev-parse", f"{baseline_snapshot_sha}^{{tree}}")
    mutant_tree = _git(repo, "rev-parse", f"{mutant_sha}^{{tree}}")
    assert baseline_snapshot_tree == baseline_tree
    assert mutant_tree != baseline_tree

    baseline_snapshot_parent = _git(repo, "show", "-s", "--format=%P", baseline_snapshot_sha)
    mutant_parent = _git(repo, "show", "-s", "--format=%P", mutant_sha)
    assert baseline_snapshot_parent == ""
    assert mutant_parent == ""

    baseline_payload = _git(repo, "cat-file", "commit", baseline_snapshot_sha)
    mutant_payload = _git(repo, "cat-file", "commit", mutant_sha)
    assert baseline_payload.splitlines()[1:] == mutant_payload.splitlines()[1:]

    assert _git(repo, "show", "-s", "--format=%s", baseline_snapshot_sha) == "chore: snapshot"
    assert _git(repo, "show", "-s", "--format=%s", mutant_sha) == "chore: snapshot"

    mutated = _git(repo, "show", f"{mutant_sha}:plugins/charness/skills/x/SKILL.md")
    assert "Section A" not in mutated and "Content A." not in mutated
    assert "## Section B" in mutated and "Content B." in mutated

    assert subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{mutant_sha}^"], capture_output=True, text=True
    ).returncode != 0

    show_output = _git(repo, "show", mutant_sha)
    assert "Section A" not in show_output
    assert "Content A." not in show_output
    assert "## Section B" in show_output
    assert "Content B." in show_output


def test_generate_manifest_records_raw_snapshot_shas_without_refs(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    record = result["units"][0]
    assert "mutant_ref" not in record
    assert len(result["baseline_snapshot_sha"]) == 40
    assert len(record["mutant_sha"]) == 40
    assert lib.list_mutant_refs(repo, "x") == []


def test_generate_commit_date_matches_baseline_committer_date(tmp_path: Path) -> None:
    # F5-class leak check: a fixed 2000-01-01 epoch on a mutant whose parent is
    # a real (e.g. 2026-dated) baseline is itself an arm-asymmetric oddity a
    # captured run's `git log -1` could notice. The mutant must instead reuse
    # the baseline commit's OWN committer date for both author and committer.
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    result = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    mutant_sha = result["units"][0]["mutant_sha"]
    baseline_date = _git(repo, "show", "-s", "--format=%cd", "--date=raw", baseline_sha)
    mutant_author_date = _git(repo, "show", "-s", "--format=%ad", "--date=raw", mutant_sha)
    mutant_committer_date = _git(repo, "show", "-s", "--format=%cd", "--date=raw", mutant_sha)
    assert mutant_author_date == baseline_date
    assert mutant_committer_date == baseline_date
    assert "946684800" not in baseline_date  # sanity: not accidentally the old fixed epoch


def test_generate_is_idempotent(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    first = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    second = lib.generate_mutants(repo, "x", baseline_sha, [unit_id])
    assert first["baseline_snapshot_sha"] == second["baseline_snapshot_sha"]
    assert first["units"][0]["mutant_sha"] == second["units"][0]["mutant_sha"]
    assert "mutant_ref" not in first["units"][0]
    assert "mutant_ref" not in second["units"][0]


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
    units_by_id, _ = lib.collect_baseline_units(repo, baseline_sha, "x")
    result = lib.generate_mutants(repo, "x", baseline_sha, None)
    created_refs = set()
    for record in result["units"]:
        unit = units_by_id[record["unit_id"]]
        ref = lib.mutant_ref_name("x", unit["content_sha256"])
        _git(repo, "update-ref", ref, record["mutant_sha"])
        created_refs.add(ref)
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
            "start_line", "end_line", "content_sha256", "unit_kind",
        }
        assert unit["unit_kind"] == "section"


@pytest.mark.parametrize("argv", [[], ["split"], ["generate"], ["cleanup"]])
def test_cli_help_exits_zero_for_every_subcommand(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main([*argv, "--help"])
    assert excinfo.value.code == 0


def test_cli_split_unknown_granularity_errors(tmp_path: Path) -> None:
    _write_skill_fixture(tmp_path, "y")
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["split", "--repo-root", str(tmp_path), "--skill", "y", "--granularity", "sentence"])
    assert excinfo.value.code != 0


def test_cli_granularity_choices_track_the_implemented_splitter() -> None:
    """argparse's `choices` and the splitter's own guard are two lists that must not
    drift: a choice the CLI accepts with no splitter behind it fails deep inside a
    run, and a granularity the splitter implements but the CLI rejects is
    unreachable."""
    assert cli.GRANULARITY_CHOICES == list(lib.GRANULARITIES)
    assert "section" in lib.GRANULARITIES


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
    assert len(manifest["baseline_snapshot_sha"]) == 40
    assert len(manifest["units"]) >= 1
    for record in manifest["units"]:
        assert "mutant_ref" not in record
        assert record["operator_kind"] == "removal"
        assert len(record["mutant_sha"]) == 40
    assert lib.list_mutant_refs(repo, "x") == []

    units_by_id, _ = lib.collect_baseline_units(repo, baseline_sha, "x")
    created_refs = set()
    for record in manifest["units"]:
        ref = lib.mutant_ref_name("x", units_by_id[record["unit_id"]]["content_sha256"])
        _git(repo, "update-ref", ref, record["mutant_sha"])
        created_refs.add(ref)
    rc = cli.main(["cleanup", "--repo-root", str(repo), "--skill", "x"])
    assert rc == 0
    assert created_refs and lib.list_mutant_refs(repo, "x") == []


def test_cli_generate_rewrite_records_operator_and_hash(tmp_path: Path) -> None:
    repo, baseline_sha = _build_fixture_repo(tmp_path)
    unit_id = _section_a_unit_id(repo, baseline_sha)
    out_path = tmp_path / "mutants.json"
    replacement_text = "## Replacement A\nReplacement body.\n"
    rc = cli.main(
        [
            "generate",
            "--repo-root",
            str(repo),
            "--skill",
            "x",
            "--baseline-ref",
            baseline_sha,
            "--unit-id",
            unit_id,
            "--replacement-text",
            replacement_text,
            "--sentinel",
            "required_summary_fragment=slim-pointer.md",
            "--sentinel",
            json.dumps(
                {
                    "name": "planner marker",
                    "channel": "trace_command_marker",
                    "value": "scripts/plan.py",
                    "deterministic": True,
                    "reason": "planner should run",
                }
            ),
            "--out",
            str(out_path),
        ]
    )
    assert rc == 0
    manifest = json.loads(out_path.read_text(encoding="utf-8"))
    assert manifest["units"][0]["operator_kind"] == "rewrite"
    assert manifest["units"][0]["replacement_content_sha256"] == lib.unit_content_sha256(replacement_text)
    assert manifest["sentinels"] == [
        {
            "channel": "required_summary_fragment",
            "value": "slim-pointer.md",
            "deterministic": True,
            "name": None,
            "reason": None,
        },
        {
            "channel": "trace_command_marker",
            "value": "scripts/plan.py",
            "deterministic": True,
            "name": "planner marker",
            "reason": "planner should run",
        },
    ]

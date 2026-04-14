from __future__ import annotations

from pathlib import Path

from .support import ROOT, make_minimal_skill_repo, run_script


def test_validate_skills_rejects_unquoted_description(tmp_path: Path) -> None:
    repo = make_minimal_skill_repo(
        tmp_path,
        "Use when something has punctuation: this should be rejected.",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "double-quoted" in result.stderr


def test_validate_skills_rejects_missing_references_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing `## References` section" in result.stderr


def test_validate_skills_rejects_unlisted_reference_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "## References",
                "",
                "- `references/other.md`",
            ]
        ),
        encoding="utf-8",
    )
    (references_dir / "other.md").write_text("# Other\n", encoding="utf-8")
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "unlisted reference file(s): `references/note.md`" in result.stderr


def test_validate_skills_accepts_support_skill_package(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "support" / "demo-support"
    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    references_dir.mkdir(parents=True)
    scripts_dir.mkdir()
    (references_dir / "runtime.md").write_text("# Runtime\n", encoding="utf-8")
    (scripts_dir / "helper.py").write_text("print('ok')\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo-support",
                'description: "Demo support skill."',
                "---",
                "",
                "# Demo Support",
                "",
                "## References",
                "",
                "- `references/runtime.md`",
                "- `scripts/helper.py`",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_public_skill_with_many_fenced_examples_and_no_scripts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "```bash",
                "echo one",
                "```",
                "",
                "```bash",
                "echo two",
                "```",
                "",
                "```bash",
                "echo three",
                "```",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "3+ fenced examples" in result.stderr
    assert "`scripts/`" in result.stderr


def test_validate_skills_accepts_public_skill_with_many_fenced_examples_when_scripts_exist(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    references_dir.mkdir(parents=True)
    scripts_dir.mkdir()
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (scripts_dir / "helper.py").write_text("print('ok')\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "```bash",
                "echo one",
                "```",
                "",
                "```bash",
                "echo two",
                "```",
                "",
                "```bash",
                "python3 scripts/helper.py",
                "```",
                "",
                "## References",
                "",
                "- `references/note.md`",
                "- `scripts/helper.py`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def make_public_skill_with_bootstrap(
    tmp_path: Path,
    bootstrap_body: str,
    *,
    extra_body: str = "",
    with_preflight_pointer: bool = True,
) -> Path:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    pointer_line = (
        "\n"
        "See `create-skill/references/binary-preflight.md` for the "
        "binary-preflight protocol.\n"
        if with_preflight_pointer
        else "\n"
    )
    body = "\n".join(
        [
            "---",
            "name: demo",
            'description: "Demo public skill."',
            "---",
            "",
            "# Demo",
            "",
            "## Bootstrap",
            "",
            "```bash",
            bootstrap_body.rstrip(),
            "```",
            pointer_line,
            extra_body,
            "",
            "## References",
            "",
            "- `references/note.md`",
            "",
        ]
    )
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    return repo


def test_validate_skills_rejects_undeclared_non_baseline_binary(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(tmp_path, "rg --files docs skills")
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "non-baseline" in result.stderr
    assert "`rg`" in result.stderr


def test_validate_skills_accepts_declared_non_baseline_binary(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg --files docs skills",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_required_tools_without_preflight_pointer(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg --files docs skills",
        with_preflight_pointer=False,
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "binary-preflight" in result.stderr


def test_validate_skills_rejects_swallow_pattern_on_non_baseline(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg -n 'pattern' . 2>/dev/null || true",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "swallow" in result.stderr


def test_validate_skills_rejects_or_true_swallow_on_non_baseline(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg -n 'pattern' . || true",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "swallow" in result.stderr


def test_validate_skills_allows_swallow_on_baseline_only_line(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "git config --get core.hooksPath || true\nfind .git/hooks -maxdepth 1 -type f 2>/dev/null | sort",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_ignores_non_baseline_inside_quoted_regex(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        '# Required Tools: rg\nrg -n "eslint|ruff|lefthook|husky" docs',
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_unused_required_tools_declaration(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\ngit status --short",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "never calls it" in result.stderr


def test_validate_skills_allows_local_script_invocation(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        'python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .',
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_support_skill_skips_preflight_gate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "support" / "demo-support"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo-support",
                'description: "Demo support skill."',
                "---",
                "",
                "# Demo Support",
                "",
                "## Bootstrap",
                "",
                "```bash",
                "rg --files docs",
                "```",
                "",
                "## References",
                "",
                "- `references/runtime.md`",
            ]
        ),
        encoding="utf-8",
    )
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "runtime.md").write_text("# Runtime\n", encoding="utf-8")
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
def test_check_skill_contracts_rejects_missing_required_snippet(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    handoff_skill_dir = repo / "skills" / "public" / "handoff"
    gather_skill_dir = repo / "skills" / "public" / "gather"
    create_skill_dir = repo / "skills" / "public" / "create-skill"
    spec_skill_dir = repo / "skills" / "public" / "spec"
    handoff_skill_dir.mkdir(parents=True)
    gather_skill_dir.mkdir(parents=True)
    create_skill_dir.mkdir(parents=True)
    spec_skill_dir.mkdir(parents=True)

    (handoff_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
        encoding="utf-8",
    )
    (gather_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (create_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "create-skill" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (spec_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = run_script("scripts/check-skill-contracts.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required contract snippet" in result.stderr

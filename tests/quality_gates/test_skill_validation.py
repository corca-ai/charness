from __future__ import annotations

from pathlib import Path

from .seeding_support import write_skill, write_text
from .support import make_minimal_skill_repo, run_script


def make_adapter_skill_repo(
    tmp_path: Path, *, with_resolver: bool = True, with_init: bool = False
) -> Path:
    repo = make_minimal_skill_repo(tmp_path, '"Demo skill."')
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir()
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        + "\n## References\n\n- `references/note.md`\n",
        encoding="utf-8",
    )
    (skill_dir / "adapter.example.yaml").write_text("version: 1\n", encoding="utf-8")
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    if with_resolver:
        (scripts_dir / "resolve_adapter.py").write_text("# resolver\n", encoding="utf-8")
    if with_init:
        (scripts_dir / "init_adapter.py").write_text(
            "# skill-owned initializer\n", encoding="utf-8"
        )
    return repo


def test_validate_skills_rejects_unquoted_description(tmp_path: Path) -> None:
    repo = make_minimal_skill_repo(
        tmp_path,
        "Use when something has punctuation: this should be rejected.",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo), real_process=True)
    assert result.returncode == 1
    assert "double-quoted" in result.stderr


def test_validate_skills_rejects_missing_references_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_skill(repo, [])
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing `## References` section" in result.stderr


def test_validate_skills_rejects_unlisted_reference_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        ["## References", "", "- `references/other.md`"],
    )
    write_text(skill_path.parent / "references" / "note.md", "# Note\n")
    write_text(skill_path.parent / "references" / "other.md", "# Other\n")
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "unlisted reference file(s): `references/note.md`" in result.stderr


def test_validate_skills_accepts_support_skill_package(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        [
            "## References",
            "",
            "- `references/runtime.md`",
            "- `scripts/helper.py`",
        ],
        package="support",
        skill_id="demo-support",
        description="Demo support skill.",
        title="Demo Support",
    )
    write_text(skill_path.parent / "references" / "runtime.md", "# Runtime\n")
    write_text(skill_path.parent / "scripts" / "helper.py", "print('ok')\n")
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_accepts_adapter_example_without_init_adapter(tmp_path: Path) -> None:
    repo = make_adapter_skill_repo(tmp_path, with_init=False)
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_requires_adapter_resolver(tmp_path: Path) -> None:
    repo = make_adapter_skill_repo(tmp_path, with_resolver=False, with_init=True)
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "scripts/resolve_adapter.py is missing" in result.stderr


def test_validate_skills_rejects_missing_shared_reference_from_reference_file(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        ["## References", "", "- `references/note.md`"],
    )
    write_text(
        skill_path.parent / "references" / "note.md",
        "Apply `../../../shared/references/does-not-exist.md`.\n",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "references/note.md references missing path" in result.stderr
    assert "does-not-exist.md" in result.stderr


def test_validate_skills_accepts_flat_exported_plugin_layout(tmp_path: Path) -> None:
    repo = tmp_path / "plugin"
    skill_dir = repo / "skills" / "demo"
    references_dir = skill_dir / "references"
    shared_refs = repo / "shared" / "references"
    references_dir.mkdir(parents=True)
    shared_refs.mkdir(parents=True)
    (shared_refs / "source-bound-records.md").write_text("# Source Bound\n", encoding="utf-8")
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
                "Apply `../../shared/references/source-bound-records.md`.",
                "",
                "## References",
                "",
                "- `references/note.md`",
                "- `../../shared/references/source-bound-records.md`",
            ]
        ),
        encoding="utf-8",
    )
    (references_dir / "note.md").write_text(
        "Apply `../../../shared/references/source-bound-records.md`.\n",
        encoding="utf-8",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "Validated 1 skill packages (1 public, 0 support)." in result.stdout


def test_validate_skills_rejects_public_skill_with_many_fenced_examples_and_no_scripts(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        [
            "## Bootstrap",
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
        ],
    )
    write_text(skill_path.parent / "references" / "note.md", "# Note\n")
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Bootstrap with 3+ fenced examples" in result.stderr
    assert "`scripts/`" in result.stderr


def test_validate_skills_accepts_public_skill_with_many_fenced_examples_when_scripts_exist(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        [
            "## Bootstrap",
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
            'python3 "$SKILL_DIR/scripts/helper.py"',
            "```",
            "",
            "## References",
            "",
            "- `references/note.md`",
            "- `scripts/helper.py`",
        ],
    )
    write_text(skill_path.parent / "references" / "note.md", "# Note\n")
    write_text(skill_path.parent / "scripts" / "helper.py", "print('ok')\n")
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_author_repo_internal_doc_cite(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        ["## References", "", "- `references/note.md`"],
    )
    write_text(
        skill_path.parent / "references" / "note.md",
        "Read `docs/implementation-discipline.md` before editing.\n",
    )

    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "author-repo-only cite" in result.stderr
    assert "docs/implementation-discipline.md" in result.stderr


def test_validate_skills_rejects_author_repo_internal_test_and_skill_cites(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        ["## References", "", "- `references/note.md`"],
    )
    write_text(
        skill_path.parent / "references" / "note.md",
        "\n".join(
            [
                "Regression lives at `tests/test_demo.py::test_case`.",
                "Source helper lives at `<repo-root>/skills/public/other`.",
                "Contract lives at `docs/prescribed-skill-closeout-contract.md`.",
            ]
        )
        + "\n",
    )

    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "tests/test_demo.py::test_case" in result.stderr
    assert "<repo-root>/skills/public/other" in result.stderr
    assert "docs/prescribed-skill-closeout-contract.md" in result.stderr


def test_validate_skills_allows_authoring_marker_and_operator_surfaces(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = write_skill(
        repo,
        ["## References", "", "- `references/note.md`"],
    )
    prove_path = write_skill(
        repo,
        ["## References", "", "- `references/verification-ladder.md`"],
        skill_id="prove",
        description="Impl skill.",
        title="Impl",
    )
    write_text(
        skill_path.parent / "references" / "note.md",
        "\n".join(
            [
                "`docs/index.md` is a consumer-owned operator surface (authoring-repo-internal).",
                "`docs/roadmap.md` is a consumer-owned operator surface.",
                "`docs/operator-acceptance.md` is a consumer-owned operator surface.",
                "`docs/release-notes.md` is a consumer-owned operator surface.",
                "`charness-artifacts/quality/latest.md` is repo-owned state.",
                "`docs/release-adapter.yaml` is adapter configuration.",
                "`.agents/release-adapter.yaml` is adapter configuration.",
                "`../../prove/references/verification-ladder.md` ships in the same plugin.",
                "The next cite is authoring-repo-internal, not vendored.",
                "`tests/test_demo.py` documents the source repo regression (authoring-repo-internal).",
            ]
        )
        + "\n",
    )
    write_text(prove_path.parent / "references" / "verification-ladder.md", "# Ladder\n")

    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_validate_skills_allows_many_non_bootstrap_examples_without_scripts(tmp_path: Path) -> None:
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
                "## Examples",
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
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
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
        "\nSee `../../shared/references/binary-preflight.md` for the binary-preflight protocol.\n"
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
    shared_refs = repo / "skills" / "shared" / "references"
    shared_refs.mkdir(parents=True)
    (shared_refs / "binary-preflight.md").write_text("# Binary Preflight\n", encoding="utf-8")
    return repo


def test_validate_skills_rejects_undeclared_non_baseline_binary(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(tmp_path, "rg --files docs skills")
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "non-baseline" in result.stderr
    assert "`rg`" in result.stderr


def test_validate_skills_accepts_declared_non_baseline_binary(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg --files docs skills",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_required_tools_without_preflight_pointer(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg --files docs skills",
        with_preflight_pointer=False,
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "binary-preflight" in result.stderr


def test_validate_skills_rejects_swallow_pattern_on_non_baseline(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg -n 'pattern' . 2>/dev/null || true",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "swallow" in result.stderr


def test_validate_skills_rejects_or_true_swallow_on_non_baseline(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg -n 'pattern' . || true",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "swallow" in result.stderr


def test_validate_skills_allows_swallow_on_baseline_only_line(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "git config --get core.hooksPath || true\nfind .git/hooks -maxdepth 1 -type f 2>/dev/null | sort",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_ignores_non_baseline_inside_quoted_regex(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        '# Required Tools: rg\nrg -n "eslint|ruff|lefthook|husky" docs',
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_unused_required_tools_declaration(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\ngit status --short",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "never calls it" in result.stderr


def test_validate_skills_allows_local_script_invocation(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        'python3 "$SKILL_DIR/scripts/helper.py" --repo-root .',
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_cwd_relative_runtime_script_invocation(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "python3 scripts/helper.py --repo-root .",
    )
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "helper.py").write_text("print('ok')\n", encoding="utf-8")
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "cwd-relative" in result.stderr


def test_validate_skills_rejects_source_tree_skill_invocation(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "sed -n '1,220p' skills/public/demo/SKILL.md",
    )
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "source-tree skill path" in result.stderr


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
    result = run_script("tools/validate_skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module, load_path_module
from tests.quality_gates.repo_shapes import install_committed_repo

from .support import ROOT, run_script

_check_doc_links = import_repo_module(ROOT / "scripts/check_doc_links.py", "scripts.check_doc_links")
_portable_command_carrier = load_path_module(
    "scripts.portable_command_carrier_test_surface",
    ROOT / "scripts" / "portable_command_carrier.py",
)


def run_check_doc_links(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_doc_links.py", *args])
    try:
        returncode = _check_doc_links.main()
    except _check_doc_links.ValidationError as exc:
        print(str(exc), file=sys.stderr)
        returncode = 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_check_doc_links_rejects_repo_local_absolute_path(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (docs_dir / "index.md").write_text(
        f"[root]({repo / 'README.md'})\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "absolute link" in result.stderr


def test_check_doc_links_rejects_relative_link_without_dot_slash_prefix(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text("See [guide](docs/guide.md).\n", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must start with `./` or `../`" in result.stderr


def test_check_doc_links_rejects_bare_internal_markdown_reference(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n\nSee docs/guide.md before editing.\n", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "bare internal markdown reference" in result.stderr


def test_check_doc_links_allows_runnable_commands_and_concept_tokens_in_backticks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text(
        "\n".join(
            [
                "# Demo",
                "",
                "Use the linked guide: [guide](./docs/guide.md).",
                "",
                "Runnable command in inline code: `sed -n '1,20p' docs/guide.md`.",
                "",
                "Concept tokens: `charness-concept`, `SKILL.md`, `v1.2.3`, `core.hooksPath`.",
                "",
                "```bash",
                "sed -n '1,20p' docs/guide.md",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    # Two SKILL.md files at different paths → ambiguous basename → allowed as concept.
    (docs_dir / "SKILL.md").write_text("# One\n", encoding="utf-8")
    (repo / "docs2").mkdir()
    (repo / "docs2" / "SKILL.md").write_text("# Two\n", encoding="utf-8")
    result = run_script("scripts/check_doc_links.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_backticked_nested_file_reference(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text(
        "See `docs/guide.md` for the guide.\n",
        encoding="utf-8",
    )
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "docs/guide.md" in result.stderr


def test_check_doc_links_rejects_backticked_missing_repo_path(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(
        "The old follow-up lived at `docs/missing-roadmap.md`.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "missing-artifact" in result.stderr
    assert "docs/missing-roadmap.md" in result.stderr


def test_check_doc_links_allows_portable_skill_placeholder_backticks(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "Read `<repo-root>/docs/index.md` after resolving the adapter.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_portable_skill_link_outside_package(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    skill_dir = repo / "skills" / "public" / "demo"
    docs_dir.mkdir(parents=True)
    skill_dir.mkdir(parents=True)
    (docs_dir / "index.md").write_text("# Index\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "Read [index](../../../docs/index.md) after resolving the adapter.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "portable skill link" in result.stderr
    assert "../../../docs/index.md" in result.stderr


def test_check_doc_links_allows_default_canonical_instruction_surfaces(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "CLAUDE.md").write_text("# Claude\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "See `AGENTS.md`, `CLAUDE.md`, AGENTS.md, and CLAUDE.md for house rules.\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_backticked_noncanonical_root_file(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(
        "# Demo\n\nSee `README.md` for the overview.\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "README.md" in result.stderr


def test_check_doc_links_allows_adapter_canonical_surface(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    agents_dir = repo / ".agents"
    docs_dir.mkdir(parents=True)
    agents_dir.mkdir()
    (agents_dir / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "canonical_markdown_surfaces:",
                "  - AGENTS.md",
                "  - CLAUDE.md",
                "  - docs/index.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (docs_dir / "index.md").write_text("# Index\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Current docs live in `docs/index.md`; docs/index.md is a canonical surface.\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_backticked_non_markdown_file_reference(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Run `scripts/run.py` for a demo.\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "scripts/run.py" in result.stderr


def test_check_doc_links_rejects_dot_slash_backtick_that_resolves_to_repo_file(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run-quality.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Prefer `./scripts/run-quality.sh` as the local quality gate.\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "./scripts/run-quality.sh" in result.stderr


def test_check_doc_links_rejects_unique_bare_basename(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "unique-runner.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Invoke `unique-runner.py` for the demo.\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "unique-runner.py" in result.stderr
    assert "unique-basename" in result.stderr


def test_check_doc_links_accepts_dot_slash_prefix_in_markdown_link(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Run [`./scripts/run.sh`](./scripts/run.sh) to demo.\n",
        encoding="utf-8",
    )
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_relative_link_that_escapes_repo_root(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    sibling_repo = tmp_path / "other-repo"
    docs_dir.mkdir(parents=True)
    sibling_repo.mkdir()
    (sibling_repo / "README.md").write_text("# Other Repo\n", encoding="utf-8")
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (docs_dir / "index.md").write_text(
        "[sibling](../../other-repo/README.md)\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "escapes repo root" in result.stderr
    assert "../../other-repo/README.md" in result.stderr


def test_check_doc_links_rejects_fenced_command_naming_a_missing_script(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text(
        "\n".join(["# Demo", "", "```bash", "python3 scripts/check_prose_pin.py --repo-root .", "```", ""]),
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "fenced command target" in result.stderr
    assert "scripts/check_prose_pin.py" in result.stderr


def test_check_doc_links_accepts_fenced_command_naming_an_existing_script(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "check_prose_pin.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "\n".join(["# Demo", "", "```bash", "python3 scripts/check_prose_pin.py --repo-root .", "```", ""]),
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_doc_links_ignores_fenced_commands_outside_repo_owned_paths(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    # A documented bootstrap writes and runs a temp-path script; only repo-owned
    # targets are the gate's business.
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(
        "\n".join(["# Demo", "", "```bash", "bash /tmp/charness-init.sh", "```", ""]),
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_doc_links_allows_placeholder_bearing_fenced_command_target(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "# Demo",
                "",
                "```bash",
                "python3 scripts/check_skill_surface_preflight.py --path skills/public/<skill>/SKILL.md",
                "python3 <repo-root>/scripts/local_only.py",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "scripts").mkdir()
    (repo / "scripts" / "check_skill_surface_preflight.py").write_text("print('hi')\n", encoding="utf-8")

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_doc_links_resolves_fenced_command_target_inside_its_skill_package(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "scripts").mkdir(parents=True)
    (skill_dir / "scripts" / "prepare_packet.py").write_text("print('hi')\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(["# Demo", "", "```bash", "python3 scripts/prepare_packet.py --repo-root .", "```", ""]),
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_inline_command_naming_a_missing_script(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    # The backtick checker waves through any span containing whitespace, so an
    # inline command with a flag rots exactly as invisibly as the fenced form.
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text(
        "Run `python3 scripts/check_prose_pin.py --repo-root .` before authoring.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "fenced command target" in result.stderr
    assert "scripts/check_prose_pin.py" in result.stderr


def test_check_doc_links_resolves_command_targets_against_the_git_listing(
    tmp_path: Path,
) -> None:
    # Fail-open guard: a gitignored target exists on this machine and does not
    # exist on the CI checkout, so resolving by `.exists()` would pass locally
    # and fail there. Every sibling check already resolves via the git listing.
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "scripts/local_only.py\n",
            "README.md": "\n".join(
                ["# Demo", "", "```bash", "python3 scripts/local_only.py", "```", ""]
            )
            + "\n",
        },
    )
    local_only = repo / "scripts" / "local_only.py"
    local_only.parent.mkdir(parents=True)
    local_only.write_text("print('hi')\n", encoding="utf-8")

    result = run_script("scripts/check_doc_links.py", "--repo-root", str(repo), "--require-git-file-listing")

    assert result.returncode == 1
    assert "scripts/local_only.py" in result.stderr


def test_check_doc_links_ignores_command_shaped_text_outside_a_fence(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    # Prose and inline code are the backticked-reference checker's territory; the
    # fenced-command check must not double-report them.
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(
        "# Demo\n\nThe bootstrap runs python3 scripts/missing.py during setup.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_doc_links_ignores_gitignored_markdown(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "docs/generated-*.md\n",
            "README.md": "# Demo\n\nUse the linked guide: [guide](./docs/guide.md).\n",
            "docs/guide.md": "# Guide\n",
        },
    )
    (repo / "docs" / "generated-bad.md").write_text("[bad](/tmp/not-in-repo.md)\n", encoding="utf-8")

    result = run_script("scripts/check_doc_links.py", "--repo-root", str(repo), "--require-git-file-listing")
    assert result.returncode == 0, result.stderr


# The `authoring-repo-internal` + `<repo-root>/` contradiction rule (#479 axis A2).
# Fixtures transcribed from the real live sites on 2026-08-04.
REAL_CONTRADICTION = (
    "So per *P4* of the authoring-repo-internal\n"
    "`<repo-root>/docs/design-north-star.md`, a passing slug-drift run and\n"
    '"I updated the cites" are *claims*.\n'
)


def test_refuses_the_real_authoring_repo_internal_contradiction(tmp_path: Path, monkeypatch, capsys) -> None:
    """`rename-critique.md:96` and four siblings say authoring-repo-INTERNAL, then use the consumer prefix."""
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "guide.md").write_text(REAL_CONTRADICTION, encoding="utf-8")

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "contradicts itself" in result.stderr
    assert "<authoring-repo>/" in result.stderr


def test_the_contradiction_rule_spans_a_wrapped_sentence(tmp_path: Path, monkeypatch, capsys) -> None:
    """A line-anchored ruler reported 2 of 6; the other 4 wrap between the phrase and the prefix.

    This is the denominator lesson as a test: the fixture puts the phrase on one
    line and the prefix on the next, which is the shape that hid four instances.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "guide.md").write_text(
        "The contract lives at the authoring-repo-internal\n`<repo-root>/docs/x.md`.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1


def test_the_contradiction_rule_accepts_the_repaired_spelling(tmp_path: Path, monkeypatch, capsys) -> None:
    """Proves the rule bites on the contradiction, not on the phrase."""
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "guide.md").write_text(
        "The contract lives at the authoring-repo-internal\n`<authoring-repo>/docs/x.md`.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0


def test_the_contradiction_rule_does_not_couple_separate_list_items(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The false positive a paragraph-scoped ruler would invent.

    Two independent bullets: one legitimately points at the reader's own tree,
    the other legitimately calls a different file authoring-repo-internal. No
    single sentence asserts both, so there is no contradiction to report.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "guide.md").write_text(
        "- Quality numbers live in `<repo-root>/charness-artifacts/quality/latest.md`.\n"
        "- The rule is authoring-repo-internal and lives elsewhere.\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_the_contradiction_rule_ignores_fenced_examples(tmp_path: Path, monkeypatch, capsys) -> None:
    """A doc teaching the broken shape must be able to show it."""
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "guide.md").write_text(
        "Wrong:\n\n```markdown\nthe authoring-repo-internal `<repo-root>/docs/x.md`\n```\n",
        encoding="utf-8",
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_the_contradiction_rule_finds_every_live_site_in_the_real_tree(monkeypatch, capsys) -> None:
    """Pins the six repairs. Runs against the checked-in tree, not a fixture."""
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(ROOT))

    assert result.returncode == 0, result.stderr


# The portable-package unmarked-tree rule (#479 axis A4).
#
# This rule already existed for `docs/**` and was OFF inside portable skill
# packages, because a markdown link from a skill package to an authoring-repo file
# cannot resolve for a consumer. That was true, and it is what the placeholder
# vocabulary now answers: with `<authoring-repo>/`, `<repo-root>/` and a resolvable
# `<plugin-dir>/` all available, "unmarked" stopped being a forced choice.
#
# The verdict needs no judgement about WHICH tree — only that the author named
# one. A bare `scripts/x.py` is refused whether it meant charness's tree or the
# reader's, because the reader cannot tell either.


def _portable_repo(tmp_path: Path, body: str, *, extra: dict[str, str] | None = None) -> Path:
    repo = tmp_path / "repo"
    skill = repo / "skills" / "public" / "demo"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: d\n---\n\n# Demo\n", encoding="utf-8")
    (skill / "references" / "note.md").write_text(body, encoding="utf-8")
    for rel, content in (extra or {}).items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return repo


def test_an_unmarked_repo_path_in_a_shipped_skill_doc_is_refused(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = _portable_repo(tmp_path, "Run `scripts/check_docs_graph.py` first.\n")

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "unmarked-tree" in result.stderr


def test_each_placeholder_prefix_is_accepted(tmp_path: Path, monkeypatch, capsys) -> None:
    """The repair must be available in every direction, or the rule is a trap."""
    for prefix in ("<authoring-repo>/", "<repo-root>/", "<plugin-dir>/", "<skill-dir>/"):
        repo = _portable_repo(tmp_path / prefix.strip("</>"), f"Run `{prefix}scripts/x.py`.\n")
        result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))
        assert result.returncode == 0, (prefix, result.stderr)


def test_the_placeholder_carve_out_is_what_accepts_a_marked_path(tmp_path: Path) -> None:
    """Asserted on the branch, because the end-to-end version is vacuous.

    `<` and `>` fall out of `PATHY_TOKEN_RE` anyway, so a placeholder-bearing
    token passes even with `has_portable_placeholder` deleted. The discriminating
    input is a token the classifier WOULD refuse with the prefix removed.
    """
    package_root = tmp_path / "skills" / "public" / "demo"
    package_root.mkdir(parents=True)
    args = (set(), {}, set(), set(), package_root)

    assert _check_doc_links.classify_backtick_token("<repo-root>/scripts/x.py", *args) is None
    assert _check_doc_links.classify_backtick_token("scripts/x.py", *args) == "unmarked-tree"
    assert _check_doc_links.has_portable_placeholder("<repo-root>/scripts/x.py") is True


def test_a_path_resolving_inside_the_skill_package_is_accepted(tmp_path: Path, monkeypatch, capsys) -> None:
    """A skill's OWN helper is reachable as written; demanding a marker would be noise."""
    repo = _portable_repo(
        tmp_path,
        "Run `scripts/own_helper.py`.\n",
        extra={"skills/public/demo/scripts/own_helper.py": "# own\n"},
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_shared_is_a_portable_package_for_package_relative_paths(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    shared = repo / "skills" / "shared"
    (shared / "references").mkdir(parents=True)
    (shared / "scripts").mkdir(parents=True)
    (shared / "scripts" / "helper.py").write_text("# shared helper\n", encoding="utf-8")
    (shared / "references" / "note.md").write_text(
        "Run `scripts/helper.py` from the shared package.\n", encoding="utf-8"
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert _check_doc_links.portable_skill_package_root(repo, shared / "references" / "note.md") == shared


def test_shared_unmarked_repo_path_is_refused(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    shared = repo / "skills" / "shared"
    (shared / "references").mkdir(parents=True)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "outside.py").write_text("# consumer/root helper\n", encoding="utf-8")
    (shared / "references" / "note.md").write_text(
        "The reader helper is `scripts/outside.py`.\n", encoding="utf-8"
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "unmarked-tree" in result.stderr


def test_a_shipped_skill_command_cannot_use_the_authoring_kind_layout(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _portable_repo(
        tmp_path,
        "Run `python3 skills/public/demo/scripts/helper.py --help`.\n",
        extra={
            "skills/public/demo/scripts/helper.py": "#!/usr/bin/env python3\n",
            "plugins/charness/skills/demo/scripts/helper.py": "#!/usr/bin/env python3\n",
        },
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "authoring-only kind-bearing layout" in result.stderr
    assert "<plugin-dir>/skills/demo/scripts/helper.py" in result.stderr


def test_shipped_skill_command_message_truncates_after_three_targets(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    extra = {
        f"skills/public/demo/scripts/helper{n}.py": "#!/usr/bin/env python3\n"
        for n in range(5)
    }
    body = "\n".join(
        f"Run `python3 skills/public/demo/scripts/helper{n}.py --help`." for n in range(5)
    ) + "\n"
    repo = _portable_repo(tmp_path, body, extra=extra)
    for n in range(5):
        target = repo / "plugins" / "charness" / "skills" / "demo" / "scripts" / f"helper{n}.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "#!/usr/bin/env python3\n", encoding="utf-8"
        )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert ", ..." in result.stderr
    assert result.stderr.count("skills/public/demo/scripts/helper") == 3


def test_a_shipped_skill_command_may_use_skill_dir_placeholder(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _portable_repo(
        tmp_path,
        'Run `python3 "$SKILL_DIR/scripts/helper.py" --help`.\n',
        extra={"skills/public/demo/scripts/helper.py": "#!/usr/bin/env python3\n"},
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_portable_command_detector_normalizes_dot_slash_and_skips_missing_source(
    tmp_path: Path,
) -> None:
    repo = _portable_repo(
        tmp_path,
        "Run `python3 skills/public/demo/scripts/missing.py --help`.\n",
    )
    doc = repo / "skills" / "public" / "demo" / "references" / "note.md"
    package_root = _check_doc_links.portable_skill_package_root(repo, doc)

    assert _portable_command_carrier._looks_like_repo_reference("./scripts/example.py")
    assert _portable_command_carrier.iter_unportable_command_targets(
        repo, doc, package_root
    ) == []


def test_an_authoring_skill_command_is_rejected_when_export_omits_target(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _portable_repo(
        tmp_path,
        "Run `python3 skills/public/demo/scripts/helper.py --help`.\n",
        extra={"skills/public/demo/scripts/helper.py": "#!/usr/bin/env python3\n"},
    )
    (repo / "plugins" / "charness").mkdir(parents=True)

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "export missing" in result.stderr


def test_an_authoring_skill_command_is_rejected_without_plugin_directory(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _portable_repo(
        tmp_path,
        "Run `python3 skills/public/demo/scripts/helper.py --help`.\n",
        extra={"skills/public/demo/scripts/helper.py": "#!/usr/bin/env python3\n"},
    )

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "export missing" in result.stderr


def test_a_canonical_markdown_surface_needs_no_tree_marker(tmp_path: Path) -> None:
    """`docs/index.md` means the same file in EVERY tree, so it needs no marker.

    Asserted on the classifier with an explicit canonical set, because the ORDER
    is the invariant: the first armed version ran the portable rule ahead of the
    canonical-surface check and demanded a marker on the repo's own agreed
    vocabulary — a false positive in a blocking gate. Fixed by ordering, not by
    adding an exemption.
    """
    package_root = tmp_path / "skills" / "public" / "demo"
    package_root.mkdir(parents=True)

    verdict = _check_doc_links.classify_backtick_token(
        "docs/index.md",
        set(),
        {},
        set(),
        {"docs/index.md"},
        package_root,
    )

    assert verdict is None
    # And without it in the canonical set, the same token IS refused — so the test
    # is about the canonical carve-out, not about the token happening to pass.
    assert (
        _check_doc_links.classify_backtick_token(
            "docs/index.md", set(), {}, set(), set(), package_root
        )
        == "unmarked-tree"
    )


def test_a_non_repo_shaped_token_is_not_a_tree_claim(tmp_path: Path, monkeypatch, capsys) -> None:
    """`package.json`, `a/b.txt`, a version string — none names a charness surface."""
    repo = _portable_repo(tmp_path, "Set `foo/bar.baz` and `1.2.3` and `some.thing`.\n")

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_a_fenced_example_of_the_unmarked_form_is_allowed(tmp_path: Path, monkeypatch, capsys) -> None:
    """A doc teaching the rule must be able to show the shape it forbids."""
    repo = _portable_repo(tmp_path, "Wrong:\n\n```text\n`scripts/x.py`\n```\n")

    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_the_live_tree_has_no_unmarked_portable_reference(monkeypatch, capsys) -> None:
    """Pins the 49 repairs: every shipped skill doc now names the tree it means."""
    result = run_check_doc_links(monkeypatch, capsys, "--repo-root", str(ROOT))

    assert result.returncode == 0, result.stderr

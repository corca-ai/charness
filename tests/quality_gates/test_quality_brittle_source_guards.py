from __future__ import annotations

from pathlib import Path

import yaml

from .seeding_support import load_module, run_main
from .support import ROOT

# In-process boundary conversion (testability-dsl-initiative goal 1): load the
# inventory entrypoint by file and drive its `main()` with captured stdout/stderr
# instead of crossing a process boundary. main() parses argv and returns the exit
# code, so patching sys.argv and capturing the streams reproduces the same CLI
# surface (flags, exit code, adapter-wrapped JSON payload) the boundary test read.
_MODULE = load_module(
    "inventory_brittle_source_guards",
    ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_brittle_source_guards.py",
)


def _run(repo: Path, *args: str):
    return run_main(
        _MODULE.main, "inventory_brittle_source_guards.py", "--repo-root", str(repo), *args
    )


def test_inventory_brittle_source_guards_flags_wrapped_fixed_pattern(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "README.md").write_text(
        "\n".join(
            [
                "# Demo",
                "",
                "The repo keeps behavior honest while prompts keep changing across",
                "several daily workflow edits and release checks.",
                "This prose is still written with ordinary column wrapping that",
                "can split fixed string assertions without changing rendered text.",
                "Another wrapped line keeps the heuristic honest for this target.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "docs" / "specs" / "current-product.spec.md").write_text(
        "\n".join(
            [
                "# Current Product",
                "",
                "| file | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | behavior honest while prompts keep changing across several daily workflow edits |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _run(repo, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["summary"]["brittle_count"] == 1
    finding = payload["findings"][0]
    assert finding["status"] == "brittle"
    assert finding["hard_wrapped"] is True
    assert finding["exact_found"] is False
    assert finding["normalized_found"] is True


def test_inventory_brittle_source_guards_reports_policy_without_tool(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Agents\n\nUse semantic line breaks for prose markdown.\n",
        encoding="utf-8",
    )
    nested_tool = repo / "scripts" / "package" / "check_prose_pin.py"
    nested_tool.parent.mkdir(parents=True)
    nested_tool.write_text("# recursive enforcement tool\n", encoding="utf-8")

    result = _run(repo, "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["policy"] == {
        "policy_declared": True,
        "enforcement_tools": ["scripts/package/check_prose_pin.py"],
        "policy_without_tool": False,
    }


def test_inventory_brittle_source_guards_skips_unreadable_markdown_specs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "\n".join(
            [
                "# Spec",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | Demo |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "docs" / "session-log.md").symlink_to(tmp_path / "missing-session-log.md")

    result = _run(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["summary"]["source_guard_count"] == 1
    assert payload["warnings"] == [
        {
            "type": "source_guard_markdown_unreadable",
            "path": "docs/session-log.md",
            "message": "Skipped unreadable markdown while scanning source guards: No such file or directory",
        }
    ]


def test_inventory_brittle_source_guards_ignores_hidden_workflow_dirs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".cwf" / "projects").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "\n".join(
            [
                "# Spec",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | Demo |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / ".cwf" / "projects" / "session-log.md").symlink_to(tmp_path / "missing-session-log.md")

    result = _run(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["summary"]["source_guard_count"] == 1
    assert payload["warnings"] == []


def test_inventory_brittle_source_guards_uses_bounded_default_roots(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "notes").mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "\n".join(
            [
                "# Spec",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | Demo |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "notes" / "extra.md").write_text(
        "\n".join(
            [
                "# Extra",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | Demo |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _run(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["scan_roots"] == ["AGENTS.md", "README.md", "docs", "specs"]
    assert payload["summary"]["source_guard_count"] == 1
    assert payload["findings"][0]["spec_path"] == "docs/spec.md"


def test_inventory_brittle_source_guards_scan_root_overrides_defaults(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "notes").mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "\n".join(["# Spec", "", "| README.md | fixed | Demo |", ""]),
        encoding="utf-8",
    )
    (repo / "notes" / "extra.md").write_text(
        "\n".join(["# Extra", "", "| README.md | fixed | Demo |", ""]),
        encoding="utf-8",
    )

    result = _run(
        repo,
        "--scan-root",
        "notes",
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["scan_roots"] == ["notes"]
    assert payload["summary"]["source_guard_count"] == 1
    assert payload["findings"][0]["spec_path"] == "notes/extra.md"

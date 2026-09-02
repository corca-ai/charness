from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import yaml

from .seeding_support import write_quality_adapter, write_skill, write_text
from .support import ROOT, run_loaded_script_main

SCRIPT = "skills/public/quality/scripts/validate_skill_ergonomics.py"


def _load_validate_module() -> ModuleType:
    module_path = ROOT / SCRIPT
    spec = importlib.util.spec_from_file_location(
        "tests.quality_gates.validate_skill_ergonomics", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATE = _load_validate_module()


def _evaluate(repo: Path) -> dict[str, object]:
    return VALIDATE.evaluate(repo.resolve())


def _returncode(payload: dict[str, object]) -> int:
    return 1 if VALIDATE.has_failures(payload) else 0


def _verdict(payload: dict[str, object]) -> dict[str, object]:
    """The verdict the retired human renderer used to state in prose.

    `_format_human` was deleted with the `--json` flag; the state it named (adapter
    invalid / not configured / discovery failed / pass / fail) is now payload keys.
    """
    return VALIDATE.verdict(payload)


def _emitted(result) -> dict[str, object]:
    """Parse a CLI run's stdout the way `main()` writes it: one YAML document.

    `main()` emits `{**evaluate(...), **verdict(...)}`, so the verdict keys are only
    present on the CLI payload, not on a direct `evaluate()` report.
    """
    assert result.stdout.strip(), f"expected a payload on stdout; stderr={result.stderr!r}"
    payload = yaml.safe_load(result.stdout)
    assert isinstance(payload, dict), f"expected a mapping payload, got {type(payload)!r}"
    return payload


def _seed_repo(tmp_path: Path, *, rules: list[str]) -> Path:
    repo = tmp_path / "repo"
    adapter_lines = []
    if rules:
        adapter_lines.append("skill_ergonomics_gate_rules:")
        for rule in rules:
            adapter_lines.append(f"  - {rule}")
    else:
        adapter_lines.append("skill_ergonomics_gate_rules: []")
    write_quality_adapter(repo, adapter_lines, repo_name="testrepo")
    write_text(repo / "skills" / "public" / "demo" / "references" / "note.md", "# Note\n")
    write_text(repo / "skills" / "public" / "steady" / "references" / "note.md", "# Note\n")
    write_skill(
        repo,
        [
            "Mode choice matters in this mode-heavy workflow.",
            "Another mode note keeps the mode pressure explicit.",
            "This option should probably be inference instead of an option.",
            "A second option mention keeps option pressure visible.",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
    )
    write_skill(
        repo,
        [
            "Use this when the repo needs a stable skill.",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
        skill_id="steady",
        description="Steady skill.",
        title="Steady",
    )
    return repo


def test_skill_ergonomics_gate_no_rules_passes(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=[])
    result = run_loaded_script_main(
        "validate_skill_ergonomics.py", VALIDATE, "--repo-root", str(repo)
    )
    assert result.returncode == 0, result.stderr
    payload = _emitted(result)
    assert payload["rules"] == []
    assert payload["violations"] == []
    assert payload["discovery_errors"] == []
    assert payload["warnings"][0]["warning_id"] == "skill_ergonomics_gate_rules_empty"
    assert payload["warnings"][0]["skill_count"] == 2

    # This run exits ZERO with no violations, so the payload has to say the gate was
    # never configured rather than reading as enforcement that passed.
    assert payload["verdict"] == "not-configured"
    assert (
        payload["verdict_detail"] == "No skill_ergonomics_gate_rules configured; nothing to check."
    )
    assert payload["warnings"][0]["attention"].startswith(
        "WARNING: skill_ergonomics_gate_rules is empty"
    )
    assert payload["warnings"][0]["attention"].endswith("(2 skill(s) present)")


def test_skill_ergonomics_gate_warns_when_empty_rules_have_broken_explicit_paths(
    tmp_path: Path,
) -> None:
    repo = _seed_repo(tmp_path, rules=[])
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - missing-skills",
                "skill_ergonomics_gate_rules: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 0
    assert payload["warnings"][0]["warning_id"] == "skill_ergonomics_requested_paths_empty"
    assert payload["warnings"][0]["requested_paths"] == ["missing-skills"]

    assert (
        "WARNING: skill_ergonomics_skill_paths is configured but resolved no non-vendored skills"
        in payload["warnings"][0]["attention"]
    )
    assert _verdict(payload)["verdict"] == "not-configured"


def test_skill_ergonomics_gate_fails_when_opted_in_rule_matches(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=["mode_option_pressure_terms"])
    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["rules"] == ["mode_option_pressure_terms"]
    assert payload["violations"][0]["rule"] == "mode_option_pressure_terms"
    assert payload["violations"][0]["skill_id"] == "demo"
    # The retired renderer printed `<rule>: <skill_path> (<heuristics>)` per violation;
    # each of those three facts is a violation key now.
    assert payload["violations"][0]["skill_path"] == "skills/public/demo/SKILL.md"
    assert payload["violations"][0]["heuristics"] == [
        "mode_pressure_terms_present",
        "option_pressure_terms_present",
    ]
    assert _verdict(payload) == {
        "verdict": "fail",
        "verdict_detail": "1 skill ergonomics violation(s).",
    }


def test_skill_ergonomics_gate_fails_on_issue_and_dated_incident_rules(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - issue_anchor_in_core",
            "  - dated_incident_in_core",
        ],
        repo_name="testrepo",
    )
    write_skill(
        repo,
        [
            "The 2026-05-28 routing miss is the reason this workflow owns next-step routing.",
            "Preserve the active guard from #123.",
        ],
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert [violation["rule"] for violation in payload["violations"]] == [
        "issue_anchor_in_core",
        "dated_incident_in_core",
    ]
    assert all(violation["skill_id"] == "demo" for violation in payload["violations"])


def test_skill_ergonomics_gate_fails_on_package_issue_anchor_rule_for_support_skill(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - portable_package_issue_anchor",
        ],
        repo_name="testrepo",
    )
    skill_path = write_skill(repo, [], package="support", description="Demo.")
    write_text(
        skill_path.parent / "references" / "history.md",
        "# History\n\nThis support package still names corca-ai/charness#123.\n",
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["violations"][0]["rule"] == "portable_package_issue_anchor"
    assert payload["violations"][0]["skill_id"] == "demo"
    assert payload["checked_skills"][0]["package_issue_anchor_count"] == 1


def test_skill_ergonomics_gate_fails_on_package_text_quality_rules(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - portable_package_dated_incident",
            "  - portable_package_host_surface_reference",
            "  - reference_discoverability_gap",
        ],
        repo_name="testrepo",
    )
    skill_path = write_skill(
        repo, ["Codex settings.json owns this host behavior."], description="Demo."
    )
    write_text(
        skill_path.parent / "references" / "hidden.md",
        "# Hidden\n\nA 2026-05-28 incident note belongs outside portable prose.\n",
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert [violation["rule"] for violation in payload["violations"]] == [
        "portable_package_dated_incident",
        "portable_package_host_surface_reference",
        "reference_discoverability_gap",
    ]
    assert all(violation["findings"] for violation in payload["violations"])


def test_skill_ergonomics_gate_keeps_existing_rules_public_only_for_support_skills(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - mode_option_pressure_terms",
        ],
        repo_name="testrepo",
    )
    write_skill(
        repo,
        [
            "Mode choice matters in this mode-heavy workflow.",
            "Another mode note keeps the mode pressure explicit.",
            "This option should probably be inference instead of an option.",
            "A second option mention keeps option pressure visible.",
        ],
        package="support",
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 0
    assert payload["checked_skills"][0]["skill_type"] == "support"
    assert payload["violations"] == []


def test_skill_ergonomics_gate_fails_on_invalid_rule_adapter_error(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=["typo_rule"])

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["adapter_errors"]
    assert "unknown rule `typo_rule`" in payload["adapter_errors"][0]
    assert payload["discovery_skipped_reason"] == "adapter_invalid"
    assert payload["checked_skills"] == []
    assert payload["violations"] == []

    # The renderer prefixed the adapter error with `quality adapter: `; the payload
    # states the same thing as a verdict beside the verbatim `adapter_errors` entry,
    # so an empty `violations` list here cannot be read as a clean run.
    assert _verdict(payload) == {
        "verdict": "adapter-invalid",
        "verdict_detail": "quality adapter did not load; nothing was judged.",
    }
    assert (
        "skill_ergonomics_gate_rules contains unknown rule `typo_rule`"
        in payload["adapter_errors"][0]
    )

    wrapper = run_loaded_script_main(
        "validate_skill_ergonomics.py", VALIDATE, "--repo-root", str(repo)
    )
    assert wrapper.returncode == 1
    wrapper_payload = _emitted(wrapper)
    assert "unknown rule `typo_rule`" in wrapper_payload["adapter_errors"][0]
    assert wrapper_payload["verdict"] == "adapter-invalid"


def test_skill_ergonomics_gate_ignores_mode_option_terms_inside_fences(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - mode_option_pressure_terms",
        ],
        repo_name="testrepo",
    )
    skill_path = write_skill(
        repo,
        [
            "## Bootstrap",
            "",
            "```bash",
            "echo mode option mode option",
            "```",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
    )
    write_text(skill_path.parent / "references" / "note.md", "# Note\n")
    payload = _evaluate(repo)
    assert _returncode(payload) == 0
    assert payload["violations"] == []
    # Rules ran and found nothing, which the payload must distinguish from the
    # exit-zero `not-configured` state that also carries an empty `violations` list.
    assert _verdict(payload) == {
        "verdict": "pass",
        "verdict_detail": "Skill ergonomics gate passed for rules: mode_option_pressure_terms",
    }


def test_skill_ergonomics_gate_rejects_removed_json_flag(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=[])
    result = run_loaded_script_main(
        "validate_skill_ergonomics.py", VALIDATE, "--repo-root", str(repo), "--json"
    )
    assert result.returncode == 2
    assert "--json" in result.stderr


def test_skill_ergonomics_gate_fails_when_rules_check_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert "no skills were checked" in payload["discovery_errors"][0]["message"]

    wrapper = run_loaded_script_main(
        "validate_skill_ergonomics.py", VALIDATE, "--repo-root", str(repo)
    )
    assert wrapper.returncode == 1
    wrapper_payload = _emitted(wrapper)
    # The renderer printed `skill discovery: <message> <skill_path>`; the payload keeps
    # each discovery error verbatim and names the state the whole run is in.
    assert wrapper_payload["verdict"] == "discovery-failed"
    assert "no skills were checked" in wrapper_payload["discovery_errors"][0]["message"]


def test_skill_ergonomics_gate_discovers_direct_skill_layout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\nA compact skill body.\n",
        encoding="utf-8",
    )
    payload = _evaluate(repo)
    assert _returncode(payload) == 0
    assert payload["checked_skills"][0]["skill_path"] == "skills/demo/SKILL.md"
    assert payload["discovery_errors"] == []


def test_skill_ergonomics_gate_reads_consumer_declared_skill_path(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    skill = repo / "src" / "skills" / "demo" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: demo\n---\n\n# Demo\n\nA compact skill body.\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\n"
        "skill_ergonomics_skill_paths:\n  - src/skills\n"
        "skill_ergonomics_gate_rules:\n  - long_core\n",
        encoding="utf-8",
    )

    payload = _evaluate(repo)

    assert _returncode(payload) == 0
    assert [item["skill_path"] for item in payload["checked_skills"]] == [
        "src/skills/demo/SKILL.md"
    ]
    assert payload["discovery_errors"] == []


def test_skill_ergonomics_gate_skips_runtime_install_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "packages" / "official-skills" / "acme-native" / "skills" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - packages/official-skills/acme-native/skills",
                "skill_ergonomics_runtime_install_skill_paths:",
                "  - packages/official-skills/acme-native/skills",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Runtime-install demo."',
                "---",
                "",
                "# Demo",
                "",
                "Mode choice matters in this mode-heavy workflow.",
                "Another mode note keeps the mode pressure explicit.",
                "This option should probably be inference instead of an option.",
                "A second option mention keeps option pressure visible.",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    payload = _evaluate(repo)
    assert _returncode(payload) == 0
    assert payload["violations"] == []
    assert payload["checked_skills"][0]["skill_type"] == "runtime_install"


def test_skill_ergonomics_gate_skips_vendored_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    own = repo / "skills" / "public" / "demo"
    vendored = repo / "packages" / "official-skills" / "charness-public" / "skills" / "vendored"
    own.mkdir(parents=True)
    vendored.mkdir(parents=True)
    (own / "references").mkdir()
    (own / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "vendored_paths:",
                "  - packages/official-skills/charness-public",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    body_lines = [
        "---",
        "name: bad",
        'description: "Vendored bad skill."',
        "---",
        "",
        "# Bad",
        "",
        "Mode choice matters in this mode-heavy workflow.",
        "Another mode note keeps the mode pressure explicit.",
        "This option should probably be inference instead of an option.",
        "A second option mention keeps option pressure visible.",
    ]
    (vendored / "SKILL.md").write_text("\n".join(body_lines) + "\n", encoding="utf-8")
    (own / "SKILL.md").write_text(
        '---\nname: demo\ndescription: "clean."\n---\n\n# Demo\n',
        encoding="utf-8",
    )
    payload = _evaluate(repo)
    assert _returncode(payload) == 0
    assert payload["violations"] == []
    paths = [skill["skill_path"] for skill in payload["checked_skills"]]
    assert paths == ["skills/public/demo/SKILL.md"]


def test_skill_ergonomics_gate_fails_when_opted_in_progressive_disclosure_risk_matches(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - progressive_disclosure_risk",
        ],
        repo_name="testrepo",
    )
    filler = [f"filler line {index}" for index in range(90)]
    write_skill(
        repo,
        [*filler, "", "## References", ""],
    )
    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["rules"] == ["progressive_disclosure_risk"]
    assert payload["violations"][0]["rule"] == "progressive_disclosure_risk"


def test_skill_ergonomics_gate_fails_when_opted_in_long_core_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - long_core",
        ],
        repo_name="testrepo",
    )
    filler = [f"filler line {index}" for index in range(170)]
    skill_path = write_skill(
        repo,
        [*filler, "", "## References", "", "- `references/note.md`"],
    )
    write_text(skill_path.parent / "references" / "note.md", "# Note\n")

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["violations"][0]["rule"] == "long_core"


def test_skill_ergonomics_gate_fails_when_opted_in_code_fence_rule_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - code_fence_without_helper_script",
        ],
        repo_name="testrepo",
    )
    write_skill(
        repo,
        [
            "## Bootstrap",
            "",
            "```bash",
            "echo first",
            "```",
            "",
            "```bash",
            "echo second",
            "```",
            "",
            "```bash",
            "echo third",
            "```",
        ],
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["violations"][0]["rule"] == "code_fence_without_helper_script"


def test_skill_ergonomics_gate_fails_when_opted_in_portable_helper_rule_matches(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - portable_helper_path_ambiguity",
        ],
        repo_name="testrepo",
    )
    skill_path = write_skill(
        repo,
        [
            "Use `scripts/helper.py` before stopping.",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
    )
    write_text(skill_path.parent / "references" / "note.md", "# Note\n")

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["violations"][0]["rule"] == "portable_helper_path_ambiguity"


def test_skill_ergonomics_gate_fails_when_opted_in_argparse_missing_help_rule_matches(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - argparse_missing_help",
        ],
        repo_name="testrepo",
    )
    skill_path = write_skill(repo, [], description="Demo.")
    scripts_dir = skill_path.parent / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run_demo.py").write_text(
        "\n".join(
            [
                "import argparse",
                "",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--workspace')",
                "parser.add_argument('--verbose', help='Print extra diagnostics.')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 1
    assert payload["violations"][0]["rule"] == "argparse_missing_help"
    assert (
        payload["violations"][0]["findings"][0]["path"] == "skills/public/demo/scripts/run_demo.py"
    )
    assert payload["checked_skills"][0]["argparse_missing_help_count"] == 1


def test_skill_ergonomics_gate_passes_argparse_missing_help_rule_when_all_args_documented(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - argparse_missing_help",
        ],
        repo_name="testrepo",
    )
    skill_path = write_skill(repo, [], description="Demo.")
    scripts_dir = skill_path.parent / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run_demo.py").write_text(
        "\n".join(
            [
                "import argparse",
                "",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument(",
                "    '--workspace',",
                "    help='Workspace id the run targets.',",
                ")",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = _evaluate(repo)
    assert _returncode(payload) == 0
    assert payload["violations"] == []

from __future__ import annotations

import importlib
from pathlib import Path

gate = importlib.import_module("tools.check_skill_bootstrap_vars")


def _skill(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "SKILL.md"
    path.write_text("# Demo\n\n## Bootstrap\n\n" + body, encoding="utf-8")
    return path


def test_exported_skill_dir_example_is_allowed(tmp_path: Path) -> None:
    reference = tmp_path / "bootstrap-resolution.md"
    reference.write_text(
        '```bash\nexport SKILL_DIR=/path/to/skill\npython3 "$SKILL_DIR/scripts/check.py"\n```\n',
        encoding="utf-8",
    )

    assert gate.check_canonical_reference(reference) == []


def test_plain_skill_dir_assignment_is_rejected(tmp_path: Path) -> None:
    reference = tmp_path / "bootstrap-resolution.md"
    reference.write_text("```bash\nSKILL_DIR=/path/to/skill\n```\n", encoding="utf-8")

    failures = gate.check_canonical_reference(reference)

    assert failures
    assert "without export" in failures[0]


def test_environment_prefix_skill_dir_assignment_is_rejected(tmp_path: Path) -> None:
    reference = tmp_path / "bootstrap-resolution.md"
    reference.write_text(
        '```bash\nSKILL_DIR=/path/to/skill python3 "$SKILL_DIR/scripts/check.py"\n```\n',
        encoding="utf-8",
    )

    assert gate.check_canonical_reference(reference)


def test_skill_canonical_var_still_requires_reference_citation(tmp_path: Path) -> None:
    skill = _skill(tmp_path, '```bash\npython3 "$SKILL_DIR/scripts/check.py"\n```\n')

    failures = gate.check_file(skill)

    assert failures == [
        "uses `$SKILL_DIR` in `## Bootstrap` shell block but does not cite "
        "`shared/references/bootstrap-resolution.md`"
    ]


def test_skill_environment_prefix_assignment_is_rejected_even_with_citation(tmp_path: Path) -> None:
    skill = _skill(
        tmp_path,
        "See `skills/shared/references/bootstrap-resolution.md`.\n\n"
        '```bash\nSKILL_DIR=/path/to/skill python3 "$SKILL_DIR/scripts/check.py"\n```\n',
    )

    failures = gate.check_file(skill)

    assert failures and "without export" in failures[0]


def test_skill_exported_assignment_is_allowed_with_citation(tmp_path: Path) -> None:
    skill = _skill(
        tmp_path,
        "See `skills/shared/references/bootstrap-resolution.md`.\n\n"
        '```bash\nexport SKILL_DIR=/path/to/skill\npython3 "$SKILL_DIR/scripts/check.py"\n```\n',
    )

    assert gate.check_file(skill) == []


def test_unknown_var_still_requires_inline_assignment(tmp_path: Path) -> None:
    skill = _skill(tmp_path, '```bash\npython3 "$CUSTOM_DIR/scripts/check.py"\n```\n')

    failures = gate.check_file(skill)

    assert failures and "CUSTOM_DIR" in failures[0]


def test_non_shell_fence_is_ignored_and_main_reports_reference_failure(
    tmp_path: Path, capsys
) -> None:
    reference = tmp_path / "bootstrap-resolution.md"
    reference.write_text(
        "```text\nSKILL_DIR=/path\n```\n```bash\nSKILL_DIR=/path\n```\n", encoding="utf-8"
    )
    assert gate.check_canonical_reference(reference) == [
        f"{reference}: shell example line 1 assigns SKILL_DIR without export; "
        "export it in a separate command before expanding $SKILL_DIR"
    ]
    canonical = tmp_path / "skills" / "shared" / "references" / "bootstrap-resolution.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text(reference.read_text(encoding="utf-8"), encoding="utf-8")

    assert gate.main(["--repo-root", str(tmp_path)]) == 1
    assert "without export" in capsys.readouterr().err


def test_main_validates_reference_when_present(tmp_path: Path, capsys) -> None:
    canonical = tmp_path / "skills" / "shared" / "references" / "bootstrap-resolution.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("```bash\nexport SKILL_DIR=/path\n```\n", encoding="utf-8")
    # A SKILL.md has to exist for the run to have a scope at all: the zero-target
    # case is a refusal, pinned in test_empty_scope_refusals.py.
    skill = tmp_path / "skills" / "public" / "demo" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "# Demo\n\n## Bootstrap\n\n```bash\nexport SKILL_DIR=/path\n```\n", encoding="utf-8"
    )

    assert gate.main(["--repo-root", str(tmp_path)]) == 0
    assert "Validated" in capsys.readouterr().out

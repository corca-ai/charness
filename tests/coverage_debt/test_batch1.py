"""Behaviour pins for repo commands whose failure and degradation arms shipped unproven.

Every test here names a behaviour an operator depends on and fails when that
behaviour breaks, not merely when a line stops executing:

* The skill scripts' bootstrap loaders must refuse with a NAMED ImportError when
  they run from a tree that owns no charness runtime, instead of dying later on a
  `NameError` that reads as a charness bug.
* The scaffolds' refusal arms must refuse rather than overwrite.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.core import scaffold_artifact_lib
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]

CLASSIFY_T_SIGNAL = load_script_module(
    "classify_t_signal_batch1", ROOT / "scripts" / "gates_support" / "classify_t_signal.py"
)
COLLECT_COMMITS = load_script_module(
    "collect_commits_batch1", ROOT / "skills/public/announcement/scripts/collect_commits.py"
)
# --------------------------------------------------------------------------
# scripts/core/scaffold_artifact_lib.py
# --------------------------------------------------------------------------


def test_a_records_family_refuses_when_every_dated_path_it_derives_is_taken(tmp_path: Path) -> None:
    """A scaffold writes a TEMPLATE, so resolving onto an existing record destroys it.

    Two default-titled critiques on one day already resolved to one file and the
    second destroyed the first while the payload reported `match`. The
    distinguisher tail buys three more names; once those are gone the only safe
    answer is a refusal that names every path tried and the remedy, so the author
    can pick a title instead of losing a record.
    """
    for name in (
        "2026-08-16-session.md",
        *(f"2026-08-16-session-{tail}.md" for tail in ("2", "3", "4")),
    ):
        (tmp_path / name).write_text("existing record\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        scaffold_artifact_lib.subject_scoped_record_payload(
            tmp_path,
            output_dir=".",
            date_text="2026-08-16",
            title="Session",
            record_slug="session",
            template="# Session\n",
            validator_command_for=lambda path: f"validate {path}",
            remedy="Pass --title to name this record differently.",
        )

    message = str(excinfo.value)
    assert "./2026-08-16-session.md" in message
    assert "./2026-08-16-session-4.md" in message
    assert "Pass --title" in message


def test_a_records_family_takes_the_first_free_distinguisher(tmp_path: Path) -> None:
    """The refusal above is only honest if the non-refusing arm actually routes.

    A scaffold that refused as soon as the first path was taken would make the
    same-day second record impossible; one that overwrote would lose the first.
    """
    (tmp_path / "2026-08-16-session.md").write_text("existing record\n", encoding="utf-8")

    payload = scaffold_artifact_lib.subject_scoped_record_payload(
        tmp_path,
        output_dir=".",
        date_text="2026-08-16",
        title="Session",
        record_slug="session",
        template="# Session\n",
        validator_command_for=lambda path: f"validate {path}",
        remedy="Pass --title to name this record differently.",
    )

    assert payload["write_artifact_path"] == "./2026-08-16-session-2.md"


def test_the_scaffold_library_names_the_helper_it_could_not_find(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The library is loaded by file path with no package context.

    Dropped into a tree that owns no `scripts/` directory it must say WHICH helper
    is missing at import time. The alternative -- binding `emit_yaml` to nothing --
    surfaces as a `NameError` deep inside a scaffold run and reads as a charness
    bug rather than as a broken install.
    """
    monkeypatch.setattr(
        scaffold_artifact_lib, "__file__", str(tmp_path / "scaffold_artifact_lib.py")
    )

    with pytest.raises(ImportError, match=r"scripts/yaml_output\.py not found"):
        scaffold_artifact_lib._load_repo_helper("yaml_output.py")


# --------------------------------------------------------------------------
# skill runtime bootstrap loaders
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module",
    [
        pytest.param(COLLECT_COMMITS, id="announcement-collect-commits"),
    ],
)
def test_a_skill_script_outside_a_charness_tree_names_the_missing_bootstrap(
    module: object, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skill scripts get copied out of the tree; that must fail loudly at load.

    Both scripts bind `emit_yaml` from the bootstrap at import time. Without the
    explicit refusal the ancestor walk simply returns `None` and the failure
    surfaces much later as an `AttributeError` on `None`, at which point the
    operator is debugging the skill instead of their install.
    """
    monkeypatch.setattr(module, "__file__", str(tmp_path / "script.py"))

    with pytest.raises(ImportError, match=r"skill_runtime_bootstrap\.py not found"):
        module._load_skill_runtime_bootstrap()


# --------------------------------------------------------------------------
# scripts/gates_support/classify_t_signal.py
# --------------------------------------------------------------------------


def test_the_t_signal_cli_prints_a_classification_and_exits_zero_without_git(
    tmp_path: Path,
) -> None:
    """This runs inside closeout, where an exit code is a gate result.

    A tree with no git history cannot be classified, and the honest answer is a
    printed `diff_unavailable` with a zero exit -- not a crash, and not silence.
    A caller parsing stdout must always get a payload with the same keys.
    """
    result = run_loaded_script_main(
        "classify_t_signal.py", CLASSIFY_T_SIGNAL, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["t_status"] == "none"
    assert payload["skipped_reason"] == "diff_unavailable"


# --------------------------------------------------------------------------
# scripts/issue/record_rca_event.py
# --------------------------------------------------------------------------


def test_the_rca_recorder_binds_packaged_owners_when_loaded_by_path() -> None:
    """A by-path load binds the packaged ledger library and live YAML helpers.

    The module's historical flat fallback is removed: the repo bootstrap is
    the single owner of repo-root insertion, so a by-path load resolves the
    packaged imports. A load that bound one name and dropped another would
    import cleanly and then fail on the first receipt it tried to render, so
    all three are asserted -- including the packaged identity of the ledger
    library (no flat `rca_ledger_lib` split).
    """
    module = load_script_module(
        "record_rca_event_by_path", ROOT / "scripts" / "issue" / "record_rca_event.py"
    )

    assert module.lib.__name__ == "scripts.issue.rca_ledger_lib"
    assert module.render_yaml({"converted": True}).strip() == "converted: true"
    assert callable(module.emit_yaml)
    assert module.lib.resolve_ledger_path(ROOT, None) == ROOT / module.lib.LEDGER_PATH

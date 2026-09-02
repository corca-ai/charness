"""Behaviour pins for repo commands whose failure and degradation arms shipped unproven.

Every test here names a behaviour an operator depends on and fails when that
behaviour breaks, not merely when a line stops executing:

* The skill scripts' bootstrap loaders must refuse with a NAMED ImportError when
  they run from a tree that owns no charness runtime, instead of dying later on a
  `NameError` that reads as a charness bug.
* The scaffolds' refusal arms must refuse rather than overwrite.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from scripts.core import scaffold_artifact_lib
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]

CLASSIFY_T_SIGNAL = load_script_module("classify_t_signal_batch1", ROOT / "scripts" / "gates_support" / "classify_t_signal.py")
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
    for name in ("2026-08-16-session.md", *(f"2026-08-16-session-{tail}.md" for tail in ("2", "3", "4"))):
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
    monkeypatch.setattr(scaffold_artifact_lib, "__file__", str(tmp_path / "scaffold_artifact_lib.py"))

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


def test_the_t_signal_cli_prints_a_classification_and_exits_zero_without_git(tmp_path: Path) -> None:
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


class _BlockScriptsPackage:
    """Makes `scripts.*` unimportable for the duration of one test, deterministically."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "scripts" or fullname.startswith("scripts."):
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def test_the_rca_recorder_loads_when_run_as_a_plain_script(monkeypatch: pytest.MonkeyPatch) -> None:
    """`python3 scripts/issue/record_rca_event.py` puts `scripts/` on the path, not the repo root.

    In that layout `from scripts import ...` cannot resolve, and the fallback arm
    is the ONLY thing that binds the ledger library and both YAML helpers. A
    fallback that bound one name and dropped another would import cleanly and then
    fail on the first receipt it tried to render, so all three are asserted.
    """
    # A meta-path finder, not a `sys.path` filter. Filtering the path leaves whether
    # `scripts` is reachable dependent on what other tests have already imported, so
    # this test took the try arm in one run and the fallback in another -- and the
    # fallback arm it exists to cover was not reliably exercised at all. A finder that
    # refuses the name outright does not depend on any of that.
    monkeypatch.setattr(sys, "meta_path", [_BlockScriptsPackage()] + sys.meta_path)
    for name in [name for name in sys.modules if name == "scripts" or name.startswith("scripts.")]:
        monkeypatch.delitem(sys.modules, name)
    monkeypatch.syspath_prepend(str(ROOT / "scripts" / "issue"))

    before = set(sys.modules)
    try:
        module = load_script_module(
            "record_rca_event_no_package", ROOT / "scripts" / "issue" / "record_rca_event.py"
        )

        # What THIS module bound, not whether `scripts` happens to be importable in
        # this interpreter. The global probe (`pytest.raises(ImportError)` around
        # `import scripts.issue.rca_ledger_lib`) passed in isolation and failed in the full
        # suite: whether some other test has left the package reachable is not a fact
        # about the layout under test, and asserting it made a correct fallback red.
        # `lib.__name__` is the discriminator: the try arm binds `scripts.issue.rca_ledger_lib`
        # and the fallback binds the bare sibling. `render_yaml.__module__` is NOT usable
        # here -- the repo's bootstrap aliases the two module names, so the same function
        # object carries `scripts.yaml_output` either way.
        assert module.lib.__name__ == "rca_ledger_lib"
        assert module.render_yaml({"converted": True}).strip() == "converted: true"
        assert callable(module.emit_yaml)
        assert module.lib.resolve_ledger_path(ROOT, None) == ROOT / module.lib.LEDGER_PATH
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]

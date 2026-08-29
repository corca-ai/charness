"""What an integration manifest DECLARES is not what the control plane DERIVES.

`integrations/tools/*.json` is read by two functions, and neither reads the field
you think it reads:

* `install_provenance_lib.detect_binary_name` takes
  `shlex.split(checks.detect.commands[0])[0]` and reports it to the operator as
  `provenance.binary_name`.
* `install_provenance_lib.package_manager_update_action` turns
  `package_managers.<mgr>.package_name` into a REGISTRY install-by-name
  (`cargo install <name> --force`, `npm install -g <name>@latest`,
  `go install <name>@latest`) and offers it as the tool's update path.

Every other rule about these manifests is checked against the field as authored.
These two are checked against the value that actually reaches a machine or an
operator, because both defects below were authored as correct-looking fields:

* A `detect` command written `PATH="${CARGO_HOME:-$HOME/.cargo}/bin:$PATH" repograph --help`
  made `charness tool doctor repograph` report
  `binary_name: PATH=${CARGO_HOME:-$HOME/.cargo}/bin:$PATH`. The field was
  reasonable; the derivation was not. Found by running the doctor, not by
  reading the manifest.
* `repograph` is built from a local crate with `cargo install --path .` and is
  NOT published to crates.io. Declaring `package_managers.cargo.package_name`
  therefore derived `cargo install repograph --force`, which resolves against
  crates.io and could reach an unrelated package of the same name. The manifest
  carried a note saying it must not be installed by name -- nothing reads the
  note, and the derivation reads the block.

Why this is a property and not a list. This repo has a good family of gates for
"a verdict that outlived the check behind it"
(`test_empty_scope_refusals.py`, `test_a_declaration_is_not_its_own_corroboration.py`,
`test_a_refused_verdict_states_its_refusal.py`), and those came from a numbered
sweep -- rows S2, S9, S10, S23. A sweep discharges a CLASS by repairing the
instances a snapshot contained, and both defects above are new instances of that
same class, authored after the sweep, in a file the sweep never had to consider.
So these tests take every manifest in the directory rather than the ones
observed broken: enumeration is O(instances) and decays as the corpus grows,
while a property holds for the manifest nobody has written yet.
"""

from __future__ import annotations

import json

import pytest

from .support import ROOT, _load_script_module

PROVENANCE = _load_script_module(
    "install_provenance_lib_under_test",
    ROOT / "scripts" / "install_provenance_lib.py",
)

MANIFEST_DIR = ROOT / "integrations" / "tools"
NON_MANIFESTS = {"manifest.schema.json", "dependencies.json", "dependencies.schema.json"}

#: `cargo install --path`, `pip install -e`, and friends all install the artifact
#: sitting at a local path. The registry name is a DIFFERENT artifact that merely
#: shares a spelling.
LOCAL_SOURCE_INSTALL_MARKERS = ("--path", "install -e")


def _manifests() -> list[tuple[str, dict]]:
    found = [
        (path.name, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(MANIFEST_DIR.glob("*.json"))
        if path.name not in NON_MANIFESTS
    ]
    # A property gate over an empty directory is the vacuous pass this family
    # exists to refuse (`test_empty_scope_refusals.py`).
    assert found, f"no integration manifests found under {MANIFEST_DIR}"
    return found


def _install_commands(manifest: dict) -> str:
    lifecycle = manifest.get("lifecycle") or {}
    install = lifecycle.get("install") or {}
    return " ".join(command for command in install.get("commands", []) if isinstance(command, str))


@pytest.mark.parametrize("name,manifest", _manifests(), ids=lambda value: value if isinstance(value, str) else "")
def test_the_derived_binary_name_is_a_bare_executable(name: str, manifest: dict) -> None:
    """`provenance.binary_name` is operator-facing and is `shlex.split(...)[0]`.

    Anything that shifts the first token -- an env assignment, a `sudo`, a flag,
    a shell builtin -- silently renames the tool in the doctor payload and makes
    `shutil.which(binary_name)` look for something that does not exist, so the
    tool reports `missing` on a machine where it is installed.
    """
    derived = PROVENANCE.detect_binary_name(manifest)

    assert derived is not None, f"{name}: checks.detect.commands[0] yields no binary name"
    assert "=" not in derived, (
        f"{name}: derived binary_name is {derived!r} -- an env assignment leads "
        "checks.detect.commands[0]. Put the bare binary first and express any "
        "PATH fallback after it (`repograph --help || \"$HOME/.cargo/bin/repograph\" --help`)."
    )
    assert not derived.startswith("-"), f"{name}: derived binary_name {derived!r} is a flag"
    assert derived.split() == [derived], f"{name}: derived binary_name {derived!r} is not one token"


@pytest.mark.parametrize("name,manifest", _manifests(), ids=lambda value: value if isinstance(value, str) else "")
def test_a_local_source_install_does_not_derive_a_registry_install(name: str, manifest: dict) -> None:
    """Install-from-a-path and install-by-name produce DIFFERENT artifacts.

    When the install builds whatever sits at a local path, the registry entry of
    the same name is not the same software -- it may not exist, or worse, may be
    someone else's package. `package_manager_update_action` cannot tell the
    difference, so the manifest must not offer it the chance.
    """
    if not any(marker in _install_commands(manifest) for marker in LOCAL_SOURCE_INSTALL_MARKERS):
        return
    declared = manifest.get("package_managers") or {}

    assert not declared, (
        f"{name}: installs from a local source path but declares package_managers "
        f"{sorted(declared)}. `package_manager_update_action` would derive a "
        "registry install-by-name for a package this manifest never publishes. "
        "Drop the block and let lifecycle.update own the rebuild."
    )


@pytest.mark.parametrize("name,manifest", _manifests(), ids=lambda value: value if isinstance(value, str) else "")
def test_every_declared_package_manager_actually_derives_an_update(name: str, manifest: dict) -> None:
    """A declared manager that derives nothing is decoration.

    `package_manager_update_action` returns None for an unsupported manager or a
    missing `package_name`, and the caller then reports the tool as having no
    update path -- while the manifest reads as though it has one.
    """
    for manager in manifest.get("package_managers") or {}:
        action = PROVENANCE.package_manager_update_action(
            manifest, {"status": "detected", "install_method": manager}
        )

        assert action is not None, (
            f"{name}: package_managers.{manager} derives no update action. Either "
            "give it a `package_name` this manager understands, or remove it so "
            "the manifest stops implying an update path that does not exist."
        )
        assert action["commands"], f"{name}: package_managers.{manager} derives an empty command list"


# --- negative controls -------------------------------------------------------
#
# A gate nobody has watched fail is not known to be a gate. Each property above
# is green over the current directory, and would stay green if its assertion
# were deleted -- so each one carries a fixture that reinjects the exact defect
# it was written for. These are not extra coverage; they are the difference
# between "the manifests are clean" and "the check would notice if they were
# not."


def test_the_binary_name_property_catches_an_env_prefix() -> None:
    manifest = {
        "tool_id": "fixture",
        "checks": {"detect": {"commands": ['PATH="$HOME/.cargo/bin:$PATH" repograph --help']}},
        "lifecycle": {"install": {"commands": []}},
    }

    with pytest.raises(AssertionError, match="env assignment"):
        test_the_derived_binary_name_is_a_bare_executable("fixture.json", manifest)


def test_the_local_source_property_catches_a_registry_declaration() -> None:
    manifest = {
        "tool_id": "fixture",
        "checks": {"detect": {"commands": ["repograph --help"]}},
        "lifecycle": {"install": {"commands": ["cd crate && cargo install --path . --locked"]}},
        "package_managers": {"cargo": {"package_name": "repograph"}},
    }

    with pytest.raises(AssertionError, match="registry install-by-name"):
        test_a_local_source_install_does_not_derive_a_registry_install("fixture.json", manifest)


def test_the_derivation_property_catches_a_decorative_manager() -> None:
    manifest = {
        "tool_id": "fixture",
        "checks": {"detect": {"commands": ["fixture --help"]}},
        "lifecycle": {"install": {"commands": ["brew install fixture"]}},
        "package_managers": {"cargo": {"notes": ["declared with no package_name"]}},
    }

    with pytest.raises(AssertionError, match="derives no update action"):
        test_every_declared_package_manager_actually_derives_an_update("fixture.json", manifest)


def test_a_clean_manifest_passes_all_three_properties() -> None:
    """The other half of a negative control: the properties must not fire on a
    manifest that is actually correct, or they would be refusals rather than checks."""
    manifest = {
        "tool_id": "fixture",
        "checks": {"detect": {"commands": ["fixture --version"]}},
        "lifecycle": {"install": {"commands": ["cargo install fixture"]}},
        "package_managers": {"cargo": {"package_name": "fixture"}},
    }

    test_the_derived_binary_name_is_a_bare_executable("fixture.json", manifest)
    test_a_local_source_install_does_not_derive_a_registry_install("fixture.json", manifest)
    test_every_declared_package_manager_actually_derives_an_update("fixture.json", manifest)

"""The repo-wide standalone-import check, proven against the REAL cycle.

A guard that only passes on a healthy tree has established nothing. The measured
instance is `scripts/quality_policy_merge.py`, extracted from
`quality_policy_defaults.py` on 2026-08-06 with a module-level import in both
directions: a cycle that resolves in exactly ONE order, invisible to 4979 passing
tests because every existing importer reached `defaults` first.

That pre-fix version was never committed — the cycle was found by a bounded reviewer
and fixed inside the same commit that created the file — so `_reconstruct_the_cycle`
rebuilds it the one way the defect is defined: hoist the two function-level sibling
imports back to module scope. The reconstruction is verified to produce the exact
`ImportError: ... partially initialized module` from the issue, so it is the defect and
not a lookalike.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import native_gate_lib
from scripts.plugin_export import packaging_lib
from tests.quality_gates.git_fixture_support import init_git_repo
from tests.repo_copy import clone_seeded_charness_repo

ROOT = Path(__file__).resolve().parents[2]
MERGE_REL = "scripts/quality_policy_merge.py"
pytestmark = pytest.mark.boundary_contract(
    reason="prove standalone-import checks and their module-order probe run in a fresh interpreter"
)


def _reconstruct_the_cycle(source: str) -> str:
    """Hoist the sibling imports out of the functions — the pre-fix shape, exactly."""
    names = sorted(set(re.findall(r"from scripts\.quality_policy_defaults import (\w+)", source)))
    assert names, "the function-level sibling imports are what break the cycle; they are gone"
    hoisted = re.sub(r"[ \t]+from scripts\.quality_policy_defaults import \w+\n", "", source)
    return hoisted.replace(
        "from __future__ import annotations",
        "from __future__ import annotations\n\nfrom scripts.quality_policy_defaults import "
        + ", ".join(names),
        1,
    )


@pytest.fixture
def real_native_core(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Use the real D1-resolved binary for runtime and inventory claims."""
    try:
        resolved = native_gate_lib.resolve_native_core(ROOT)
    except native_gate_lib.NativeGateError as exc:
        pytest.fail(f"native core unavailable through the D1 shim: {exc}")
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(resolved.path))
    return resolved.path


@pytest.fixture
def clean_repo(tmp_path: Path, seeded_charness_git_repo: Path, real_native_core: Path) -> Path:
    """An isolated copy of this repo. The whole package is copied, not just the module:
    the cycle exists only in relation to `quality_policy_defaults`'s re-export, so a
    module copied on its own would not reproduce it and a check that passed on that copy
    would prove nothing.

    Isolated rather than in-tree because mutating the real checkout lets an xdist worker
    observe a transiently broken module — `check_test_repo_copy_invariants` refuses it,
    and it was right to: the first cut of this file did exactly that.
    """
    return clone_seeded_charness_repo(tmp_path, seeded_charness_git_repo)


@pytest.fixture
def repo_with_the_real_cycle(clean_repo: Path) -> Path:
    """Reintroduce the defect in the isolated copy."""
    merge = clean_repo / MERGE_REL
    merge.write_text(_reconstruct_the_cycle(merge.read_text(encoding="utf-8")), encoding="utf-8")
    return clean_repo


def _load_check_module():
    import importlib.util

    check = ROOT / "scripts" / "gates" / "check_standalone_imports.py"
    spec = importlib.util.spec_from_file_location("check_standalone_imports", check)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def _run_check_at(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the REAL check against a throwaway package root."""
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "gates" / "check_standalone_imports.py"),
            "--repo-root",
            str(repo),
            *args,
        ],
        capture_output=True,
        text=True,
    )


def _run_check(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(repo / "scripts" / "gates" / "check_standalone_imports.py"),
            "--repo-root",
            str(repo),
            *args,
        ],
        capture_output=True,
        text=True,
    )


def _report(result: subprocess.CompletedProcess) -> dict:
    """The check's stdout is unconditionally YAML since the `--json` removal.

    Parsed rather than grepped: the emitter wraps long scalars, so `scope_note` — the
    field carrying the PARTIAL/denominator claim — is split across lines and a substring
    search over raw stdout silently stops matching.
    """
    payload = yaml.safe_load(result.stdout)
    assert isinstance(payload, dict), f"stdout was not a YAML mapping: {result.stdout[:400]!r}"
    return payload


def _native_standalone_report(repo: Path) -> dict:
    module = _load_check_module()
    try:
        return module.select_standalone_targets(repo, changed=None)
    except module.NativeGateError as exc:
        pytest.fail(f"native core unavailable through the D1 shim: {exc}")


def _tracked_python_paths(repo: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z", "--cached"],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    return {
        raw.decode()
        for raw in result.stdout.split(b"\0")
        if raw.endswith(b".py")
        and not raw.endswith(b"/__init__.py")
        and (repo / raw.decode()).is_file()
    }


def _export_plugin(tmp_path: Path) -> Path:
    plugin = tmp_path / "plugin"
    manifest = packaging_lib.load_manifest(ROOT, "charness")
    packaging_lib.export_plugin_tree(ROOT, plugin, manifest)
    init_git_repo(plugin)
    subprocess.run(["git", "add", "-A"], cwd=plugin, check=True, capture_output=True, text=True)
    return plugin


@pytest.mark.release_only
def test_the_reconstruction_really_is_the_issues_cycle(repo_with_the_real_cycle: Path) -> None:
    """Before asking whether the check catches it, prove the fixture reproduces the
    defect and not something that merely fails to import."""
    result = subprocess.run(
        [sys.executable, "-c", "import scripts.quality_policy_merge"],
        cwd=repo_with_the_real_cycle,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "partially initialized module 'scripts.quality_policy_merge'" in result.stderr
    assert "circular import" in result.stderr


@pytest.mark.release_only
def test_the_check_catches_the_real_cycle(repo_with_the_real_cycle: Path) -> None:
    """The acceptance criterion: it FAILS on the pre-fix module, not merely passes on a
    clean tree."""
    result = _run_check(repo_with_the_real_cycle)

    assert result.returncode == 1
    payload = _report(result)
    assert payload["verdict"] == "BLOCKED"
    # Membership, not equality: every module that reaches the cycling one fails through
    # the same cycle, so the collateral entries are the defect too. The claim is that
    # the module carrying the defect is named as a CYCLE, with the issue's own text.
    cycles = {item["path"]: item["detail"] for item in payload["cycles"]}
    assert "scripts/quality_policy_merge.py" in cycles, payload
    assert "partially initialized" in cycles["scripts/quality_policy_merge.py"]


@pytest.mark.release_only
def test_a_changed_scope_run_catches_the_cycle_in_the_module_it_was_given(
    repo_with_the_real_cycle: Path,
) -> None:
    """The pre-push lane is where this check will actually run, and the first cut FAILED
    here while passing the full sweep.

    Two load shapes exist in this repo and the check tries both, because a module built
    for direct execution raises a sibling `ModuleNotFoundError` when imported as a
    package member — a wrong-shape error, not a defect. But falling through to the
    `direct` shape after a CYCLE masks it: that shape loads the file as a top-level
    module under a different name, which is not the module the cycle runs through. So
    `--changed` on the one module carrying the defect reported `ok`. A cycle now stops
    the fallback.
    """
    result = _run_check(repo_with_the_real_cycle, "--changed", MERGE_REL)

    assert result.returncode == 1, result.stdout
    assert [item["path"] for item in _report(result)["cycles"]] == [
        "scripts/quality_policy_merge.py"
    ]


@pytest.mark.release_only
def test_a_partial_run_says_so_in_its_own_output(clean_repo: Path) -> None:
    """A partial run must never read as a whole-package verdict — this repo's own
    `partial` lesson, applied to the gate it produced. The scope travels WITH the
    verdict, not in a comment somewhere the reader has to go find."""
    partial = _run_check(clean_repo, "--changed", MERGE_REL)

    assert partial.returncode == 0, partial.stdout
    payload = _report(partial)
    assert payload["scope"] == "partial"
    assert payload["selection"] == "repograph standalone-targets v1"
    assert "PARTIAL: checked 1 of" in payload["scope_note"]
    assert "UNCHECKED, not proven clean" in payload["scope_note"]


@pytest.mark.slow_corpus
@pytest.mark.release_only
def test_the_clean_tree_passes_and_says_what_it_covered(clean_repo: Path) -> None:
    """The other half of the same rule: a FULL run states its denominator too, so `ok`
    is a claim about a number rather than an unqualified all-clear."""
    result = _run_check(clean_repo)

    assert result.returncode == 0, result.stdout
    payload = _report(result)
    assert payload["verdict"] == "ok"
    assert payload["selection"] == "repograph standalone-targets v1"
    assert re.search(r"checked all \d+ discovered module\(s\)", payload["scope_note"]), payload


@pytest.mark.release_only
def test_an_empty_changed_scope_says_nothing_was_checked(clean_repo: Path) -> None:
    """An empty scope that prints a bare `ok` is a green nobody earned.

    It does not BLOCK — a commit touching only non-module Python legitimately matches
    nothing — but it must say so, and name what matched nothing, so a caller passing
    paths in the wrong shape finds out here instead of reading a pass. This is also the
    regression pin for the resolution bug that produced it: `--changed` paths were
    resolved against the process CWD rather than `--repo-root`, so they matched by luck
    in the real checkout and matched NOTHING anywhere else.
    """
    result = _run_check(clean_repo, "--changed", "docs/index.md")

    assert result.returncode == 0
    payload = _report(result)
    assert "NOTHING WAS CHECKED" in payload["scope_note"]
    assert payload["unmatched_changed"] == ["docs/index.md"]


@pytest.mark.release_only
def test_changed_paths_resolve_against_the_repo_root_not_the_cwd(clean_repo: Path) -> None:
    """The same bug from the other side: a relative `--changed` path must name a module
    in the repo being CHECKED, whatever directory the process happens to start in."""
    result = subprocess.run(
        [
            sys.executable,
            str(clean_repo / "scripts" / "gates" / "check_standalone_imports.py"),
            "--repo-root",
            str(clean_repo),
            "--changed",
            MERGE_REL,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout
    assert _report(result)["checked"] == 1, result.stdout


def _mini_repo(root: Path, files: dict[str, str]) -> Path:
    """A Git-backed throwaway package for cycle shapes outside this repo."""
    from .repo_shapes import install_committed_repo

    payload = {"scripts/__init__.py": ""}
    payload.update({f"scripts/{name}": body for name, body in files.items()})
    return install_committed_repo(root, payload)


def test_a_cycle_a_module_turns_into_a_missing_sibling_is_still_caught(
    tmp_path: Path, real_native_core: Path
) -> None:
    """The shape fallback must not become a mask, and this is the input that made it one.

    This repo's dominant preamble is `try: from scripts import x / except ImportError:
    import x`. Under a real cycle the first arm raises `partially initialized`, the
    `except` swallows it, and the second arm fails with a plain missing-sibling
    `ModuleNotFoundError` — which is ALSO the legitimate wrong-shape signal the fallback
    exists for. Testing wrong-shape alone therefore let the `direct` shape clear it, and
    `direct` loads the file as a top-level module under a different name, through which
    the cycle does not run. CPython's exception chaining keeps the original text in the
    same stderr, so a cycle marker anywhere vetoes the fallback.
    """
    repo = _mini_repo(
        tmp_path,
        {
            "lib_x.py": "from scripts.entry_y import NAME\nVALUE = 'lib'\n",
            "entry_y.py": "try:\n    from scripts import lib_x as lib\nexcept ImportError:\n"
            "    import lib_x as lib\nNAME = 'entry'\n",
        },
    )

    result = _run_check_at(repo)

    assert result.returncode == 1, result.stdout
    assert [item["path"] for item in _report(result)["cycles"]], result.stdout


def test_a_module_that_imports_in_no_shape_blocks(tmp_path: Path, real_native_core: Path) -> None:
    """Splitting cycle from import-error is worth doing in the OUTPUT — a missing
    dependency has a different fix — but making only one half blocking left the other as
    a hole: the gate held the evidence that a changed module could not be imported at
    all, printed it as a note, and exited 0."""
    repo = _mini_repo(tmp_path, {"broken.py": "import a_dependency_that_is_not_installed\n"})

    result = _run_check_at(repo)

    assert result.returncode == 1, result.stdout
    payload = _report(result)
    assert payload["verdict"] == "BLOCKED"
    assert [item["path"] for item in payload["other_failures"]] == ["scripts/broken.py"]
    # The two classes must stay split in the OUTPUT: this is not a cycle, and nothing in
    # the payload may call it one (a missing dependency has a different fix).
    assert payload["cycles"] == [], "a missing dependency is not a cycle"
    assert "cycle_meaning" not in payload, "a missing dependency is not a cycle"
    assert "not a cycle" in payload["other_failure_meaning"]


def test_a_wrong_shape_sibling_error_still_falls_through(
    tmp_path: Path, real_native_core: Path
) -> None:
    """The false-positive control for the two tests above. Narrowing the fallback must
    not break the case it exists for: 35 healthy modules in this repo use the
    sibling-import preamble and fail the package shape by design."""
    repo = _mini_repo(
        tmp_path,
        {
            "helper.py": "VALUE = 'helper'\n",
            "entry.py": "import helper\nNAME = helper.VALUE\n",
        },
    )

    result = _run_check_at(repo)

    assert result.returncode == 0, result.stdout


def test_every_tracked_module_is_either_discovered_or_deliberately_excluded(
    real_native_core: Path,
) -> None:
    """The real native selection must cover every authoring-tree module."""
    tracked = _tracked_python_paths(ROOT)
    discovered = {target["path"] for target in _native_standalone_report(ROOT)["targets"]}
    excluded_prefixes = (
        "tests/",
        "plugins/",
        "docs/",
        "native/",
        "charness-artifacts/",
    )
    unreachable = sorted(
        name for name in tracked - discovered if not name.startswith(excluded_prefixes)
    )

    assert not unreachable, (
        "these tracked Python modules are not in the real native standalone-targets output "
        f"and have no recorded exclusion: {unreachable}"
    )


def test_the_exported_mirror_enumerates_its_own_modules(
    tmp_path: Path, real_native_core: Path
) -> None:
    """The real native selection must cover the shipped mirror layout too."""
    mirror = _export_plugin(tmp_path)
    tracked = _tracked_python_paths(mirror)
    discovered = {target["path"] for target in _native_standalone_report(mirror)["targets"]}

    assert not sorted(tracked - discovered), (
        "these tracked mirror modules are not in the real native standalone-targets output: "
        f"{sorted(tracked - discovered)}"
    )


def test_a_partial_run_names_unmatched_paths_even_when_something_matched(
    real_native_core: Path,
) -> None:
    """The case B5 actually repaired, and the one its first test could not reach.

    Both existing scope tests have zero unmatched or zero matched, so reverting the fix to
    "name unmatched only when NOTHING matched" left them green. The pre-push lane produces
    this shape routinely: a rename stages one path that resolves and one that does not, and
    the silent-about-the-other behaviour is exactly what B5 removed.
    """
    result = _run_check(ROOT, "--changed", MERGE_REL, "docs/index.md")

    payload = _report(result)
    assert "PARTIAL: checked 1 of" in payload["scope_note"]
    assert payload["unmatched_changed"] == ["docs/index.md"]


def test_native_report_detail_describes_unestablished_targets() -> None:
    module = _load_check_module()

    document = {
        "unestablished": [
            {"detail": "native inventory is stale"},
            {"detail": "one target has no command"},
            {"detail": 42},
            "not a target",
        ]
    }

    assert module._native_report_detail(document, "ignored stderr") == (
        "native inventory is stale; one target has no command"
    )
    assert module._native_report_detail({}, "  native failed  ") == "native failed"
    assert module._native_report_detail([], "") == "(no native diagnostic)"


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ([], "did not emit a JSON object"),
        ({"schema": "old"}, "unexpected schema: 'old'"),
        ({"schema": "repograph.standalone_targets.v1"}, "has no target list"),
        (
            {"schema": "repograph.standalone_targets.v1", "targets": [None]},
            "target 0 has no inventory-relative path",
        ),
        (
            {
                "schema": "repograph.standalone_targets.v1",
                "targets": [{"path": "scripts/a.py"}],
            },
            "target 'scripts/a.py' has no shape list",
        ),
        (
            {
                "schema": "repograph.standalone_targets.v1",
                "targets": [{"path": "scripts/a.py", "shapes": [None]}],
            },
            "target 'scripts/a.py' shape 0 has no command",
        ),
        (
            {
                "schema": "repograph.standalone_targets.v1",
                "targets": [],
                "scope": "unestablished",
                "unestablished": [{"detail": "selection is unavailable"}],
            },
            "reported an unestablished condition: selection is unavailable",
        ),
    ],
)
def test_invalid_native_selection_documents_are_refused(document: object, message: str) -> None:
    module = _load_check_module()

    with pytest.raises(module.NativeSelectionError, match=re.escape(message)):
        module._validate_selection_document(document)


def test_native_selection_refuses_unexecutable_binary(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_check_module()
    binary = tmp_path / "repograph"
    monkeypatch.setattr(
        module.native_gate_lib,
        "resolve_native_core",
        lambda repo: SimpleNamespace(path=binary),
    )

    def refuse_to_run(*args: object, **kwargs: object) -> None:
        raise OSError("permission denied")

    monkeypatch.setattr(module, "run_process", refuse_to_run)

    with pytest.raises(module.NativeSelectionError, match=r"could not execute.*permission denied"):
        module.select_standalone_targets(tmp_path, changed=None)


def test_native_selection_refuses_invalid_success_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_check_module()
    monkeypatch.setattr(
        module.native_gate_lib,
        "resolve_native_core",
        lambda repo: SimpleNamespace(path=tmp_path / "repograph"),
    )
    monkeypatch.setattr(
        module,
        "run_process",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "{not json}", ""),
    )

    with pytest.raises(module.NativeSelectionError, match="emitted invalid JSON"):
        module.select_standalone_targets(tmp_path, changed=None)


def test_native_selection_reports_native_failure_detail(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_check_module()
    monkeypatch.setattr(
        module.native_gate_lib,
        "resolve_native_core",
        lambda repo: SimpleNamespace(path=tmp_path / "repograph"),
    )
    monkeypatch.setattr(
        module,
        "run_process",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command,
            2,
            '{"unestablished":[{"detail":"inventory unavailable"}]}',
            "fallback stderr",
        ),
    )

    with pytest.raises(
        module.NativeSelectionError,
        match=r"exited 2 \(native condition\): inventory unavailable",
    ):
        module.select_standalone_targets(tmp_path, changed=None)


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (native_gate_lib.NativeGateError("repograph is unavailable"), "native gate unavailable"),
        (None, "selection failed for a human-readable reason"),
    ],
)
def test_main_reports_native_selection_failures(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: Exception | None,
    message: str,
) -> None:
    module = _load_check_module()
    if error is None:
        error = module.NativeSelectionError(message)
    monkeypatch.setattr(module, "run", lambda *args, **kwargs: (_ for _ in ()).throw(error))
    monkeypatch.setattr(sys, "argv", ["check_standalone_imports", "--repo-root", str(ROOT)])

    assert module.main() == 1
    assert message in capsys.readouterr().err

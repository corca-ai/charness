from __future__ import annotations

import importlib
import textwrap
from pathlib import Path

import yaml

from .support import run_script

shim_gate = importlib.import_module("scripts.check_bootstrap_shim_consistency")

SCRIPT = "scripts/check_bootstrap_shim_consistency.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
DRIFTED_SHIM = (FIXTURES / "drifted_skill_runtime_bootstrap.py.txt").read_text(encoding="utf-8")
HEADER = "import runpy\nfrom pathlib import Path\nfrom types import SimpleNamespace\n\n\n"


def _seed_repo(tmp_path: Path, *, drifted: bool) -> Path:
    repo = tmp_path / "repo"
    scripts_dir = repo / "skills" / "public" / "demo" / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "canonical_helper.py").write_text(
        HEADER + shim_gate.CANONICAL_SHIM + "\n", encoding="utf-8"
    )
    body = DRIFTED_SHIM if drifted else shim_gate.CANONICAL_SHIM + "\n"
    (scripts_dir / "second_helper.py").write_text(HEADER + body, encoding="utf-8")
    return repo


def test_reports_drifted_copy_and_exits_nonzero(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=True)
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "drift"
    assert payload["checked_files"] == 2
    assert payload["drifted"] == ["skills/public/demo/scripts/second_helper.py"]


def test_clean_tree_exits_zero(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    # `ok` alone is not the claim: the count is what says two copies were actually
    # compared, and `empty-scope` is the state a zero-comparison run reports instead.
    assert payload["status"] == "ok"
    assert payload["checked_files"] == 2


def test_fix_rewrites_to_canonical_and_round_trips(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=True)
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert fix_result.returncode == 0
    payload = yaml.safe_load(fix_result.stdout)
    assert payload["fixed"] == ["skills/public/demo/scripts/second_helper.py"]
    rewritten = (repo / "skills/public/demo/scripts/second_helper.py").read_text(encoding="utf-8")
    assert shim_gate.CANONICAL_SHIM in rewritten
    recheck = run_script(SCRIPT, "--repo-root", str(repo))
    assert recheck.returncode == 0


def test_nested_drifted_copy_is_reported_not_rewritten(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    nested = repo / "scripts" / "nested_holder.py"
    nested.parent.mkdir(parents=True)
    nested.write_text(
        HEADER + "def outer():\n" + textwrap.indent(DRIFTED_SHIM, "    "),
        encoding="utf-8",
    )
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert fix_result.returncode == 1
    payload = yaml.safe_load(fix_result.stdout)
    assert payload["unfixable"] == ["scripts/nested_holder.py"]
    assert textwrap.indent(DRIFTED_SHIM, "    ").rstrip() in nested.read_text(encoding="utf-8")


def test_fix_is_safe_with_form_feed_before_the_shim(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    target = repo / "skills" / "public" / "demo" / "scripts" / "second_helper.py"
    target.write_text(
        HEADER + 'PAGE_BREAK = "before\x0cafter"\nKEEP_ME = 1\n\n' + DRIFTED_SHIM,
        encoding="utf-8",
    )
    # splitlines-based splicing would treat the \x0c as a line break, shift
    # the window, and delete real statements while reporting success.
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert fix_result.returncode == 0
    rewritten = target.read_text(encoding="utf-8")
    assert "KEEP_ME = 1" in rewritten
    assert shim_gate.CANONICAL_SHIM in rewritten
    recheck = run_script(SCRIPT, "--repo-root", str(repo))
    assert recheck.returncode == 0


def test_fix_rewrites_two_module_level_shims_in_one_file(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    target = repo / "skills" / "public" / "demo" / "scripts" / "second_helper.py"
    target.write_text(HEADER + DRIFTED_SHIM + "\n\n" + DRIFTED_SHIM, encoding="utf-8")
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert fix_result.returncode == 0
    rewritten = target.read_text(encoding="utf-8")
    assert rewritten.count(shim_gate.CANONICAL_SHIM) == 2


def test_failure_message_names_the_deliberate_evolution_path(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=True)
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 1
    # The remedy used to be a stderr line; output is unconditionally YAML now, so a
    # drift verdict has to carry the deliberate-evolution path in the payload itself.
    remedies = yaml.safe_load(result.stdout)["remedies"]
    assert any("CANONICAL_SHIM" in remedy for remedy in remedies), remedies


def test_name_prefix_collision_is_not_scanned(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    holder = repo / "scripts" / "module_loader.py"
    holder.parent.mkdir(parents=True, exist_ok=True)
    holder.write_text(
        "def _load_skill_runtime_bootstrap_module():\n    return None\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["checked_files"] == 2


def test_syntax_error_file_is_not_scanned_and_does_not_crash(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    bad = repo / "scripts" / "broken_helper.py"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("def _load_skill_runtime_bootstrap(:\n    pass\n", encoding="utf-8")
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["checked_files"] == 2


def test_fix_with_residual_nested_drift_reports_unfixable_not_fixed(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    target = repo / "scripts" / "mixed_holder.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        HEADER + DRIFTED_SHIM + "\n\ndef outer():\n" + textwrap.indent(DRIFTED_SHIM, "    "),
        encoding="utf-8",
    )
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert fix_result.returncode == 1
    payload = yaml.safe_load(fix_result.stdout)
    assert payload["unfixable"] == ["scripts/mixed_holder.py"]
    assert payload["fixed"] == []
    rewritten = target.read_text(encoding="utf-8")
    assert shim_gate.CANONICAL_SHIM in rewritten


def test_normalized_setup_helper_still_bootstraps() -> None:
    import importlib.util

    from .support import ROOT

    target = ROOT / "skills" / "public" / "setup" / "scripts" / "normalize_host_docs.py"
    spec = importlib.util.spec_from_file_location("normalize_host_docs_shim_smoke", target)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.main)


# The header a module needs for the canonical shim, minus the `import runpy` that
# `__import__("runpy")` was the workaround for. This is the real shape found in
# `skills/public/quality/scripts/inventory_empty_scope_honesty.py`.
HEADER_WITHOUT_RUNPY = "from pathlib import Path\nfrom types import SimpleNamespace\n\n\n"
SHIM_WORKING_AROUND_MISSING_IMPORT = (
    'def _load_skill_runtime_bootstrap():\n'
    '    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)\n'
    '    if bootstrap is None:\n'
    '        raise ImportError("skill_runtime_bootstrap.py not found")\n'
    '    return SimpleNamespace(**__import__("runpy").run_path(str(bootstrap)))\n'
)


def _seed_repo_missing_runpy(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    scripts_dir = repo / "skills" / "public" / "demo" / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "no_runpy_helper.py").write_text(
        HEADER_WITHOUT_RUNPY + SHIM_WORKING_AROUND_MISSING_IMPORT, encoding="utf-8"
    )
    return repo


def test_fix_refuses_a_file_whose_module_never_imports_runpy(tmp_path: Path) -> None:
    """Splicing the canonical block here produced a file that raised NameError.

    The post-fix check only re-parsed the shim, so a syntactically perfect
    canonical block over a module missing `import runpy` was reported as `fixed`.
    Following the gate's own printed remedy broke the file it was fixing.
    """
    repo = _seed_repo_missing_runpy(tmp_path)
    target = repo / "skills/public/demo/scripts/no_runpy_helper.py"
    before = target.read_text(encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["fixed"] == []
    assert payload["unfixable"] == ["skills/public/demo/scripts/no_runpy_helper.py"]
    # The file is left exactly as it was: declining beats writing a broken file.
    assert target.read_text(encoding="utf-8") == before
    # ...and the refusal names the missing import, or it is a verdict nobody can act on.
    reason = payload["unfixable_reasons"]["skills/public/demo/scripts/no_runpy_helper.py"]
    assert "runpy" in reason


def test_required_names_are_derived_from_the_canonical_shim() -> None:
    """A hand-kept list would go stale the moment CANONICAL_SHIM is edited."""
    assert shim_gate._shim_required_names() == {"Path", "SimpleNamespace", "runpy"}


def test_conditional_and_aliased_imports_count_as_bound(tmp_path: Path) -> None:
    """The repo's real import shapes must not read as missing dependencies."""
    source = textwrap.dedent(
        """
        from types import SimpleNamespace

        try:
            from scripts.helper import Path
        except ModuleNotFoundError:
            from helper import Path

        import runpy as runpy
        """
    )
    assert shim_gate.missing_shim_dependencies(source) == []

    nested = textwrap.dedent(
        """
        from pathlib import Path
        from types import SimpleNamespace

        def _elsewhere():
            import runpy
        """
    )
    # An import inside another function is invisible to the module-level shim.
    assert shim_gate.missing_shim_dependencies(nested) == ["runpy"]

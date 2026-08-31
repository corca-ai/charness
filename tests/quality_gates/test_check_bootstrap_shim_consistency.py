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


def _payload(result):
    return yaml.safe_load(result.stdout)


def test_shim_scan_and_fix_shapes_on_one_tree(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    target = repo / "skills" / "public" / "demo" / "scripts" / "second_helper.py"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)

    clean = run_script(SCRIPT, "--repo-root", str(repo))
    assert clean.returncode == 0
    clean_payload = _payload(clean)
    assert clean_payload["status"] == "ok"
    assert clean_payload["checked_files"] == 2

    (scripts / "module_loader.py").write_text(
        "def _load_skill_runtime_bootstrap_module():\n    return None\n",
        encoding="utf-8",
    )
    (scripts / "broken_helper.py").write_text(
        "def _load_skill_runtime_bootstrap(:\n    pass\n", encoding="utf-8"
    )
    ignored = run_script(SCRIPT, "--repo-root", str(repo))
    assert ignored.returncode == 0
    assert _payload(ignored)["checked_files"] == 2

    nested = scripts / "nested_holder.py"
    nested.write_text(
        HEADER + "def outer():\n" + textwrap.indent(DRIFTED_SHIM, "    "),
        encoding="utf-8",
    )
    nested_fix = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert nested_fix.returncode == 1
    assert _payload(nested_fix)["unfixable"] == ["scripts/nested_holder.py"]
    assert textwrap.indent(DRIFTED_SHIM, "    ").rstrip() in nested.read_text(encoding="utf-8")
    nested.unlink()

    target.write_text(
        HEADER + 'PAGE_BREAK = "before\x0cafter"\nKEEP_ME = 1\n\n' + DRIFTED_SHIM,
        encoding="utf-8",
    )
    form_feed = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert form_feed.returncode == 0
    rewritten = target.read_text(encoding="utf-8")
    assert "KEEP_ME = 1" in rewritten
    assert shim_gate.CANONICAL_SHIM in rewritten
    assert run_script(SCRIPT, "--repo-root", str(repo)).returncode == 0

    target.write_text(HEADER + DRIFTED_SHIM + "\n\n" + DRIFTED_SHIM, encoding="utf-8")
    doubled = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert doubled.returncode == 0
    assert target.read_text(encoding="utf-8").count(shim_gate.CANONICAL_SHIM) == 2

    mixed = scripts / "mixed_holder.py"
    mixed.write_text(
        HEADER + DRIFTED_SHIM + "\n\ndef outer():\n" + textwrap.indent(DRIFTED_SHIM, "    "),
        encoding="utf-8",
    )
    mixed_fix = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert mixed_fix.returncode == 1
    mixed_payload = _payload(mixed_fix)
    assert mixed_payload["unfixable"] == ["scripts/mixed_holder.py"]
    assert mixed_payload["fixed"] == []
    assert shim_gate.CANONICAL_SHIM in mixed.read_text(encoding="utf-8")
    mixed.unlink()

    target.write_text(HEADER + DRIFTED_SHIM, encoding="utf-8")
    drifted = run_script(SCRIPT, "--repo-root", str(repo))
    assert drifted.returncode == 1
    drifted_payload = _payload(drifted)
    assert drifted_payload["status"] == "drift"
    assert drifted_payload["checked_files"] == 2
    assert drifted_payload["drifted"] == ["skills/public/demo/scripts/second_helper.py"]
    assert any("CANONICAL_SHIM" in remedy for remedy in drifted_payload["remedies"])

    repaired = run_script(SCRIPT, "--repo-root", str(repo), "--fix")
    assert repaired.returncode == 0
    assert _payload(repaired)["fixed"] == ["skills/public/demo/scripts/second_helper.py"]
    assert shim_gate.CANONICAL_SHIM in target.read_text(encoding="utf-8")
    assert run_script(SCRIPT, "--repo-root", str(repo)).returncode == 0


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


def test_shim_dependency_contracts_without_a_tree() -> None:
    assert shim_gate._shim_required_names() == {"Path", "SimpleNamespace", "runpy"}
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
    assert shim_gate.missing_shim_dependencies(nested) == ["runpy"]
